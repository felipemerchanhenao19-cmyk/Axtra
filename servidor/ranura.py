"""Ranura privada de Axtra: el oído, el cerebro y la voz que Axtra le presta a los orbes de los negocios.

Axtra es la tarjeta madre: aquí están todas las claves. Esta app escucha en un puerto interno (8090) que el
túnel de Cloudflare NO publica; solo la alcanza el contenedor de los orbes (apex) dentro del servidor.
Cada respuesta trae lo que costó, para llevar la cuenta por negocio.
"""
import base64
import hmac
import os
import re
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
    """Un restaurante puede tener varios PIN separados por coma (APEX_PIN_DOMICILIOS=3333,2222): sirve cualquiera."""
    valor = os.getenv(f"APEX_PIN_{p.restaurante.upper().replace('-', '_')}", "")
    esperados = [x.strip() for x in valor.split(",") if len(x.strip()) >= 4]
    if not esperados:
        raise HTTPException(503, "este restaurante no tiene PIN configurado")
    return {"ok": any([hmac.compare_digest(p.pin.encode(), e.encode()) for e in esperados])}


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
    # Si el modelo principal rechaza (límite de uso de Groq o falla suelta), se intenta con Whisper turbo: tiene su propio
    # cupo y es más rápido. Sin este respaldo, un límite de Groq deja sordos a todos los orbes.
    modelos = list(dict.fromkeys([config.ORBE_MODELO_OIDO, "whisper-large-v3-turbo"]))
    r, error = None, ""
    for modelo in modelos:
        try:
            r = requests.post(GROQ_OIDO, timeout=20, headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
                              files={"file": (f"voz.{fmt}", audio, oido._MIME[fmt])},
                              data={"model": modelo, "language": idioma[:5], "temperature": "0",
                                    "response_format": "verbose_json", **({"prompt": pista[:600]} if pista else {})})
        except requests.RequestException as e:
            error, r = f"Groq Whisper falló: {e}", None
            continue
        if r.status_code < 400:
            break
        error = f"Groq Whisper falló: {r.status_code} {r.text[:200]} (audio {fmt}, {len(audio)} bytes, empieza {audio[:12].hex()})"
        if r.status_code not in (429, 500, 502, 503, 504):   # el audio está mal: otro modelo no lo arregla
            break
    if r is None or r.status_code >= 400:
        raise HTTPException(502, error)
    d = r.json()
    return {"texto": (d.get("text") or "").strip(), "segundos": float(d.get("duration") or 0), "proveedor": "groq"}


# ---------------- Cerebro: piensa y decide qué herramientas usar ----------------
class Pensar(BaseModel):
    sistema: str = Field(max_length=30000)
    mensajes: list = Field(max_length=60)
    herramientas: list = []
    max_tokens: int = Field(300, le=1500)


# Cada modelo de Groq tiene su propio cupo por minuto y por día. Con un solo modelo, una mesa conversando agota el cupo
# y todos los orbes quedan mudos; con varios, cuando uno se agota responde el siguiente (y después Gemini).
RESPALDOS_GROQ = [m.strip() for m in os.getenv("ORBE_MODELOS_RESPALDO",
                  "openai/gpt-oss-120b,meta-llama/llama-4-scout-17b-16e-instruct").split(",") if m.strip()]
RESPALDOS_GEMINI = [m.strip() for m in os.getenv("GEMINI_MODELOS_RESPALDO", "gemini-flash-lite-latest").split(",") if m.strip()]
_DESCANSO: dict = {}          # modelo → hasta cuándo no pedirle nada (dijo que se le acabó el cupo): así no se pierde tiempo


class Rechazo(RuntimeError):
    def __init__(self, codigo: int, texto: str, espera: float = 0):
        super().__init__(f"{codigo}: {texto[:200]}")
        self.codigo, self.espera = codigo, espera


def _espera(r) -> float:
    """Cuántos segundos pide el proveedor esperar antes de volver a intentar con ese modelo."""
    try:
        return min(3600.0, float((getattr(r, "headers", None) or {}).get("retry-after")))
    except (TypeError, ValueError):
        pass
    texto = r.text or ""
    if m := re.search(r"try again in ([\d.]+)ms", texto):
        return float(m.group(1)) / 1000
    if m := re.search(r"try again in (?:(\d+)h)?(?:(\d+)m(?!s))?([\d.]+)?s?", texto):
        h, mi, se = (float(x) if x else 0 for x in m.groups())
        if h or mi or se:
            return min(3600.0, h * 3600 + mi * 60 + se)
    return 600.0 if "per day" in texto or "TPD" in texto or "RPD" in texto else 20.0


def _chat(url: str, clave: str, modelo: str, p: Pensar, timeout: float = 15) -> dict:
    cuerpo = {"model": modelo, "max_tokens": p.max_tokens + 300, "temperature": 0.4,
              "messages": [{"role": "system", "content": p.sistema}] + p.mensajes}
    if p.herramientas:
        cuerpo["tools"] = p.herramientas
        cuerpo["tool_choice"] = "auto"
    if "gpt-oss" in modelo:
        cuerpo["reasoning_effort"] = "low"
    r = requests.post(url, json=cuerpo, timeout=timeout, headers={"Authorization": f"Bearer {clave}"})
    if r.status_code >= 400:
        raise Rechazo(r.status_code, r.text, _espera(r) if r.status_code == 429 else 0)
    d = r.json()
    m = d["choices"][0]["message"]
    u = d.get("usage") or {}
    return {"mensaje": {"role": "assistant", "content": m.get("content") or "", "tool_calls": m.get("tool_calls") or []},
            "uso": {"entrada": u.get("prompt_tokens", 0), "salida": u.get("completion_tokens", 0),
                    "cache": (u.get("prompt_tokens_details") or {}).get("cached_tokens", 0)}, "modelo": modelo}


def _cerebros() -> list:
    groq = list(dict.fromkeys([config.ORBE_MODELO, *RESPALDOS_GROQ])) if config.GROQ_API_KEY else []
    gemini = list(dict.fromkeys([config.GEMINI_MODELO, *RESPALDOS_GEMINI])) if config.GEMINI_API_KEY else []
    todos = [("groq", GROQ_CHAT, config.GROQ_API_KEY, m) for m in groq] + \
            [("gemini", GEMINI_CHAT, config.GEMINI_API_KEY, m) for m in gemini]
    ahora = time.time()
    listos = [o for o in todos if _DESCANSO.get(o[3], 0) <= ahora]
    return listos or todos                     # si todos descansan, se intenta igual: alguno pudo recuperarse


@app.post("/pensar")
def pensar(p: Pensar):
    errores, t0 = [], time.time()
    for nombre, url, clave, modelo in _cerebros():
        if time.time() - t0 > 20:                      # el cliente ya esperó demasiado: mejor la frase de respaldo
            errores.append("sin tiempo para más respaldos")
            break
        try:
            return {**_chat(url, clave, modelo, p, timeout=15 if not errores else 10), "proveedor": nombre}
        except Rechazo as e:
            errores.append(f"{modelo}: {e}")
            if e.codigo == 429:
                _DESCANSO[modelo] = time.time() + max(2.0, e.espera)
            elif e.codigo in (401, 403, 404):          # modelo retirado o clave sin acceso: no insistir por un rato
                _DESCANSO[modelo] = time.time() + 1800
        except (requests.RequestException, KeyError, IndexError, ValueError) as e:
            errores.append(f"{modelo}: {e}")
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

