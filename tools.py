"""Herramientas que Axtra puede usar por su cuenta."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from config import CITY, LATITUDE, LONGITUDE, TIMEZONE

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

WEATHER_CODES = {
    0: "despejado", 1: "mayormente despejado", 2: "parcialmente nublado", 3: "nublado",
    45: "niebla", 48: "niebla", 51: "llovizna ligera", 53: "llovizna", 55: "llovizna fuerte",
    61: "lluvia ligera", 63: "lluvia", 65: "lluvia fuerte", 80: "chubascos ligeros",
    81: "chubascos", 82: "chubascos fuertes", 95: "tormenta", 96: "tormenta con granizo",
    99: "tormenta fuerte con granizo",
}


def get_datetime() -> dict:
    now = datetime.now(ZoneInfo(TIMEZONE))
    return {
        "fecha": f"{DIAS[now.weekday()]} {now.day} de {MESES[now.month - 1]} de {now.year}",
        "hora": now.strftime("%I:%M %p"),
    }


def get_weather() -> dict:
    """Clima actual y del día desde Open-Meteo (gratis, sin clave)."""
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
            "timezone": TIMEZONE,
            "forecast_days": 1,
        },
        timeout=10,
    )
    r.raise_for_status()
    d = r.json()
    cur, day = d["current"], d["daily"]
    return {
        "ciudad": CITY,
        "ahora": {
            "temperatura_c": cur["temperature_2m"],
            "sensacion_c": cur["apparent_temperature"],
            "humedad_pct": cur["relative_humidity_2m"],
            "viento_kmh": cur["wind_speed_10m"],
            "estado": WEATHER_CODES.get(cur["weather_code"], "variable"),
        },
        "hoy": {
            "maxima_c": day["temperature_2m_max"][0],
            "minima_c": day["temperature_2m_min"][0],
            "prob_lluvia_pct": day["precipitation_probability_max"][0],
            "estado": WEATHER_CODES.get(day["weather_code"][0], "variable"),
        },
    }


# Definiciones que se le envían a Claude
TOOL_SCHEMAS = [
    {
        "name": "get_weather",
        "description": f"Clima actual y pronóstico de hoy en {CITY}.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_datetime",
        "description": "Fecha y hora actuales en Colombia.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

import autonomy  # noqa: E402
import finance  # noqa: E402
import memory  # noqa: E402
import skills  # noqa: E402
import usage  # noqa: E402
import briefing  # noqa: E402
import business  # noqa: E402
import dictation  # noqa: E402
import finance_pro  # noqa: E402
import google_services  # noqa: E402
import language  # noqa: E402
import media  # noqa: E402
import vision  # noqa: E402
import companion  # noqa: E402

TOOL_SCHEMAS += (memory.TOOL_SCHEMAS + finance.TOOL_SCHEMAS + autonomy.TOOL_SCHEMAS + usage.TOOL_SCHEMAS + skills.TOOL_SCHEMAS
                 + finance_pro.TOOL_SCHEMAS + google_services.TOOL_SCHEMAS + business.TOOL_SCHEMAS
                 + dictation.TOOL_SCHEMAS + briefing.TOOL_SCHEMAS + media.TOOL_SCHEMAS
                 + language.TOOL_SCHEMAS + vision.TOOL_SCHEMAS
                 + companion.TOOL_SCHEMAS)

_FUNCS = {"get_weather": get_weather, "get_datetime": get_datetime,
          **memory.FUNCS, **finance.FUNCS, **autonomy.FUNCS, **usage.FUNCS, **skills.FUNCS,
          **finance_pro.FUNCS, **google_services.FUNCS, **business.FUNCS, **dictation.FUNCS,
          **briefing.FUNCS, **media.FUNCS, **language.FUNCS, **vision.FUNCS, **companion.FUNCS}


def run_tool(name: str, args: dict):
    """Devuelve texto JSON, o una lista [imagen, texto] cuando la herramienta toma una foto."""
    try:
        value = _FUNCS[name](**(args or {}))
        if isinstance(value, dict) and "__imagen_b64__" in value:
            img = value.pop("__imagen_b64__")
            return [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img}},
                    {"type": "text", "text": json.dumps(value, ensure_ascii=False)}]
        return json.dumps(value, ensure_ascii=False)
    except Exception as e:  # la IA recibe el error y lo explica
        print(f"  (error en herramienta {name}: {e})")
        return json.dumps({"error": str(e)}, ensure_ascii=False)
