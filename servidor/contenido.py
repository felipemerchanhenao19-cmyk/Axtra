"""Agente de contenido de Apex para TikTok e Instagram.

- Guarda el calendario de videos (2 al día) con su guion, texto y hashtags.
- Arma cada video solo: voz de Apex (edge-tts), subtítulos sincronizados palabra por palabra, pantallas reales del demo,
  el orbe y un cierre con la marca y el WhatsApp. Formato vertical 1080×1920, listo para Reels y TikTok.
- Publica por las APIs oficiales (nada de robots que inician sesión):
  · Instagram: API de Meta (cuenta profesional) → el Reel se publica solo a la hora programada.
  · TikTok: Content Posting API → el video llega como borrador a la bandeja de TikTok y Felipe lo publica con un toque
    (TikTok no deja publicar en público a una aplicación hasta que pasa su revisión).
- Nada se publica sin que Felipe lo apruebe en axtra.chat/contenido.html.
- Cada semana propone nuevas ideas con lo que funcionó (métricas de Instagram).

Marca personal de Felipe (cuentas aparte de las de Apex):
- Felipe graba sus videos con el celular y los sube. El agente los edita solo: los pone verticales, quita los silencios,
  les pone subtítulos con lo que dijo (Groq Whisper) y el gancho arriba, y escribe el texto de la publicación.
- El agente le propone ideas para grabar (qué decir y cómo grabarlo), sin inventarle historias ni cifras.
- Su voz clonada (ElevenLabs) para los días en que no puede grabar: videos con su voz y textos en pantalla.
"""
import asyncio
import base64
import datetime as dt
import difflib
import json
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import requests

from . import config

AQUI = Path(__file__).resolve().parent
MEDIOS = AQUI / "medios"
FUENTES = MEDIOS / "fuentes"
FUENTE_FUERTE = FUENTES / "Inter-ExtraBold.otf"
FUENTE = FUENTES / "Inter-Bold.otf"
CALENDARIO = AQUI / "contenido_calendario.json"
VISUALES = {"portada_es", "carta_es", "pedido_es", "idiomas", "carta_en", "orbe", "texto"}
ESTADOS = ("propuesta", "aprobada", "publicada", "error", "descartada")
COLOMBIA = dt.timezone(dt.timedelta(hours=-5))
W, H, FPS = 1080, 1920, 30
VOZ = os.getenv("CONTENIDO_VOZ", "es-CO-GonzaloNeural")
RITMO = os.getenv("CONTENIDO_RITMO", "+8%")
WHATSAPP = os.getenv("CONTENIDO_WHATSAPP", "WhatsApp 310 789 7960")
CUENTA = os.getenv("CONTENIDO_CUENTA", "@apex_corporationn")
URL_PUBLICA = os.getenv("CONTENIDO_URL_PUBLICA", "https://api.axtra.chat/v1/contenido").rstrip("/")
GRAPH = "https://graph.facebook.com/v23.0"
TIKTOK = "https://open.tiktokapis.com/v2"
TIKTOK_UN_TROZO = 64 * 1024 * 1024          # TikTok recibe hasta 64 MB de una vez; más grande va por partes
TIKTOK_TROZO = 32 * 1024 * 1024

TIPOS = ("auto", "grabado")                  # auto: lo arma el agente; grabado: Felipe lo graba y el agente lo edita
CUENTAS = ("apex", "personal")               # personal: la marca personal de Felipe, con sus propias cuentas
VOCES = ("apex", "felipe")                   # felipe: su voz clonada (ElevenLabs)
OPCIONES_BASE = {"cortar_silencios": True, "cierre": False}
PERSONAL_NOMBRE = os.getenv("CONTENIDO_PERSONAL_NOMBRE", "Felipe")
PERSONAL_CUENTA = os.getenv("CONTENIDO_PERSONAL_CUENTA", "")          # p. ej. «@felipe»: sale en el cierre si se activa
PERSONAL_HORA = os.getenv("CONTENIDO_PERSONAL_HORA", "18:00")
HASHTAGS_PERSONAL = ["#emprendimiento", "#inteligenciaartificial", "#emprendedores", "#colombia"]
ELEVEN = "https://api.elevenlabs.io/v1"
MODELO_ELEVEN = os.getenv("CONTENIDO_MODELO_VOZ", "eleven_multilingual_v2")
GROQ_OIDO = "https://api.groq.com/openai/v1/audio/transcriptions"
MODELO_OIDO = os.getenv("CONTENIDO_MODELO_OIDO", "whisper-large-v3")
VOCABULARIO = os.getenv("CONTENIDO_VOCABULARIO", "Felipe, Apex, Axtra, orbe, Tuluá, inteligencia artificial, TikTok, Instagram")
MAX_SUBIDA = int(os.getenv("CONTENIDO_MAX_SUBIDA_MB", "1500")) * 1024 * 1024
MAX_GRABACION = 10 * 60                      # segundos
PUNTUACION = ".,;:!?…¡¿\"'«»()[]“”‘’"
# Whisper en español «oye» frases en los silencios (créditos de subtítulos de Amara): esos trozos se descartan
ALUCINACIONES = ("amara.org", "subtítulos realizados por", "subtitulos realizados por", "subtítulos por la comunidad")

_hilo = threading.local()
_render = threading.Lock()


def carpeta_videos() -> Path:
    """Los videos viven en los datos de Apex: la puerta pública (api.axtra.chat) los sirve para que Instagram los descargue."""
    from .apex import config as apex_config
    d = apex_config.DATA_DIR / "contenido"
    d.mkdir(parents=True, exist_ok=True)
    return d


def carpeta_grabaciones() -> Path:
    """Los originales que graba Felipe son privados: no van a la carpeta que sirve la puerta pública."""
    d = config.DATA_DIR / "contenido_grabaciones"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------- Base de datos ----------------
def conn() -> sqlite3.Connection:
    ruta = str(config.DATA_DIR / "contenido.db")
    c = getattr(_hilo, "c", None)
    if c is None or getattr(_hilo, "ruta", None) != ruta:
        c = sqlite3.connect(ruta, timeout=30, check_same_thread=False)
        c.row_factory = sqlite3.Row
        c.executescript("""
        CREATE TABLE IF NOT EXISTS piezas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, cuando REAL, pilar TEXT, titulo TEXT, gancho TEXT, escenas TEXT,
            descripcion TEXT, hashtags TEXT, estado TEXT DEFAULT 'propuesta', video TEXT DEFAULT '', duracion REAL,
            ig_id TEXT DEFAULT '', ig_enlace TEXT DEFAULT '', tiktok_id TEXT DEFAULT '', tiktok_estado TEXT DEFAULT '',
            metricas TEXT DEFAULT '', error TEXT DEFAULT '', origen TEXT DEFAULT 'calendario', creada REAL, actualizada REAL);
        CREATE TABLE IF NOT EXISTS ajustes (clave TEXT PRIMARY KEY, valor TEXT);
        """)
        columnas = {f[1] for f in c.execute("PRAGMA table_info(piezas)")}
        for col, definicion in (("tipo", "TEXT DEFAULT 'auto'"), ("cuenta", "TEXT DEFAULT 'apex'"), ("voz", "TEXT DEFAULT 'apex'"),
                                ("grabacion", "TEXT DEFAULT ''"), ("transcripcion", "TEXT DEFAULT ''"), ("notas", "TEXT DEFAULT ''"),
                                ("opciones", "TEXT DEFAULT ''")):
            if col not in columnas:                       # bases de datos de antes de la marca personal
                c.execute(f"ALTER TABLE piezas ADD COLUMN {col} {definicion}")
        c.commit()
        _hilo.c, _hilo.ruta = c, ruta
    return c


def ajuste(clave: str, valor: str | None = None) -> str:
    if valor is not None:
        conn().execute("INSERT INTO ajustes(clave, valor) VALUES (?, ?) ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor", (clave, valor))
        conn().commit()
        return valor
    f = conn().execute("SELECT valor FROM ajustes WHERE clave=?", (clave,)).fetchone()
    return f["valor"] if f else ""


def _fila(f) -> dict:
    d = dict(f)
    d["escenas"] = json.loads(d.get("escenas") or "[]")
    d["hashtags"] = json.loads(d.get("hashtags") or "[]")
    d["metricas"] = json.loads(d["metricas"]) if d.get("metricas") else {}
    d["opciones"] = {**OPCIONES_BASE, **(json.loads(d["opciones"]) if d.get("opciones") else {})}
    d["transcripcion"] = json.loads(d["transcripcion"]) if d.get("transcripcion") else {}
    for k, base in (("tipo", "auto"), ("cuenta", "apex"), ("voz", "apex"), ("grabacion", ""), ("notas", "")):
        d[k] = d.get(k) or base
    d["hora_colombia"] = dt.datetime.fromtimestamp(d["cuando"], COLOMBIA).strftime("%Y-%m-%d %H:%M") if d.get("cuando") else ""
    return d


def validar(p: dict) -> dict:
    """En un video grabado, las escenas son la guía de lo que Felipe va a decir (puede no tener: subió un video suyo)."""
    tipo = p.get("tipo") if p.get("tipo") in TIPOS else "auto"
    escenas = []
    for e in p.get("escenas") or []:
        voz = str(e.get("voz", "")).strip()[:400]
        if not voz:
            continue
        if tipo == "grabado":
            escenas.append({"voz": voz, "visual": "camara"})
        else:
            escenas.append({"voz": voz, "visual": e.get("visual") if e.get("visual") in VISUALES else "orbe",
                            **({"texto": str(e.get("texto", ""))[:80]} if e.get("texto") else {})})
    if not escenas and tipo == "auto":
        raise ValueError("la pieza no tiene guion")
    cuenta = p.get("cuenta") if p.get("cuenta") in CUENTAS else ("personal" if tipo == "grabado" else "apex")
    return {"pilar": str(p.get("pilar", ""))[:40], "titulo": str(p.get("titulo", ""))[:80], "gancho": str(p.get("gancho", ""))[:70],
            "escenas": escenas[:6] if tipo == "auto" else escenas[:8], "descripcion": str(p.get("descripcion", ""))[:1500],
            "hashtags": [h if h.startswith("#") else "#" + h for h in (str(x).strip().replace(" ", "") for x in p.get("hashtags") or []) if len(h) > 1][:10],
            "tipo": tipo, "cuenta": cuenta, "voz": p.get("voz") if p.get("voz") in VOCES and tipo == "auto" else "apex",
            "notas": str(p.get("notas", "")).strip()[:600]}


def agregar(p: dict, cuando: float, origen: str = "calendario", estado: str = "propuesta") -> int:
    v, ahora = validar(p), time.time()
    cid = conn().execute("INSERT INTO piezas(cuando, pilar, titulo, gancho, escenas, descripcion, hashtags, estado, origen, tipo, cuenta, voz, notas, "
                         "creada, actualizada) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (cuando, v["pilar"], v["titulo"], v["gancho"], json.dumps(v["escenas"], ensure_ascii=False), v["descripcion"],
                          json.dumps(v["hashtags"], ensure_ascii=False), estado, origen, v["tipo"], v["cuenta"], v["voz"], v["notas"], ahora, ahora)).lastrowid
    conn().commit()
    return cid


def _momento(dia_base: dt.date, dias: int, hora: str) -> float:
    h, m = (int(x) for x in hora.split(":"))
    return dt.datetime.combine(dia_base + dt.timedelta(days=dias), dt.time(h, m), COLOMBIA).timestamp()


def sembrar(desde: dt.date | None = None) -> int:
    """Carga el calendario inicial (una sola vez), empezando mañana."""
    if conn().execute("SELECT count(*) FROM piezas").fetchone()[0]:
        return 0
    cal = json.loads(CALENDARIO.read_text())
    base = desde or (dt.datetime.now(COLOMBIA).date() + dt.timedelta(days=1))
    for p in cal["piezas"]:
        agregar({**p, "hashtags": list(dict.fromkeys(cal["hashtags_base"] + p.get("hashtags", [])))}, _momento(base, p["dia"] - 1, p["hora"]))
    return len(cal["piezas"])


def piezas(desde: float = 0, estado: str = "", cuenta: str = "") -> list:
    sql, args = "SELECT * FROM piezas WHERE cuando >= ?", [desde]
    if estado:
        sql += " AND estado = ?"; args.append(estado)
    if cuenta:
        sql += " AND coalesce(cuenta, 'apex') = ?"; args.append(cuenta)
    return [_fila(f) for f in conn().execute(sql + " ORDER BY cuando", args)]


def pieza(pid: int) -> dict:
    f = conn().execute("SELECT * FROM piezas WHERE id=?", (pid,)).fetchone()
    if not f:
        raise KeyError(pid)
    return _fila(f)


GUION = ("escenas", "gancho", "titulo", "descripcion", "hashtags", "pilar", "tipo", "cuenta", "voz", "notas")


def actualizar(pid: int, **campos) -> dict:
    actual = pieza(pid)
    if any(k in campos for k in GUION):
        v = validar({**actual, **{k: campos[k] for k in GUION if k in campos}})
        # Lo que se ve o se oye cambió: hay que volver a armar el video. En uno grabado, la guía de qué decir no cuenta.
        if v["gancho"] != actual["gancho"] or v["cuenta"] != actual["cuenta"] or v["tipo"] != actual["tipo"] or \
                (v["tipo"] == "auto" and (v["escenas"] != actual["escenas"] or v["voz"] != actual["voz"])):
            campos.setdefault("video", "")     # si viene el video nuevo, ese queda
        campos.update({k: json.dumps(v[k], ensure_ascii=False) if k in ("escenas", "hashtags") else v[k] for k in v})
    if "opciones" in campos and not isinstance(campos["opciones"], str):
        nuevas = {**actual["opciones"], **{k: bool(x) for k, x in dict(campos["opciones"]).items() if k in OPCIONES_BASE}}
        if nuevas != actual["opciones"]:
            campos.setdefault("video", "")
        campos["opciones"] = json.dumps(nuevas)
    if "transcripcion" in campos and not isinstance(campos["transcripcion"], str):
        campos["transcripcion"] = json.dumps(campos["transcripcion"], ensure_ascii=False)
    if "estado" in campos and campos["estado"] not in ESTADOS:
        raise ValueError("estado desconocido")
    if "cuando" in campos:
        campos["cuando"] = float(campos["cuando"])
    permitidos = {"cuando", "pilar", "titulo", "gancho", "escenas", "descripcion", "hashtags", "estado", "video", "duracion", "ig_id", "ig_enlace",
                  "tiktok_id", "tiktok_estado", "metricas", "error", "tipo", "cuenta", "voz", "notas", "grabacion", "transcripcion", "opciones"}
    campos = {k: v for k, v in campos.items() if k in permitidos}
    if campos:
        conn().execute(f"UPDATE piezas SET {', '.join(f'{k}=?' for k in campos)}, actualizada=? WHERE id=?", (*campos.values(), time.time(), pid))
        conn().commit()
    if campos.get("video") == "" and actual["video"]:
        (carpeta_videos() / actual["video"]).unlink(missing_ok=True)      # el video viejo ya no sirve
    return pieza(pid)


def para_pantalla(p: dict) -> dict:
    """Lo que necesita la página (sin las marcas de tiempo de cada palabra ni el nombre del original)."""
    d = {k: v for k, v in p.items() if k not in ("transcripcion", "grabacion")}
    d["subtitulos"] = (p.get("transcripcion") or {}).get("texto", "")
    d["grabada"] = bool(p.get("grabacion"))
    return d


def texto_publicacion(p: dict) -> str:
    texto = p["descripcion"].strip()
    if p.get("voz") == "felipe" and p.get("tipo", "auto") == "auto":
        texto = (texto + "\n\nVoz generada con IA.").strip()     # TikTok e Instagram piden avisar del contenido hecho con IA
    return (texto + "\n\n" + " ".join(p["hashtags"])).strip()


# ---------------- El video ----------------
def _ffmpeg(*args, timeout=300):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError("ffmpeg: " + r.stderr[-600:])


def _duracion(f: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def _voz(texto: str, destino: Path) -> list:
    """La voz de la escena y cuándo dice cada palabra (para los subtítulos)."""
    import edge_tts

    async def correr():
        palabras, audio = [], bytearray()
        try:
            com = edge_tts.Communicate(texto, VOZ, rate=RITMO, boundary="WordBoundary", proxy=os.getenv("HTTPS_PROXY") or None)
        except TypeError:                                   # edge-tts 6: ya manda las palabras
            com = edge_tts.Communicate(texto, VOZ, rate=RITMO, proxy=os.getenv("HTTPS_PROXY") or None)
        async for t in com.stream():
            if t["type"] == "audio":
                audio.extend(t["data"])
            elif t["type"] == "WordBoundary":
                palabras.append((t["offset"] / 1e7, (t["offset"] + t["duration"]) / 1e7, t["text"]))
        if not audio:
            raise RuntimeError("la voz no respondió")
        destino.write_bytes(bytes(audio))
        return palabras

    for intento in range(3):
        try:
            return asyncio.run(asyncio.wait_for(correr(), 40))
        except Exception:
            if intento == 2:
                raise
            time.sleep(2 * (intento + 1))


def _ass_texto(t: str) -> str:
    return t.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def _hora_ass(s: float) -> str:
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"


def trozos(palabras: list, texto: str = "", maximo_letras: int = 22) -> list:
    """Agrupa las palabras en frases cortas de subtítulo (máx. 3 palabras o 22 letras). Corta donde el guion tiene
    puntuación: la voz no la marca, así que se busca cada palabra en el texto original."""
    fin_frase, pos = [], 0
    for _, _, w in palabras:
        k = texto.find(w, pos) if texto else -1
        if k >= 0:
            pos = k + len(w)
            fin_frase.append(bool(re.match(r"\s*[.,;:!?…]", texto[pos:pos + 3])))
        else:
            fin_frase.append(bool(re.search(r"[.,;:!?…]$", w)))
    out, actual = [], []
    for (ini, fin, w), corta in zip(palabras, fin_frase):
        if actual and (len(actual) >= 3 or len(" ".join(x[2] for x in actual) + " " + w) > maximo_letras):
            out.append(actual); actual = []
        actual.append((ini, fin, w))
        if corta:
            out.append(actual); actual = []
    if actual:
        out.append(actual)
    return [(g[0][0], g[-1][1], " ".join(x[2] for x in g)) for g in out]


def subtitulos(gancho: str, frases: list, final: float, margen: int = 300) -> str:
    """Archivo ASS: el gancho arriba los primeros segundos y los subtítulos grandes abajo (estilo TikTok).
    margen: distancia desde abajo; en los videos de Felipe van más arriba, a la altura del pecho."""
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter ExtraBold,76,&H00FFFFFF,&H00FFFFFF,&H00100A05,&H64000000,0,0,0,0,100,100,0,0,1,6,0,2,90,90,{margen},1
Style: Gancho,Inter ExtraBold,66,&H00201A11,&H00201A11,&H005F9BBF,&H005F9BBF,0,0,0,0,100,100,0,0,3,22,0,8,110,110,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if gancho:
        ev.append(f"Dialogue: 1,{_hora_ass(0)},{_hora_ass(min(3.6, final))},Gancho,,0,0,0,,{{\\fad(150,250)}}{_ass_texto(gancho)}")
    for ini, fin, t in frases:
        ev.append(f"Dialogue: 0,{_hora_ass(ini)},{_hora_ass(max(fin, ini + 0.35))},Sub,,0,0,0,,{{\\fad(60,60)}}{_ass_texto(t)}")
    return cab + "\n".join(ev) + "\n"


def _escapar_drawtext(t: str) -> str:
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def _lineas_texto(texto: str, y0: int, tam: int = 104) -> str:
    lineas = [l.strip() for l in texto.split("\n") if l.strip()][:4]
    paso = int(tam * 1.25)
    y = y0 - paso * len(lineas) // 2
    out = []
    for i, l in enumerate(lineas):
        color = "0xDCC08C" if i == len(lineas) - 1 and len(lineas) > 1 else "0xF6F1E7"
        out.append(f"drawtext=fontfile='{FUENTE_FUERTE}':text='{_escapar_drawtext(l)}':fontcolor={color}:fontsize={tam}:x=(w-text_w)/2:y={y + i * paso}")
    return ",".join(out)


def _segmento(escena: dict, audio: Path, dur: float, i: int, destino: Path):
    fondo = f"color=c=0x0B1324:s={W}x{H}:r={FPS}:d={dur:.3f}"
    v = escena["visual"]
    entradas = ["-f", "lavfi", "-i", fondo]
    if v == "texto":
        filtro = f"[0:v]vignette=PI/5,{_lineas_texto(escena.get('texto') or '', 860)}[v]"
    elif v == "orbe":
        entradas += ["-stream_loop", "-1", "-i", str(MEDIOS / "clips" / "orbe.mp4"), "-loop", "1", "-i", str(MEDIOS / "mascara_orbe.png")]
        filtro = (f"[1:v]scale=920:920,setsar=1,format=yuva420p[o0];[2:v]format=gray,scale=920:920[m];[o0][m]alphamerge[o];"
                  f"[0:v]vignette=PI/5[f];[f][o]overlay=(W-w)/2:430:shortest=1[v]")
    else:
        clip = MEDIOS / "clips" / f"{v}.mp4"
        largo = max(1.0, _duracion(clip))
        inicio = (i * 2.7) % max(0.1, largo - 1)
        entradas += ["-stream_loop", "-1", "-ss", f"{inicio:.2f}", "-i", str(clip)]
        filtro = (f"[1:v]scale=-2:1290,setsar=1,pad=iw+14:ih+14:7:7:color=0x2A3550[t];[0:v]vignette=PI/5[f];"
                  f"[f][t]overlay=(W-w)/2:380:shortest=1[v]")
    n_audio = {"texto": 1, "orbe": 3}.get(v, 2)
    _ffmpeg(*entradas, "-i", str(audio), "-filter_complex", filtro + f";[{n_audio}:a]apad,atrim=0:{dur:.3f}[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k", str(destino))


def _cierre(destino: Path, dur: float = 2.8, cuenta: str = "apex"):
    """El último cuadro: la marca y el WhatsApp de Apex, o el nombre y la cuenta de Felipe en su marca personal."""
    if cuenta == "personal":
        textos = [(PERSONAL_NOMBRE, FUENTE_FUERTE, 104, "0xF6F1E7", 860)] + ([(PERSONAL_CUENTA, FUENTE, 56, "0xDCC08C", 1000)] if PERSONAL_CUENTA else [])
    else:
        textos = [("Apex Play", FUENTE_FUERTE, 96, "0xF6F1E7", 1060), ("Mesero digital con IA para restaurantes", FUENTE, 44, "0x9AA6BA", 1190),
                  (WHATSAPP, FUENTE_FUERTE, 58, "0xDCC08C", 1340), (CUENTA, FUENTE, 46, "0xF6F1E7", 1430)]
    dibujos = ",".join(f"drawtext=fontfile='{f}':text='{_escapar_drawtext(t)}':fontcolor={c}:fontsize={s}:x=(w-text_w)/2:y={y}" for t, f, s, c, y in textos)
    if cuenta == "personal":
        entradas, filtro, audio = [], f"[0:v]vignette=PI/5,{dibujos},fade=t=in:st=0:d=0.35[v]", "1:a"
    else:
        entradas = ["-i", str(MEDIOS / "logo.png")]
        filtro, audio = f"[1:v]scale=360:360[l];[0:v]vignette=PI/5[f];[f][l]overlay=(W-w)/2:560,{dibujos},fade=t=in:st=0:d=0.35[v]", "2:a"
    _ffmpeg("-f", "lavfi", "-i", f"color=c=0x0B1324:s={W}x{H}:r={FPS}:d={dur}", *entradas,
            "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-filter_complex", filtro,
            "-map", "[v]", "-map", audio, "-t", str(dur), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k", str(destino))


def armar_video(pid: int) -> dict:
    """Arma el video de una pieza y lo guarda con un nombre que no se puede adivinar (Instagram lo descarga por enlace).
    Si Felipe lo grabó, lo edita (editar_grabacion)."""
    p = pieza(pid)
    if p["tipo"] == "grabado":
        return editar_grabacion(pid)
    with _render, tempfile.TemporaryDirectory(prefix="contenido-") as tmp:
        tmp = Path(tmp)
        partes, frases, t = [], [], 0.0
        for i, e in enumerate(p["escenas"]):
            mp3 = tmp / f"voz{i}.mp3"
            palabras = _voz_felipe(e["voz"], mp3) if p["voz"] == "felipe" else _voz(e["voz"], mp3)
            dur = _duracion(mp3) + 0.2
            seg = tmp / f"seg{i}.mp4"
            _segmento(e, mp3, dur, i, seg)
            frases += [(t + a, t + b, w) for a, b, w in trozos(palabras, e["voz"])]
            partes.append(seg); t += dur
        cierre = tmp / "cierre.mp4"; _cierre(cierre, cuenta=p["cuenta"]); partes.append(cierre)
        lista = tmp / "lista.txt"
        lista.write_text("".join(f"file '{x}'\n" for x in partes))
        unido = tmp / "unido.mp4"
        _ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(unido))
        ass = tmp / "subs.ass"; ass.write_text(subtitulos(p["gancho"], frases, t))
        nombre = secrets.token_hex(16) + ".mp4"
        final = carpeta_videos() / nombre
        _ffmpeg("-i", str(unido), "-vf", f"subtitles={ass}:fontsdir={FUENTES}", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-b:a", "160k",
                "-movflags", "+faststart", str(final), timeout=600)
    viejo = p.get("video")
    if viejo and (carpeta_videos() / viejo).exists():
        (carpeta_videos() / viejo).unlink()
    return actualizar(pid, video=nombre, duracion=round(_duracion(final), 1), error="")


# ---------------- La voz clonada de Felipe (ElevenLabs) ----------------
def voz_felipe_id() -> str:
    return ajuste("voz_felipe_id") or os.getenv("CONTENIDO_VOZ_FELIPE_ID", "")


def voz_felipe_lista() -> bool:
    return bool(os.getenv("ELEVENLABS_API_KEY") and voz_felipe_id())


def _error_eleven(r) -> str:
    try:
        d = r.json()
    except ValueError:
        return f"{r.status_code} {r.text[:200]}"
    det = d.get("detail") if isinstance(d, dict) else d
    if isinstance(det, dict):
        det = det.get("message") or det.get("status") or det
    return f"{r.status_code} {str(det)[:200]}"


def clonar_voz(muestra: Path) -> str:
    """Clona la voz de Felipe con una grabación suya (audio o video, de 30 segundos a 5 minutos hablando normal)."""
    clave = os.getenv("ELEVENLABS_API_KEY")
    if not clave:
        raise RuntimeError("falta ELEVENLABS_API_KEY en el .env del servidor")
    with tempfile.TemporaryDirectory(prefix="voz-") as tmp:
        mp3 = Path(tmp) / "muestra.mp3"
        try:
            _ffmpeg("-i", str(muestra), "-vn", "-ac", "1", "-ar", "44100", "-b:a", "128k", "-t", "300", str(mp3))
        except RuntimeError:
            raise ValueError("no se pudo leer el audio de ese archivo")
        dur = _duracion(mp3)
        if dur < 25:
            raise ValueError(f"la muestra dura {dur:.0f} segundos: grabe al menos 30 (mejor de 1 a 3 minutos) hablando normal, sin música")
        r = requests.post(f"{ELEVEN}/voices/add", timeout=180, headers={"xi-api-key": clave},
                          data={"name": f"{PERSONAL_NOMBRE} (contenido)", "remove_background_noise": "true",
                                "description": "Voz propia para su contenido de TikTok e Instagram"},
                          files=[("files", ("muestra.mp3", mp3.read_bytes(), "audio/mpeg"))])
    if r.status_code >= 300:
        raise RuntimeError(f"ElevenLabs no clonó la voz: {_error_eleven(r)}")
    nueva = r.json().get("voice_id")
    if not nueva:
        raise RuntimeError("ElevenLabs no devolvió la voz")
    vieja = ajuste("voz_felipe_id")
    ajuste("voz_felipe_id", nueva)
    if vieja and vieja != nueva:
        try:
            requests.delete(f"{ELEVEN}/voices/{vieja}", timeout=30, headers={"xi-api-key": clave})
        except requests.RequestException:
            pass
    return nueva


def borrar_voz() -> None:
    """Felipe puede borrar su voz clonada: se quita de ElevenLabs y de aquí."""
    vieja = ajuste("voz_felipe_id")
    if vieja and os.getenv("ELEVENLABS_API_KEY"):
        r = requests.delete(f"{ELEVEN}/voices/{vieja}", timeout=30, headers={"xi-api-key": os.getenv("ELEVENLABS_API_KEY")})
        if r.status_code >= 300 and r.status_code != 404:
            raise RuntimeError(f"ElevenLabs no la borró: {_error_eleven(r)}")
    ajuste("voz_felipe_id", "")


def palabras_de_alineacion(al: dict) -> list:
    """ElevenLabs dice cuándo suena cada letra; los subtítulos necesitan cuándo empieza y termina cada palabra."""
    out, actual, t0, t1 = [], "", 0.0, 0.0
    for ch, a, b in zip(al.get("characters") or [], al.get("character_start_times_seconds") or [], al.get("character_end_times_seconds") or []):
        if ch.isspace():
            if actual:
                out.append((t0, t1, actual)); actual = ""
            continue
        if not actual:
            t0 = a
        actual += ch; t1 = b
    if actual:
        out.append((t0, t1, actual))
    return [(round(a, 3), round(b, 3), w.strip(PUNTUACION)) for a, b, w in out if w.strip(PUNTUACION)]


def _voz_felipe(texto: str, destino: Path) -> list:
    """Como _voz, pero con la voz clonada de Felipe."""
    clave, voz = os.getenv("ELEVENLABS_API_KEY"), voz_felipe_id()
    if not (clave and voz):
        raise RuntimeError("su voz clonada no está lista: clónela en «Mi marca personal»")
    for intento in range(3):
        r = requests.post(f"{ELEVEN}/text-to-speech/{voz}/with-timestamps", timeout=120, params={"output_format": "mp3_44100_128"},
                          headers={"xi-api-key": clave, "Content-Type": "application/json"},
                          json={"text": texto, "model_id": MODELO_ELEVEN,
                                "voice_settings": {"stability": 0.45, "similarity_boost": 0.85, "style": 0.15, "use_speaker_boost": True}})
        if r.status_code == 200:
            break
        if (r.status_code < 500 and r.status_code != 429) or intento == 2:
            raise RuntimeError(f"ElevenLabs no hizo la voz: {_error_eleven(r)}")
        time.sleep(3 * (intento + 1))
    d = r.json()
    destino.write_bytes(base64.b64decode(d["audio_base64"]))
    return palabras_de_alineacion(d.get("alignment") or d.get("normalized_alignment") or {})


# ---------------- Videos que graba Felipe ----------------
def recibir_parte(clave: str, desde: int, total: int, datos: bytes):
    """Los videos del celular pesan cientos de MB y Cloudflare no deja pasar más de 100 MB por petición: llegan por partes.
    Si una parte llega dos veces (se cortó la respuesta y el celular la reenvía), no se repite. Devuelve el archivo completo
    cuando llega la última parte; antes, None."""
    if not re.fullmatch(r"[a-z0-9_-]{1,40}", clave):
        raise ValueError("subida inválida")
    if total <= 0 or total > MAX_SUBIDA:
        raise ValueError(f"el archivo debe pesar menos de {MAX_SUBIDA // 2 ** 20} MB")
    carpeta = carpeta_grabaciones() / "subiendo"
    carpeta.mkdir(exist_ok=True)
    f = carpeta / f"{clave}.part"
    if desde == 0:
        f.write_bytes(datos)
    else:
        tam = f.stat().st_size if f.exists() else -1
        if tam == desde:
            with f.open("ab") as fh:
                fh.write(datos)
        elif tam != desde + len(datos):
            raise ValueError("la subida se cortó; vuelva a intentarlo")
    tam = f.stat().st_size
    if tam > total:
        f.unlink()
        raise ValueError("la subida llegó dañada; vuelva a intentarlo")
    return f if tam == total else None


def _probar(f: Path) -> dict:
    """Medidas del video como se ve en el celular (los celulares graban acostado y marcan que se gire)."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(f)], capture_output=True, text=True, timeout=60)
    try:
        info = json.loads(r.stdout or "{}")
    except ValueError:
        info = {}
    flujos = info.get("streams") or []
    v = next((s for s in flujos if s.get("codec_type") == "video" and not (s.get("disposition") or {}).get("attached_pic")), None)
    if not v or not v.get("width"):
        raise ValueError("ese archivo no es un video")
    w, h = int(v["width"]), int(v["height"])
    giro = (v.get("tags") or {}).get("rotate") or next((x["rotation"] for x in v.get("side_data_list") or [] if "rotation" in x), 0)
    if abs(int(float(giro or 0))) % 180 == 90:
        w, h = h, w
    return {"ancho": w, "alto": h, "duracion": float((info.get("format") or {}).get("duration") or v.get("duration") or 0),
            "audio": any(s.get("codec_type") == "audio" for s in flujos),
            "hdr": v.get("color_transfer") in ("arib-std-b67", "smpte2084")}         # el iPhone graba en HDR


def guardar_grabacion(pid: int, archivo: Path, nombre: str = "") -> dict:
    """Guarda el original que subió Felipe (aparte, privado) y deja la pieza lista para editarse."""
    p = pieza(pid)
    try:
        info = _probar(archivo)
        if info["duracion"] < 1.5:
            raise ValueError("el video es demasiado corto")
        if info["duracion"] > MAX_GRABACION:
            raise ValueError(f"el video dura más de {MAX_GRABACION // 60} minutos; recórtelo y súbalo de nuevo")
    except ValueError:
        archivo.unlink(missing_ok=True)
        raise
    ext = re.sub(r"[^a-z0-9]", "", Path(nombre).suffix.lower())[:5] or "mp4"
    destino = carpeta_grabaciones() / f"{pid}-{secrets.token_hex(8)}.{ext}"
    shutil.move(str(archivo), destino)
    if p["grabacion"]:
        (carpeta_grabaciones() / p["grabacion"]).unlink(missing_ok=True)
    return actualizar(pid, tipo="grabado", grabacion=destino.name, transcripcion="", video="", error="")


def limpiar_transcripcion(d: dict) -> dict:
    """Respuesta de Whisper → texto y palabras con su tiempo, sin lo que se inventó en los silencios."""
    segmentos = d.get("segments") or []
    malos = [(float(s.get("start", 0)), float(s.get("end", 0))) for s in segmentos
             if float(s.get("no_speech_prob") or 0) > 0.6 or any(x in str(s.get("text", "")).lower() for x in ALUCINACIONES)]
    if segmentos:
        texto = " ".join(str(s.get("text", "")).strip() for s in segmentos if (float(s.get("start", 0)), float(s.get("end", 0))) not in malos)
    else:
        texto = str(d.get("text", ""))
    palabras = []
    for w in d.get("words") or []:
        t = str(w.get("word", "")).strip().strip(PUNTUACION)
        a, b = float(w.get("start", 0)), float(w.get("end", 0))
        if t and not any(x <= (a + b) / 2 <= y for x, y in malos):
            palabras.append([round(a, 3), round(max(b, a + 0.05), 3), t])
    return {"texto": re.sub(r"\s+", " ", texto).strip(), "palabras": palabras}


def _transcribir(audio: Path) -> dict:
    """Lo que dijo Felipe y cuándo dijo cada palabra (Groq Whisper, gratis)."""
    if not config.GROQ_API_KEY:
        raise RuntimeError("falta GROQ_API_KEY en el servidor")
    errores = []
    for modelo in dict.fromkeys([MODELO_OIDO, "whisper-large-v3-turbo"]):
        try:
            r = requests.post(GROQ_OIDO, timeout=300, headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
                              files={"file": ("voz.mp3", audio.read_bytes(), "audio/mpeg")},
                              data=[("model", modelo), ("language", "es"), ("temperature", "0"), ("response_format", "verbose_json"),
                                    ("timestamp_granularities[]", "word"), ("timestamp_granularities[]", "segment"), ("prompt", VOCABULARIO)])
        except requests.RequestException as e:
            errores.append(f"{modelo}: {e}"); continue
        if r.status_code == 200:
            return limpiar_transcripcion(r.json())
        errores.append(f"{modelo}: {r.status_code} {r.text[:150]}")
    raise RuntimeError("Whisper no respondió (" + "; ".join(errores) + ")")


def cortes(palabras: list, duracion: float, hueco: float = 0.7, antes: float = 0.18, despues: float = 0.28) -> list:
    """Los trozos del video que se quedan: se quitan el arranque, el final y las pausas largas (cortes rápidos estilo TikTok).
    Deja un poco de aire antes y después de cada palabra para no comerse sílabas."""
    if not palabras:
        return [(0.0, round(duracion, 3))]
    trozos_, ini, fin = [], max(0.0, palabras[0][0] - antes), palabras[0][1]
    for a, b, _ in palabras[1:]:
        if a - fin > hueco:
            trozos_.append((ini, fin + despues)); ini = max(0.0, a - antes)
        fin = max(fin, b)
    trozos_.append((ini, fin + 0.4))
    out = []
    for a, b in trozos_:                                   # a cuadros enteros (30 por segundo) y sin pasarse del final
        a, b = int(a * FPS) / FPS, min(duracion, -(-b * FPS // 1) / FPS)
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        elif b - a >= 2 / FPS:
            out.append((a, b))
    return [(round(a, 3), round(b, 3)) for a, b in out] or [(0.0, round(duracion, 3))]


def remapear(palabras: list, trozos_: list) -> list:
    """Los tiempos de cada palabra en el video ya cortado."""
    inicios, t = [], 0.0
    for a, b in trozos_:
        inicios.append(t); t += b - a
    out = []
    for ini, fin, w in palabras:
        medio = (ini + fin) / 2
        k = min(range(len(trozos_)), key=lambda i: 0 if trozos_[i][0] <= medio <= trozos_[i][1] else min(abs(medio - trozos_[i][0]), abs(medio - trozos_[i][1])))
        a, b = trozos_[k]
        out.append((round(inicios[k] + min(max(ini, a), b) - a, 3), round(inicios[k] + min(max(fin, a), b) - a, 3), w))
    return out


def alinear(palabras: list, texto: str) -> list:
    """Felipe corrige lo que Whisper entendió mal: las palabras corregidas toman el tiempo de las que reemplazan."""
    nuevas = [w.strip(PUNTUACION) for w in texto.split()]
    nuevas = [w for w in nuevas if w]
    norm = lambda w: re.sub(r"[^\w]", "", w.lower())
    sm = difflib.SequenceMatcher(a=[norm(w) for _, _, w in palabras], b=[norm(w) for w in nuevas], autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            out += [[palabras[i1 + k][0], palabras[i1 + k][1], nuevas[j1 + k]] for k in range(j2 - j1)]
        elif op in ("replace", "insert"):
            if i2 > i1:
                ini, fin = palabras[i1][0], palabras[i2 - 1][1]
            else:                                          # palabra nueva entre dos que ya estaban
                ini = palabras[i1 - 1][1] if i1 > 0 else (palabras[0][0] if palabras else 0.0)
                fin = palabras[i1][0] if i1 < len(palabras) else ini + 0.3 * (j2 - j1)
                fin = max(fin, ini + 0.12 * (j2 - j1))
            letras = [max(1, len(w)) for w in nuevas[j1:j2]]
            t = ini
            for w, n in zip(nuevas[j1:j2], letras):
                d = (fin - ini) * n / sum(letras)
                out.append([round(t, 3), round(t + d, 3), w]); t += d
    return out


def corregir_subtitulos(pid: int, texto: str) -> dict:
    p = pieza(pid)
    if not p["transcripcion"]:
        raise ValueError("este video todavía no tiene subtítulos")
    texto = re.sub(r"\s+", " ", texto).strip()[:8000]
    return actualizar(pid, transcripcion={"texto": texto, "palabras": alinear(p["transcripcion"].get("palabras", []), texto)}, video="")


_HAY_ZSCALE = None


def _tonos_hdr() -> str:
    """Los videos HDR del iPhone se ven lavados si se pasan a video normal sin ajustar los tonos."""
    global _HAY_ZSCALE
    if _HAY_ZSCALE is None:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
        _HAY_ZSCALE = " zscale " in r.stdout and " tonemap " in r.stdout
    return ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
            if _HAY_ZSCALE else "")


def _encuadre(ancho: int, alto: int) -> str:
    """Vertical 1080×1920. Si ya es vertical, llena la pantalla; si es acostado o cuadrado, va completo sobre el mismo video desenfocado."""
    if 0.5 <= ancho / max(1, alto) <= 0.62:
        return f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
    return (f"split=2[fa][fb];[fa]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=10:2,scale={W}:{H},eq=brightness=-0.08[fondo];"
            f"[fb]scale={W}:{H}:force_original_aspect_ratio=decrease,setsar=1[frente];[fondo][frente]overlay=(W-w)/2:(H-h)/2,setsar=1")


def _comando_edicion(src: Path, info: dict, trozos_: list, ass: Path) -> list:
    k = len(trozos_)
    entradas = ["-i", str(src)] + ([] if info["audio"] else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"])
    f = [f"[0:v]{_tonos_hdr() if info.get('hdr') else ''}fps={FPS},setsar=1,split={k}" + "".join(f"[vi{i}]" for i in range(k)),
         f"[{'0' if info['audio'] else '1'}:a]aresample=48000,asplit={k}" + "".join(f"[ai{i}]" for i in range(k))]
    for i, (a, b) in enumerate(trozos_):
        f.append(f"[vi{i}]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
        f.append(f"[ai{i}]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}]")
    f.append("".join(f"[v{i}][a{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=1[cv][ca]")
    f.append(f"[cv]{_encuadre(info['ancho'], info['alto'])}[e]")
    f.append(f"[e]subtitles={ass}:fontsdir={FUENTES}[v]")
    f.append("[ca]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    return [*entradas, "-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
            "-crf", "21", "-maxrate", "10M", "-bufsize", "20M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k",
            "-movflags", "+faststart"]


INSTRUCCIONES_TEXTOS = """Eres el editor de redes de la marca personal de un emprendedor colombiano. Te paso la transcripción de un video que él grabó.
Escribe, en español colombiano y sin inventar nada que él no diga:
- titulo: máximo 60 letras, para reconocer el video en su calendario.
- gancho: máximo 45 letras; es el texto grande de arriba en los primeros segundos y sale de lo que dice al empezar.
- descripcion: 2 a 4 frases en primera persona para la publicación, que inviten a comentar.
- hashtags: 5 a 8, sin repetir.
Responde SOLO un JSON: {"titulo", "gancho", "descripcion", "hashtags": [...]}"""


def _completar_textos(pid: int, tr: dict, enrutador=None) -> dict:
    """Si Felipe subió un video sin idea previa, el agente escribe el título, el gancho y el texto con lo que dijo."""
    p = pieza(pid)
    faltan = [k for k in ("titulo", "gancho", "descripcion") if not p[k].strip()] + ([] if p["hashtags"] else ["hashtags"])
    if not faltan or not tr.get("texto"):
        return p
    try:
        from .enrutador import Enrutador
        r = (enrutador or Enrutador())._cadena(["claude_barato", "claude", "groq_pro", "gemini"], INSTRUCCIONES_TEXTOS,
                                               [{"role": "user", "content": "Transcripción:\n" + tr["texto"][:6000]}], max_tokens=800)
        m = re.search(r"\{.*\}", r.texto, re.S)
        d = json.loads(m.group(0)) if m else {}
    except Exception:
        d = {}
    primera = re.split(r"(?<=[.!?])\s", tr["texto"].strip())[0]
    respaldo = {"titulo": primera[:60], "gancho": "", "descripcion": primera, "hashtags": HASHTAGS_PERSONAL}
    return actualizar(pid, **{k: d.get(k) or respaldo[k] for k in faltan})


def editar_grabacion(pid: int, enrutador=None) -> dict:
    """El video que grabó Felipe, listo para TikTok e Instagram: vertical, sin silencios, con subtítulos y el gancho arriba."""
    p = pieza(pid)
    src = carpeta_grabaciones() / (p["grabacion"] or "_")
    if not p["grabacion"] or not src.exists():
        raise ValueError("falta subir su video")
    info, aviso, tr = _probar(src), "", p["transcripcion"]
    if not tr and info["audio"]:                            # se transcribe una sola vez (luego Felipe puede corregirlo)
        with tempfile.TemporaryDirectory(prefix="oido-") as tmp:
            audio = Path(tmp) / "voz.mp3"
            try:
                _ffmpeg("-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", str(audio))
                tr = _transcribir(audio)
                actualizar(pid, transcripcion=tr)
                p = _completar_textos(pid, tr, enrutador)
            except Exception as e:
                aviso, tr = f"El video quedó sin subtítulos: {e}"[:300], {}
    palabras = [tuple(x) for x in tr.get("palabras", [])]
    trozos_ = cortes(palabras, info["duracion"]) if palabras and p["opciones"]["cortar_silencios"] else [(0.0, round(info["duracion"], 3))]
    largo = sum(b - a for a, b in trozos_)
    with _render, tempfile.TemporaryDirectory(prefix="grabacion-") as tmp:
        tmp = Path(tmp)
        ass = tmp / "subs.ass"
        ass.write_text(subtitulos(p["gancho"], trozos(remapear(palabras, trozos_), tr.get("texto", "")), largo, margen=480))
        principal = tmp / "principal.mp4"
        _ffmpeg(*_comando_edicion(src, info, trozos_, ass), str(principal), timeout=1800)
        nombre = secrets.token_hex(16) + ".mp4"
        final = carpeta_videos() / nombre
        if p["opciones"]["cierre"]:
            cierre = tmp / "cierre.mp4"
            _cierre(cierre, 2.2, "personal")
            lista = tmp / "lista.txt"
            lista.write_text(f"file '{principal}'\nfile '{cierre}'\n")
            _ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", "-movflags", "+faststart", str(final))
        else:
            shutil.move(str(principal), final)
    viejo = pieza(pid).get("video")
    if viejo and (carpeta_videos() / viejo).exists():
        (carpeta_videos() / viejo).unlink()
    return actualizar(pid, video=nombre, duracion=round(_duracion(final), 1), error=aviso)


def siguiente_hueco(cuenta: str = "personal", hora: str = "") -> float:
    """El próximo día que no tiene video de esa cuenta, a la hora de la marca personal (un video al día)."""
    hora = hora or PERSONAL_HORA
    ocupados = {p["hora_colombia"][:10] for p in piezas(desde=time.time() - 86400, cuenta=cuenta) if p["estado"] != "descartada"}
    dia = dt.datetime.now(COLOMBIA).date()
    while True:
        t = _momento(dia, 0, hora)
        if t > time.time() + 1800 and dia.isoformat() not in ocupados:
            return t
        dia += dt.timedelta(days=1)


def nueva_grabada() -> dict:
    """Felipe sube un video suyo sin idea previa: queda en el próximo día libre de su marca personal."""
    return pieza(agregar({"tipo": "grabado", "cuenta": "personal"}, siguiente_hueco("personal"), origen="felipe"))


def limpiar_grabaciones(ahora: float | None = None) -> int:
    """Los originales pesan mucho: se borran dos semanas después de publicados o descartados, y las subidas a medias, al día."""
    ahora = ahora or time.time()
    n = 0
    for f in conn().execute("SELECT id, grabacion FROM piezas WHERE grabacion != '' AND estado IN ('publicada', 'descartada') AND cuando < ?",
                            (ahora - 14 * 86400,)).fetchall():
        (carpeta_grabaciones() / f["grabacion"]).unlink(missing_ok=True)
        conn().execute("UPDATE piezas SET grabacion='' WHERE id=?", (f["id"],)); n += 1
    conn().commit()
    for parte in (carpeta_grabaciones() / "subiendo").glob("*.part"):
        if parte.stat().st_mtime < ahora - 86400:
            parte.unlink(missing_ok=True)
    return n


# ---------------- Publicar ----------------
def _ig(cuenta: str = "apex") -> tuple:
    """Apex: IG_USUARIO_ID e IG_TOKEN. Marca personal de Felipe: IG_PERSONAL_USUARIO_ID e IG_PERSONAL_TOKEN."""
    pre = "IG_PERSONAL_" if cuenta == "personal" else "IG_"
    return os.getenv(pre + "USUARIO_ID", ""), os.getenv(pre + "TOKEN", "")


def _tt(cuenta: str) -> str:
    return "personal_" if cuenta == "personal" else ""


def instagram_listo(cuenta: str = "apex") -> bool:
    return all(_ig(cuenta))


def tiktok_listo(cuenta: str = "apex") -> bool:
    respaldo = os.getenv("TIKTOK_PERSONAL_REFRESH_TOKEN" if cuenta == "personal" else "TIKTOK_REFRESH_TOKEN")
    return bool(os.getenv("TIKTOK_CLIENT_KEY") and os.getenv("TIKTOK_CLIENT_SECRET") and (ajuste(_tt(cuenta) + "tiktok_refresh") or respaldo))


def publicar_instagram(p: dict, espera: float = 10, intentos: int = 60) -> dict:
    """Reel en dos pasos: Instagram descarga el video del enlace público, y cuando termina de procesarlo se publica."""
    uid, token = _ig(p.get("cuenta", "apex"))
    r = requests.post(f"{GRAPH}/{uid}/media", timeout=60, data={"media_type": "REELS", "video_url": f"{URL_PUBLICA}/{p['video']}",
                                                                  "caption": texto_publicacion(p)[:2200], "share_to_feed": "true", "access_token": token})
    d = r.json()
    if "id" not in d:
        raise RuntimeError(f"Instagram no aceptó el video: {d.get('error', {}).get('message', r.text[:200])}")
    contenedor = d["id"]
    for _ in range(intentos):
        e = requests.get(f"{GRAPH}/{contenedor}", timeout=30, params={"fields": "status_code,status", "access_token": token}).json()
        if e.get("status_code") == "FINISHED":
            break
        if e.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram no pudo procesar el video: {e.get('status', e.get('status_code'))}")
        time.sleep(espera)
    else:
        raise RuntimeError("Instagram tardó demasiado procesando el video")
    pub = requests.post(f"{GRAPH}/{uid}/media_publish", timeout=60, data={"creation_id": contenedor, "access_token": token}).json()
    if "id" not in pub:
        raise RuntimeError(f"Instagram no publicó: {pub.get('error', {}).get('message', pub)}")
    enlace = requests.get(f"{GRAPH}/{pub['id']}", timeout=30, params={"fields": "permalink", "access_token": token}).json().get("permalink", "")
    return {"ig_id": pub["id"], "ig_enlace": enlace}


def _tiktok_token(cuenta: str = "apex") -> str:
    """El token de TikTok dura 24 h: se renueva con el refresh token (que dura un año) y se guarda el nuevo.
    Cada cuenta (Apex y la personal de Felipe) guarda los suyos."""
    pre = _tt(cuenta)
    if ajuste(pre + "tiktok_token") and float(ajuste(pre + "tiktok_vence") or 0) > time.time() + 300:
        return ajuste(pre + "tiktok_token")
    respaldo = os.getenv("TIKTOK_PERSONAL_REFRESH_TOKEN" if cuenta == "personal" else "TIKTOK_REFRESH_TOKEN")
    r = requests.post(f"{TIKTOK}/oauth/token/", timeout=30, headers={"Content-Type": "application/x-www-form-urlencoded"},
                      data={"client_key": os.getenv("TIKTOK_CLIENT_KEY"), "client_secret": os.getenv("TIKTOK_CLIENT_SECRET"),
                            "grant_type": "refresh_token", "refresh_token": ajuste(pre + "tiktok_refresh") or respaldo}).json()
    if "access_token" not in r:
        raise RuntimeError(f"TikTok no renovó el acceso: {r.get('error_description') or r.get('error') or r}")
    ajuste(pre + "tiktok_token", r["access_token"]); ajuste(pre + "tiktok_vence", str(time.time() + int(r.get("expires_in", 86400))))
    if r.get("refresh_token"):
        ajuste(pre + "tiktok_refresh", r["refresh_token"])
    return r["access_token"]


def tiktok_conectar(code: str, redirect_uri: str, cuenta: str = "apex") -> None:
    """Primera vez: Felipe autoriza en TikTok y vuelve con un código que se cambia por los tokens."""
    r = requests.post(f"{TIKTOK}/oauth/token/", timeout=30, headers={"Content-Type": "application/x-www-form-urlencoded"},
                      data={"client_key": os.getenv("TIKTOK_CLIENT_KEY"), "client_secret": os.getenv("TIKTOK_CLIENT_SECRET"),
                            "code": code, "grant_type": "authorization_code", "redirect_uri": redirect_uri}).json()
    if "access_token" not in r:
        raise RuntimeError(f"TikTok no conectó: {r.get('error_description') or r.get('error') or r}")
    pre = _tt(cuenta)
    ajuste(pre + "tiktok_token", r["access_token"]); ajuste(pre + "tiktok_vence", str(time.time() + int(r.get("expires_in", 86400))))
    ajuste(pre + "tiktok_refresh", r.get("refresh_token", ""))


def enviar_tiktok(p: dict) -> dict:
    """Manda el video como borrador a la bandeja de TikTok (Felipe le pone el sonido del momento y lo publica).
    Hasta 64 MB va de una vez; los videos grabados más pesados van por partes de 32 MB (la última lleva el resto)."""
    archivo = carpeta_videos() / p["video"]
    tam = archivo.stat().st_size
    trozo = tam if tam <= TIKTOK_UN_TROZO else TIKTOK_TROZO
    n = max(1, tam // trozo)
    token = _tiktok_token(p.get("cuenta", "apex"))
    ini = requests.post(f"{TIKTOK}/post/publish/inbox/video/init/", timeout=60,
                        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"},
                        json={"source_info": {"source": "FILE_UPLOAD", "video_size": tam, "chunk_size": trozo, "total_chunk_count": n}}).json()
    if (ini.get("error") or {}).get("code") not in (None, "ok") or "upload_url" not in (ini.get("data") or {}):
        raise RuntimeError(f"TikTok no aceptó el video: {(ini.get('error') or {}).get('message') or ini}")
    with archivo.open("rb") as fh:
        for i in range(n):
            a = i * trozo
            b = tam - 1 if i == n - 1 else a + trozo - 1
            fh.seek(a)
            up = requests.put(ini["data"]["upload_url"], data=fh.read(b - a + 1), timeout=300,
                              headers={"Content-Type": "video/mp4", "Content-Range": f"bytes {a}-{b}/{tam}"})
            if up.status_code >= 300:
                raise RuntimeError(f"TikTok no recibió el video ({up.status_code})")
    return {"tiktok_id": ini["data"].get("publish_id", ""), "tiktok_estado": "borrador en la bandeja de TikTok"}


def publicar(pid: int) -> dict:
    p = pieza(pid)
    if p["estado"] != "aprobada":
        raise ValueError("solo se publica lo aprobado")
    if not p["video"] or not (carpeta_videos() / p["video"]).exists():
        if p["tipo"] == "grabado" and not p["grabacion"]:
            return actualizar(pid, estado="error", error="llegó la hora y falta subir su video")
        try:
            p = armar_video(pid)
        except Exception as e:
            return actualizar(pid, estado="error", error=f"no se pudo armar el video: {e}"[:400])
    hechos, errores, cuenta = {}, [], p["cuenta"]
    if instagram_listo(cuenta) and not p["ig_id"]:
        try:
            hechos.update(publicar_instagram(p))
        except Exception as e:
            errores.append(f"Instagram: {e}")
    if tiktok_listo(cuenta) and not p["tiktok_id"]:
        try:
            hechos.update(enviar_tiktok(p))
        except Exception as e:
            errores.append(f"TikTok: {e}")
    if not instagram_listo(cuenta) and not tiktok_listo(cuenta):
        errores.append("falta conectar Instagram y TikTok" + (" de su marca personal" if cuenta == "personal" else ""))
    estado = "publicada" if hechos and not errores else ("error" if errores and not hechos else "publicada")
    p = actualizar(pid, **hechos, estado=estado, error="; ".join(errores))
    try:
        from . import push
        if hechos.get("tiktok_id"):
            push.enviar("Video listo en TikTok", f"«{p['titulo']}» está en su bandeja de borradores: póngale sonido y publíquelo.", "/contenido.html")
        if errores:
            push.enviar("Un video no se publicó", f"«{p['titulo']}»: {'; '.join(errores)[:120]}", "/contenido.html")
    except Exception:
        pass
    return p


# ---------------- Métricas e ideas nuevas ----------------
def actualizar_metricas() -> int:
    n = 0
    for p in piezas(desde=time.time() - 30 * 86400, estado="publicada"):
        if not p["ig_id"] or not instagram_listo(p["cuenta"]):
            continue
        r = requests.get(f"{GRAPH}/{p['ig_id']}/insights", timeout=30,
                         params={"metric": "reach,likes,comments,shares,saved,views", "access_token": _ig(p["cuenta"])[1]}).json()
        m = {x["name"]: (x.get("values") or [{}])[0].get("value", 0) for x in r.get("data", [])}
        if m:
            actualizar(p["id"], metricas=json.dumps(m)); n += 1
    return n


INSTRUCCIONES_IDEAS = """Eres el estratega de contenido de Apex Corporation (Colombia): software e IA para restaurantes.
Productos: Apex Play (mesero digital: carta por QR en 7 idiomas, pedidos desde el celular de cada persona de la mesa, orbe al que se le habla,
alergias con aviso al mesero, pedidos a la caja en un panel) y Apex Domicilios (canal propio de domicilios, sin comisión por pedido, pago por Nequi).
Público: dueños y administradores de restaurantes, sobre todo en ciudades turísticas (Cartagena, Medellín, Santa Marta, San Andrés, Bogotá).
Escribe videos verticales de 20 a 35 segundos para TikTok e Instagram, en español colombiano, tratando de «usted».
Reglas: nunca inventes cifras, clientes, testimonios ni premios (si das números, di que son un ejemplo); nada de precios de Apex;
un gancho de máximo 45 letras que detenga el dedo; 3 a 5 escenas de máximo 25 palabras de voz cada una; termina con una invitación suave.
Visual de cada escena: uno de portada_es, carta_es, pedido_es, idiomas, carta_en, orbe, texto (con «texto»: 1 a 3 líneas cortas separadas por \\n).
Pilares: Mírelo funcionar, El problema, Turistas, Consejo, Cuentas claras, Detrás de Apex.
Responde SOLO un JSON: {"piezas": [{"pilar", "titulo", "gancho", "escenas": [{"voz", "visual", "texto"?}], "descripcion", "hashtags": [...]}]}"""


def _contexto_ideas(hechas: list) -> str:
    mejores = sorted([p for p in hechas if p["metricas"]], key=lambda p: -(p["metricas"].get("views") or p["metricas"].get("reach") or 0))[:5]
    return ("Títulos ya usados (no los repitas): " + "; ".join(p["titulo"] for p in hechas[-40:] if p["titulo"]) +
            ("\nLos que mejor funcionaron: " + "; ".join(f"{p['titulo']} ({p['metricas']})" for p in mejores) if mejores else ""))


def proponer(dias: int = 7, enrutador=None) -> list:
    """Ideas para los próximos días, aprendiendo de lo que ya se hizo y de lo que funcionó. Quedan como «propuesta»."""
    from .enrutador import Enrutador
    e = enrutador or Enrutador()
    hechas = piezas(desde=time.time() - 60 * 86400, cuenta="apex")
    r = e._cadena(["claude_barato", "claude", "groq_pro", "gemini"], INSTRUCCIONES_IDEAS,
                  [{"role": "user", "content": f"{_contexto_ideas(hechas)}\n\nEscribe {dias * 2} videos nuevos (2 por día)."}], max_tokens=6000)
    m = re.search(r"\{.*\}", r.texto, re.S)
    nuevas = json.loads(m.group(0))["piezas"] if m else []
    ultimo = max([p["cuando"] for p in piezas(cuenta="apex")] + [time.time()])
    base = dt.datetime.fromtimestamp(ultimo, COLOMBIA).date() + dt.timedelta(days=1)
    ids = []
    for k, p in enumerate(nuevas[: dias * 2]):
        try:
            ids.append(agregar(p, _momento(base, k // 2, ("12:30", "19:00")[k % 2]), origen="agente"))
        except (ValueError, KeyError, TypeError):
            continue
    return ids


def instrucciones_personal(con_voz: bool) -> str:
    voz = ("- Máximo 2 de cada 7 pueden ser «voz_en_off» (para los días en que no puede grabar): el agente los arma solo con su voz clonada "
           "y textos grandes en pantalla; ahí cada punto lleva «texto»: 1 a 3 líneas cortas separadas por \\n.\n") if con_voz else \
          "- Todas son «grabar».\n"
    return f"""Eres el estratega de la marca personal de {PERSONAL_NOMBRE} en TikTok e Instagram.
Quién es: un emprendedor colombiano de Tuluá (Valle del Cauca) que fundó Apex Corporation, una empresa que crea agentes de inteligencia
artificial para negocios, y que programó Axtra, su propio asistente con IA. Su marca personal NO vende Apex ni sus productos: habla de
emprender, de la IA en la vida real, de su día a día construyendo una empresa y de lo que va aprendiendo.
Él graba los videos con el celular, hablando a cámara con sus palabras: tú le das la idea y una guía corta, no un libreto rígido.
Reglas:
- Nunca inventes cifras, logros, clientes, premios ni anécdotas suyas: si la idea necesita una historia, pídele que cuente la suya
  (por ejemplo «Cuenta cuándo…» o «Di qué te pasó cuando…»).
- Gancho de máximo 45 letras que detenga el dedo: es el texto grande de arriba y lo primero que dice.
- 3 a 5 puntos de lo que dice, en primera persona y en español colombiano natural, de máximo 25 palabras cada uno;
  el último invita a comentar o a seguirlo. Videos de 20 a 45 segundos.
- «consejo»: en una frase, dónde y cómo grabarlo (lugar, plano, qué mostrar en pantalla).
- Pilares: Construyendo en público, IA en la vida real, Lecciones de emprendedor, Herramientas que uso, Mi opinión, Un día conmigo.
{voz}Responde SOLO un JSON: {{"piezas": [{{"formato": "grabar" o "voz_en_off", "pilar", "titulo", "gancho", "puntos": [{{"voz", "texto"?}}],
"consejo", "descripcion", "hashtags": [...]}}]}}"""


def _partir(texto: str, ancho: int = 16, lineas: int = 3) -> str:
    """Texto grande en pantalla cuando la idea no trae uno: las primeras palabras en líneas cortas."""
    out, actual = [], ""
    for w in texto.split():
        if actual and len(actual) + 1 + len(w) > ancho:
            out.append(actual); actual = ""
            if len(out) == lineas:
                out[-1] += "…"
                break
        actual = f"{actual} {w}".strip()
    if actual and len(out) < lineas:
        out.append(actual)
    return "\n".join(out)


def proponer_personal(dias: int = 7, enrutador=None) -> list:
    """Ideas para la marca personal: una por día, para que Felipe las grabe. Si su voz clonada está lista, algunas las arma el agente."""
    from .enrutador import Enrutador
    e = enrutador or Enrutador()
    con_voz = voz_felipe_lista()
    hechas = piezas(desde=time.time() - 60 * 86400, cuenta="personal")
    r = e._cadena(["claude_barato", "claude", "groq_pro", "gemini"], instrucciones_personal(con_voz),
                  [{"role": "user", "content": f"{_contexto_ideas(hechas)}\n\nEscribe {dias} ideas nuevas (una por día)."}], max_tokens=6000)
    m = re.search(r"\{.*\}", r.texto, re.S)
    nuevas = json.loads(m.group(0))["piezas"] if m else []
    ids = []
    for p in nuevas[:dias]:
        try:
            puntos = [x if isinstance(x, dict) else {"voz": str(x)} for x in p.get("puntos") or p.get("escenas") or []]
            if con_voz and p.get("formato") == "voz_en_off":
                datos = {"tipo": "auto", "voz": "felipe",
                         "escenas": [{"voz": x.get("voz", ""), "visual": "texto", "texto": x.get("texto") or _partir(str(x.get("voz", "")))} for x in puntos]}
            else:
                datos = {"tipo": "grabado", "escenas": [{"voz": x.get("voz", "")} for x in puntos]}
            ids.append(agregar({**p, **datos, "cuenta": "personal", "notas": p.get("consejo", "")}, siguiente_hueco("personal"), origen="agente"))
        except (ValueError, KeyError, TypeError, AttributeError):
            continue
    return ids


# ---------------- El vigilante: arma y publica a su hora ----------------
def revisar(ahora: float | None = None) -> dict:
    ahora = ahora or time.time()
    hecho = {"armados": 0, "publicados": 0}
    for p in piezas(desde=ahora - 6 * 3600, estado="aprobada"):
        # Se arma una sola vez antes de la hora (la voz clonada cuesta): si falló, se intenta de nuevo al publicar.
        # Uno grabado se arma apenas Felipe lo sube; sin el video no hay nada que armar.
        listo_para_armar = p["tipo"] != "grabado" or p["grabacion"]
        if p["cuando"] <= ahora + 3 * 3600 and not p["video"] and listo_para_armar and not p["error"].startswith(("armando", "no se pudo armar")):
            try:
                armar_video(p["id"]); hecho["armados"] += 1
            except Exception as e:
                actualizar(p["id"], error=f"no se pudo armar el video: {e}"[:400])
        if p["cuando"] <= ahora and not pieza(p["id"])["error"].startswith("armando"):
            publicar(p["id"]); hecho["publicados"] += 1
    if time.time() - float(ajuste("metricas_ultima") or 0) > 86400:
        ajuste("metricas_ultima", str(time.time()))
        try:
            actualizar_metricas()
        except Exception:
            pass
        try:
            limpiar_grabaciones()
        except Exception:
            pass
    return hecho


def iniciar_vigilante() -> None:
    def bucle():
        try:
            sembrar()
            # Si el servidor se reinició mientras armaba un video, ese aviso quedaría para siempre y la pieza no se publicaría
            conn().execute("UPDATE piezas SET error='' WHERE error LIKE 'armando%'"); conn().commit()
        except Exception as e:
            print(f"  (contenido: {e})")
        while True:
            try:
                revisar()
            except Exception as e:
                print(f"  (contenido: {e})")
            time.sleep(60)
    threading.Thread(target=bucle, daemon=True, name="contenido").start()
