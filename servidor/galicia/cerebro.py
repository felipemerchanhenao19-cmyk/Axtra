"""El cerebro de Galicia: Groq (texto, visión y oído). Si un modelo se queda sin cupo, responde el siguiente."""
import base64
import json
import re
import time

import requests

from . import config

CHAT = "https://api.groq.com/openai/v1/chat/completions"
OIDO = "https://api.groq.com/openai/v1/audio/transcriptions"
_DESCANSO: dict = {}          # modelo → hasta cuándo no pedirle nada


class SinCerebro(RuntimeError):
    """Ningún modelo pudo responder (sin internet, sin clave o sin cupo)."""


def disponible() -> bool:
    return bool(config.GROQ_API_KEY)


def _espera(r) -> float:
    try:
        return min(3600.0, float(r.headers.get("retry-after")))
    except (TypeError, ValueError):
        pass
    if m := re.search(r"try again in ([\d.]+)s", r.text or ""):
        return min(3600.0, float(m.group(1)))
    return 600.0 if "per day" in (r.text or "") else 20.0


def _pedir(modelos: list, cuerpo: dict, timeout: float = 60) -> dict:
    if not config.GROQ_API_KEY:
        raise SinCerebro("falta GROQ_API_KEY en el .env del servidor")
    errores = []
    ahora = time.time()
    orden = [m for m in modelos if _DESCANSO.get(m, 0) <= ahora] or modelos
    for modelo in orden:
        body = {**cuerpo, "model": modelo}
        if "gpt-oss" in modelo:
            body["reasoning_effort"] = "medium" if body.get("tools") else "low"
        try:
            r = requests.post(CHAT, json=body, timeout=timeout, headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"})
        except requests.RequestException as e:
            errores.append(f"{modelo}: sin conexión ({type(e).__name__})")
            continue
        if r.status_code == 429:
            _DESCANSO[modelo] = time.time() + _espera(r)
        elif r.status_code in (401, 403, 404):
            _DESCANSO[modelo] = time.time() + 1800
        if r.status_code >= 400:
            errores.append(f"{modelo}: {r.status_code} {r.text[:160]}")
            if r.status_code == 400 and "json" in r.text.lower() and body.get("response_format"):
                body.pop("response_format")          # algunos modelos no aceptan el modo JSON: reintentar sin él
                try:
                    r = requests.post(CHAT, json=body, timeout=timeout,
                                      headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"})
                    if r.status_code < 400:
                        return r.json()["choices"][0]["message"]
                except requests.RequestException:
                    pass
            continue
        try:
            return r.json()["choices"][0]["message"]
        except (ValueError, KeyError, IndexError) as e:
            errores.append(f"{modelo}: respuesta rara ({e})")
    raise SinCerebro("; ".join(errores) or "sin modelos")


def chat(mensajes: list, herramientas: list = None, max_tokens: int = 1200) -> dict:
    """Conversación con herramientas. Devuelve el mensaje del asistente (content y tool_calls)."""
    cuerpo = {"messages": mensajes, "max_tokens": max_tokens, "temperature": 0.2}
    if herramientas:
        cuerpo["tools"] = herramientas
        cuerpo["tool_choice"] = "auto"
    m = _pedir(config.MODELOS_TEXTO, cuerpo)
    return {"role": "assistant", "content": m.get("content") or "", "tool_calls": m.get("tool_calls") or []}


def _json(texto: str) -> dict:
    texto = re.sub(r"<think>.*?</think>", "", texto or "", flags=re.S).strip()
    if m := re.search(r"\{.*\}", texto, flags=re.S):
        texto = m.group(0)
    try:
        return json.loads(texto)
    except ValueError:
        raise SinCerebro("la IA no devolvió datos legibles")


def extraer_texto(instrucciones: str, contenido: str, max_tokens: int = 3000) -> dict:
    """Saca datos estructurados (JSON) de un texto: un extracto, una factura en PDF..."""
    m = _pedir(config.MODELOS_TEXTO, {
        "messages": [{"role": "system", "content": instrucciones}, {"role": "user", "content": contenido[:60000]}],
        "max_tokens": max_tokens, "temperature": 0, "response_format": {"type": "json_object"}}, timeout=120)
    return _json(m.get("content"))


def extraer_imagen(instrucciones: str, imagen: bytes, mime: str = "image/jpeg") -> dict:
    """Lee una foto (factura, recibo, extracto) y devuelve los datos en JSON."""
    url = f"data:{mime};base64,{base64.b64encode(imagen).decode()}"
    m = _pedir(config.MODELOS_VISION, {
        "messages": [{"role": "user", "content": [{"type": "text", "text": instrucciones},
                                                  {"type": "image_url", "image_url": {"url": url}}]}],
        "max_tokens": 2500, "temperature": 0, "response_format": {"type": "json_object"}}, timeout=90)
    return _json(m.get("content"))


def transcribir(audio: bytes, nombre: str = "voz.ogg") -> str:
    """Nota de voz → texto (Groq Whisper)."""
    if not config.GROQ_API_KEY:
        raise SinCerebro("falta GROQ_API_KEY")
    try:
        r = requests.post(OIDO, timeout=60, headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
                          files={"file": (nombre, audio, "audio/ogg")},
                          data={"model": config.MODELO_OIDO, "language": "es", "temperature": "0",
                                "prompt": "Hacienda, papa, bultos, ganado, leche, litros, tarjeta, Bancolombia, Banco Agrario, cuota, factura."})
    except requests.RequestException as e:
        raise SinCerebro(f"sin conexión ({type(e).__name__})")
    if r.status_code >= 400:
        raise SinCerebro(f"Whisper: {r.status_code} {r.text[:160]}")
    return (r.json().get("text") or "").strip()
