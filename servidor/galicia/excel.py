"""El libro de Excel de la hacienda: se genera desde la base de datos, claro y sencillo, con una hoja por tema."""
from collections import defaultdict

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from . import config, db
from .herramientas import rentabilidad_lote

VERDE = PatternFill("solid", fgColor="2E5E3A")
CLARO = PatternFill("solid", fgColor="EAF2EA")
ROJO = PatternFill("solid", fgColor="F8D7D3")
AMARILLO = PatternFill("solid", fgColor="FFF1C2")
BLANCO = Font(bold=True, color="FFFFFF")
NEGRITA = Font(bold=True)
LINEA = Border(bottom=Side(style="thin", color="C8D3C8"))
PESOS = '"$"#,##0;[Red]-"$"#,##0'
MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
         "Noviembre", "Diciembre"]


def _hoja(libro, titulo: str, encabezados: list, filas: list, dinero: tuple = (), anchos: dict = None, total: tuple = ()):
    h = libro.create_sheet(titulo)
    h.append(encabezados)
    for c in h[1]:
        c.fill, c.font = VERDE, BLANCO
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    h.row_dimensions[1].height = 30
    for f in filas:
        h.append(list(f))
    ultima = h.max_row
    for col in dinero:
        letra = get_column_letter(col)
        for fila in range(2, ultima + 1):
            h[f"{letra}{fila}"].number_format = PESOS
    if total and ultima >= 2:
        h.append([])
        fila_total = ultima + 2
        h.cell(fila_total, 1, "TOTAL").font = NEGRITA
        for col in total:
            letra = get_column_letter(col)
            c = h.cell(fila_total, col, f"=SUM({letra}2:{letra}{ultima})")
            c.number_format, c.font, c.fill = PESOS, NEGRITA, CLARO
    for i, enc in enumerate(encabezados, start=1):
        largo = max([len(str(enc))] + [len(str(f[i - 1])) for f in filas[:300] if i - 1 < len(f) and f[i - 1] is not None])
        h.column_dimensions[get_column_letter(i)].width = (anchos or {}).get(i, min(45, max(10, largo + 2)))
    h.freeze_panes = "A2"
    if filas:
        h.auto_filter.ref = f"A1:{get_column_letter(len(encabezados))}{ultima}"
    return h


def _mes(fecha: str) -> str:
    return f"{MESES[int(fecha[5:7])]} {fecha[:4]}"


def generar(desde: str, hasta: str):
    libro = Workbook()
    portada = libro.active
    portada.title = "Inicio"
    movs = db.filas("SELECT m.*, c.nombre AS cuenta, l.nombre AS lote FROM movimientos m LEFT JOIN cuentas c ON c.id=m.cuenta_id "
                    "LEFT JOIN lotes l ON l.id=m.lote_id WHERE m.fecha BETWEEN ? AND ? ORDER BY m.fecha, m.id", (desde, hasta))

    # ---- Inicio ----
    ingresos = sum(m["monto"] for m in movs if m["tipo"] == "ingreso")
    g_hac = sum(m["monto"] for m in movs if m["tipo"] == "gasto" and m["ambito"] == "hacienda")
    g_per = sum(m["monto"] for m in movs if m["tipo"] == "gasto" and m["ambito"] == "personal")
    portada["A1"] = config.NOMBRE
    portada["A1"].font = Font(bold=True, size=18, color="2E5E3A")
    portada["A2"] = f"Informe del {desde} al {hasta} · generado el {db.hoy().isoformat()}"
    filas = [("Ingresos", ingresos), ("Gastos de la hacienda", g_hac), ("Gastos personales", g_per),
             ("Resultado de la hacienda (ingresos − gastos hacienda)", ingresos - g_hac),
             ("Resultado total (incluye gastos personales)", ingresos - g_hac - g_per)]
    for i, (k, v) in enumerate(filas, start=4):
        portada.cell(i, 1, k).font = NEGRITA
        c = portada.cell(i, 2, v)
        c.number_format = PESOS
        c.fill = CLARO if v >= 0 else ROJO
    portada.cell(10, 1, "Hojas: Resumen mensual · Movimientos · Por categoría · Vencimientos · Tarjetas · "
                        "Papa · Labores · Ganado · Leche")
    portada.column_dimensions["A"].width, portada.column_dimensions["B"].width = 55, 20

    # ---- Resumen mensual ----
    meses = defaultdict(lambda: defaultdict(float))
    for m in movs:
        clave = m["fecha"][:7]
        if m["tipo"] == "ingreso":
            meses[clave][f"i_{m['actividad']}"] += m["monto"]
        elif m["ambito"] == "personal":
            meses[clave]["g_personal"] += m["monto"]
        else:
            meses[clave][f"g_{m['actividad']}"] += m["monto"]
    filas = []
    for clave in sorted(meses):
        x = meses[clave]
        ing = sum(v for k, v in x.items() if k.startswith("i_"))
        gas = sum(v for k, v in x.items() if k.startswith("g_"))
        filas.append([_mes(clave + "-01"), x["i_papa"], x["i_leche"], x["i_ganado"], x["i_general"], ing,
                      x["g_papa"], x["g_ganado"], x["g_leche"], x["g_general"], x["g_personal"], gas, ing - gas])
    _hoja(libro, "Resumen mensual", ["Mes", "Ingreso papa", "Ingreso leche", "Ingreso ganado", "Otros ingresos",
                                     "Total ingresos", "Gasto papa", "Gasto ganado", "Gasto leche", "Gasto general hacienda",
                                     "Gastos personales", "Total gastos", "Resultado"],
          filas, dinero=tuple(range(2, 14)), total=tuple(range(2, 14)))

    # ---- Movimientos ----
    filas = [[m["fecha"], m["tipo"].capitalize(), m["monto"] if m["tipo"] == "ingreso" else -m["monto"], m["categoria"],
              "Personal" if m["ambito"] == "personal" else "Hacienda", m["actividad"].capitalize(), m["lote"] or "",
              m["cuenta"] or "Efectivo", m["tercero"], m["nit"], m["factura"], m["descripcion"], m["usuario"], m["origen"]]
             for m in movs]
    h = _hoja(libro, "Movimientos", ["Fecha", "Tipo", "Valor", "Categoría", "Hacienda / Personal", "Actividad", "Lote",
                                     "Tarjeta / cuenta", "Proveedor / cliente", "NIT", "N.º factura", "Descripción",
                                     "Registró", "Origen"], filas, dinero=(3,), anchos={12: 40}, total=(3,))
    for fila in range(2, len(filas) + 2):
        if h[f"B{fila}"].value == "Ingreso":
            h[f"C{fila}"].fill = CLARO

    # ---- Por categoría ----
    claves = sorted({m["fecha"][:7] for m in movs})
    cats = defaultdict(lambda: defaultdict(float))
    for m in movs:
        if m["tipo"] == "gasto":
            cats[(m["categoria"], "Personal" if m["ambito"] == "personal" else "Hacienda")][m["fecha"][:7]] += m["monto"]
    filas = [[c, a, *[cats[(c, a)][k] for k in claves], sum(cats[(c, a)].values())] for (c, a) in sorted(cats)]
    _hoja(libro, "Por categoría", ["Categoría", "Hacienda / Personal", *[_mes(k + "-01") for k in claves], "Total"],
          filas, dinero=tuple(range(3, len(claves) + 4)), total=tuple(range(3, len(claves) + 4)))

    # ---- Vencimientos ----
    obl = db.filas("SELECT o.*, c.nombre AS cuenta FROM obligaciones o LEFT JOIN cuentas c ON c.id=o.cuenta_id "
                   "WHERE o.activa=1 ORDER BY o.fecha")
    hoy = db.hoy().isoformat()
    filas = [[o["fecha"], o["nombre"], o["tipo"], o["cuenta"] or "", o["monto"], o["monto_minimo"], o["frecuencia"],
              f"{o['cuotas_pagadas']} de {o['cuotas_total']}" if o["cuotas_total"] else "", o["saldo"],
              "VENCIDO" if o["fecha"] < hoy else ""] for o in obl]
    h = _hoja(libro, "Vencimientos", ["Fecha límite", "Qué", "Tipo", "Tarjeta / cuenta", "Valor", "Pago mínimo",
                                      "Frecuencia", "Cuotas pagadas", "Saldo", "Estado"], filas, dinero=(5, 6, 9))
    for fila in range(2, len(filas) + 2):
        if h[f"J{fila}"].value == "VENCIDO":
            for c in h[fila]:
                c.fill = ROJO

    # ---- Tarjetas ----
    filas = []
    for c in db.filas("SELECT * FROM cuentas WHERE activa=1 ORDER BY banco, nombre"):
        uso = (c["deuda"] or 0) / c["cupo"] if c["cupo"] else None
        filas.append([c["nombre"], c["banco"], c["ultimos4"], c["titular"], c["cupo"], c["deuda"],
                      f"{round(uso * 100)}%" if uso is not None else "", c["dia_corte"], c["dia_pago"], ""])
        for d in db.filas("SELECT * FROM diferidos WHERE cuenta_id=?", (c["id"],)):
            filas.append([f"   ↳ {d['descripcion']}", "", "", "", None, d["saldo"], "", "", "",
                          f"Cuota {d['cuota_actual']} de {d['cuotas_total']} · {round(d['valor_cuota'] or 0):,}".replace(",", ".")])
    _hoja(libro, "Tarjetas", ["Tarjeta / cuenta", "Banco", "Últimos 4", "Titular", "Cupo", "Deuda", "Uso del cupo",
                              "Día de corte", "Día de pago", "Compras a cuotas"], filas, dinero=(5, 6), anchos={1: 38, 10: 34})

    # ---- Papa ----
    filas = []
    for l in db.filas("SELECT * FROM lotes ORDER BY id"):
        r = rentabilidad_lote(l)
        filas.append([r["lote"], r["variedad"], r["hectareas"], r["fecha_siembra"], r["estado"], r["costo_total"],
                      r["bultos"], r["ingresos"], r["utilidad"], r["costo_por_bulto"], r["costo_por_hectarea"]])
    _hoja(libro, "Papa", ["Lote", "Variedad", "Hectáreas", "Siembra", "Estado", "Costo total", "Bultos", "Ingresos",
                          "Utilidad", "Costo por bulto", "Costo por hectárea"], filas, dinero=(6, 8, 9, 10, 11), total=(6, 8, 9))
    labores = db.filas("SELECT lb.*, l.nombre AS lote FROM labores lb LEFT JOIN lotes l ON l.id=lb.lote_id ORDER BY lb.fecha")
    _hoja(libro, "Labores", ["Fecha", "Lote", "Labor", "Producto", "Cantidad", "Costo", "Próxima", "Notas"],
          [[x["fecha"], x["lote"], x["tipo"], x["producto"], x["cantidad"], x["costo"], x["proxima"] or "", x["notas"]]
           for x in labores], dinero=(6,), total=(6,))

    # ---- Ganado ----
    animales = db.filas("SELECT * FROM animales ORDER BY estado, categoria, codigo")
    eventos = db.filas("SELECT e.*, a.codigo FROM eventos e LEFT JOIN animales a ON a.id=e.animal_id ORDER BY e.fecha")
    ultimo = {}
    for e in eventos:
        if e["animal_id"]:
            ultimo[e["animal_id"]] = e
    filas = [[a["codigo"], a["nombre"], a["categoria"], a["sexo"], a["raza"], a["nacimiento"] or "", a["madre"], a["estado"],
              f"{ultimo[a['id']]['tipo']} {ultimo[a['id']]['fecha']}" if a["id"] in ultimo else ""] for a in animales]
    _hoja(libro, "Ganado", ["Código", "Nombre", "Categoría", "Sexo", "Raza", "Nacimiento", "Madre", "Estado",
                            "Último evento"], filas)
    _hoja(libro, "Eventos ganado", ["Fecha", "Animal", "Evento", "Detalle", "Valor", "Próxima fecha"],
          [[e["fecha"], e["codigo"] or "Todo el hato", e["tipo"], e["detalle"], e["valor"], e["proxima"] or ""] for e in eventos],
          dinero=(5,))

    # ---- Leche ----
    dias = db.filas("SELECT fecha, SUM(litros) AS litros, MAX(vacas) AS vacas FROM leche WHERE fecha BETWEEN ? AND ? "
                    "GROUP BY fecha ORDER BY fecha", (desde, hasta))
    h = _hoja(libro, "Leche", ["Fecha", "Litros", "Vacas en ordeño", "Litros por vaca"],
              [[d["fecha"], d["litros"], d["vacas"], round(d["litros"] / d["vacas"], 1) if d["vacas"] else None] for d in dias],
              total=(2,))
    if dias:
        h.cell(h.max_row, 1, "TOTAL LITROS")
        h.cell(h.max_row, 2).number_format = "#,##0.0"
    _hoja(libro, "Pagos de leche", ["Desde", "Hasta", "Comprador", "Litros pagados", "Precio por litro", "Descuentos", "Neto recibido"],
          [[x["desde"], x["hasta"], x["comprador"], x["litros"], x["precio_litro"], x["descuentos"], x["neto"]]
           for x in db.filas("SELECT * FROM liquidaciones_leche WHERE hasta>=? AND desde<=? ORDER BY desde", (desde, hasta))],
          dinero=(5, 6, 7), total=(7,))

    for hoja in libro.worksheets[1:]:
        for fila in hoja.iter_rows(min_row=2, max_row=hoja.max_row):
            for c in fila:
                c.border = LINEA
    ruta = config.EXCEL_DIR / f"Galicia_{desde}_a_{hasta}.xlsx"
    libro.save(ruta)
    return ruta
