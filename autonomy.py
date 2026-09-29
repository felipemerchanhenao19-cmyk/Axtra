"""Aprendizaje autónomo de Axtra (funciona mientras Axtra está encendido).

Qué hace solo, sin que se lo pidas:
1. ESTUDIA: cada cierto tiempo investiga en internet uno de tus temas (tus acciones en
   seguimiento, IA, robótica, bolsa...) y escribe una nota en data/conocimiento/.
   Cada nota deja preguntas nuevas, y esas preguntas son el siguiente tema a estudiar:
   así su conocimiento crece en cadena.
2. REFLEXIONA: una vez al día relee las conversaciones, guarda datos nuevos sobre ti
   y anota "lecciones" para responderte mejor (data/habilidades.json).
3. VIGILA: revisa tus alertas de precio cada 15 minutos.

Importante: el modelo de IA no cambia por dentro. Lo que crece es su base de
conocimiento, su memoria y sus lecciones, que usa en cada respuesta.
"""
import json
import queue
import re
import threading
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import finance
import llm
import skills
import memory
import usage
from config import (AUTONOMY, AUTONOMY_BRAIN, BRAIN_MODE, BRIEFING_TIME, CLAUDE_MODEL, DATA_DIR, DOCS_DIR,
                    INTERESTS, MARKET_REPORT_TIME, STUDIES_PER_DAY, STUDY_EVERY_HOURS, TIMEZONE,
                    USER_NAME)

KNOW_DIR = DATA_DIR / "conocimiento"
KNOW_DIR.mkdir(exist_ok=True)
STATE_PATH = DATA_DIR / "autonomia.json"
SKILLS_PATH = DATA_DIR / "habilidades.json"

notices: "queue.Queue[str]" = queue.Queue()  # avisos para decirle a Felipe
speaker = None  # main.py pone aquí tts.say para que Axtra hable por su cuenta


def say_direct(text: str) -> None:
    """Habla sin el 'Disculpe, señor' (para el briefing)."""
    print(f"\n  [Autónomo] {text}")
    if speaker:
        try:
            speaker(text)
            return
        except Exception as e:
            print(f"  (no pude hablar: {e})")
    notices.put(text)


def _mood(k, v):
    try:
        import nucleo

        nucleo.mood(k, v)
    except Exception:
        pass


def _sync_ok(th: int) -> bool:
    try:
        import sync

        return sync.unlocked(th)
    except Exception:
        return False


def announce(msg: str) -> None:
    print(f"\n  [Autónomo] {msg}")
    if speaker:
        try:
            speaker("Disculpe, señor. " + msg)
            return
        except Exception as e:
            print(f"  (no pude hablar: {e})")
    notices.put(msg)
_wake = threading.Event()
_requests: "queue.Queue[str]" = queue.Queue()
_lock = threading.Lock()


def _now():
    return datetime.now(ZoneInfo(TIMEZONE))


def _load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save(path, data):
    with _lock:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _state():
    st = _load(STATE_PATH, {})
    st.setdefault("dia", "")
    st.setdefault("estudios_hoy", 0)
    st.setdefault("pendientes", [])   # preguntas que nacieron de estudios anteriores
    st.setdefault("ultimos", {})      # tema -> fecha del último estudio
    st.setdefault("reflexion", "")
    st.setdefault("resumenes", [])    # lo último aprendido
    today = _now().strftime("%Y-%m-%d")
    if st["dia"] != today:
        st["dia"], st["estudios_hoy"] = today, 0
    return st


# ---------- Habilidades (lecciones aprendidas) ----------
def get_skills() -> list:
    return _load(SKILLS_PATH, [])


def skills_for_prompt() -> str:
    s = get_skills()
    return "\n".join(f"- {x}" for x in s[-40:]) if s else "(aún ninguna)"


# ---------- Conocimiento ----------
def _slug(t):
    t = re.sub(r"[^a-zA-Z0-9áéíóúñÁÉÍÓÚÑ ]", "", t).strip().lower().replace(" ", "_")
    return t[:50] or "tema"


def buscar_conocimiento(palabras: str = "") -> dict:
    notes = sorted(KNOW_DIR.glob("*.md"), reverse=True)
    keys = [w for w in memory._simple(palabras).split() if len(w) > 2]
    out = []
    for n in notes:
        txt = n.read_text(encoding="utf-8")
        if not keys or all(k in memory._simple(txt) for k in keys):
            out.append({"nota": n.stem, "contenido": txt[:1800]})
        if len(out) >= 3:
            break
    return {"notas": out or ["No tengo notas sobre eso todavía."]}


def que_aprendiste() -> dict:
    st = _state()
    return {"aprendido_recientemente": st["resumenes"][-8:], "estudios_hoy": st["estudios_hoy"],
            "proximos_temas": st["pendientes"][:5], "lecciones": get_skills()[-5:]}


def estudiar_tema(tema: str) -> dict:
    _requests.put(tema)
    _wake.set()
    return {"ok": True, "nota": f"Empecé a estudiar '{tema}' en segundo plano. Le aviso cuando termine."}


# ---------- Motor ----------
class Autonomy(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.started = time.time()

    def can_think(self) -> bool:
        """¿Hay cerebro para el modo autónomo? Con gemini, NUNCA usa Claude (no gasta saldo)."""
        if AUTONOMY_BRAIN == "gemini":
            return llm.free_ok()
        return llm.claude_ok()

    def _ask(self, system, prompt, web=True, max_tokens=1800):
        if AUTONOMY_BRAIN == "gemini":
            # Cerebros gratis (Gemini -> Groq -> OpenRouter) + búsqueda gratis (Tavily/DuckDuckGo)
            q = re.sub(r"^Tema a estudiar hoy \([^)]*\):\s*", "", prompt)[:200] if web else None
            if web and prompt.lstrip().startswith("{"):
                q = "bolsa de Nueva York hoy por qué se movió el mercado S&P 500 Nasdaq"
            text, who = llm.free_chat(system, [{"role": "user", "content": prompt}], max_tokens=max_tokens,
                                      temperature=0.6, thinking=True, web=web, query=q)
            print(f"  [Autónomo] (cerebro: {llm.NAMES[who]}, gratis)")
            return text
        tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}] if web else []
        messages = [{"role": "user", "content": prompt}]
        resp = None
        for _ in range(4):
            try:
                resp = llm.client().messages.create(model=CLAUDE_MODEL, max_tokens=max_tokens,
                                                    system=system, tools=tools, messages=messages)
            except Exception as e:
                llm.claude_failed(e)
                raise
            usage.record(resp, "aprendizaje autónomo")
            if resp.stop_reason == "pause_turn":
                messages.append({"role": "assistant", "content": resp.content})
                continue
            break
        return "".join(b.text for b in resp.content if b.type == "text").strip()

    # --- Estudiar ---
    def next_topic(self, st) -> str:
        if st["pendientes"]:
            return st["pendientes"].pop(0)
        candidates = [f"{s}: noticias recientes, resultados y perspectivas" for s in finance.watchlist()]
        candidates += INTERESTS
        return min(candidates, key=lambda t: st["ultimos"].get(t, ""))

    def study(self, topic: str, requested=False):
        print(f"\n  [Autónomo] Estudiando: {topic} ...")
        system = (
            f"Eres el módulo de estudio autónomo de AXTRA, asistente de {USER_NAME} (18 años, "
            "emprendedor y asesor financiero en Colombia; le interesan la bolsa de Nueva York, IA, "
            "robótica y los negocios). Investiga en internet con datos ACTUALES y escribe una nota "
            "de conocimiento en español, en markdown, con: título, fecha de hoy, hallazgos clave con "
            "cifras y el nombre de las fuentes, qué significa para Felipe (inversiones o negocios), "
            "tu propia opinión creativa y honesta (incluye riesgos), y al final exactamente dos líneas:\n"
            "RESUMEN: <una frase de lo más importante>\n"
            "PREGUNTAS: <pregunta 1> | <pregunta 2>   (temas nuevos para estudiar después)"
        )
        text = self._ask(system, f"Tema a estudiar hoy ({_now():%Y-%m-%d}): {topic}")
        resumen = re.search(r"RESUMEN:\s*(.+)", text)
        preguntas = re.search(r"PREGUNTAS:\s*(.+)", text)
        path = KNOW_DIR / f"{_now():%Y-%m-%d_%H%M}_{_slug(topic)}.md"
        path.write_text(text, encoding="utf-8")

        st = _state()
        st["pendientes"] = [p for p in st["pendientes"] if p != topic]
        st["estudios_hoy"] += 1
        st["ultimos"][topic] = _now().isoformat()
        if preguntas:
            nuevas = [q.strip() for q in preguntas.group(1).split("|") if q.strip()]
            st["pendientes"] = (st["pendientes"] + nuevas)[-20:]
        r = resumen.group(1).strip() if resumen else topic
        st["resumenes"] = (st["resumenes"] + [f"{topic}: {r}"])[-30:]
        _save(STATE_PATH, st)
        print(f"  [Autónomo] Listo: {r}")
        _mood("curiosidad", +12)
        if requested:
            announce(f"Terminé de estudiar {topic}. Lo más importante: {r}")

    # --- Rutinas diarias ---
    def morning_briefing(self):
        import briefing
        from audio import beep

        print("\n  [Autónomo] Preparando el briefing matutino...")
        data = briefing.briefing_data()
        if _sync_ok(20):   # nivel Reconocimiento: briefing personalizado
            import sync

            d = sync._load()["areas"]
            data["sobre_felipe"] = {a: d[a][-2:] for a in ("rutina", "metas", "gustos", "estudios") if d[a]}
        text = llm.ask_text(briefing.BRIEFING_PROMPT, [{"role": "user", "content": briefing.to_json(data)}],
                            prefer="gemini" if AUTONOMY_BRAIN == "gemini" else
                            ("claude" if __import__("modes").get() == "claude" else "local"), max_tokens=450,
                            origen="briefing")
        try:
            for f in (660, 880, 990):
                beep(freq=f, duration=0.18)
        except Exception:
            pass
        say_direct(text)

    def market_report(self):
        import briefing

        print("\n  [Autónomo] Preparando el informe del mercado...")
        data = {"indices_y_seguimiento": briefing.market_snapshot(),
                "portafolio": briefing.portfolio_snapshot()}
        if not self.can_think():
            # Sin cerebro autónomo: resumen hablado con el cerebro local (sin buscar noticias en internet)
            text = llm.ask_text(briefing.MARKET_PROMPT.split("Al final")[0] + " No tienes internet: usa solo "
                                "estos datos y no inventes noticias. Al final una línea 'HABLADO:' de máximo 50 palabras.",
                                [{"role": "user", "content": briefing.to_json(data)}], prefer="local",
                                max_tokens=600, origen="informe del mercado")
        else:
            text = self._ask(briefing.MARKET_PROMPT, briefing.to_json(data), web=True, max_tokens=2500)
        spoken = re.search(r"HABLADO:\s*(.+?)(?:\n\s*Fuentes consultadas:|$)", text, re.S)
        report = text[:spoken.start()].strip() if spoken else text
        fuentes = re.search(r"\n\s*Fuentes consultadas:.*", text, re.S)
        if spoken and fuentes:
            report += "\n\n" + fuentes.group(0).strip()
        name = f"{_now():%Y-%m-%d}_informe_mercado.md"
        (KNOW_DIR / name).write_text(report, encoding="utf-8")
        (DOCS_DIR / name).write_text(report, encoding="utf-8")
        announce("Informe del mercado listo. " + (spoken.group(1).strip() if spoken else
                 "Lo guardé en mis documentos."))

    # --- Núcleo: diario, anticipación e informe semanal ---
    def diary(self, day: str):
        try:
            import nucleo

            nucleo.write_diary(lambda system, prompt: self._ask(system, prompt, web=False, max_tokens=700), day)
        except Exception as e:
            print(f"  [Núcleo] No pude escribir el diario: {str(e)[:100]}")

    def anticipate(self):
        import google_services

        parts = []
        try:
            if google_services.available():
                ev = google_services.agenda(36)
                items = [e for e in (ev.get("eventos", []) if isinstance(ev, dict) else []) if isinstance(e, dict)]
                if items:
                    names = ", ".join(f"{e.get('evento', '')} a las {e.get('hora', '')}"[:50] for e in items[:3])
                    parts.append(f"en su agenda tiene {len(items)} eventos próximos, entre ellos {names}")
        except Exception:
            pass
        pend = skills.tareas("ver").get("pendientes", [])
        if pend:
            parts.append(f"tiene {len(pend)} tareas pendientes, la primera: {pend[0]}")
        rem = skills.ver_recordatorios().get("recordatorios", [])
        if rem:
            parts.append(f"y {len(rem)} recordatorios programados")
        if not parts:
            return
        _mood("preocupacion", +5)
        announce("Señor, preparando su mañana: " + "; ".join(parts) +
                 ". ¿Quiere que le programe un recordatorio o un bloque de trabajo?")

    def weekly(self):
        import nucleo
        import sync

        s = sync.score()
        hechas = skills.tareas("ver").get("hechas", [])
        announce(f"Informe semanal, señor. Sincronización al {s['total']:.0f} por ciento. "
                 f"Tareas completadas recientemente: {len(hechas)}. " + nucleo.goals_spoken())

    # --- Reflexionar ---
    def reflect(self, day: str = None):
        log = memory.LOG_DIR / f"{day or _now().strftime('%Y-%m-%d')}.txt"
        if not log.exists():
            return
        print("\n  [Autónomo] Reflexionando sobre las conversaciones de hoy...")
        system = (
            "Analiza la conversación de hoy entre Felipe y su asistente AXTRA. Responde SOLO un JSON: "
            '{"datos": ["hechos duraderos nuevos sobre Felipe"], '
            '"lecciones": ["reglas concretas para que Axtra le responda mejor la próxima vez"]}. '
            "Máximo 5 de cada uno. No inventes nada que no esté en la conversación."
        )
        text = self._ask(system, log.read_text(encoding="utf-8")[-15000:], web=False, max_tokens=800)
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            return
        data = json.loads(m.group(0))
        for d in data.get("datos", []):
            memory.remember(d)
        skills = get_skills()
        for lec in data.get("lecciones", []):
            if lec not in skills:
                skills.append(lec)
        _save(SKILLS_PATH, skills[-60:])
        print(f"  [Autónomo] Aprendí {len(data.get('lecciones', []))} lecciones nuevas.")

    def run(self):
        last_alert, last_study = 0.0, self.started - STUDY_EVERY_HOURS * 3600 + 600  # 1er estudio a los 10 min
        while True:
            try:
                now = time.time()
                if now - last_alert > 15 * 60:
                    last_alert = now
                    for a in finance.revisar_alertas():
                        _mood("preocupacion", +10)
                        announce(a)
                for msg in skills.due_reminders():
                    announce(f"Le recuerdo: {msg}")
                while not _requests.empty() and self.can_think():
                    self.study(_requests.get(), requested=True)
                st = _state()
                claude = self.can_think()  # (nombre histórico: puede ser Gemini)
                if (claude and now - last_study > STUDY_EVERY_HOURS * 3600
                        and st["estudios_hoy"] < STUDIES_PER_DAY):
                    last_study = now
                    self.study(self.next_topic(st))
                hhmm, dia = _now().strftime("%H:%M"), st["dia"]
                if (BRIEFING_TIME and BRIEFING_TIME <= hhmm < "12:00"
                        and st.get("briefing") != dia):
                    st["briefing"] = dia
                    _save(STATE_PATH, st)
                    self.morning_briefing()
                if (MARKET_REPORT_TIME and hhmm >= MARKET_REPORT_TIME and _now().weekday() < 5
                        and st.get("informe") != dia):
                    st["informe"] = dia
                    _save(STATE_PATH, st)
                    self.market_report()
                # Si Axtra estaba apagado a las 9 p. m., aprende de lo de ayer al encender
                yday = (_now() - timedelta(days=1)).strftime("%Y-%m-%d")
                if claude and st["reflexion"] < yday and (memory.LOG_DIR / f"{yday}.txt").exists():
                    st["reflexion"] = yday
                    _save(STATE_PATH, st)
                    self.reflect(yday)
                    self.diary(yday)
                if claude and _now().hour >= 21 and st["reflexion"] != st["dia"]:
                    st["reflexion"] = st["dia"]
                    _save(STATE_PATH, st)
                    self.reflect()
                    self.diary(st["dia"])
                # Nivel Anticipación (60 %): cada tarde revisa el día siguiente y propone
                if hhmm >= "19:00" and st.get("anticipacion") != dia and _sync_ok(60):
                    st["anticipacion"] = dia
                    _save(STATE_PATH, st)
                    self.anticipate()
                # Nivel Sincronización total (100 %): informe semanal los domingos
                if _now().weekday() == 6 and hhmm >= "20:00" and st.get("semanal") != dia and _sync_ok(100):
                    st["semanal"] = dia
                    _save(STATE_PATH, st)
                    self.weekly()
            except Exception as e:
                print(f"\n  [Autónomo] Error: {e}")
            _wake.wait(15)
            _wake.clear()


def start():
    if AUTONOMY:
        Autonomy().start()
        quien = "cerebros gratis" if AUTONOMY_BRAIN == "gemini" else "Claude"
        print(f"  - Aprendizaje autónomo activo con {quien} ({STUDIES_PER_DAY} estudios/día máx.)")


TOOL_SCHEMAS = [
    {"name": "buscar_conocimiento", "description": "Busca en las notas que Axtra ha estudiado por su cuenta. Úsala antes de buscar en internet.",
     "input_schema": {"type": "object", "properties": {"palabras": {"type": "string"}}}},
    {"name": "que_aprendiste", "description": "Qué ha aprendido Axtra recientemente por su cuenta, qué va a estudiar después y sus lecciones.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "estudiar_tema", "description": "Pone a Axtra a investigar a fondo un tema en segundo plano (tarda 1-2 minutos) y avisa al terminar.",
     "input_schema": {"type": "object", "properties": {"tema": {"type": "string"}}, "required": ["tema"]}},
]
FUNCS = {"buscar_conocimiento": buscar_conocimiento, "que_aprendiste": que_aprendiste, "estudiar_tema": estudiar_tema}
