"""Escáner de prospectos de Apex: mapa, turismo cercano, registro mercantil, puntaje, filtros y seguimiento."""
import json
import time

import pytest
from fastapi.testclient import TestClient

from servidor import app as app_mod, config, prospectos as p


def nodo(i, nombre, lat, lon, **tags):
    return {"type": "node", "id": i, "lat": lat, "lon": lon, "tags": {"amenity": "restaurant", "name": nombre, **tags}}


RESTAURANTES = [
    nodo(1, "La Mulata", 10.4236, -75.5503, cuisine="regional", phone="+57 300 000", opening_hours="Mo-Su 12:00-22:00",
         **{"addr:street": "Calle Quero", "name:en": "La Mulata"}),
    {"type": "way", "id": 2, "center": {"lat": 10.42361, "lon": -75.55031}, "tags": {"amenity": "restaurant", "name": "Restaurante La Mulata"}},  # el mismo, otra vez
    nodo(3, "Burger Planet", 10.40, -75.50, cuisine="burger", brand="Burger Planet"),
    nodo(4, "La Estación", 10.39, -75.48),
    nodo(5, "Sin nombre", 10.39, -75.48) | {"tags": {"amenity": "restaurant"}},
]
TURISMO = [{"type": "node", "id": 100 + i, "lat": 10.4236 + 0.0003 * i, "lon": -75.5503} for i in range(8)]
SOCIEDADES = [{"razon_social": "LA MULATA S.A.S.", "numero_identificacion": "900809054", "organizacion_juridica": "SAS", "ultimo_ano_renovado": str(time.gmtime().tm_year)},
              {"razon_social": "INVERSIONES LA ESTACION EK S.A.S", "numero_identificacion": "900000001", "organizacion_juridica": "SAS", "ultimo_ano_renovado": "2020"}]


@pytest.fixture
def falso(monkeypatch, tmp_path):
    monkeypatch.setattr(p, "DB", tmp_path / "prospectos.db")
    monkeypatch.setattr(p, "geocodificar", lambda c, pais: {"nombre": "Cartagena de Indias", "completo": "", "pais_codigo": "CO", "area": 3601343457,
                                                             "caja": (10.3, -75.6, 10.5, -75.4), "lat": 10.42, "lon": -75.54})
    consultas = []
    monkeypatch.setattr(p, "_overpass", lambda q, rondas=3: (consultas.append(q), RESTAURANTES if "restaurant" in q else TURISMO)[1])
    monkeypatch.setattr(p, "camara", lambda ciudad: "CARTAGENA")
    monkeypatch.setattr(p, "registro", lambda cam: ([dict(s) for s in SOCIEDADES], 5109))
    return consultas


def test_escaneo_completo(falso):
    r = p.escanear("Cartagena", "Colombia")
    assert r == {"ciudad": "Cartagena de Indias", "encontrados": 3, "turismo": 8, "registro_total": 5109, "cruzados": 1}
    filas = {f["nombre"]: f for f in p.buscar()}
    assert "Sin nombre" not in filas and "Restaurante La Mulata" not in filas          # sin nombre y repetido: fuera
    m = filas["La Mulata"]
    assert m["razon_social"] == "LA MULATA S.A.S." and m["nit"] == "900809054" and m["flujo"] == "alto" and m["turismo"] == 8
    assert m["nicho"] == "Típica / regional" and m["tipo"] == "Independiente" and "sociedad registrada y al día" in m["razones"]
    assert filas["Burger Planet"]["tipo"] == "Cadena" and filas["Burger Planet"]["puntaje"] < m["puntaje"]
    assert not filas["La Estación"]["razon_social"]                     # «Inversiones La Estación EK» no es seguro que sea el mismo
    assert p.buscar()[0]["nombre"] == "La Mulata"                       # el mejor primero
    assert len(falso) == 2 and "out center;" in falso[1]                 # turismo: solo coordenadas, consulta liviana


def test_volver_a_escanear_conserva_el_seguimiento(falso):
    p.escanear("Cartagena", "Colombia")
    pid = next(f["id"] for f in p.buscar() if f["nombre"] == "La Mulata")
    p.seguimiento(pid, estado="demo", notas="Habló con Carlos, el administrador", siguiente="2026-11-20")
    p.escanear("Cartagena", "Colombia")
    f = p.seguimiento(pid)
    assert (f["estado"], f["notas"], f["siguiente"]) == ("demo", "Habló con Carlos, el administrador", "2026-11-20")
    with pytest.raises(ValueError):
        p.seguimiento(pid, estado="inventado")


def test_filtros(falso):
    p.escanear("Cartagena", "Colombia")
    assert [f["nombre"] for f in p.buscar(tipo="Cadena")] == ["Burger Planet"]
    assert [f["nombre"] for f in p.buscar(contacto=True)] == ["La Mulata"]
    assert [f["nombre"] for f in p.buscar(texto="mulata")] == ["La Mulata"]
    assert all(f["puntaje"] >= 50 for f in p.buscar(minimo=50))
    o = p.opciones()
    assert o["ciudades"][0]["valor"] == "Cartagena de Indias" and "piloto" in o["estados"]


def test_cruce_con_el_registro():
    soc = [{"razon_social": n} for n in ("GRUPO PEZETARIAN S.A.S.", "RESTAURANTE EL BURLADOR DE SEVILLA S.A.S.", "ESTACION EK RESTAURANTE BAR S.A.S",
                                         "SABOR COSTEÑO D.R S.A.S.")]
    idx = p.indice_registro(soc)
    assert p.cruzar("Pezetarian", soc, idx)[0]["razon_social"] == "GRUPO PEZETARIAN S.A.S."            # «grupo» es genérico
    assert p.cruzar("El Burlador de Sevilla", soc, idx)[1] == 1.0
    assert p.cruzar("La Estacion", soc, idx)[0] is None                                                 # le sobra «EK»
    assert p.cruzar("Bar", soc, idx)[0] is None                                                         # nombre demasiado corto
    assert p.nucleo("RESTAURANTE LA CEVICHERIA S.A.S.") == "cevicheria"


def test_turismo_cercano():
    rest = [{"type": "node", "id": 1, "lat": 10.0, "lon": -75.0}, {"type": "node", "id": 2, "lat": 10.05, "lon": -75.0}]
    tur = [{"lat": 10.001, "lon": -75.0}, {"lat": 10.0035, "lon": -75.0}, {"lat": 10.01, "lon": -75.0}]   # 110 m, 390 m, 1,1 km
    assert p.densidad_turistica(rest, tur) == {"n1": 2, "n2": 0}


def test_un_escaneo_a_la_vez(falso, monkeypatch):
    lento = []
    monkeypatch.setattr(p, "escanear", lambda c, pais, eid=None: (lento.append(c), time.sleep(.3)))
    p.escanear_en_fondo("Cartagena", "Colombia")
    with pytest.raises(RuntimeError):
        p.escanear_en_fondo("Medellín", "Colombia")
    time.sleep(.5)
    p.escanear_en_fondo("Medellín", "Colombia")                          # ya terminó el primero
    time.sleep(.4)
    assert lento == ["Cartagena", "Medellín"]


def test_pagina_y_api_solo_con_sesion(falso, monkeypatch):
    c = TestClient(app_mod.app)
    assert c.get("/api/prospectos").status_code == 401                   # sin la sesión de Felipe no se ve nada
    monkeypatch.setattr(config, "MODO_DESARROLLO", True)
    p.escanear("Cartagena", "Colombia")
    lista = c.get("/api/prospectos", params={"flujo": "alto"}).json()
    assert [f["nombre"] for f in lista] == ["La Mulata"]
    r = c.patch(f"/api/prospectos/{lista[0]['id']}", json={"estado": "contactado"})
    assert r.status_code == 200 and r.json()["estado"] == "contactado"
    assert c.patch("/api/prospectos/n999", json={"estado": "demo"}).status_code == 404
    assert c.patch(f"/api/prospectos/{lista[0]['id']}", json={"estado": "x"}).status_code == 422
    csv = c.get("/api/prospectos.csv").text
    assert csv.lstrip("﻿").startswith("puntaje,nombre,ciudad") and "LA MULATA S.A.S." in csv
    assert c.get("/escaner.html").status_code == 200


def test_nicho_el_que_mas_sirve_y_cocina_en_espanol():
    assert p.calificar({"cuisine": "colombiana;internacional;salad;burger"}, 0, None)["nicho"] == "Típica / regional"
    assert p.calificar({"cuisine": "pizza;seafood"}, 0, None)["nicho"] == "Mariscos"
    assert p.calificar({}, 0, None)["nicho"] == "Sin dato"
