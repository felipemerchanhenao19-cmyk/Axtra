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
playing = False        # True si Jarvis puso música
paused_by_jarvis = False

# Teclas multimedia de Windows (funcionan con YouTube en Chrome/Brave/Edge, Spotify, etc.)
VK = {"pausar": 0xB3, "reanudar": 0xB3, "siguiente": 0xB0, "anterior": 0xB1,
      "subir_volumen": 0xAF, "bajar_volumen": 0xAE, "silenciar": 0xAD}


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
    if paused_by_jarvis:  # si Jarvis pausó su propia música para escuchar, reanúdala para reconocerla
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
        if paused_by_jarvis:          # ya está en pausa mientras hablamos: que se quede así
            paused_by_jarvis = False
        else:
            _press(VK["pausar"])
        playing = False
    elif accion == "reanudar":
        if not paused_by_jarvis:      # si está en pausa por la conversación, se reanuda sola al final
            _press(VK["reanudar"])
        playing = True
    else:
        n = max(1, int(veces)) * (5 if "volumen" in accion else 1)
        _press(VK[accion], n)
        if accion in ("siguiente", "anterior"):
            playing, paused_by_jarvis = True, False
    return {"ok": True, "accion": accion}


# Pausa automática: cuando le hablas a Jarvis con música puesta, baja la música y luego la reanuda
def duck() -> None:
    global paused_by_jarvis
    if playing and not paused_by_jarvis:
        _press(VK["pausar"])
        paused_by_jarvis = True


def unduck() -> None:
    global paused_by_jarvis
    if playing and paused_by_jarvis:
        _press(VK["reanudar"])
        paused_by_jarvis = False


TOOL_SCHEMAS = [
    {"name": "reconocer_cancion", "description": "Escucha la música que está sonando (10 s) y dice qué canción es, artista, álbum y año (como Shazam).",
     "input_schema": {"type": "object", "properties": {"segundos": {"type": "number"}}}},
    {"name": "canciones_reconocidas", "description": "Últimas canciones que Jarvis ha reconocido.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "poner_musica", "description": "Pone música en YouTube: una canción, artista, álbum, género o ambiente (ej: 'lo-fi para estudiar', 'Bad Bunny').",
     "input_schema": {"type": "object", "properties": {"busqueda": {"type": "string"}}, "required": ["busqueda"]}},
    {"name": "control_musica", "description": "Controla la música que suena: pausar, reanudar, siguiente, anterior, subir_volumen, bajar_volumen, silenciar. 'veces' = cuántos pasos de volumen.",
     "input_schema": {"type": "object", "properties": {"accion": {"type": "string", "enum": list(VK)}, "veces": {"type": "integer"}}, "required": ["accion"]}},
]
FUNCS = {"reconocer_cancion": reconocer_cancion, "canciones_reconocidas": canciones_reconocidas,
         "poner_musica": poner_musica, "control_musica": control_musica}
