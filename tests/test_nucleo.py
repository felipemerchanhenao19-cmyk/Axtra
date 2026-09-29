import pytest

from axtra.cerebros import Cerebro, ErrorCerebro
from axtra.nucleo import Axtra


class Falso(Cerebro):
    def __init__(self, nombre, activo=True, falla=False):
        self.nombre, self.activo, self.falla = nombre, activo, falla
        self.llamadas = 0

    def disponible(self):
        return self.activo

    def responder(self, historial, sistema):
        self.llamadas += 1
        if self.falla:
            raise ErrorCerebro(f"{self.nombre} caído")
        return f"{self.nombre}: {historial[-1].texto}"


def crear(**cerebros):
    return Axtra(cerebros, ["gemini", "grok", "claude"], "sistema")


def test_auto_usa_el_primero_del_orden():
    axtra = crear(claude=Falso("claude"), gemini=Falso("gemini"), grok=Falso("grok"))
    assert axtra.preguntar("hola") == ("gemini", "gemini: hola")
    assert len(axtra.historial) == 2


def test_respaldo_si_un_cerebro_falla():
    axtra = crear(claude=Falso("claude"), gemini=Falso("gemini", falla=True), grok=Falso("grok"))
    assert axtra.preguntar("hola")[0] == "grok"


def test_salta_cerebros_sin_llave():
    axtra = crear(claude=Falso("claude"), gemini=Falso("gemini", activo=False),
                  grok=Falso("grok", activo=False))
    assert axtra.preguntar("hola")[0] == "claude"


def test_modo_fijo_tiene_prioridad():
    axtra = crear(claude=Falso("claude"), gemini=Falso("gemini"), grok=Falso("grok"))
    axtra.cambiar_modo("claude")
    assert axtra.preguntar("hola")[0] == "claude"


def test_todos_fallan_no_guarda_historial():
    axtra = crear(claude=Falso("claude", falla=True), gemini=Falso("gemini", falla=True))
    with pytest.raises(ErrorCerebro):
        axtra.preguntar("hola")
    assert axtra.historial == []


def test_cerebro_desconocido():
    axtra = crear(claude=Falso("claude"))
    with pytest.raises(ValueError):
        axtra.cambiar_modo("chatgpt")


def test_consultar_todos_no_toca_historial():
    axtra = crear(claude=Falso("claude"), gemini=Falso("gemini", falla=True))
    r = axtra.consultar_todos("hola")
    assert r["claude"] == "claude: hola" and r["gemini"].startswith("[error]")
    assert axtra.historial == []
