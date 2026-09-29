"""AXTRA - Fase 1. Ejecuta: python axtra.py y di "Axtra"."""
import sys
import time

import config
from audio import beep, record_utterance  # noqa: F401

STOP_PHRASES = ("eso es todo", "gracias axtra", "nada más", "nada mas", "descansa")


def main():
    import llm

    print("Iniciando sistemas...")
    local = llm.local_ok(force=True)
    if not config.ANTHROPIC_API_KEY and not local and not (config.GEMINI_API_KEY or config.GROQ_API_KEY or config.OPENROUTER_API_KEY):
        sys.exit("Falta ANTHROPIC_API_KEY en el archivo .env (o instala el cerebro local: python axtra.py cerebro)")
    import modes

    modo = modes.NAMES[modes.get()] + "  (cámbialo por voz: 'desactiva / activa el cerebro avanzado')"
    print(f"  - Cerebro: {modo}")
    gratis = [n for n, k in (("Gemini", config.GEMINI_API_KEY), ("Groq", config.GROQ_API_KEY),
                              ("OpenRouter", config.OPENROUTER_API_KEY)) if k]
    if gratis:
        print(f"  - Cerebros gratis en la nube: {', '.join(gratis)}")
    print(f"  - Búsqueda gratis: {'Tavily + ' if config.TAVILY_API_KEY else ''}DuckDuckGo")
    if local:
        print(f"  - Cerebro local listo: {config.LOCAL_MODEL}")
        if not (gratis and config.CHAT_BRAIN == "gemini"):
            import threading  # sin Gemini, el local se carga de una vez para responder rápido

            threading.Thread(target=llm.warm_up, daemon=True).start()
    elif config.BRAIN_MODE != "claude":
        print("  ⚠ Cerebro local apagado: abre Ollama o ejecuta 'python axtra.py cerebro'. Mientras tanto todo va por Claude.")
    import socket

    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3).close()
    except OSError:
        print("  ⚠ SIN INTERNET: Axtra arrancará con la voz de Windows y no podrá pensar hasta que vuelva "
              "la conexión. Revisa el Wi-Fi.")
    from brain import Brain
    from speech import STT, TTS
    from wake_es import after_stop, strip_wake

    tts = TTS()
    voice_id = None
    if config.REQUIRE_VOICE_MATCH:
        from voice_id import VoiceID

        voice_id = VoiceID()
        if voice_id.voiceprint is None:
            sys.exit("Primero registra tu voz con: python axtra.py registrar")

    from audio import pick_microphone

    print(f"  - Micrófono: {pick_microphone()}")
    print("  - Cargando oído (Whisper)...")
    stt = STT()
    print("  - Cargando palabra de activación...")
    if config.WAKE_MODE == "en":
        from audio import WakeWordListener

        wake = WakeWordListener()
        wake_label = "Hey Axtra"
    else:
        from wake_es import SpanishWakeListener

        wake = SpanishWakeListener()
        wake_label = "Axtra"
    brain = Brain()
    import autonomy

    autonomy.speaker = tts.say  # para avisos, alertas y recordatorios por su cuenta
    autonomy.start()
    import vision

    vision.watcher.start()
    import companion

    companion.brain = brain
    companion.start()
    if hasattr(wake, "tts"):
        wake.tts = tts  # para que no confunda su propia voz con la tuya

    if config.BARGE_IN and config.WAKE_MODE != "en":
        from wake_es import is_stop

        def interrupt_check(audio):
            text = wake._quick_transcribe(audio)
            return is_stop(text), text

        tts.interrupt_check = interrupt_check
        print("  - Puedes interrumpirlo diciendo: 'Axtra, para' o 'detente'")

    import nucleo
    import sync

    nucleo.ensure_identity()
    try:
        sc = sync.score()
        print(f"  - Sincronización: {sc['total']:.0f}% (nivel {sc['nivel'][1]})")
        extra = f" Sincronización al {sc['total']:.0f} por ciento." if sc["total"] >= 20 else ""
    except Exception as e:
        print(f"  (sincronización: {e})")
        extra = ""
    import escritorio

    escritorio.brain, escritorio.tts, escritorio.stt = brain, tts, stt
    print("  - Escritorio: di 'Axtra, activa escritorio' para escribirle (responde en voz alta)")
    tts.say(f"Sistemas en línea. A su servicio, señor.{extra}")

    while True:
        print(f"\n[Esperando '{wake_label}'...]")
        if config.WAKE_MODE == "en":
            wake.wait()
            rest = ""
            wake_audio = None
        else:
            wake_audio, rest = wake.wait()

        import control_pc
        import media

        media.duck()  # si hay música puesta por Axtra, la pausa mientras hablan

        # Avisos pendientes del modo autónomo (alertas, estudios terminados)
        while not autonomy.notices.empty():
            tts.say("Antes, señor: " + autonomy.notices.get())

        companion.touch()
        from quick import norm

        if companion.take_reply() or len(rest.split()) >= 2 or norm(rest) in control_pc.ONE_WORD:
            # Respuesta a algo que Axtra dijo, o la orden venía en la misma frase: "Axtra, ¿qué hora es?" o "Dame más info, Axtra"
            audio = wake_audio
        else:
            # Solo dijo "Axtra" / "Hola Axtra": responde y espera la orden
            tts.say("¿Sí, señor?", cache=True)
            audio = record_utterance(start_timeout=8)

        retried = False
        verified = False
        answered = False
        # Conversación: tras cada respuesta escucha unos segundos más sin repetir "Axtra"
        while audio is not None:
            # Con el mouse por voz las órdenes son muy cortas ("clic", "cinco"): se verifica la voz
            # una vez por conversación para no rechazarlas por falta de audio
            if voice_id is not None and not (verified and control_pc.recent()):
                ok, score = voice_id.is_owner(audio)
                print(f"  (voz: {score:.2f})")
                if not ok:
                    tts.say("Lo siento, no reconozco su voz. Acceso denegado.")
                    break
                verified = True

            t0 = time.time()
            raw = stt.transcribe(audio)
            print(f"Tú: {raw}   ({time.time() - t0:.1f}s)")
            if any(p in raw.lower() for p in STOP_PHRASES):
                tts.say("A la orden, señor.", cache=True)
                break
            text = strip_wake(raw) if raw else ""
            if not text:
                if retried or answered:   # ruido en la escucha extra: vuelve a esperar sin molestar
                    break
                retried = True
                tts.say("¿Sí, señor?", cache=True)
                audio = record_utterance(start_timeout=8)
                continue

            try:
                answer = brain.ask(text)
            except Exception as e:
                print(f"  Error del cerebro: {e}")
                answer = ("Señor, ningún cerebro está disponible: " + (llm.claude_reason or "revise el internet") +
                          ", y el cerebro local está apagado. Abra Ollama, por favor.")
            if answer == "__APAGAR__":
                tts.say("Desconectando sistemas. Hasta luego, señor.")
                return
            answered = True
            tts.say(answer, interruptible=config.BARGE_IN)

            import dictation
            import language

            import sync
            import voices

            if dictation.pending:
                dictation.run(tts, stt)
                break
            if voices.pending_demo:
                voices.demo(tts)
            if sync.pending:
                sync.run_session(tts, stt)
                break
            import aprendizaje

            if aprendizaje.pending is not None:
                def listen():
                    a = record_utterance(start_timeout=40, max_seconds=90, silence_end=2.0)
                    return stt.transcribe(a) if a is not None else ""
                aprendizaje.run(tts, listen)
                break
            if language.pending:
                language.run(tts, stt)
                break

            if media.playing and not media.paused_by_jarvis:
                break  # acaba de poner música: no escuchar la canción como si fuera una orden

            if tts.last_interrupt:
                int_audio, int_text = tts.last_interrupt
                tts.last_interrupt = None
                if len(after_stop(int_text).split()) >= 2:
                    audio = int_audio  # "Axtra, para, mejor dime el clima"
                else:
                    tts.say("Dígame, señor.", cache=True)
                    audio = record_utterance(start_timeout=8)
                continue

            beep(freq=660, duration=0.1)
            wait = 30 if control_pc.recent() else config.FOLLOW_UP_SECONDS  # modo mouse: escucha más
            print(f"  (te sigo escuchando {wait:.0f} s...)")
            audio = record_utterance(start_timeout=wait, silence_end=0.8 if control_pc.recent() else None)
            if audio is None:
                if control_pc.grid.active:
                    control_pc.grid.hide()
                print("  (en espera: di 'Axtra' para volver a hablar)")

        media.unduck()  # reanuda la música al terminar la conversación
        companion.touch()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAxtra desconectado.")
