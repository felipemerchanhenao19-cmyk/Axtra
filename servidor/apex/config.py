"""Configuración de Apex Play. Aquí NO hay claves: el oído, el cerebro y la voz los presta Axtra (la tarjeta
madre) por su ranura privada. Los datos de cada restaurante están en restaurantes/*.json."""
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("APEX_DATOS", BASE / "datos"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR = DATA_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)
RANURA_URL = os.getenv("RANURA_URL", "http://axtra:8090").rstrip("/")
RANURA_CLAVE = os.getenv("RANURA_CLAVE", "")
MODO_DESARROLLO = os.getenv("APEX_MODO", "") == "desarrollo"     # permite http://localhost como origen
COP_POR_USD = float(os.getenv("APEX_COP_POR_USD", "4000"))

# Precios en dólares (revisarlos de vez en cuando). Se calculan a precio de lista, sin restar lo gratis:
# el costo real suele ser menor (p. ej. Google regala 1 millón de caracteres de voz al mes).
PRECIOS_USD = {
    "oido_groq_hora": 0.04,          # Groq Whisper turbo, mínimo 10 s por audio
    "cerebro": {                      # por millón de tokens (entrada, salida)
        "groq": (0.075, 0.30),        # gpt-oss-20b
        "gemini": (0.30, 2.50),       # respaldo
    },
    # Google cobra según el tipo de voz (por millón de caracteres). edge = la voz gratis de Axtra.
    "voz_millon_caracteres": {"Chirp3-HD": 30.0, "Studio": 30.0, "Neural2": 16.0, "Wavenet": 16.0,
                              "Standard": 4.0, "edge": 0.0},
}

TOPES_POR_DEFECTO = {"tope_cop_mes": 80000, "minutos_por_sesion": 15, "turnos_por_sesion": 60}

FRASES_POR_DEFECTO = {
    "saludo": "Estoy a su servicio, espero su pedido; si tiene dudas, lo atenderé.",
    "eleccion": "Muy buena elección.",
    "despedida": "Fue un placer atenderlo, si tiene alguna duda indíqueme.",
    "repetir": "Disculpe, no le escuché bien. ¿Me lo repite, por favor?",
    "vacio": "Aún no ha seleccionado ningún plato. ¿Qué le provoca?",
    "mesero": "Con gusto, enseguida va un mesero a su mesa.",
    "sin_voz": "En este momento no puedo atenderle por voz. Toque «Llamar al mesero» y con gusto le atienden.",
}


def restaurantes() -> dict:
    """Lee restaurantes/*.json (uno por restaurante). Se relee en cada llamada: editar el archivo basta."""
    out = {}
    for f in sorted((BASE / "restaurantes").glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        r.setdefault("id", f.stem)
        r["topes"] = {**TOPES_POR_DEFECTO, **r.get("topes", {})}
        r["frases"] = {**FRASES_POR_DEFECTO, **r.get("frases", {})}
        r.setdefault("voz", {})
        out[r["id"]] = r
    return out


def restaurante(rid: str):
    return restaurantes().get(rid)

