"""Equivalentes en Linux de lo que Axtra hace con funciones propias de Windows.

Pensado para Linux Mint (escritorio Cinnamon, que usa X11). Usa programas del sistema que instala
instalar_linux.sh:
- pactl (volumen)            - playerctl (pausar / siguiente en YouTube, Spotify...)
- xdotool y xprintidle (qué ventana usas y cuánto llevas sin tocar el PC, para el modo compañero)
- tesseract (leer el texto de la pantalla para "haz clic en Enviar")
- xdg-open (abrir documentos, imágenes y bocetos)
Si falta alguno, esa función simplemente no hace nada y Axtra sigue funcionando.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

# pactl y compañía traducen sus mensajes; en inglés sabemos leerlos siempre igual
_ENV = {**os.environ, "LC_ALL": "C"}


def _run(*cmd, timeout: float = 3):
    """Ejecuta un programa del sistema. Devuelve lo que imprimió, o None si falta o falló."""
    if not shutil.which(cmd[0]):
        return None
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=_ENV)
    except Exception:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


# ---------------- Volumen (PipeWire / PulseAudio) ----------------
def volume_get():
    """(porcentaje 0-100, silenciado) o None si no se puede leer."""
    vol = _run("pactl", "get-sink-volume", "@DEFAULT_SINK@")
    mute = _run("pactl", "get-sink-mute", "@DEFAULT_SINK@")
    m = re.search(r"(\d+)%", vol or "")
    if not m or mute is None:
        return None
    return int(m.group(1)), mute.lower().endswith("yes")


def volume_set(pct: float) -> bool:
    pct = int(max(0, min(100, pct)))
    return (_run("pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{pct}%") is not None
            and _run("pactl", "set-sink-mute", "@DEFAULT_SINK@", "0") is not None)


def volume_mute(on: bool = True) -> bool:
    return _run("pactl", "set-sink-mute", "@DEFAULT_SINK@", "1" if on else "0") is not None


# ---------------- Batería ----------------
def on_battery() -> bool:
    """True si el portátil funciona con batería (cargador desconectado)."""
    for p in Path("/sys/class/power_supply").glob("*"):
        try:
            if (p / "type").read_text().strip() == "Mains":
                return (p / "online").read_text().strip() == "0"
        except OSError:
            continue
    return False


# ---------------- Modo compañero ----------------
def idle_seconds():
    out = _run("xprintidle")
    return int(out) / 1000 if out and out.isdigit() else None


def active_window() -> str:
    return (_run("xdotool", "getactivewindow", "getwindowname") or "").lower()


# ---------------- Música (teclas multimedia) ----------------
# Mismos códigos que las teclas multimedia de Windows que usa media.py
_MEDIA = {0xB3: ("playerctl", "play-pause"), 0xB0: ("playerctl", "next"), 0xB1: ("playerctl", "previous")}


def media_key(vk: int, times: int = 1) -> bool:
    ok = True
    for _ in range(times):
        if vk in _MEDIA:
            ok = _run(*_MEDIA[vk]) is not None and ok
        elif vk in (0xAF, 0xAE):   # subir / bajar volumen: 2 % por "tecla", como en Windows
            g = volume_get()
            ok = g is not None and volume_set(g[0] + (2 if vk == 0xAF else -2)) and ok
        elif vk == 0xAD:
            g = volume_get()
            ok = g is not None and volume_mute(not g[1]) and ok
    return ok


def media_status():
    """'playing', 'paused' o None, según lo que esté sonando (YouTube en el navegador, Spotify...)."""
    out = (_run("playerctl", "status") or "").lower()
    return {"playing": "playing", "paused": "paused"}.get(out)


# ---------------- Leer la pantalla (OCR con Tesseract) ----------------
def ocr_lines(zoom: int = 1):
    """Lee el texto de la pantalla. Devuelve una lista de líneas; cada línea es una lista de
    (palabra, x, y, ancho, alto) en coordenadas de la pantalla. zoom=2 amplía la captura antes de
    leerla: más lento, pero lee bien el texto chico o claro sobre fondo oscuro (como el botón
    "Saltar anuncio" de YouTube)."""
    import pytesseract
    from PIL import ImageGrab

    img = ImageGrab.grab().convert("L")
    if zoom > 1:
        img = img.resize((img.width * zoom, img.height * zoom))
    data = pytesseract.image_to_data(img, lang="spa+eng", output_type=pytesseract.Output.DICT)
    lines = {}
    for i, word in enumerate(data["text"]):
        if not word.strip():
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines.setdefault(key, []).append(
            (word, data["left"][i] // zoom, data["top"][i] // zoom, data["width"][i] // zoom,
             data["height"][i] // zoom))
    return list(lines.values())


# ---------------- Abrir programas y archivos ----------------
# Por cada app de Windows, los programas equivalentes en Linux (se usa el primero que exista)
APPS = {
    "calculadora": ("gnome-calculator", "mate-calc", "galculator", "kcalc"),
    "bloc de notas": ("xed", "gnome-text-editor", "gedit", "mousepad", "kate"),
    "explorador": ("nemo", "nautilus", "thunar", "dolphin"),
    "paint": ("drawing", "pinta", "kolourpaint"),
}


def open_app(name: str) -> bool:
    for exe in APPS.get(name, ()):
        if shutil.which(exe):
            subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            return True
    return False


def open_path(path) -> bool:
    """Abre un archivo con el programa predeterminado (como hacer doble clic)."""
    if not shutil.which("xdg-open"):
        return False
    subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    return True
