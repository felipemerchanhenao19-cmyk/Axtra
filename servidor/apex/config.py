"""Configuración de Apex Play (claves en apex.env, datos de cada restaurante en restaurantes/*.json)."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE.parent / "apex.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_URL = os.getenv("OPENAI_URL", "https://api.openai.com/v1")
MODELO = os.getenv("APEX_MODELO", "gpt-realtime-2.1-mini")       # cada restaurante puede usar otro
DATA_DIR = Path(os.getenv("APEX_DATOS", BASE / "datos"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODO_DESARROLLO = os.getenv("APEX_MODO", "") == "desarrollo"     # permite http://localhost como origen

# USD por millón de tokens. Revísalos en la página de precios de OpenAI y ajústalos en apex.env si cambian.
PRECIOS = {
    "gpt-realtime-2.1-mini": {"audio_in": 10.0, "audio_in_cache": 0.30, "audio_out": 20.0,
                              "texto_in": 0.60, "texto_in_cache": 0.06, "texto_out": 2.40},
    "gpt-realtime-2.1": {"audio_in": 32.0, "audio_in_cache": 0.40, "audio_out": 64.0,
                         "texto_in": 4.0, "texto_in_cache": 0.40, "texto_out": 16.0},
}
if os.getenv("APEX_PRECIOS"):
    PRECIOS.update(json.loads(os.environ["APEX_PRECIOS"]))

TOPES_POR_DEFECTO = {"sesiones_mes": 1500, "minutos_mes": 1500, "usd_mes": 40, "minutos_por_sesion": 8}


def restaurantes() -> dict:
    """Lee restaurantes/*.json (uno por restaurante). Se relee en cada llamada: editar el archivo basta."""
    out = {}
    for f in sorted((BASE / "restaurantes").glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        r.setdefault("id", f.stem)
        r["topes"] = {**TOPES_POR_DEFECTO, **r.get("topes", {})}
        r.setdefault("modelo", MODELO)
        out[r["id"]] = r
    return out


def restaurante(rid: str):
    return restaurantes().get(rid)


def pin(r: dict) -> str:
    """El PIN del panel del mesero vive en apex.env (APEX_PIN_<ID>), nunca en GitHub."""
    return os.getenv(r.get("pin_env") or f"APEX_PIN_{r['id'].upper()}", "")
