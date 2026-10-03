"""Orbes de negocios (Apex Play) con el motor económico de Axtra: mesas, turnos de voz, herramientas,
frases grabadas, costo en pesos, respaldo y panel."""
import base64
import copy
import json

import pytest
from fastapi.testclient import TestClient

from servidor.apex import app as apex_app, config, db, orbe

ORIGEN = {"Origin": "https://api.axtra.chat"}
PIN = {"X-Apex-Pin": "4321"}
WEBM = b"\x1aE\xdf\xa3" + b"\x00" * 3000


class Resp:
    def __init__(self, datos=None, contenido=b"", headers=None, status=200):
        self.datos, self.content, self.headers, self.status_code = datos, contenido, headers or {}, status
        self.text = json.dumps(datos) if datos is not None else ""

    def json(self):
        return self.datos


class AxtraFalso:
    """Simula la ranura de Axtra: oído, cerebro (con un guion de respuestas) y voz."""

    def __init__(self):
        self.oido = "quiero un ajiaco"
        self.guion = []          # mensajes que devolverá el cerebro, en orden
        self.llamadas = []
        self.caido = False

    def __call__(self, ruta, **kw):
        self.llamadas.append((ruta, copy.deepcopy(kw.get("json"))))
        if self.caido:
            raise orbe.SinRanura("Axtra caído")
        if ruta == "/pin":
            return Resp({"ok": kw["json"]["pin"] == "4321"})
        if ruta == "/oido":
            return Resp({"texto": self.oido, "segundos": 2.5, "proveedor": "groq"})
        if ruta == "/pensar":
            m = self.guion.pop(0) if self.guion else {"role": "assistant", "content": "Con gusto.", "tool_calls": []}
            return Resp({"mensaje": m, "uso": {"entrada": 3000, "salida": 60}, "proveedor": "groq"})
        if ruta == "/voz":
            return Resp(contenido=b"ID3" + kw["json"]["texto"].encode(), headers={"X-Proveedor": "google",
                                                                               "X-Caracteres": str(len(kw["json"]["texto"]))})
        raise AssertionError(ruta)


def herramienta(nombre, args=None, i="1"):
    return {"role": "assistant", "content": "", "tool_calls": [
        {"id": f"call_{i}", "type": "function", "function": {"name": nombre, "arguments": json.dumps(args or {})}}]}


def texto(t):
    return {"role": "assistant", "content": t, "tool_calls": []}


@pytest.fixture
def axtra(monkeypatch):
    falso = AxtraFalso()
    monkeypatch.setattr(orbe, "_ranura", falso)
    return falso


@pytest.fixture
def c(axtra, monkeypatch):
    original = config.restaurante
    monkeypatch.setattr(config, "restaurante", lambda rid: {**original(rid), "ejemplo": False} if original(rid) else None)
    con = db.conn()
    for t in ("mesas", "sesiones", "pedidos", "llamadas", "consumos"):
        con.execute(f"DELETE FROM {t}")
    con.commit()
    for f in config.AUDIO_DIR.glob("*.mp3"):
        f.unlink()
    apex_app._cubos.clear()
    return TestClient(apex_app.app)


def abrir(c, mesa="1", abierta=True):
    assert c.post("/v1/panel/demo/mesa", json={"mesa": mesa, "abierta": abierta}, headers=PIN).status_code == 200


def sesion(c, mesa="1", **extra):
    return c.post("/v1/sesion", json={"restaurante": "demo", "mesa": mesa, **extra}, headers=ORIGEN)


def turno(c, s, audio=WEBM):
    return c.post("/v1/turno", content=audio, headers={**ORIGEN, "Content-Type": "audio/webm",
                                                       "X-Apex-Sesion": s["sesion"], "X-Apex-Secreto": s["secreto"]})


def accion(c, s, tipo, **extra):
    return c.post("/v1/accion", json={"sesion": s["sesion"], "secreto": s["secreto"], "tipo": tipo, **extra}, headers=ORIGEN)


@pytest.fixture
def mesas_con_llave(monkeypatch):
    """Un restaurante normal: las mesas las abre el mesero (el demo las tiene siempre abiertas)."""
    original = config.restaurante
    monkeypatch.setattr(config, "restaurante", lambda rid: {**original(rid), "mesas_siempre_abiertas": False} if original(rid) else None)


def test_mesa_cerrada_no_da_sesion(c, mesas_con_llave):
    r = sesion(c)
    assert r.status_code == 403 and "cerrada" in r.json()["error"]


def test_demo_tiene_mesas_siempre_abiertas(c):
    assert sesion(c, "7").status_code == 200


def test_sesion_trae_frases_grabadas(c):
    abrir(c)
    s = sesion(c).json()
    assert s["frases"]["saludo"] == "/v1/frase/demo/saludo" and not s["sin_voz"]
    assert "token" not in s and "clave" not in json.dumps(s)        # la puerta no tiene ninguna llave


def test_frase_fija_se_genera_una_vez(c, axtra):
    a = c.get("/v1/frase/demo/eleccion")
    b = c.get("/v1/frase/demo/eleccion")
    assert a.content == b.content == "ID3Muy buena elección.".encode()
    assert [x for x, _ in axtra.llamadas].count("/voz") == 1        # la segunda vez sale del caché: gratis
    assert c.get("/v1/frase/demo/inventada").status_code == 404


def test_origen_no_permitido(c):
    abrir(c)
    r = c.post("/v1/sesion", json={"restaurante": "demo", "mesa": "1"}, headers={"Origin": "https://malo.com"})
    assert r.status_code == 403
    pre = c.options("/v1/turno", headers={"Origin": "https://malo.com", "Access-Control-Request-Method": "POST"})
    assert pre.status_code == 403
    ok = c.options("/v1/turno", headers={**ORIGEN, "Access-Control-Request-Method": "POST"})
    assert ok.status_code == 204 and "X-Apex-Sesion" in ok.headers["access-control-allow-headers"]


def test_una_sesion_por_mesa_y_retomar(c):
    abrir(c)
    s1 = sesion(c).json()
    assert sesion(c).status_code == 409                 # otro teléfono con la foto del QR
    assert sesion(c, anterior={"sesion": s1["sesion"], "secreto": s1["secreto"]}).status_code == 200


def test_turno_completo_con_herramientas(c, axtra):
    abrir(c, "2")
    s = sesion(c, "2").json()
    axtra.guion = [herramienta("agregar_plato", {"plato_id": "ajiaco"}), texto("Excelente, un ajiaco santafereño.")]
    r = turno(c, s).json()
    assert base64.b64decode(r["audio"]) == "ID3Excelente, un ajiaco santafereño.".encode()
    assert r["pedido"]["platos"] == [{"id": "ajiaco", "plato": "Ajiaco santafereño", "cantidad": 1}]
    # El cerebro recibió el menú, las reglas y las herramientas; y la respuesta de la herramienta
    pensar = [j for ruta, j in axtra.llamadas if ruta == "/pensar"]
    assert "Bandeja paisa" in pensar[0]["sistema"] and "38 mil pesos" in pensar[0]["sistema"]
    assert {h["function"]["name"] for h in pensar[0]["herramientas"]} >= {"agregar_plato", "confirmar_pedido", "llamar_mesero"}
    assert pensar[1]["mensajes"][-1]["role"] == "tool" and "Ajiaco" in pensar[1]["mensajes"][-1]["content"]


def test_botones_pedir_y_confirmar_por_voz(c, axtra):
    abrir(c, "3")
    s = sesion(c, "3").json()
    r = accion(c, s, "pedir", plato_id="bandeja", cantidad=2).json()
    assert r["frase"] == "/v1/frase/demo/sugerir" and r["sugerir"] == "limonada" and r["pedido"]["total_numero"] == 76000
    assert "limonada" in r["texto"]
    assert not [x for x, _ in axtra.llamadas if x == "/pensar"]      # la sugerencia es una frase grabada: no gasta cerebro
    axtra.guion = [texto("Su pedido: dos bandejas paisas, 76 mil pesos. ¿Lo confirma?")]
    r = accion(c, s, "pedir_todo").json()
    assert b"Lo confirma" in base64.b64decode(r["audio"])
    axtra.oido = "sí, confírmelo"
    axtra.guion = [herramienta("confirmar_pedido"), texto("Fue un placer atenderlo, si tiene alguna duda indíqueme.")]
    r = turno(c, s).json()
    assert r["despedida"] is True and r["pedido"]["pedido_numero"]
    p = c.get("/v1/panel/demo", headers=PIN).json()
    assert p["pedidos"][0]["mesa"] == "3" and p["pedidos"][0]["total"] == 76000
    assert p["uso_mes"]["pedidos"] == 1 and p["uso_mes"]["ventas"] == 76000


def test_pedir_todo_vacio_y_plato_inexistente(c):
    abrir(c)
    s = sesion(c).json()
    assert accion(c, s, "pedir_todo").json()["frase"] == "/v1/frase/demo/vacio"
    assert accion(c, s, "pedir", plato_id="pizza").status_code == 409


def test_no_entendio_pide_repetir_sin_gastar_cerebro(c, axtra):
    abrir(c)
    s = sesion(c).json()
    axtra.oido = " . "
    assert turno(c, s).json()["frase"] == "/v1/frase/demo/repetir"
    assert "/pensar" not in [x for x, _ in axtra.llamadas]


def test_precio_segun_tipo_de_voz():
    assert orbe.precio_voz("google", "es-US-Chirp3-HD-Charon") == 30.0
    assert orbe.precio_voz("google", "es-US-Neural2-B") == 16.0
    assert orbe.precio_voz("google", "es-US-Standard-A") == 4.0
    assert orbe.precio_voz("edge", "x") == 0.0


def test_costo_en_pesos(c):
    abrir(c)
    s = sesion(c).json()
    turno(c, s)
    gasto = db.uso_mes("demo")["gasto_por_pieza"]
    assert gasto["oido"] == pytest.approx(10 / 3600 * 0.111 * 4000, abs=0.01)         # mínimo 10 s (whisper-large-v3)
    assert gasto["cerebro"] == pytest.approx((3000 * 0.075 + 60 * 0.30) / 1e6 * 4000, abs=0.01)
    assert gasto["voz"] == pytest.approx(len("Con gusto.") * 16 / 1e6 * 4000, abs=0.01)   # voz Neural2
    assert db.gasto_mes("demo") < 5                    # un turno cuesta unos pocos pesos


def test_tope_del_mes_usa_solo_frases_y_mesero(c, axtra, monkeypatch):
    abrir(c)
    s = sesion(c).json()
    r = config.restaurante("demo")
    monkeypatch.setattr(config, "restaurante", lambda rid: {**r, "topes": {**r["topes"], "tope_cop_mes": 0}})
    res = turno(c, s).json()
    assert res["sin_voz"] and res["frase"] == "/v1/frase/demo/sin_voz"
    assert "/oido" not in [x for x, _ in axtra.llamadas]   # no gasta nada más
    assert accion(c, s, "mesero").json()["frase"] == "/v1/frase/demo/mesero"


def test_si_axtra_falla_respaldo_y_mesero(c, axtra):
    abrir(c)
    s = sesion(c).json()
    axtra.caido = True
    res = turno(c, s).json()
    assert res["sin_voz"] is True
    assert accion(c, s, "mesero").status_code == 200                     # el mesero siempre se puede llamar
    axtra.caido = False
    assert c.get("/v1/panel/demo", headers=PIN).json()["llamadas"][0]["mesa"] == "1"


def test_cerrar_mesa_corta_la_conversacion(c):
    abrir(c, "4")
    s = sesion(c, "4").json()
    abrir(c, "4", abierta=False)
    assert turno(c, s).status_code == 410


def test_secreto_falso(c):
    abrir(c)
    s = sesion(c).json()
    assert turno(c, {**s, "secreto": "x" * 20}).status_code == 401


def test_vigilante_cierra_sesiones_quietas(c):
    abrir(c, "5")
    s = sesion(c, "5").json()
    con = db.conn()
    con.execute("UPDATE sesiones SET actividad = actividad - 600"); con.commit()
    apex_app.revisar_sesiones()
    assert db.sesion(s["sesion"])["motivo_fin"] == "sin actividad"


def test_panel_pin_lo_guarda_axtra(c, axtra):
    assert c.get("/v1/panel/demo").status_code == 401
    assert c.get("/v1/panel/demo", headers={"X-Apex-Pin": "0000"}).status_code == 401
    assert ("/pin", {"restaurante": "demo", "pin": "0000"}) in axtra.llamadas


def test_pin_bloqueado_tras_muchos_intentos(c):
    for _ in range(8):
        c.get("/v1/panel/demo", headers={"X-Apex-Pin": "1111"})
    assert c.get("/v1/panel/demo", headers=PIN).status_code == 429      # ni el correcto pasa durante el bloqueo


def test_limite_de_peticiones(c):
    abrir(c)
    assert 429 in [sesion(c).status_code for _ in range(8)]


def test_historial_no_parte_herramientas():
    msgs = [{"role": "user", "content": "x"}] + [herramienta("ver_pedido"), {"role": "tool", "tool_call_id": "call_1", "content": "{}"},
                                                 texto("ok"), {"role": "user", "content": "y"}] * 8
    abrir_db = db.conn()
    abrir_db.execute("INSERT OR REPLACE INTO sesiones (id, secreto, restaurante, mesa, creada) VALUES ('h','s','demo','1',0)")
    abrir_db.commit()
    db.guardar_historial("h", msgs)
    guardado = db.historial("h")
    assert guardado[0]["role"] == "user" and len(guardado) <= 24


def test_menu_y_paginas(c):
    m = c.get("/v1/menu/demo").json()
    assert m["nombre"] == "Su restaurante" and len(m["menu"]) == 5 and "personalidad" not in m
    assert next(p for p in m["menu"] if p["id"] == "volcan")["antes"] == 19000
    assert c.get("/demo").status_code == 200 and c.get("/panel").status_code == 200
    assert c.get("/web/apex-voz.js").status_code == 200
    assert c.get("/qr").status_code == 200 and c.get("/web/qrcode.js").status_code == 200
    assert c.get("/v1/mesas/demo").json()["mesas"][0] == "1"
    assert c.get("/", follow_redirects=False).headers["location"] == "/demo"


def test_botones_quitar_oferta_y_enviar_sin_cerebro(c, axtra):
    s = sesion(c, "4").json()
    accion(c, s, "pedir", plato_id="ajiaco")                          # sugiere la limonada (una sola vez)
    assert accion(c, s, "pedir", plato_id="omelet").json()["frase"] == "/v1/frase/demo/eleccion"
    r = accion(c, s, "quitar", plato_id="omelet").json()               # se equivocó: lo quita
    assert r["frase"] == "/v1/frase/demo/quitado" and [p["id"] for p in r["pedido"]["platos"]] == ["ajiaco"]
    r = accion(c, s, "confirmar").json()                                # antes de enviar ofrece el postre
    assert r["frase"] == "/v1/frase/demo/oferta" and r["oferta"] == "volcan" and not r.get("despedida")
    r = accion(c, s, "confirmar").json()                                # «No, enviar así»: no insiste
    assert r["frase"] == "/v1/frase/demo/enviado" and r["despedida"] is True and r["pedido"]["pedido_numero"]
    assert not [x for x, _ in axtra.llamadas if x == "/pensar"]
    assert c.get("/v1/panel/demo", headers=PIN).json()["pedidos"][0]["total"] == 32000


def test_oferta_aceptada_se_suma_al_pedido(c):
    s = sesion(c, "5").json()
    accion(c, s, "pedir", plato_id="limonada")
    assert accion(c, s, "confirmar").json()["oferta"] == "volcan"
    r = accion(c, s, "confirmar", plato_id="volcan").json()             # «Sí, agregarlo»
    assert r["despedida"] and r["pedido"]["total_numero"] == 12000 + 14000


def test_modo_ejemplo_sin_mesas_y_muchas_personas_a_la_vez(axtra):
    """El modelo de ejemplo: un solo link, sin mesas; cada persona tiene su conversación."""
    apex_app._cubos.clear()
    cli = TestClient(apex_app.app)
    a = cli.post("/v1/sesion", json={"restaurante": "demo", "mesa": "ejemplo"}, headers=ORIGEN).json()
    b = cli.post("/v1/sesion", json={"restaurante": "demo", "mesa": "ejemplo"}, headers=ORIGEN).json()
    assert a["ejemplo"] and a["sesion"] != b["sesion"]
    accion(cli, a, "pedir", plato_id="omelet")
    accion(cli, a, "confirmar")
    assert accion(cli, a, "confirmar").json()["pedido"]["pedido_numero"]
    assert accion(cli, b, "pedir_todo").json()["frase"] == "/v1/frase/demo/vacio"     # el pedido de A no se mezcla con B


def test_paginas_sin_cache_y_aguantan_peticiones_raras(c):
    r = c.get("/demo", headers={"Range": "bytes=abc"})                   # una vista previa de enlace rara
    assert r.status_code == 200 and r.headers["cache-control"] == "no-cache"
    assert c.get("/web/apex-voz.js").headers["cache-control"] == "no-cache"
    assert "apex-voz.js?v=" in r.text
    assert c.get("/qr", headers={"Range": "bytes=abc"}).status_code == 200


def llamadas(*pares):
    """Un mensaje del cerebro con varias herramientas a la vez."""
    return {"role": "assistant", "content": "", "tool_calls": [
        {"id": f"c{i}", "type": "function", "function": {"name": n, "arguments": json.dumps(a)}} for i, (n, a) in enumerate(pares)]}


def _platos(c):
    return {p["plato"]: p["cantidad"] for p in c}


def test_el_orbe_no_agrega_lo_que_el_cliente_no_pidio(c, axtra):
    s = sesion(c, "1").json()
    axtra.oido = "quiero un ajiaco"
    # El cerebro se equivoca: agrega el ajiaco dos veces, con cantidad 3, y una limonada que nadie pidió
    axtra.guion = [llamadas(("agregar_plato", {"plato_id": "ajiaco", "cantidad": 3}), ("agregar_plato", {"plato_id": "ajiaco"}),
                            ("agregar_plato", {"plato_id": "limonada"})), texto("Listo, un ajiaco.")]
    r = turno(c, s).json()
    assert _platos(r["pedido"]["platos"]) == {"Ajiaco santafereño": 1}


def test_la_cantidad_es_la_que_dijo_el_cliente(c, axtra):
    s = sesion(c, "1").json()
    axtra.oido = "me trae dos ajiacos y una limonada de coco"
    axtra.guion = [llamadas(("agregar_plato", {"plato_id": "ajiaco"}), ("agregar_plato", {"plato_id": "limonada", "cantidad": 2})),
                   texto("Con gusto.")]
    assert _platos(turno(c, s).json()["pedido"]["platos"]) == {"Ajiaco santafereño": 2, "Limonada de coco": 1}


def test_si_a_la_sugerencia_si_agrega_y_no_no(c, axtra):
    s = sesion(c, "1").json()
    accion(c, s, "pedir", plato_id="bandeja")                       # el orbe sugirió la limonada
    axtra.oido = "no gracias"
    axtra.guion = [herramienta("agregar_plato", {"plato_id": "limonada"}), texto("Listo.")]
    assert _platos(turno(c, s).json()["pedido"]["platos"]) == {"Bandeja paisa": 1}
    s2 = sesion(c, "2").json()
    accion(c, s2, "pedir", plato_id="bandeja")
    axtra.oido = "sí, por favor"
    axtra.guion = [herramienta("agregar_plato", {"plato_id": "limonada"}), texto("Listo.")]
    assert _platos(turno(c, s2).json()["pedido"]["platos"]) == {"Bandeja paisa": 1, "Limonada de coco": 1}


def test_confirmar_por_voz_trae_la_factura_completa(c, axtra):
    s = sesion(c, "1").json()
    accion(c, s, "pedir", plato_id="ajiaco")
    accion(c, s, "pedir", plato_id="limonada")
    axtra.oido = "sí, confírmelo"
    # Tras confirmar, el cerebro mira el carrito (ya vacío): la factura debe ser la del pedido enviado
    axtra.guion = [herramienta("confirmar_pedido"), herramienta("ver_pedido", i="2"), texto("¡Listo!")]
    r = turno(c, s).json()
    assert r["pedido"]["pedido_numero"] and r["pedido"]["total_numero"] == 44000
    assert _platos(r["pedido"]["platos"]) == {"Ajiaco santafereño": 1, "Limonada de coco": 1}


def test_carta_y_frases_en_otro_idioma(c):
    m = c.get("/v1/menu/demo?idioma=en").json()
    assert m["idioma"] == "en" and {i["codigo"] for i in m["idiomas"]} == {"es", "en", "pt", "de", "ru", "ja"}
    assert next(p for p in m["menu"] if p["id"] == "limonada")["nombre"] == "Coconut lemonade"
    s = c.post("/v1/sesion", json={"restaurante": "demo", "mesa": "1", "idioma": "ja"}, headers=ORIGEN).json()
    assert s["frases"]["saludo"].endswith("?idioma=ja") and "オーブ" in s["saludo"]
    r = accion(c, s, "pedir", plato_id="bandeja").json()
    assert "ココナッツ" in r["texto"] and r["frase"].endswith("?idioma=ja")
    assert "いらっしゃいませ".encode() in c.get(s["frases"]["saludo"]).content       # la voz falsa repite el texto


def test_cambiar_idioma_en_la_conversacion(c, axtra):
    s = sesion(c, "1").json()
    r = c.post("/v1/idioma", json={**{k: s[k] for k in ("sesion", "secreto")}, "idioma": "en"}, headers=ORIGEN).json()
    assert "Welcome" in r["saludo"]
    axtra.oido = "two ajiacos please"
    axtra.guion = [herramienta("agregar_plato", {"plato_id": "ajiaco"}), texto("Two ajiacos.")]
    t = turno(c, s).json()
    assert _platos(t["pedido"]["platos"]) == {"Ajiaco santafereño": 2}
    pensar = [j for ruta, j in axtra.llamadas if ruta == "/pensar"][-1]
    assert "Habla SIEMPRE en English" in pensar["sistema"] and "Coconut lemonade (Limonada de coco)" in pensar["sistema"]
    oido = [kw for ruta, kw in axtra.llamadas if ruta == "/oido"]
    assert c.post("/v1/idioma", json={**{k: s[k] for k in ("sesion", "secreto")}, "idioma": "xx"}, headers=ORIGEN).status_code == 404


def test_el_oido_recibe_idioma_y_nombres_de_los_platos(c, axtra, monkeypatch):
    vistos = []
    original = orbe._ranura
    monkeypatch.setattr(orbe, "_ranura", lambda ruta, **kw: (vistos.append((ruta, kw.get("params"))), original(ruta, **kw))[1])
    s = c.post("/v1/sesion", json={"restaurante": "demo", "mesa": "1", "idioma": "de"}, headers=ORIGEN).json()
    turno(c, s)
    params = next(p for ruta, p in vistos if ruta == "/oido")
    assert params["idioma"] == "de" and "Kokos-Limonade" in params["pista"] and "Bandeja paisa" in params["pista"]


def test_control_de_pedidos_en_japones_y_ruso(c, axtra):
    s = c.post("/v1/sesion", json={"restaurante": "demo", "mesa": "1", "idioma": "ja"}, headers=ORIGEN).json()
    axtra.oido = "アヒアコを二つください"
    axtra.guion = [llamadas(("agregar_plato", {"plato_id": "ajiaco"}), ("agregar_plato", {"plato_id": "volcan"})), texto("はい")]
    assert _platos(turno(c, s).json()["pedido"]["platos"]) == {"アヒアコ": 2}
    s2 = c.post("/v1/sesion", json={"restaurante": "demo", "mesa": "2", "idioma": "ru"}, headers=ORIGEN).json()
    accion(c, s2, "pedir", plato_id="omelet")                         # el orbe ofrece el лимонад
    axtra.oido = "да, пожалуйста"
    axtra.guion = [herramienta("agregar_plato", {"plato_id": "limonada"}), texto("Хорошо.")]
    assert _platos(turno(c, s2).json()["pedido"]["platos"]) == {"Омлет ранчеро": 1, "Кокосовый лимонад": 1}
