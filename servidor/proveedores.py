"""Los cerebros de Axtra. Todos responden igual: chat(sistema, mensajes, ...) -> Respuesta.

Gratis: Groq (básico e intermedio), Cerebras, Gemini y OpenRouter.
De pago: Claude (barato, normal y fuerte) y Grok (solo si pones XAI_API_KEY).
Si uno falla o se queda sin cuota, se pausa un rato y el enrutador pasa al siguiente.
"""
import re
import time
from dataclasses import dataclass, field

import requests

from . import config, db


class NoDisponible(Exception):
    """El cerebro no puede responder ahora (sin clave, sin cuota, tope de gasto, caído...)."""


@dataclass
class Respuesta:
    texto: str
    cerebro: str            # nombre para mostrar, p. ej. "Groq" o "Claude"
    modelo: str
    usd: float = 0.0
    fuentes: list = field(default_factory=list)


class Proveedor:
    nombre = "cerebro"
    gratis = True
    privado = False         # True = se le pueden enviar datos personales (planes de pago)

    def __init__(self):
        self.pausado_hasta = 0.0

    def configurado(self) -> bool:
        return True

    def disponible(self) -> bool:
        return self.configurado() and time.time() >= self.pausado_hasta

    def pausar(self, segundos: float, motivo: str):
        self.pausado_hasta = time.time() + segundos
        raise NoDisponible(f"{self.nombre}: {motivo}")

    def chat(self, sistema: str, mensajes: list, max_tokens: int = 1500, pensar: bool = False) -> Respuesta:
        raise NotImplementedError


def _texto_msgs(mensajes: list) -> list:
    return [{"role": m["role"], "content": m["content"]} for m in mensajes
            if isinstance(m.get("content"), str) and m["content"].strip()]


# ---------------- Formato OpenAI: Groq, Cerebras, OpenRouter y Grok ----------------
class Compatible(Proveedor):
    url = ""

    def __init__(self, nombre: str, url: str, clave: str, modelo: str, gratis: bool = True):
        super().__init__()
        self.nombre, self.url, self.clave, self.modelo, self.gratis = nombre, url, clave, modelo, gratis
        self.privado = not gratis

    def configurado(self) -> bool:
        return bool(self.clave)

    def _antes(self):
        """Los de pago revisan su tope mensual antes de gastar."""

    def _costo(self, usage: dict) -> float:
        return 0.0

    def chat(self, sistema, mensajes, max_tokens=1500, pensar=False):
        if not self.disponible():
            raise NoDisponible(f"{self.nombre}: no disponible ahora")
        self._antes()
        body = {"model": self.modelo, "max_tokens": max_tokens + (2000 if pensar else 300),
                "messages": [{"role": "system", "content": sistema}] + _texto_msgs(mensajes)}
        if "gpt-oss" in self.modelo:
            body["reasoning_effort"] = "high" if pensar else "low"
        if self.nombre == "OpenRouter":
            body["reasoning"] = {"exclude": True}
        headers = {"Authorization": f"Bearer {self.clave}"}
        if self.nombre == "OpenRouter":
            headers.update({"HTTP-Referer": "https://github.com/felipemerchanhenao19-cmyk/Axtra", "X-Title": "Axtra"})
        for intento in range(2):
            try:
                r = requests.post(self.url, headers=headers, json=body, timeout=90)
            except requests.RequestException as e:
                self.pausar(60, f"sin conexión ({type(e).__name__})")
            if r.status_code == 400 and intento == 0 and ("reasoning" in r.text):
                body.pop("reasoning_effort", None)
                body.pop("reasoning", None)
                continue
            if r.status_code == 429:
                self.pausar(60 if "minute" in r.text.lower() else 3600, "sin cuota por ahora")
            if r.status_code in (401, 402, 403):
                self.pausar(6 * 3600, f"clave inválida o sin saldo ({r.status_code})")
            if r.status_code >= 500:
                self.pausar(120, f"saturado ({r.status_code})")
            if r.status_code >= 400:
                raise NoDisponible(f"{self.nombre}: error {r.status_code}: {r.text[:160]}")
            data = r.json()
            choices = data.get("choices") or []
            texto = ((choices[0].get("message") or {}).get("content") or "") if choices else ""
            texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.S).strip()
            if not texto:
                raise NoDisponible(f"{self.nombre}: respuesta vacía")
            usd = self._costo(data.get("usage") or {})
            return Respuesta(texto, self.nombre, self.modelo, usd)
        raise NoDisponible(f"{self.nombre}: no respondió")


class Grok(Compatible):
    def __init__(self):
        super().__init__("Grok", "https://api.x.ai/v1/chat/completions", config.XAI_API_KEY,
                         config.GROK_MODELO, gratis=False)

    def _antes(self):
        if db.gasto_mes("grok") >= config.TOPE_GROK_USD:
            raise NoDisponible("Grok: llegó al tope de gasto del mes")

    def _costo(self, usage):
        pin, pout = config.PRECIOS.get(self.modelo, (3.0, 15.0))
        usd = (usage.get("prompt_tokens", 0) * pin + usage.get("completion_tokens", 0) * pout) / 1e6
        db.sumar_gasto("grok", usd)
        return usd


# ---------------- Gemini (Google) ----------------
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"


class Gemini(Proveedor):
    nombre = "Gemini"

    def __init__(self):
        super().__init__()
        self.modelo = config.GEMINI_MODELO

    def configurado(self):
        return bool(config.GEMINI_API_KEY)

    def chat(self, sistema, mensajes, max_tokens=1500, pensar=False, buscar=False):
        if not self.disponible():
            raise NoDisponible("Gemini: no disponible ahora")
        contents = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
                    for m in _texto_msgs(mensajes)]
        cfg = {"maxOutputTokens": max_tokens + (2000 if pensar else 200)}
        if not pensar:
            cfg["thinkingConfig"] = {"thinkingBudget": 0}
        body = {"systemInstruction": {"parts": [{"text": sistema}]}, "contents": contents, "generationConfig": cfg}
        if buscar:
            body["tools"] = [{"google_search": {}}]
        try:
            r = requests.post(f"{GEMINI_URL}/models/{config.GEMINI_MODELO}:generateContent",
                              headers={"x-goog-api-key": config.GEMINI_API_KEY}, json=body, timeout=60)
        except requests.RequestException as e:
            self.pausar(60, f"sin conexión ({type(e).__name__})")
        if r.status_code == 429:
            self.pausar(30 * 60, "se acabó la cuota gratis por ahora")
        if r.status_code in (401, 403):
            self.pausar(6 * 3600, "clave inválida")
        if r.status_code >= 500:
            self.pausar(120, f"saturado ({r.status_code})")
        if r.status_code >= 400:
            raise NoDisponible(f"Gemini: error {r.status_code}: {r.text[:160]}")
        cands = r.json().get("candidates") or []
        parts = (cands[0].get("content") or {}).get("parts", []) if cands else []
        texto = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
        if not texto:
            raise NoDisponible("Gemini: respuesta vacía")
        fuentes = []
        if buscar and cands:
            for c in (cands[0].get("groundingMetadata") or {}).get("groundingChunks") or []:
                w = c.get("web") or {}
                if w.get("uri") and w not in fuentes:
                    fuentes.append({"titulo": w.get("title") or w["uri"], "url": w["uri"]})
        return Respuesta(texto, "Gemini", config.GEMINI_MODELO, 0.0, fuentes[:8])


# ---------------- Claude (Anthropic) ----------------
class Claude(Proveedor):
    gratis = False
    privado = True

    def __init__(self, modelo: str, nombre: str = "Claude"):
        super().__init__()
        self.modelo, self.nombre = modelo, nombre
        self._cliente = None

    def configurado(self):
        return bool(config.ANTHROPIC_API_KEY)

    def cliente(self):
        if self._cliente is None:
            import anthropic

            self._cliente = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        return self._cliente

    def chat(self, sistema, mensajes, max_tokens=1500, pensar=False):
        import anthropic

        if not self.disponible():
            raise NoDisponible(f"{self.nombre}: no disponible ahora")
        if db.gasto_mes("claude") >= config.TOPE_CLAUDE_USD:
            raise NoDisponible("Claude: llegó al tope de gasto del mes")
        kwargs = dict(model=self.modelo, max_tokens=16000,
                      system=[{"type": "text", "text": sistema, "cache_control": {"type": "ephemeral"}}],
                      messages=_texto_msgs(mensajes))
        if "haiku" not in self.modelo:
            # Opus 5.5 / Sonnet 5.5: piensan solos (adaptativo); el esfuerzo controla cuánto
            kwargs["output_config"] = {"effort": "high" if pensar else "medium"}
            # Si Claude rechaza algo por seguridad, la API lo reintenta sola con otro modelo de Claude
            kwargs["betas"] = ["server-side-fallback-2026-07-01"]
            kwargs["fallbacks"] = "default"
            llamar = self.cliente().beta.messages.create
        else:
            llamar = self.cliente().messages.create
        try:
            resp = llamar(**kwargs)
        except anthropic.AuthenticationError:
            self.pausar(6 * 3600, "la clave no es válida")
        except anthropic.RateLimitError:
            self.pausar(60, "demasiadas peticiones, espera un momento")
        except anthropic.APIStatusError as e:
            if "credit balance" in str(e).lower():
                self.pausar(30 * 60, "se acabó el saldo de la API")
            self.pausar(120, f"error {e.status_code}")
        except anthropic.APIConnectionError:
            self.pausar(60, "sin conexión")
        usd = self._costo(resp.usage)
        if resp.stop_reason == "refusal":
            raise NoDisponible(f"{self.nombre}: prefirió no responder esto")
        texto = "".join(b.text for b in resp.content if b.type == "text").strip()
        if not texto:
            raise NoDisponible(f"{self.nombre}: respuesta vacía")
        return Respuesta(texto, self.nombre, self.modelo, usd)

    def _costo(self, u) -> float:
        pin, pout = config.PRECIOS.get(self.modelo, (4.0, 20.0))
        entrada = (getattr(u, "input_tokens", 0) or 0) + 1.25 * (getattr(u, "cache_creation_input_tokens", 0) or 0) \
            + 0.1 * (getattr(u, "cache_read_input_tokens", 0) or 0)
        usd = (entrada * pin + (getattr(u, "output_tokens", 0) or 0) * pout) / 1e6
        db.sumar_gasto("claude", usd)
        return usd


# ---------------- Todos los cerebros ----------------
def crear() -> dict:
    groq_url = "https://api.groq.com/openai/v1/chat/completions"
    return {
        "groq": Compatible("Groq", groq_url, config.GROQ_API_KEY, config.GROQ_BASICO),
        "groq_pro": Compatible("Groq", groq_url, config.GROQ_API_KEY, config.GROQ_INTERMEDIO),
        "cerebras": Compatible("Cerebras", "https://api.cerebras.ai/v1/chat/completions",
                               config.CEREBRAS_API_KEY, config.CEREBRAS_MODELO),
        "gemini": Gemini(),
        "openrouter": Compatible("OpenRouter", "https://openrouter.ai/api/v1/chat/completions",
                                 config.OPENROUTER_API_KEY, config.OPENROUTER_MODELO),
        "claude_barato": Claude(config.CLAUDE_BARATO, "Claude Haiku"),
        "claude": Claude(config.CLAUDE_NORMAL, "Claude"),
        "claude_fuerte": Claude(config.CLAUDE_FUERTE, "Claude Opus"),
        "grok": Grok(),
    }
