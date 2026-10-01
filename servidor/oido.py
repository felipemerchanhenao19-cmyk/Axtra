"""Oído de Axtra: convierte tu voz en texto. Groq Whisper (gratis) y, de respaldo, el reconocedor de Google."""
import io
import wave

import requests

from . import config


def _groq(wav: bytes, idioma: str) -> str:
    r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", timeout=60,
                      headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
                      files={"file": ("voz.wav", wav, "audio/wav")},
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


def transcribir(wav: bytes, idioma: str = "es", region: str = "es-CO") -> str:
    """wav: audio WAV mono de 16 bits (así lo manda la app). idioma: 'es', 'ru', 'en'..."""
    try:
        with wave.open(io.BytesIO(wav)) as w:
            if w.getsampwidth() != 2 or w.getnchannels() != 1:
                raise ValueError("el audio debe ser WAV mono de 16 bits")
            if w.getnframes() / w.getframerate() > 120:
                raise ValueError("audio demasiado largo (máximo 2 minutos)")
    except (wave.Error, EOFError) as e:
        raise ValueError(f"audio dañado ({e})")
    errores = []
    if config.GROQ_API_KEY:
        try:
            return _groq(wav, idioma)
        except requests.RequestException as e:
            errores.append(f"Groq: {e}")
    try:
        return _google(wav, region)
    except Exception as e:
        errores.append(f"Google: {e}")
    raise RuntimeError("No pude entender el audio (" + "; ".join(errores) + ")")
