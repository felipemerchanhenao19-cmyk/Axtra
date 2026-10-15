"""Apex Domicilios: la misma carta y el mismo orbe de Apex Play, pero el pedido sale con dirección y forma de pago."""
import time

from servidor.apex import config, db, orbe
from servidor.tests.test_apex import ORIGEN, PIN, accion, axtra, c, herramienta, texto  # noqa: F401 (fixtures)

DATOS = {"nombre": "Ana Pérez", "telefono": "300 123 4567", "direccion": "Calle 10 # 20-30", "barrio": "Centro",
         "zona": "z2", "notas": "Torre 2", "pago": "contra_entrega", "acepta_datos": True}


def sesion_dom(c):
    r = c.post("/v1/sesion", json={"restaurante": "domicilios", "mesa": "domicilio"}, headers=ORIGEN)
    assert r.status_code == 200
    return r.json()


def domicilio(c, s, **cambios):
    return c.post("/v1/domicilio", json={"sesion": s["sesion"], "secreto": s["secreto"], **DATOS, **cambios}, headers=ORIGEN)


def test_hereda_la_carta_del_demo():
    r = config.restaurante("domicilios")
    assert r["id"] == "domicilios" and r["mesas"] == [] and r["domicilio"]["minimo"] == 20000
    assert [p["id"] for p in r["menu"]] == [p["id"] for p in config.restaurante("demo")["menu"]]
    assert r["frases"]["eleccion"] == config.restaurante("demo")["frases"]["eleccion"]       # heredada
    assert "datos" in r["frases"] and "datos" not in config.restaurante("demo")["frases"]


def test_menu_publica_los_datos_del_domicilio(c):
    m = c.get("/v1/menu/domicilios").json()
    assert m["domicilio"]["pagos"] == ["contra_entrega", "nequi"] and len(m["domicilio"]["zonas"]) == 3
    assert c.get("/v1/menu/demo").json()["domicilio"] is None


def test_pedido_completo_a_domicilio(c, axtra):
    s = sesion_dom(c)
    accion(c, s, "pedir", plato_id="bandeja")
    r = accion(c, s, "confirmar").json()
    assert r["oferta"] == "torta"                               # primero ofrece el postre del día
    r = accion(c, s, "confirmar").json()                        # «No, continuar»
    assert r["datos"] is True and r["frase"].startswith("/v1/frase/domicilios/datos?")
    assert c.get("/v1/panel/domicilios", headers=PIN).json()["pedidos"] == []      # aún no sale: faltan los datos
    r = domicilio(c, s)
    assert r.status_code == 200, r.text
    p = r.json()["pedido"]
    assert p["pedido_numero"] and p["subtotal"] == 38000 and p["envio"] == 5000 and p["total_numero"] == 43000
    assert r.json()["despedida"] is True
    assert accion(c, s, "ver").json()["pedido"]["platos"] == []             # el carrito quedó vacío
    # La caja lo ve con todos los datos (mismo PIN del demo)
    caja = c.get("/v1/panel/domicilios", headers=PIN).json()
    assert caja["domicilio"] is True and caja["mesas"] == []
    e = caja["pedidos"][0]["entrega"]
    assert e["telefono"] == "3001234567" and e["direccion"] == "Calle 10 # 20-30" and e["zona"].startswith("Media")
    # Seguimiento: solo con el código del cliente
    url = f"/v1/seguimiento/domicilios/{p['pedido_numero']}"
    assert c.get(url, params={"t": p["seguimiento"]}).json()["estado"] == "nuevo"
    assert c.get(url, params={"t": "otro"}).status_code == 404
    assert c.get(url, params={"t": "ñandú"}).status_code == 404
    assert c.post(f"/v1/panel/domicilios/pedido/{p['pedido_numero']}", json={"estado": "en_camino"}, headers=PIN).status_code == 200
    assert c.get(url, params={"t": p["seguimiento"]}).json()["estado"] == "en_camino"


def test_validaciones_del_domicilio(c, axtra):
    s = sesion_dom(c)
    assert domicilio(c, s).status_code == 409                                  # carrito vacío
    accion(c, s, "pedir", plato_id="limonada")
    r = domicilio(c, s)
    assert r.status_code == 409 and "mínimo" in r.json()["error"]             # 12 mil < 20 mil
    accion(c, s, "pedir", plato_id="ajiaco")
    assert domicilio(c, s, pago="pse").status_code == 422                     # PSE aún no está activo
    assert domicilio(c, s, acepta_datos=False).status_code == 422
    assert domicilio(c, s, zona="z9").status_code == 422
    assert domicilio(c, s, telefono="abc-defg").status_code == 422
    assert domicilio(c, s, pago="nequi").status_code == 200


def test_el_orbe_de_domicilios_no_envia_ni_llama_mesero(c, axtra):
    r = config.localizar(config.restaurante("domicilios"), "")
    nombres = {h["function"]["name"] for h in orbe.herramientas(r)}
    assert nombres == {"agregar_plato", "quitar_plato", "ver_pedido"}
    assert "Continuar" in orbe.instrucciones(r, "domicilio") and "A DOMICILIO" in orbe.instrucciones(r, "domicilio")
    s = sesion_dom(c)
    assert accion(c, s, "mesero").status_code == 400
    axtra.oido = "quiero un ajiaco"
    axtra.guion = [herramienta("agregar_plato", {"plato_id": "ajiaco"}), texto("¡Listo! Un ajiaco.")]
    t = c.post("/v1/turno", content=b"\x1aE\xdf\xa3" + b"\x00" * 3000,
               headers={**ORIGEN, "Content-Type": "audio/webm", "X-Apex-Sesion": s["sesion"], "X-Apex-Secreto": s["secreto"]}).json()
    assert t["pedido"]["platos"][0]["id"] == "ajiaco"
    pensar = [j for ruta, j in axtra.llamadas if ruta == "/pensar"]
    assert "confirmar_pedido" not in {h["function"]["name"] for h in pensar[0]["herramientas"]}


def test_los_ejemplos_borran_los_datos_viejos(c):
    db.nuevo_pedido("domicilios", "domicilio", "x", [], 1000, {"nombre": "Viejo"})
    db.conn().execute("UPDATE pedidos SET creado=? WHERE restaurante='domicilios'", (time.time() - 7 * 3600,))
    db.nuevo_pedido("domicilios", "domicilio", "y", [], 1000, {"nombre": "Nuevo"})
    db.borrar_pedidos_viejos("domicilios", 6 * 3600)
    assert [p["entrega"]["nombre"] for p in db.pedidos("domicilios")] == ["Nuevo"]


def test_la_caja_de_domicilios_tiene_su_propio_pin(c, axtra):
    c.get("/v1/panel/domicilios", headers=PIN)
    c.get("/v1/panel/demo", headers=PIN)
    pines = [j["restaurante"] for ruta, j in axtra.llamadas if ruta == "/pin"]
    assert pines == ["domicilios", "demo"]          # cada restaurante pregunta por su PIN (APEX_PIN_<ID>)
