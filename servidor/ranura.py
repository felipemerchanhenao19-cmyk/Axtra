"""Ranura privada de Axtra: el oído, el cerebro y la voz que Axtra le presta a los orbes de los negocios.

Axtra es la tarjeta madre: aquí están todas las claves. Esta app escucha en un puerto interno (8090) que el
túnel de Cloudflare NO publica; solo la alcanza el contenedor de los orbes (apex) dentro del servidor.
Cada respuesta trae lo que costó, para llevar la cuenta por negocio.
"""
import base64
import hmac
import os
import time

import requests
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from . import config, oido, voz

app = FastAPI(title="Axtra · ranura", docs_url=None, redoc_url=None, openapi_url=None)
CLAVE = os.getenv("RANURA_CLAVE", "")      # opcional: una contraseña más entre contenedores

GROQ_CHAT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_OIDO = "https://api.groq.com/openai/v1/audio/transcriptions"
GEMINI_CHAT = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GOOGLE_TTS = "https://texttospeech.googleapis.com/v1/text:synthesize"


@app.middleware("http")
async def solo_adentro(request: Request, call_next):
    # Lo que llega por Cloudflare trae cf-ray: aquí nunca debería llegar nada de afuera.
    if request.headers.get("cf-ray") or request.headers.get("cf-connecting-ip"):
        return Response(status_code=404)
    if CLAVE and not hmac.compare_digest(request.headers.get("x-ranura", ""), CLAVE):
        return Response(status_code=401)
    return await call_next(request)


@app.get("/salud")
def salud():
    return {"ok": True, "oido": bool(config.GROQ_API_KEY), "cerebro": bool(config.GROQ_API_KEY or config.GEMINI_API_KEY),
            "voz_google": bool(config.GOOGLE_TTS_API_KEY)}


# ---------------- PIN del panel del mesero (vive en el .env de Axtra: APEX_PIN_<ID>) ----------------
class Pin(BaseModel):
    restaurante: str = Field(max_length=60, pattern=r"^[A-Za-z0-9_-]+$")
    pin: str = Field(max_length=20)


@app.post("/pin")
def verificar_pin(p: Pin):
    esperado = os.getenv(f"APEX_PIN_{p.restaurante.upper().replace('-', '_')}", "")
    if len(esperado) < 4:
        raise HTTPException(503, "este restaurante no tiene PIN configurado")
    return {"ok": hmac.compare_digest(p.pin.encode(), esperado.encode())}


# ---------------- Oído: voz → texto ----------------
@app.post("/oido")
def escuchar(audio: bytes = Body(..., media_type="application/octet-stream"), idioma: str = "es", tipo: str = "",
             pista: str = ""):
    """pista: palabras que probablemente dirá el cliente (los platos del menú). Whisper las reconoce mucho mejor."""
    if len(audio) > 6_000_000:
        raise HTTPException(413, "audio demasiado largo")
    fmt = oido.formato(audio, tipo)
    if not fmt:
        raise HTTPException(422, f"formato de audio desconocido (tipo «{tipo[:60]}», empieza {audio[:16].hex()}, {len(audio)} bytes)")
    if not config.GROQ_API_KEY:
        raise HTTPException(503, "falta GROQ_API_KEY")
    try:
        r = requests.post(GROQ_OIDO, timeout=30, headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
                          files={"file": (f"voz.{fmt}", audio, oido._MIME[fmt])},
                          data={"model": config.ORBE_MODELO_OIDO, "language": idioma[:5], "temperature": "0",
                                "response_format": "verbose_json", **({"prompt": pista[:600]} if pista else {})})
    except requests.RequestException as e:
        raise HTTPException(502, f"Groq Whisper falló: {e}")
    if r.status_code >= 400:          # Groq explica por qué rechazó el audio: se guarda para poder corregirlo
        raise HTTPException(502, f"Groq Whisper falló: {r.status_code} {r.text[:200]} "
                                 f"(audio {fmt}, {len(audio)} bytes, empieza {audio[:12].hex()})")
    d = r.json()
    return {"texto": (d.get("text") or "").strip(), "segundos": float(d.get("duration") or 0), "proveedor": "groq"}


# ---------------- Cerebro: piensa y decide qué herramientas usar ----------------
class Pensar(BaseModel):
    sistema: str = Field(max_length=30000)
    mensajes: list = Field(max_length=60)
    herramientas: list = []
    max_tokens: int = Field(300, le=1500)


def _chat(url: str, clave: str, modelo: str, p: Pensar) -> dict:
    cuerpo = {"model": modelo, "max_tokens": p.max_tokens + 300, "temperature": 0.4,
              "messages": [{"role": "system", "content": p.sistema}] + p.mensajes}
    if p.herramientas:
        cuerpo["tools"] = p.herramientas
        cuerpo["tool_choice"] = "auto"
    if "gpt-oss" in modelo:
        cuerpo["reasoning_effort"] = "low"
    r = requests.post(url, json=cuerpo, timeout=25, headers={"Authorization": f"Bearer {clave}"})
    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    d = r.json()
    m = d["choices"][0]["message"]
    u = d.get("usage") or {}
    return {"mensaje": {"role": "assistant", "content": m.get("content") or "", "tool_calls": m.get("tool_calls") or []},
            "uso": {"entrada": u.get("prompt_tokens", 0), "salida": u.get("completion_tokens", 0)}, "modelo": modelo}


@app.post("/pensar")
def pensar(p: Pensar):
    errores = []
    opciones = [("groq", GROQ_CHAT, config.GROQ_API_KEY, config.ORBE_MODELO),
                ("gemini", GEMINI_CHAT, config.GEMINI_API_KEY, config.GEMINI_MODELO)]
    for nombre, url, clave, modelo in opciones:
        if not clave:
            continue
        for intento in range(2 if nombre == "groq" else 1):     # Groq a veces rechaza una llamada suelta: un reintento
            try:
                return {**_chat(url, clave, modelo, p), "proveedor": nombre}
            except (requests.RequestException, RuntimeError, KeyError, IndexError, ValueError) as e:
                errores.append(f"{nombre}: {e}")
                if intento == 0 and nombre == "groq":
                    time.sleep(0.4)
    raise HTTPException(502, "ningún cerebro respondió (" + "; ".join(errores) + ")")


# ---------------- Voz: texto → audio ----------------
class Hablar(BaseModel):
    texto: str = Field(min_length=1, max_length=1500)
    voz_google: str = "es-US-Neural2-B"
    voz_edge: str = "es-CO-GonzaloNeural"
    velocidad: float = Field(1.0, ge=0.5, le=1.6)
    tono: str = Field("+0Hz", pattern=r"^[+-]\d{1,2}Hz$")      # más agudo = más alegre
    axtra: bool = False          # usar la misma voz de Axtra (la de su .env: VOZ_AXTRA, VOZ_VELOCIDAD y VOZ_TONO)
    idioma: str = Field("", max_length=5)


def _google(h: Hablar) -> bytes:
    idioma = "-".join(h.voz_google.split("-")[:2])
    r = requests.post(GOOGLE_TTS, params={"key": config.GOOGLE_TTS_API_KEY}, timeout=20,
                      json={"input": {"text": h.texto}, "voice": {"languageCode": idioma, "name": h.voz_google},
                            "audioConfig": {"audioEncoding": "MP3", "speakingRate": h.velocidad,
                                            "pitch": round(int(h.tono[:-2]) / 12, 1)}})
    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    return base64.b64decode(r.json()["audioContent"])


@app.post("/voz")
def hablar(h: Hablar):
    texto = voz.limpiar(h.texto)
    if h.axtra:                  # la voz de Axtra: en español la suya; en otro idioma, la voz que Axtra usa en ese idioma
        nativa = next((v[1] for v in voz.IDIOMAS.values() if v[0] == h.idioma), None)
        try:
            audio = voz.sintetizar(texto, voz=nativa or config.VOZ_AXTRA, ritmo=config.VOZ_VELOCIDAD, tono=config.VOZ_TONO)
        except Exception as e:
            raise HTTPException(502, f"no hay voz disponible: {e}")
        return Response(audio, media_type="audio/mpeg", headers={"X-Proveedor": "edge", "X-Caracteres": str(len(texto))})
    if config.GOOGLE_TTS_API_KEY and h.voz_google:          # voz_google vacía = usar directo la voz gratis
        try:
            return Response(_google(h), media_type="audio/mpeg",
                            headers={"X-Proveedor": "google", "X-Caracteres": str(len(texto))})
        except (requests.RequestException, RuntimeError, KeyError, ValueError):
            pass                                    # respaldo: la voz gratis de Axtra
    try:
        audio = voz.sintetizar(texto, voz=h.voz_edge, ritmo=f"{round((h.velocidad - 1) * 100):+d}%", tono=h.tono)
    except Exception as e:
        raise HTTPException(502, f"no hay voz disponible: {e}")
    return Response(audio, media_type="audio/mpeg", headers={"X-Proveedor": "edge", "X-Caracteres": str(len(texto))})

