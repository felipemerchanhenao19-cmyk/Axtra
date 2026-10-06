"""Ranura privada de Axtra (tarjeta madre): oído, cerebro con respaldo, voz con respaldo, PIN y Negocios."""
import base64

import pytest
from fastapi.testclient import TestClient

from servidor import app as app_mod, config, ranura, voz


class R:
    def __init__(self, datos, status=200):
        self.datos, self.status_code, self.text = datos, status, str(datos)

    def json(self):
        return self.datos

    def raise_for_status(self):
        if self.status_code >= 400:
            raise ranura.requests.HTTPError(str(self.status_code))


@pytest.fixture
def c():
    return TestClient(ranura.app)


def test_no_acepta_nada_que_venga_por_cloudflare(c):
    assert c.get("/salud", headers={"cf-ray": "abc"}).status_code == 404
    assert c.get("/salud").status_code == 200


def test_cerebro_groq_y_respaldo_gemini(c, monkeypatch):
    monkeypatch.setattr(config, "GROQ_API_KEY", "g")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "m")
    urls = []

    def post(url, json=None, headers=None, timeout=None, **kw):
        urls.append(url)
        if "groq" in url:
            return R({"error": "caído"}, 503)
        return R({"choices": [{"message": {"content": "Hola", "tool_calls": None}}],
                  "usage": {"prompt_tokens": 100, "completion_tokens": 5}})

    monkeypatch.setattr(ranura.requests, "post", post)
    r = c.post("/pensar", json={"sistema": "s", "mensajes": [{"role": "user", "content": "hola"}],
                                "herramientas": [{"type": "function", "function": {"name": "x"}}]}).json()
    assert r["proveedor"] == "gemini" and r["mensaje"]["content"] == "Hola" and r["uso"]["entrada"] == 100
    assert "groq" in urls[0] and "groq" in urls[1] and "generativelanguage" in urls[2]     # un reintento a Groq


def test_voz_google_y_respaldo_gratis(c, monkeypatch):
    monkeypatch.setattr(config, "GOOGLE_TTS_API_KEY", "k")
    monkeypatch.setattr(ranura.requests, "post", lambda *a, **k: R({"audioContent": base64.b64encode(b"MP3google").decode()}))
    r = c.post("/voz", json={"texto": "Muy buena elección."})
    assert r.content == b"MP3google" and r.headers["x-proveedor"] == "google" and r.headers["x-caracteres"] == "19"
    monkeypatch.setattr(ranura.requests, "post", lambda *a, **k: R({"error": "sin saldo"}, 403))
    monkeypatch.setattr(voz, "sintetizar", lambda t, voz=None, **k: b"MP3edge:" + voz.encode())
    r = c.post("/voz", json={"texto": "Hola", "voz_edge": "es-CO-SalomeNeural"})
    assert r.content == b"MP3edge:es-CO-SalomeNeural" and r.headers["x-proveedor"] == "edge"


def test_oido_groq(c, monkeypatch):
    monkeypatch.setattr(config, "GROQ_API_KEY", "g")
    monkeypatch.setattr(ranura.requests, "post", lambda *a, **k: R({"text": " quiero un ajiaco ", "duration": 2.4}))
    r = c.post("/oido", content=b"\x1aE\xdf\xa3" + b"\0" * 100, headers={"Content-Type": "application/octet-stream"}).json()
    assert r == {"texto": "quiero un ajiaco", "segundos": 2.4, "proveedor": "groq"}


def test_pin(c, monkeypatch):
    assert c.post("/pin", json={"restaurante": "demo", "pin": "4321"}).json()["ok"] is True
    assert c.post("/pin", json={"restaurante": "demo", "pin": "0000"}).json()["ok"] is False
    assert c.post("/pin", json={"restaurante": "otro", "pin": "1234"}).status_code == 503


def test_negocios_en_axtra(monkeypatch):
    monkeypatch.setattr(config, "MODO_DESARROLLO", True)
    lista = TestClient(app_mod.app).get("/api/negocios").json()
    demo = next(n for n in lista if n["id"] == "demo")
    assert demo["nombre"] == "Su restaurante" and demo["tope_cop"] == 80000 and demo["mesas"] == 10
    assert {"conversaciones", "pedidos", "ventas", "gasto_cop"} <= set(demo["uso"])


def test_formatos_de_audio_de_cualquier_celular():
    from servidor import oido
    assert oido.formato(b"\x00\x00\x00\x00" + b"\x1aE\xdf\xa3" + b"\x00" * 50) == "webm"     # cabecera un poco corrida
    assert oido.formato(b"\x00\x00\x00\x1cftypM4A " + b"\x00" * 20) == "mp4"
    assert oido.formato(b"ID3\x04" + b"\x00" * 20) == "mp3"
    assert oido.formato(b"\x00" * 30, "audio/webm;codecs=opus") == "webm"                     # lo dice el navegador
    assert oido.formato(b"\x00" * 30, "audio/mp4") == "mp4"
    assert oido.formato(b"\x00" * 30) == ""


def test_voz_de_respaldo_respeta_la_velocidad(c, monkeypatch):
    from servidor import voz
    visto = {}
    monkeypatch.setattr(voz, "sintetizar", lambda texto, **kw: (visto.update(kw), b"ID3")[1])
    monkeypatch.setattr(ranura.config, "GOOGLE_TTS_API_KEY", "")
    assert c.post("/voz", json={"texto": "hola", "velocidad": 1.15}).headers["x-proveedor"] == "edge"
    assert visto["ritmo"] == "+15%"



def test_groq_rechaza_una_vez_y_el_reintento_funciona(c, monkeypatch):
    monkeypatch.setattr(config, "GROQ_API_KEY", "g")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    monkeypatch.setattr(ranura.time, "sleep", lambda s: None)
    veces = []

    def post(url, json=None, headers=None, timeout=None, **kw):
        veces.append(url)
        if len(veces) == 1:
            return R({"error": {"code": "tool_use_failed"}}, 400)
        return R({"choices": [{"message": {"content": "Listo", "tool_calls": None}}], "usage": {}})

    monkeypatch.setattr(ranura.requests, "post", post)
    r = c.post("/pensar", json={"sistema": "s", "mensajes": [{"role": "user", "content": "hola"}]}).json()
    assert r["proveedor"] == "groq" and r["mensaje"]["content"] == "Listo" and len(veces) == 2



def test_voz_gratis_recibe_el_tono(c, monkeypatch):
    from servidor import voz
    visto = {}
    monkeypatch.setattr(voz, "sintetizar", lambda texto, **kw: (visto.update(kw), b"ID3")[1])
    monkeypatch.setattr(ranura.config, "GOOGLE_TTS_API_KEY", "")
    c.post("/voz", json={"texto": "hola", "tono": "+10Hz"})
    assert visto["tono"] == "+10Hz"
    assert c.post("/voz", json={"texto": "hola", "tono": "fuerte"}).status_code == 422



def test_voz_de_axtra_en_cada_idioma(c, monkeypatch):
    from servidor import voz
    vistos = []
    monkeypatch.setattr(voz, "sintetizar", lambda texto, **kw: (vistos.append(kw), b"ID3")[1])
    monkeypatch.setattr(ranura.config, "GOOGLE_TTS_API_KEY", "k")          # aunque haya Google, usa la de Axtra
    monkeypatch.setattr(ranura.config, "VOZ_AXTRA", "es-ES-AlvaroNeural")
    c.post("/voz", json={"texto": "hola", "axtra": True, "idioma": "es"})
    c.post("/voz", json={"texto": "hello", "axtra": True, "idioma": "en"})
    assert vistos[0]["voz"] == "es-ES-AlvaroNeural" and vistos[0]["tono"] == ranura.config.VOZ_TONO
    assert vistos[1]["voz"] == "en-US-AndrewNeural" and vistos[1]["ritmo"] == ranura.config.VOZ_VELOCIDAD
