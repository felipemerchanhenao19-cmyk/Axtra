"""Modo compañero: Jarvis te habla por iniciativa propia mientras usas el computador.

Cuándo habla:
- Solo si estás usando el PC (teclado o mouse en el último minuto) y dentro de tus horas activas.
- Cada cierto tiempo (por defecto unos 45 minutos, con algo de variación) y nunca justo después
  de que hayan hablado, ni con música puesta, ni en clases, dictados o videollamadas.
- Te saluda la primera vez que usas el PC en el día, te pregunta por tu día, comenta algo útil
  (agenda, mercado, clientes, algo que aprendió) o te sugiere una pausa si llevas mucho tiempo.
- Puedes responderle SIN decir "Jarvis" durante unos segundos después de que te habla.
- "Jarvis, no me hables por una hora" lo silencia; "Jarvis, háblame más seguido" cambia la frecuencia.

Privacidad: para saber qué haces solo usa el TIPO de programa (navegador, Word, código...),
nunca el contenido de la pantalla.
"""
import json
import random
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import usage
from config import (BRAIN_MODE, CHAT_ACTIVE_HOURS, CHAT_EVERY_MIN, CHAT_ENABLED,
                    DATA_DIR, TIMEZONE, USER_NAME)

STATE_PATH = DATA_DIR / "companero.json"
brain = None          # main.py conecta el cerebro para que Jarvis recuerde lo que dijo
_invite_until = 0.0
_replied = False
_last_talk = time.time()   # última vez que hablaron (cualquier conversación)
_lock = threading.Lock()

QUIET_APPS = ("zoom", "meet", "teams", "skype", "discord", "obs", "webex")
APP_TYPES = {
    "navegador": ("chrome", "brave", "edge", "firefox", "opera"),
    "Word": ("word",), "Excel": ("excel",), "PowerPoint": ("powerpoint",),
    "programación": ("visual studio", "code", "pycharm", "powershell", "terminal", "cmd"),
    "YouTube": ("youtube",), "WhatsApp": ("whatsapp",), "TradingView": ("tradingview",),
    "Netflix/video": ("netflix", "prime video", "disney"), "juego": ("steam", "epic games", "minecraft"),
}


def _now():
    return datetime.now(ZoneInfo(TIMEZONE))


def _state():
    try:
        st = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        st = {}
    st.setdefault("silencio_hasta", 0)
    st.setdefault("cada_min", CHAT_EVERY_MIN)
    st.setdefault("ultimas_frases", [])
    st.setdefault("saludo_dia", "")
    return st


def _save(st):
    with _lock:
        STATE_PATH.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------- Invitación a responder sin decir "Jarvis" ----------
def open_invite(seconds: float = 15) -> None:
    global _invite_until
    _invite_until = time.time() + seconds


def invited() -> bool:
    return time.time() < _invite_until


def close_invite(replied: bool = False) -> None:
    global _invite_until, _replied
    _invite_until = 0.0
    _replied = replied


def take_reply() -> bool:
    global _replied
    r, _replied = _replied, False
    return r


def touch() -> None:
    """main.py lo llama en cada conversación, para no interrumpir justo después."""
    global _last_talk
    _last_talk = time.time()


# ---------- ¿Qué está haciendo en el PC? (solo Windows) ----------
def idle_seconds():
    try:
        import ctypes

        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        li = LASTINPUTINFO()
        li.cbSize = ctypes.sizeof(li)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li))
        return (ctypes.windll.kernel32.GetTickCount() - li.dwTime) / 1000
    except Exception:
        return None


def active_window() -> str:
    try:
        import ctypes

        hwnd = ctypes.windll.user32.GetForegroundWindow()
        buf = ctypes.create_unicode_buffer(512)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, 512)
        return buf.value.lower()
    except Exception:
        return ""


def app_type(title: str) -> str:
    for name, keys in APP_TYPES.items():
        if any(k in title for k in keys):
            return name
    return "otro programa" if title else "desconocido"


# ---------- Herramientas ----------
def modo_silencio(minutos: float = 60) -> dict:
    st = _state()
    st["silencio_hasta"] = time.time() + float(minutos) * 60
    _save(st)
    return {"ok": True, "nota": f"No hablaré por iniciativa propia durante {minutos:.0f} minutos."}


def frecuencia_charla(minutos: float) -> dict:
    st = _state()
    st["cada_min"] = max(10, float(minutos))
    st["silencio_hasta"] = 0
    _save(st)
    return {"ok": True, "cada_min": st["cada_min"]}


TOOL_SCHEMAS = [
    {"name": "modo_silencio", "description": "Jarvis deja de hablar por iniciativa propia durante X minutos (sigue respondiendo si le hablan).",
     "input_schema": {"type": "object", "properties": {"minutos": {"type": "number"}}}},
    {"name": "frecuencia_charla", "description": "Cada cuántos minutos (aprox.) Jarvis inicia conversación mientras Felipe usa el PC. También desactiva el silencio.",
     "input_schema": {"type": "object", "properties": {"minutos": {"type": "number"}}, "required": ["minutos"]}},
]
FUNCS = {"modo_silencio": modo_silencio, "frecuencia_charla": frecuencia_charla}


# ---------- Motor ----------
PROMPT = (
    f"Eres JARVIS, el mayordomo de IA de {USER_NAME} (18 años, emprendedor en Tuluá, Colombia: "
    "ventas, páginas web, bolsa, IA). Él está usando el computador y TÚ inicias la conversación. "
    "Di UNA sola intervención corta (máximo 30 palabras), natural y cálida, con tu humor seco de "
    "mayordomo británico. Elige lo más oportuno según el contexto: un saludo si es la primera vez "
    "del día, preguntarle cómo va su día o su trabajo, un recordatorio útil de su agenda o sus "
    "clientes, un dato del mercado o algo interesante que aprendiste, una idea para su negocio, o "
    "sugerirle una pausa si lleva mucho tiempo en el PC. A veces termina con una pregunta. No repitas "
    "las frases anteriores. Sin listas ni emojis. Responde SOLO con lo que vas a decir."
)


class Companion(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.active_since = None
        self.next_at = time.time() + random.uniform(5, 12) * 60

    def _in_hours(self) -> bool:
        try:
            a, b = CHAT_ACTIVE_HOURS.split("-")
            return a <= _now().strftime("%H:%M") <= b
        except ValueError:
            return True

    def _blocked(self) -> str:
        import dictation
        import language
        import media

        title = active_window()
        if any(q in title for q in QUIET_APPS):
            return "videollamada"
        if media.playing or dictation.pending or language.pending:
            return "ocupado"
        if time.time() - _last_talk < 8 * 60:
            return "hablaron hace poco"
        return ""

    def _context(self, first_today: bool, st) -> dict:
        import autonomy
        import briefing
        import business
        import google_services
        import skills

        mins = round((time.time() - self.active_since) / 60) if self.active_since else 0
        ctx = {
            "fecha_hora": _now().strftime("%A %d de %B, %I:%M %p"),
            "primera_vez_hoy_en_el_pc": first_today,
            "minutos_seguidos_en_el_pc": mins,
            "programa_que_usa": app_type(active_window()),
            "tareas_pendientes": briefing._safe(skills.tareas, "ver").get("pendientes", [])[:5],
            "clientes_para_hoy": [c["nombre"] for c in briefing._safe(business.crm_ver, "hoy").get("clientes", [])][:5],
            "aprendido_recientemente": briefing._safe(autonomy.que_aprendiste).get("aprendido_recientemente", [])[-2:],
            "frases_anteriores_no_repetir": st["ultimas_frases"][-6:],
        }
        if google_services.available():
            ctx["agenda_proximas_horas"] = briefing._safe(google_services.agenda, 4)
        return ctx

    def speak_up(self):
        import autonomy

        st = _state()
        today = _now().strftime("%Y-%m-%d")
        first = st["saludo_dia"] != today
        ctx = self._context(first, st)
        import llm

        # En modo híbrido o local lo dice el cerebro local (gratis)
        line = llm.ask_text(PROMPT, [{"role": "user", "content": json.dumps(ctx, ensure_ascii=False, default=str)}],
                            prefer="claude" if BRAIN_MODE == "claude" else "local", max_tokens=120,
                            origen="modo compañero", temperature=0.9)
        import re

        line = re.sub(r"^\s*(jarvis|asistente)\s*:\s*", "", line.replace("[AVANZADO]", ""), flags=re.I)
        line = line.strip().strip('"').strip()
        if not line:
            return
        st["saludo_dia"] = today
        st["ultimas_frases"] = (st["ultimas_frases"] + [line])[-12:]
        _save(st)
        if brain is not None:  # para que entienda tu respuesta
            brain.history += [{"role": "user", "content": "(Felipe está en el PC; Jarvis inicia la conversación)"},
                              {"role": "assistant", "content": line}]
            brain.history = brain.history[-12:]
        if autonomy.speaker:
            autonomy.speaker(line)
            open_invite(15)

    def run(self):
        while True:
            try:
                idle = idle_seconds()
                if idle is None:
                    return  # no es Windows: sin modo compañero
                now = time.time()
                if idle < 60:
                    self.active_since = self.active_since or now
                elif idle > 10 * 60:
                    self.active_since = None  # se fue del PC: la próxima vez cuenta como regreso
                st = _state()
                using = idle < 60 and self.active_since and now - self.active_since > 90
                if (using and now >= self.next_at and now > st["silencio_hasta"]
                        and self._in_hours() and not self._blocked()):
                    self.speak_up()
                    every = st["cada_min"] * 60
                    self.next_at = now + random.uniform(0.7, 1.3) * every
            except Exception as e:
                print(f"  (compañero: {e})")
            time.sleep(30)


def start():
    if CHAT_ENABLED:
        Companion().start()
        print(f"  - Modo compañero activo (te hablará cada ~{CHAT_EVERY_MIN} min mientras usas el PC)")
