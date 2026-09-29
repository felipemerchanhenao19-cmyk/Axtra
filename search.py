"""Búsqueda en internet GRATIS, independiente de cualquier cerebro.

1. Tavily (si pones TAVILY_API_KEY): 1000 búsquedas gratis al mes, hecho para IA.
2. DuckDuckGo (sin clave, sin límite fijo): el respaldo de siempre.
Los resultados se le pasan a cualquier cerebro gratis (Gemini, Groq, OpenRouter) para que responda con
datos actuales, así no dependemos de las búsquedas gratis de Gemini.
"""
import re
import time

import requests

from config import TAVILY_API_KEY

_blocked = {"tavily": 0.0, "ddg": 0.0}
NEWS_WORDS = r"\b(noticia|hoy|ayer|ultim|actualidad|semana|mercado|bolsa|resultado|gano|precio)"


def _tavily(query: str, n: int, news: bool):
    r = requests.post("https://api.tavily.com/search", timeout=25,
                      headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
                      json={"api_key": TAVILY_API_KEY, "query": query, "max_results": n,
                            "search_depth": "basic", "topic": "news" if news else "general"})
    if r.status_code in (401, 403, 429, 432, 433):
        _blocked["tavily"] = time.time() + 12 * 3600
        raise RuntimeError(f"Tavily {r.status_code}: sin búsquedas disponibles")
    r.raise_for_status()
    return [{"titulo": x.get("title", ""), "url": x.get("url", ""), "texto": x.get("content", "")}
            for x in r.json().get("results", [])]


def _ddg(query: str, n: int, news: bool):
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS   # nombre antiguo del paquete
    with DDGS() as d:
        rows = []
        if news:
            try:
                rows = list(d.news(query, region="wt-wt", max_results=n))
            except Exception:
                rows = []
        if not rows:
            rows = list(d.text(query, region="wt-wt", max_results=n))
    return [{"titulo": x.get("title", ""), "url": x.get("href") or x.get("url", ""),
             "texto": x.get("body") or x.get("excerpt", "")} for x in rows]


def web(query: str, n: int = 6):
    """Lista de resultados [{titulo, url, texto}] o [] si no se pudo buscar."""
    query = re.sub(r"^\[[^\]]*\]\s*", "", query).strip()[:300]
    news = bool(re.search(NEWS_WORDS, query.lower()))
    for name, fn in (("tavily", _tavily), ("ddg", _ddg)):
        if name == "tavily" and not TAVILY_API_KEY:
            continue
        if time.time() < _blocked[name]:
            continue
        try:
            res = [x for x in fn(query, n, news) if x["texto"]]
            if res:
                print(f"  (buscó en internet con {'Tavily' if name == 'tavily' else 'DuckDuckGo'}: gratis)")
                return res
        except ImportError:
            print("  (falta el buscador gratis: ejecuta python instalar.py)")
        except Exception as e:
            print(f"  (búsqueda {name} falló: {str(e)[:90]})")
            if name == "ddg":
                _blocked["ddg"] = time.time() + 120
    return []


def as_context(results) -> str:
    return "\n".join(f"[{i + 1}] {x['titulo']} ({x['url']}): {x['texto'][:600]}" for i, x in enumerate(results))


def sources(results) -> str:
    return "\n".join(f"- {x['titulo']} ({x['url']})" for x in results[:8])
