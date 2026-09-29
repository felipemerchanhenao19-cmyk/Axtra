"""Los cerebros de Axtra y cuándo usar cada uno.

- GEMINI (Google, plan gratuito): charla y clases de idiomas. Rápido, listo y gratis con límite
  diario; necesita internet. Ojo: en el plan gratis Google puede usar lo que se le envía, por eso
  solo recibe la charla, nunca datos de clientes ni del negocio.

- Cerebro LOCAL: un modelo pequeño que corre en tu PC con Ollama. Gratis, sin internet, más lento
  y menos inteligente. Sirve para charlar, el modo compañero, las clases de idiomas y el briefing.
- Cerebro AVANZADO: Claude (API de Anthropic). Cuesta saldo; se usa para finanzas, búsquedas,
  documentos, cámara, correos y todo lo que necesita herramientas.

Si Claude falla (sin saldo, sin internet o sin clave), Axtra pasa solo al cerebro local.
"""
import re
import time

import requests

from config import (ANTHROPIC_API_KEY, CHAT_BRAIN, CLAUDE_MODEL, FREE_BRAINS, GEMINI_API_KEY, GEMINI_MODEL,
                    GROQ_API_KEY, GROQ_MODEL, LOCAL_KEEP_ALIVE, LOCAL_MODEL, OLLAMA_URL, OPENROUTER_API_KEY,
                    OPENROUTER_MODEL)

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
    body = {"model": LOCAL_MODEL, "messages": msgs, "stream": False, "keep_alive": LOCAL_KEEP_ALIVE,
            "options": {"num_predict": max_tokens, "temperature": temperature, "num_ctx": ctx}}
    if any(k in LOCAL_MODEL for k in ("qwen3", "deepseek-r1", "think")):
        body["think"] = False   # modelos que "piensan en voz alta": respuesta directa, más rápida
    r = requests.post(f"{OLLAMA_URL}/api/chat", timeout=180, json=body)
    r.raise_for_status()
    import usage

    usage.record_local()
    text = r.json().get("message", {}).get("content", "")
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


def warm_up() -> None:
    """Carga el modelo local en memoria al arrancar (la primera respuesta sale más rápido)."""
    if local_ok(force=True):
        try:
            requests.post(f"{OLLAMA_URL}/api/generate", timeout=120,
                          json={"model": LOCAL_MODEL, "prompt": "", "keep_alive": LOCAL_KEEP_ALIVE})
        except Exception:
            pass


# ---------------- Gemini (Google) ----------------
_gemini = {"blocked_until": 0.0, "search_blocked_until": 0.0, "model": GEMINI_MODEL, "no_thinking_cfg": False}
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"


def gemini_ok() -> bool:
    return bool(GEMINI_API_KEY) and time.time() >= _gemini["blocked_until"]


def gemini_search_ok() -> bool:
    return gemini_ok() and time.time() >= _gemini["search_blocked_until"]


def _gemini_pick_model() -> str:
    """Si el modelo configurado no existe, escoge el mejor 'flash' disponible para la clave."""
    r = requests.get(f"{GEMINI_URL}/models", params={"key": GEMINI_API_KEY, "pageSize": 200}, timeout=15)
    r.raise_for_status()
    names = [m["name"].split("/")[-1] for m in r.json().get("models", [])
             if "generateContent" in m.get("supportedGenerationMethods", [])]
    flash = [n for n in names if "flash" in n and not any(x in n for x in ("image", "tts", "live", "audio", "embedding"))]
    if not flash:
        raise RuntimeError("tu clave de Gemini no tiene modelos Flash disponibles")
    stable = [n for n in flash if "preview" not in n and "exp" not in n and "lite" not in n] or flash

    def ver(n):
        m = re.search(r"(\d+(?:\.\d+)?)", n)
        return float(m.group(1)) if m else 0.0
    return sorted(stable, key=ver)[-1]


def gemini_chat(system: str, messages: list, max_tokens: int = 300, temperature: float = 0.7,
                search: bool = False, thinking: bool = False) -> str:
    """search=True: Gemini busca en Google antes de responder y agrega las fuentes al final.
    thinking=True: lo deja "pensar" (más lento, mejor para estudios e informes)."""
    contents = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
                for m in messages if isinstance(m.get("content"), str) and m["content"].strip()]
    body = {"systemInstruction": {"parts": [{"text": system}]}, "contents": contents,
            "generationConfig": {"maxOutputTokens": max_tokens + (2000 if thinking else 200), "temperature": temperature}}
    if search:
        body["tools"] = [{"google_search": {}}]
    for attempt in range(3):
        if not _gemini["no_thinking_cfg"] and not thinking:
            body["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 0}   # sin "pensar": más rápido
        else:
            body["generationConfig"].pop("thinkingConfig", None)
        r = requests.post(f"{GEMINI_URL}/models/{_gemini['model']}:generateContent",
                          headers={"x-goog-api-key": GEMINI_API_KEY}, json=body, timeout=40)
        if r.status_code == 404 and attempt == 0:
            _gemini["model"] = _gemini_pick_model()
            print(f"  (Gemini: uso el modelo {_gemini['model']})")
            continue
        if r.status_code == 400 and "thinking" in r.text.lower() and not _gemini["no_thinking_cfg"]:
            _gemini["no_thinking_cfg"] = True
            continue
        if r.status_code == 429:
            try:
                detail = r.json().get("error", {}).get("message", "")
            except Exception:
                detail = r.text
            print(f"  (Gemini dice: {detail[:220]})")
            if re.search(r"per ?minute|PerMinute|retry in", detail, re.I) and attempt < 2:
                time.sleep(6)   # límite por minuto: esperar un momento y reintentar
                continue
            if search:   # sin búsquedas gratis; las respuestas normales siguen funcionando
                _gemini["search_blocked_until"] = time.time() + 3 * 3600
                raise RuntimeError("Gemini no tiene búsquedas gratis disponibles ahora")
            _gemini["blocked_until"] = time.time() + 30 * 60
            raise RuntimeError("se acabó la cuota gratis de Gemini por ahora")
        if r.status_code in (500, 502, 503, 504):
            if attempt < 1:
                time.sleep(2)   # Google saturado un momento: reintenta una vez
                continue
            _gemini["blocked_until"] = time.time() + 3 * 60
            raise RuntimeError(f"Google está saturado ({r.status_code}); uso otro cerebro unos minutos")
        if r.status_code in (401, 403):
            _gemini["blocked_until"] = time.time() + 6 * 3600
            raise RuntimeError("la clave de Gemini no es válida o Gemini no está disponible en tu región")
        r.raise_for_status()
        cands = r.json().get("candidates") or []
        parts = (cands[0].get("content") or {}).get("parts", []) if cands else []
        text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
        if not text:
            raise RuntimeError("Gemini no devolvió texto")
        if search and cands:
            chunks = (cands[0].get("groundingMetadata") or {}).get("groundingChunks") or []
            seen, refs = set(), []
            for c in chunks:
                w = c.get("web") or {}
                t = w.get("title") or w.get("uri")
                if t and t not in seen:
                    seen.add(t)
                    refs.append(f"- {t}" + (f" ({w['uri']})" if w.get("uri") else ""))
            if refs:
                text += "\n\nFuentes consultadas:\n" + "\n".join(refs[:10])
        import usage

        usage.record_local("gemini")
        return text
    raise RuntimeError("Gemini no respondió")


# ---------------- Groq y OpenRouter (formato OpenAI, planes gratis) ----------------
PROVIDERS = {
    "groq": {"url": "https://api.groq.com/openai/v1/chat/completions", "key": GROQ_API_KEY, "model": GROQ_MODEL},
    "openrouter": {"url": "https://openrouter.ai/api/v1/chat/completions", "key": OPENROUTER_API_KEY,
                   "model": OPENROUTER_MODEL},
}
_blocked = {"groq": 0.0, "openrouter": 0.0}
NAMES = {"gemini": "Gemini", "groq": "Groq", "openrouter": "OpenRouter", "local": "local", "claude": "Claude"}


def compat_ok(name: str) -> bool:
    return bool(PROVIDERS[name]["key"]) and time.time() >= _blocked[name]


def compat_chat(name: str, system: str, messages: list, max_tokens: int = 300, temperature: float = 0.7,
                thinking: bool = False) -> str:
    p = PROVIDERS[name]
    msgs = [{"role": "system", "content": system}] + [
        {"role": m["role"], "content": m["content"]} for m in messages if isinstance(m.get("content"), str)]
    body = {"model": p["model"], "messages": msgs, "temperature": temperature,
            "max_tokens": max_tokens + (1500 if "gpt-oss" in p["model"] or thinking or name == "openrouter" else 100)}
    if name == "openrouter":
        body["reasoning"] = {"exclude": True}   # algunos modelos gratis "piensan": solo queremos la respuesta
    if "gpt-oss" in p["model"]:
        body["reasoning_effort"] = "medium" if thinking else "low"
    headers = {"Authorization": f"Bearer {p['key']}"}
    if name == "openrouter":
        headers.update({"HTTP-Referer": "https://github.com/axtra-felipe", "X-Title": "Axtra"})
    for attempt in range(3):
        r = requests.post(p["url"], headers=headers, json=body, timeout=60)
        if r.status_code == 400 and "reasoning" in r.text and ("reasoning_effort" in body or "reasoning" in body):
            body.pop("reasoning_effort", None)
            body.pop("reasoning", None)
            continue
        if r.status_code in (500, 502, 503, 504):
            _blocked[name] = time.time() + 3 * 60
            raise RuntimeError(f"{NAMES[name]} saturado ({r.status_code})")
        if r.status_code == 429:
            print(f"  ({NAMES[name]} dice: {r.text[:180]})")
            _blocked[name] = time.time() + (60 if "minute" in r.text.lower() else 60 * 60)
            raise RuntimeError(f"{NAMES[name]} sin cuota gratis por ahora")
        if r.status_code in (401, 402, 403):
            _blocked[name] = time.time() + 6 * 3600
            raise RuntimeError(f"{NAMES[name]}: clave inválida o sin acceso ({r.status_code})")
        r.raise_for_status()
        choices = r.json().get("choices") or []
        text = ((choices[0].get("message") or {}).get("content") or "") if choices else ""
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
        if not text and attempt == 0:
            body["max_tokens"] += 2000   # se le fue la respuesta en "pensar": más espacio y otro intento
            continue
        if not text:
            raise RuntimeError(f"{NAMES[name]} no devolvió texto")
        import usage

        usage.record_local(name)
        return text
    raise RuntimeError(f"{NAMES[name]} no respondió")


# ---------------- Cadena de cerebros gratis en la nube ----------------
def provider_ok(name: str) -> bool:
    return gemini_ok() if name == "gemini" else compat_ok(name) if name in PROVIDERS else False


def free_ok() -> bool:
    return any(provider_ok(n) for n in FREE_BRAINS)


def free_chat(system: str, messages: list, max_tokens: int = 350, temperature: float = 0.7,
              thinking: bool = False, web: bool = False, query: str = None):
    """Responde con el primer cerebro gratis disponible (Gemini -> Groq -> OpenRouter).
    web=True: primero busca en internet gratis (Tavily/DuckDuckGo) y le da los resultados al cerebro;
    si esa búsqueda falla, intenta la búsqueda propia de Gemini. Devuelve (texto, nombre_del_cerebro)."""
    extra, refs = "", ""
    if web:
        import search

        q = query or next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        res = search.web(q)
        if res:
            extra = ("\n\nRESULTADOS DE BÚSQUEDA EN INTERNET (actuales; úsalos como fuente principal, "
                     "no inventes nada que no esté aquí o que no sepas con certeza):\n" + search.as_context(res))
            refs = "\n\nFuentes consultadas:\n" + search.sources(res)
    last = None
    for name in FREE_BRAINS:
        if not provider_ok(name):
            continue
        try:
            if name == "gemini":
                use_google = web and not extra and gemini_search_ok()
                text = gemini_chat(system + extra, messages, max_tokens, temperature, search=use_google,
                                   thinking=thinking)
            else:
                if web and not extra:
                    continue   # sin resultados de búsqueda, estos cerebros no saben lo actual
                text = compat_chat(name, system + extra, messages, max_tokens, temperature, thinking)
            return text + (refs if refs and "Fuentes consultadas" not in text else ""), name
        except Exception as e:
            last = e
            print(f"  ({NAMES[name]} falló: {str(e)[:100]})")
    raise RuntimeError(f"Sin cerebros gratis disponibles ({last or 'agrega claves de Gemini, Groq u OpenRouter'})")


# ---------------- Cerebro barato: nube gratis -> local ----------------
def cheap_order(prefer: str = CHAT_BRAIN) -> list:
    return ["nube", "local"] if prefer != "local" else ["local", "nube"]


def cheap_ok() -> bool:
    return free_ok() or local_ok()


def cheap_chat(system_local: str, messages: list, system_cloud: str = None, max_tokens: int = 250,
               temperature: float = 0.7, prefer: str = CHAT_BRAIN):
    """Charla gratis. Devuelve (texto, 'gemini' o 'local'). system_cloud: versión del prompt sin
    datos privados, para Gemini."""
    last = None
    for b in cheap_order(prefer):
        try:
            if b == "nube" and free_ok():
                return free_chat(system_cloud or system_local, messages[-6:], max_tokens, temperature)
            if b == "local" and local_ok():
                return local_chat(system_local, messages, max_tokens, temperature), "local"
        except Exception as e:
            last = e
            print(f"  ({b} falló: {str(e)[:100]})")
    raise RuntimeError(f"Sin cerebro gratis disponible ({last or 'sin Gemini ni Ollama'})")


# ---------------- Cerebro avanzado (Claude) ----------------
def client():
    global _client
    if _client is None:
        import anthropic

        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def claude_ok() -> bool:
    import modes

    if not modes.claude_allowed():   # modo "gratis" o "local": Claude nunca se usa
        return False
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
    order = {"local": ["local", "claude"], "gemini": ["gemini", "local", "claude"]}.get(prefer, ["claude", "local"])
    last = None
    for brain in order:
        try:
            if brain == "gemini" and free_ok():
                return free_chat(system, messages, max_tokens=max_tokens, temperature=temperature)[0]
            if brain == "local" and local_ok():
                return local_chat(system, messages, max_tokens=max_tokens, temperature=temperature)
            if brain == "claude" and claude_ok():
                return claude_text(system, messages, max_tokens=max_tokens, origen=origen)
        except Exception as e:
            last = e
            if brain == "claude":
                claude_failed(e)
            else:
                print(f"  ({brain} falló: {str(e)[:100]})")
    raise RuntimeError(f"Ningún cerebro disponible ({last or why_unavailable(order)})")


def why_unavailable(brains: list) -> str:
    """Explica por qué no hay ningún cerebro de la lista, para que Felipe sepa qué arreglar."""
    import modes

    reasons = []
    for brain in brains:
        if brain == "gemini":
            names = "/".join(NAMES.get(n, n) for n in FREE_BRAINS)
            if not any(GEMINI_API_KEY if n == "gemini" else PROVIDERS.get(n, {}).get("key") for n in FREE_BRAINS):
                reasons.append(f"sin claves de {names} en el .env")
            else:
                reasons.append(f"{names} sin cuota gratis por ahora")
        elif brain == "local":
            reasons.append("Ollama apagado")
        elif brain == "claude":
            if not modes.claude_allowed():
                reasons.append("Claude desactivado (modo gratis)")
            elif not ANTHROPIC_API_KEY:
                reasons.append("sin clave de Claude en el .env")
            else:
                reasons.append(f"Claude: {claude_reason or 'sin saldo o sin conexión'}")
    return ", ".join(reasons)
