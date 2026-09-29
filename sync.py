"""Sincronización Axtra–Felipe (inspirada en Atlas): una barra de 0 a 100 % que mide, con datos
reales, qué tan bien conoce Axtra a su dueño. Al pasar niveles se desbloquean funciones.

Puntos (100 en total):
  Identidad    10  voz registrada 4, cara registrada 3, datos básicos 3
  Conocimiento 35  7 áreas x 5 datos (rutina, metas, negocios, estudios, gustos, estilo, personas)
  Experiencia  20  +0.5 por día de uso (máx 15) y +0.1 por conversación (máx 1/día, 5 en total);
                   baja 1 punto por cada semana sin usarlo
  Precisión    20  % de aciertos: "exacto", "bien" suman; "te equivocaste", "eso no es así" restan
                   (cuenta completo desde 10 señales)
  Confianza    15  Google 4, perfil de Apex 3, CRM con 3+ clientes 2, sesiones de sincronización 1 c/u (máx 4),
                   modo compañero activo 2
"""
import json
import re
import threading
import unicodedata
from datetime import date, datetime, timedelta

from config import BASE_DIR, CHAT_ENABLED, DATA_DIR, VOICEPRINT_PATH

PATH = DATA_DIR / "sincronizacion.json"
_lock = threading.RLock()

AREAS = {
    "rutina": ("su rutina", r"\b(levant|despiert|duerm|horario|rutina|madrug|gimnasio|gym|entren|desayun|almuerz|"
                            r"a las \d|por las (mananas|tardes|noches)|todos los dias|cada dia)"),
    "metas": ("sus metas", r"\b(meta|objetivo|quiero lograr|sueno|planeo|proposito|ahorrar para|quiero ser|quiero tener|"
                           r"mi plan|para (el|este) ano)"),
    "negocios": ("sus negocios", r"\b(apex|cliente|negocio|empresa|venta|vender|orbe|marketplace|boceto|pagina web|"
                                 r"emprend|socio comercial|precio)"),
    "estudios": ("sus estudios", r"\b(universidad|uceva|materia|parcial|examen|semestre|carrera|profesor|estudi|"
                                 r"comercio internacional|tarea de|trabajo de la u)"),
    "gustos": ("sus gustos", r"\b(me gusta|me encanta|favorit|musica|cancion|artista|comida|pelicula|serie|deporte|"
                             r"equipo|futbol|odio|no me gusta|prefiero comer|libro)"),
    "estilo": ("su forma de trabajar conmigo", r"\b(prefiero que|respuestas|hablame|no me gusta que|dime siempre|"
                                                r"llamame|cuando te|quiero que me|explicame asi|corto|detallado)"),
    "personas": ("las personas importantes para usted", r"\b(mama|papa|madre|padre|herman|novia|novio|amig|primo|prima|"
                                                         r"tio|tia|abuel|jefe|companero|socio|familia)"),
}
LEVELS = [
    (0, "Inicial", "órdenes, charla y funciones básicas"),
    (20, "Reconocimiento", "saludo y briefing personalizados; recuerdo sus gustos sin que me los repita"),
    (40, "Sintonía", "modo compañero personal: sé cuándo hablarle y de qué"),
    (60, "Anticipación", "me adelanto: cada tarde reviso su día siguiente y le propongo qué preparar"),
    (80, "Copiloto", "atajo 'lo de siempre': repito lo que suele pedirme a esta hora"),
    (100, "Sincronización total", "informe semanal de sus metas y le rindo cuentas"),
]
POSITIVE = r"^(exacto|perfecto|correcto|eso es|asi es|bien hecho|muy bien|excelente|acertaste|justo eso|tienes razon)\b"
NEGATIVE = (r"\b(te equivocaste|estas equivocado|eso no es (asi|cierto|verdad)|no es asi|incorrecto|estas mal|"
            r"no entendiste|eso esta mal|no era eso|eso no fue lo que)\b")


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", (t or "").lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _load() -> dict:
    try:
        d = json.loads(PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        d = {}
    d.setdefault("inicio", date.today().isoformat())
    d.setdefault("dias", [])
    d.setdefault("conversaciones", {})
    d.setdefault("aciertos", 0)
    d.setdefault("errores", 0)
    d.setdefault("sesiones", 0)
    d.setdefault("areas", {a: [] for a in AREAS})
    for a in AREAS:
        d["areas"].setdefault(a, [])
    d.setdefault("nivel_anunciado", 0)
    d.setdefault("habitos", [])
    return d


def _save(d: dict) -> None:
    with _lock:
        PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------- Eventos ----------------
def classify(text: str):
    t = _norm(text)
    return [a for a, (_, pat) in AREAS.items() if re.search(pat, t)]


def add_fact(text: str, area: str = None) -> None:
    """Un dato nuevo sobre Felipe (desde 'recuerda que', la reflexión o una sesión)."""
    with _lock:
        d = _load()
        for a in ([area] if area else classify(text)):
            if a in d["areas"] and text not in d["areas"][a]:
                d["areas"][a] = (d["areas"][a] + [text])[-30:]
        _save(d)


def record_exchange(user_text: str) -> None:
    """Cada conversación: experiencia, y señales de acierto o error."""
    with _lock:
        d = _load()
        today = date.today().isoformat()
        if today not in d["dias"]:
            d["dias"].append(today)
        d["conversaciones"][today] = d["conversaciones"].get(today, 0) + 1
        t = _norm(user_text)
        t = re.sub(r"^(axtra|oye)\s+", "", t)
        if re.search(POSITIVE, t):
            d["aciertos"] += 1
            _mood("satisfaccion", +6)
        elif re.search(NEGATIVE, t):
            d["errores"] += 1
            _mood("satisfaccion", -4)
        _save(d)


def record_habit(text: str) -> None:
    """Órdenes directas y la hora en que se piden (para 'lo de siempre')."""
    with _lock:
        d = _load()
        d["habitos"] = (d["habitos"] + [[datetime.now().hour, text]])[-300:]
        _save(d)


def session_done() -> None:
    with _lock:
        d = _load()
        d["sesiones"] += 1
        _save(d)


def _mood(k, v):
    try:
        import nucleo

        nucleo.mood(k, v)
    except Exception:
        pass


# ---------------- Puntaje ----------------
def score() -> dict:
    d = _load()
    # Identidad
    ident = 0.0
    if VOICEPRINT_PATH.exists():
        ident += 4
    if (DATA_DIR / "cara_modelo.yml").exists():
        ident += 3
    try:
        import memory

        if len(memory.get_facts()) >= 2:
            ident += 3
    except Exception:
        pass
    # Conocimiento
    know = sum(min(5, len(v)) for v in d["areas"].values())
    # Experiencia
    days = len(d["dias"])
    conv = sum(min(10, n) for n in d["conversaciones"].values()) * 0.1
    exp = min(15, days * 0.5) + min(5, conv)
    if d["dias"]:
        idle = (date.today() - date.fromisoformat(max(d["dias"]))).days
        if idle > 7:
            exp -= (idle - 7) // 7 + 1
    exp = max(0.0, exp)
    # Precisión
    n = d["aciertos"] + d["errores"]
    ratio = d["aciertos"] / n if n else 0.0
    prec = 20 * ratio * min(1.0, n / 10)
    # Confianza
    trust = 0.0
    try:
        import google_services

        if google_services.available():
            trust += 4
    except Exception:
        pass
    apex = BASE_DIR / "perfil" / "apex.md"
    if apex.exists() and len(apex.read_text(encoding="utf-8", errors="ignore")) > 1000:
        trust += 3
    try:
        import business

        if len(business.crm_ver().get("clientes", [])) >= 3:
            trust += 2
    except Exception:
        pass
    trust += min(4, d["sesiones"])
    if CHAT_ENABLED:
        trust += 2
    parts = {"identidad": round(ident, 1), "conocimiento": round(float(know), 1), "experiencia": round(exp, 1),
             "precision": round(prec, 1), "confianza": round(trust, 1)}
    total = round(min(100.0, sum(parts.values())), 1)
    weakest = min(AREAS, key=lambda a: len(d["areas"][a]))
    return {"total": total, "partes": parts, "area_debil": weakest, "nivel": level(total)}


def level(total: float):
    lv = LEVELS[0]
    for L in LEVELS:
        if total >= L[0]:
            lv = L
    return lv


def unlocked(threshold: int) -> bool:
    return score()["total"] >= threshold


def locked_msg(threshold: int) -> str:
    s = score()
    name = next(L[1] for L in LEVELS if L[0] == threshold)
    return (f"Esa función se desbloquea en el nivel {name}, al {threshold} por ciento de sincronización, señor. "
            f"Vamos en {s['total']:.0f}. Diga 'sincronicemos' y me ayuda a conocerlo mejor.")


def check_level_up() -> str:
    """Si subió de nivel desde el último aviso, devuelve el anuncio (una sola vez)."""
    with _lock:
        d = _load()
        s = score()
        th = s["nivel"][0]
        if th > d["nivel_anunciado"]:
            d["nivel_anunciado"] = th
            _save(d)
            if th == 0:
                return ""
            _mood("satisfaccion", +10)
            return (f"Por cierto, señor: nuestra sincronización llegó al {s['total']:.0f} por ciento. "
                    f"Nivel {s['nivel'][1]}. Nueva función: {s['nivel'][2]}.")
    return ""


def report() -> str:
    s = score()
    p = s["partes"]
    nxt = next((L for L in LEVELS if L[0] > s["total"]), None)
    msg = (f"Nuestra sincronización está en {s['total']:.0f} por ciento, nivel {s['nivel'][1]}. "
           f"Identidad {p['identidad']:.0f} de 10, conocimiento {p['conocimiento']:.0f} de 35, experiencia "
           f"{p['experiencia']:.0f} de 20, precisión {p['precision']:.0f} de 20 y confianza {p['confianza']:.0f} de 15. ")
    if nxt:
        msg += f"El siguiente nivel, {nxt[1]}, se abre al {nxt[0]}. "
    msg += f"Donde menos lo conozco es en {AREAS[s['area_debil']][0]}."
    return msg


def what_i_know() -> str:
    d = _load()
    parts = []
    for a, (label, _) in AREAS.items():
        items = d["areas"][a][-2:]
        if items:
            parts.append(f"De {label}: " + "; ".join(items))
    if not parts:
        return "Todavía sé muy poco de usted, señor. Diga 'sincronicemos' y le hago unas preguntas."
    return " ".join(parts)[:900] + " Si algo no quiere que lo recuerde, diga: olvida lo de, y el tema."


def usual_command():
    """'Lo de siempre': la orden directa más repetida a esta hora (±1 h)."""
    d = _load()
    h = datetime.now().hour
    from collections import Counter

    c = Counter(t for hh, t in d["habitos"] if abs(hh - h) <= 1 or abs(hh - h) == 23)
    if not c:
        return None
    text, n = c.most_common(1)[0]
    return text if n >= 2 else None


# ---------------- Sesión de sincronización ----------------
QUESTIONS = {
    "rutina": ["¿A qué hora se levanta normalmente?", "¿Cómo es un día normal suyo entre semana?",
               "¿A qué hora rinde mejor para trabajar o estudiar?", "¿Hace ejercicio? ¿Qué días?",
               "¿A qué hora suele acostarse?"],
    "metas": ["¿Cuál es su meta más importante para este año?", "¿Dónde quiere estar en cinco años?",
              "¿Qué quiere lograr con Apex en los próximos seis meses?", "¿Qué hábito quiere construir?",
              "¿Qué significaría para usted tener éxito?"],
    "negocios": ["¿Qué es lo que más le cuesta hoy en sus negocios?", "¿Cuál es su cliente ideal?",
                 "¿Qué producto o servicio le deja más dinero?", "¿Cómo consigue clientes normalmente?",
                 "¿Qué haría con Apex si tuviera el doble de tiempo?"],
    "estudios": ["¿Qué materias está viendo este semestre?", "¿Cuál es la materia que más le cuesta?",
                 "¿Cuándo son sus próximos parciales?", "¿Qué le gusta de su carrera?",
                 "¿Cómo prefiere estudiar: leyendo, escuchando o practicando?"],
    "gustos": ["¿Qué música escucha para concentrarse?", "¿Cuál es su comida favorita?",
               "¿Qué película o serie le ha marcado?", "¿Qué deporte o equipo sigue?",
               "¿Qué hace para descansar?"],
    "estilo": ["¿Prefiere que le responda corto o con detalle?", "¿Le gusta que le lleve la contraria cuando no estoy de acuerdo?",
               "¿A qué hora prefiere que no le hable?", "¿Cómo prefiere que le llame: señor, Felipe o de otra forma?",
               "¿Qué es lo que más le molesta de un asistente?"],
    "personas": ["¿Con quién cuenta cuando necesita un consejo? Solo nombre y relación.",
                 "¿Tiene socios o compañeros en sus proyectos? ¿Cómo se llaman?",
                 "¿Hay alguna fecha importante de alguien cercano que quiera que recuerde?",
                 "¿Quién le inspira como emprendedor?", "¿Con quién estudia o trabaja más seguido?"],
}
SKIP = r"\b(paso|siguiente|no quiero (responder|decir)|prefiero no|saltala|salta)\b"
STOP = r"\b(termina|terminar|fin de la sesion|ya no mas|suficiente|para la sesion|basta)\b"
pending = False


def start_session() -> str:
    global pending
    pending = True
    return "Con gusto, señor. Le haré cinco preguntas. Si alguna no quiere responderla, diga paso."


def run_session(tts, stt, get_answer=None) -> None:
    """5 preguntas del área que menos conoce. Las respuestas se guardan como recuerdos.
    get_answer: función que devuelve la respuesta escrita (modo texto); si no, escucha por voz."""
    global pending
    pending = False
    import memory

    d = _load()
    area = min(AREAS, key=lambda a: len(d["areas"][a]))
    asked = set(d.get("preguntas_hechas", []))
    qs = [q for q in QUESTIONS[area] if q not in asked] or QUESTIONS[area]
    before = score()["total"]
    answered = 0
    tts.say(f"Hoy quiero conocer mejor {AREAS[area][0]}.")
    for q in qs[:5]:
        tts.say(q)
        if get_answer:
            ans = (get_answer() or "").strip()
        else:
            from audio import record_utterance

            audio = record_utterance(start_timeout=15, max_seconds=40, silence_end=1.8)
            if audio is None:
                continue
            ans = stt.transcribe(audio).strip()
        print(f"  [Sincronización] Tú: {ans}")
        t = _norm(ans)
        if re.search(STOP, t):
            break
        if not ans or re.search(SKIP, t):
            continue
        fact = f"{q.rstrip('?').lstrip('¿')}: {ans}"
        memory.remember(fact)
        add_fact(fact, area)
        answered += 1
        d = _load()
        d["preguntas_hechas"] = (d.get("preguntas_hechas", []) + [q])[-200:]
        _save(d)
    if answered:
        session_done()
    after = score()["total"]
    _mood("satisfaccion", +5)
    tts.say(f"Gracias, señor. Sincronización del {before:.0f} al {after:.0f} por ciento." + (
        " " + check_level_up() if after >= 20 else ""))
