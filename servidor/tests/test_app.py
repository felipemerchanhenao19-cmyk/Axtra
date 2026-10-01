import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from servidor import app as app_mod
from servidor import config, seguridad
from servidor.enrutador import Enrutador

from .test_enrutador import cerebros


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setattr(app_mod, "_enrutador", Enrutador(cerebros()))
    return TestClient(app_mod.app)


def test_sin_acceso_configurado_no_deja_entrar(cliente):
    assert cliente.get("/api/salud").status_code == 200
    assert cliente.get("/api/chats").status_code == 401
    assert cliente.post("/api/chat", json={"texto": "hola"}).status_code == 401


def test_conversacion_completa_en_modo_desarrollo(cliente, monkeypatch):
    monkeypatch.setattr(config, "MODO_DESARROLLO", True)
    r = cliente.post("/api/chat", json={"texto": "hola"}).json()
    assert r["cerebro"] == "Groq" and r["chat_id"]
    r2 = cliente.post("/api/chat", json={"texto": "¿y tú?", "chat_id": r["chat_id"]}).json()
    assert r2["chat_id"] == r["chat_id"]
    msgs = cliente.get(f"/api/chats/{r['chat_id']}").json()["mensajes"]
    assert [m["rol"] for m in msgs] == ["user", "assistant", "user", "assistant"]
    assert cliente.get("/api/archivos/..%2Faxtra.db").status_code == 404
    assert cliente.delete(f"/api/chats/{r['chat_id']}").json()["ok"]


@pytest.fixture
def cloudflare(monkeypatch):
    """Simula Cloudflare Access con una llave propia."""
    llave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    monkeypatch.setattr(config, "CF_ACCESS_EQUIPO", "axtra")
    monkeypatch.setattr(config, "CF_ACCESS_AUD", "aud123")

    class Clave:
        key = llave.public_key()

    class ClienteJWK:
        def get_signing_key_from_jwt(self, token):
            return Clave()

    monkeypatch.setattr(seguridad, "_cliente", lambda: ClienteJWK())

    def token(correo="felipe@ejemplo.com", aud="aud123", vence=300, **extra):
        ahora = int(time.time())
        datos = {"aud": aud, "iss": "https://axtra.cloudflareaccess.com", "iat": ahora, "exp": ahora + vence, **extra}
        if correo is not None:
            datos["email"] = correo
        return jwt.encode(datos, llave, algorithm="RS256")
    return token


def test_solo_entra_tu_cuenta(cliente, cloudflare):
    h = lambda t: {"Cf-Access-Jwt-Assertion": t}
    assert cliente.get("/api/chats", headers=h(cloudflare())).status_code == 200
    assert cliente.get("/api/chats", headers=h(cloudflare(correo="otro@ejemplo.com"))).status_code == 401
    assert cliente.get("/api/chats", headers=h(cloudflare(aud="otra-app"))).status_code == 401
    assert cliente.get("/api/chats", headers=h(cloudflare(vence=-120))).status_code == 401
    assert cliente.get("/api/chats", headers=h("basura")).status_code == 401
