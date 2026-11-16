"""Alertas: cada mañana revisa qué vence y avisa por Telegram. También arma los textos de /pendientes, /resumen
y /tarjetas, que funcionan aunque la IA no esté disponible."""
from datetime import date, timedelta

from . import config, db
from .herramientas import calcular_resumen, pesos, proximos, ver_cuentas

ICONO = {"tarjeta": "💳", "credito": "🏦", "cuota": "🧾", "impuesto": "🏛️", "seguro": "🛡️", "servicio": "💡", "otro": "📌"}
MESES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]


def _cuando(dias: int) -> str:
    if dias < 0:
        return f"*VENCIDO hace {-dias} día{'s' if dias < -1 else ''}*"
    return {0: "*HOY*", 1: "*mañana*"}.get(dias, f"en {dias} días")


def _linea_pago(o: dict) -> str:
    valor = f" · {pesos(o['monto'])}" if o["monto"] else ""
    minimo = f" (mínimo {pesos(o['monto_minimo'])})" if o.get("monto_minimo") else ""
    cuotas = f" · cuota {o['cuotas_pagadas'] + 1} de {o['cuotas_total']}" if o["cuotas_total"] else ""
    return f"{ICONO.get(o['tipo'], '📌')} {o['nombre']}{valor}{minimo}{cuotas} — {_cuando(o['dias'])} ({o['fecha']})"


def texto_pendientes(dias: int = 30) -> tuple:
    """Devuelve (texto, botones) con lo que vence en los próximos días."""
    p = proximos(dias)
    if not (p["pagos"] or p["labores"] or p["ganado"]):
        return f"✅ Nada vence en los próximos {dias} días.", []
    lineas, botones = [f"📅 *Lo que viene (próximos {dias} días)*"], []
    if p["pagos"]:
        lineas.append("\n*Pagos*")
        for o in p["pagos"]:
            lineas.append(_linea_pago(o))
            if len(botones) < 8:
                botones.append([(f"✅ Ya pagué: {o['nombre'][:28]}", f"p:{o['id']}")])
    if p["labores"]:
        lineas.append("\n*Papa*")
        for l in p["labores"]:
            lineas.append(f"🥔 {l['tipo']} en {l['lote']} — {_cuando((date.fromisoformat(l['proxima']) - db.hoy()).days)}")
    if p["ganado"]:
        lineas.append("\n*Ganado*")
        for e in p["ganado"]:
            quien = e["codigo"] and f"{e['codigo']}{' ' + e['nombre'] if e['nombre'] else ''}" or "todo el hato"
            que = "parto esperado" if e["tipo"] == "servicio" else f"próxima {e['tipo']}"
            lineas.append(f"🐄 {que} de {quien} — {_cuando((date.fromisoformat(e['proxima']) - db.hoy()).days)}")
    return "\n".join(lineas), botones


def texto_resumen(desde: str = None, hasta: str = None) -> str:
    hoy = db.hoy()
    r = calcular_resumen(desde or hoy.replace(day=1).isoformat(), hasta or hoy.isoformat())
    lineas = [f"📊 *Resumen {r['desde']} a {r['hasta']}*",
              f"Ingresos: *{pesos(r['ingresos'])}*",
              f"Gastos hacienda: {pesos(r['gastos_hacienda'])}",
              f"Gastos personales: {pesos(r['gastos_personales'])}",
              f"Resultado: *{pesos(r['resultado'])}*"]
    if r["ingresos_por_actividad"]:
        lineas.append("\n*Ingresos por actividad*")
        lineas += [f"  {k.capitalize()}: {pesos(v)}" for k, v in sorted(r["ingresos_por_actividad"].items(), key=lambda x: -x[1])]
    if r["gastos_por_categoria"]:
        lineas.append("\n*Gastos por categoría*")
        lineas += [f"  {k}: {pesos(v)}" for k, v in sorted(r["gastos_por_categoria"].items(), key=lambda x: -x[1])[:10]]
    return "\n".join(lineas)


def texto_tarjetas() -> str:
    datos = ver_cuentas({})
    if not datos["cuentas"]:
        return "No hay tarjetas registradas. Mándame la foto o el PDF del extracto, o escríbeme: «registra la Visa de Bancolombia, paga el 15»."
    lineas = ["💳 *Tarjetas y cuentas*"]
    for c in datos["cuentas"]:
        lineas.append(f"\n*{c['nombre']}*" + (f" ****{c['ultimos4']}" if c["ultimos4"] else ""))
        if c["cupo"]:
            lineas.append(f"  Deuda {pesos(c['deuda'])} de {pesos(c['cupo'])}" + (f" ({c['uso_cupo']})" if c.get("uso_cupo") else ""))
        for o in c["proximos_pagos"][:2]:
            lineas.append(f"  Próximo pago: {o['fecha']}" + (f" · {pesos(o['monto'])}" if o["monto"] else ""))
        for d in c["diferidos"][:6]:
            lineas.append(f"  • {d['descripcion']}: cuota {d['cuota_actual']}/{d['cuotas_total']} · {pesos(d['valor_cuota'])}")
    return "\n".join(lineas)


# ---------------- La revisión de cada mañana ----------------
def _umbral(dias: int):
    """En qué aviso cae: con avisos 7,3,1,0 → 5 días cae en el de 7. Así no se pierde si el servidor estuvo apagado."""
    candidatos = [x for x in config.DIAS_AVISO if x >= dias]
    return min(candidatos) if candidatos else None


def revision_diaria() -> tuple:
    """Devuelve (texto, botones) con lo nuevo que hay que avisar hoy, o ("", []) si no hay nada."""
    hoy = db.hoy()
    p = proximos(max(config.DIAS_AVISO + [14]))
    lineas, botones, claves = [], [], []
    for o in p["pagos"]:
        if o["dias"] < 0:
            clave = f"obl:{o['id']}:{o['fecha']}:vencido:{hoy}"            # vencido: se recuerda todos los días
        else:
            u = _umbral(o["dias"])
            if u is None:
                continue
            clave = f"obl:{o['id']}:{o['fecha']}:{u}"
        if not db.ya_avisado(clave):
            lineas.append(_linea_pago(o))
            claves.append(clave)
            if len(botones) < 8:
                botones.append([(f"✅ Ya pagué: {o['nombre'][:28]}", f"p:{o['id']}")])
    for l in p["labores"]:
        dias = (date.fromisoformat(l["proxima"]) - hoy).days
        clave = f"lab:{l['id']}:{l['proxima']}"
        if dias <= 2 and not db.ya_avisado(clave):
            lineas.append(f"🥔 Toca {l['tipo']} en {l['lote']} — {_cuando(dias)}")
            claves.append(clave)
    for e in p["ganado"]:
        dias = (date.fromisoformat(e["proxima"]) - hoy).days
        quien = e["codigo"] and f"{e['codigo']}{' ' + e['nombre'] if e['nombre'] else ''}" or "todo el hato"
        if e["tipo"] == "servicio":
            u = 14 if dias > 3 else 0
            texto = f"🐄 Parto esperado de {quien} — {_cuando(dias)}"
        else:
            u = 0 if dias <= 3 else None
            texto = f"🐄 Toca {e['tipo']} ({e['detalle'] or 'refuerzo'}) de {quien} — {_cuando(dias)}"
        clave = f"ev:{e['id']}:{e['proxima']}:{u}"
        if u is not None and dias <= 14 and not db.ya_avisado(clave):
            lineas.append(texto)
            claves.append(clave)
    for c in db.filas("SELECT * FROM cuentas WHERE activa=1 AND cupo>0 AND deuda IS NOT NULL"):
        uso = c["deuda"] / c["cupo"]
        clave = f"cupo:{c['id']}:{round(c['deuda'])}"
        if uso >= 0.9 and not db.ya_avisado(clave):
            lineas.append(f"⚠️ {c['nombre']} va en el {round(uso * 100)}% del cupo ({pesos(c['deuda'])} de {pesos(c['cupo'])})")
            claves.append(clave)
    ayer = (hoy - timedelta(days=1)).isoformat()
    semana = (hoy - timedelta(days=8)).isoformat()
    if db.fila("SELECT 1 AS x FROM leche WHERE fecha>=?", (semana,)) and not db.fila("SELECT 1 AS x FROM leche WHERE fecha=?", (ayer,)):
        clave = f"leche:{ayer}"
        if not db.ya_avisado(clave):
            lineas.append(f"🥛 No tengo los litros de leche de ayer ({ayer}). ¿Cuántos fueron?")
            claves.append(clave)
    for clave in claves:
        db.marcar_avisado(clave)
    if not lineas:
        return "", []
    return "☀️ *Buenos días. Para tener en cuenta:*\n\n" + "\n".join(lineas), botones


def informe_mensual():
    """El día 1: resumen del mes anterior. Devuelve (texto, desde, hasta) o None si ya se envió."""
    hoy = db.hoy()
    if hoy.day != 1:
        return None
    fin = hoy - timedelta(days=1)
    inicio = fin.replace(day=1)
    clave = f"mes:{inicio.isoformat()[:7]}"
    if db.ya_avisado(clave):
        return None
    db.marcar_avisado(clave)
    texto = texto_resumen(inicio.isoformat(), fin.isoformat()).replace("📊 *Resumen", f"📆 *Cierre de {MESES[inicio.month]}:", 1)
    return texto, inicio.isoformat(), fin.isoformat()
