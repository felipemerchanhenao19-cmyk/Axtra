"""Finanzas avanzadas: análisis fundamental (SEC), simulador de inversiones y gráficas."""
import json
import os
import threading
from datetime import datetime

import requests

import finance
from config import DATA_DIR, DOCS_DIR, SEC_CONTACT

SIM_PATH = DATA_DIR / "simulador.json"
_lock = threading.Lock()


def open_path(path) -> None:
    """Abre un archivo en Windows (imagen, documento, página)."""
    try:
        if os.name == "nt":
            os.startfile(str(path))
    except Exception as e:
        print(f"  (no pude abrir {path}: {e})")


# ---------- Análisis fundamental (datos oficiales de la SEC, empresas de EE. UU.) ----------
_cik_cache = {}
TAGS = {
    "ingresos": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
    "utilidad_neta": ["NetIncomeLoss", "ProfitLoss"],
    "utilidad_operativa": ["OperatingIncomeLoss"],
    "eps_diluido": ["EarningsPerShareDiluted", "EarningsPerShareBasic"],
    "activos": ["Assets"],
    "pasivos": ["Liabilities"],
    "patrimonio": ["StockholdersEquity"],
    "caja": ["CashAndCashEquivalentsAtCarryingValue"],
    "deuda_largo_plazo": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "flujo_caja_operativo": ["NetCashProvidedByUsedInOperatingActivities"],
}


def _sec_headers():
    # La SEC pide identificarse con un correo: pon el tuyo en .env (JARVIS_CONTACTO_SEC)
    return {"User-Agent": f"Jarvis asistente personal {SEC_CONTACT}".strip()}


def _cik(ticker: str) -> str:
    if not _cik_cache:
        r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=_sec_headers(), timeout=20)
        r.raise_for_status()
        for row in r.json().values():
            _cik_cache[row["ticker"].upper()] = (str(row["cik_str"]).zfill(10), row["title"])
    if ticker.upper() not in _cik_cache:
        raise ValueError(f"{ticker} no está en la SEC (puede ser una empresa extranjera)")
    return _cik_cache[ticker.upper()]


def _annual(facts: dict, tags: list) -> dict:
    """Valores anuales (10-K) por año fiscal para la primera etiqueta que exista."""
    gaap = facts.get("facts", {}).get("us-gaap", {})
    for tag in tags:
        if tag not in gaap:
            continue
        units = gaap[tag]["units"]
        vals = units.get("USD") or units.get("USD/shares") or next(iter(units.values()))
        out = {}
        for v in vals:
            if v.get("form") == "10-K" and v.get("fp") == "FY" and v.get("end"):
                start = v.get("start")
                if start:  # solo periodos de ~1 año (evita trimestres dentro del 10-K)
                    days = (datetime.fromisoformat(v["end"]) - datetime.fromisoformat(start)).days
                    if not 330 <= days <= 400:
                        continue
                out[v["end"][:4]] = v["val"]
        if out:
            return dict(sorted(out.items())[-4:])
    return {}


def analisis_fundamental(simbolo: str) -> dict:
    s = finance.sym(simbolo)
    cik, nombre = _cik(s)
    r = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                     headers=_sec_headers(), timeout=30)
    r.raise_for_status()
    facts = r.json()
    data = {k: _annual(facts, tags) for k, tags in TAGS.items()}

    def last(k):
        d = data.get(k) or {}
        return list(d.values())[-1] if d else None

    def growth(k):
        d = list((data.get(k) or {}).values())
        return round((d[-1] / d[-2] - 1) * 100, 1) if len(d) >= 2 and d[-2] else None

    price = finance.last_price(s)
    ingresos, utilidad, eps = last("ingresos"), last("utilidad_neta"), last("eps_diluido")
    millones = lambda v: round(v / 1e6) if v is not None else None  # noqa: E731
    return {
        "empresa": nombre, "simbolo": s, "precio": round(price, 2),
        "ingresos_anuales_millones_usd": {y: millones(v) for y, v in data["ingresos"].items()},
        "utilidad_neta_millones_usd": {y: millones(v) for y, v in data["utilidad_neta"].items()},
        "crecimiento_ingresos_pct": growth("ingresos"),
        "crecimiento_utilidad_pct": growth("utilidad_neta"),
        "margen_neto_pct": round(utilidad / ingresos * 100, 1) if ingresos and utilidad else None,
        "eps_diluido": eps,
        "per_precio_utilidad": round(price / eps, 1) if eps and eps > 0 else None,
        "caja_millones": millones(last("caja")),
        "deuda_largo_plazo_millones": millones(last("deuda_largo_plazo")),
        "patrimonio_millones": millones(last("patrimonio")),
        "deuda_sobre_patrimonio": round(last("deuda_largo_plazo") / last("patrimonio"), 2)
        if last("deuda_largo_plazo") and last("patrimonio") else None,
        "flujo_caja_operativo_millones": millones(last("flujo_caja_operativo")),
        "fuente": "Reportes anuales 10-K en la SEC",
    }


# ---------- Simulador de inversiones (dinero ficticio) ----------
def _sim():
    try:
        return json.loads(SIM_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _sim_save(d):
    with _lock:
        SIM_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def sim_reiniciar(capital: float = 10000) -> dict:
    spx = finance.last_price("^GSPC")
    d = {"efectivo": float(capital), "capital_inicial": float(capital), "posiciones": {},
         "operaciones": [], "inicio": datetime.now().strftime("%Y-%m-%d"), "sp500_inicio": spx}
    _sim_save(d)
    return {"ok": True, "capital": capital, "nota": "Simulador reiniciado con dinero ficticio."}


def sim_operar(accion: str, simbolo: str, acciones: float) -> dict:
    d = _sim()
    if d is None:
        sim_reiniciar()
        d = _sim()
    s, n = finance.sym(simbolo), float(acciones)
    price = finance.last_price(s)
    pos = d["posiciones"].get(s, {"acciones": 0.0, "precio_promedio": 0.0})
    if accion == "comprar":
        cost = price * n
        if cost > d["efectivo"]:
            return {"error": f"Efectivo insuficiente: tienes {d['efectivo']:.2f} y necesitas {cost:.2f}"}
        total = pos["acciones"] + n
        pos["precio_promedio"] = (pos["acciones"] * pos["precio_promedio"] + cost) / total
        pos["acciones"] = total
        d["efectivo"] -= cost
    else:
        if n > pos["acciones"]:
            return {"error": f"Solo tienes {pos['acciones']} acciones de {s}"}
        pos["acciones"] -= n
        d["efectivo"] += price * n
    if pos["acciones"] > 0:
        d["posiciones"][s] = pos
    else:
        d["posiciones"].pop(s, None)
    d["operaciones"].append({"fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "accion": accion,
                             "simbolo": s, "acciones": n, "precio": round(price, 2)})
    _sim_save(d)
    return {"ok": True, "operacion": d["operaciones"][-1], "efectivo": round(d["efectivo"], 2)}


def sim_ver() -> dict:
    d = _sim()
    if d is None:
        return {"nota": "El simulador no ha empezado. Pide: 'reinicia el simulador con 10 mil dólares'."}
    valor, filas = d["efectivo"], []
    for s, p in d["posiciones"].items():
        price = finance.last_price(s)
        valor += price * p["acciones"]
        filas.append({"simbolo": s, "acciones": p["acciones"], "precio_promedio": round(p["precio_promedio"], 2),
                      "precio_actual": round(price, 2),
                      "ganancia_pct": round((price / p["precio_promedio"] - 1) * 100, 2)})
    try:
        spx_pct = round((finance.last_price("^GSPC") / d["sp500_inicio"] - 1) * 100, 2)
    except Exception:
        spx_pct = None
    return {"valor_total": round(valor, 2), "efectivo": round(d["efectivo"], 2), "posiciones": filas,
            "rendimiento_pct": round((valor / d["capital_inicial"] - 1) * 100, 2),
            "sp500_mismo_periodo_pct": spx_pct, "desde": d["inicio"],
            "ultimas_operaciones": d["operaciones"][-5:]}


# ---------- Gráficas ----------
def grafica(simbolo: str, periodo: str = "1y", comparar: str = "") -> dict:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    rng = periodo if periodo in ("1mo", "3mo", "6mo", "1y", "2y", "5y") else "1y"
    symbols = [finance.sym(simbolo)] + [finance.sym(c) for c in comparar.split(",") if c.strip()]
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=110)
    fig.patch.set_facecolor("#0b1220")
    ax.set_facecolor("#0b1220")
    colors = ["#4cc9f0", "#f72585", "#b5e48c", "#ffd166"]
    for i, s in enumerate(symbols):
        _, pairs = finance.get_history(s, rng)
        dates = [datetime.fromtimestamp(t) for t, _ in pairs]
        closes = [c for _, c in pairs]
        if len(symbols) > 1:  # comparar en % desde el inicio
            closes = [(c / closes[0] - 1) * 100 for c in closes]
        ax.plot(dates, closes, color=colors[i % 4], linewidth=2, label=s)
        if len(symbols) == 1 and len(closes) >= 50:
            sma = [sum(closes[j - 49:j + 1]) / 50 for j in range(49, len(closes))]
            ax.plot(dates[49:], sma, color="#ffd166", linewidth=1, linestyle="--", label="Media 50 días")
    ax.set_title(f"{' vs '.join(symbols)} · {rng}", color="white", fontsize=14)
    ax.set_ylabel("% de cambio" if len(symbols) > 1 else "Precio (USD)", color="#9aa4b2")
    ax.tick_params(colors="#9aa4b2")
    for sp in ax.spines.values():
        sp.set_color("#243044")
    ax.grid(color="#1c2638")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend(facecolor="#0b1220", labelcolor="white", edgecolor="#243044")
    path = DOCS_DIR / f"grafica_{'_'.join(s.replace('^', '') for s in symbols)}.png"
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)
    open_path(path)
    return {"ok": True, "archivo": str(path), "nota": "La gráfica ya está abierta en pantalla."}


TOOL_SCHEMAS = [
    {"name": "analisis_fundamental", "description": "Análisis fundamental de una empresa de EE. UU. con sus reportes oficiales (ingresos, utilidad, márgenes, deuda, caja, P/E). Para empresas extranjeras usa la búsqueda web.",
     "input_schema": {"type": "object", "properties": {"simbolo": {"type": "string"}}, "required": ["simbolo"]}},
    {"name": "sim_reiniciar", "description": "Reinicia el simulador de inversiones con dinero ficticio.",
     "input_schema": {"type": "object", "properties": {"capital": {"type": "number"}}}},
    {"name": "sim_operar", "description": "Compra o vende en el SIMULADOR (dinero ficticio) al precio actual.",
     "input_schema": {"type": "object", "properties": {"accion": {"type": "string", "enum": ["comprar", "vender"]}, "simbolo": {"type": "string"}, "acciones": {"type": "number"}}, "required": ["accion", "simbolo", "acciones"]}},
    {"name": "sim_ver", "description": "Estado del simulador: valor, posiciones, rendimiento y comparación contra el S&P 500.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "grafica", "description": "Muestra en pantalla la gráfica de precio de un activo. Periodo: 1mo, 3mo, 6mo, 1y, 2y, 5y. 'comparar' = otros símbolos separados por coma.",
     "input_schema": {"type": "object", "properties": {"simbolo": {"type": "string"}, "periodo": {"type": "string"}, "comparar": {"type": "string"}}, "required": ["simbolo"]}},
]
FUNCS = {"analisis_fundamental": analisis_fundamental, "sim_reiniciar": sim_reiniciar,
         "sim_operar": sim_operar, "sim_ver": sim_ver, "grafica": grafica}
