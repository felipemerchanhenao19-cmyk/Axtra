"""Música: reconocer canciones (tipo Shazam) y poner música en YouTube con control por voz."""
import asyncio
import io
import json
import re
import time
import urllib.parse
import wave
import webbrowser

import numpy as np
import requests

from config import DATA_DIR, SAMPLE_RATE

HISTORY_PATH = DATA_DIR / "canciones_reconocidas.json"
playing = False        # True si Axtra puso música
paused_by_jarvis = False

# Teclas multimedia de Windows (funcionan con YouTube en Chrome/Brave/Edge, Spotify, etc.)
VK = {"pausar": 0xB3, "reanudar": 0xB3, "siguiente": 0xB0, "anterior": 0xB1,
      "subir_volumen": 0xAF, "bajar_volumen": 0xAE, "silenciar": 0xAD}


def _real_status_uncapped():
    import asyncio

    from winsdk.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as _Manager,
        GlobalSystemMediaTransportControlsSessionPlaybackStatus as _Status,
    )

    async def _run():
        mgr = await _Manager.request_async()
        session = mgr.get_current_session()
        if session is None:
            return None
        return session.get_playback_info().playback_status

    status = asyncio.run(_run())
    if status == _Status.PLAYING:
        return "playing"
    if status == _Status.PAUSED:
        return "paused"
    return None


def _real_status(timeout: float = 1.2):
    """Le pregunta a Windows qué está sonando de verdad (Media Session). None si no se puede saber
    o si tarda demasiado (a veces esta consulta se cuelga varios segundos; con límite de tiempo,
    pausar/reanudar nunca esperan más de lo que dura 'timeout').

    Esto evita el problema de la tecla de pausa: es un interruptor único (pausa Y reanuda con la misma
    tecla), así que si algo cambió el estado sin que Axtra se enterara (el video se acabó, un anuncio
    empezó, el usuario le dio play a mano), tocar la tecla a ciegas puede hacer justo lo contrario de
    lo que se pidió. Consultando el estado real, solo tocamos la tecla cuando de verdad hace falta.
    """
    import queue
    import threading

    q = queue.Queue(maxsize=1)

    def _worker():
        try:
            q.put(_real_status_uncapped())
        except Exception:
            q.put(None)

    th = threading.Thread(target=_worker, daemon=True)
    th.start()
    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        return None    # se demoró demasiado: seguimos sin saber el estado real, pero sin quedarnos esperando


def _press(vk: int, times: int = 1) -> None:
    try:
        import ctypes

        for _ in range(times):
            ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
            time.sleep(0.05)
    except Exception as e:
        print(f"  (no pude usar las teclas multimedia: {e})")


# ---------- Reconocer música ----------
def _record_raw(seconds: float) -> np.ndarray:
    import sounddevice as sd

    audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    return audio[:, 0]


def _wav_bytes(pcm: np.ndarray) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def reconocer_cancion(segundos: float = 10) -> dict:
    """Escucha la música que suena en la habitación y dice qué canción es."""
    try:
        from shazamio import Shazam
    except ImportError:
        return {"error": "Falta instalar: venv/Scripts/python -m pip install shazamio"}
    global paused_by_jarvis
    if paused_by_jarvis:  # si Axtra pausó su propia música para escuchar, reanúdala para reconocerla
        _press(VK["reanudar"])
        paused_by_jarvis = False
        time.sleep(1)
    print(f"  (escuchando la música {segundos:.0f} segundos...)")
    pcm = _record_raw(float(segundos))
    if np.abs(pcm).mean() < 30:
        return {"resultado": "No escucho música; súbele el volumen o acerca el computador."}
    result = asyncio.run(Shazam().recognize(_wav_bytes(pcm)))
    track = result.get("track")
    if not track:
        return {"resultado": "No reconocí la canción. Intenta con más volumen o en el coro."}
    meta = {m.get("title"): m.get("text") for s in track.get("sections", [])
            for m in s.get("metadata", []) or []}
    info = {"cancion": track.get("title"), "artista": track.get("subtitle"),
            "album": meta.get("Album"), "anio": meta.get("Released"),
            "genero": (track.get("genres") or {}).get("primary"),
            "fecha": time.strftime("%Y-%m-%d %H:%M")}
    try:
        hist = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        hist = []
    HISTORY_PATH.write_text(json.dumps((hist + [info])[-200:], ensure_ascii=False, indent=2), encoding="utf-8")
    return info


def canciones_reconocidas() -> dict:
    try:
        return {"historial": json.loads(HISTORY_PATH.read_text(encoding="utf-8"))[-10:]}
    except Exception:
        return {"historial": []}


# ---------- Poner música ----------
def poner_musica(busqueda: str) -> dict:
    """Busca en YouTube y reproduce el primer resultado (canción, artista, playlist o género)."""
    global playing, paused_by_jarvis
    q = busqueda.strip()
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(q)
    try:
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "es-CO,es;q=0.9"},
                            timeout=15).text
        vid = re.search(r'"videoId":"([\w-]{11})"', html)
        title = re.search(r'"title":\{"runs":\[\{"text":"([^"]+)"', html)
        if vid:
            url = f"https://www.youtube.com/watch?v={vid.group(1)}"
    except Exception as e:
        print(f"  (búsqueda directa falló, abro los resultados: {e})")
        title = None
    webbrowser.open(url)
    playing, paused_by_jarvis = True, False
    return {"ok": True, "reproduciendo": title.group(1) if title else q, "enlace": url}


def control_musica(accion: str, veces: int = 1) -> dict:
    """accion: pausar, reanudar, siguiente, anterior, subir_volumen, bajar_volumen, silenciar."""
    global playing, paused_by_jarvis
    if accion not in VK:
        return {"error": f"Acciones: {', '.join(VK)}"}
    if accion == "pausar":
        st = _real_status()
        if st == "paused":
            pass                       # ya está en pausa de verdad: no tocar la tecla (evita reanudarla)
        elif st == "playing":
            _press(VK["pausar"])
        elif paused_by_jarvis:         # no se pudo verificar, pero ya está en pausa mientras hablamos
            pass
        else:
            _press(VK["pausar"])       # no se pudo verificar: mejor esfuerzo, como antes
        paused_by_jarvis = False
        playing = False
    elif accion == "reanudar":
        st = _real_status()
        if st == "playing":
            pass                       # ya está sonando de verdad: no tocar la tecla (evita pausarla)
        elif st == "paused":
            _press(VK["reanudar"])
        elif not paused_by_jarvis:     # no se pudo verificar y no está en pausa por la conversación
            _press(VK["reanudar"])
        paused_by_jarvis = False
        playing = True
    elif accion in ("subir_volumen", "bajar_volumen", "silenciar"):
        import volume

        step = 10 * max(1, int(veces))
        ok = (volume.change(step if accion == "subir_volumen" else -step) if accion != "silenciar"
              else volume.mute(True))
        if not ok:   # sin control directo: teclas multimedia (silenciar se omite: es un interruptor peligroso)
            if accion == "silenciar":
                return {"ok": False, "nota": "No pude silenciar; baje el volumen en su lugar."}
            _press(VK[accion], max(1, int(veces)) * 5)
        g = volume.get()
        return {"ok": True, "accion": accion,
                "volumen_real": (f"{g[0]}%" + (" (silenciado)" if g[1] else "")) if g else "desconocido",
                "nota": "Axtra quita el silencio solo cuando necesita hablar."}
    else:
        _press(VK[accion], max(1, int(veces)))
        if accion in ("siguiente", "anterior"):
            playing, paused_by_jarvis = True, False
    return {"ok": True, "accion": accion}


def volumen(accion: str = "ver", porcentaje: float = None) -> dict:
    """ver | poner (porcentaje) | subir | bajar | silenciar | activar_sonido. Devuelve el volumen REAL."""
    import volume

    if accion == "poner" and porcentaje is not None:
        volume.set_level(float(porcentaje))
    elif accion == "subir":
        volume.change(float(porcentaje or 10))
    elif accion == "bajar":
        volume.change(-float(porcentaje or 10))
    elif accion == "silenciar":
        volume.mute(True)
    elif accion == "activar_sonido":
        volume.mute(False)
    g = volume.get()
    if g is None:
        return {"error": "No puedo controlar el volumen de Windows (falta pycaw: ejecute python instalar.py)."}
    return {"volumen": g[0], "silenciado": g[1]}


# Pausa automática: cuando le hablas a Axtra con música puesta, baja la música y luego la reanuda
def duck() -> None:
    global paused_by_jarvis
    if not (playing and not paused_by_jarvis):
        return
    st = _real_status()
    if st == "paused":       # ya está pausado (se acabó el video, lo pausaron a mano...): no tocar nada
        paused_by_jarvis = True
        return
    _press(VK["pausar"])
    paused_by_jarvis = True


def unduck() -> None:
    global paused_by_jarvis
    if not (playing and paused_by_jarvis):
        return
    st = _real_status()
    if st == "playing":      # ya está sonando (le dieron play a mano): no tocar nada
        paused_by_jarvis = False
        return
    _press(VK["reanudar"])
    paused_by_jarvis = False


TOOL_SCHEMAS = [
    {"name": "reconocer_cancion", "description": "Escucha la música que está sonando (10 s) y dice qué canción es, artista, álbum y año (como Shazam).",
     "input_schema": {"type": "object", "properties": {"segundos": {"type": "number"}}}},
    {"name": "canciones_reconocidas", "description": "Últimas canciones que Axtra ha reconocido.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "poner_musica", "description": "Pone música en YouTube: una canción, artista, álbum, género o ambiente (ej: 'lo-fi para estudiar', 'Bad Bunny').",
     "input_schema": {"type": "object", "properties": {"busqueda": {"type": "string"}}, "required": ["busqueda"]}},
    {"name": "control_musica", "description": "Controla la música que suena: pausar, reanudar, siguiente, anterior, subir_volumen, bajar_volumen, silenciar. 'veces' = cuántos pasos de volumen.",
     "input_schema": {"type": "object", "properties": {"accion": {"type": "string", "enum": list(VK)}, "veces": {"type": "integer"}}, "required": ["accion"]}},
]
TOOL_SCHEMAS.append({"name": "volumen", "description": "Volumen REAL de Windows: ver, poner (porcentaje 0-100), subir, bajar, silenciar o activar_sonido. Devuelve el nivel real; úsalo para verificar antes de decir que cambiaste el volumen.",
                     "input_schema": {"type": "object", "properties": {"accion": {"type": "string", "enum": ["ver", "poner", "subir", "bajar", "silenciar", "activar_sonido"]}, "porcentaje": {"type": "number"}}, "required": ["accion"]}})
FUNCS = {"volumen": volumen, "reconocer_cancion": reconocer_cancion, "canciones_reconocidas": canciones_reconocidas,
         "poner_musica": poner_musica, "control_musica": control_musica}
