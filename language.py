"""Profesor de idiomas: conversación por voz en inglés (y otros idiomas) con corrección y progreso.

Cómo funciona una clase:
- Axtra cambia a una voz nativa multilingüe y te habla en el idioma que practicas.
- Te corrige con amabilidad (explica en español si hace falta) y sigue la conversación.
- Guarda tu vocabulario nuevo y tus errores frecuentes para repasarlos en la siguiente clase.
- Dices "fin de la clase" o "end the lesson" para terminar y recibir tu resumen.
"""
import json
import re
from datetime import datetime

import llm
from audio import record_utterance
from config import BRAIN_MODE, DATA_DIR, LANGUAGE_BRAIN, USER_NAME

PROGRESS_PATH = DATA_DIR / "idiomas.json"
pending = None

LANGS = {
    "ingles": ("inglés", "en-US", "en-US-AndrewMultilingualNeural"),
    "frances": ("francés", "fr-FR", "fr-FR-RemyMultilingualNeural"),
    "portugues": ("portugués", "pt-BR", "en-US-AndrewMultilingualNeural"),
    "aleman": ("alemán", "de-DE", "de-DE-FlorianMultilingualNeural"),
    "italiano": ("italiano", "it-IT", "it-IT-GiuseppeMultilingualNeural"),
    "mandarin": ("chino mandarín", "zh-CN", "en-US-AndrewMultilingualNeural"),
    "japones": ("japonés", "ja-JP", "en-US-AndrewMultilingualNeural"),
}
END = ("fin de la clase", "terminar la clase", "termina la clase", "end the lesson",
       "end of the lesson", "finish the lesson", "stop the lesson")


def _key(idioma: str) -> str:
    k = idioma.lower().strip()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("english", "ingles")):
        k = k.replace(a, b)
    return next((x for x in LANGS if x in k), "ingles")


def _progress():
    try:
        return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(p):
    PROGRESS_PATH.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")


def iniciar_clase(idioma: str = "inglés", nivel: str = "", tema: str = "") -> dict:
    global pending
    pending = {"idioma": _key(idioma), "nivel": nivel, "tema": tema}
    return {"ok": True, "nota": "La clase empieza apenas termines de hablar conmigo."}


def progreso_idiomas() -> dict:
    p = _progress()
    return {k: {"nivel": v.get("nivel"), "clases": v.get("clases", 0), "minutos": v.get("minutos", 0),
                "palabras_aprendidas": len(v.get("vocabulario", [])),
                "errores_frecuentes": v.get("errores", [])[-5:]} for k, v in p.items()} or {
        "nota": "Aún no has tomado clases. Di: 'Axtra, quiero practicar inglés'."}


def _tutor_prompt(name, lang, info, prog):
    vocab = ", ".join(prog.get("vocabulario", [])[-15:]) or "ninguno aún"
    errors = "; ".join(prog.get("errores", [])[-8:]) or "ninguno aún"
    level = info["nivel"] or prog.get("nivel") or "desconocido (evalúalo en los primeros turnos)"
    return (
        f"Eres AXTRA, ahora profesor particular de {name} de {USER_NAME}, un emprendedor colombiano de 18 "
        f"años interesado en negocios, bolsa, tecnología e IA. Nivel: {level}. Tema de hoy: "
        f"{info['tema'] or 'conversación libre sobre sus intereses'}.\n"
        "- SIEMPRE lo llamas 'señor' en español, nunca su nombre de pila.\n"
        f"- Habla principalmente en {name}, con frases cortas y naturales (esto se convierte en voz).\n"
        "- Ajusta la dificultad a su nivel: si es básico, habla despacio y simple, y aclara en español "
        "solo lo necesario.\n"
        "- Cuando cometa un error importante, corrígelo brevemente: dale la forma correcta y sigue la "
        "conversación. No corrijas todo, solo lo que más le ayuda.\n"
        "- Haz siempre una pregunta para que él siga hablando. Él debe hablar más que tú.\n"
        "- Repasa de forma natural este vocabulario y estos errores de clases anteriores: "
        f"vocabulario [{vocab}]; errores [{errors}].\n"
        "- Si te pregunta algo en español, respóndele y vuelve al idioma.\n"
        "- El texto que te llega es una transcripción de voz: si una palabra suena rara, puede ser "
        "un problema de pronunciación; menciónalo con tacto.\n"
        "- Al FINAL de cada respuesta agrega líneas ocultas (no se leen en voz alta) solo si aplican:\n"
        "VOCAB: palabra = significado\nERROR: lo que dijo -> forma correcta\nNIVEL: A1/A2/B1/B2/C1\n"
        "Sin markdown ni listas en la parte hablada."
    )


def _split(text):
    spoken, meta = [], {"VOCAB": [], "ERROR": [], "NIVEL": []}
    # los modelos pequeños a veces ponen "VOCAB:" en la misma línea: sepáralo
    text = re.sub(r"\s*\**\s*\b(VOCAB|ERROR|NIVEL)\s*\**\s*:", r"\n\1:", text)
    for line in text.splitlines():
        m = re.match(r"^\s*(VOCAB|ERROR|NIVEL)\s*:\s*(.+)", line)
        if m:
            meta[m.group(1)].append(m.group(2).strip())
        else:
            spoken.append(line)
    return " ".join(spoken).strip(), meta


def run(tts, stt) -> None:
    global pending
    info, pending = pending, None
    if not info:
        return
    name, stt_lang, voice = LANGS[info["idioma"]]
    p = _progress()
    prog = p.setdefault(info["idioma"], {"clases": 0, "minutos": 0, "vocabulario": [], "errores": [], "nivel": ""})
    prefer = LANGUAGE_BRAIN if LANGUAGE_BRAIN in ("gemini", "local", "claude") else "gemini"
    if prefer == "claude" and not llm.claude_ok():
        prefer = "local"
    if prefer == "gemini" and not llm.free_ok():
        prefer = "local"
    print(f"  [Clase] Cerebro: {dict(claude='Claude', gemini='nube gratis (Gemini/Groq/OpenRouter)', local='local (gratis)')[prefer]}")
    system = _tutor_prompt(name, info["idioma"], info, prog)
    messages = [{"role": "user", "content": f"(Empieza la clase de {name}: salúdame y hazme la primera pregunta.)"}]
    start = datetime.now()
    tts.voice_override = (voice, "-8%" if prog.get("nivel", "") in ("", "A1", "A2") else "+0%", "+0Hz")
    try:
        silent = 0
        while True:
            try:
                answer = llm.ask_text(system, messages, prefer=prefer, max_tokens=260 if prefer != "claude" else 500,
                                      origen=f"clase de {name}", temperature=0.6)
            except Exception as e:
                print(f"  [Clase] sin cerebro: {e}")
                tts.voice_override = None
                tts.say("Lo siento, señor, no tengo cerebro disponible para la clase. Abra Ollama, por favor.")
                return
            spoken, meta = _split(answer)
            messages.append({"role": "assistant", "content": answer})
            for v in meta["VOCAB"]:
                if v not in prog["vocabulario"]:
                    prog["vocabulario"].append(v)
            prog["errores"] = (prog["errores"] + [e for e in meta["ERROR"] if e not in prog["errores"][-10:]])[-40:]
            if meta["NIVEL"]:
                prog["nivel"] = meta["NIVEL"][-1][:2].upper()
            tts.say(spoken)

            audio = record_utterance(start_timeout=20, max_seconds=45, silence_end=1.8)
            if audio is None:
                silent += 1
                if silent >= 2:
                    break
                messages.append({"role": "user", "content": "(no respondió; anímalo con una pregunta más fácil)"})
                continue
            silent = 0
            text = stt.transcribe(audio, language=stt_lang, min_confidence=0.55)
            print(f"  [Clase] Tú: {text}")
            if any(e in text.lower() for e in END):
                break
            messages.append({"role": "user", "content": text or "(no se entendió lo que dijo)"})
            messages = messages[-30:]
            if messages[0]["role"] != "user":
                messages = messages[1:]
    finally:
        mins = round((datetime.now() - start).seconds / 60, 1)
        prog["clases"] += 1
        prog["minutos"] = round(prog["minutos"] + mins, 1)
        prog["vocabulario"] = prog["vocabulario"][-300:]
        _save(p)
        tts.voice_override = None
    nuevos = len(prog["vocabulario"])
    clases = f"{prog['clases']} clase" + ("s" if prog["clases"] != 1 else "")
    n = max(1, round(mins))
    tts.say(f"Fin de la clase, señor. Practicamos {n} minuto{'s' if n != 1 else ''}. Lleva {clases} de "
            f"{name}, {nuevos} palabras en su vocabulario"
            + (f" y su nivel estimado es {prog['nivel']}." if prog.get("nivel") else "."))


TOOL_SCHEMAS = [
    {"name": "iniciar_clase", "description": "Inicia una clase de idiomas por voz (inglés por defecto; también francés, portugués, alemán, italiano, mandarín, japonés). Opcional: nivel (A1-C1) y tema (ej: entrevista de trabajo, negocios, viajes).",
     "input_schema": {"type": "object", "properties": {"idioma": {"type": "string"}, "nivel": {"type": "string"}, "tema": {"type": "string"}}}},
    {"name": "progreso_idiomas", "description": "Progreso de Felipe en idiomas: nivel, clases, minutos, vocabulario y errores frecuentes.",
     "input_schema": {"type": "object", "properties": {}}},
]
FUNCS = {"iniciar_clase": iniciar_clase, "progreso_idiomas": progreso_idiomas}
