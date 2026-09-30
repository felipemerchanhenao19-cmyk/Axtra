"""Configuración central de Axtra. Los valores se pueden cambiar en el archivo .env"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Usa los certificados de Windows (necesario con antivirus como Kaspersky
# que revisan las conexiones seguras). Si no está instalado, sigue normal.
try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# --- Cerebro (Claude) ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("JARVIS_MODEL", "claude-haiku-4-5")

# Precios en dólares por millón de tokens (para estimar gastos). Revisa los actuales en anthropic.com
PRICE_IN = float(os.getenv("JARVIS_PRECIO_ENTRADA", "1"))
PRICE_OUT = float(os.getenv("JARVIS_PRECIO_SALIDA", "5"))
PRICE_SEARCH = 0.01  # por búsqueda web

# --- Cerebro local (Ollama, gratis y sin internet) ---
# JARVIS_CEREBRO: hibrido (recomendado) | claude (todo con Claude) | local (nunca gasta saldo)
BRAIN_MODE = os.getenv("JARVIS_CEREBRO", "hibrido").lower()
# Modelo local: qwen2.5:3b (equilibrado) | qwen2.5:1.5b (más rápido, más simple)
LOCAL_MODEL = os.getenv("JARVIS_MODELO_LOCAL", "qwen2.5:3b")
# Cuánto tiempo queda cargado el cerebro local sin usarse (más tiempo = responde rápido tras una pausa)
LOCAL_KEEP_ALIVE = os.getenv("JARVIS_MANTENER_CEREBRO", "4h")
OLLAMA_URL = os.getenv("JARVIS_OLLAMA_URL", "http://localhost:11434")
# --- Gemini (Google): cerebro en la nube con plan gratuito, para charla e idiomas ---
# Clave gratis en aistudio.google.com. Vacío = no se usa.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("JARVIS_MODELO_GEMINI", "gemini-flash-latest")
# Quién responde la charla: gemini (más listo y rápido, necesita internet) o local
# --- Más cerebros gratis (se usan en este orden cuando uno se queda sin cuota) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")            # console.groq.com (gratis)
GROQ_MODEL = os.getenv("JARVIS_MODELO_GROQ", "openai/gpt-oss-120b")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")  # openrouter.ai (modelos :free)
OPENROUTER_MODEL = os.getenv("JARVIS_MODELO_OPENROUTER", "openrouter/free")
FREE_BRAINS = [b.strip() for b in os.getenv("JARVIS_CEREBROS_GRATIS", "gemini,groq,openrouter").lower().split(",") if b.strip()]
# Búsqueda gratis en internet: Tavily (1000/mes con clave gratis en tavily.com) y DuckDuckGo (sin clave)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
# Preguntas e ideas sobre Apex: gemini/gratis (cerebros gratis) o claude (gasta saldo)
BUSINESS_BRAIN = os.getenv("JARVIS_CEREBRO_NEGOCIO", "gemini").lower()
CHAT_BRAIN = os.getenv("JARVIS_CEREBRO_CHARLA", "gemini").lower()
# Clases de idiomas: local (gratis) o claude (mejor calidad, gasta saldo)
LANGUAGE_BRAIN = os.getenv("JARVIS_CEREBRO_IDIOMAS", "gemini").lower()  # gemini | local | claude

# --- Usuario y ubicación ---
USER_NAME = os.getenv("JARVIS_USER_NAME", "Felipe")
CITY = os.getenv("JARVIS_CITY", "Tuluá")
REGION = os.getenv("JARVIS_REGION", "Valle del Cauca")
COUNTRY_CODE = "CO"
LATITUDE = float(os.getenv("JARVIS_LAT", "4.0847"))
LONGITUDE = float(os.getenv("JARVIS_LON", "-76.1954"))
TIMEZONE = "America/Bogota"

# --- Voz de Axtra (edge-tts, gratis) ---
# Otras opciones: es-CO-SalomeNeural (mujer), es-MX-JorgeNeural, es-ES-AlvaroNeural
# Estilos listos: "mayordomo" (voz mayor, grave y pausada, estilo Alfred) o "colombiano"
VOICE_PRESETS = {
    "mayordomo": ("es-ES-AlvaroNeural", "-8%", "-12Hz"),
    "colombiano": ("es-CO-GonzaloNeural", "+5%", "+0Hz"),
    "mexicano": ("es-MX-JorgeNeural", "+0%", "-5Hz"),
}
_preset = VOICE_PRESETS.get(os.getenv("JARVIS_VOZ_ESTILO", "mayordomo").lower(), VOICE_PRESETS["mayordomo"])
TTS_VOICE = os.getenv("JARVIS_VOICE", _preset[0])
TTS_RATE = os.getenv("JARVIS_VOICE_RATE", _preset[1])
TTS_PITCH = os.getenv("JARVIS_VOICE_PITCH", _preset[2])

# --- Voz clonada (ElevenLabs) ---
# JARVIS_TTS_PROVIDER=edge (gratis) o elevenlabs (voz clonada)
TTS_PROVIDER = os.getenv("JARVIS_TTS_PROVIDER", "edge").lower()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
# eleven_flash_v2_5 = rápido y barato | eleven_multilingual_v2 = más natural
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_flash_v2_5")

# --- Oído ---
# "small" entiende mejor el español; si tu PC va lento, usa "base"
WHISPER_MODEL = os.getenv("JARVIS_WHISPER_MODEL", "small")
# "es" = di "Axtra" en español | "en" = di "Hey Axtra" en inglés
WAKE_MODE = os.getenv("JARVIS_WAKE_MODE", "es").lower()
WAKE_MODEL = os.getenv("JARVIS_WAKE_MODEL", "base")
WAKEWORD_THRESHOLD = float(os.getenv("JARVIS_WAKE_THRESHOLD", "0.5"))
# Volumen mínimo para considerar que alguien habla (tu voz normal da 250-450)
MIN_SPEECH_LEVEL = float(os.getenv("JARVIS_MIN_SPEECH_LEVEL", "60"))
# Micrófono a usar (parte del nombre, p. ej. "USB"). Vacío = el predeterminado de Windows.
MIC_DEVICE = os.getenv("JARVIS_MICROFONO", "").strip()
# Segundos de silencio para saber que terminaste de hablar (súbelo si te corta)
END_PAUSE = float(os.getenv("JARVIS_PAUSA_FINAL", "0.5"))
# Reconocimiento de voz: google (gratis, en la nube, entiende mejor) o whisper (local)
STT_PROVIDER = os.getenv("JARVIS_RECONOCIMIENTO", "google").lower()
STT_LANGUAGE = os.getenv("JARVIS_IDIOMA", "es-CO")
# Interrumpir a Axtra mientras habla diciendo "Axtra, para" / "detente" / "basta"
BARGE_IN = os.getenv("JARVIS_INTERRUMPIR", "1") == "1"
FOLLOW_UP_SECONDS = float(os.getenv("JARVIS_FOLLOW_UP_SECONDS", "10"))

# --- Aprendizaje autónomo ---
AUTONOMY = os.getenv("JARVIS_AUTONOMIA", "1") == "1"
# Cerebro del modo autónomo (estudios, informe del mercado, briefing, reflexión): gemini (gratis) o claude
AUTONOMY_BRAIN = os.getenv("JARVIS_CEREBRO_AUTONOMO", "gemini").lower()
STUDIES_PER_DAY = int(os.getenv("JARVIS_ESTUDIOS_POR_DIA", "3"))
STUDY_EVERY_HOURS = float(os.getenv("JARVIS_HORAS_ENTRE_ESTUDIOS", "4"))
INTERESTS = [t.strip() for t in os.getenv(
    "JARVIS_INTERESES",
    "Bolsa de Nueva York: qué movió el mercado hoy;Inteligencia artificial: avances y empresas;"
    "Robótica y robots humanoides;Semiconductores y chips de IA;"
    "Estrategias de inversión y gestión de riesgo;Economía de Colombia y el dólar;"
    "Ideas de negocio con IA para Latinoamérica",
).split(";") if t.strip()]

# --- Rutinas diarias ---
BRIEFING_TIME = os.getenv("JARVIS_BRIEFING_HORA", "06:30")        # "" para desactivar
MARKET_REPORT_TIME = os.getenv("JARVIS_INFORME_MERCADO_HORA", "16:15")  # después del cierre de NY
# Correo de contacto que pide la SEC (EE. UU.) para datos fundamentales; pon el tuyo en .env
SEC_CONTACT = os.getenv("JARVIS_CONTACTO_SEC", "")

# --- Modo compañero: Axtra te habla por iniciativa propia cuando usas el PC ---
CHAT_ENABLED = os.getenv("JARVIS_CONVERSADOR", "1") == "1"
CHAT_EVERY_MIN = float(os.getenv("JARVIS_CONVERSADOR_MINUTOS", "45"))
CHAT_ACTIVE_HOURS = os.getenv("JARVIS_HORAS_ACTIVAS", "08:00-22:30")

# --- Batería: con el cargador desconectado Axtra apaga la cámara de fondo y ahorra procesador ---
BATTERY_SAVER = os.getenv("JARVIS_AHORRO_BATERIA", "1") == "1"

# --- Cámara ---
CAMERA_INDEX = int(os.getenv("JARVIS_CAMARA", "0"))           # 0 = cámara del portátil
CAMERA_GREETING = os.getenv("JARVIS_CAMARA_SALUDO", "1") == "1"  # saludarte al verte llegar

# --- Seguridad por voz ---
VOICE_THRESHOLD = float(os.getenv("JARVIS_VOICE_THRESHOLD", "0.75"))
REQUIRE_VOICE_MATCH = os.getenv("JARVIS_REQUIRE_VOICE_MATCH", "1") == "1"

# --- Rutas y audio ---
SAMPLE_RATE = 16000
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DOCS_DIR = BASE_DIR / "mis_documentos"   # bocetos, propuestas, dictados, gráficas
DOCS_DIR.mkdir(exist_ok=True)
VOICEPRINT_PATH = DATA_DIR / "voiceprint.npy"
