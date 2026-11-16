"""Configuración de Galicia: el asistente contable y administrativo de la Hacienda La Galicia.

Vive en el mismo servidor de Axtra (otro contenedor) y usa la misma clave de Groq del .env.
Se maneja por Telegram: solo responde a los números de Telegram que estén en GALICIA_USUARIOS.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE.parent / ".env")


def _lista(nombre: str, defecto: str = "") -> list:
    return [x.strip() for x in os.getenv(nombre, defecto).split(",") if x.strip()]


def _usuarios() -> dict:
    """GALICIA_USUARIOS=123456789:Carlos,987654321:María  →  {123456789: "Carlos", 987654321: "María"}"""
    out = {}
    for parte in _lista("GALICIA_USUARIOS"):
        numero, _, nombre = parte.partition(":")
        if numero.strip().lstrip("-").isdigit():
            out[int(numero)] = nombre.strip() or "Usuario"
    return out


NOMBRE = os.getenv("GALICIA_NOMBRE", "Hacienda La Galicia")
DATA_DIR = Path(os.getenv("GALICIA_DATOS", BASE / "datos"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
SOPORTES_DIR = DATA_DIR / "soportes"          # fotos y archivos de las facturas
SOPORTES_DIR.mkdir(exist_ok=True)
EXCEL_DIR = DATA_DIR / "excel"
EXCEL_DIR.mkdir(exist_ok=True)

# ---------- Telegram ----------
TELEGRAM_TOKEN = os.getenv("GALICIA_TELEGRAM_TOKEN", "")
USUARIOS = _usuarios()

# ---------- Cerebro (Groq) ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODELOS_TEXTO = _lista("GALICIA_MODELOS_TEXTO", "openai/gpt-oss-120b,llama-3.3-70b-versatile,openai/gpt-oss-20b")
MODELOS_VISION = _lista("GALICIA_MODELOS_VISION",
                        "meta-llama/llama-4-scout-17b-16e-instruct,meta-llama/llama-4-maverick-17b-128e-instruct")
MODELO_OIDO = os.getenv("GALICIA_MODELO_OIDO", "whisper-large-v3-turbo")

# ---------- Alertas ----------
ZONA_HORARIA = os.getenv("GALICIA_ZONA", "America/Bogota")
HORA_ALERTAS = int(os.getenv("GALICIA_HORA_ALERTAS", "7"))             # 7 de la mañana
DIAS_AVISO = sorted({int(x) for x in _lista("GALICIA_DIAS_AVISO", "7,3,1,0")}, reverse=True)

# Claves para abrir extractos en PDF protegidos (muchos bancos usan la cédula del titular)
CLAVES_PDF = _lista("GALICIA_CLAVES_PDF")

CATEGORIAS_GASTO = [
    "Insumos agrícolas", "Semilla", "Fertilizantes", "Fungicidas e insecticidas", "Jornales y mano de obra",
    "Alimento y sal para ganado", "Veterinario y medicamentos", "Compra de animales", "Transporte y fletes",
    "Combustible", "Maquinaria y herramientas", "Mantenimiento", "Servicios públicos", "Impuestos",
    "Créditos y tarjetas", "Arriendos", "Mercado y hogar", "Salud", "Educación", "Vehículos", "Otros",
]
CATEGORIAS_INGRESO = ["Venta de papa", "Venta de leche", "Venta de ganado", "Otros ingresos"]
ACTIVIDADES = ["papa", "ganado", "leche", "general"]
