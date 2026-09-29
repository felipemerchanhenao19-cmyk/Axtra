"""Palabra de activación en ESPAÑOL: basta con decir "Jarvis".

Escucha cada frase que se dice en la habitación, la transcribe con un Whisper
pequeño y rápido, y se activa si oye "Jarvis" (acepta variantes como
"Yarvis", "Jarbis", "Harvis"). Si dices todo seguido, por ejemplo
"Jarvis, ¿qué hora es?", la pregunta se procesa de una vez.
"""
import difflib
import re
import time
import unicodedata

from audio import record_utterance
from config import END_PAUSE, SAMPLE_RATE, WAKE_MODEL

WAKE = "jarvis"
GREETINGS = {"", "jola", "oje", "jey", "ey", "vuenas", "vuenos", "vuenosdias", "que", "si", "ola"}


def _norm(word: str) -> str:
    w = unicodedata.normalize("NFD", word.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    w = re.sub(r"[^a-z]", "", w).replace("b", "v")
    for prefix in ("ll", "ch", "sh", "y", "h", "g", "x", "d"):
        if w.startswith(prefix):
            w = "j" + w[len(prefix):]
            break
    return w


def _similar(a: str, b: str = WAKE) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def find_wake(text: str):
    """Devuelve (posición, cantidad_de_palabras) de "Jarvis" en el texto, o None."""
    words = text.split()
    # 1) Primero busca "Jarvis" como una sola palabra
    for i, w in enumerate(words):
        n = _norm(w)
        if len(n) >= 4 and _similar(n) >= 0.75:
            return i, 1
    # 2) Luego como dos palabras cortas pegadas: "jar vis"
    for i in range(len(words) - 1):
        a, b = _norm(words[i]), _norm(words[i + 1])
        if len(a) <= 4 and len(b) <= 4 and len(a + b) >= 5 and _similar(a + b) >= 0.85:
            return i, 2
    return None


def strip_wake(text: str) -> str:
    """Quita la palabra "Jarvis" (y un saludo antes): "Hola Jarvis, ¿qué hora es?" -> "¿qué hora es?"."""
    found = find_wake(text)
    if not found:
        return text.strip()
    i, n = found
    words = text.split()
    before, after = words[:i], words[i + n:]
    if _norm("".join(before)) in GREETINGS:
        before = []
    return " ".join(before + after).strip(" ,.;:")


STOP_WORDS = {"detente", "basta", "silencio", "callate", "stop", "suficiente"}


def is_stop(text: str) -> bool:
    """¿Felipe quiere interrumpir? ("Jarvis, para", "detente", "basta", "cállate")."""
    words = [_norm(w) for w in text.split()]
    plain = {re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", w.lower())) for w in text.split()}
    return bool(find_wake(text)) or bool(plain & STOP_WORDS) or "parapara" in "".join(words)


def after_stop(text: str) -> str:
    """Lo que Felipe dijo además de interrumpir: "Jarvis, para, mejor dime el clima" -> "mejor dime el clima"."""
    rest = strip_wake(text)
    words = [w for w in rest.split()
             if re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", w.lower())) not in STOP_WORDS | {"para", "ya", "espera"}]
    return " ".join(words).strip(" ,.;:")


class SpanishWakeListener:
    tts = None  # main.py lo conecta para ignorar la propia voz de Jarvis

    def __init__(self, model_size: str = WAKE_MODEL):
        from faster_whisper import WhisperModel

        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def _quick_transcribe(self, audio) -> str:
        opts = dict(language="es", beam_size=1, condition_on_previous_text=False,
                    vad_filter=True,
                    initial_prompt="Jarvis, el asistente. Hola Jarvis.")
        try:
            segments, _ = self.model.transcribe(audio, hotwords="Jarvis", **opts)
        except TypeError:  # versiones viejas de faster-whisper sin "hotwords"
            segments, _ = self.model.transcribe(audio, **opts)
        from speech import join_segments

        return join_segments(segments)

    def wait(self):
        """Espera hasta oír "Jarvis". Devuelve (audio, resto_del_texto)."""
        while True:
            audio = record_utterance(start_timeout=None, max_seconds=25, silence_end=END_PAUSE * 0.8)
            if audio is None or len(audio) < SAMPLE_RATE * 0.4:
                continue
            started = time.time() - len(audio) / SAMPLE_RATE
            if self.tts and (self.tts.speaking or started < self.tts.last_end + 0.3):
                continue  # era la voz de Jarvis, no la tuya
            text = self._quick_transcribe(audio)
            if not text:
                continue
            print(f"  (oí: {text})")
            import companion

            if companion.invited():
                # Jarvis te acaba de hablar: puedes responderle sin decir "Jarvis"
                companion.close_invite(replied=True)
                print(f"  (respuesta a Jarvis: \"{text}\")")
                return audio, text
            found = find_wake(text)
            if found:
                i, n = found
                words = text.split()
                rest = " ".join(words[:i] + words[i + n:]).strip(" ,.;:¡!¿?")
                if _norm(rest) in GREETINGS:
                    rest = ""
                print(f"  (activado: \"{text}\")")
                return audio, rest
