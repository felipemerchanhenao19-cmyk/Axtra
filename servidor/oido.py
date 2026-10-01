"""Oído de Axtra: convierte tu voz en texto. Groq Whisper (gratis) y, de respaldo, el reconocedor de Google."""
import io
import wave

import requests

from . import config


# Formatos que manda el celular: WAV (antiguo) o audio comprimido de MediaRecorder
def formato(audio: bytes) -> str:
    if audio[:4] == b"RIFF" and audio[8:12] == b"WAVE":
        return "wav"
    if audio[:4] == b"\x1aE\xdf\xa3":
        return "webm"
    if audio[:4] == b"OggS":
        return "ogg"
    if audio[4:8] == b"ftyp":
        return "mp4"
    return ""


_MIME = {"wav": "audio/wav", "webm": "audio/webm", "ogg": "audio/ogg", "mp4": "audio/mp4"}


def _groq(audio: bytes, idioma: str, fmt: str = "wav") -> str:
    r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", timeout=60,
                      headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
                      files={"file": (f"voz.{fmt}", audio, _MIME[fmt])},
                      data={"model": config.GROQ_MODELO_OIDO, "language": idioma, "temperature": "0",
                            "response_format": "json"})
    r.raise_for_status()
    return (r.json().get("text") or "").strip()


def _google(wav: bytes, idioma_region: str) -> str:
    import speech_recognition as sr

    with wave.open(io.BytesIO(wav)) as w:
        datos = sr.AudioData(w.readframes(w.getnframes()), w.getframerate(), w.getsampwidth())
    try:
        return sr.Recognizer().recognize_google(datos, language=idioma_region).strip()
    except sr.UnknownValueError:
        return ""


def transcribir(audio: bytes, idioma: str = "es", region: str = "es-CO") -> str:
    """audio: WAV mono de 16 bits o audio comprimido del celular (webm/ogg/mp4). idioma: 'es', 'ru', 'en'..."""
    fmt = formato(audio)
    if not fmt:
        raise ValueError("audio dañado o en un formato desconocido")
    if fmt == "wav":
        try:
            with wave.open(io.BytesIO(audio)) as w:
                if w.getsampwidth() != 2 or w.getnchannels() != 1:
                    raise ValueError("el audio debe ser WAV mono de 16 bits")
                if w.getnframes() / w.getframerate() > 120:
                    raise ValueError("audio demasiado largo (máximo 2 minutos)")
        except (wave.Error, EOFError) as e:
            raise ValueError(f"audio dañado ({e})")
    errores = []
    if config.GROQ_API_KEY:
        try:
            return _groq(audio, idioma, fmt)
        except requests.RequestException as e:
            errores.append(f"Groq: {e}")
    if fmt == "wav":                    # el reconocedor de Google de respaldo solo entiende WAV
        try:
            return _google(audio, region)
        except Exception as e:
            errores.append(f"Google: {e}")
    else:
        errores.append("sin Groq no hay respaldo para este formato")
    raise RuntimeError("No pude entender el audio (" + "; ".join(errores) + ")")
