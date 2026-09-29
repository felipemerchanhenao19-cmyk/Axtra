"""Palabra de activación en ESPAÑOL: basta con decir "Axtra".

Escucha cada frase que se dice en la habitación, la transcribe con un Whisper
pequeño y rápido, y se activa si oye "Axtra" (acepta variantes como
"Astra", "Extra", "Aztra"). Si dices todo seguido, por ejemplo
"Axtra, ¿qué hora es?", la pregunta se procesa de una vez.
"""
import difflib
import re
import time
import unicodedata

from audio import record_utterance
from config import END_PAUSE, SAMPLE_RATE, WAKE_MODEL

WAKE = "axtra"
GREETINGS = {"", "jola", "oje", "jey", "ey", "vuenas", "vuenos", "vuenosdias", "que", "si", "ola"}


def _norm(word: str) -> str:
    """Quita tildes y deja solo letras. "Axtra" no tiene una consonante inicial ambigua como tenía
    "Jarvis" (h/y/g/x/d...), así que aquí no hace falta doblar sonidos — la similitud difusa de abajo
    ya cubre variantes como "astra", "extra" o "aztra"."""
    w = unicodedata.normalize("NFD", word.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z]", "", w)


def _similar(a: str, b: str = WAKE) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def find_wake(text: str):
    """Devuelve (posición, cantidad_de_palabras) de "Axtra" en el texto, o None."""
    words = text.split()
    # 1) Primero busca "Axtra" como una sola palabra
    for i, w in enumerate(words):
        n = _norm(w)
        if n == "extra":
            continue  # palabra real y común en español; sola no activa (ver el punto 3: sí cuenta tras un saludo)
        if len(n) >= 4 and _similar(n) >= 0.70:
            return i, 1
    # 2) Luego como dos palabras cortas pegadas: "ax tra"
    for i in range(len(words) - 1):
        a, b = _norm(words[i]), _norm(words[i + 1])
        if len(a) <= 4 and len(b) <= 4 and len(a + b) >= 5 and _similar(a + b) >= 0.75:
            return i, 2
    # 3) Después de un saludo ("hola", "oye"...) acepta lo que Whisper/Google suelen oír en vez de "Axtra"
    for i in range(len(words) - 1):
        a, b = _plain(words[i]), _plain(words[i + 1])
        if a in ("hola", "ola", "oye", "hey", "ok", "okey", "okay", "buenas", "buenos") and b in LOOSE:
            return i + 1, 1
    return None


def _plain(w: str) -> str:
    w = unicodedata.normalize("NFD", w.lower())
    return "".join(c for c in w if unicodedata.category(c) != "Mn").strip(",.!¡?¿;:")


# Palabras que se confunden con "Axtra" (solo cuentan justo después de un saludo).
# "asta"/"autra" quedan fuera a propósito: se parecen demasiado a "hasta"/"otra" sin la "h" o la "o"
# (muy comunes en frases normales) y activarían a Axtra por accidente.
LOOSE = {"extra", "astra", "aztra", "actra", "ashtra", "achtra", "abstracta", "hastra", "abstra",
         "alstra", "actrra", "aztera", "axtera"}


def strip_wake(text: str) -> str:
    """Quita la palabra "Axtra" (y un saludo antes): "Hola Axtra, ¿qué hora es?" -> "¿qué hora es?"."""
    found = find_wake(text)
    if not found:
        return text.strip()
    i, n = found
    words = text.split()
    before, after = words[:i], words[i + n:]
    if _norm("".join(before)) in GREETINGS or (len(before) == 1 and _plain(before[0]) in
                                               ("hola", "ola", "oye", "hey", "ok", "okey", "okay", "buenas")):
        before = []
    return " ".join(before + after).strip(" ,.;:")


STOP_WORDS = {"detente", "basta", "silencio", "callate", "stop", "suficiente"}


def is_stop(text: str) -> bool:
    """¿Felipe quiere interrumpir? ("Axtra, para", "detente", "basta", "cállate")."""
    words = [_norm(w) for w in text.split()]
    plain = {re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", w.lower())) for w in text.split()}
    return bool(find_wake(text)) or bool(plain & STOP_WORDS) or "parapara" in "".join(words)


def after_stop(text: str) -> str:
    """Lo que Felipe dijo además de interrumpir: "Axtra, para, mejor dime el clima" -> "mejor dime el clima"."""
    rest = strip_wake(text)
    words = [w for w in rest.split()
             if re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", w.lower())) not in STOP_WORDS | {"para", "ya", "espera"}]
    return " ".join(words).strip(" ,.;:")


class SpanishWakeListener:
    tts = None  # main.py lo conecta para ignorar la propia voz de Axtra

    def __init__(self, model_size: str = WAKE_MODEL):
        from faster_whisper import WhisperModel

        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def _quick_transcribe(self, audio) -> str:
        opts = dict(language="es", beam_size=1, condition_on_previous_text=False,
                    vad_filter=True,
                    initial_prompt="Axtra, el asistente. Hola Axtra.")
        try:
            segments, _ = self.model.transcribe(audio, hotwords="Axtra", **opts)
        except TypeError:  # versiones viejas de faster-whisper sin "hotwords"
            segments, _ = self.model.transcribe(audio, **opts)
        from speech import join_segments

        return join_segments(segments)

    def wait(self):
        """Espera hasta oír "Axtra". Devuelve (audio, resto_del_texto)."""
        while True:
            audio = record_utterance(start_timeout=None, max_seconds=25, silence_end=END_PAUSE * 0.8)
            if audio is None or len(audio) < SAMPLE_RATE * 0.4:
                continue
            started = time.time() - len(audio) / SAMPLE_RATE
            if self.tts and (self.tts.speaking or started < self.tts.last_end + 0.3):
                continue  # era la voz de Axtra, no la tuya
            text = self._quick_transcribe(audio)
            if not text:
                continue
            print(f"  (oí: {text})")
            import companion

            if companion.invited():
                # Axtra te acaba de hablar: puedes responderle sin decir "Axtra"
                companion.close_invite(replied=True)
                print(f"  (respuesta a Axtra: \"{text}\")")
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
