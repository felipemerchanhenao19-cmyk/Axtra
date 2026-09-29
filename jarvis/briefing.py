"""Rutinas diarias: briefing matutino e informe del mercado al cierre."""
import json

import finance
import google_services
import skills
from config import USER_NAME

INDICES = {"S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Dow Jones": "^DJI", "Dólar en Colombia": "COP=X"}


def _safe(fn, *a, **k):
    try:
        return fn(*a, **k)
    except Exception as e:
        return {"no_disponible": str(e)[:120]}


def market_snapshot() -> dict:
    out = {}
    for name, s in INDICES.items():
        q = _safe(finance.cotizacion, s)
        out[name] = {"precio": q.get("precio"), "cambio_pct": q.get("cambio_dia_pct")} if "precio" in q else q
    for s in finance.watchlist()[:8]:
        q = _safe(finance.cotizacion, s)
        out[s] = {"precio": q.get("precio"), "cambio_pct": q.get("cambio_dia_pct")} if "precio" in q else q
    return out


def briefing_data() -> dict:
    """Todo lo que Jarvis necesita para el briefing de la mañana."""
    import autonomy
    import business
    from tools import get_datetime, get_weather

    data = {
        "fecha": get_datetime(),
        "clima": _safe(get_weather),
        "tareas": _safe(skills.tareas, "ver"),
        "recordatorios": _safe(skills.ver_recordatorios),
        "clientes_para_contactar_hoy": _safe(business.crm_ver, "hoy"),
        "mercado_ultimo_cierre": _safe(market_snapshot),
        "aprendido_mientras_dormia": _safe(autonomy.que_aprendiste).get("aprendido_recientemente", [])[-3:],
    }
    if google_services.available():
        data["agenda_proximas_3_horas"] = _safe(google_services.agenda, 3)
        data["agenda_resto_del_dia"] = _safe(google_services.agenda, 16)
        data["correos_sin_leer"] = _safe(google_services.correos, "is:unread newer_than:1d", 6)
    else:
        data["agenda"] = "Google Calendar no está conectado (ver LEEME)."
    return data


BRIEFING_PROMPT = (
    f"Eres JARVIS, mayordomo de IA de {USER_NAME}. Con estos datos, dale los buenos días y su briefing "
    "matutino HABLADO (se convierte en voz): saludo cálido y breve, clima, lo que tiene en las primeras "
    "3 horas y lo importante del resto del día, tareas pendientes, clientes a contactar, correos "
    "importantes, cómo cerró el mercado y una idea o dato interesante que aprendiste. Máximo 150 "
    "palabras, sin listas ni markdown, cifras redondeadas. Termina con una frase motivadora con humor seco."
)

MARKET_PROMPT = (
    f"Eres JARVIS, analista financiero personal de {USER_NAME}. Con estos datos del cierre y buscando en "
    "internet por qué se movió hoy el mercado de Nueva York, escribe el INFORME DIARIO DEL MERCADO en "
    "markdown: resumen del día, índices, sus acciones en seguimiento y su portafolio, noticias que "
    "movieron el mercado, qué vigilar mañana y tu opinión. Al final una línea que empiece con "
    "'HABLADO:' con un resumen de máximo 60 palabras para decirlo en voz alta, sin markdown."
)


def portfolio_snapshot() -> dict:
    return _safe(finance.portafolio_ver)


def to_json(d) -> str:
    return json.dumps(d, ensure_ascii=False, default=str)[:12000]


TOOL_SCHEMAS = [
    {"name": "datos_briefing", "description": "Reúne clima, agenda, tareas, clientes a contactar, correos y mercado para dar el briefing del día cuando Felipe lo pida.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "resumen_mercado", "description": "Precios y cambio del día de los índices principales, el dólar y la lista de seguimiento.",
     "input_schema": {"type": "object", "properties": {}}},
]
FUNCS = {"datos_briefing": briefing_data, "resumen_mercado": market_snapshot}
