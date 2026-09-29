"""Modo dictado: hablas tu trabajo y Axtra lo convierte en un documento Word con TUS palabras.

Axtra solo corrige ortografía, puntuación y orden; no inventa contenido ni cambia tus ideas.
Comandos mientras dictas:
  "nuevo párrafo" / "punto aparte"   → nuevo párrafo
  "título ..."                        → crea un título
  "borra lo último"                   → elimina la última frase
  "fin del dictado"                   → termina y crea el documento
"""
import anthropic

import usage
from audio import record_utterance
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

pending = None  # {"titulo": ..., "tipo": ...} cuando Felipe pide dictar

END = ("fin del dictado", "terminar dictado", "termina el dictado", "finalizar dictado")
UNDO = ("borra lo último", "borra lo ultimo", "borrar lo último", "borrar lo ultimo")

FORMAT_PROMPT = (
    "Eres un editor. Recibes el dictado de un estudiante universitario transcrito por voz. "
    "Conviértelo en un documento limpio respetando SUS palabras, su estilo y sus ideas:\n"
    "- Corrige ortografía, tildes, puntuación, mayúsculas y errores evidentes de la transcripción.\n"
    "- Une frases entrecortadas y quita muletillas (eh, este, o sea) y repeticiones.\n"
    "- Interpreta los comandos 'nuevo párrafo', 'punto aparte' y 'título ...' como formato.\n"
    "- Organiza en párrafos; usa '# ' para títulos solo si él los dictó o si es obvio.\n"
    "- NO agregues ideas, datos, argumentos, ejemplos ni fuentes que él no dijo. Si algo quedó "
    "incompleto o confuso, marca [revisar: ...].\n"
    "Responde SOLO con el texto final."
)


def iniciar_dictado(titulo: str, tipo: str = "trabajo") -> dict:
    global pending
    pending = {"titulo": titulo, "tipo": tipo}
    return {"ok": True, "nota": "El modo dictado empieza en cuanto termines de hablar conmigo."}


def run(tts, stt) -> None:
    global pending
    info, pending = pending, None
    if not info:
        return
    tts.say("Modo dictado activado, señor. Hable con calma. Diga nuevo párrafo para cambiar de "
            "párrafo, y fin del dictado cuando termine.")
    parts, silent = [], 0
    while True:
        print("  [Dictado] escuchando...")
        audio = record_utterance(start_timeout=90, max_seconds=60, silence_end=2.5)
        if audio is None:
            silent += 1
            if silent >= 2:
                tts.say("No le escucho. Cierro el dictado con lo que tenemos.")
                break
            tts.say("¿Sigue ahí, señor? Continúe cuando quiera.", cache=True)
            continue
        silent = 0
        text = stt.transcribe(audio)
        if not text:
            continue
        low = text.lower()
        if any(u in low for u in UNDO):
            if parts:
                print(f"  [Dictado] borrado: {parts.pop()}")
            tts.say("Borrado.", cache=True)
            continue
        end = next((e for e in END if e in low), None)
        if end:
            before = text[:low.index(end)].strip()
            if before:
                parts.append(before)
            break
        parts.append(text)
        print(f"  [Dictado] {text}")

    if not parts:
        tts.say("El dictado quedó vacío, señor.")
        return
    tts.say("Un momento, estoy organizando su documento.", cache=True)
    raw = "\n".join(parts)
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        resp = client.messages.create(model=CLAUDE_MODEL, max_tokens=8000, system=FORMAT_PROMPT,
                                      messages=[{"role": "user", "content": raw}])
        usage.record(resp, "dictado")
        clean = "".join(b.text for b in resp.content if b.type == "text").strip() or raw
    except Exception as e:
        print(f"  [Dictado] no pude organizarlo ({e}); guardo el texto tal cual.")
        clean = raw
    import business

    business.guardar_documento(info["titulo"], clean, "docx")
    business.guardar_documento(info["titulo"] + " (dictado original)", raw, "md", abrir_ahora=False)
    words = len(clean.split())
    tts.say(f"Listo, señor. Su documento de {words} palabras está abierto en Word. "
            "También guardé el dictado original, sin editar.")


TOOL_SCHEMAS = [{
    "name": "iniciar_dictado",
    "description": "Activa el modo dictado: Felipe dicta un trabajo o documento con su voz y Axtra lo convierte en un Word con sus propias palabras (solo corrige y organiza).",
    "input_schema": {"type": "object", "properties": {"titulo": {"type": "string"}, "tipo": {"type": "string"}}, "required": ["titulo"]},
}]
FUNCS = {"iniciar_dictado": iniciar_dictado}
