"""Apex Play: sesión del orbe, mesas, herramientas, pedidos, orígenes, topes y panel."""
import json

import pytest
from fastapi.testclient import TestClient

from servidor.apex import app as apex_app, config, db, orbe

ORIGEN = {"Origin": "https://api.axtra.chat"}
PIN = {"X-Apex-Pin": "4321"}


class RespuestaFalsa:
    def __init__(self, datos, status=200):
        self.datos, self.status_code, self.ok, self.text = datos, status, status < 400, json.dumps(datos)

    def json(self):
        return self.datos


@pytest.fixture
def openai(monkeypatch):
    llamadas = []

    def falso_post(url, json=None, headers=None, timeout=None):
        llamadas.append({"url": url, "json": json, "auth": (headers or {}).get("Authorization")})
        if url.endswith("/realtime/client_secrets"):
            return RespuestaFalsa({"value": "ek_prueba", "expires_at": 9999999999})
        return RespuestaFalsa({})

    monkeypatch.setattr(orbe.requests, "post", falso_post)
    return llamadas


@pytest.fixture
def c(openai):
    con = db.conn()
    for t in ("mesas", "sesiones", "pedidos", "llamadas"):
        con.execute(f"DELETE FROM {t}")
    con.commit()
    apex_app._cubos.clear()
    return TestClient(apex_app.app)


def abrir(c, mesa="1", abierta=True):
    assert c.post("/v1/panel/demo/mesa", json={"mesa": mesa, "abierta": abierta}, headers=PIN).status_code == 200


def sesion(c, mesa="1", **extra):
    return c.post("/v1/sesion", json={"restaurante": "demo", "mesa": mesa, **extra}, headers=ORIGEN)


def herr(c, s, nombre, args=None):
    return c.post("/v1/herramienta", json={"sesion": s["sesion"], "secreto": s["secreto"], "nombre": nombre,
                                           "argumentos": args or {}}, headers=ORIGEN).json()


def test_mesa_cerrada_no_da_sesion(c, openai):
    r = sesion(c)
    assert r.status_code == 403 and "cerrada" in r.json()["error"]
    assert not openai                                   # ni siquiera se llamó a OpenAI


def test_sesion_entrega_token_efimero_configurado(c, openai):
    abrir(c)
    r = sesion(c).json()
    assert r["token"] == "ek_prueba" and r["modelo"] == "gpt-realtime-2.1-mini" and r["frases"]["eleccion"]
    pedido = openai[0]
    assert pedido["url"].endswith("/v1/realtime/client_secrets") and pedido["auth"] == "Bearer sk-prueba"
    s = pedido["json"]["session"]
    assert s["type"] == "realtime" and s["audio"]["output"]["voice"] == "marin"
    assert {t["name"] for t in s["tools"]} >= {"agregar_plato", "ver_pedido", "confirmar_pedido", "llamar_mesero"}
    assert "Bandeja paisa" in s["instructions"] and "mesa 1" in s["instructions"]
    assert pedido["json"]["expires_after"]["seconds"] == 60
    assert "sk-prueba" not in json.dumps(r)             # la llave real nunca sale


def test_origen_no_permitido(c):
    abrir(c)
    r = c.post("/v1/sesion", json={"restaurante": "demo", "mesa": "1"}, headers={"Origin": "https://malo.com"})
    assert r.status_code == 403
    pre = c.options("/v1/sesion", headers={"Origin": "https://malo.com", "Access-Control-Request-Method": "POST"})
    assert pre.status_code == 403 and "access-control-allow-origin" not in pre.headers
    ok = c.options("/v1/sesion", headers={**ORIGEN, "Access-Control-Request-Method": "POST"})
    assert ok.status_code == 204 and ok.headers["access-control-allow-origin"] == "https://api.axtra.chat"


def test_una_sesion_por_mesa_y_retomar(c):
    abrir(c)
    s1 = sesion(c).json()
    assert sesion(c).status_code == 409                 # otro teléfono con la foto del QR
    s2 = sesion(c, anterior={"sesion": s1["sesion"], "secreto": s1["secreto"]})
    assert s2.status_code == 200                        # el mismo teléfono al recargar la página
    assert db.sesion(s1["sesion"])["fin"]


def test_flujo_completo_de_pedido(c):
    abrir(c, "2")
    s = sesion(c, "2").json()
    assert herr(c, s, "agregar_plato", {"plato_id": "ajiaco"})["agregado"] == "Ajiaco santafereño"
    r = herr(c, s, "agregar_plato", {"plato_id": "Bandeja Paisa", "cantidad": 2})   # por nombre también sirve
    assert r["total_numero"] == 32000 + 2 * 38000
    assert herr(c, s, "agregar_plato", {"plato_id": "pizza"})["ok"] is False        # no inventa platos
    assert herr(c, s, "quitar_plato", {"plato_id": "ajiaco"})["total_numero"] == 76000
    assert herr(c, s, "ver_pedido")["platos"] == [{"plato": "Bandeja paisa", "cantidad": 2}]
    conf = herr(c, s, "confirmar_pedido")
    assert conf["ok"] and conf["pedido_numero"] and "placer" in conf["siguiente"]
    assert herr(c, s, "confirmar_pedido")["ok"] is False                          # no se duplica
    herr(c, s, "llamar_mesero", {"motivo": "la cuenta"})
    p = c.get("/v1/panel/demo", headers=PIN).json()
    assert p["pedidos"][0]["mesa"] == "2" and p["pedidos"][0]["total"] == 76000
    assert p["llamadas"][0]["motivo"] == "la cuenta"


def test_cerrar_mesa_corta_y_bloquea(c, openai):
    abrir(c, "3")
    s = sesion(c, "3").json()
    c.post("/v1/sesion/llamada", json={"sesion": s["sesion"], "secreto": s["secreto"], "call_id": "rtc_abc123"},
           headers=ORIGEN)
    abrir(c, "3", abierta=False)
    assert any(x["url"].endswith("/realtime/calls/rtc_abc123/hangup") for x in openai)
    r = c.post("/v1/herramienta", json={"sesion": s["sesion"], "secreto": s["secreto"], "nombre": "agregar_plato",
                                        "argumentos": {"plato_id": "ajiaco"}}, headers=ORIGEN)
    assert r.status_code == 410


def test_secreto_falso(c):
    abrir(c)
    s = sesion(c).json()
    r = c.post("/v1/herramienta", json={"sesion": s["sesion"], "secreto": "x" * 20, "nombre": "ver_pedido"},
               headers=ORIGEN)
    assert r.status_code == 401


def test_fin_registra_uso_y_costo(c):
    abrir(c)
    s = sesion(c).json()
    uso = {"audio_in": 100_000, "audio_out": 50_000, "texto_in": 10_000}
    r = c.post("/v1/sesion/fin", content=json.dumps({"sesion": s["sesion"], "secreto": s["secreto"], "uso": uso}),
               headers={**ORIGEN, "Content-Type": "text/plain"})          # así llega con sendBeacon
    assert r.status_code == 200
    esperado = (100_000 * 10 + 50_000 * 20 + 10_000 * 0.6) / 1e6
    assert db.uso_mes("demo")["usd"] == pytest.approx(esperado, abs=1e-6)
    assert sesion(c).status_code == 200                 # la mesa quedó libre


def test_topes_del_mes(c, monkeypatch):
    abrir(c)
    r = config.restaurante("demo")
    monkeypatch.setattr(config, "restaurante", lambda rid: {**r, "topes": {**r["topes"], "sesiones_mes": 1}})
    assert sesion(c).status_code == 200
    c.post("/v1/panel/demo/mesa", json={"mesa": "1", "abierta": False}, headers=PIN)
    abrir(c)
    assert sesion(c).status_code == 429


def test_vigilante_corta_sesiones_largas_y_abandonadas(c, openai):
    abrir(c, "4"); abrir(c, "5")
    larga, abandonada = sesion(c, "4").json(), sesion(c, "5").json()
    db.poner_call_id(larga["sesion"], "rtc_largo")
    con = db.conn()
    con.execute("UPDATE sesiones SET creada = creada - 3600"); con.commit()
    apex_app.revisar_sesiones()
    assert db.sesion(larga["sesion"])["motivo_fin"] == "tope de minutos por sesión"
    assert db.sesion(abandonada["sesion"])["motivo_fin"] == "no conectó"
    assert any(x["url"].endswith("/rtc_largo/hangup") for x in openai)


def test_panel_pide_pin(c):
    assert c.get("/v1/panel/demo").status_code == 401
    assert c.get("/v1/panel/demo", headers={"X-Apex-Pin": "0000"}).status_code == 401


def test_limite_de_peticiones(c):
    abrir(c)
    codigos = [sesion(c).status_code for _ in range(8)]
    assert 429 in codigos


def test_menu_y_paginas(c):
    m = c.get("/v1/menu/demo").json()
    assert m["nombre"] == "La Mesa de Apex" and len(m["menu"]) == 3 and "personalidad" not in m
    assert c.get("/demo").status_code == 200 and c.get("/panel").status_code == 200
    assert c.get("/web/apex-voz.js").status_code == 200
