"""JARVIS - Fase 1. Ejecuta: python jarvis.py y di "Jarvis"."""
import sys
import time

import config
from audio import beep, record_utterance  # noqa: F401

STOP_PHRASES = ("eso es todo", "gracias jarvis", "nada más", "nada mas", "descansa")


def main():
    import llm

    print("Iniciando sistemas...")
    local = llm.local_ok(force=True)
    if not config.ANTHROPIC_API_KEY and not local:
        sys.exit("Falta ANTHROPIC_API_KEY en el archivo .env (o instala el cerebro local: python jarvis.py cerebro)")
    modo = {"hibrido": "híbrido (órdenes directas + cerebro local + Claude para lo difícil)",
            "local": "solo local (no gasta saldo)", "claude": "solo Claude"}.get(config.BRAIN_MODE, config.BRAIN_MODE)
    print(f"  - Cerebro: {modo}")
    if local:
        print(f"  - Cerebro local listo: {config.LOCAL_MODEL}")
        import threading

        threading.Thread(target=llm.warm_up, daemon=True).start()
    elif config.BRAIN_MODE != "claude":
        print("  ⚠ Cerebro local apagado: abre Ollama o ejecuta 'python jarvis.py cerebro'. Mientras tanto todo va por Claude.")
    import socket

    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3).close()
    except OSError:
        print("  ⚠ SIN INTERNET: Jarvis arrancará con la voz de Windows y no podrá pensar hasta que vuelva "
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
            sys.exit("Primero registra tu voz con: python jarvis.py registrar")

    print("  - Cargando oído (Whisper)...")
    stt = STT()
    print("  - Cargando palabra de activación...")
    if config.WAKE_MODE == "en":
        from audio import WakeWordListener

        wake = WakeWordListener()
        wake_label = "Hey Jarvis"
    else:
        from wake_es import SpanishWakeListener

        wake = SpanishWakeListener()
        wake_label = "Jarvis"
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
        print("  - Puedes interrumpirlo diciendo: 'Jarvis, para' o 'detente'")

    tts.say(f"Sistemas en línea. A su servicio, {config.USER_NAME}.")

    while True:
        print(f"\n[Esperando '{wake_label}'...]")
        if config.WAKE_MODE == "en":
            wake.wait()
            rest = ""
            wake_audio = None
        else:
            wake_audio, rest = wake.wait()

        import media

        media.duck()  # si hay música puesta por Jarvis, la pausa mientras hablan

        # Avisos pendientes del modo autónomo (alertas, estudios terminados)
        while not autonomy.notices.empty():
            tts.say("Antes, señor: " + autonomy.notices.get())

        companion.touch()
        if companion.take_reply() or len(rest.split()) >= 2:
            # Respuesta a algo que Jarvis dijo, o la orden venía en la misma frase: "Jarvis, ¿qué hora es?" o "Dame más info, Jarvis"
            audio = wake_audio
        else:
            # Solo dijo "Jarvis" / "Hola Jarvis": responde y espera la orden
            tts.say("¿Sí, señor?", cache=True)
            audio = record_utterance(start_timeout=8)

        retried = False
        # Conversación: tras cada respuesta escucha unos segundos más sin repetir "Jarvis"
        while audio is not None:
            if voice_id is not None:
                ok, score = voice_id.is_owner(audio)
                print(f"  (voz: {score:.2f})")
                if not ok:
                    tts.say("Lo siento, no reconozco su voz. Acceso denegado.")
                    break

            t0 = time.time()
            raw = stt.transcribe(audio)
            print(f"Tú: {raw}   ({time.time() - t0:.1f}s)")
            if any(p in raw.lower() for p in STOP_PHRASES):
                tts.say("A la orden, señor.", cache=True)
                break
            text = strip_wake(raw) if raw else ""
            if not text:
                if retried:
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
            tts.say(answer, interruptible=config.BARGE_IN)

            import dictation
            import language

            if dictation.pending:
                dictation.run(tts, stt)
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
                    audio = int_audio  # "Jarvis, para, mejor dime el clima"
                else:
                    tts.say("Dígame, señor.", cache=True)
                    audio = record_utterance(start_timeout=8)
                continue

            beep(freq=660, duration=0.1)
            print(f"  (te sigo escuchando {config.FOLLOW_UP_SECONDS:.0f} s...)")
            audio = record_utterance(start_timeout=config.FOLLOW_UP_SECONDS)
            if audio is None:
                print("  (en espera: di 'Jarvis' para volver a hablar)")

        media.unduck()  # reanuda la música al terminar la conversación
        companion.touch()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nJarvis desconectado.")
