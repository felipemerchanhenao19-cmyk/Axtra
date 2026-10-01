import time
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from servidor import app as app_mod
from servidor import config, db, push, recordatorios
from servidor.enrutador import Enrutador

from .test_app import cloudflare  # noqa: F401  (fixture)
from .test_enrutador import cerebros

TZ = ZoneInfo("America/Bogota")
AHORA = datetime(2026, 10, 1, 9, 0, tzinfo=TZ)   # jueves 9:00 a. m.


@pytest.mark.parametrize("texto,mensaje,esperado", [
    ("Recuérdame en 20 minutos sacar la ropa", "sacar la ropa", datetime(2026, 10, 1, 9, 20, tzinfo=TZ)),
    ("recuérdame llamar a mi mamá en una hora", "llamar a mi mama", datetime(2026, 10, 1, 10, 0, tzinfo=TZ)),
    ("Recuérdame a las 6:30 pm ir al gimnasio", "ir al gimnasio", datetime(2026, 10, 1, 18, 30, tzinfo=TZ)),
    ("Avísame mañana a las 7 de la mañana que tengo parcial", "tengo parcial", datetime(2026, 10, 2, 7, 0, tzinfo=TZ)),
    ("Recuérdame a las 8 revisar el CRM", "revisar el crm", datetime(2026, 10, 1, 20, 0, tzinfo=TZ)),  # 8 a. m. ya pasó
    ("Despiértame mañana a las 6:15", "Hora de despertar, señor.", datetime(2026, 10, 2, 6, 15, tzinfo=TZ)),
])
def test_interpretar_recordatorios(texto, mensaje, esperado):
    msg, cuando = recordatorios.interpretar(texto, AHORA)
    assert (msg, cuando) == (mensaje, esperado)


def test_recordatorio_sin_hora_pregunta_cuando():
    assert recordatorios.interpretar("recuérdame comprar pan", AHORA)[1] is None
    assert "¿Cuándo" in recordatorios.responder("recuérdame comprar pan")


def test_recordatorio_por_chat_se_guarda():
    r = Enrutador(cerebros()).responder("Recuérdame en 5 minutos tomar agua")
    assert r["nivel"] == "recordatorio" and "tomar agua" in r["texto"]
    assert any(x["mensaje"] == "tomar agua" for x in db.recordatorios_pendientes())


def test_datos_privados_solo_a_cerebros_de_pago():
    db.guardar_pc({"recuerdos": [{"texto": "Le gusta el café sin azúcar", "fecha": "2026-09-30"}],
                   "crm": [{"nombre": "Don Pepe", "negocio": "Mr Papa", "estado": "propuesta"}]})
    p = cerebros()
    e = Enrutador(p)
    e.responder("hola, ¿cómo estás?")
    assert "café" not in p["groq"].llamadas[0]["sistema"]                 # gratis: nunca
    e.responder("¿A qué clientes debo llamar hoy?")
    sistema = p["claude_barato"].llamadas[0]["sistema"]                   # de pago: sí
    assert "café sin azúcar" in sistema and "Mr Papa" in sistema


def test_solo_el_pc_sube_datos(monkeypatch, cloudflare):  # noqa: F811
    monkeypatch.setattr(app_mod, "_enrutador", Enrutador(cerebros()))
    monkeypatch.setattr(config, "CF_SERVICIO_ID", "id-del-pc.access")
    c = TestClient(app_mod.app)
    datos = {"sincronizacion": {"total": 46, "nivel": "Sintonía"}}
    yo = {"Cf-Access-Jwt-Assertion": cloudflare()}
    pc = {"Cf-Access-Jwt-Assertion": cloudflare(correo=None, common_name="id-del-pc.access")}
    otro = {"Cf-Access-Jwt-Assertion": cloudflare(correo=None, common_name="otro-servicio")}
    assert c.post("/api/pc/sincronizar", json=datos, headers=yo).status_code == 403    # tu cuenta no sube datos
    assert c.post("/api/pc/sincronizar", json=datos, headers=otro).status_code == 401  # otro servicio: fuera
    assert c.post("/api/pc/sincronizar", json=datos, headers=pc).json()["ok"]          # el PC sí
    assert c.get("/api/aprendizaje", headers=yo).json()["sincronizacion"]["total"] == 46


def test_sincronizar_y_ver_aprendizaje(monkeypatch):
    monkeypatch.setattr(config, "MODO_DESARROLLO", True)
    c = TestClient(app_mod.app)
    r = c.post("/api/pc/sincronizar", json={"sincronizacion": {"total": 46, "nivel": "Sintonía"},
                                             "protocolo": [{"tema": "Neurociencia", "porcentaje": 34}], "x": 1}).json()
    assert r["guardado"] == ["protocolo", "sincronizacion"]
    a = c.get("/api/aprendizaje").json()
    assert a["sincronizacion"]["total"] == 46 and a["protocolo"][0]["tema"] == "Neurociencia" and a["ultima_sincronizacion"]


def test_notificaciones(monkeypatch):
    enviados = []

    class Resp:
        status_code = 410

    class Falla(Exception):
        response = Resp()

    import pywebpush

    def falso(subscription_info, **k):
        if "vieja" in subscription_info["endpoint"]:
            raise pywebpush.WebPushException("se fue", response=Resp())
        enviados.append(subscription_info["endpoint"])

    monkeypatch.setattr(pywebpush, "webpush", falso)
    assert len(push.clave_publica()) > 80                       # llave VAPID creada sola
    db.guardar_suscripcion({"endpoint": "https://push.ejemplo/nueva", "keys": {"p256dh": "a", "auth": "b"}})
    db.guardar_suscripcion({"endpoint": "https://push.ejemplo/vieja", "keys": {"p256dh": "a", "auth": "b"}})
    assert push.enviar("Axtra", "hola") == 1 and enviados == ["https://push.ejemplo/nueva"]
    assert [s["endpoint"] for s in db.suscripciones()] == ["https://push.ejemplo/nueva"]   # la vieja se borra
    rid = db.crear_recordatorio("tomar agua", time.time() - 1)
    recordatorios._revisar()
    assert all(r["id"] != rid for r in db.recordatorios_pendientes())
