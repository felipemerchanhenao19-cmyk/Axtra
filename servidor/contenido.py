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
"""
import asyncio
import datetime as dt
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

_hilo = threading.local()
_render = threading.Lock()


def carpeta_videos() -> Path:
    """Los videos viven en los datos de Apex: la puerta pública (api.axtra.chat) los sirve para que Instagram los descargue."""
    from .apex import config as apex_config
    d = apex_config.DATA_DIR / "contenido"
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
    d["hora_colombia"] = dt.datetime.fromtimestamp(d["cuando"], COLOMBIA).strftime("%Y-%m-%d %H:%M") if d.get("cuando") else ""
    return d


def validar(p: dict) -> dict:
    escenas = [{"voz": str(e.get("voz", "")).strip()[:400], "visual": e.get("visual") if e.get("visual") in VISUALES else "orbe",
                **({"texto": str(e.get("texto", ""))[:80]} if e.get("texto") else {})} for e in (p.get("escenas") or []) if str(e.get("voz", "")).strip()]
    if not escenas:
        raise ValueError("la pieza no tiene guion")
    return {"pilar": str(p.get("pilar", ""))[:40], "titulo": str(p.get("titulo", ""))[:80], "gancho": str(p.get("gancho", ""))[:70],
            "escenas": escenas[:6], "descripcion": str(p.get("descripcion", ""))[:1500],
            "hashtags": [h if h.startswith("#") else "#" + h for h in (str(x).strip().replace(" ", "") for x in p.get("hashtags") or []) if len(h) > 1][:10]}


def agregar(p: dict, cuando: float, origen: str = "calendario", estado: str = "propuesta") -> int:
    v, ahora = validar(p), time.time()
    cid = conn().execute("INSERT INTO piezas(cuando, pilar, titulo, gancho, escenas, descripcion, hashtags, estado, origen, creada, actualizada) "
                         "VALUES (?,?,?,?,?,?,?,?,?,?,?)", (cuando, v["pilar"], v["titulo"], v["gancho"], json.dumps(v["escenas"], ensure_ascii=False),
                                                            v["descripcion"], json.dumps(v["hashtags"], ensure_ascii=False), estado, origen, ahora, ahora)).lastrowid
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


def piezas(desde: float = 0, estado: str = "") -> list:
    sql, args = "SELECT * FROM piezas WHERE cuando >= ?", [desde]
    if estado:
        sql += " AND estado = ?"; args.append(estado)
    return [_fila(f) for f in conn().execute(sql + " ORDER BY cuando", args)]


def pieza(pid: int) -> dict:
    f = conn().execute("SELECT * FROM piezas WHERE id=?", (pid,)).fetchone()
    if not f:
        raise KeyError(pid)
    return _fila(f)


def actualizar(pid: int, **campos) -> dict:
    actual = pieza(pid)
    if "escenas" in campos or "gancho" in campos or "titulo" in campos or "descripcion" in campos or "hashtags" in campos or "pilar" in campos:
        v = validar({**actual, **{k: v for k, v in campos.items() if k in ("escenas", "gancho", "titulo", "descripcion", "hashtags", "pilar")}})
        if v["escenas"] != actual["escenas"] or v["gancho"] != actual["gancho"]:
            campos["video"] = ""                          # cambió el guion: hay que volver a armar el video
        campos.update({k: json.dumps(v[k], ensure_ascii=False) if k in ("escenas", "hashtags") else v[k] for k in v})
    if "estado" in campos and campos["estado"] not in ESTADOS:
        raise ValueError("estado desconocido")
    if "cuando" in campos:
        campos["cuando"] = float(campos["cuando"])
    permitidos = {"cuando", "pilar", "titulo", "gancho", "escenas", "descripcion", "hashtags", "estado", "video", "duracion", "ig_id", "ig_enlace",
                  "tiktok_id", "tiktok_estado", "metricas", "error"}
    campos = {k: v for k, v in campos.items() if k in permitidos}
    if campos:
        conn().execute(f"UPDATE piezas SET {', '.join(f'{k}=?' for k in campos)}, actualizada=? WHERE id=?", (*campos.values(), time.time(), pid))
        conn().commit()
    return pieza(pid)


def texto_publicacion(p: dict) -> str:
    return (p["descripcion"].strip() + "\n\n" + " ".join(p["hashtags"])).strip()


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


def subtitulos(gancho: str, frases: list, final: float) -> str:
    """Archivo ASS: el gancho arriba los primeros segundos y los subtítulos grandes abajo (estilo TikTok)."""
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter ExtraBold,76,&H00FFFFFF,&H00FFFFFF,&H00100A05,&H64000000,0,0,0,0,100,100,0,0,1,6,0,2,90,90,300,1
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


def _cierre(destino: Path, dur: float = 2.8):
    textos = [("Apex Play", FUENTE_FUERTE, 96, "0xF6F1E7", 1060), ("Mesero digital con IA para restaurantes", FUENTE, 44, "0x9AA6BA", 1190),
              (WHATSAPP, FUENTE_FUERTE, 58, "0xDCC08C", 1340), (CUENTA, FUENTE, 46, "0xF6F1E7", 1430)]
    dibujos = ",".join(f"drawtext=fontfile='{f}':text='{_escapar_drawtext(t)}':fontcolor={c}:fontsize={s}:x=(w-text_w)/2:y={y}" for t, f, s, c, y in textos)
    _ffmpeg("-f", "lavfi", "-i", f"color=c=0x0B1324:s={W}x{H}:r={FPS}:d={dur}", "-i", str(MEDIOS / "logo.png"),
            "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-filter_complex",
            f"[1:v]scale=360:360[l];[0:v]vignette=PI/5[f];[f][l]overlay=(W-w)/2:560,{dibujos},fade=t=in:st=0:d=0.35[v]",
            "-map", "[v]", "-map", "2:a", "-t", str(dur), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k", str(destino))


def armar_video(pid: int) -> dict:
    """Arma el video de una pieza y lo guarda con un nombre que no se puede adivinar (Instagram lo descarga por enlace)."""
    p = pieza(pid)
    with _render, tempfile.TemporaryDirectory(prefix="contenido-") as tmp:
        tmp = Path(tmp)
        partes, frases, t = [], [], 0.0
        for i, e in enumerate(p["escenas"]):
            mp3 = tmp / f"voz{i}.mp3"
            palabras = _voz(e["voz"], mp3)
            dur = _duracion(mp3) + 0.2
            seg = tmp / f"seg{i}.mp4"
            _segmento(e, mp3, dur, i, seg)
            frases += [(t + a, t + b, w) for a, b, w in trozos(palabras, e["voz"])]
            partes.append(seg); t += dur
        cierre = tmp / "cierre.mp4"; _cierre(cierre); partes.append(cierre)
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


# ---------------- Publicar ----------------
def instagram_listo() -> bool:
    return bool(os.getenv("IG_USUARIO_ID") and os.getenv("IG_TOKEN"))


def tiktok_listo() -> bool:
    return bool(os.getenv("TIKTOK_CLIENT_KEY") and os.getenv("TIKTOK_CLIENT_SECRET") and (ajuste("tiktok_refresh") or os.getenv("TIKTOK_REFRESH_TOKEN")))


def publicar_instagram(p: dict, espera: float = 10, intentos: int = 60) -> dict:
    """Reel en dos pasos: Instagram descarga el video del enlace público, y cuando termina de procesarlo se publica."""
    uid, token = os.getenv("IG_USUARIO_ID"), os.getenv("IG_TOKEN")
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


def _tiktok_token() -> str:
    """El token de TikTok dura 24 h: se renueva con el refresh token (que dura un año) y se guarda el nuevo."""
    if ajuste("tiktok_token") and float(ajuste("tiktok_vence") or 0) > time.time() + 300:
        return ajuste("tiktok_token")
    r = requests.post(f"{TIKTOK}/oauth/token/", timeout=30, headers={"Content-Type": "application/x-www-form-urlencoded"},
                      data={"client_key": os.getenv("TIKTOK_CLIENT_KEY"), "client_secret": os.getenv("TIKTOK_CLIENT_SECRET"),
                            "grant_type": "refresh_token", "refresh_token": ajuste("tiktok_refresh") or os.getenv("TIKTOK_REFRESH_TOKEN")}).json()
    if "access_token" not in r:
        raise RuntimeError(f"TikTok no renovó el acceso: {r.get('error_description') or r.get('error') or r}")
    ajuste("tiktok_token", r["access_token"]); ajuste("tiktok_vence", str(time.time() + int(r.get("expires_in", 86400))))
    if r.get("refresh_token"):
        ajuste("tiktok_refresh", r["refresh_token"])
    return r["access_token"]


def tiktok_conectar(code: str, redirect_uri: str) -> None:
    """Primera vez: Felipe autoriza en TikTok y vuelve con un código que se cambia por los tokens."""
    r = requests.post(f"{TIKTOK}/oauth/token/", timeout=30, headers={"Content-Type": "application/x-www-form-urlencoded"},
                      data={"client_key": os.getenv("TIKTOK_CLIENT_KEY"), "client_secret": os.getenv("TIKTOK_CLIENT_SECRET"),
                            "code": code, "grant_type": "authorization_code", "redirect_uri": redirect_uri}).json()
    if "access_token" not in r:
        raise RuntimeError(f"TikTok no conectó: {r.get('error_description') or r.get('error') or r}")
    ajuste("tiktok_token", r["access_token"]); ajuste("tiktok_vence", str(time.time() + int(r.get("expires_in", 86400))))
    ajuste("tiktok_refresh", r.get("refresh_token", ""))


def enviar_tiktok(p: dict) -> dict:
    """Manda el video como borrador a la bandeja de TikTok (Felipe le pone el sonido del momento y lo publica)."""
    archivo = carpeta_videos() / p["video"]
    datos = archivo.read_bytes()
    token = _tiktok_token()
    ini = requests.post(f"{TIKTOK}/post/publish/inbox/video/init/", timeout=60,
                        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"},
                        json={"source_info": {"source": "FILE_UPLOAD", "video_size": len(datos), "chunk_size": len(datos), "total_chunk_count": 1}}).json()
    if (ini.get("error") or {}).get("code") not in (None, "ok") or "upload_url" not in (ini.get("data") or {}):
        raise RuntimeError(f"TikTok no aceptó el video: {(ini.get('error') or {}).get('message') or ini}")
    up = requests.put(ini["data"]["upload_url"], data=datos, timeout=300,
                      headers={"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{len(datos) - 1}/{len(datos)}"})
    if up.status_code >= 300:
        raise RuntimeError(f"TikTok no recibió el video ({up.status_code})")
    return {"tiktok_id": ini["data"].get("publish_id", ""), "tiktok_estado": "borrador en la bandeja de TikTok"}


def publicar(pid: int) -> dict:
    p = pieza(pid)
    if p["estado"] != "aprobada":
        raise ValueError("solo se publica lo aprobado")
    if not p["video"] or not (carpeta_videos() / p["video"]).exists():
        p = armar_video(pid)
    hechos, errores = {}, []
    if instagram_listo() and not p["ig_id"]:
        try:
            hechos.update(publicar_instagram(p))
        except Exception as e:
            errores.append(f"Instagram: {e}")
    if tiktok_listo() and not p["tiktok_id"]:
        try:
            hechos.update(enviar_tiktok(p))
        except Exception as e:
            errores.append(f"TikTok: {e}")
    if not instagram_listo() and not tiktok_listo():
        errores.append("falta conectar Instagram y TikTok")
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
    if not instagram_listo():
        return 0
    n = 0
    for p in piezas(desde=time.time() - 30 * 86400, estado="publicada"):
        if not p["ig_id"]:
            continue
        r = requests.get(f"{GRAPH}/{p['ig_id']}/insights", timeout=30,
                         params={"metric": "reach,likes,comments,shares,saved,views", "access_token": os.getenv("IG_TOKEN")}).json()
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


def proponer(dias: int = 7, enrutador=None) -> list:
    """Ideas para los próximos días, aprendiendo de lo que ya se hizo y de lo que funcionó. Quedan como «propuesta»."""
    from .enrutador import Enrutador
    e = enrutador or Enrutador()
    hechas = piezas(desde=time.time() - 60 * 86400)
    mejores = sorted([p for p in hechas if p["metricas"]], key=lambda p: -(p["metricas"].get("views") or p["metricas"].get("reach") or 0))[:5]
    contexto = ("Títulos ya usados (no los repitas): " + "; ".join(p["titulo"] for p in hechas[-40:]) +
                ("\nLos que mejor funcionaron: " + "; ".join(f"{p['titulo']} ({p['metricas']})" for p in mejores) if mejores else ""))
    r = e._cadena(["claude_barato", "claude", "groq_pro", "gemini"], INSTRUCCIONES_IDEAS,
                  [{"role": "user", "content": f"{contexto}\n\nEscribe {dias * 2} videos nuevos (2 por día)."}], max_tokens=6000)
    m = re.search(r"\{.*\}", r.texto, re.S)
    nuevas = json.loads(m.group(0))["piezas"] if m else []
    ultimo = max([p["cuando"] for p in piezas()] + [time.time()])
    base = dt.datetime.fromtimestamp(ultimo, COLOMBIA).date() + dt.timedelta(days=1)
    ids = []
    for k, p in enumerate(nuevas[: dias * 2]):
        try:
            ids.append(agregar(p, _momento(base, k // 2, ("12:30", "19:00")[k % 2]), origen="agente"))
        except (ValueError, KeyError, TypeError):
            continue
    return ids


# ---------------- El vigilante: arma y publica a su hora ----------------
def revisar(ahora: float | None = None) -> dict:
    ahora = ahora or time.time()
    hecho = {"armados": 0, "publicados": 0}
    for p in piezas(desde=ahora - 6 * 3600, estado="aprobada"):
        if p["cuando"] <= ahora + 3 * 3600 and not p["video"]:
            try:
                armar_video(p["id"]); hecho["armados"] += 1
            except Exception as e:
                actualizar(p["id"], error=f"no se pudo armar el video: {e}"[:400])
        if p["cuando"] <= ahora:
            publicar(p["id"]); hecho["publicados"] += 1
    if time.time() - float(ajuste("metricas_ultima") or 0) > 86400:
        ajuste("metricas_ultima", str(time.time()))
        try:
            actualizar_metricas()
        except Exception:
            pass
    return hecho


def iniciar_vigilante() -> None:
    def bucle():
        try:
            sembrar()
        except Exception as e:
            print(f"  (contenido: {e})")
        while True:
            try:
                revisar()
            except Exception as e:
                print(f"  (contenido: {e})")
            time.sleep(60)
    threading.Thread(target=bucle, daemon=True, name="contenido").start()
