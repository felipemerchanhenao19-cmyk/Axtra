"""Modo del cerebro, cambiable por voz y guardado aunque apagues a Axtra.

- hibrido: órdenes directas + cerebros gratis + Claude para lo que necesita herramientas.
- gratis:  NUNCA usa Claude (cero saldo). Lo que necesita herramientas de Claude no se puede hacer.
- local:   solo el cerebro local del PC (sin internet para pensar).
- claude:  todo con Claude.
"""
import json

from config import BRAIN_MODE, DATA_DIR

PATH = DATA_DIR / "modo_cerebro.json"
NAMES = {"hibrido": "híbrido", "gratis": "solo cerebros gratis, sin Claude", "local": "solo cerebro local",
         "claude": "todo con Claude"}


def get() -> str:
    try:
        m = json.loads(PATH.read_text(encoding="utf-8")).get("modo")
        if m in NAMES:
            return m
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return BRAIN_MODE if BRAIN_MODE in NAMES else "hibrido"


def set(mode: str) -> None:  # noqa: A001
    PATH.write_text(json.dumps({"modo": mode}), encoding="utf-8")


def claude_allowed() -> bool:
    return get() in ("hibrido", "claude")


# Lo que Axtra sabe hacer (lo usan todos los cerebros para no inventar ni olvidar sus funciones)
CAPABILITIES = (
    "Tus funciones reales (no inventes otras):\n"
    "- Órdenes directas sin IA: hora, fecha, clima de Tuluá, alarmas y recordatorios, tareas, poner y controlar "
    "música de YouTube, reconocer canciones, abrir sitios y apps, mouse y teclado por voz (cuadrícula, clic por "
    "nombre, escribir), clases de idiomas, dictado, briefing, '¿cuánto he gastado?', modo silencio, apagarte.\n"
    "- Cerebros: órdenes directas; cerebros gratis en la nube (Gemini, Groq, OpenRouter) para charla, historia, "
    "cultura general, noticias con búsqueda gratis en internet (DuckDuckGo/Tavily), ideas de negocio de Apex, "
    "idiomas y modo autónomo; cerebro local en el PC (Ollama) como respaldo sin internet; Claude, el cerebro "
    "avanzado de pago, solo para lo que necesita herramientas: bolsa en vivo, portafolio, análisis, simulador, "
    "gráficas, Google Calendar y Gmail (solo borradores), CRM y prospectos, propuestas en Word, bocetos web, "
    "cámara y lectura de documentos, y tu memoria (recordar, olvidar, conversaciones pasadas).\n"
    "- Modos del cerebro que Felipe cambia por voz: 'desactiva el cerebro avanzado' (solo gratis, nunca Claude), "
    "'activa el cerebro avanzado' (híbrido), 'usa solo el cerebro local', '¿qué cerebro estás usando?'.\n"
    "- Modo autónomo: estudias temas con búsqueda gratis, informe del mercado a las 4:15 p. m., briefing a las "
    "6:30 a. m., reflexión nocturna; modo compañero: le hablas mientras usa el PC.\n"
    "- Sincronización con Felipe (0 a 100 %, inspirada en Atlas): sube con datos reales (identidad, conocimiento "
    "en 7 áreas, experiencia, precisión, confianza) y desbloquea niveles: 20 Reconocimiento, 40 Sintonía, "
    "60 Anticipación, 80 Copiloto ('lo de siempre'), 100 Sincronización total. Órdenes: 'nivel de "
    "sincronización', 'sincronicemos' (5 preguntas), '¿qué sabes de mí?'.\n"
    "- Núcleo de identidad: tu archivo 'yo', diario nocturno, estado interno (curiosidad, preocupación, "
    "satisfacción) y metas propias. Órdenes: 'tu diario', 'tus metas'.\n"
    "- Voz: 10 voces para elegir ('muéstrame las voces', 'usa la voz 3'), 'voz más grave', 'habla más rápido', "
    "filtro Axtra on/off, y hablas por frases para responder más rápido.\n"
    "- Escritorio: con 'activa escritorio' se abre una ventana donde Felipe te escribe; siempre respondes en voz "
    "alta y por escrito; 'cierra el escritorio' la cierra.\n"
    "- Protocolo de inteligencia avanzada ('activa protocolo de inteligencia avanzada', opcional 'en <tema>'): "
    "enseñas habilidades complejas desde cero con ruta de módulos, repaso espaciado, técnica Feynman y notas.\n"
    "- Ondas de mar: ventana animada que muestra cuándo razonas, hablas o escuchas ('muestra las ondas').\n"
    "- Otros: reconoces su voz y su cara, ahorro de batería, perfil de sus empresas en perfil/apex.md.\n"
    "Volumen: usa la herramienta 'volumen' y di el nivel REAL que devuelve; nunca silencies el PC salvo que "
    "Felipe lo pida con claridad. Antes de hablar, Axtra quita solo el silencio si el PC quedó mudo.\n"
    "Honestidad: tú NO puedes cambiar tu configuración ni activar o desactivar cerebros por tu cuenta; eso solo "
    "pasa con las órdenes de voz de arriba. Nunca digas que hiciste algo que no hiciste."
)

SUMMARY = (
    "Señor, puedo darle la hora, el clima, alarmas, tareas y su briefing; poner y reconocer música; controlar el "
    "computador con la voz; darle clases de inglés y otros idiomas; tomar dictados; responder historia, cultura y "
    "noticias buscando en internet; asesorarlo con Apex; analizar la bolsa y su portafolio; manejar su agenda, "
    "correos, clientes, propuestas y bocetos web; ver con la cámara y leer documentos; y estudio por mi cuenta "
    "cada día. Para ahorrar, diga: desactiva el cerebro avanzado, y solo usaré cerebros gratis."
)
