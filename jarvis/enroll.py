"""Registra tu voz para que Jarvis solo te obedezca a ti. Ejecuta: python enroll.py"""
from audio import beep, record_utterance
from voice_id import VoiceID

FRASES = [
    "Jarvis, buenos días, ¿cómo está el clima hoy en Tuluá?",
    "Necesito revisar mis tareas pendientes para esta mañana.",
    "Busca las noticias más importantes sobre inteligencia artificial.",
    "Despiértame mañana a las seis y media, por favor.",
    "¿Cómo abrió hoy la bolsa de Nueva York con las acciones de tecnología?",
    "Recuérdame llamar a los clientes nuevos esta tarde.",
]


def main():
    print("Cargando el modelo de voz...")
    vid = VoiceID()
    print("\nVas a leer 6 frases en voz alta, con tu tono normal, en tu cuarto.")
    print("Después del pitido, lee la frase. Jarvis detecta solo cuando terminas.\n")

    embeddings = []
    for i, frase in enumerate(FRASES, 1):
        while True:
            input(f"[{i}/{len(FRASES)}] Presiona Enter y lee:\n   \"{frase}\"")
            beep()
            audio = record_utterance(start_timeout=8, max_seconds=12)
            emb = vid.embed(audio) if audio is not None else None
            if emb is not None:
                embeddings.append(emb)
                print("   ✓ Grabada\n")
                break
            print("   ✗ No te escuché bien, repitamos.\n")

    vid.voiceprint = VoiceID.save_voiceprint(embeddings)
    print("Huella de voz guardada en data/voiceprint.npy\n")

    print("Prueba: di cualquier frase después del pitido.")
    input("Presiona Enter...")
    beep()
    audio = record_utterance(start_timeout=8)
    if audio is not None:
        ok, score = vid.is_owner(audio)
        print(f"Similitud: {score:.2f} -> {'RECONOCIDO' if ok else 'NO reconocido'}")
        print("Consejo: pide a alguien más que pruebe. Si su similitud supera el umbral,")
        print("sube JARVIS_VOICE_THRESHOLD en .env (por ejemplo a 0.80).")


if __name__ == "__main__":
    main()
