"""Configuración del servidor de Axtra (variables de entorno o archivo .env)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")


def _f(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return default


USER_NAME = os.getenv("AXTRA_USUARIO", "Felipe")
DATA_DIR = Path(os.getenv("AXTRA_DATOS", BASE / "datos"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
FILES_DIR = DATA_DIR / "archivos"
FILES_DIR.mkdir(exist_ok=True)

# ---------- Cerebros gratis ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASICO = os.getenv("GROQ_MODELO_BASICO", "openai/gpt-oss-20b")         # charla: rápido
GROQ_INTERMEDIO = os.getenv("GROQ_MODELO_INTERMEDIO", "openai/gpt-oss-120b")  # explicar, resumir, planear
GROQ_MODELO_OIDO = os.getenv("GROQ_MODELO_OIDO", "whisper-large-v3-turbo")        # tu voz a texto (gratis)
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
CEREBRAS_MODELO = os.getenv("CEREBRAS_MODELO", "gpt-oss-120b")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODELO = os.getenv("GEMINI_MODELO", "gemini-flash-latest")
GEMINI_MODELO_IMAGEN = os.getenv("GEMINI_MODELO_IMAGEN", "gemini-2.5-flash-image")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODELO = os.getenv("OPENROUTER_MODELO", "openrouter/free")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# ---------- Cerebros de pago ----------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_BARATO = os.getenv("CLAUDE_MODELO_BARATO", "claude-haiku-4-5")    # lo personal sencillo
CLAUDE_NORMAL = os.getenv("CLAUDE_MODELO", "claude-sonnet-5-5")           # documentos y herramientas
CLAUDE_FUERTE = os.getenv("CLAUDE_MODELO_FUERTE", "claude-opus-5-5")     # "piénsalo bien", lo importante
XAI_API_KEY = os.getenv("XAI_API_KEY", "")                                # Grok: vacío = desactivado
GROK_MODELO = os.getenv("GROK_MODELO", "grok-4-latest")

# Topes de gasto mensual en dólares (al llegar, ese cerebro se pausa hasta el mes siguiente)
TOPE_CLAUDE_USD = _f("TOPE_CLAUDE_USD", 10)
TOPE_GROK_USD = _f("TOPE_GROK_USD", 10)
# Si todos los cerebros gratis fallan, ¿puede responder Claude (barato) para no dejarte sin respuesta?
PAGO_DE_RESPALDO = os.getenv("PAGO_DE_RESPALDO", "1") == "1"

# Precio por millón de tokens (entrada, salida). Grok: revisa el precio real en la consola de xAI.
PRECIOS = {
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-opus-5-5": (4.0, 20.0),
    GROK_MODELO: (_f("GROK_PRECIO_ENTRADA", 3.0), _f("GROK_PRECIO_SALIDA", 15.0)),
}

# ---------- Voz (edge-tts, gratis): la misma voz de mayordomo del Axtra del PC ----------
VOZ_AXTRA = os.getenv("VOZ_AXTRA", "es-ES-AlvaroNeural")
VOZ_VELOCIDAD = os.getenv("VOZ_VELOCIDAD", "+4%")
VOZ_TONO = os.getenv("VOZ_TONO", "-12Hz")

# ---------- Orbes de los negocios (Apex Play): Axtra es su tarjeta madre ----------
# Voz natural de Google Cloud Text-to-Speech (1 millón de caracteres gratis al mes). Vacío = voz gratis de Axtra.
GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY", "")
ORBE_MODELO = os.getenv("ORBE_MODELO", "openai/gpt-oss-20b")        # cerebro de los orbes (Groq)
ORBE_MODELO_OIDO = os.getenv("ORBE_MODELO_OIDO", "whisper-large-v3")   # oído de los orbes: el más preciso de Groq
# Ranura privada: solo la usan los orbes desde dentro del servidor (nunca pasa por el túnel)
RANURA_PUERTO = int(os.getenv("RANURA_PUERTO", "8090"))

# ---------- Acceso (Cloudflare Access: solo tu cuenta de Google entra) ----------
CF_ACCESS_EQUIPO = os.getenv("CF_ACCESS_EQUIPO", "")   # ej: axtra  (de axtra.cloudflareaccess.com)
CF_ACCESS_AUD = os.getenv("CF_ACCESS_AUD", "")
CORREO_PERMITIDO = os.getenv("AXTRA_CORREO", "").lower()
# Token de servicio de Cloudflare Access que usa el Axtra del PC para subir tus datos (su "Client ID")
CF_SERVICIO_ID = os.getenv("CF_ACCESS_SERVICIO_ID", "")
ZONA_HORARIA = os.getenv("AXTRA_ZONA", "America/Bogota")
# Solo para probar en tu computador, nunca en el servidor publicado
MODO_DESARROLLO = os.getenv("AXTRA_MODO", "") == "desarrollo"
