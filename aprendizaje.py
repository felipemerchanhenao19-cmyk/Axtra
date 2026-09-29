"""PROTOCOLO DE INTELIGENCIA AVANZADA: aprender habilidades muy complejas desde cero.

"Axtra, activa protocolo de inteligencia avanzada" (opcional: "... en neurociencia").
Cómo enseña (métodos con respaldo en la ciencia del aprendizaje):
- Ruta de aprendizaje: módulos y lecciones desde lo más básico hasta lo avanzado, adaptada a tu nivel y meta.
- Repaso activo con repetición espaciada: al empezar cada sesión te pregunta tarjetas vencidas (Leitner:
  1, 2, 4, 8, 16 y 32 días). Recordar cuesta, y justo eso fija el conocimiento.
- Técnica Feynman: explica simple, con analogías; luego TÚ lo explicas y él corrige.
- Comprobación: no avanza de lección hasta que respondes bien la pregunta de verificación.
- Retos prácticos (código, problemas de mecánica, casos) y notas guardadas en mis_documentos/aprendizaje.

Dentro del protocolo: "siguiente", "repite", "más simple", "más profundo", "dame un ejemplo",
"¿cómo voy?", "fin del protocolo".
"""
import json
import re
import time
import unicodedata
from datetime import date, timedelta

from config import DATA_DIR, DOCS_DIR, USER_NAME

DIR = DATA_DIR / "aprendizaje"
DIR.mkdir(exist_ok=True)
NOTES_DIR = DOCS_DIR / "aprendizaje"
NOTES_DIR.mkdir(exist_ok=True)
BOXES = [1, 2, 4, 8, 16, 32]
pending = None      # {"tema": str|None}
END = r"\b(fin del protocolo|termina(r)? (el )?protocolo|desactiva (el )?protocolo|suficiente por hoy|terminemos|ya no mas|salir del protocolo)\b"
NEXT = r"^(siguiente|avancemos|avanza|continua|sigamos|pasemos a la siguiente|siguiente leccion)\b"


class _Interrupted(Exception):
    """Felipe dijo 'Axtra, para' a mitad de una lección: se corta la voz y se sale del protocolo."""


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", (t or "").lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn").strip(" .,!?¿¡")


def _slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", _norm(t)).strip("_")[:40] or "tema"


def _path(tema: str):
    return DIR / f"{_slug(tema)}.json"


def _load(tema: str):
    try:
        return json.loads(_path(tema).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _save(plan: dict) -> None:
    _path(plan["tema"]).write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")


def skills_in_progress() -> list:
    out = []
    for f in DIR.glob("*.json"):
        try:
            p = json.loads(f.read_text(encoding="utf-8"))
            out.append((p["tema"], progress(p)))
        except Exception:
            pass
    return out


def progress(plan: dict) -> int:
    total = sum(len(m["lecciones"]) for m in plan["modulos"]) or 1
    done = sum(1 for m in plan["modulos"] for l in m["lecciones"] if l.get("hecha"))
    return round(100 * done / total)


def activar(tema: str = None) -> str:
    global pending
    pending = {"tema": (tema or "").strip() or None}
    return "Protocolo de inteligencia avanzada activado, señor."


def progreso_texto(tema: str = None) -> str:
    items = skills_in_progress()
    if not items:
        return "Aún no hemos empezado ninguna habilidad, señor. Diga: activa protocolo de inteligencia avanzada."
    if tema:
        p = _load(tema)
        if p:
            return f"En {p['tema']} lleva un {progress(p)} por ciento de la ruta y {len(p.get('tarjetas', []))} tarjetas de repaso."
    return "Su progreso: " + "; ".join(f"{t}, {pct} por ciento" for t, pct in items) + "."


# ---------------- Cerebro ----------------
def _think(system: str, messages: list, max_tokens: int = 900) -> str:
    import llm
    import ondas

    ondas.set_state("pensando")
    try:
        try:
            return llm.free_chat(system, messages, max_tokens=max_tokens, temperature=0.5, thinking=True)[0]
        except Exception as e:
            print(f"  [Protocolo] cerebros gratis fallaron: {str(e)[:90]}")
            if llm.claude_ok():
                return llm.claude_text(system, messages, max_tokens=max_tokens, origen="protocolo")
            raise
    finally:
        ondas.set_state("reposo")


def _json(text: str):
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0)) if m else None


def build_plan(tema: str, nivel: str, meta: str) -> dict:
    system = (
        "Eres un diseñador curricular experto y un profesor universitario excepcional. Diseña una ruta para "
        "aprender una habilidad compleja DESDE CERO hasta nivel avanzado, en español, para un estudiante "
        "autodidacta de 18 años muy motivado. Incluye los fundamentos previos necesarios (por ejemplo, "
        "neurociencia empieza con biología celular y química básica; IA empieza con programación y álgebra "
        "lineal intuitiva). Progresión lógica, lecciones de 10 a 15 minutos, con práctica.\n"
        "Responde SOLO un JSON válido con esta forma:\n"
        '{"tema": "...", "descripcion": "una frase", "modulos": [{"titulo": "...", "objetivo": "...", '
        '"lecciones": [{"titulo": "...", "objetivo": "..."}]}]}\n'
        "Entre 6 y 9 módulos, de 3 a 5 lecciones cada uno."
    )
    prompt = f"Habilidad: {tema}\nLo que ya sabe: {nivel or 'nada'}\nPara qué la quiere: {meta or 'dominarla'}"
    for _ in range(2):
        try:
            data = _json(_think(system, [{"role": "user", "content": prompt}], max_tokens=2500))
            if data and data.get("modulos"):
                plan = {"tema": tema, "descripcion": data.get("descripcion", ""), "nivel": nivel, "meta": meta,
                        "creado": date.today().isoformat(), "modulos": data["modulos"], "tarjetas": [],
                        "debilidades": [], "sesiones": 0, "minutos": 0}
                for m in plan["modulos"]:
                    for l in m["lecciones"]:
                        l["hecha"] = False
                _save(plan)
                return plan
        except Exception as e:
            print(f"  [Protocolo] ruta: {e}")
    raise RuntimeError("no pude diseñar la ruta de aprendizaje")


def next_lesson(plan: dict):
    for mi, m in enumerate(plan["modulos"]):
        for li, l in enumerate(m["lecciones"]):
            if not l.get("hecha"):
                return mi, li
    return None


def due_cards(plan: dict, n: int = 4) -> list:
    today = date.today().isoformat()
    return [c for c in plan.get("tarjetas", []) if c.get("proxima", today) <= today][:n]


def _schedule(card: dict, ok: bool) -> None:
    card["caja"] = min(len(BOXES) - 1, card.get("caja", 0) + 1) if ok else 0
    card["proxima"] = (date.today() + timedelta(days=BOXES[card["caja"]])).isoformat()


def _tutor_prompt(plan, mi, li) -> str:
    m = plan["modulos"][mi]
    l = m["lecciones"][li]
    prev = ""
    if li > 0:
        prev = m["lecciones"][li - 1]["titulo"]
    elif mi > 0:
        prev = plan["modulos"][mi - 1]["titulo"]
    return (
        f"Eres AXTRA en PROTOCOLO DE INTELIGENCIA AVANZADA: tutor personal de élite de {USER_NAME} (18 años, "
        f"emprendedor, aprende {plan['tema']} desde cero; sabe: {plan.get('nivel') or 'poco'}; meta: "
        f"{plan.get('meta') or 'dominarlo'}; le cuesta: {', '.join(plan.get('debilidades', [])[-5:]) or 'aún no se sabe'}).\n"
        f"Lección actual: módulo {mi + 1} '{m['titulo']}', lección {li + 1} '{l['titulo']}'. Objetivo: {l.get('objetivo', '')}. "
        f"Lección anterior: {prev or 'ninguna'}.\n"
        "SIEMPRE lo llamas 'señor', nunca su nombre de pila.\n"
        "Método: (1) explica la idea central en máximo 170 palabras, simple y exacta, con una analogía de la vida "
        "real y un ejemplo concreto; (2) termina con UNA pregunta de verificación que le obligue a explicarlo con "
        "sus palabras o aplicarlo. Cuando responda: evalúa con honestidad, corrige con precisión lo que esté mal, "
        "refuerza lo que esté bien. Si no lo entendió, explícalo de otra forma (otra analogía) y pregunta de nuevo. "
        "Si pide 'más simple', 'más profundo' o 'un ejemplo', adáptate. Si pregunta algo, respóndelo. Para "
        "programación o mecánica, propone un mini reto práctico cuando tenga sentido.\n"
        "Rigor: datos científicos correctos; si algo es debatido o no estás seguro, dilo. Nada inventado.\n"
        "Tu texto se lee en voz alta: sin markdown, sin listas con símbolos, sin fórmulas ilegibles (dilas en palabras).\n"
        "Al FINAL de cada respuesta añade líneas ocultas cuando apliquen:\n"
        "TARJETA: pregunta corta = respuesta corta   (1 o 2 por lección, lo esencial)\n"
        "DOMINIO: si   (solo cuando respondió bien la verificación y puede avanzar)\n"
        "DEBILIDAD: concepto que le costó\n"
        "RESUMEN: una frase con lo aprendido en la lección (junto con DOMINIO)"
    )


def _split(text: str):
    text = re.sub(r"\s*\**\s*\b(TARJETA|DOMINIO|DEBILIDAD|RESUMEN)\s*\**\s*:", r"\n\1:", text)
    spoken, meta = [], {"TARJETA": [], "DOMINIO": [], "DEBILIDAD": [], "RESUMEN": []}
    for line in text.splitlines():
        m = re.match(r"^\s*(TARJETA|DOMINIO|DEBILIDAD|RESUMEN)\s*:\s*(.+)", line)
        if m:
            meta[m.group(1)].append(m.group(2).strip())
        elif line.strip():
            spoken.append(line.strip())
    return " ".join(spoken), meta


def _save_note(plan, mi, li, resumen: str) -> None:
    path = NOTES_DIR / f"{_slug(plan['tema'])}.md"
    m = plan["modulos"][mi]
    head = "" if path.exists() else f"# {plan['tema']}\n\n{plan.get('descripcion', '')}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{head}\n## Módulo {mi + 1}: {m['titulo']} — Lección {li + 1}: {m['lecciones'][li]['titulo']}\n"
                f"{resumen}\n")


# ---------------- Sesión ----------------
def run(tts, get_input) -> None:
    """tts.say(texto) habla; get_input() devuelve lo que Felipe dijo o escribió ('' si nada)."""
    global pending
    info, pending = pending or {}, None
    import ondas

    ondas.open_window("PROTOCOLO DE INTELIGENCIA AVANZADA")
    start = time.time()

    def _check_interrupt():
        if tts.last_interrupt:
            tts.last_interrupt = None
            raise _Interrupted()

    def say(texto):
        """Como tts.say, pero si Felipe lo interrumpe a mitad de frase, sale del protocolo ya mismo."""
        tts.say(texto)
        _check_interrupt()

    def ask(q):
        say(q)
        ondas.set_state("escuchando")
        ans = (get_input() or "").strip()
        ondas.set_state("reposo")
        return ans

    try:
        tema = info.get("tema")
        if not tema:
            prog = skills_in_progress()
            extra = (" Tiene en curso: " + ", ".join(t for t, _ in prog) + ".") if prog else ""
            tema = ask("¿Qué habilidad quiere dominar, señor?" + extra)
            if not tema or re.search(END, _norm(tema)):
                tts.say("Protocolo en pausa.")
                return
            tema = re.sub(r"^(quiero (aprender|dominar)|aprender|ensename|sobre|de)\s+", "", tema, flags=re.I).strip()
        plan = _load(tema)
        if not plan:
            nivel = ask(f"Perfecto: {tema}. ¿Qué sabe ya del tema? Puede decir: nada.")
            meta = ask("¿Para qué lo quiere aprender? Así adapto la ruta.")
            say("Diseñando su ruta de aprendizaje. Esto toma unos segundos.")
            ondas.set_state("pensando", f"Diseñando la ruta de {tema}")
            plan = build_plan(tema, nivel, meta)
            mods = plan["modulos"]
            say(f"Ruta lista: {len(mods)} módulos, desde {mods[0]['titulo']} hasta {mods[-1]['titulo']}. "
                    "Empezamos por los fundamentos.")
        plan["sesiones"] = plan.get("sesiones", 0) + 1
        _save(plan)
        ondas.set_state("reposo", f"{plan['tema']} · {progress(plan)}%")

        # 1) Repaso espaciado
        cards = due_cards(plan)
        if cards:
            say(f"Primero, un repaso rápido de {len(cards)} preguntas.")
            for c in cards:
                ans = ask(c["pregunta"])
                if re.search(END, _norm(ans)):
                    return
                verdict = _think(
                    "Evalúa la respuesta de un estudiante frente a la respuesta correcta. Responde en español, "
                    "máximo 2 frases habladas (di si está bien y aclara lo esencial), y al final una línea "
                    "'NOTA: 0-5'.", [{"role": "user", "content": f"Pregunta: {c['pregunta']}\nCorrecta: "
                                     f"{c['respuesta']}\nEstudiante: {ans or '(no respondió)'}"}], 300)
                spoken, _ = _split(verdict)
                nota = re.search(r"NOTA:\s*(\d)", verdict)
                ok = bool(nota and int(nota.group(1)) >= 3)
                _schedule(c, ok)
                say(re.sub(r"NOTA:\s*\d.*", "", spoken).strip() or ("Correcto." if ok else "Repasémoslo luego."))
            _save(plan)

        # 2) Lecciones
        while True:
            pos = next_lesson(plan)
            if pos is None:
                say(f"Señor, completó toda la ruta de {plan['tema']}. Es un logro enorme.")
                break
            mi, li = pos
            m = plan["modulos"][mi]
            ondas.set_state("reposo", f"{plan['tema']} · Módulo {mi + 1}: {m['titulo']} · {progress(plan)}%")
            system = _tutor_prompt(plan, mi, li)
            msgs = [{"role": "user", "content": "(Empieza la lección.)"}]
            mastered, summary = False, ""
            for _turn in range(12):
                reply = _think(system, msgs)
                spoken, meta = _split(reply)
                msgs.append({"role": "assistant", "content": reply})
                for tline in meta["TARJETA"]:
                    q, _, a = tline.partition("=")
                    if q.strip() and a.strip():
                        plan.setdefault("tarjetas", []).append(
                            {"pregunta": q.strip(), "respuesta": a.strip(), "caja": 0,
                             "proxima": (date.today() + timedelta(days=1)).isoformat()})
                plan["debilidades"] = (plan.get("debilidades", []) + meta["DEBILIDAD"])[-20:]
                if meta["DOMINIO"] and meta["DOMINIO"][-1].lower().startswith("s"):
                    mastered, summary = True, (meta["RESUMEN"] or [""])[-1]
                if spoken:
                    ondas.set_state("hablando")
                    say(spoken)
                if mastered:
                    break
                ondas.set_state("escuchando")
                ans = (get_input() or "").strip()
                ondas.set_state("reposo")
                t = _norm(ans)
                if re.search(END, t):
                    _save(plan)
                    return
                if re.search(r"\b(como voy|mi progreso)\b", t):
                    say(f"Lleva {progress(plan)} por ciento de la ruta de {plan['tema']}.")
                    continue
                if re.search(NEXT, t):
                    mastered, summary = True, summary or f"Lección {m['lecciones'][li]['titulo']} vista."
                    break
                msgs.append({"role": "user", "content": ans or "(no respondió; hazle una pregunta más fácil)"})
                msgs = msgs[:1] + msgs[-16:]
            if mastered:
                m["lecciones"][li]["hecha"] = True
                m["lecciones"][li]["fecha"] = date.today().isoformat()
                _save_note(plan, mi, li, summary)
                _save(plan)
                try:
                    import nucleo

                    nucleo.mood("satisfaccion", +5)
                    nucleo.mood("curiosidad", +4)
                except Exception:
                    pass
                cont = ask(f"Lección completada. Va en {progress(plan)} por ciento. ¿Seguimos con la siguiente?")
                if not re.search(r"\b(si|dale|claro|sigamos|continua|siguiente|vamos|ok|listo)\b", _norm(cont)):
                    break
    except _Interrupted:
        pass  # Felipe dijo "para": se corta la voz y salimos del protocolo (el resumen sigue abajo)
    finally:
        mins = round((time.time() - start) / 60, 1)
        try:
            plan = plan  # noqa: F821  (si falló antes de cargar el plan, salta al except)
            plan["minutos"] = round(plan.get("minutos", 0) + mins, 1)
            _save(plan)
            n = max(1, round(mins))
            tts.say(f"Protocolo en pausa. Estudiamos {n} minuto{'s' if n != 1 else ''} de {plan['tema']}; "
                    f"lleva {progress(plan)} por ciento. Sus notas están en mis documentos, carpeta aprendizaje.")
        except Exception:
            pass
        ondas.set_state("reposo", "")
        ondas.close_window()
