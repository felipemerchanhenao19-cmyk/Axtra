"""Habilidades prácticas: recordatorios y alarmas, lista de tareas y abrir sitios/apps en el PC."""
import json
import os
import re
import threading
import webbrowser
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import DATA_DIR, TIMEZONE

REM_PATH = DATA_DIR / "recordatorios.json"
TASKS_PATH = DATA_DIR / "tareas.json"
_lock = threading.Lock()


def _now():
    return datetime.now(ZoneInfo(TIMEZONE))


def _load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save(path, data):
    with _lock:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------- Recordatorios y alarmas ----------
def crear_recordatorio(mensaje: str, minutos: float = None, hora: str = None) -> dict:
    """minutos: dentro de cuántos minutos. hora: 'HH:MM' en formato 24 h (hoy o mañana)."""
    now = _now()
    if minutos is not None:
        when = now + timedelta(minutes=float(minutos))
    elif hora:
        m = re.match(r"(\d{1,2}):(\d{2})", hora)
        if not m:
            return {"error": "La hora debe ser HH:MM en formato 24 horas"}
        when = now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0)
        if when <= now:
            when += timedelta(days=1)
    else:
        return {"error": "Indica minutos u hora"}
    items = _load(REM_PATH)
    items.append({"mensaje": mensaje, "cuando": when.isoformat()})
    _save(REM_PATH, items)
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    cuando = "hoy" if when.date() == now.date() else dias[when.weekday()]
    return {"ok": True, "sonara": f"{cuando} a las {when:%I:%M %p}"}


def ver_recordatorios() -> dict:
    return {"recordatorios": _load(REM_PATH)}


def borrar_recordatorio(palabras: str) -> dict:
    items = _load(REM_PATH)
    keep = [r for r in items if palabras.lower() not in r["mensaje"].lower()]
    _save(REM_PATH, keep)
    return {"borrados": len(items) - len(keep)}


def due_reminders() -> list:
    """Devuelve los recordatorios que ya tocan y los borra (lo usa el módulo autónomo)."""
    items = _load(REM_PATH)
    now = _now()
    due = [r for r in items if datetime.fromisoformat(r["cuando"]) <= now]
    if due:
        _save(REM_PATH, [r for r in items if r not in due])
    return [r["mensaje"] for r in due]


# ---------- Tareas ----------
def tareas(accion: str, texto: str = "") -> dict:
    items = _load(TASKS_PATH)
    if accion == "agregar" and texto:
        items.append({"tarea": texto, "creada": _now().strftime("%Y-%m-%d"), "hecha": False})
    elif accion in ("completar", "borrar") and texto:
        for t in items:
            if texto.lower() in t["tarea"].lower():
                if accion == "completar":
                    t["hecha"] = True
                else:
                    t["borrar"] = True
        items = [t for t in items if not t.get("borrar")]
    _save(TASKS_PATH, items)
    return {"pendientes": [t["tarea"] for t in items if not t["hecha"]],
            "hechas": [t["tarea"] for t in items if t["hecha"]][-5:]}


# ---------- Abrir cosas en el PC ----------
SITES = {
    "youtube": "https://www.youtube.com", "google": "https://www.google.com",
    "gmail": "https://mail.google.com", "correo": "https://mail.google.com",
    "whatsapp": "https://web.whatsapp.com", "calendario": "https://calendar.google.com",
    "drive": "https://drive.google.com", "spotify": "https://open.spotify.com",
    "claude": "https://claude.ai", "tradingview": "https://www.tradingview.com",
    "yahoo finanzas": "https://finance.yahoo.com", "linkedin": "https://www.linkedin.com",
    "instagram": "https://www.instagram.com", "noticias": "https://news.google.com/?hl=es-419&gl=CO",
}
APPS = {"calculadora": "calc.exe", "bloc de notas": "notepad.exe", "explorador": "explorer.exe",
        "paint": "mspaint.exe"}


def abrir(que: str) -> dict:
    q = que.strip().lower()
    if q in APPS and os.name == "nt":
        os.startfile(APPS[q])
        return {"ok": True, "abierto": q}
    url = SITES.get(q)
    if not url and re.match(r"^(https?://)?[\w-]+(\.[\w-]+)+(/\S*)?$", q):
        url = q if q.startswith("http") else "https://" + q
    if not url:
        url = "https://www.google.com/search?q=" + re.sub(r"\s+", "+", que.strip())
    webbrowser.open(url)
    return {"ok": True, "abierto": url}


TOOL_SCHEMAS = [
    {"name": "crear_recordatorio", "description": "Crea un recordatorio o alarma. Jarvis lo dirá en voz alta a la hora indicada. Usa 'minutos' (dentro de X minutos) o 'hora' (HH:MM, 24 h).",
     "input_schema": {"type": "object", "properties": {"mensaje": {"type": "string"}, "minutos": {"type": "number"}, "hora": {"type": "string"}}, "required": ["mensaje"]}},
    {"name": "ver_recordatorios", "description": "Lista los recordatorios pendientes.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "borrar_recordatorio", "description": "Borra recordatorios que contengan esas palabras.",
     "input_schema": {"type": "object", "properties": {"palabras": {"type": "string"}}, "required": ["palabras"]}},
    {"name": "tareas", "description": "Lista de tareas de Felipe: ver, agregar, completar o borrar.",
     "input_schema": {"type": "object", "properties": {"accion": {"type": "string", "enum": ["ver", "agregar", "completar", "borrar"]}, "texto": {"type": "string"}}, "required": ["accion"]}},
    {"name": "abrir", "description": "Abre en el PC un sitio web (youtube, gmail, whatsapp, tradingview, noticias, una dirección web), una app (calculadora, bloc de notas) o una búsqueda en Google.",
     "input_schema": {"type": "object", "properties": {"que": {"type": "string"}}, "required": ["que"]}},
]
FUNCS = {"crear_recordatorio": crear_recordatorio, "ver_recordatorios": ver_recordatorios,
         "borrar_recordatorio": borrar_recordatorio, "tareas": tareas, "abrir": abrir}
