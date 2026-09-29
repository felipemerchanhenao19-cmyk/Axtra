"""Control de gastos: cuenta los tokens y búsquedas que usa Axtra y estima el costo en dólares."""
import json
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

from config import DATA_DIR, PRICE_IN, PRICE_OUT, PRICE_SEARCH, TIMEZONE

PATH = DATA_DIR / "gastos.json"
_lock = threading.Lock()


def _load():
    try:
        return json.loads(PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def record(resp, origen: str = "conversación") -> None:
    u = getattr(resp, "usage", None)
    if u is None:
        return
    inp = getattr(u, "input_tokens", 0) or 0
    out = getattr(u, "output_tokens", 0) or 0
    cread = getattr(u, "cache_read_input_tokens", 0) or 0
    cwrite = getattr(u, "cache_creation_input_tokens", 0) or 0
    stu = getattr(u, "server_tool_use", None)
    searches = (getattr(stu, "web_search_requests", 0) or 0) if stu else 0
    cost = (inp * PRICE_IN + cwrite * PRICE_IN * 1.25 + cread * PRICE_IN * 0.1 + out * PRICE_OUT) / 1e6
    cost += searches * PRICE_SEARCH
    day = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d")
    with _lock:
        d = _load()
        e = d.setdefault(day, {"usd": 0.0, "llamadas": 0, "busquedas": 0, "por_origen": {}})
        e["usd"] = round(e["usd"] + cost, 5)
        e["llamadas"] += 1
        e["busquedas"] += searches
        e["por_origen"][origen] = round(e["por_origen"].get(origen, 0) + cost, 5)
        PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def record_local(kind: str = "local") -> None:
    """Cuenta respuestas gratis: kind = 'local' (cerebro en el PC) o 'directo' (orden sin IA)."""
    day = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d")
    with _lock:
        d = _load()
        e = d.setdefault(day, {"usd": 0.0, "llamadas": 0, "busquedas": 0, "por_origen": {}})
        e[f"gratis_{kind}"] = e.get(f"gratis_{kind}", 0) + 1
        PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def cuanto_he_gastado() -> dict:
    d = _load()
    days = sorted(d)
    today = d.get(days[-1], {}) if days else {}
    last7 = [d[k]["usd"] for k in days[-7:]]
    avg = sum(last7) / len(last7) if last7 else 0
    return {
        "hoy_usd": round(today.get("usd", 0), 3),
        "hoy_por_origen": today.get("por_origen", {}),
        "hoy_respuestas_gratis_cerebro_local": today.get("gratis_local", 0),
        "hoy_respuestas_gratis_gemini": today.get("gratis_gemini", 0),
        "hoy_respuestas_gratis_groq": today.get("gratis_groq", 0),
        "hoy_respuestas_gratis_openrouter": today.get("gratis_openrouter", 0),
        "hoy_ordenes_directas_sin_ia": today.get("gratis_directo", 0),
        "promedio_diario_usd": round(avg, 3),
        "total_registrado_usd": round(sum(v["usd"] for v in d.values()), 3),
        "dias_que_dura_5_usd_a_este_ritmo": round(5 / avg, 1) if avg else None,
        "nota": "Es una estimación; el saldo exacto está en console.anthropic.com.",
    }


TOOL_SCHEMAS = [{
    "name": "cuanto_he_gastado",
    "description": "Cuánto dinero ha gastado Axtra en la API (hoy, promedio diario y cuánto dura el saldo).",
    "input_schema": {"type": "object", "properties": {}},
}]
FUNCS = {"cuanto_he_gastado": cuanto_he_gastado}
