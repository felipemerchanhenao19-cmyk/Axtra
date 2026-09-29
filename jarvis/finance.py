"""Módulo financiero de Jarvis: cotizaciones, análisis técnico, portafolio, seguimiento y alertas.

Datos: Yahoo Finance (gráficos públicos) y Stooq como respaldo. Gratis, sin clave.
Jarvis ANALIZA y OPINA, pero NUNCA compra ni vende: las decisiones son de Felipe.
"""
import csv
import io
import json
import math
import threading
from datetime import datetime

import requests

from config import DATA_DIR

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
PORTFOLIO_PATH = DATA_DIR / "portafolio.json"
_lock = threading.Lock()

ALIASES = {
    "nvidia": "NVDA", "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL",
    "alphabet": "GOOGL", "amazon": "AMZN", "meta": "META", "facebook": "META",
    "tesla": "TSLA", "tsmc": "TSM", "amd": "AMD", "broadcom": "AVGO", "intel": "INTC",
    "asml": "ASML", "palantir": "PLTR", "netflix": "NFLX", "jpmorgan": "JPM",
    "visa": "V", "mastercard": "MA", "coca cola": "KO", "berkshire": "BRK-B",
    "s&p 500": "^GSPC", "s&p500": "^GSPC", "sp500": "^GSPC", "nasdaq": "^IXIC",
    "dow jones": "^DJI", "bitcoin": "BTC-USD", "ethereum": "ETH-USD",
    "dolar": "COP=X", "dólar": "COP=X", "peso colombiano": "COP=X",
    "ecopetrol": "EC", "bancolombia": "CIB", "oro": "GC=F", "petroleo": "CL=F", "petróleo": "CL=F",
    "voo": "VOO", "spy": "SPY", "qqq": "QQQ", "botz": "BOTZ", "robo": "ROBO",
}


def sym(s: str) -> str:
    k = s.strip().lower()
    return ALIASES.get(k, s.strip().upper())


# ---------- Datos ----------
def _yahoo(symbol: str, rng: str = "1y"):
    r = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        params={"range": rng, "interval": "1d"}, headers=UA, timeout=15,
    )
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    closes = res["indicators"]["quote"][0]["close"]
    pairs = [(t, c) for t, c in zip(res["timestamp"], closes) if c is not None]
    if len(pairs) < 2:
        raise ValueError("pocos datos")
    return res["meta"], pairs


def _stooq(symbol: str):
    s = symbol.lower()
    if "." not in s and not s.startswith("^") and "=" not in s and "-" not in s:
        s += ".us"
    r = requests.get("https://stooq.com/q/d/l/", params={"s": s, "i": "d"}, headers=UA, timeout=15)
    rows = list(csv.DictReader(io.StringIO(r.text)))
    if not rows or "Close" not in rows[0]:
        raise ValueError("sin datos")
    pairs = [(datetime.strptime(x["Date"], "%Y-%m-%d").timestamp(), float(x["Close"])) for x in rows[-260:]]
    return {"currency": "USD", "regularMarketPrice": pairs[-1][1], "symbol": symbol.upper()}, pairs


def get_history(symbol: str, rng: str = "1y"):
    try:
        return _yahoo(symbol, rng)
    except Exception as e1:
        try:
            return _stooq(symbol)
        except Exception as e2:
            raise RuntimeError(f"No pude obtener datos de {symbol} (Yahoo: {e1}; Stooq: {e2})")


def last_price(symbol: str) -> float:
    meta, pairs = get_history(symbol)
    return float(meta.get("regularMarketPrice") or pairs[-1][1])


# ---------- Análisis ----------
def _pct(a, b):
    return round((a / b - 1) * 100, 2) if b else None


def _sma(values, n):
    return round(sum(values[-n:]) / n, 2) if len(values) >= n else None


def _rsi(values, n=14):
    if len(values) <= n:
        return None
    gains = losses = 0.0
    for a, b in zip(values[-n - 1:-1], values[-n:]):
        d = b - a
        gains += max(d, 0)
        losses += max(-d, 0)
    if losses == 0:
        return 100.0
    rs = (gains / n) / (losses / n)
    return round(100 - 100 / (1 + rs), 1)


def cotizacion(simbolo: str) -> dict:
    s = sym(simbolo)
    meta, pairs = get_history(s)
    closes = [c for _, c in pairs]
    price = float(meta.get("regularMarketPrice") or closes[-1])
    return {
        "simbolo": s,
        "nombre": meta.get("longName") or meta.get("shortName") or s,
        "precio": round(price, 2),
        "moneda": meta.get("currency", "USD"),
        "cambio_dia_pct": _pct(price, closes[-2]),
        "fecha_dato": datetime.fromtimestamp(pairs[-1][0]).strftime("%Y-%m-%d"),
    }


def analisis_tecnico(simbolo: str) -> dict:
    s = sym(simbolo)
    meta, pairs = get_history(s)
    c = [x for _, x in pairs]
    price = float(meta.get("regularMarketPrice") or c[-1])
    rets = [b / a - 1 for a, b in zip(c[:-1], c[1:]) if a]
    mean = sum(rets) / len(rets)
    vol = math.sqrt(sum((r - mean) ** 2 for r in rets) / len(rets)) * math.sqrt(252) * 100
    peak, max_dd = c[0], 0.0
    for x in c:
        peak = max(peak, x)
        max_dd = min(max_dd, x / peak - 1)
    sma50, sma200 = _sma(c, 50), _sma(c, 200)
    tendencia = "sin datos suficientes"
    if sma50 and sma200:
        tendencia = "alcista" if price > sma50 > sma200 else "bajista" if price < sma50 < sma200 else "mixta"
    return {
        **cotizacion(s),
        "rendimiento_1_mes_pct": _pct(price, c[-22]) if len(c) > 22 else None,
        "rendimiento_3_meses_pct": _pct(price, c[-64]) if len(c) > 64 else None,
        "rendimiento_1_anio_pct": _pct(price, c[0]),
        "maximo_52_semanas": round(max(c), 2),
        "minimo_52_semanas": round(min(c), 2),
        "media_movil_20": _sma(c, 20), "media_movil_50": sma50, "media_movil_200": sma200,
        "rsi_14": _rsi(c),
        "volatilidad_anual_pct": round(vol, 1),
        "caida_maxima_1_anio_pct": round(max_dd * 100, 1),
        "tendencia": tendencia,
        "nota": "RSI > 70 suele indicar sobrecompra; < 30 sobreventa. Es análisis técnico, no una garantía.",
    }


# ---------- Portafolio, seguimiento y alertas ----------
def _load():
    try:
        return json.loads(PORTFOLIO_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"posiciones": {}, "seguimiento": [], "alertas": []}


def _save(d):
    with _lock:
        PORTFOLIO_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def portafolio_registrar(simbolo: str, acciones: float, precio: float) -> dict:
    d, s = _load(), sym(simbolo)
    p = d["posiciones"].get(s, {"acciones": 0.0, "precio_promedio": 0.0})
    total = p["acciones"] + float(acciones)
    p["precio_promedio"] = round((p["acciones"] * p["precio_promedio"] + float(acciones) * float(precio)) / total, 4)
    p["acciones"] = total
    d["posiciones"][s] = p
    _save(d)
    return {"ok": True, "simbolo": s, **p}


def portafolio_vender(simbolo: str, acciones: float) -> dict:
    d, s = _load(), sym(simbolo)
    if s not in d["posiciones"]:
        return {"error": f"No hay posición en {s}"}
    d["posiciones"][s]["acciones"] -= float(acciones)
    if d["posiciones"][s]["acciones"] <= 0:
        del d["posiciones"][s]
    _save(d)
    return {"ok": True, "posiciones": d["posiciones"]}


def portafolio_ver() -> dict:
    d = _load()
    filas, invertido, actual = [], 0.0, 0.0
    for s, p in d["posiciones"].items():
        try:
            precio = last_price(s)
        except Exception:
            precio = p["precio_promedio"]
        costo, valor = p["acciones"] * p["precio_promedio"], p["acciones"] * precio
        invertido, actual = invertido + costo, actual + valor
        filas.append({"simbolo": s, "acciones": p["acciones"], "precio_promedio": p["precio_promedio"],
                      "precio_actual": round(precio, 2), "ganancia_pct": _pct(valor, costo),
                      "valor": round(valor, 2)})
    return {"posiciones": filas, "invertido": round(invertido, 2), "valor_actual": round(actual, 2),
            "ganancia_total_pct": _pct(actual, invertido) if invertido else 0,
            "seguimiento": d["seguimiento"], "alertas": d["alertas"]}


def lista_seguimiento(accion: str, simbolo: str = "") -> dict:
    d = _load()
    s = sym(simbolo) if simbolo else ""
    if accion == "agregar" and s and s not in d["seguimiento"]:
        d["seguimiento"].append(s)
    elif accion == "quitar" and s in d["seguimiento"]:
        d["seguimiento"].remove(s)
    _save(d)
    return {"seguimiento": d["seguimiento"]}


def alerta_precio(simbolo: str, precio: float, direccion: str) -> dict:
    d = _load()
    d["alertas"].append({"simbolo": sym(simbolo), "precio": float(precio),
                         "direccion": "abajo" if "baj" in direccion.lower() or "abajo" in direccion.lower() else "arriba"})
    _save(d)
    return {"ok": True, "alertas": d["alertas"]}


def revisar_alertas() -> list:
    """La usa el módulo autónomo cada 15 minutos. Devuelve avisos y borra las alertas cumplidas."""
    d = _load()
    avisos, quedan = [], []
    for a in d["alertas"]:
        try:
            p = last_price(a["simbolo"])
        except Exception:
            quedan.append(a)
            continue
        hit = p <= a["precio"] if a["direccion"] == "abajo" else p >= a["precio"]
        if hit:
            avisos.append(f"Alerta de precio: {a['simbolo']} está en {p:.2f} "
                          f"({'bajó de' if a['direccion'] == 'abajo' else 'superó'} {a['precio']}).")
        else:
            quedan.append(a)
    if avisos:
        d["alertas"] = quedan
        _save(d)
    return avisos


def watchlist() -> list:
    return _load()["seguimiento"]


TOOL_SCHEMAS = [
    {"name": "cotizacion", "description": "Precio actual y cambio del día de una acción, ETF, índice, cripto o divisa (ej: NVDA, Nvidia, S&P 500, bitcoin, dólar).",
     "input_schema": {"type": "object", "properties": {"simbolo": {"type": "string"}}, "required": ["simbolo"]}},
    {"name": "analisis_tecnico", "description": "Análisis completo de 1 año: rendimientos, medias móviles, RSI, volatilidad, caída máxima y tendencia.",
     "input_schema": {"type": "object", "properties": {"simbolo": {"type": "string"}}, "required": ["simbolo"]}},
    {"name": "portafolio_ver", "description": "Muestra el portafolio de Felipe con ganancias/pérdidas, su lista de seguimiento y alertas.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "portafolio_registrar", "description": "Registra una compra que Felipe YA hizo (Jarvis no compra nada).",
     "input_schema": {"type": "object", "properties": {"simbolo": {"type": "string"}, "acciones": {"type": "number"}, "precio": {"type": "number"}}, "required": ["simbolo", "acciones", "precio"]}},
    {"name": "portafolio_vender", "description": "Registra una venta que Felipe YA hizo.",
     "input_schema": {"type": "object", "properties": {"simbolo": {"type": "string"}, "acciones": {"type": "number"}}, "required": ["simbolo", "acciones"]}},
    {"name": "lista_seguimiento", "description": "Ver, agregar o quitar acciones de la lista de seguimiento (Jarvis las estudia solo).",
     "input_schema": {"type": "object", "properties": {"accion": {"type": "string", "enum": ["ver", "agregar", "quitar"]}, "simbolo": {"type": "string"}}, "required": ["accion"]}},
    {"name": "alerta_precio", "description": "Crea una alerta: avisa cuando un activo suba por encima o baje por debajo de un precio.",
     "input_schema": {"type": "object", "properties": {"simbolo": {"type": "string"}, "precio": {"type": "number"}, "direccion": {"type": "string", "enum": ["arriba", "abajo"]}}, "required": ["simbolo", "precio", "direccion"]}},
]

FUNCS = {
    "cotizacion": cotizacion, "analisis_tecnico": analisis_tecnico, "portafolio_ver": portafolio_ver,
    "portafolio_registrar": portafolio_registrar, "portafolio_vender": portafolio_vender,
    "lista_seguimiento": lista_seguimiento, "alerta_precio": alerta_precio,
}
