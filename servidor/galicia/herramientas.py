"""Lo que el asistente sabe hacer: cada función es una herramienta que la IA puede usar.

Todas reciben ctx = {"usuario": "Carlos", "chat": 123, "archivos": []} y devuelven un dict
que la IA lee para contestar. Si algo falta o está mal, devuelven {"error": "..."} y la IA pregunta.
"""
import difflib
from datetime import date, timedelta

from . import config, db

HERRAMIENTAS: dict = {}       # nombre → (función, esquema)


def herramienta(texto_ayuda: str, /, **parametros):
    """Registra una función como herramienta. parametros: nombre=(tipo, descripción[, enum]) ; '*' = obligatorio."""
    def deco(fn):
        props, requeridos = {}, []
        for nombre, spec in parametros.items():
            tipo, desc, *resto = spec
            if tipo.endswith("*"):
                tipo = tipo[:-1]
                requeridos.append(nombre)
            props[nombre] = {"type": tipo, "description": desc}
            if resto:
                props[nombre]["enum"] = resto[0]
        HERRAMIENTAS[fn.__name__] = (fn, {"type": "function", "function": {
            "name": fn.__name__, "description": texto_ayuda,
            "parameters": {"type": "object", "properties": props, "required": requeridos}}})
        return fn
    return deco


def esquemas() -> list:
    return [e for _, e in HERRAMIENTAS.values()]


def ejecutar(nombre: str, argumentos: dict, ctx: dict) -> dict:
    if nombre not in HERRAMIENTAS:
        return {"error": f"no existe la herramienta {nombre}"}
    fn = HERRAMIENTAS[nombre][0]
    try:
        return fn(ctx, **{k: v for k, v in (argumentos or {}).items() if v not in (None, "")})
    except (ValueError, TypeError, KeyError) as e:
        return {"error": str(e)}


# ---------------- Ayudas ----------------
def pesos(valor) -> str:
    return "$" + f"{round(valor or 0):,}".replace(",", ".")


def monto(valor) -> float:
    """350000, "350.000", "$ 350.000,50", "350 mil", "1,2 millones" → número."""
    if isinstance(valor, (int, float)):
        return float(valor)
    t = db.normal(valor).replace("$", "").replace("cop", "").strip()
    mult = 1
    if "millon" in t:
        mult, t = 1_000_000, t.split("millon")[0]
    elif "mil" in t:
        mult, t = 1_000, t.split("mil")[0]
    t = t.strip().replace(" ", "")
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".")
    elif "," in t:
        t = t.replace(",", ".") if mult > 1 or len(t.split(",")[-1]) != 3 else t.replace(",", "")
    elif t.count(".") >= 1 and (mult == 1 and len(t.split(".")[-1]) == 3):
        t = t.replace(".", "")
    return float(t) * mult


def _positivo(valor, nombre="monto") -> float:
    v = monto(valor)
    if v <= 0:
        raise ValueError(f"el {nombre} debe ser mayor que cero")
    return v


def _categoria(valor: str, tipo: str) -> str:
    opciones = config.CATEGORIAS_INGRESO if tipo == "ingreso" else config.CATEGORIAS_GASTO
    if not valor:
        return "Otros ingresos" if tipo == "ingreso" else "Otros"
    por_normal = {db.normal(o): o for o in opciones}
    if db.normal(valor) in por_normal:
        return por_normal[db.normal(valor)]
    contiene = [o for n, o in por_normal.items() if db.normal(valor) in n]       # «jornales» → «Jornales y mano de obra»
    if len(contiene) == 1:
        return contiene[0]
    cerca = difflib.get_close_matches(db.normal(valor), list(por_normal), n=1, cutoff=0.6)
    return por_normal[cerca[0]] if cerca else valor.strip().capitalize()


def _ambito(valor: str) -> str:
    return "personal" if db.normal(valor).startswith(("pers", "casa", "hogar", "famil")) else "hacienda"


def _actividad(valor: str) -> str:
    v = db.normal(valor)
    for a in config.ACTIVIDADES:
        if v.startswith(a[:4]):
            return a
    if v.startswith(("vaca", "bovin", "anim", "potr")):
        return "ganado"
    return "general"


def _lote(ref):
    if ref in (None, ""):
        return None
    l = db.buscar("lotes", ref)
    if not l:
        raise ValueError(f"no encuentro el lote «{ref}». Lotes: {', '.join(x['nombre'] for x in db.filas('SELECT nombre FROM lotes')) or 'ninguno registrado'}")
    return l


def _cuenta(ref):
    if ref in (None, ""):
        return None
    c = db.buscar("cuentas", ref, campos=("nombre", "banco", "ultimos4", "titular"))
    if not c:
        raise ValueError(f"no encuentro la tarjeta o cuenta «{ref}». Registradas: "
                         f"{', '.join(x['nombre'] for x in db.filas('SELECT nombre FROM cuentas')) or 'ninguna'}")
    return c


def _animal(ref):
    a = db.buscar("animales", ref, campos=("codigo", "nombre"))
    if not a:
        raise ValueError(f"no encuentro el animal «{ref}». Regístralo primero con su número o nombre.")
    return a


def nuevo_movimiento(acc: db.Accion, **d) -> int:
    tipo = "ingreso" if db.normal(d.get("tipo")) .startswith("ing") else "gasto"
    datos = {
        "fecha": db.fecha(d.get("fecha")), "tipo": tipo, "monto": _positivo(d.get("monto")),
        "categoria": _categoria(d.get("categoria", ""), tipo), "ambito": _ambito(d.get("ambito", "hacienda")),
        "actividad": _actividad(d.get("actividad", "general")), "lote_id": d.get("lote_id"),
        "cuenta_id": d.get("cuenta_id"), "tercero": d.get("tercero", ""), "nit": d.get("nit", ""),
        "factura": d.get("factura", ""), "cufe": d.get("cufe", ""), "descripcion": d.get("descripcion", ""),
        "soporte": d.get("soporte", ""), "origen": d.get("origen", "chat"), "usuario": acc.usuario,
    }
    if datos["ambito"] == "personal":
        datos["actividad"] = "general"
    return acc.insertar("movimientos", datos)


def _cerrar(ctx: dict, acc: db.Accion, resultado: dict) -> dict:
    accion = acc.guardar()
    if accion:
        ctx.setdefault("acciones", []).append(accion)
    return resultado


# ================= Dinero =================
@herramienta("Registra un gasto o un ingreso. Úsala para compras, pagos de jornales, ventas, etc. "
             "No la uses para pagar una tarjeta o cuota ya registrada (para eso: pagar_obligacion).",
             tipo=("string*", "gasto o ingreso", ["gasto", "ingreso"]),
             monto=("number*", "valor en pesos colombianos, sin puntos (350 mil = 350000)"),
             descripcion=("string*", "qué fue, corto: «3 bultos de abono 15-15-15»"),
             categoria=("string", "categoría (ver lista del sistema)"),
             ambito=("string", "hacienda o personal (gastos de la casa/familia = personal)", ["hacienda", "personal"]),
             actividad=("string", "a qué actividad de la hacienda pertenece", config.ACTIVIDADES),
             fecha=("string", "AAAA-MM-DD; vacío = hoy"),
             cuenta=("string", "con qué tarjeta o cuenta se pagó (nombre); vacío = efectivo"),
             tercero=("string", "proveedor, trabajador o comprador"),
             lote=("string", "lote de papa al que se carga el gasto, si aplica"))
def registrar_movimiento(ctx, tipo, monto, descripcion, categoria="", ambito="hacienda", actividad="general",
                         fecha=None, cuenta=None, tercero="", lote=None):
    l, c = _lote(lote), _cuenta(cuenta)
    if l:
        actividad = "papa"
    acc = db.Accion(ctx["usuario"], f"{tipo} {pesos(globals()['monto'](monto))} {descripcion}")
    id_ = nuevo_movimiento(acc, tipo=tipo, monto=monto, descripcion=descripcion, categoria=categoria, ambito=ambito,
                           actividad=actividad, fecha=fecha, cuenta_id=c and c["id"], tercero=tercero,
                           lote_id=l and l["id"], origen=ctx.get("origen", "chat"))
    m = db.fila("SELECT * FROM movimientos WHERE id=?", (id_,))
    return _cerrar(ctx, acc, {"ok": True, "registrado": m})


@herramienta("Busca movimientos ya registrados (para responder «¿cuánto pagamos al veterinario?» o revisar algo).",
             texto=("string", "palabra a buscar en descripción, proveedor o categoría"),
             desde=("string", "AAAA-MM-DD"), hasta=("string", "AAAA-MM-DD"),
             tipo=("string", "gasto o ingreso", ["gasto", "ingreso"]), limite=("integer", "máximo de filas (defecto 15)"))
def buscar_movimientos(ctx, texto="", desde=None, hasta=None, tipo=None, limite=15):
    sql, args = "SELECT m.*, c.nombre AS cuenta, l.nombre AS lote FROM movimientos m LEFT JOIN cuentas c ON c.id=m.cuenta_id " \
                "LEFT JOIN lotes l ON l.id=m.lote_id WHERE m.fecha BETWEEN ? AND ?", \
        [db.fecha(desde, date(2000, 1, 1)), db.fecha(hasta, date(2100, 1, 1))]
    if tipo:
        sql += " AND m.tipo=?"
        args.append(tipo)
    todas = db.filas(sql + " ORDER BY m.fecha DESC, m.id DESC", args)
    if texto:
        t = db.normal(texto)
        todas = [m for m in todas if t in db.normal(f"{m['descripcion']} {m['tercero']} {m['categoria']} {m['actividad']} {m['cuenta'] or ''} {m['lote'] or ''}")]
    total = sum(m["monto"] for m in todas)
    return {"encontrados": len(todas), "total": total, "total_texto": pesos(total),
            "movimientos": [{k: m[k] for k in ("id", "fecha", "tipo", "monto", "descripcion", "categoria", "ambito",
                                               "actividad", "tercero", "cuenta", "lote")} for m in todas[:int(limite)]]}


@herramienta("Resumen de ingresos y gastos de un periodo, separado por hacienda/personal, actividad y categoría.",
             desde=("string", "AAAA-MM-DD; vacío = primer día del mes actual"), hasta=("string", "AAAA-MM-DD; vacío = hoy"),
             ambito=("string", "solo hacienda o solo personal", ["hacienda", "personal"]),
             actividad=("string", "solo una actividad", config.ACTIVIDADES))
def resumen(ctx, desde=None, hasta=None, ambito=None, actividad=None):
    return calcular_resumen(db.fecha(desde, db.hoy().replace(day=1)), db.fecha(hasta), ambito, actividad)


def calcular_resumen(desde: str, hasta: str, ambito=None, actividad=None) -> dict:
    sql, args = "SELECT * FROM movimientos WHERE fecha BETWEEN ? AND ?", [desde, hasta]
    if ambito:
        sql += " AND ambito=?"
        args.append(_ambito(ambito))
    if actividad:
        sql += " AND actividad=?"
        args.append(_actividad(actividad))
    movs = db.filas(sql, args)
    ingresos = sum(m["monto"] for m in movs if m["tipo"] == "ingreso")
    gastos = sum(m["monto"] for m in movs if m["tipo"] == "gasto")
    por = lambda campo, tipo: {k: sum(m["monto"] for m in movs if m["tipo"] == tipo and m[campo] == k)  # noqa: E731
                               for k in sorted({m[campo] for m in movs if m["tipo"] == tipo})}
    return {"desde": desde, "hasta": hasta, "ingresos": ingresos, "gastos": gastos, "resultado": ingresos - gastos,
            "texto": {"ingresos": pesos(ingresos), "gastos": pesos(gastos), "resultado": pesos(ingresos - gastos)},
            "gastos_hacienda": sum(m["monto"] for m in movs if m["tipo"] == "gasto" and m["ambito"] == "hacienda"),
            "gastos_personales": sum(m["monto"] for m in movs if m["tipo"] == "gasto" and m["ambito"] == "personal"),
            "gastos_por_actividad": por("actividad", "gasto"), "ingresos_por_actividad": por("actividad", "ingreso"),
            "gastos_por_categoria": por("categoria", "gasto"), "movimientos": len(movs)}


# ================= Tarjetas, créditos y vencimientos =================
def _proxima_fecha_dia(dia: int, desde: date = None) -> str:
    d = desde or db.hoy()
    for meses in (0, 1):
        base = db.sumar_meses(d.replace(day=1), meses)
        ultimo_dia = (db.sumar_meses(base, 1) - timedelta(days=1)).day
        f = base.replace(day=min(max(1, dia), ultimo_dia))
        if f >= d:
            return f.isoformat()
    return d.isoformat()


@herramienta("Registra una tarjeta de crédito, cuenta bancaria o crédito. Si tiene día de pago, el asistente "
             "avisará cada mes antes de esa fecha.",
             nombre=("string*", "cómo la llaman: «Visa Bancolombia de Carlos», «Mastercard Agrario»"),
             tipo=("string", "tarjeta, cuenta, credito o efectivo", ["tarjeta", "cuenta", "credito", "efectivo"]),
             banco=("string", "Bancolombia, Banco Agrario, Davivienda..."), ultimos4=("string", "últimos 4 números"),
             titular=("string", "a nombre de quién"), cupo=("number", "cupo total en pesos"),
             dia_corte=("integer", "día del mes del corte"), dia_pago=("integer", "día del mes límite de pago"))
def registrar_cuenta(ctx, nombre, tipo="tarjeta", banco="", ultimos4="", titular="", cupo=None, dia_corte=None, dia_pago=None):
    acc = db.Accion(ctx["usuario"], f"tarjeta/cuenta {nombre}")
    id_ = acc.insertar("cuentas", {"nombre": nombre.strip(), "tipo": tipo, "banco": banco, "ultimos4": str(ultimos4)[-4:],
                                   "titular": titular, "cupo": monto(cupo) if cupo else None,
                                   "dia_corte": int(dia_corte) if dia_corte else None,
                                   "dia_pago": int(dia_pago) if dia_pago else None})
    extra = {}
    if dia_pago and tipo == "tarjeta":
        fecha = _proxima_fecha_dia(int(dia_pago))
        acc.insertar("obligaciones", {"nombre": f"Pago {nombre.strip()}", "tipo": "tarjeta", "cuenta_id": id_,
                                      "fecha": fecha, "frecuencia": "mensual"})
        extra["proximo_pago"] = fecha
    return _cerrar(ctx, acc, {"ok": True, "id": id_, **extra})


@herramienta("Registra algo que hay que pagar o renovar en una fecha: cuota de crédito (Banco Agrario/Finagro), compra "
             "a cuotas, impuesto predial, SOAT, seguro, servicio, arriendo. El asistente avisará antes de que venza.",
             nombre=("string*", "qué es: «Crédito Finagro tractor», «Predial 2027», «SOAT camioneta»"),
             fecha=("string*", "próximo vencimiento AAAA-MM-DD"),
             monto=("number", "valor de la cuota o pago, si se sabe"),
             frecuencia=("string", "cada cuánto se repite", ["unica", "mensual", "bimestral", "trimestral", "semestral", "anual"]),
             tipo=("string", "clase", ["cuota", "credito", "tarjeta", "impuesto", "seguro", "servicio", "otro"]),
             cuenta=("string", "tarjeta o cuenta con la que se relaciona"),
             cuotas_total=("integer", "número total de cuotas"), cuotas_pagadas=("integer", "cuántas ya se pagaron"),
             saldo=("number", "saldo pendiente de la deuda"), notas=("string", "detalles"))
def registrar_obligacion(ctx, nombre, fecha, monto=None, frecuencia="mensual", tipo="cuota", cuenta=None,
                         cuotas_total=None, cuotas_pagadas=0, saldo=None, notas=""):
    c = _cuenta(cuenta)
    acc = db.Accion(ctx["usuario"], f"vencimiento {nombre}")
    id_ = acc.insertar("obligaciones", {
        "nombre": nombre.strip(), "fecha": db.fecha(fecha), "monto": globals()["monto"](monto) if monto else None,
        "frecuencia": frecuencia, "tipo": tipo, "cuenta_id": c and c["id"],
        "cuotas_total": int(cuotas_total) if cuotas_total else None, "cuotas_pagadas": int(cuotas_pagadas or 0),
        "saldo": globals()["monto"](saldo) if saldo else None, "notas": notas})
    return _cerrar(ctx, acc, {"ok": True, "id": id_, "obligacion": db.fila("SELECT * FROM obligaciones WHERE id=?", (id_,))})


CATEGORIA_OBLIGACION = {"impuesto": "Impuestos", "servicio": "Servicios públicos", "seguro": "Vehículos"}


@herramienta("Marca como pagada una tarjeta, cuota o vencimiento ya registrado y pasa a la siguiente fecha. "
             "El pago de tarjeta NO se cuenta como gasto (las compras ya son los gastos); los demás pagos sí.",
             obligacion=("string*", "nombre o número del vencimiento"), monto=("number", "valor pagado; vacío = el de la cuota"),
             fecha=("string", "AAAA-MM-DD; vacío = hoy"), cuenta=("string", "desde qué cuenta se pagó"),
             ambito=("string", "hacienda o personal", ["hacienda", "personal"]))
def pagar_obligacion(ctx, obligacion, monto=None, fecha=None, cuenta=None, ambito="hacienda"):
    o = db.buscar("obligaciones", obligacion, extra="WHERE activa=1")
    if not o:
        raise ValueError(f"no encuentro un vencimiento activo llamado «{obligacion}»")
    valor = globals()["monto"](monto) if monto else (o["monto"] or 0)
    if valor <= 0:
        raise ValueError(f"¿cuánto se pagó de «{o['nombre']}»? No tengo el valor de la cuota")
    c = _cuenta(cuenta)
    acc = db.Accion(ctx["usuario"], f"pago {o['nombre']} {pesos(valor)}")
    mov = None
    if o["tipo"] != "tarjeta":
        mov = nuevo_movimiento(acc, tipo="gasto", monto=valor, descripcion=f"Pago {o['nombre']}",
                               categoria=CATEGORIA_OBLIGACION.get(o["tipo"], "Créditos y tarjetas"), ambito=ambito,
                               fecha=fecha, cuenta_id=c and c["id"])
    acc.insertar("pagos", {"obligacion_id": o["id"], "fecha": db.fecha(fecha), "monto": valor, "movimiento_id": mov})
    pagadas = (o["cuotas_pagadas"] or 0) + 1
    cambios = {"cuotas_pagadas": pagadas}
    if o["saldo"]:
        cambios["saldo"] = max(0, o["saldo"] - valor)
    termina = o["frecuencia"] == "unica" or (o["cuotas_total"] and pagadas >= o["cuotas_total"]) or cambios.get("saldo") == 0
    if termina:
        cambios["activa"] = 0
    else:
        cambios["fecha"] = db.siguiente_fecha(o["fecha"], o["frecuencia"])
    acc.actualizar("obligaciones", o["id"], cambios)
    return _cerrar(ctx, acc, {"ok": True, "pagado": pesos(valor), "terminada": bool(termina),
                              "proximo_vencimiento": cambios.get("fecha"), "contado_como_gasto": mov is not None,
                              "cuotas": f"{pagadas} de {o['cuotas_total']}" if o["cuotas_total"] else None})


@herramienta("Lista lo que vence pronto (pagos, cuotas, impuestos) y lo vencido, más labores y eventos del ganado próximos.",
             dias=("integer", "cuántos días hacia adelante (defecto 30)"))
def ver_vencimientos(ctx, dias=30):
    return proximos(int(dias))


def proximos(dias: int = 30) -> dict:
    hoy = db.hoy()
    limite = (hoy + timedelta(days=dias)).isoformat()
    obligaciones = db.filas("SELECT o.*, c.nombre AS cuenta FROM obligaciones o LEFT JOIN cuentas c ON c.id=o.cuenta_id "
                            "WHERE o.activa=1 AND o.fecha<=? ORDER BY o.fecha", (limite,))
    for o in obligaciones:
        o["dias"] = (date.fromisoformat(o["fecha"]) - hoy).days
    labores = db.filas("SELECT lb.*, l.nombre AS lote FROM labores lb LEFT JOIN lotes l ON l.id=lb.lote_id "
                       "WHERE lb.proxima BETWEEN ? AND ? ORDER BY lb.proxima", ((hoy - timedelta(days=3)).isoformat(), limite))
    eventos = db.filas("SELECT e.*, a.codigo, a.nombre FROM eventos e LEFT JOIN animales a ON a.id=e.animal_id "
                       "WHERE e.proxima BETWEEN ? AND ? AND (a.estado IS NULL OR a.estado='activo') ORDER BY e.proxima",
                       ((hoy - timedelta(days=3)).isoformat(), limite))
    return {"hoy": hoy.isoformat(), "pagos": obligaciones, "labores": labores, "ganado": eventos,
            "total_pagos": pesos(sum(o["monto"] or 0 for o in obligaciones))}


@herramienta("Muestra las tarjetas y cuentas con su cupo, deuda, compras a cuotas (diferidos) y próximo pago.")
def ver_cuentas(ctx):
    cuentas = db.filas("SELECT * FROM cuentas WHERE activa=1 ORDER BY banco, nombre")
    for c in cuentas:
        c["diferidos"] = db.filas("SELECT descripcion, valor_cuota, cuota_actual, cuotas_total, saldo FROM diferidos "
                                  "WHERE cuenta_id=?", (c["id"],))
        c["proximos_pagos"] = db.filas("SELECT id, nombre, fecha, monto, monto_minimo FROM obligaciones "
                                       "WHERE cuenta_id=? AND activa=1 ORDER BY fecha", (c["id"],))
        if c["cupo"] and c["deuda"] is not None:
            c["uso_cupo"] = f"{round(100 * c['deuda'] / c['cupo'])}%"
    otras = db.filas("SELECT * FROM obligaciones WHERE activa=1 AND cuenta_id IS NULL ORDER BY fecha")
    return {"cuentas": cuentas, "otros_vencimientos": otras}


# ================= Papa =================
@herramienta("Registra un lote de papa (una siembra).",
             nombre=("string*", "nombre del lote: «Lote 1», «El Alto»"), hectareas=("number", "área en hectáreas"),
             variedad=("string", "Pastusa, Única, Criolla, Diacol Capiro..."), fecha_siembra=("string", "AAAA-MM-DD"),
             notas=("string", "detalles"))
def registrar_lote(ctx, nombre, hectareas=None, variedad="", fecha_siembra=None, notas=""):
    acc = db.Accion(ctx["usuario"], f"lote {nombre}")
    id_ = acc.insertar("lotes", {"nombre": nombre.strip(), "hectareas": float(hectareas) if hectareas else None,
                                 "variedad": variedad, "fecha_siembra": db.fecha(fecha_siembra) if fecha_siembra else None,
                                 "notas": notas})
    return _cerrar(ctx, acc, {"ok": True, "id": id_})


@herramienta("Registra una labor en un lote de papa: siembra, fertilización, fumigación, aporque, desyerba, riego... "
             "Si dice cuándo toca la próxima (ej. fumigar cada 8 días), ponla en «proxima» y el asistente avisará.",
             lote=("string*", "nombre del lote"), tipo=("string*", "fumigación, fertilización, aporque, desyerba, siembra..."),
             fecha=("string", "AAAA-MM-DD; vacío = hoy"), producto=("string", "producto usado"),
             cantidad=("string", "cantidad con unidad: «3 bultos», «2 litros»"),
             costo=("number", "costo de la labor en pesos (insumos + jornales)"),
             pagado_ahora=("boolean", "true si ese costo es una compra/pago nuevo que también hay que registrar como gasto"),
             proxima=("string", "fecha AAAA-MM-DD de la próxima vez que toca esta labor"),
             notas=("string", "detalles"))
def registrar_labor(ctx, lote, tipo, fecha=None, producto="", cantidad="", costo=None, pagado_ahora=False, proxima=None, notas=""):
    l = _lote(lote)
    acc = db.Accion(ctx["usuario"], f"labor {tipo} en {l['nombre']}")
    mov = None
    if costo and pagado_ahora:
        mov = nuevo_movimiento(acc, tipo="gasto", monto=costo, descripcion=f"{tipo} {producto} {l['nombre']}".strip(),
                               categoria="Jornales y mano de obra" if "jornal" in db.normal(f"{tipo} {producto}") else "Insumos agrícolas",
                               actividad="papa", lote_id=l["id"], fecha=fecha)
    id_ = acc.insertar("labores", {"lote_id": l["id"], "fecha": db.fecha(fecha), "tipo": tipo, "producto": producto,
                                   "cantidad": str(cantidad or ""), "costo": monto(costo) if costo else None,
                                   "movimiento_id": mov, "proxima": db.fecha(proxima) if proxima else None, "notas": notas})
    return _cerrar(ctx, acc, {"ok": True, "id": id_, "gasto_registrado": mov is not None})


@herramienta("Registra una cosecha o venta de papa de un lote. Si trae precio, también queda el ingreso.",
             lote=("string*", "nombre del lote"), bultos=("number*", "bultos cosechados"),
             precio_bulto=("number", "precio de venta por bulto"), comprador=("string", "a quién se vendió"),
             fecha=("string", "AAAA-MM-DD; vacío = hoy"),
             final=("boolean", "true si con esto se terminó de cosechar el lote"), notas=("string", "detalles"))
def registrar_cosecha(ctx, lote, bultos, precio_bulto=None, comprador="", fecha=None, final=False, notas=""):
    l = _lote(lote)
    acc = db.Accion(ctx["usuario"], f"cosecha {bultos} bultos {l['nombre']}")
    mov = None
    if precio_bulto:
        mov = nuevo_movimiento(acc, tipo="ingreso", monto=float(bultos) * monto(precio_bulto), categoria="Venta de papa",
                               descripcion=f"{bultos} bultos de papa {l['nombre']}", actividad="papa",
                               lote_id=l["id"], tercero=comprador, fecha=fecha)
    acc.insertar("cosechas", {"lote_id": l["id"], "fecha": db.fecha(fecha), "bultos": float(bultos),
                              "precio_bulto": monto(precio_bulto) if precio_bulto else None, "comprador": comprador,
                              "movimiento_id": mov, "notas": notas})
    if final:
        acc.actualizar("lotes", l["id"], {"estado": "cosechado"})
    return _cerrar(ctx, acc, {"ok": True, "ingreso": pesos(float(bultos) * monto(precio_bulto)) if precio_bulto else None})


@herramienta("Estado y rentabilidad de los lotes de papa: costos, bultos, ingresos, costo por bulto y por hectárea.",
             lote=("string", "un lote en particular; vacío = todos"))
def estado_lotes(ctx, lote=None):
    lotes = [_lote(lote)] if lote else db.filas("SELECT * FROM lotes ORDER BY estado, id DESC")
    return {"lotes": [rentabilidad_lote(l) for l in lotes]}


def rentabilidad_lote(l: dict) -> dict:
    gastos = db.fila("SELECT COALESCE(SUM(monto),0) AS t FROM movimientos WHERE lote_id=? AND tipo='gasto'", (l["id"],))["t"]
    labores_sin_gasto = db.fila("SELECT COALESCE(SUM(costo),0) AS t FROM labores WHERE lote_id=? AND movimiento_id IS NULL",
                                (l["id"],))["t"]
    ingresos = db.fila("SELECT COALESCE(SUM(monto),0) AS t FROM movimientos WHERE lote_id=? AND tipo='ingreso'", (l["id"],))["t"]
    bultos = db.fila("SELECT COALESCE(SUM(bultos),0) AS t FROM cosechas WHERE lote_id=?", (l["id"],))["t"]
    costo = gastos + labores_sin_gasto
    ultima = db.fila("SELECT tipo, fecha, proxima FROM labores WHERE lote_id=? ORDER BY fecha DESC, id DESC LIMIT 1", (l["id"],))
    dias = (db.hoy() - date.fromisoformat(l["fecha_siembra"])).days if l["fecha_siembra"] else None
    return {"lote": l["nombre"], "estado": l["estado"], "variedad": l["variedad"], "hectareas": l["hectareas"],
            "fecha_siembra": l["fecha_siembra"], "dias_desde_siembra": dias, "costo_total": costo,
            "ingresos": ingresos, "utilidad": ingresos - costo, "bultos": bultos,
            "costo_por_bulto": round(costo / bultos) if bultos else None,
            "costo_por_hectarea": round(costo / l["hectareas"]) if l["hectareas"] else None, "ultima_labor": ultima}


# ================= Leche =================
@herramienta("Registra los litros de leche de un día.",
             litros=("number*", "litros del día (sumando ordeños)"), fecha=("string", "AAAA-MM-DD; vacío = hoy"),
             vacas=("integer", "vacas en ordeño"), notas=("string", "detalles"))
def registrar_leche(ctx, litros, fecha=None, vacas=None, notas=""):
    f = db.fecha(fecha)
    acc = db.Accion(ctx["usuario"], f"leche {litros} L {f}")
    acc.insertar("leche", {"fecha": f, "litros": float(litros), "vacas": int(vacas) if vacas else None, "notas": notas})
    total_dia = db.fila("SELECT SUM(litros) AS t FROM leche WHERE fecha=?", (f,))["t"]
    return _cerrar(ctx, acc, {"ok": True, "litros_del_dia": total_dia})


@herramienta("Registra lo que pagó el comprador de leche por un periodo (quincena) y lo compara con los litros anotados.",
             neto=("number*", "valor neto recibido en pesos"), desde=("string*", "inicio del periodo AAAA-MM-DD"),
             hasta=("string*", "fin del periodo AAAA-MM-DD"), litros=("number", "litros que reconoce el comprador"),
             precio_litro=("number", "precio por litro"), descuentos=("number", "descuentos (transporte, cuota, etc.)"),
             comprador=("string", "quién compra la leche"), fecha_pago=("string", "cuándo se recibió el pago"))
def registrar_pago_leche(ctx, neto, desde, hasta, litros=None, precio_litro=None, descuentos=None, comprador="", fecha_pago=None):
    d, h = db.fecha(desde), db.fecha(hasta)
    acc = db.Accion(ctx["usuario"], f"pago leche {d} a {h}")
    mov = nuevo_movimiento(acc, tipo="ingreso", monto=neto, categoria="Venta de leche", actividad="leche",
                           descripcion=f"Leche {d} a {h}", tercero=comprador, fecha=fecha_pago or h)
    acc.insertar("liquidaciones_leche", {"desde": d, "hasta": h, "litros": float(litros) if litros else None,
                                         "precio_litro": monto(precio_litro) if precio_litro else None,
                                         "descuentos": monto(descuentos) if descuentos else None, "neto": monto(neto),
                                         "comprador": comprador, "movimiento_id": mov})
    anotados = db.fila("SELECT COALESCE(SUM(litros),0) AS t FROM leche WHERE fecha BETWEEN ? AND ?", (d, h))["t"]
    r = {"ok": True, "litros_anotados_en_finca": anotados}
    if litros and anotados:
        r["diferencia_litros"] = round(anotados - float(litros), 1)
    return _cerrar(ctx, acc, r)


@herramienta("Resumen de la leche: litros por día, promedio, pagos recibidos y precio promedio.",
             desde=("string", "AAAA-MM-DD; vacío = hace 30 días"), hasta=("string", "AAAA-MM-DD; vacío = hoy"))
def resumen_leche(ctx, desde=None, hasta=None):
    d, h = db.fecha(desde, db.hoy() - timedelta(days=30)), db.fecha(hasta)
    dias = db.filas("SELECT fecha, SUM(litros) AS litros FROM leche WHERE fecha BETWEEN ? AND ? GROUP BY fecha ORDER BY fecha", (d, h))
    total = sum(x["litros"] for x in dias)
    pagos = db.filas("SELECT * FROM liquidaciones_leche WHERE hasta>=? AND desde<=? ORDER BY desde", (d, h))
    return {"desde": d, "hasta": h, "dias_con_registro": len(dias), "litros_total": total,
            "promedio_diario": round(total / len(dias), 1) if dias else 0, "ultimos_dias": dias[-10:],
            "pagos": pagos, "recibido": pesos(sum(p["neto"] or 0 for p in pagos))}


# ================= Ganado =================
@herramienta("Registra un animal (vaca, novilla, ternero, toro...). Si se compró, con precio_compra queda el gasto.",
             codigo=("string*", "número o marca del animal"), nombre=("string", "nombre"),
             sexo=("string", "hembra o macho", ["hembra", "macho"]),
             categoria=("string", "vaca, novilla, ternera, ternero, toro, torete..."), raza=("string", "raza"),
             nacimiento=("string", "AAAA-MM-DD"), madre=("string", "código de la madre"),
             precio_compra=("number", "si se compró: valor"), notas=("string", "detalles"))
def registrar_animal(ctx, codigo, nombre="", sexo="", categoria="", raza="", nacimiento=None, madre="", precio_compra=None, notas=""):
    if db.fila("SELECT id FROM animales WHERE codigo=? AND estado='activo'", (str(codigo).strip(),)):
        raise ValueError(f"ya hay un animal activo con el código {codigo}")
    acc = db.Accion(ctx["usuario"], f"animal {codigo}")
    id_ = acc.insertar("animales", {"codigo": str(codigo).strip(), "nombre": nombre, "sexo": sexo, "categoria": categoria,
                                    "raza": raza, "nacimiento": db.fecha(nacimiento) if nacimiento else None,
                                    "madre": madre, "notas": notas})
    if precio_compra:
        mov = nuevo_movimiento(acc, tipo="gasto", monto=precio_compra, categoria="Compra de animales", actividad="ganado",
                               descripcion=f"Compra {categoria or 'animal'} {codigo}")
        acc.insertar("eventos", {"animal_id": id_, "fecha": db.fecha(None), "tipo": "compra", "valor": monto(precio_compra),
                                 "movimiento_id": mov})
    return _cerrar(ctx, acc, {"ok": True, "id": id_})


TIPOS_EVENTO = ["vacuna", "servicio", "parto", "pesaje", "tratamiento", "secado", "venta", "muerte", "otro"]


@herramienta("Registra un evento de un animal o de todo el hato: vacuna, servicio/inseminación (calcula el parto "
             "esperado a 283 días), parto, pesaje, tratamiento, secado, venta (con valor = ingreso), muerte.",
             animal=("string*", "código o nombre del animal; «hato» si fue para todos (ej. vacunación de aftosa)"),
             tipo=("string*", "tipo de evento", TIPOS_EVENTO), fecha=("string", "AAAA-MM-DD; vacío = hoy"),
             detalle=("string", "producto, peso, sexo de la cría, comprador..."),
             valor=("number", "costo (vacuna/tratamiento) o precio de venta"),
             proxima=("string", "AAAA-MM-DD de la próxima dosis o revisión"))
def evento_animal(ctx, animal, tipo, fecha=None, detalle="", valor=None, proxima=None):
    tipo = db.normal(tipo)
    tipo = "servicio" if tipo.startswith(("insem", "monta", "serv")) else tipo
    hato = db.normal(animal) in ("hato", "todos", "todo el hato", "todas", "finca")
    a = None if hato else _animal(animal)
    f = db.fecha(fecha)
    if tipo == "servicio" and not proxima:
        proxima = (date.fromisoformat(f) + timedelta(days=283)).isoformat()
    acc = db.Accion(ctx["usuario"], f"{tipo} {'hato' if hato else a['codigo']}")
    mov = None
    if valor and tipo == "venta" and a:
        mov = nuevo_movimiento(acc, tipo="ingreso", monto=valor, categoria="Venta de ganado", actividad="ganado",
                               descripcion=f"Venta {a['categoria'] or 'animal'} {a['codigo']}", tercero=detalle, fecha=f)
    elif valor and tipo in ("vacuna", "tratamiento"):
        mov = nuevo_movimiento(acc, tipo="gasto", monto=valor, categoria="Veterinario y medicamentos", actividad="ganado",
                               descripcion=f"{tipo} {detalle} {'hato' if hato else a['codigo']}".strip(), fecha=f)
    if a and tipo == "parto":         # el servicio anterior ya no debe avisar
        for e in db.filas("SELECT id FROM eventos WHERE animal_id=? AND tipo='servicio' AND proxima>=?",
                          (a["id"], (date.fromisoformat(f) - timedelta(days=60)).isoformat())):
            acc.actualizar("eventos", e["id"], {"proxima": None})
    acc.insertar("eventos", {"animal_id": a and a["id"], "fecha": f, "tipo": tipo, "detalle": detalle,
                             "valor": monto(valor) if valor else None, "proxima": db.fecha(proxima) if proxima else None,
                             "movimiento_id": mov})
    if a and tipo in ("venta", "muerte"):
        acc.actualizar("animales", a["id"], {"estado": "vendido" if tipo == "venta" else "muerto"})
    return _cerrar(ctx, acc, {"ok": True, "proxima": proxima, "movimiento": mov is not None})


@herramienta("Inventario del ganado: cuántos animales activos por categoría, lista y últimos eventos.",
             animal=("string", "ver la hoja de vida de un solo animal"))
def inventario_ganado(ctx, animal=None):
    if animal:
        a = _animal(animal)
        return {"animal": a, "eventos": db.filas("SELECT fecha, tipo, detalle, valor, proxima FROM eventos WHERE animal_id=? "
                                                  "ORDER BY fecha DESC", (a["id"],))}
    activos = db.filas("SELECT codigo, nombre, sexo, categoria, raza, nacimiento FROM animales WHERE estado='activo' ORDER BY categoria, codigo")
    conteo = {}
    for a in activos:
        conteo[a["categoria"] or "sin categoría"] = conteo.get(a["categoria"] or "sin categoría", 0) + 1
    return {"total": len(activos), "por_categoria": conteo, "animales": activos[:60],
            "ultimos_eventos": db.filas("SELECT e.fecha, e.tipo, e.detalle, a.codigo FROM eventos e LEFT JOIN animales a "
                                        "ON a.id=e.animal_id ORDER BY e.fecha DESC, e.id DESC LIMIT 10")}


# ================= Factura pendiente, Excel y deshacer =================
CAMPOS_PENDIENTE = ("tercero", "nit", "total", "fecha", "factura", "categoria", "ambito", "actividad", "lote", "cuenta", "descripcion")


@herramienta("Corrige la factura que se está revisando (la última foto o archivo enviado, aún sin guardar). "
             "Úsala cuando digan cosas como «el total es 350 mil», «es de ganado», «se pagó con la Visa».",
             tercero=("string", "proveedor"), nit=("string", "NIT"), total=("number", "valor total"),
             fecha=("string", "AAAA-MM-DD"), factura=("string", "número de factura"), categoria=("string", "categoría"),
             ambito=("string", "hacienda o personal", ["hacienda", "personal"]),
             actividad=("string", "actividad", config.ACTIVIDADES), lote=("string", "lote de papa"),
             cuenta=("string", "tarjeta o cuenta con que se pagó"), descripcion=("string", "descripción"),
             guardar=("boolean", "true si además pidieron guardarla ya"))
def ajustar_factura(ctx, guardar=False, **cambios):
    p = db.ultimo_pendiente(ctx["chat"])
    if not p or p["tipo"] != "factura":
        raise ValueError("no hay ninguna factura esperando revisión")
    datos = p["datos"]
    for k, v in cambios.items():
        if k in CAMPOS_PENDIENTE:
            if k == "lote":
                _lote(v)
                datos["actividad"] = "papa"
            if k == "cuenta":
                _cuenta(v)
            datos[k] = monto(v) if k == "total" else v
    db.cambiar_pendiente(p["id"], datos)
    ctx.setdefault("refrescar", []).append(p["id"])
    if guardar:
        from . import documentos
        return documentos.guardar_factura(p["id"], ctx)
    return {"ok": True, "factura": datos, "nota": "la tarjeta de la factura se actualizó; falta tocar Guardar"}


@herramienta("Genera el libro de Excel (movimientos, resumen, tarjetas, papa, ganado, leche) y lo envía por el chat.",
             desde=("string", "AAAA-MM-DD; vacío = 1 de enero del año actual"), hasta=("string", "AAAA-MM-DD; vacío = hoy"))
def exportar_excel(ctx, desde=None, hasta=None):
    from . import excel
    ruta = excel.generar(db.fecha(desde, db.hoy().replace(month=1, day=1)), db.fecha(hasta))
    ctx.setdefault("archivos", []).append(str(ruta))
    return {"ok": True, "archivo": ruta.name, "nota": "el archivo se envía solo al chat"}


@herramienta("Deshace el último registro que hizo esta persona (si se equivocó).")
def deshacer_ultimo(ctx):
    hecho = db.deshacer(usuario=ctx["usuario"])
    return {"ok": bool(hecho), "deshecho": hecho or "no había nada para deshacer"}
