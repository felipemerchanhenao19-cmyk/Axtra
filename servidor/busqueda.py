"""Búsqueda en internet gratis: Tavily (si hay clave, 1000 gratis al mes) y DuckDuckGo (sin clave)."""
import re
import time

import requests

from . import config

_pausa = {"tavily": 0.0, "ddg": 0.0}
NOTICIAS = r"\b(noticia|hoy|ayer|ultim|actualidad|semana|mercado|bolsa|resultado|gano|precio)"


def _tavily(q: str, n: int, noticias: bool):
    r = requests.post("https://api.tavily.com/search", timeout=25,
                      headers={"Authorization": f"Bearer {config.TAVILY_API_KEY}"},
                      json={"query": q, "max_results": n, "search_depth": "basic",
                            "topic": "news" if noticias else "general"})
    if r.status_code in (401, 403, 429, 432, 433):
        _pausa["tavily"] = time.time() + 12 * 3600
        raise RuntimeError(f"Tavily {r.status_code}")
    r.raise_for_status()
    return [{"titulo": x.get("title", ""), "url": x.get("url", ""), "texto": x.get("content", "")}
            for x in r.json().get("results", [])]


def _ddg(q: str, n: int, noticias: bool):
    from ddgs import DDGS

    with DDGS() as d:
        filas = []
        if noticias:
            try:
                filas = list(d.news(q, region="wt-wt", max_results=n))
            except Exception:
                filas = []
        if not filas:
            filas = list(d.text(q, region="wt-wt", max_results=n))
    return [{"titulo": x.get("title", ""), "url": x.get("href") or x.get("url", ""),
             "texto": x.get("body") or x.get("excerpt", "")} for x in filas]


def web(q: str, n: int = 6) -> list:
    """[{titulo, url, texto}] o [] si no se pudo buscar."""
    q = q.strip()[:300]
    noticias = bool(re.search(NOTICIAS, q.lower()))
    for nombre, fn in (("tavily", _tavily), ("ddg", _ddg)):
        if (nombre == "tavily" and not config.TAVILY_API_KEY) or time.time() < _pausa[nombre]:
            continue
        try:
            res = [x for x in fn(q, n, noticias) if x["texto"]]
            if res:
                return res
        except Exception:
            _pausa[nombre] = max(_pausa[nombre], time.time() + 120)
    return []


def contexto(res: list) -> str:
    return "\n".join(f"[{i + 1}] {x['titulo']} ({x['url']}): {x['texto'][:600]}" for i, x in enumerate(res))
