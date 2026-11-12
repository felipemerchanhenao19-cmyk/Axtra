"""Escáner de prospectos de Apex: el agente que encuentra restaurantes para vender Apex Play.

1. Busca la ciudad (Nominatim, OpenStreetMap) en cualquier país.
2. Trae sus restaurantes y los hoteles, hostales y atracciones turísticas (Overpass, OpenStreetMap).
3. Estima el flujo de turistas de cada restaurante: cuántos hoteles y atracciones tiene a 400 m.
4. En Colombia, lo cruza con el registro mercantil público (Confecámaras en datos.gov.co, CIIU 5611 restaurantes):
   si el restaurante es una sociedad, trae su razón social, NIT y último año renovado.
5. Le pone un puntaje de 0 a 100 y lo guarda con su estado de seguimiento (nuevo, contactado, demo, piloto, cliente…).

Solo usa datos públicos de negocios. No guarda cédulas ni busca antecedentes de personas (Habeas Data, Ley 1581):
para el representante legal deja el NIT y el enlace al RUES, donde la Cámara de Comercio lo publica.
"""
import difflib
import json
import math
import os
import re
import sqlite3
import threading
import time
import unicodedata
from collections import defaultdict

import requests

from . import config

AGENTE = os.getenv("ESCANER_AGENTE", "ApexEscaner/0.1")
NOMINATIM = "https://nominatim.openstreetmap.org/search"
OVERPASS = [u.strip() for u in os.getenv("ESCANER_OVERPASS", "https://overpass-api.de/api/interpreter,"
            "https://overpass.private.coffee/api/interpreter,https://overpass.kumi.systems/api/interpreter").split(",") if u.strip()]
RUES = "https://www.datos.gov.co/resource/c82u-588k.json"        # Confecámaras: registro mercantil (RUES)
CIIU_RESTAURANTES = ("5611", "5612", "5613", "5619")           # expendio a la mesa, autoservicio, bebidas, otros
ESTADOS = ("nuevo", "contactado", "demo", "piloto", "cliente", "descartado")
RADIO_TURISMO_M = 400

DB = config.DATA_DIR / "prospectos.db"
_hilo = threading.local()


# ---------------- Base de datos ----------------
def conn() -> sqlite3.Connection:
    c = getattr(_hilo, "c", None)
    if c is None or getattr(_hilo, "ruta", None) != str(DB):
        c = sqlite3.connect(DB, timeout=30, check_same_thread=False)
        c.row_factory = sqlite3.Row
        c.executescript("""
        CREATE TABLE IF NOT EXISTS prospectos (
            id TEXT PRIMARY KEY, ciudad TEXT, pais TEXT, nombre TEXT, cocina TEXT, nicho TEXT, tipo TEXT,
            lat REAL, lon REAL, direccion TEXT, telefono TEXT, web TEXT, email TEXT, instagram TEXT, facebook TEXT,
            horario TEXT, idiomas TEXT, turismo INTEGER, flujo TEXT, puntaje INTEGER, razones TEXT,
            razon_social TEXT, nit TEXT, renovado TEXT, confianza REAL,
            estado TEXT DEFAULT 'nuevo', notas TEXT DEFAULT '', siguiente TEXT DEFAULT '', visto REAL, actualizado REAL);
        CREATE INDEX IF NOT EXISTS prospectos_ciudad ON prospectos(pais, ciudad);
        CREATE TABLE IF NOT EXISTS escaneos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ciudad TEXT, pais TEXT, inicio REAL, fin REAL, estado TEXT,
            mensaje TEXT, encontrados INTEGER DEFAULT 0, registro_total INTEGER DEFAULT 0, cruzados INTEGER DEFAULT 0);
        """)
        _hilo.c, _hilo.ruta = c, str(DB)
    return c


# ---------------- Utilidades ----------------
def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s or "").lower())
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


SOBRA = re.compile(r"\b(s\s*a\s*s|sas|s\s*a|ltda|limitada|e\s*u|y\s*cia|cia|restaurante|restaurant|rest|bar|grill|"
                   r"cafe|the|el|la|los|las|de|del|y|and|en|zomac|bic)\b")


def nucleo(nombre: str) -> str:
    """El nombre sin «SAS», «Restaurante», artículos ni signos: «RESTAURANTE LA CEVICHERIA S.A.S.» → «cevicheria»."""
    s = re.sub(r"[^a-z0-9 ]+", " ", norm(nombre).replace(".", ""))
    return re.sub(r"\s+", " ", SOBRA.sub(" ", s)).strip()


def distancia_m(a_lat, a_lon, b_lat, b_lon) -> float:
    r = 6371000
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lon - a_lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def _get(url, **kw):
    return requests.get(url, headers={"User-Agent": AGENTE}, timeout=kw.pop("timeout", 40), **kw)


# ---------------- 1. La ciudad ----------------
def geocodificar(ciudad: str, pais: str) -> dict:
    r = _get(NOMINATIM, params={"city": ciudad, "country": pais, "format": "json", "limit": 5, "addressdetails": 1})
    r.raise_for_status()
    lugares = r.json()
    if not lugares:
        r = _get(NOMINATIM, params={"q": f"{ciudad}, {pais}", "format": "json", "limit": 5, "addressdetails": 1})
        r.raise_for_status()
        lugares = r.json()
    if not lugares:
        raise ValueError(f"no encontré «{ciudad}» en {pais}")
    l = next((x for x in lugares if x.get("osm_type") == "relation"), lugares[0])
    sur, norte, oeste, este = (float(v) for v in l["boundingbox"])
    return {"nombre": l.get("name") or ciudad, "completo": l.get("display_name", ""),
            "pais_codigo": (l.get("address") or {}).get("country_code", "").upper(),
            "area": 3600000000 + int(l["osm_id"]) if l.get("osm_type") == "relation" else None,
            "caja": (sur, oeste, norte, este), "lat": float(l["lat"]), "lon": float(l["lon"])}


# ---------------- 2. Restaurantes y turismo ----------------
def _overpass(consulta: str, rondas: int = 3) -> list:
    """Prueba cada servidor público del mapa; si todos están ocupados, espera y vuelve a intentar."""
    errores = []
    for ronda in range(rondas):
        for url in OVERPASS:
            try:
                r = requests.post(url, data={"data": consulta}, headers={"User-Agent": AGENTE}, timeout=180)
                if r.status_code == 200 and r.text.lstrip().startswith("{"):
                    return r.json().get("elements", [])
                errores.append(f"{url.split('/')[2]}: {'ocupado' if r.status_code in (200, 429, 504) else r.status_code}")
            except (requests.RequestException, ValueError) as e:
                errores.append(f"{url.split('/')[2]}: {type(e).__name__}")
        if ronda < rondas - 1:
            time.sleep(20 * (ronda + 1))
    raise RuntimeError("el mapa no respondió (" + "; ".join(errores[-len(OVERPASS):]) + "): intente en unos minutos")


def _coordenadas(elementos: list) -> list:
    out = []
    for e in elementos:
        lat, lon = e.get("lat") or (e.get("center") or {}).get("lat"), e.get("lon") or (e.get("center") or {}).get("lon")
        if lat is not None and lon is not None:
            out.append({**e, "lat": lat, "lon": lon, "tags": e.get("tags") or {}})
    return out


def lugares(ciudad: dict) -> tuple[list, list]:
    """Los restaurantes (con sus datos) y los hoteles y atracciones (solo dónde están). Dos consultas cortas: los mapas
    públicos cortan las consultas largas."""
    filtro = "(area.a)" if ciudad["area"] else "({},{},{},{})".format(*ciudad["caja"])
    cab = f"[out:json][timeout:120];area({ciudad['area']})->.a;" if ciudad["area"] else "[out:json][timeout:120];"
    rest = _coordenadas(_overpass(cab + f'nwr["amenity"="restaurant"]{filtro};out center tags;'))
    tur = _coordenadas(_overpass(cab + f'nwr["tourism"~"^(hotel|hostel|guest_house|attraction|museum)$"]{filtro};out center;'))
    return unicos([r for r in rest if (r["tags"].get("name") or "").strip()]), tur


def unicos(rest: list, metros: float = 80) -> list:
    """El mismo restaurante a veces está dos veces en el mapa (el punto y el edificio): se deja el que tiene más datos."""
    por_nombre = defaultdict(list)
    for r in sorted(rest, key=lambda r: -len(r["tags"])):
        por_nombre[nucleo(r["tags"]["name"]) or norm(r["tags"]["name"])].append(r)
    out = []
    for grupo in por_nombre.values():
        elegidos = []
        for r in grupo:
            if not any(distancia_m(r["lat"], r["lon"], e["lat"], e["lon"]) < metros for e in elegidos):
                elegidos.append(r)
        out += elegidos
    return out


def densidad_turistica(rest: list, tur: list, radio=RADIO_TURISMO_M) -> dict:
    """Cuántos hoteles y atracciones tiene cada restaurante a menos de 400 m (con una cuadrícula, para que sea rápido)."""
    paso = radio / 111000
    celdas = defaultdict(list)
    for t in tur:
        celdas[(int(t["lat"] / paso), int(t["lon"] / paso))].append(t)
    out = {}
    for r in rest:
        ci, cj = int(r["lat"] / paso), int(r["lon"] / paso)
        n = 0
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for t in celdas.get((ci + di, cj + dj), ()):
                    if distancia_m(r["lat"], r["lon"], t["lat"], t["lon"]) <= radio:
                        n += 1
        out[f"{r['type'][0]}{r['id']}"] = n
    return out


# ---------------- 3. Registro mercantil (Colombia) ----------------
def camara(ciudad: str) -> str | None:
    """El nombre de la Cámara de Comercio de la ciudad tal como aparece en el registro («MEDELLIN PARA ANTIOQUIA»)."""
    n = re.sub(r"[^A-Z ]", "", norm(ciudad).upper().replace("DE INDIAS", "")).strip()     # solo letras: va dentro de la consulta
    n = {"BOGOTA DC": "BOGOTA", "SANTAFE DE BOGOTA": "BOGOTA"}.get(n, n)
    r = _get(RUES, params={"$query": f"SELECT camara_comercio, count(*) AS n WHERE upper(camara_comercio) like '%{n.split()[0]}%' "
                                      "GROUP BY camara_comercio ORDER BY n DESC LIMIT 5"})
    r.raise_for_status()
    filas = r.json()
    mejor = next((f["camara_comercio"] for f in filas if n in f["camara_comercio"]), None)
    return mejor or (filas[0]["camara_comercio"] if filas else None)


def registro(nombre_camara: str) -> tuple[list, int]:
    """Las sociedades de restaurantes activas de esa cámara (las personas naturales no se pueden unir al nombre del local)."""
    ciiu = ",".join(f"'{c}'" for c in CIIU_RESTAURANTES)
    base = f"camara_comercio='{nombre_camara.replace(chr(39), chr(39) * 2)}' AND cod_ciiu_act_econ_pri in({ciiu}) AND estado_matricula='ACTIVA'"
    total = _get(RUES, params={"$query": f"SELECT count(*) AS n WHERE {base}"}).json()
    soc = _get(RUES, timeout=90, params={"$query": "SELECT razon_social, numero_identificacion, organizacion_juridica, ultimo_ano_renovado "
                                         f"WHERE {base} AND organizacion_juridica != 'PERSONA NATURAL' LIMIT 50000"}).json()
    return soc, int(total[0]["n"]) if total else 0


GENERICAS = {"grupo", "group", "express", "co", "gourmet", "inversiones", "comercializadora", "food", "foods", "internacional",
             "colombia", "cartagena", "medellin", "bogota", "cali", "liquidacion", "company", "sucursal", "1", "2"}


def cruzar(nombre: str, sociedades: list, indice: dict | None = None) -> tuple[dict | None, float]:
    """La sociedad del registro cuyo nombre es el del restaurante. Devuelve (sociedad, confianza 0-1)."""
    a = nucleo(nombre)
    if len(a) < 4:
        return None, 0.0
    candidatas = sociedades
    if indice is not None:
        vistos, candidatas = set(), []
        for w in a.split():
            for s in indice.get(w, ()):
                if id(s) not in vistos:
                    vistos.add(id(s)); candidatas.append(s)
    mejor, conf = None, 0.0
    for s in candidatas:
        b = s.get("_nucleo") or nucleo(s.get("razon_social", ""))
        if not b:
            continue
        c = difflib.SequenceMatcher(None, a, b).ratio()
        ta, tb = set(a.split()), set(b.split()) - GENERICAS
        if a == b:
            c = 1.0
        elif a == " ".join(w for w in b.split() if w not in GENERICAS):
            c = .95
        elif ta and ta <= tb and tb - ta <= GENERICAS:      # solo le sobran palabras genéricas («grupo», «express»…)
            c = max(c, .95)
        elif ta < tb or tb < ta:                             # le sobra una palabra con significado: no es seguro
            c = min(c, .85)
        if len(ta) == 1 and c >= .88:
            c = min(c, .9)                                   # nombre de una sola palabra («Sierpe»): verificar
        if c > conf:
            mejor, conf = s, c
    return (mejor, round(conf, 2)) if conf >= .88 else (None, 0.0)


def indice_registro(sociedades: list) -> dict:
    idx = defaultdict(list)
    for s in sociedades:
        s["_nucleo"] = nucleo(s.get("razon_social", ""))
        for w in set(s["_nucleo"].split()):
            if len(w) >= 3:
                idx[w].append(s)
    return idx


# ---------------- 4. Puntaje ----------------
NICHOS = {  # cocina de OpenStreetMap → nicho en español y qué tanto le sirve Apex (turistas que piden en su idioma)
    "regional": ("Típica / regional", 15), "local": ("Típica / regional", 15), "colombian": ("Típica / regional", 15),
    "seafood": ("Mariscos", 15), "fish": ("Mariscos", 15), "caribbean": ("Caribeña", 15), "latin_american": ("Latinoamericana", 13),
    "international": ("Internacional", 14), "fusion": ("Fusión", 14), "steak_house": ("Carnes / parrilla", 13),
    "barbecue": ("Carnes / parrilla", 12), "grill": ("Carnes / parrilla", 12), "peruvian": ("Peruana", 12),
    "mediterranean": ("Mediterránea", 12), "spanish": ("Española", 11), "italian": ("Italiana", 10), "french": ("Francesa", 11),
    "japanese": ("Japonesa / sushi", 10), "sushi": ("Japonesa / sushi", 10), "mexican": ("Mexicana", 10), "arab": ("Árabe", 10),
    "lebanese": ("Árabe", 10), "thai": ("Asiática", 10), "asian": ("Asiática", 10), "indian": ("India", 10),
    "vegetarian": ("Vegetariana", 11), "vegan": ("Vegetariana", 11), "breakfast": ("Desayunos", 8),
    # a veces el mapa tiene la cocina en español
    "colombiana": ("Típica / regional", 15), "tipica": ("Típica / regional", 15), "típica": ("Típica / regional", 15),
    "mariscos": ("Mariscos", 15), "pescado": ("Mariscos", 15), "internacional": ("Internacional", 14), "caribena": ("Caribeña", 15),
    "caribeña": ("Caribeña", 15), "parrilla": ("Carnes / parrilla", 13), "carnes": ("Carnes / parrilla", 13), "italiana": ("Italiana", 10),
    "peruana": ("Peruana", 12), "mexicana": ("Mexicana", 10), "vegetariana": ("Vegetariana", 11), "francesa": ("Francesa", 11),
    "pizza": ("Pizza", 6), "burger": ("Hamburguesas", 5), "chinese": ("China", 6), "chicken": ("Pollo", 5),
}
IDIOMAS_NOMBRE = ("en", "fr", "de", "pt", "it", "ja", "zh", "ko", "ru")


def calificar(t: dict, turismo: int, sociedad: dict | None) -> dict:
    cocinas = [c.strip() for c in (t.get("cuisine") or "").lower().split(";") if c.strip()]
    conocidas = [NICHOS[c] for c in cocinas if c in NICHOS]
    nicho, p_nicho = max(conocidas, key=lambda x: x[1]) if conocidas else \
        ("Sin dato" if not cocinas else cocinas[0].replace("_", " ").capitalize(), 7)
    razones, puntos = [], 0
    p_tur = 0 if turismo == 0 else 10 if turismo <= 2 else 20 if turismo <= 5 else 28 if turismo <= 10 else 35
    puntos += p_tur
    if turismo:
        razones.append(f"{turismo} hoteles/atracciones a {RADIO_TURISMO_M} m")
    idiomas = [k for k in IDIOMAS_NOMBRE if t.get(f"name:{k}") or t.get(f"description:{k}")]
    if idiomas:
        puntos += 5; razones.append("nombre o descripción en otros idiomas")
    contacto = 0
    if t.get("phone") or t.get("contact:phone"):
        contacto += 8
    if t.get("website") or t.get("contact:website"):
        contacto += 6
    if any(t.get(k) for k in ("contact:instagram", "instagram", "email", "contact:email", "contact:facebook", "facebook")):
        contacto += 6
    puntos += contacto
    est = (5 if t.get("opening_hours") else 0) + (4 if cocinas else 0) + (3 if t.get("addr:street") else 0) + \
          (3 if any(t.get(k) for k in ("outdoor_seating", "wheelchair", "reservation", "payment:credit_cards")) else 0)
    puntos += est
    puntos += p_nicho
    if sociedad and "LIQUIDACION" in norm(sociedad.get("razon_social", "")).upper():
        puntos -= 15; razones.append("la sociedad está en liquidación")
    elif sociedad:
        renovado = str(sociedad.get("ultimo_ano_renovado") or "0")
        al_dia = renovado.isdigit() and int(renovado) >= time.gmtime().tm_year - 1
        puntos += 15 if al_dia else 8
        razones.append("sociedad registrada" + (" y al día" if al_dia else ""))
    cadena = bool(t.get("brand") or t.get("brand:wikidata"))
    if cadena:
        puntos -= 10; razones.append("cadena: la decisión se toma en otra parte")
    flujo = "alto" if p_tur >= 28 else "medio" if p_tur >= 10 else "bajo"
    return {"puntaje": max(0, min(100, puntos)), "nicho": nicho, "cocina": ", ".join(cocinas), "tipo": "Cadena" if cadena else "Independiente",
            "flujo": flujo, "razones": razones, "idiomas": ",".join(idiomas)}


# ---------------- 5. El escaneo completo ----------------
def _actualizar_escaneo(eid: int, **campos):
    sets = ", ".join(f"{k}=?" for k in campos)
    conn().execute(f"UPDATE escaneos SET {sets} WHERE id=?", (*campos.values(), eid)); conn().commit()


def escanear(ciudad: str, pais: str = "Colombia", eid: int | None = None) -> dict:
    if eid is None:
        eid = conn().execute("INSERT INTO escaneos(ciudad, pais, inicio, estado, mensaje) VALUES (?,?,?,?,?)",
                             (ciudad, pais, time.time(), "trabajando", "buscando la ciudad")).lastrowid
        conn().commit()
    try:
        lugar = geocodificar(ciudad, pais)
        nombre_ciudad = lugar["nombre"]
        _actualizar_escaneo(eid, ciudad=nombre_ciudad, mensaje="trayendo restaurantes y hoteles del mapa")
        rest, tur = lugares(lugar)
        dens = densidad_turistica(rest, tur)
        sociedades, total_registro, idx = [], 0, None
        if lugar["pais_codigo"] == "CO" or norm(pais) == "colombia":
            _actualizar_escaneo(eid, mensaje="cruzando con el registro mercantil")
            try:
                cam = camara(nombre_ciudad)
                if cam:
                    sociedades, total_registro = registro(cam)
                    idx = indice_registro(sociedades)
            except (requests.RequestException, ValueError, KeyError) as e:
                _actualizar_escaneo(eid, mensaje=f"registro mercantil no disponible ({type(e).__name__})")
        cruzados, ahora = 0, time.time()
        c = conn()
        for r in rest:
            t, pid = r["tags"], f"{r['type'][0]}{r['id']}"
            soc, conf = cruzar(t.get("name", ""), sociedades, idx) if sociedades else (None, 0.0)
            cruzados += bool(soc)
            cal = calificar(t, dens.get(pid, 0), soc)
            direccion = " ".join(x for x in (t.get("addr:street"), t.get("addr:housenumber")) if x)
            fila = {"id": pid, "ciudad": nombre_ciudad, "pais": pais, "nombre": t.get("name"), "lat": r["lat"], "lon": r["lon"],
                    "direccion": direccion, "telefono": t.get("phone") or t.get("contact:phone") or "",
                    "web": t.get("website") or t.get("contact:website") or "", "email": t.get("email") or t.get("contact:email") or "",
                    "instagram": t.get("contact:instagram") or t.get("instagram") or "",
                    "facebook": t.get("contact:facebook") or t.get("facebook") or "", "horario": t.get("opening_hours") or "",
                    "turismo": dens.get(pid, 0), "razon_social": soc["razon_social"] if soc else "",
                    "nit": soc.get("numero_identificacion", "") if soc else "", "renovado": soc.get("ultimo_ano_renovado", "") if soc else "",
                    "confianza": conf, "visto": ahora, "actualizado": ahora,
                    **{k: v for k, v in cal.items() if k != "razones"}, "razones": json.dumps(cal["razones"], ensure_ascii=False)}
            columnas = ", ".join(fila)
            # Al volver a escanear se actualizan los datos, pero se conserva el seguimiento (estado, notas, próxima fecha)
            c.execute(f"INSERT INTO prospectos({columnas}) VALUES ({', '.join('?' * len(fila))}) "
                      f"ON CONFLICT(id) DO UPDATE SET {', '.join(f'{k}=excluded.{k}' for k in fila if k != 'id')}", tuple(fila.values()))
        c.commit()
        res = {"ciudad": nombre_ciudad, "encontrados": len(rest), "turismo": len(tur), "registro_total": total_registro, "cruzados": cruzados}
        _actualizar_escaneo(eid, fin=time.time(), estado="listo", encontrados=len(rest), registro_total=total_registro, cruzados=cruzados,
                            mensaje=f"{len(rest)} restaurantes · {len(tur)} hoteles y atracciones · {cruzados} cruzados con el registro")
        return res
    except Exception as e:
        _actualizar_escaneo(eid, fin=time.time(), estado="error", mensaje=str(e)[:300])
        raise


_ocupado = {"si": False}
_candado = threading.Lock()


def escanear_en_fondo(ciudad: str, pais: str) -> int:
    """El agente trabaja en segundo plano (un escaneo a la vez, para respetar los servicios públicos del mapa)."""
    with _candado:
        if _ocupado["si"]:
            raise RuntimeError("ya hay un escaneo en curso; espere a que termine")
        _ocupado["si"] = True
    try:
        eid = conn().execute("INSERT INTO escaneos(ciudad, pais, inicio, estado, mensaje) VALUES (?,?,?,?,?)",
                             (ciudad, pais, time.time(), "trabajando", "buscando la ciudad")).lastrowid
        conn().commit()
    except Exception:
        _ocupado["si"] = False
        raise

    def trabajar():
        try:
            escanear(ciudad, pais, eid)
        except Exception:
            pass                       # el error queda anotado en el escaneo
        finally:
            _ocupado["si"] = False
    threading.Thread(target=trabajar, daemon=True).start()
    return eid


# ---------------- Consultas para la página ----------------
def buscar(pais="", ciudad="", nicho="", tipo="", flujo="", minimo=0, estado="", contacto=False, texto="", limite=2000) -> list:
    sql, args = "SELECT * FROM prospectos WHERE puntaje >= ?", [int(minimo or 0)]
    for campo, valor in (("pais", pais), ("ciudad", ciudad), ("nicho", nicho), ("tipo", tipo), ("flujo", flujo), ("estado", estado)):
        if valor:
            sql += f" AND {campo} = ?"; args.append(valor)
    if contacto:
        sql += " AND (telefono != '' OR web != '' OR instagram != '' OR email != '')"
    if texto:
        sql += " AND (nombre LIKE ? OR razon_social LIKE ? OR direccion LIKE ?)"; args += [f"%{texto}%"] * 3
    sql += " ORDER BY puntaje DESC, turismo DESC LIMIT ?"; args.append(int(limite))
    out = []
    for f in conn().execute(sql, args).fetchall():
        d = dict(f); d["razones"] = json.loads(d.get("razones") or "[]"); out.append(d)
    return out


def opciones() -> dict:
    c = conn()
    lista = lambda campo: [dict(f) for f in c.execute(f"SELECT {campo} AS valor, count(*) AS n FROM prospectos GROUP BY {campo} ORDER BY n DESC")]
    return {"paises": lista("pais"), "ciudades": [dict(f) for f in c.execute(
                "SELECT pais, ciudad AS valor, count(*) AS n FROM prospectos GROUP BY pais, ciudad ORDER BY n DESC")],
            "nichos": lista("nicho"), "tipos": lista("tipo"), "flujos": lista("flujo"), "estados": list(ESTADOS)}


def escaneos(n=20) -> list:
    return [dict(f) for f in conn().execute("SELECT * FROM escaneos ORDER BY id DESC LIMIT ?", (n,))]


def seguimiento(pid: str, estado: str | None = None, notas: str | None = None, siguiente: str | None = None) -> dict:
    if estado is not None and estado not in ESTADOS:
        raise ValueError("estado desconocido")
    campos = {k: v for k, v in (("estado", estado), ("notas", notas), ("siguiente", siguiente)) if v is not None}
    if campos:
        conn().execute(f"UPDATE prospectos SET {', '.join(f'{k}=?' for k in campos)}, actualizado=? WHERE id=?",
                       (*campos.values(), time.time(), pid)); conn().commit()
    f = conn().execute("SELECT * FROM prospectos WHERE id=?", (pid,)).fetchone()
    if not f:
        raise KeyError(pid)
    return dict(f)
