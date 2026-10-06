"""Genera web/modelos/torta.glb: una torta de chocolate en 3D a tamaño real (unos 20 cm), para verla en
realidad aumentada sobre la mesa. Capas de bizcocho y crema, cubierta de chocolate, fresas y una porción cortada.

Uso: python -m servidor.apex.herramientas.torta_3d   (requiere: pip install trimesh shapely)"""
import math
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon

SALIDA = Path(__file__).resolve().parent.parent / "web" / "modelos" / "torta.glb"


def material(rgb, rugosidad=0.6):
    lineal = [(c / 255) ** 2.2 for c in rgb]         # glTF guarda el color en lineal (si no, se ve deslavado)
    return trimesh.visual.material.PBRMaterial(baseColorFactor=[*lineal, 1.0],
                                               metallicFactor=0.0, roughnessFactor=rugosidad)


def pintar(malla, rgb, rugosidad=0.6):
    malla.visual = trimesh.visual.TextureVisuals(uv=np.zeros((len(malla.vertices), 2)), material=material(rgb, rugosidad))
    return malla


def sector(r_ext, desde, hasta, alto, z, r_int=0.0, pasos=72):
    """Porción de cilindro (en grados) extruida: sirve para la torta sin la porción y para la porción misma."""
    angs = np.radians(np.linspace(desde, hasta, pasos))
    borde = [(r_ext * math.cos(a), r_ext * math.sin(a)) for a in angs]
    centro = [(r_int * math.cos(a), r_int * math.sin(a)) for a in angs[::-1]] if r_int else [(0.0, 0.0)]
    m = trimesh.creation.extrude_polygon(Polygon(borde + centro), alto)
    m.apply_translation([0, 0, z])
    return m


BIZCOCHO, CREMA, COBERTURA, PLATO, FRESA, HOJA = (74, 38, 22), (238, 222, 196), (52, 26, 14), (244, 243, 240), (200, 30, 42), (60, 130, 50)
CAPAS = [(BIZCOCHO, 0.022), (CREMA, 0.007), (BIZCOCHO, 0.022), (CREMA, 0.007), (BIZCOCHO, 0.02)]
R, CORTE = 0.09, 42           # radio de la torta (m) y ángulo de la porción que se sacó


def torta(desde, hasta, desplazar=(0, 0)):
    partes, z = [], 0.010
    for color, alto in CAPAS:                                   # capas: se ven en la cara del corte
        partes.append(pintar(sector(R - 0.003, desde, hasta, alto, z), color, 0.9)); z += alto
    alto_total = z - 0.010
    partes.append(pintar(sector(R, desde, hasta, alto_total, 0.010, r_int=R - 0.003), COBERTURA, 0.35))  # costado
    partes.append(pintar(sector(R + 0.002, desde, hasta, 0.006, z), COBERTURA, 0.3))                    # cubierta
    for p in partes:
        p.apply_translation([*desplazar, 0])
    return partes, z + 0.006


def fresa(x, y, z):
    f = trimesh.creation.icosphere(subdivisions=2, radius=0.011)
    f.apply_scale([1, 1, 1.25])
    f.apply_translation([x, y, z + 0.011])
    h = trimesh.creation.cone(radius=0.008, height=0.006, sections=12)
    h.apply_translation([x, y, z + 0.024])
    return [pintar(f, FRESA, 0.4), pintar(h, HOJA, 0.7)]


def construir() -> trimesh.Scene:
    escena = trimesh.Scene()
    plato = trimesh.creation.cylinder(radius=0.135, height=0.01, sections=96)
    plato.apply_translation([0, 0, 0.005])
    escena.add_geometry(pintar(plato, PLATO, 0.25))
    cuerpo, tope = torta(CORTE, 360)
    for p in cuerpo:
        escena.add_geometry(p)
    for i in range(7):                                          # fresas alrededor del borde, fuera del corte
        a = math.radians(CORTE + 22 + i * (360 - CORTE - 30) / 6)
        for p in fresa(0.066 * math.cos(a), 0.066 * math.sin(a), tope):
            escena.add_geometry(p)
    for p in fresa(0, 0, tope):
        escena.add_geometry(p)
    mitad = math.radians(CORTE / 2)                             # la porción, servida al lado
    porcion, tope_p = torta(0, CORTE, desplazar=(0.045 * math.cos(mitad), 0.045 * math.sin(mitad)))
    for p in porcion:
        escena.add_geometry(p)
    # glTF usa Y hacia arriba: girar la escena (aquí se construyó con Z hacia arriba)
    escena.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    return escena


if __name__ == "__main__":
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_bytes(construir().export(file_type="glb"))
    print(SALIDA, SALIDA.stat().st_size, "bytes")
