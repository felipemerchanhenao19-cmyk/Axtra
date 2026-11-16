"""Facturas y extractos: foto, PDF, XML de factura electrónica DIAN o ZIP del correo.

Orden de confianza: XML de la DIAN (exacto, sin IA) → PDF con texto → foto (IA de visión).
Nada se guarda solo: queda «pendiente» y la persona toca Guardar (la IA propone, el humano confirma).
"""
import io
import json
import re
import time
import xml.etree.ElementTree as ET
import zipfile
from datetime import date

from . import cerebro, config, db
from .herramientas import _ambito, _actividad, _categoria, _cuenta, _lote, monto, nuevo_movimiento, pesos

INSTRUCCIONES = f"""Eres el auxiliar contable de una finca en Colombia (papa, ganado y leche). Lee el documento y
responde SOLO un JSON. Primero decide "tipo":
- "factura": factura, cuenta de cobro, recibo, tiquete de compra o remisión de un proveedor.
- "extracto": extracto mensual de tarjeta de crédito o de cuenta bancaria.
- "otro": cualquier otra cosa.

Si es "factura":
{{"tipo":"factura","tercero":"nombre del proveedor","nit":"NIT o cédula del proveedor","fecha":"AAAA-MM-DD",
"factura":"número","cufe":"CUFE si aparece","total":número,"iva":número,"medio_pago":"efectivo/tarjeta/crédito/transferencia",
"items":[{{"descripcion":"...","cantidad":número,"valor":número}}],"descripcion":"resumen de 3 a 8 palabras",
"categoria":"una de {config.CATEGORIAS_GASTO}","ambito":"hacienda o personal","actividad":"papa, ganado, leche o general"}}
Pistas: abonos, semilla, fungicidas, insecticidas → papa. Sal, concentrado, vacunas, droga veterinaria → ganado.
Cantinas, filtros, insumos de ordeño → leche. Mercado, ropa, restaurante, salud → personal.

Si es "extracto":
{{"tipo":"extracto","banco":"...","producto":"tarjeta de crédito o cuenta","franquicia":"Visa/Mastercard/...",
"ultimos4":"últimos 4 dígitos","titular":"...","fecha_corte":"AAAA-MM-DD","fecha_limite_pago":"AAAA-MM-DD",
"pago_total":número,"pago_minimo":número,"cupo_total":número,"deuda_total":número,
"diferidos":[{{"descripcion":"...","fecha_compra":"AAAA-MM-DD","valor_cuota":número,"cuota_actual":número,"cuotas_total":número,"saldo":número}}],
"movimientos":[{{"fecha":"AAAA-MM-DD","descripcion":"comercio","valor":número,"tipo":"gasto o ingreso",
"categoria":"una de las categorías","ambito":"hacienda o personal","actividad":"papa, ganado, leche o general"}}]}}
En "movimientos" van las compras y avances del periodo (no los pagos a la tarjeta, ni intereses ni cuotas de manejo,
que van como gasto con categoría "Créditos y tarjetas").

Los valores son pesos colombianos como números sin puntos ni signos (1.250.000 → 1250000). Si un dato no aparece, usa null.
Hoy es {{hoy}}."""


def _instrucciones() -> str:
    return INSTRUCCIONES.replace("{hoy}", db.hoy().isoformat())


# ---------------- Factura electrónica DIAN (XML UBL 2.1) ----------------
NS = {"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
      "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}


def _texto(nodo, ruta: str) -> str:
    n = nodo.find(ruta, NS)
    return (n.text or "").strip() if n is not None and n.text else ""


def leer_xml(contenido: bytes) -> dict:
    """Lee la factura electrónica. Casi siempre llega como AttachedDocument con la factura adentro (CDATA)."""
    raiz = ET.fromstring(contenido)
    if not raiz.tag.endswith("Invoice"):
        for d in raiz.iter("{%s}Description" % NS["cbc"]):
            if d.text and "Invoice" in d.text:
                raiz = ET.fromstring(d.text.strip().encode())
                break
        else:
            raise ValueError("el XML no trae una factura")
    proveedor = raiz.find("cac:AccountingSupplierParty/cac:Party", NS)
    nombre = nit = ""
    if proveedor is not None:
        nombre = _texto(proveedor, "cac:PartyTaxScheme/cbc:RegistrationName") or \
            _texto(proveedor, "cac:PartyLegalEntity/cbc:RegistrationName") or _texto(proveedor, "cac:PartyName/cbc:Name")
        nit = _texto(proveedor, "cac:PartyTaxScheme/cbc:CompanyID") or _texto(proveedor, "cac:PartyLegalEntity/cbc:CompanyID")
    items = []
    for linea in raiz.findall("cac:InvoiceLine", NS):
        items.append({"descripcion": _texto(linea, "cac:Item/cbc:Description"),
                      "cantidad": float(_texto(linea, "cbc:InvoicedQuantity") or 0),
                      "valor": float(_texto(linea, "cbc:LineExtensionAmount") or 0)})
    total = _texto(raiz, "cac:LegalMonetaryTotal/cbc:PayableAmount")
    iva = sum(float(t.text or 0) for t in raiz.findall("cac:TaxTotal/cbc:TaxAmount", NS))
    medio = _texto(raiz, "cac:PaymentMeans/cbc:ID")
    return {"tipo": "factura", "tercero": nombre, "nit": nit, "fecha": _texto(raiz, "cbc:IssueDate"),
            "factura": _texto(raiz, "cbc:ID"), "cufe": _texto(raiz, "cbc:UUID"), "total": float(total or 0), "iva": iva,
            "medio_pago": "crédito" if medio == "2" else "contado", "items": items, "exacta": True}


# ---------------- PDF ----------------
def texto_pdf(contenido: bytes) -> str:
    from pypdf import PdfReader
    lector = PdfReader(io.BytesIO(contenido))
    if lector.is_encrypted:
        for clave in ["", *config.CLAVES_PDF]:
            try:
                if lector.decrypt(clave):
                    break
            except Exception:
                continue
        else:
            raise PermissionError("el PDF tiene clave")
    return "\n".join((p.extract_text() or "") for p in lector.pages[:12])


def imagen_pdf(contenido: bytes) -> bytes:
    """Primera página del PDF como imagen (para PDF escaneados, sin texto)."""
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(contenido, password=(config.CLAVES_PDF or [None])[0])
    img = pdf[0].render(scale=2).to_pil()
    salida = io.BytesIO()
    img.convert("RGB").save(salida, "JPEG", quality=85)
    return salida.getvalue()


# ---------------- Leer cualquier archivo ----------------
def leer(contenido: bytes, nombre: str = "", mime: str = "") -> dict:
    nombre = (nombre or "").lower()
    if nombre.endswith(".zip") or contenido[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(contenido)) as z:
            nombres = z.namelist()
            xml = next((n for n in nombres if n.lower().endswith(".xml")), None)
            if xml:
                return leer(z.read(xml), xml)
            pdf = next((n for n in nombres if n.lower().endswith(".pdf")), None)
            if pdf:
                return leer(z.read(pdf), pdf)
        raise ValueError("el ZIP no trae XML ni PDF")
    if nombre.endswith(".xml") or contenido.lstrip()[:5] == b"<?xml":
        return leer_xml(contenido)
    if nombre.endswith(".pdf") or contenido[:4] == b"%PDF":
        texto = texto_pdf(contenido)
        if len(texto.strip()) > 200:
            return cerebro.extraer_texto(_instrucciones(), texto)
        return cerebro.extraer_imagen(_instrucciones(), imagen_pdf(contenido))
    return cerebro.extraer_imagen(_instrucciones(), achicar(contenido), "image/jpeg")


def achicar(imagen: bytes, lado: int = 2000) -> bytes:
    """Fotos muy pesadas (enviadas como archivo) se reducen: Groq acepta hasta ~4 MB y la IA lee igual de bien."""
    if len(imagen) < 2_500_000:
        return imagen
    from PIL import Image, ImageOps
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(imagen))).convert("RGB")
    img.thumbnail((lado, lado))
    salida = io.BytesIO()
    img.save(salida, "JPEG", quality=85)
    return salida.getvalue()


def _num(v):
    try:
        return monto(v) if v not in (None, "") else None
    except (ValueError, TypeError):
        return None


def _fecha_o_hoy(v) -> str:
    try:
        return db.fecha(v)
    except ValueError:
        return db.hoy().isoformat()


def preparar(datos: dict, chat: int, soporte: str = "") -> dict:
    """Normaliza lo que leyó la IA, aplica lo aprendido y lo deja pendiente. Devuelve {id, tipo, datos, aviso}."""
    tipo = datos.get("tipo")
    if tipo == "factura":
        d = {"tercero": (datos.get("tercero") or "").strip(), "nit": str(datos.get("nit") or "").strip(),
             "fecha": _fecha_o_hoy(datos.get("fecha")), "factura": str(datos.get("factura") or "").strip(),
             "cufe": str(datos.get("cufe") or "").strip(), "total": _num(datos.get("total")) or 0,
             "iva": _num(datos.get("iva")), "medio_pago": datos.get("medio_pago") or "",
             "items": (datos.get("items") or [])[:30], "soporte": soporte, "exacta": bool(datos.get("exacta"))}
        d["descripcion"] = (datos.get("descripcion") or ", ".join(i.get("descripcion", "") for i in d["items"][:3]))[:120]
        d["categoria"] = _categoria(datos.get("categoria") or "", "gasto")
        d["ambito"] = _ambito(datos.get("ambito") or "hacienda")
        d["actividad"] = _actividad(datos.get("actividad") or "general")
        aprendida = db.regla(d["nit"], d["tercero"])
        if aprendida:
            d.update(categoria=aprendida["categoria"], ambito=aprendida["ambito"], actividad=aprendida["actividad"])
            d["aprendido"] = True
        aviso = ""
        if dup := db.duplicado_factura(d["cufe"], d["nit"], d["factura"]):
            aviso = f"⚠️ Esta factura parece ya registrada (el {dup['fecha']}, {pesos(dup['monto'])})."
        return {"id": db.guardar_pendiente(chat, "factura", d), "tipo": "factura", "datos": d, "aviso": aviso}
    if tipo == "extracto":
        d = {k: datos.get(k) for k in ("banco", "producto", "franquicia", "titular")}
        d["ultimos4"] = re.sub(r"\D", "", str(datos.get("ultimos4") or ""))[-4:]
        for k in ("fecha_corte", "fecha_limite_pago"):
            try:
                d[k] = db.fecha(datos.get(k)) if datos.get(k) else None
            except ValueError:
                d[k] = None
        for k in ("pago_total", "pago_minimo", "cupo_total", "deuda_total"):
            d[k] = _num(datos.get(k))
        d["diferidos"] = [x for x in (datos.get("diferidos") or []) if isinstance(x, dict)][:40]
        d["movimientos"] = []
        for m in (datos.get("movimientos") or [])[:150]:
            valor = _num(m.get("valor")) if isinstance(m, dict) else None
            if not valor:
                continue
            tipo_m = "ingreso" if db.normal(m.get("tipo")).startswith("ing") else "gasto"
            d["movimientos"].append({"fecha": _fecha_o_hoy(m.get("fecha")), "descripcion": str(m.get("descripcion") or "")[:80],
                                     "valor": abs(valor), "tipo": tipo_m, "categoria": _categoria(m.get("categoria") or "", tipo_m),
                                     "ambito": _ambito(m.get("ambito") or "hacienda"),
                                     "actividad": _actividad(m.get("actividad") or "general")})
        d["soporte"] = soporte
        d["cuenta_existente"] = (cuenta_del_extracto(d) or {}).get("nombre")
        d["nuevos"] = sum(1 for m in d["movimientos"] if not db.parecido(m["fecha"], m["valor"]))
        return {"id": db.guardar_pendiente(chat, "extracto", d), "tipo": "extracto", "datos": d, "aviso": ""}
    return {"id": None, "tipo": "otro", "datos": datos, "aviso": ""}


# ---------------- Tarjetas de revisión (lo que ve la persona antes de Guardar) ----------------
def tarjeta_factura(d: dict) -> str:
    lineas = ["🧾 *Factura*" + (" (electrónica DIAN ✓)" if d.get("exacta") else ""),
              f"Proveedor: {d['tercero'] or '¿?'}" + (f" · NIT {d['nit']}" if d.get("nit") else ""),
              f"Fecha: {d['fecha']}" + (f" · N.º {d['factura']}" if d.get("factura") else ""),
              f"*Total: {pesos(d['total'])}*" + (f" (IVA {pesos(d['iva'])})" if d.get("iva") else "")]
    for i in d.get("items", [])[:6]:
        lineas.append(f"  • {i.get('descripcion', '')[:40]} {pesos(_num(i.get('valor')) or 0)}")
    if len(d.get("items", [])) > 6:
        lineas.append(f"  • … y {len(d['items']) - 6} más")
    destino = "🏠 Personal" if d["ambito"] == "personal" else f"🌾 Hacienda · {d['actividad']}"
    lineas += [f"Categoría: {d['categoria']}", f"Va para: {destino}" + (f" · lote {d['lote']}" if d.get("lote") else "")]
    if d.get("cuenta"):
        lineas.append(f"Pagada con: {d['cuenta']}")
    if d.get("aprendido"):
        lineas.append("_(clasificada como las anteriores de este proveedor)_")
    lineas.append("\n¿Está bien? Toca Guardar, cambia la actividad con los botones o escríbeme la corrección.")
    return "\n".join(lineas)


def tarjeta_extracto(d: dict) -> str:
    lineas = [f"💳 *Extracto {d.get('banco') or ''} {d.get('franquicia') or ''}* ****{d.get('ultimos4') or '?'}".replace("  ", " ")]
    if d.get("titular"):
        lineas.append(f"Titular: {d['titular']}")
    lineas += [f"Fecha límite de pago: *{d.get('fecha_limite_pago') or '¿?'}*",
               f"Pago total: *{pesos(d.get('pago_total'))}* · mínimo: {pesos(d.get('pago_minimo'))}"]
    if d.get("cupo_total"):
        lineas.append(f"Deuda: {pesos(d.get('deuda_total'))} de {pesos(d['cupo_total'])} de cupo")
    if d["diferidos"]:
        lineas.append(f"\nCompras a cuotas ({len(d['diferidos'])}):")
        for x in d["diferidos"][:8]:
            lineas.append(f"  • {str(x.get('descripcion', ''))[:30]}: cuota {x.get('cuota_actual')} de {x.get('cuotas_total')}"
                          f" · {pesos(_num(x.get('valor_cuota')) or 0)}")
    lineas.append(f"\nCompras del mes: {len(d['movimientos'])} ({d['nuevos']} sin registrar todavía)")
    lineas.append(f"Tarjeta: {'ya registrada como «' + d['cuenta_existente'] + '»' if d.get('cuenta_existente') else 'nueva (la registro al guardar)'}")
    return "\n".join(lineas)


# ---------------- Guardar ----------------
def guardar_factura(pid: int, ctx: dict) -> dict:
    p = db.pendiente(pid)
    if not p:
        raise ValueError("esa factura ya se guardó o se descartó")
    d = p["datos"]
    if not d.get("total"):
        raise ValueError("falta el total de la factura: escríbeme cuánto fue")
    l, c = _lote(d.get("lote")), _cuenta(d.get("cuenta"))
    acc = db.Accion(ctx["usuario"], f"factura {d['tercero']} {pesos(d['total'])}")
    id_ = nuevo_movimiento(acc, tipo="gasto", monto=d["total"], descripcion=d.get("descripcion") or "Factura",
                           categoria=d["categoria"], ambito=d["ambito"], actividad="papa" if l else d["actividad"],
                           fecha=d["fecha"], tercero=d["tercero"], nit=d.get("nit", ""), factura=d.get("factura", ""),
                           cufe=d.get("cufe", ""), soporte=d.get("soporte", ""), lote_id=l and l["id"],
                           cuenta_id=c and c["id"], origen="xml" if d.get("exacta") else "foto")
    db.aprender(d.get("nit"), d["tercero"], d["categoria"], d["ambito"], d["actividad"])
    db.borrar_pendiente(pid)
    accion = acc.guardar()
    ctx.setdefault("acciones", []).append(accion)
    return {"ok": True, "id": id_, "accion": accion, "texto": f"✅ Guardada: {d['tercero']} · {pesos(d['total'])} · "
            f"{'personal' if d['ambito'] == 'personal' else d['actividad']} · {d['categoria']}"}


def cuenta_del_extracto(d: dict):
    if d.get("ultimos4"):
        c = db.fila("SELECT * FROM cuentas WHERE ultimos4=? AND activa=1", (d["ultimos4"],))
        if c:
            return c
    if d.get("banco"):
        candidatas = [c for c in db.filas("SELECT * FROM cuentas WHERE activa=1 AND tipo='tarjeta'")
                      if db.normal(d["banco"]).split(" ")[0] in db.normal(f"{c['banco']} {c['nombre']}")]
        if len(candidatas) == 1 and not candidatas[0]["ultimos4"]:
            return candidatas[0]
    return None


def guardar_extracto(pid: int, ctx: dict, importar: bool = False) -> dict:
    p = db.pendiente(pid)
    if not p:
        raise ValueError("ese extracto ya se guardó o se descartó")
    d = p["datos"]
    acc = db.Accion(ctx["usuario"], f"extracto {d.get('banco') or ''} ****{d.get('ultimos4') or ''}")
    c = cuenta_del_extracto(d)
    nombre = c["nombre"] if c else " ".join(x for x in (d.get("franquicia"), d.get("banco"), d.get("ultimos4")) if x) or "Tarjeta"
    dia_pago = date.fromisoformat(d["fecha_limite_pago"]).day if d.get("fecha_limite_pago") else None
    dia_corte = date.fromisoformat(d["fecha_corte"]).day if d.get("fecha_corte") else None
    cambios = {"cupo": d.get("cupo_total"), "deuda": d.get("deuda_total"), "dia_pago": dia_pago, "dia_corte": dia_corte,
               "ultimos4": d.get("ultimos4") or None, "banco": d.get("banco") or None, "titular": d.get("titular") or None}
    cambios = {k: v for k, v in cambios.items() if v is not None}
    if c:
        acc.actualizar("cuentas", c["id"], cambios)
        cuenta_id = c["id"]
    else:
        cuenta_id = acc.insertar("cuentas", {"nombre": nombre, "tipo": "tarjeta", **cambios})
    if d.get("fecha_limite_pago"):
        o = db.fila("SELECT * FROM obligaciones WHERE cuenta_id=? AND tipo='tarjeta' AND activa=1", (cuenta_id,))
        datos_o = {"fecha": d["fecha_limite_pago"], "monto": d.get("pago_total"), "monto_minimo": d.get("pago_minimo")}
        if o:
            acc.actualizar("obligaciones", o["id"], datos_o)
        else:
            acc.insertar("obligaciones", {"nombre": f"Pago {nombre}", "tipo": "tarjeta", "cuenta_id": cuenta_id,
                                          "frecuencia": "mensual", **datos_o})
    for viejo in db.filas("SELECT * FROM diferidos WHERE cuenta_id=?", (cuenta_id,)):
        db.ejecutar("DELETE FROM diferidos WHERE id=?", (viejo["id"],))
        acc.pasos.append({"restaurar_fila": ["diferidos", viejo]})
    for x in d["diferidos"]:
        acc.insertar("diferidos", {"cuenta_id": cuenta_id, "descripcion": str(x.get("descripcion") or "")[:80],
                                   "fecha_compra": x.get("fecha_compra"), "valor_cuota": _num(x.get("valor_cuota")),
                                   "cuota_actual": x.get("cuota_actual"), "cuotas_total": x.get("cuotas_total"),
                                   "saldo": _num(x.get("saldo")), "actualizado": d.get("fecha_corte") or db.hoy().isoformat()})
    importados = 0
    if importar:
        for m in d["movimientos"]:
            if db.parecido(m["fecha"], m["valor"]):
                continue
            nuevo_movimiento(acc, tipo=m["tipo"], monto=m["valor"], descripcion=m["descripcion"], categoria=m["categoria"],
                             ambito=m["ambito"], actividad=m["actividad"], fecha=m["fecha"], cuenta_id=cuenta_id,
                             tercero=m["descripcion"], origen="extracto", soporte=d.get("soporte", ""))
            importados += 1
    db.borrar_pendiente(pid)
    accion = acc.guardar()
    ctx.setdefault("acciones", []).append(accion)
    texto = f"✅ Extracto guardado en «{nombre}»."
    if d.get("fecha_limite_pago"):
        texto += f" Te aviso antes del {d['fecha_limite_pago']} para el pago de {pesos(d.get('pago_total'))}."
    if importados:
        texto += f" Registré {importados} compras del mes."
    return {"ok": True, "accion": accion, "texto": texto}


def guardar_soporte(contenido: bytes, extension: str) -> str:
    carpeta = config.SOPORTES_DIR / db.hoy().strftime("%Y-%m")
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{int(time.time() * 1000)}.{extension.lstrip('.') or 'bin'}"
    ruta.write_bytes(contenido)
    return str(ruta.relative_to(config.DATA_DIR))


def resumen_json(d: dict) -> str:
    return json.dumps(d, ensure_ascii=False)[:3000]
