"""Los dos cerebros de Jarvis y cuándo usar cada uno.

- Cerebro LOCAL: un modelo pequeño que corre en tu PC con Ollama. Gratis, sin internet, más lento
  y menos inteligente. Sirve para charlar, el modo compañero, las clases de idiomas y el briefing.
- Cerebro AVANZADO: Claude (API de Anthropic). Cuesta saldo; se usa para finanzas, búsquedas,
  documentos, cámara, correos y todo lo que necesita herramientas.

Si Claude falla (sin saldo, sin internet o sin clave), Jarvis pasa solo al cerebro local.
"""
import time

import requests

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, LOCAL_MODEL, OLLAMA_URL

_local_cache = {"t": 0.0, "ok": False}
_claude_blocked_until = 0.0
claude_reason = ""          # por qué Claude no está disponible (para avisarle a Felipe)
_client = None


# ---------------- Cerebro local (Ollama) ----------------
def local_ok(force: bool = False) -> bool:
    """¿Está Ollama encendido y con el modelo descargado? (se revisa como mucho cada 30 s)"""
    now = time.time()
    if not force and now - _local_cache["t"] < 30:
        return _local_cache["ok"]
    ok = False
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        names = [m.get("name", "") for m in r.json().get("models", [])]
        ok = any(n in (LOCAL_MODEL, LOCAL_MODEL + ":latest") for n in names)
    except Exception:
        ok = False
    _local_cache.update(t=now, ok=ok)
    return ok


def local_chat(system: str, messages: list, max_tokens: int = 250, temperature: float = 0.7,
               ctx: int = 3072) -> str:
    """Llama al modelo local. messages = [{"role": "user"/"assistant", "content": "texto"}]."""
    msgs = [{"role": "system", "content": system}] + [
        {"role": m["role"], "content": m["content"]} for m in messages if isinstance(m.get("content"), str)]
    r = requests.post(f"{OLLAMA_URL}/api/chat", timeout=180, json={
        "model": LOCAL_MODEL, "messages": msgs, "stream": False, "keep_alive": "30m",
        "options": {"num_predict": max_tokens, "temperature": temperature, "num_ctx": ctx},
    })
    r.raise_for_status()
    import usage

    usage.record_local()
    return r.json().get("message", {}).get("content", "").strip()


def warm_up() -> None:
    """Carga el modelo local en memoria al arrancar (la primera respuesta sale más rápido)."""
    if local_ok(force=True):
        try:
            requests.post(f"{OLLAMA_URL}/api/generate", timeout=120,
                          json={"model": LOCAL_MODEL, "prompt": "", "keep_alive": "30m"})
        except Exception:
            pass


# ---------------- Cerebro avanzado (Claude) ----------------
def client():
    global _client
    if _client is None:
        import anthropic

        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def claude_ok() -> bool:
    return bool(ANTHROPIC_API_KEY) and time.time() >= _claude_blocked_until


def claude_failed(e: Exception) -> str:
    """Anota por qué falló Claude y lo pausa un rato para no insistir. Devuelve el motivo."""
    global _claude_blocked_until, claude_reason
    msg = str(e).lower()
    if "credit balance" in msg or "billing" in msg:
        claude_reason, wait = "se acabó el saldo de la API", 30 * 60
    elif "authentication" in msg or "api key" in msg or "401" in msg:
        claude_reason, wait = "la clave de la API no es válida", 30 * 60
    elif "rate" in msg and "limit" in msg or "overloaded" in msg or "529" in msg:
        claude_reason, wait = "el servicio está saturado", 60
    else:
        claude_reason, wait = "no hay conexión con el cerebro avanzado", 60
    _claude_blocked_until = time.time() + wait
    print(f"  (cerebro avanzado no disponible: {claude_reason}; uso el local)")
    return claude_reason


def claude_text(system, messages: list, max_tokens: int = 500, origen: str = "conversación") -> str:
    import usage

    resp = client().messages.create(model=CLAUDE_MODEL, max_tokens=max_tokens, system=system,
                                    messages=messages)
    usage.record(resp, origen)
    return "".join(b.text for b in resp.content if b.type == "text").strip()


# ---------------- Elegir cerebro ----------------
def ask_text(system: str, messages: list, prefer: str = "local", max_tokens: int = 400,
             origen: str = "conversación", temperature: float = 0.7) -> str:
    """Respuesta de texto simple (sin herramientas). prefer: 'local' o 'claude'.
    Si el preferido no está disponible o falla, usa el otro."""
    order = ["local", "claude"] if prefer == "local" else ["claude", "local"]
    last = None
    for brain in order:
        try:
            if brain == "local" and local_ok():
                return local_chat(system, messages, max_tokens=max_tokens, temperature=temperature)
            if brain == "claude" and claude_ok():
                return claude_text(system, messages, max_tokens=max_tokens, origen=origen)
        except Exception as e:
            last = e
            if brain == "claude":
                claude_failed(e)
            else:
                print(f"  (cerebro local falló: {e})")
    raise RuntimeError(f"Ningún cerebro disponible ({last or 'Ollama apagado y Claude sin saldo/conexión'})")
