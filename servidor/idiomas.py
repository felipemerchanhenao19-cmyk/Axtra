"""Modo idiomas: frases con su pronunciación escrita en español, voz nativa y revisión de pronunciación.

Ejemplo:  "¿Cómo se dice hola, cómo estás en ruso?"
  Привет, как дела?   ->  pri-VIÉT, kak di-LÁ   (la sílaba en MAYÚSCULAS es la que suena más fuerte)
Luego lo repites: Axtra escucha con el reconocedor de ese idioma, compara palabra por palabra y te da
un puntaje y un consejo. Todo con cerebros gratis.

Progreso de 0 a 100 %: frases dominadas (80 puntos o más) sobre una meta de 500 frases.
Niveles aproximados: A1 < 50 frases, A2 < 150, B1 < 300, B2 < 500, C1 desde 500.
"""
import difflib
import json
import re
import unicodedata

from . import db
from .proveedores import NoDisponible
from .voz import IDIOMAS, NOMBRES

META_FRASES = 500
ALIAS = {"ingles": "ingles", "english": "ingles", "ruso": "ruso", "frances": "frances", "portugues": "portugues",
         "aleman": "aleman", "italiano": "italiano", "japones": "japones", "chino": "chino", "mandarin": "chino",
         "coreano": "coreano", "arabe": "arabe"}
IDIOMA_RE = re.compile(r"\b(" + "|".join(ALIAS) + r")\b")
PEDIDO_RE = re.compile(r"\b(como se dice|como se pronuncia|como digo|como le digo|traduce\w*|ensena\w*|aprender|"
                       r"practicar|practiquemos|clase de|leccion de|frases?|saludos?|palabras?|vocabulario|"
                       r"como se escribe|que significa|dime en)\b")
CEREBROS_IDIOMAS = ["gemini", "groq_pro", "cerebras", "openrouter"]   # todos gratis


def _sin_tildes(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def detectar(texto: str):
    """Devuelve el idioma (clave de IDIOMAS) si el mensaje pide algo de idiomas, o None."""
    t = _sin_tildes(texto)
    m = IDIOMA_RE.search(t)
    if m and PEDIDO_RE.search(t):
        return ALIAS[m.group(1)]
    return None


def _sistema(usuario: str) -> str:
    lista = ", ".join(IDIOMAS)
    return (
        f"Eres AXTRA, profesor particular de idiomas de {usuario}, cuyo idioma nativo es el español de Colombia. "
        "Llámalo 'señor'. Responde SOLO con un objeto JSON válido, sin texto antes ni después, con esta forma:\n"
        '{"idioma": "<una de: ' + lista + '>", "explicacion": "1 o 2 frases en español, tono de mayordomo", '
        '"frases": [{"frase": "en el idioma, con su alfabeto real", "pronunciacion": "cómo suena, escrito con '
        'letras y sonidos del español, sílabas separadas por guion y la sílaba tónica en MAYÚSCULAS", '
        '"traduccion": "en español", "nota": "registro o detalle útil (opcional)"}], '
        '"consejo": "un consejo breve de pronunciación en español"}\n'
        "Máximo 4 frases. La pronunciación debe reflejar cómo suena DE VERDAD, no cómo se escribe. Ejemplo en "
        "ruso: «Привет, как дела?» -> «pri-VIÉT, kak di-LÁ» (la 'е' sin acento suena casi como 'i'; la 'o' sin "
        "acento suena 'a'). En inglés: «How are you?» -> «jáu ar IÚ». Nunca inventes palabras."
    )


def _json(texto: str) -> dict:
    m = re.search(r"\{.*\}", texto, flags=re.S)
    if not m:
        raise ValueError("sin JSON")
    return json.loads(m.group(0))


def leccion(enrutador, texto: str, idioma: str, historial: list = None) -> dict:
    """Pide la lección a un cerebro gratis y la valida."""
    from . import config

    mensajes = list(historial or [])[-6:] + [{"role": "user", "content": texto}]
    ultimo_error = None
    for _ in range(2):
        r = enrutador._cadena(CEREBROS_IDIOMAS, _sistema(config.USER_NAME), mensajes, max_tokens=1200, pensar=True)
        try:
            data = _json(r.texto)
            frases = [f for f in data.get("frases", []) if f.get("frase") and f.get("pronunciacion")][:4]
            if not frases:
                raise ValueError("sin frases")
            idioma = data.get("idioma") if data.get("idioma") in IDIOMAS else idioma
            return {"idioma": idioma, "nombre": NOMBRES[idioma], "explicacion": data.get("explicacion", ""),
                    "frases": frases, "consejo": data.get("consejo", ""), "cerebro": r.cerebro,
                    "progreso": progreso(idioma)}
        except (ValueError, json.JSONDecodeError) as e:
            ultimo_error = e
    raise NoDisponible(f"no pude preparar la lección ({ultimo_error})")


# ---------------- Pronunciación ----------------
def _palabras(texto: str, idioma: str) -> list:
    t = texto.lower().replace("ё", "е")
    t = "".join(c for c in t if not unicodedata.category(c).startswith("P"))
    if idioma not in ("ruso", "arabe", "japones", "chino", "coreano"):
        t = _sin_tildes(t)
    if idioma in ("japones", "chino"):          # sin espacios: se compara letra por letra
        return [c for c in t if not c.isspace()]
    return t.split()


def evaluar(objetivo: str, idioma: str, oido: str) -> dict:
    """Compara lo que debía decir con lo que entendió el reconocedor. Puntaje de 0 a 100."""
    meta, dicho = _palabras(objetivo, idioma), _palabras(oido, idioma)
    palabras, total = [], 0.0
    originales = objetivo.split() if idioma not in ("japones", "chino") else meta
    for i, w in enumerate(meta):
        mejor = max((difflib.SequenceMatcher(None, w, d).ratio() for d in dicho), default=0.0)
        total += mejor
        estado = "bien" if mejor >= 0.8 else "casi" if mejor >= 0.5 else "repetir"
        visible = originales[i].strip(".,!?¿¡;:«»\"") if i < len(originales) else w
        palabras.append({"palabra": visible, "estado": estado})
    puntaje = round(100 * total / max(1, len(meta)))
    return {"puntaje": puntaje, "palabras": palabras, "oido": oido}


def consejo(enrutador, objetivo: str, pronunciacion: str, resultado: dict) -> str:
    malas = [p["palabra"] for p in resultado["palabras"] if p["estado"] != "bien"]
    if not malas:
        return "¡Excelente pronunciación, señor!"
    try:
        r = enrutador._cadena(
            CEREBROS_IDIOMAS,
            "Eres profesor de pronunciación para hispanohablantes. Da UN consejo breve (máximo 2 frases) en "
            "español, concreto, sobre cómo pronunciar mejor las palabras indicadas. Llama al alumno 'señor'.",
            [{"role": "user", "content": f"Frase: {objetivo}\nCómo suena: {pronunciacion}\n"
                                         f"El reconocedor entendió: {resultado['oido'] or '(nada)'}\n"
                                         f"Palabras a mejorar: {', '.join(malas)}"}],
            max_tokens=200)
        return r.texto.strip()
    except NoDisponible:
        return f"Practique despacio: {', '.join(malas)}. Escuche la voz nativa y repita sílaba por sílaba."


def progreso(idioma: str) -> dict:
    p = db.practicas(idioma)
    d = p["dominadas"]
    nivel = "A1" if d < 50 else "A2" if d < 150 else "B1" if d < 300 else "B2" if d < META_FRASES else "C1"
    return {**p, "idioma": idioma, "nombre": NOMBRES.get(idioma, idioma), "nivel": nivel,
            "porcentaje": min(100, round(100 * d / META_FRASES))}
