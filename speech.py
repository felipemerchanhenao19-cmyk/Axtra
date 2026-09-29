"""Voz a texto (Whisper local, gratis) y texto a voz (edge-tts, gratis)."""
import asyncio
import re
import threading
import time
import uuid

import numpy as np

from config import (DATA_DIR, ELEVENLABS_API_KEY, ELEVENLABS_MODEL, ELEVENLABS_VOICE_ID,
                    SAMPLE_RATE, STT_LANGUAGE, STT_PROVIDER, TTS_PITCH, TTS_PROVIDER, TTS_RATE,
                    TTS_VOICE, WHISPER_MODEL)


class STT:
    """Convierte tu voz en texto. Usa Google (gratis, entiende mejor) y Whisper local de respaldo."""

    def __init__(self, model_size: str = WHISPER_MODEL):
        from faster_whisper import WhisperModel

        # int8 = rápido en procesadores sin tarjeta de video
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.google = None
        if STT_PROVIDER == "google":
            try:
                import speech_recognition as sr

                self.sr = sr
                self.google = sr.Recognizer()
                print("  - Reconocimiento de voz: Google (respaldo: Whisper)")
            except ImportError:
                print("  (Falta SpeechRecognition: uso Whisper. Instala con: "
                      "venv/Scripts/python -m pip install SpeechRecognition)")

    def _google_call(self, fn, timeout: float = 3.5):
        """Corre la llamada a Google con un tope de tiempo: si internet está lento o falla a medias,
        no nos quedamos esperando varios segundos — pasamos a Whisper (local) enseguida."""
        import queue
        import threading

        q = queue.Queue(maxsize=1)

        def _worker():
            try:
                q.put(("ok", fn()))
            except Exception as e:
                q.put(("err", e))

        threading.Thread(target=_worker, daemon=True).start()
        try:
            kind, val = q.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError("Google tardó demasiado")
        if kind == "err":
            raise val
        return val

    def transcribe(self, audio, language: str = None, min_confidence: float = 0.0) -> str:
        """language: código de Google (es-CO, en-US, fr-FR...). Si la confianza de Google es menor a
        min_confidence, usa Whisper con detección automática de idioma (útil en clases de idiomas)."""
        lang = language or STT_LANGUAGE
        if self.google is not None:
            try:
                pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes()
                data = self.sr.AudioData(pcm, SAMPLE_RATE, 2)
                if min_confidence <= 0:
                    return self._google_call(lambda: self.google.recognize_google(data, language=lang)).strip()
                res = self._google_call(lambda: self.google.recognize_google(data, language=lang, show_all=True))
                alts = res.get("alternative", []) if isinstance(res, dict) else []
                if alts and alts[0].get("confidence", 1.0) >= min_confidence:
                    return alts[0]["transcript"].strip()
                return self._whisper(audio, None)
            except self.sr.UnknownValueError:
                return "" if min_confidence <= 0 else self._whisper(audio, None)
            except Exception as e:
                print(f"  (Google no respondió a tiempo, uso Whisper: {e})")
        return self._whisper(audio, lang.split("-")[0] if language else "es")

    def _whisper(self, audio, language="es") -> str:
        segments, _ = self.model.transcribe(
            audio, language=language, beam_size=1, vad_filter=True,
            condition_on_previous_text=False,
            initial_prompt="Conversación con Axtra, el asistente de Felipe." if language == "es" else None,
        )
        return join_segments(segments)


def join_segments(segments) -> str:
    """Une el texto y descarta lo que Whisper "inventa" cuando solo hay ruido."""
    parts = [s.text.strip() for s in segments
             if s.no_speech_prob < 0.6 and s.avg_logprob > -1.0]
    text = " ".join(parts).strip()
    words = text.lower().split()
    if len(words) >= 4 and len(set(words)) <= 2:  # "y y y y y"
        return ""
    return text


def clean_for_speech(text: str) -> str:
    """Quita símbolos de formato que sonarían raro en voz y lee bien porcentajes y dólares."""
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"(\d)\s*%", r"\1 por ciento", text)
    text = re.sub(r"(?:US\$|USD\s?)\s*(\d[\d.,]*)", r"\1 dólares", text)
    text = re.sub(r"[*#_`>|]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class TTS:
    def __init__(self, voice: str = TTS_VOICE, rate: str = TTS_RATE):
        import pygame

        pygame.mixer.init()
        self.pygame = pygame
        self.voice = voice
        self.rate = rate
        self.provider = TTS_PROVIDER
        self.lock = threading.RLock()     # evita que dos voces hablen a la vez
        self.interrupt_check = None       # función(audio) -> (bool, texto); la pone main.py
        self.last_interrupt = None        # (audio, texto) si Felipe interrumpió
        self.voice_override = None        # (voz, velocidad, tono) temporal, p. ej. en clases de inglés
        self.speaking = False             # True mientras suena la voz de Axtra
        self.last_end = 0.0               # cuándo terminó de hablar (para no escucharse a sí mismo)
        if self.provider == "elevenlabs":
            if not (ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID):
                print("  (Falta ELEVENLABS_API_KEY o ELEVENLABS_VOICE_ID: uso la voz gratis)")
                self.provider = "edge"
            else:
                self.voice = "eleven:" + ELEVENLABS_VOICE_ID
                print("  - Voz clonada: ElevenLabs")

    async def _synth_edge(self, text: str, path: str) -> None:
        import edge_tts

        import voices

        voice, rate, pitch = self.voice_override or getattr(self, "preview", None) or voices.current()
        try:
            await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(path)
        except Exception:
            if not self.voice_override:
                raise
            # si la voz del idioma no existe, usa la multilingüe (habla casi todos los idiomas)
            await edge_tts.Communicate(text, "en-US-AndrewMultilingualNeural", rate=rate).save(path)

    def _synth_eleven(self, text: str, path: str) -> None:
        import requests

        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
            params={"output_format": "mp3_44100_128"},
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={
                "text": text,
                "model_id": ELEVENLABS_MODEL,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
                **({"language_code": "es"} if "2_5" in ELEVENLABS_MODEL else {}),
            },
            timeout=30,
        )
        if r.status_code != 200:
            raise RuntimeError(f"ElevenLabs {r.status_code}: {r.text[:200]}")
        with open(path, "wb") as f:
            f.write(r.content)

    def _synth(self, text: str, path: str) -> None:
        if self.provider == "elevenlabs" and not self.voice_override:
            try:
                return self._synth_eleven(text, path)
            except Exception as e:
                print(f"  (voz clonada falló, uso la gratis: {e})")
        asyncio.run(self._synth_edge(text, path))

    def _play(self, path, interruptible: bool = False) -> None:
        import ondas

        self.speaking = True
        prev = ondas._state["estado"]
        ondas.set_state("hablando")
        try:
            self._play_inner(path, interruptible)
        finally:
            self.speaking = False
            self.last_end = time.time()
            ondas.set_state("reposo" if prev == "hablando" else prev)

    def _play_inner(self, path, interruptible: bool = False) -> None:
        music = self.pygame.mixer.music
        music.load(str(path))
        music.play()
        stop = threading.Event()
        if interruptible and self.interrupt_check:
            threading.Thread(target=self._listen_for_interrupt, args=(stop,), daemon=True).start()
        while music.get_busy():
            if self.last_interrupt:
                music.stop()
                print("  (interrumpido)")
                break
            time.sleep(0.05)
        stop.set()
        music.unload()

    def _listen_for_interrupt(self, stop: threading.Event) -> None:
        from audio import record_utterance

        while not stop.is_set():
            audio = record_utterance(start_timeout=0.6, max_seconds=6, silence_end=0.6)
            if audio is None or stop.is_set():
                continue
            try:
                hit, text = self.interrupt_check(audio)
            except Exception:
                continue
            if hit and not stop.is_set():
                self.last_interrupt = (audio, text)
                return

    def _prepare(self, text: str, path: str):
        """Sintetiza y, si está activo, aplica el filtro Axtra. Devuelve la ruta a reproducir."""
        import voices

        self._synth(text, path)
        if not self.voice_override and self.provider != "elevenlabs" and voices.filter_on():
            return voices.apply_filter(path) or path
        return path

    def say(self, text: str, cache: bool = False, interruptible: bool = True) -> None:
        """Habla. cache=True guarda frases repetidas; interruptible=False evita que Felipe lo corte
        (úsalo solo para avisos cortos que no deben cortarse a medias). Por defecto TODO es
        interrumpible diciendo "Axtra, para" — así el Protocolo, las clases, el escritorio y
        cualquier "guion" largo dejan de hablar apenas se lo pidas, no solo la charla normal.
        Las respuestas largas se dicen por frases: empieza a hablar mientras prepara el resto."""
        import voices

        text = clean_for_speech(text)
        if not text:
            return
        with self.lock:
            self.last_interrupt = None
            print(f"Axtra: {text}")
            try:
                import volume

                volume.ensure_audible()   # nunca hablar con el PC silenciado o en volumen 0
            except Exception:
                pass
            try:
                if cache:
                    key = f"{voices.current()}|{voices.filter_on()}|{self.voice_override}|{text}"
                    base = DATA_DIR / f"cache_{uuid.uuid5(uuid.NAMESPACE_URL, key).hex}"
                    play = next((p for p in (base.with_name(base.name + ".mp3_fx.wav"),
                                             base.with_name(base.name + "_fx.wav"), base.with_suffix(".mp3"))
                                 if p.exists()), None)
                    if play is None:
                        try:
                            play = self._prepare(text, str(base.with_suffix(".mp3")))
                        except Exception:
                            base.with_suffix(".mp3").unlink(missing_ok=True)
                            raise
                    self._play(play)
                    return
                chunks = split_sentences(text)
                if len(chunks) == 1:
                    path = DATA_DIR / f"tts_{uuid.uuid4().hex}.mp3"
                    try:
                        play = self._prepare(text, str(path))
                        self._play(play, interruptible)
                    finally:
                        _cleanup(path)
                    return
                self._say_chunks(chunks, interruptible)
            except Exception as e:
                # Sin internet (o falla la voz en línea): usa la voz de Windows, que funciona sin conexión
                print(f"  (voz en línea no disponible: {str(e)[:80]}; uso la voz de Windows)")
                self._offline_say(text)

    def _say_chunks(self, chunks, interruptible: bool) -> None:
        """Prepara la frase siguiente mientras suena la actual (responde más rápido)."""
        import queue

        q = queue.Queue(maxsize=2)
        err = []

        def producer():
            for c in chunks:
                if self.last_interrupt:
                    break
                path = DATA_DIR / f"tts_{uuid.uuid4().hex}.mp3"
                try:
                    q.put((path, self._prepare(c, str(path))))
                except Exception as e:
                    err.append(e)
                    _cleanup(path)
                    break
            q.put(None)

        threading.Thread(target=producer, daemon=True).start()
        played = 0
        while True:
            item = q.get()
            if item is None:
                break
            path, play = item
            try:
                if not self.last_interrupt:
                    self._play(play, interruptible)
                    played += 1
            finally:
                _cleanup(path)
        if err and played == 0:
            raise err[0]


    def _offline_say(self, text: str) -> None:
        try:
            if not hasattr(self, "_sapi"):
                import pyttsx3

                self._sapi = pyttsx3.init()
                for v in self._sapi.getProperty("voices"):
                    if "spanish" in v.name.lower() or "es-" in v.id.lower() or "español" in v.name.lower():
                        self._sapi.setProperty("voice", v.id)
                        break
                self._sapi.setProperty("rate", 175)
            self.speaking = True
            self._sapi.say(text)
            self._sapi.runAndWait()
        except Exception as e:
            print(f"  (tampoco pude usar la voz de Windows: {e})")
        finally:
            self.speaking = False
            self.last_end = time.time()


def split_sentences(text: str, target: int = 180):
    """Divide en bloques de frases completas de ~180 letras (el primero corto, para empezar rápido)."""
    parts = re.split(r"(?<=[.!?¿¡;:])\s+", text)
    out, cur = [], ""
    for p in parts:
        limit = 90 if not out else target
        if cur and len(cur) + len(p) > limit:
            out.append(cur.strip())
            cur = p
        else:
            cur = (cur + " " + p).strip()
    if cur:
        out.append(cur.strip())
    return out or [text]


def _cleanup(path) -> None:
    from pathlib import Path

    p = Path(path)
    for f in (p, p.with_name(p.name.rsplit(".", 1)[0] + "_fx.wav")):
        try:
            f.unlink(missing_ok=True)
        except Exception:
            pass
