import io
import json
import wave

import pytest
from fastapi.testclient import TestClient

from servidor import app as app_mod
from servidor import config, idiomas, oido, voz
from servidor.enrutador import Enrutador, clasificar
from servidor.proveedores import Respuesta

from .test_enrutador import Falso, cerebros

LECCION = {"idioma": "ruso", "explicacion": "Así se dice, señor.", "consejo": "La e suena casi como i.",
           "frases": [{"frase": "Привет, как дела?", "pronunciacion": "pri-VIÉT, kak di-LÁ",
                       "traduccion": "Hola, ¿cómo estás?", "nota": "informal"}]}


class Profesor(Falso):
    def chat(self, sistema, mensajes, max_tokens=1500, pensar=False, buscar=False):
        self.llamadas.append({"sistema": sistema})
        return Respuesta("Claro:\n```json\n" + json.dumps(LECCION, ensure_ascii=False) + "\n```", self.nombre, "x")


@pytest.mark.parametrize("texto,idioma", [
    ("¿Cómo se dice hola, cómo estás en ruso?", "ruso"),
    ("Enséñame frases básicas en inglés", "ingles"),
    ("Quiero practicar francés", "frances"),
    ("¿Qué significa arigato en japonés?", "japones"),
    ("Hablemos del mercado chino", None),          # no es una lección
    ("¿Cómo va el dólar hoy?", None),
])
def test_detectar(texto, idioma):
    assert idiomas.detectar(texto) == idioma


def test_leccion_con_cerebro_gratis():
    p = cerebros(gemini=Profesor("Gemini"))
    assert clasificar("¿Cómo se dice hola en ruso?") == "idioma"
    r = Enrutador(p).responder("¿Cómo se dice hola, cómo estás en ruso?")
    lec = r["leccion"]
    assert r["nivel"] == "idioma" and r["cerebro"] == "Gemini" and not p["claude"].llamadas
    assert lec["frases"][0]["pronunciacion"] == "pri-VIÉT, kak di-LÁ" and lec["progreso"]["nivel"] == "A1"


def test_pronunciacion_bien_y_mal():
    bien = idiomas.evaluar("Привет, как дела?", "ruso", "привет как дела")
    assert bien["puntaje"] == 100 and all(p["estado"] == "bien" for p in bien["palabras"])
    mal = idiomas.evaluar("Привет, как дела?", "ruso", "привет как")
    assert mal["palabras"][2] == {"palabra": "дела", "estado": "repetir"} and mal["puntaje"] < 80
    ingles = idiomas.evaluar("How are you?", "ingles", "how are you")
    assert ingles["puntaje"] == 100


def _wav(segundos=1.0):
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b"\x00\x00" * int(16000 * segundos))
    return b.getvalue()


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setattr(config, "MODO_DESARROLLO", True)
    monkeypatch.setattr(app_mod, "_enrutador", Enrutador(cerebros(gemini=Falso("Gemini"))))
    return TestClient(app_mod.app)


def test_api_pronunciacion_y_progreso(cliente, monkeypatch):
    monkeypatch.setattr(oido, "transcribir", lambda wav, idioma, region: "привет как дела")
    r = cliente.post("/api/idiomas/pronunciacion", params={"idioma": "ruso", "objetivo": "Привет, как дела?"},
                     content=_wav(), headers={"Content-Type": "audio/wav"}).json()
    assert r["puntaje"] == 100 and r["progreso"]["dominadas"] == 1 and r["progreso"]["porcentaje"] == 0
    assert cliente.get("/api/idiomas/progreso").json()[0]["idioma"] == "ruso"


def test_api_audio_danado(cliente):
    r = cliente.post("/api/escuchar", content=b"no es audio", headers={"Content-Type": "audio/wav"})
    assert r.status_code == 422


def test_api_voz(cliente, monkeypatch):
    llamadas = []
    monkeypatch.setattr(voz, "sintetizar", lambda t, i, l: llamadas.append((t, i, l)) or b"ID3audio")
    r = cliente.post("/api/voz", json={"texto": "Привет", "idioma": "ruso", "lento": True})
    assert r.content == b"ID3audio" and r.headers["content-type"] == "audio/mpeg"
    cliente.post("/api/voz", json={"texto": "Hola", "idioma": "klingon"})
    assert llamadas == [("Привет", "ruso", True), ("Hola", None, False)]


def test_la_app_se_sirve(cliente):
    assert "AXTRA" in cliente.get("/").text
    assert cliente.get("/manifest.webmanifest").json()["name"] == "Axtra"
