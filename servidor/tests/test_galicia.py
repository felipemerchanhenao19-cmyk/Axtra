"""Galicia: el asistente contable de la Hacienda La Galicia (registros, cuotas, alertas, facturas, Excel y bot)."""
import io
import json
from datetime import date

import pytest
from openpyxl import load_workbook

from servidor.galicia import agente, alertas, bot, cerebro, db, documentos, excel, herramientas as h

HOY = date(2026, 11, 16)
CTX = {"usuario": "Carlos", "chat": 111}


@pytest.fixture(autouse=True)
def limpio(monkeypatch):
    for tabla in db.TABLAS | {"acciones", "avisos", "estado"}:
        db.ejecutar(f"DELETE FROM {tabla}")
    monkeypatch.setattr(db, "hoy", lambda: HOY)
    agente._HISTORIAL.clear()
    yield


def ctx():
    return dict(CTX)


# ---------------- Dinero ----------------
@pytest.mark.parametrize("texto,valor", [(350000, 350000), ("350.000", 350000), ("$ 1.250.000", 1250000),
                                         ("350 mil", 350000), ("1,2 millones", 1200000), ("85000.50", 85000.5)])
def test_montos(texto, valor):
    assert h.monto(texto) == valor


def test_registrar_resumir_y_deshacer():
    c = ctx()
    h.registrar_movimiento(c, tipo="gasto", monto="420 mil", descripcion="4 jornales desyerba", categoria="jornales",
                           actividad="papa")
    h.registrar_movimiento(c, tipo="gasto", monto=180000, descripcion="Mercado", categoria="Mercado y hogar", ambito="personal",
                           actividad="papa")
    h.registrar_movimiento(c, tipo="ingreso", monto=2_000_000, descripcion="Venta novillo", categoria="venta de ganado",
                           actividad="ganado")
    r = h.resumen(c)
    assert r["ingresos"] == 2_000_000 and r["gastos_hacienda"] == 420000 and r["gastos_personales"] == 180000
    assert r["gastos_por_categoria"]["Jornales y mano de obra"] == 420000
    personal = db.fila("SELECT * FROM movimientos WHERE ambito='personal'")
    assert personal["actividad"] == "general"              # lo personal nunca se carga a la papa
    assert "Venta novillo" in db.deshacer(usuario="Carlos")
    assert h.resumen(c)["ingresos"] == 0


def test_monto_negativo_es_error():
    assert "error" in h.ejecutar("registrar_movimiento", {"tipo": "gasto", "monto": 0, "descripcion": "x"}, ctx())


# ---------------- Tarjetas, cuotas y vencimientos ----------------
def test_tarjeta_crea_su_pago_mensual_y_pagar_no_es_gasto():
    c = ctx()
    h.registrar_cuenta(c, nombre="Visa Bancolombia", banco="Bancolombia", ultimos4="4521", dia_pago=5)
    o = db.fila("SELECT * FROM obligaciones")
    assert o["fecha"] == "2026-12-05" and o["tipo"] == "tarjeta"
    r = h.pagar_obligacion(c, obligacion="visa bancolombia", monto=850000)
    assert r["contado_como_gasto"] is False and r["proximo_vencimiento"] == "2027-01-05"
    assert db.fila("SELECT COUNT(*) AS n FROM movimientos")["n"] == 0


def test_credito_por_cuotas_avanza_y_termina():
    c = ctx()
    h.registrar_obligacion(c, nombre="Crédito Finagro tractor", fecha="2026-11-20", monto=2_300_000, frecuencia="semestral",
                           tipo="credito", cuotas_total=2, cuotas_pagadas=0)
    r = h.pagar_obligacion(c, obligacion="finagro")
    assert r["proximo_vencimiento"] == "2027-05-20" and r["cuotas"] == "1 de 2" and r["contado_como_gasto"]
    r = h.pagar_obligacion(c, obligacion="finagro")
    assert r["terminada"] and not db.fila("SELECT activa FROM obligaciones")["activa"]
    db.deshacer(usuario="Carlos")                          # deshacer el último pago revive la cuota
    o = db.fila("SELECT * FROM obligaciones")
    assert o["activa"] == 1 and o["fecha"] == "2027-05-20" and o["cuotas_pagadas"] == 1


def test_fin_de_mes_no_se_desborda():
    assert db.siguiente_fecha("2027-01-31", "mensual") == "2027-02-28"


# ---------------- Papa ----------------
def test_lote_costos_y_cosecha():
    c = ctx()
    h.registrar_lote(c, nombre="El Alto", hectareas=2, variedad="Pastusa", fecha_siembra="2026-06-01")
    h.registrar_movimiento(c, tipo="gasto", monto=3_000_000, descripcion="semilla", categoria="Semilla", lote="el alto")
    h.registrar_labor(c, lote="El Alto", tipo="fumigación", producto="Curzate", costo=400000, pagado_ahora=True,
                      proxima="2026-11-18")
    h.registrar_labor(c, lote="El Alto", tipo="aporque", costo=600000)            # de bodega: suma al costo, no al gasto
    h.registrar_cosecha(c, lote="alto", bultos=200, precio_bulto="95 mil", final=True)
    r = h.estado_lotes(c)["lotes"][0]
    assert r["costo_total"] == 4_000_000 and r["ingresos"] == 19_000_000 and r["costo_por_bulto"] == 20000
    assert r["costo_por_hectarea"] == 2_000_000 and r["estado"] == "cosechado"
    assert db.fila("SELECT SUM(monto) AS t FROM movimientos WHERE tipo='gasto'")["t"] == 3_400_000


def test_lote_inexistente_dice_cuales_hay():
    h.registrar_lote(ctx(), nombre="Lote 1")
    r = h.ejecutar("registrar_labor", {"lote": "zzzz", "tipo": "riego"}, ctx())
    assert "Lote 1" in r["error"]


# ---------------- Leche y ganado ----------------
def test_leche_y_liquidacion():
    c = ctx()
    for dia in range(1, 16):
        h.registrar_leche(c, litros=300, fecha=f"2026-11-{dia:02d}")
    r = h.registrar_pago_leche(c, neto=6_100_000, desde="2026-11-01", hasta="2026-11-15", litros=4450, precio_litro=1450)
    assert r["litros_anotados_en_finca"] == 4500 and r["diferencia_litros"] == 50
    assert h.resumen_leche(c, desde="2026-11-01")["promedio_diario"] == 300


def test_ganado_servicio_parto_y_venta():
    c = ctx()
    h.registrar_animal(c, codigo="15", nombre="Mariposa", sexo="hembra", categoria="vaca")
    h.evento_animal(c, animal="mariposa", tipo="inseminación", fecha="2026-02-10")
    e = db.fila("SELECT * FROM eventos")
    assert e["tipo"] == "servicio" and e["proxima"] == "2026-11-20"           # 283 días
    assert any(x["tipo"] == "servicio" for x in h.proximos(30)["ganado"])
    h.evento_animal(c, animal="15", tipo="parto", fecha="2026-11-18", detalle="hembra")
    assert not h.proximos(30)["ganado"]                                       # ya parió: no más aviso
    h.evento_animal(c, animal="hato", tipo="vacuna", detalle="aftosa", valor=120000, proxima="2027-05-15")
    h.evento_animal(c, animal="15", tipo="venta", valor=3_500_000, detalle="Don Pedro")
    assert db.fila("SELECT estado FROM animales")["estado"] == "vendido"
    assert h.resumen(c)["ingresos_por_actividad"]["ganado"] == 3_500_000


# ---------------- Facturas ----------------
XML_DIAN = """<?xml version="1.0" encoding="UTF-8"?>
<AttachedDocument xmlns="urn:oasis:names:specification:ubl:schema:xsd:AttachedDocument-2"
  xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
  xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
 <cac:Attachment><cac:ExternalReference><cbc:Description><![CDATA[<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
  xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
  xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
 <cbc:ID>FE-2291</cbc:ID><cbc:UUID>abc123cufe</cbc:UUID><cbc:IssueDate>2026-11-10</cbc:IssueDate>
 <cac:AccountingSupplierParty><cac:Party><cac:PartyTaxScheme><cbc:RegistrationName>AGROINSUMOS DEL ORIENTE SAS</cbc:RegistrationName>
 <cbc:CompanyID>900123456</cbc:CompanyID></cac:PartyTaxScheme></cac:Party></cac:AccountingSupplierParty>
 <cac:PaymentMeans><cbc:ID>1</cbc:ID></cac:PaymentMeans>
 <cac:TaxTotal><cbc:TaxAmount>47500</cbc:TaxAmount></cac:TaxTotal>
 <cac:LegalMonetaryTotal><cbc:PayableAmount>297500.00</cbc:PayableAmount></cac:LegalMonetaryTotal>
 <cac:InvoiceLine><cbc:InvoicedQuantity>2</cbc:InvoicedQuantity><cbc:LineExtensionAmount>250000</cbc:LineExtensionAmount>
 <cac:Item><cbc:Description>Abono 15-15-15 x 50 kg</cbc:Description></cac:Item></cac:InvoiceLine>
</Invoice>]]></cbc:Description></cac:ExternalReference></cac:Attachment>
</AttachedDocument>"""


def test_xml_dian_exacto_y_zip():
    d = documentos.leer(XML_DIAN.encode())
    assert d["tercero"] == "AGROINSUMOS DEL ORIENTE SAS" and d["nit"] == "900123456" and d["total"] == 297500
    assert d["cufe"] == "abc123cufe" and d["items"][0]["cantidad"] == 2 and d["exacta"]
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("ad0900123456.xml", XML_DIAN)
    assert documentos.leer(buf.getvalue(), "factura.zip")["factura"] == "FE-2291"


def test_factura_aprende_y_detecta_duplicado():
    p = documentos.preparar({**documentos.leer(XML_DIAN.encode()), "categoria": "Fertilizantes", "actividad": "papa"}, 111)
    assert p["datos"]["actividad"] == "papa" and not p["aviso"]
    d = p["datos"]
    d["actividad"] = "ganado"                                  # la persona la corrigió con el botón
    db.cambiar_pendiente(p["id"], d)
    r = documentos.guardar_factura(p["id"], ctx())
    assert r["ok"] and db.fila("SELECT origen, cufe FROM movimientos")["origen"] == "xml"
    otra = documentos.preparar({**documentos.leer(XML_DIAN.encode()), "actividad": "papa"}, 111)
    assert "ya registrada" in otra["aviso"]
    assert otra["datos"]["actividad"] == "ganado" and otra["datos"]["aprendido"]      # aprendió del proveedor


def test_ajustar_factura_por_chat():
    h.registrar_cuenta(ctx(), nombre="Mastercard Agrario", banco="Banco Agrario")
    p = documentos.preparar({"tipo": "factura", "tercero": "Almacén El Campo", "total": None, "fecha": "2026-11-15"}, 111)
    with pytest.raises(ValueError):
        documentos.guardar_factura(p["id"], ctx())
    r = h.ajustar_factura(ctx(), total="350 mil", cuenta="mastercard", guardar=True)
    assert r["ok"]
    m = db.fila("SELECT m.monto, c.nombre FROM movimientos m JOIN cuentas c ON c.id=m.cuenta_id")
    assert m["monto"] == 350000 and m["nombre"] == "Mastercard Agrario"


EXTRACTO = {"tipo": "extracto", "banco": "Bancolombia", "franquicia": "Visa", "ultimos4": "4521", "titular": "Carlos",
            "fecha_corte": "2026-11-10", "fecha_limite_pago": "2026-11-25", "pago_total": "1.850.000",
            "pago_minimo": 420000, "cupo_total": 8_000_000, "deuda_total": 7_500_000,
            "diferidos": [{"descripcion": "Guadañadora", "valor_cuota": 150000, "cuota_actual": 3, "cuotas_total": 12, "saldo": 1_350_000}],
            "movimientos": [{"fecha": "2026-10-20", "descripcion": "AGROCAMPO", "valor": 230000, "categoria": "Insumos agrícolas",
                             "actividad": "papa"},
                            {"fecha": "2026-10-22", "descripcion": "EXITO", "valor": 310000, "categoria": "Mercado y hogar",
                             "ambito": "personal"}]}


def test_extracto_crea_tarjeta_pago_cuotas_e_importa_sin_duplicar():
    h.registrar_movimiento(ctx(), tipo="gasto", monto=230000, descripcion="abono agrocampo", fecha="2026-10-21")
    p = documentos.preparar(EXTRACTO, 111)
    assert p["datos"]["nuevos"] == 1 and "4521" in documentos.tarjeta_extracto(p["datos"])
    r = documentos.guardar_extracto(p["id"], ctx(), importar=True)
    assert "2026-11-25" in r["texto"]
    cta = db.fila("SELECT * FROM cuentas")
    assert cta["ultimos4"] == "4521" and cta["dia_pago"] == 25 and cta["deuda"] == 7_500_000
    o = db.fila("SELECT * FROM obligaciones")
    assert o["monto"] == 1_850_000 and o["monto_minimo"] == 420000 and o["fecha"] == "2026-11-25"
    assert db.fila("SELECT * FROM diferidos")["cuotas_total"] == 12
    assert db.fila("SELECT COUNT(*) AS n FROM movimientos")["n"] == 2                 # solo entró el Éxito
    # el mes siguiente: misma tarjeta, se actualiza (no se duplica) y los diferidos se reemplazan
    p2 = documentos.preparar({**EXTRACTO, "fecha_limite_pago": "2026-12-26", "movimientos": [],
                              "diferidos": [{**EXTRACTO["diferidos"][0], "cuota_actual": 4}]}, 111)
    assert p2["datos"]["cuenta_existente"] == cta["nombre"]
    documentos.guardar_extracto(p2["id"], ctx())
    assert db.fila("SELECT COUNT(*) AS n FROM cuentas")["n"] == 1
    assert db.fila("SELECT fecha FROM obligaciones")["fecha"] == "2026-12-26"
    assert [d["cuota_actual"] for d in db.filas("SELECT * FROM diferidos")] == [4]
    db.deshacer(usuario="Carlos")                                                     # vuelve la cuota 3
    assert [d["cuota_actual"] for d in db.filas("SELECT * FROM diferidos")] == [3]


# ---------------- Alertas ----------------
def test_alertas_avisan_una_vez_por_umbral_y_vencidas_a_diario(monkeypatch):
    c = ctx()
    h.registrar_obligacion(c, nombre="Predial", fecha="2026-11-21", monto=900000, frecuencia="anual", tipo="impuesto")
    h.registrar_obligacion(c, nombre="SOAT camioneta", fecha="2026-11-10", monto=1_100_000, frecuencia="anual", tipo="seguro")
    h.registrar_obligacion(c, nombre="Lejano", fecha="2027-03-01", frecuencia="anual")
    texto, botones = alertas.revision_diaria()
    assert "Predial" in texto and "en 5 días" in texto and "VENCIDO hace 6 días" in texto and "Lejano" not in texto
    assert len(botones) == 2
    texto, _ = alertas.revision_diaria()
    assert texto == ""                                             # mismo día: no repite
    monkeypatch.setattr(db, "hoy", lambda: date(2026, 11, 18))
    texto, _ = alertas.revision_diaria()
    assert "Predial" in texto and "SOAT" in texto                  # umbral de 3 días + vencido de nuevo


def test_alerta_de_leche_y_cupo():
    c = ctx()
    h.registrar_leche(c, litros=310, fecha="2026-11-13")
    db.ejecutar("INSERT INTO cuentas (nombre, cupo, deuda) VALUES ('Visa', 1000000, 950000)")
    texto, _ = alertas.revision_diaria()
    assert "litros de leche de ayer" in texto and "95% del cupo" in texto


def test_informe_mensual_solo_el_dia_1(monkeypatch):
    assert alertas.informe_mensual() is None
    monkeypatch.setattr(db, "hoy", lambda: date(2026, 12, 1))
    texto, desde, hasta = alertas.informe_mensual()
    assert "noviembre" in texto and desde == "2026-11-01" and hasta == "2026-11-30"
    assert alertas.informe_mensual() is None


# ---------------- Excel ----------------
def test_excel_tiene_todas_las_hojas():
    c = ctx()
    h.registrar_lote(c, nombre="Lote 1", hectareas=1)
    h.registrar_movimiento(c, tipo="gasto", monto=100000, descripcion="fungicida", lote="lote 1")
    h.registrar_movimiento(c, tipo="ingreso", monto=500000, descripcion="leche", actividad="leche", categoria="Venta de leche")
    h.registrar_leche(c, litros=200)
    ruta = excel.generar("2026-01-01", "2026-12-31")
    libro = load_workbook(ruta)
    assert {"Inicio", "Resumen mensual", "Movimientos", "Por categoría", "Vencimientos", "Tarjetas", "Papa", "Labores",
            "Ganado", "Eventos ganado", "Leche", "Pagos de leche"} <= set(libro.sheetnames)
    mov = libro["Movimientos"]
    assert mov["C2"].value == -100000 and mov["C3"].value == 500000 and mov["C5"].value == "=SUM(C2:C3)"
    assert libro["Inicio"]["B4"].value == 500000


# ---------------- El asistente (con un cerebro falso) ----------------
def _llamada(nombre, **args):
    return {"id": f"c{nombre}", "type": "function", "function": {"name": nombre, "arguments": json.dumps(args)}}


def test_agente_usa_herramientas_y_responde(monkeypatch):
    guion = [{"role": "assistant", "content": "", "tool_calls": [
                 _llamada("registrar_movimiento", tipo="gasto", monto=255000, descripcion="3 bultos de sal",
                          categoria="Alimento y sal para ganado", actividad="ganado")]},
             {"role": "assistant", "content": "Listo: $255.000 en sal para el ganado.", "tool_calls": []}]
    vistos = []

    def falso(mensajes, herramientas=None, max_tokens=1200):
        vistos.append(mensajes)
        return guion.pop(0)
    monkeypatch.setattr(cerebro, "chat", falso)
    r = agente.responder("compré 3 bultos de sal a 85 mil", "Carlos", 111)
    assert r["texto"].startswith("Listo") and len(r["acciones"]) == 1
    assert db.fila("SELECT * FROM movimientos")["usuario"] == "Carlos"
    assert vistos[1][-1]["role"] == "tool" and "2026-11-16" in vistos[0][0]["content"]


# ---------------- El bot (con un Telegram falso) ----------------
class TelegramFalso:
    def __init__(self):
        self.enviados, self.editados = [], []

    def enviar(self, chat, texto, botones=None, markdown=True):
        self.enviados.append((chat, texto, botones))

    def editar(self, chat, mensaje, texto, botones=None):
        self.editados.append((chat, texto, botones))

    def contestar_boton(self, *a, **k):
        pass

    def escribiendo(self, *a):
        pass

    def enviar_archivo(self, chat, ruta, texto=""):
        self.enviados.append((chat, f"ARCHIVO {ruta}", None))

    def descargar(self, file_id):
        return XML_DIAN.encode(), "documents/file_1.xml"


@pytest.fixture
def tg(monkeypatch):
    falso = TelegramFalso()
    for nombre in ("enviar", "editar", "contestar_boton", "escribiendo", "enviar_archivo", "descargar"):
        monkeypatch.setattr(bot.telegram, nombre, getattr(falso, nombre))
    return falso


def test_bot_rechaza_desconocidos(tg):
    bot.atender({"message": {"chat": {"id": 999, "type": "private"}, "from": {"id": 999}, "text": "hola"}})
    assert "privado" in tg.enviados[0][1] and "999" in tg.enviados[0][1]
    assert db.fila("SELECT COUNT(*) AS n FROM movimientos")["n"] == 0


def test_bot_factura_xml_botones_y_guardar(tg):
    msg = {"chat": {"id": 111, "type": "private"}, "from": {"id": 111},
           "document": {"file_id": "F", "file_name": "factura.xml", "mime_type": "text/xml"}}
    bot.atender({"message": msg})
    _, tarjeta, botones = tg.enviados[-1]
    assert "AGROINSUMOS" in tarjeta and "$297.500" in tarjeta
    pid = int(botones[-1][0][1].split(":")[1])
    q = {"id": "q", "from": {"id": 222}, "message": {"chat": {"id": 111}, "message_id": 5}}
    bot.atender({"callback_query": {**q, "data": f"a:{pid}:leche"}})
    assert "leche" in tg.editados[-1][1]
    bot.atender({"callback_query": {**q, "data": f"g:{pid}"}})
    assert "Guardada" in tg.editados[-1][1]
    m = db.fila("SELECT * FROM movimientos")
    assert m["actividad"] == "leche" and m["usuario"] == "María" and m["soporte"].endswith(".xml")
    accion = tg.editados[-1][2][0][0][1]
    bot.atender({"callback_query": {**q, "data": accion}})
    assert db.fila("SELECT COUNT(*) AS n FROM movimientos")["n"] == 0


def test_bot_sin_ia_guarda_en_cola_y_reintenta(tg, monkeypatch):
    def caido(*a, **k):
        raise cerebro.SinCerebro("sin cupo")
    monkeypatch.setattr(cerebro, "chat", caido)
    bot.atender({"message": {"chat": {"id": 111, "type": "private"}, "from": {"id": 111}, "text": "hoy 300 litros"}})
    assert "Guardé tu mensaje" in tg.enviados[-1][1]
    monkeypatch.setattr(cerebro, "chat", lambda *a, **k: {"role": "assistant", "content": "Anotados 300 litros.", "tool_calls": []})
    monkeypatch.setattr(cerebro, "disponible", lambda: True)
    bot.reintentar_cola()
    assert "Anotados 300 litros" in tg.enviados[-1][1]
    assert not db.filas("SELECT * FROM pendientes")


def test_bot_boton_ya_pague_desde_alerta(tg):
    h.registrar_obligacion(ctx(), nombre="Cuota moto", fecha="2026-11-18", monto=450000, cuotas_total=24, cuotas_pagadas=10)
    texto, botones = alertas.texto_pendientes()
    assert "cuota 11 de 24" in texto
    bot.atender({"callback_query": {"id": "q", "data": botones[0][0][1], "from": {"id": 111},
                                    "message": {"chat": {"id": 111}, "message_id": 9}}})
    assert "Próximo: 2026-12-18" in tg.enviados[-1][1]


def test_comandos_funcionan_sin_ia(tg):
    for cmd in ("/pendientes", "/resumen", "/tarjetas", "/ayuda", "/excel"):
        bot.atender({"message": {"chat": {"id": 111, "type": "private"}, "from": {"id": 111}, "text": cmd}})
    assert len(tg.enviados) == 5 and tg.enviados[-1][1].startswith("ARCHIVO")


def test_fotos_pesadas_se_achican():
    from PIL import Image
    import os
    buf = io.BytesIO()
    Image.frombytes("RGB", (3000, 3000), os.urandom(3000 * 3000 * 3)).save(buf, "PNG")
    assert len(buf.getvalue()) > 2_500_000
    chica = documentos.achicar(buf.getvalue())
    assert len(chica) < len(buf.getvalue()) and max(Image.open(io.BytesIO(chica)).size) == 2000
