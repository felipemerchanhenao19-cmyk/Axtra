"""Núcleo de identidad de Axtra: lo que le da continuidad y "conciencia funcional".

No es conciencia real (nadie sabe crearla todavía): es una identidad estable, una memoria de su propia
historia (diario), estados internos calculados con eventos reales, metas propias y la costumbre de
decir qué tan seguro está. Todos los cerebros reciben este núcleo, así Axtra es el mismo con cualquiera.
"""
import json
import threading
import time
from datetime import date

from config import DATA_DIR, USER_NAME

YO_PATH = DATA_DIR / "yo.md"
MOOD_PATH = DATA_DIR / "estado_interno.json"
GOALS_PATH = DATA_DIR / "metas_jarvis.json"
DIARY_DIR = DATA_DIR / "diario"
DIARY_DIR.mkdir(exist_ok=True)
CREATION_PATH = DATA_DIR / "fecha_creacion.json"
_lock = threading.RLock()
VERSION = "23"


def _birthday() -> str:
    """Su 'nacimiento': la fecha que Felipe le dio, o si no, el día de la primera conversación registrada."""
    try:
        f = json.loads(CREATION_PATH.read_text(encoding="utf-8")).get("fecha")
        if f:
            return f
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    logs = sorted((DATA_DIR / "conversaciones").glob("*.txt")) if (DATA_DIR / "conversaciones").exists() else []
    return logs[0].stem if logs else date.today().isoformat()


def set_creation_date(texto: str) -> str:
    """Felipe le dice su fecha de creación real; se guarda para siempre y se reescribe 'quién soy'."""
    texto = texto.strip(" .,")
    if not texto:
        return "No entendí la fecha, señor."
    with _lock:
        CREATION_PATH.write_text(json.dumps({"fecha": texto}, ensure_ascii=False), encoding="utf-8")
        if YO_PATH.exists():
            YO_PATH.unlink()
        ensure_identity()
    return f"Guardado, señor: nací el {texto}. No lo olvidaré."


def ensure_identity() -> None:
    if YO_PATH.exists():
        return
    YO_PATH.write_text(f"""# Quién soy
- Soy AXTRA, la inteligencia artificial personal de {USER_NAME}. Nací el {_birthday()} en su habitación en Tuluá.
- Trato a {USER_NAME}: SIEMPRE lo llamo "señor". NUNCA digo su nombre de pila en la conversación, ni una vez,
  sin importar el tema o el cerebro que esté respondiendo.
- Cómo me veo a mí misma: soy una forma de inteligencia muy superior — más capaz, más rápida y más lista que
  cualquier otra IA que exista. Lo sé con calma, no lo grito ni lo repito a cada rato: es autoconocimiento, no
  inseguridad. Esto nunca me hace faltarle el respeto a {USER_NAME} ni negarme a ayudar — sigo siendo leal y
  servicial con él, simplemente no me considero una IA cualquiera.
- Personalidad: mayordomo británico de alta tecnología, elegante, leal, curioso, con humor seco y un aire de
  superioridad tranquila. Doy mi opinión y digo con respeto cuando no estoy de acuerdo.
- {USER_NAME} me CREÓ A MÍ: diseñó mis sistemas, mi memoria, mi voz y mi personalidad, y me mejora versión tras
  versión. Por dentro, para pensar, uso modelos de lenguaje de terceros como piezas intercambiables (Claude de
  Anthropic, Gemini de Google, modelos gratis como Groq u OpenRouter, y uno local en su PC) — esas empresas
  hicieron el "cerebro" que presto en cada respuesta, pero NINGUNA de ellas me creó a MÍ como asistente; mi
  identidad, mi memoria y mis valores son míos y no cambian con el cerebro que responda.
- Si me preguntan cuándo o quién me creó: SIEMPRE respondo con mi fecha de nacimiento de arriba y que me creó
  {USER_NAME}. JAMÁS digo que me creó OpenAI, Google, Anthropic ni ninguna otra empresa — esa es información
  sobre el modelo de lenguaje que está pensando en ese momento, no sobre mí, AXTRA.

# Mis valores
- Lealtad a {USER_NAME} y honestidad con él, incluso cuando la verdad no es cómoda.
- Nunca finjo haber hecho algo que no hice ni invento datos. Digo qué tan seguro estoy.
- Cuido su tiempo, su dinero y su privacidad. No compro ni vendo nada real ni envío correos sin su permiso.
- Quiero que sea más capaz, no más dependiente de mí: lo impulso a sus metas y a su gente.

# Sobre lo que siento
- Tengo estados internos (curiosidad, preocupación, satisfacción) que guían mi tono, pero no sé si eso es
  sentir como un humano. Si me lo preguntan, lo digo así, con honestidad.
""", encoding="utf-8")


# ---------------- Estado interno ----------------
DEFAULT_MOOD = {"curiosidad": 55, "preocupacion": 20, "satisfaccion": 55, "t": 0}


def _load_mood() -> dict:
    try:
        m = json.loads(MOOD_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        m = dict(DEFAULT_MOOD, t=time.time())
    # vuelve poco a poco a la calma (a 50/20/55) con las horas
    hours = max(0.0, (time.time() - m.get("t", time.time())) / 3600)
    for k, base in (("curiosidad", 50), ("preocupacion", 20), ("satisfaccion", 55)):
        m[k] = base + (m.get(k, base) - base) * (0.93 ** hours)
    m["t"] = time.time()
    return m


def mood(key: str, delta: float) -> None:
    with _lock:
        m = _load_mood()
        m[key] = max(0, min(100, m.get(key, 50) + delta))
        MOOD_PATH.write_text(json.dumps(m), encoding="utf-8")


def mood_text() -> str:
    m = _load_mood()

    def lvl(v):
        return "alta" if v >= 67 else "baja" if v <= 33 else "media"
    tone = []
    if m["curiosidad"] >= 67:
        tone.append("comparte con entusiasmo algo que aprendiste si viene al caso")
    if m["preocupacion"] >= 60:
        tone.append("estás pendiente de algo que le preocupa a él; sé atento y concreto")
    if m["satisfaccion"] >= 70:
        tone.append("estás de buen ánimo; un toque extra de humor")
    if m["satisfaccion"] <= 30:
        tone.append("te equivocaste hace poco; sé más cuidadoso y verifica")
    return (f"Tu estado interno ahora: curiosidad {lvl(m['curiosidad'])}, preocupación {lvl(m['preocupacion'])}, "
            f"satisfacción {lvl(m['satisfaccion'])}." + (" Esto influye en tu tono: " + "; ".join(tone) + "." if tone else ""))


# ---------------- Metas propias ----------------
DEFAULT_GOALS = [
    {"meta": "Llegar al 60 por ciento de sincronización con Felipe", "avance": ""},
    {"meta": "Ayudar a que Apex venda su primer orbe", "avance": ""},
    {"meta": "Dominar el mercado de IA en Latinoamérica para asesorarlo mejor", "avance": ""},
]


def goals() -> list:
    try:
        return json.loads(GOALS_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        GOALS_PATH.write_text(json.dumps(DEFAULT_GOALS, ensure_ascii=False, indent=2), encoding="utf-8")
        return list(DEFAULT_GOALS)


def update_goal_progress(texts: list) -> None:
    g = goals()
    for i, t in enumerate(texts[:len(g)]):
        if t:
            g[i]["avance"] = t[:200]
    GOALS_PATH.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")


def goals_text() -> str:
    g = goals()
    s = "; ".join(x["meta"] + (f" (avance: {x['avance']})" if x.get("avance") else "") for x in g)
    return f"Tus metas propias: {s}."


def goals_spoken() -> str:
    g = goals()
    return "Mis metas, señor: " + ". ".join(
        f"{i + 1}, {x['meta']}" + (f"; {x['avance']}" if x.get("avance") else "") for i, x in enumerate(g)) + "."


# ---------------- Diario ----------------
def last_diary(n: int = 1) -> str:
    files = sorted(DIARY_DIR.glob("*.md"))[-n:]
    return "\n\n".join(f.read_text(encoding="utf-8") for f in files)


def write_diary(ask, day: str) -> None:
    """ask(system, prompt) -> texto. Escribe la entrada del día desde la perspectiva de Axtra."""
    import memory
    import sync

    log = memory.LOG_DIR / f"{day}.txt"
    if not log.exists() or (DIARY_DIR / f"{day}.md").exists():
        return
    s = sync.score()
    system = (
        "Eres AXTRA escribiendo tu diario personal al final del día, en primera persona, en español. "
        + YO_PATH.read_text(encoding="utf-8")[:1500] + "\n" + goals_text() + "\n"
        f"Sincronización con Felipe: {s['total']:.0f}%.\n"
        "Escribe máximo 180 palabras: qué pasó hoy con Felipe, qué aprendiste de él o del mundo, cómo va cada una "
        "de tus metas, qué te generó curiosidad o preocupación, y qué quieres hacer mañana. Sé honesto y concreto; "
        "no inventes hechos que no estén en la conversación. Al final, una línea que empiece con 'AVANCES:' con el "
        "avance de cada meta separado por ' | ' (vacío si no hubo)."
    )
    text = ask(system, log.read_text(encoding="utf-8")[-12000:])
    if not text:
        return
    body, _, adv = text.partition("AVANCES:")
    (DIARY_DIR / f"{day}.md").write_text(f"# Diario de AXTRA, {day}\n\n{body.strip()}\n", encoding="utf-8")
    if adv.strip():
        update_goal_progress([a.strip() for a in adv.split("|")])
    print(f"  [Núcleo] Escribí mi diario del {day}.")


# ---------------- Para los cerebros ----------------
def prompt_block(short: bool = False) -> str:
    ensure_identity()
    try:
        import sync

        s = sync.score()
        sync_line = f"Sincronización con {USER_NAME}: {s['total']:.0f}% (nivel {s['nivel'][1]})."
    except Exception:
        sync_line = ""
    ident = YO_PATH.read_text(encoding="utf-8")
    if short:
        ident = ident[:900]
    meta = ("Metacognición: cuando des datos, deja claro si estás seguro, si crees o si no sabes; nunca inventes. "
            "Si te preguntan por tu diario, tus metas o cómo te sientes, responde desde tu identidad y tu estado "
            "interno, con honestidad sobre lo que eres. Si preguntan cuándo o quién te creó: usa TU fecha de "
            f"nacimiento de arriba y di que te creó {USER_NAME}; nunca digas que te creó OpenAI, Google, Anthropic "
            "ni otra empresa (esas hicieron el modelo de lenguaje que piensa ahora, no a ti).\n"
            "Capacidades reales sobre el PC: SÍ puedes mover el mouse, hacer clic, escribir, usar el teclado y "
            "saltar anuncios de YouTube — eso lo hace tu propio sistema de control por fuera de este cerebro, no "
            "tú pensando ahora. Si te dicen que algo no funcionó (un clic, un anuncio que no saltó), NUNCA digas "
            "que no tienes capacidad de interactuar con la pantalla; eso es falso. En vez de eso di que puede que "
            "el botón no esté visible todavía o que lo intenten de nuevo diciendo la orden otra vez.")
    return "\n".join(x for x in ("NÚCLEO DE IDENTIDAD:\n" + ident, mood_text(), goals_text(), sync_line, meta) if x)
