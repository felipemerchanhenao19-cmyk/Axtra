"""«Turno de noche»: miniserie en 3D (personajes de bloques) sobre un restaurante de verdad. Drama serio, humor seco, nada de chiste:
la gracia sale de la situación (la hora pico, la comisión) y el asistente de Apex la resuelve sin hacer ruido.
Precios (clientes nuevos, 50 % de descuento): Apex Play según mesas y carta. Apex Domicilios: montaje $ 450.000 ($ 550.000 con el lector
de comprobantes de Nequi) y $ 60.000 al mes los primeros 12 meses (normal $ 120.000).
Plano: set (restaurante | oficina), cam [[x,y,z, tx,ty,tz, fov], ...] repartidas en el plano (o con tiempo delante: 8 valores),
actores {id: {pos, rot, gesto, emo, mira, sentado, inclina}}, orbis {id: {pos, nace, mira, estado}}, e (escenario), titulo, trans, final, lineas.
Claves de tiempo: segundos desde el inicio del plano, "l1" (inicio de la línea 1 del plano), "f1" (fin de la línea 1), "l1+0.5"."""
from math import sin, cos, radians, hypot

def cerca(pos, rot, dist=2.3, giro=10, alt=0.06, fov=36, y=1.72):
    """Primer plano: cámara frente a alguien que mira hacia «rot» (0 = hacia +z), un poco de lado."""
    a = radians(rot + giro); return [pos[0] + sin(a) * dist, y + alt, pos[1] + cos(a) * dist, pos[0], y, pos[1], fov]

def sobre(a, b, dist=1.2, lado=0.4, alt=0.12, fov=36, ya=1.72, yb=1.72):
    """Por encima del hombro: cámara detrás de «a», mirando la cara de «b» (en vertical los dos quedan en la misma columna)."""
    dx, dz = b[0] - a[0], b[1] - a[1]; n = hypot(dx, dz); ux, uz = dx / n, dz / n; px, pz = uz, -ux
    return [a[0] - ux * dist + px * lado, ya + alt, a[1] - uz * dist + pz * lado, b[0], yb, b[1], fov]

def L(quien, txt, pausa=0.4, **e): return (quien, txt, pausa, e)

ELENCO = {
    "jairo": dict(piel="#c48a64", sombraPiel="#ad7552", pelo="#6e6862", cejas="#3a3632", bigote="#4a4440", camisa="#e8e2d6", delantal="#3b2a22",
                  pantalon="#2a2f3a", semilla=1, alto=1.0),
    "brayan": dict(piel="#a86f4e", sombraPiel="#93603f", pelo="#1a120e", cejas="#1a120e", camisa="#f2efe8", chaleco="#1f2328", corbatin="#141414",
                   pantalon="#1b1e24", peinado="copete", semilla=2, alto=0.97),
    "marcela": dict(piel="#d9a27e", sombraPiel="#c48d6a", pelo="#3a2418", cejas="#3a2418", peinado="moño", saco="#2f3a4a", camisa="#e8e4dc",
                    gafas="#15171a", pantalon="#262b33", labios="#9a3b3f", semilla=5, alto=0.95),
    "cliente": dict(piel="#b97c58", sombraPiel="#a36b4a", pelo="#2b1d16", camisa="#3a5a7a", peinado="flequillo", semilla=7),
}
REPARTO = {
    "jairo": dict(voz=("es-CO-GonzaloNeural", "-9%", "-14Hz")),
    "brayan": dict(voz=("es-VE-SebastianNeural", "+4%", "+3Hz")),
    "marcela": dict(voz=("es-VE-PaolaNeural", "-6%", "-4Hz")),
    "cliente": dict(voz=("es-US-AlonsoNeural", "+0%", "+0Hz")),
    "orbi": dict(voz=("es-CO-SalomeNeural", "+2%", "+2Hz"), fx="radio"),
}
# clientes del salón (sentados, conversan); mesa 7: el acompañante del cliente
_c = [("#7a3b3b", "#2b1d16", "largo"), ("#3a6a4a", "#5a3a28", None), ("#c9a24a", "#1a120e", "moño"), ("#4a4a6a", "#6e6862", None),
      ("#8a5a7a", "#2b1d16", "largo"), ("#2a4a6a", "#1a120e", "copete"), ("#6a3a2a", "#3a2418", None)]
_pos = [(2.4, 1.15, 180), (2.4, -0.35, 0), (-2.4, 4.15, 180), (-2.4, 2.65, 0), (2.6, 3.95, 180), (2.6, 2.45, 0), (-2.6, -0.15, 0)]
EXTRAS = [dict(set="restaurante", x=x, z=z, rot=r, charla=True, cfg=dict(camisa=c, pelo=p, cejas=p, peinado=pe or "normal",
               piel=["#c98d6b", "#a86f4e", "#d9a27e", "#8a5a3e"][i % 4], sombraPiel=["#b47a5a", "#93603f", "#c48d6a", "#7a4a30"][i % 4]))
          for i, ((x, z, r), (c, p, pe)) in enumerate(zip(_pos, _c))]

# posiciones fijas del restaurante
JAIRO = [1.0, -4.3]; BRAYAN = [0.3, -2.72]; CLIENTE = [-2.6, 1.35]
O7 = [-2.6, 1.42, 0.6]; O4 = [2.4, 1.42, 0.4]; O9 = [-2.4, 1.42, 3.4]; O2 = [2.6, 1.42, 3.2]
SALON = {"cliente": dict(pos=CLIENTE, rot=180, sentado=True, gesto="manos_mesa")}
JAI2 = [0, -0.75]; MAR = [0, 0.85]
PEDIDO7 = ["Mesa 7 · 8:04 p. m.", "2 × Bandeja paisa · 1 × Limonada de coco"]
PEDIDO4 = ["Mesa 4 · 8:05 p. m.", "1 × Ajiaco · 2 × Limonada de coco"]

EPISODIOS = {
 # ─────────── Capítulo 1 · «Mesa siete» (Apex Play)
 "mesa-siete": dict(producto="play", reparto=REPARTO, elenco=ELENCO, extras=EXTRAS,
  copy="Viernes, 8 p. m. Un solo mesero. Veinticinco minutos de espera en la mesa cuatro. Turno de noche, capítulo 1. 🎬",
  hashtags="#Restaurantes #Emprendedores #Tulua #Negocios #TurnoDeNoche",
  planos=[
   dict(set="restaurante", titulo=["Viernes · 8:00 p. m.", "Turno de noche"], musica="tension", min=3.6, mano=0.02,
        cam=[[0.2, 2.7, 7.0, 0, 1.0, -1.2, 40], [0.0, 2.2, 5.2, 0, 1.1, -1.4, 40]], fx=[dict(tipo="lluvia", k=1.4)],
        extrasGesto={0: "mano_arriba", 3: "mano_arriba", 4: "mano_arriba"},
        actores={"jairo": dict(pos=JAIRO, gesto="trapo", mira=-10, emo="cansado"), **SALON,
                 "brayan": dict(pos=[[0, -4.2, 4.6], [3.4, -0.6, 1.2]], rot=133, gesto="reposo", emo="triste")}),
   dict(set="restaurante", musica="tension", cola=0.3, mano=0.015,
        cam=[sobre(JAIRO, BRAYAN, 1.0, 0.72, 0.1, 38), sobre(JAIRO, BRAYAN, 1.0, 0.72, 0.08, 36)],
        actores={"jairo": dict(pos=JAIRO, gesto="trapo", mira=-15, miraY=0.25, emo="cansado"),
                 "brayan": dict(pos=[[0, 0.1, -2.0], [0.7, 0.3, -2.72]], rot=180, inclina=[[0, 0.18], [1.2, 0.12]], mira="jairo", emo="triste")},
        lineas=[L("brayan", "Don Jairo.", 0.8)]),
   dict(set="restaurante", musica="tension", cola=0.4,
        cam=[cerca(JAIRO, 0, 2.5, 12), cerca(JAIRO, 0, 2.2, 8)],
        actores={"jairo": dict(pos=JAIRO, gesto="trapo", mira=-8, miraY=0.3, emo="cansado"), "brayan": dict(pos=BRAYAN, rot=180, mira="jairo", emo="triste")},
        lineas=[L("jairo", "Dígame que es una buena noticia.", 0.3)]),
   dict(set="restaurante", musica="tension", cola=0.3,
        cam=[cerca(BRAYAN, 180, 2.1, -12, y=1.68), cerca(BRAYAN, 180, 1.95, -9, y=1.68)],
        actores={"jairo": dict(pos=JAIRO, gesto="trapo", emo="cansado"), "brayan": dict(pos=BRAYAN, rot=180, mira="jairo", emo="triste", inclina=0.06)},
        lineas=[L("brayan", "La mesa siete lleva veinte minutos esperando.", 0.2)]),
   dict(set="restaurante", musica="tension", cola=0.5,
        cam=[sobre(BRAYAN, JAIRO, 1.0, 0.72, 0.15, 38), sobre(BRAYAN, JAIRO, 1.0, 0.72, 0.12, 36)],
        actores={"jairo": dict(pos=JAIRO, gesto=[[0, "trapo"], ["f0+0.2", "baja"]], mira=[[0, -10], ["l0", "brayan"]], emo="cansado"),
                 "brayan": dict(pos=BRAYAN, rot=180, mira="jairo", emo=[[0, "triste"], ["l1", "serio"]])},
        lineas=[L("jairo", "¿Y la cuatro?", 0.2), L("brayan", "Veinticinco.", 0.9)]),
   dict(set="restaurante", musica="tension", cola=0.2, mano=0.008,
        cam=[cerca(JAIRO, 0, 2.7, 4, 0.0, 34), cerca(JAIRO, 0, 2.0, 2, 0.0, 34)],
        actores={"jairo": dict(pos=JAIRO, gesto="baja", mira=[[0, 0], ["l1", "brayan"]], emo=[[0, "cerrados"], ["l2", "cansado"]]),
                 "brayan": dict(pos=BRAYAN, rot=180, mira="jairo", emo="serio")},
        lineas=[L("jairo", "¿Cuántos meseros tenemos hoy?", 1.3), L("brayan", "Yo.", 0.35), L("jairo", "¿Y el otro?", 0.6)]),
   dict(set="restaurante", cola=1.0,
        cam=[cerca(BRAYAN, 180, 1.9, -8, y=1.68, fov=34), cerca(BRAYAN, 180, 1.8, -8, y=1.68, fov=34)],
        actores={"jairo": dict(pos=JAIRO, gesto="baja", emo="cansado"), "brayan": dict(pos=BRAYAN, rot=180, mira="jairo", emo="serio")},
        lineas=[L("brayan", "También yo.", 0.5)]),
   # la mesa siete escanea el código: aparece el asistente
   dict(set="restaurante", musica="esperanza", trans="negro", cola=0.6, fx=[dict(tipo="destello", p=0.12)],
        cam=[[-0.35, 1.68, 0.97, -2.6, 1.36, 0.97, 46], [-0.6, 1.6, 0.97, -2.6, 1.38, 0.97, 44]],
        e=dict(qrLuz={"7": [[0, 0], [0.4, 1.0], [2.2, 0.15]]}),
        orbis={"o7": dict(pos=O7, nace=[0.5, 2.0], mira=[[0, "cam"], ["l0", "cliente"]])},
        actores={"cliente": dict(pos=CLIENTE, rot=180, sentado=True, gesto=[[0, "celular"], ["l0", "manos_mesa"]], mira=[[0, -20], [1.0, "o7"]], miraY=0.1,
                                 emo=[[0, "neutro"], [1.2, "sorpresa"], ["l1", "neutro"]])},
        lineas=[L("orbi", "Buenas noches. ¿Qué les provoca hoy?", 2.1), L("cliente", "Dos bandejas paisas… y una limonada de coco.", 0.4),
                L("orbi", "Listo. Ya van para la cocina.", 0.3, pedido=True)]),
   # el pedido llega solo a la caja; los dos miran el salón
   dict(set="restaurante", musica="esperanza", min=3.4, fx=[dict(tipo="destello", p=0.15)],
        cam=[[1.85, 1.62, -2.75, 1.7, 1.22, -3.45, 30], [1.4, 1.95, -0.2, 0.6, 1.55, -3.6, 36]],
        e=dict(tablet=[[0, {}], [0.4, {"pedidos": [PEDIDO7], "nuevo": True}]], comandas=5),
        orbis={"o7": dict(pos=O7, voz=False)},
        actores={"jairo": dict(pos=JAIRO, gesto="baja", mira=[[0, "brayan"], [1.0, -60], [2.0, "o7"]], miraDur=0.9, emo=[[0, "cansado"], [1.4, "sorpresa"]]),
                 "brayan": dict(pos=BRAYAN, rot=[[0, 180], [1.3, 150]], mira=[[0, "jairo"], [1.2, "o7"]], miraDur=0.9, emo=[[0, "serio"], [1.6, "sorpresa"]])}),
   # todas las mesas atendidas
   dict(set="restaurante", musica="esperanza", cola=0.8, fx=[dict(tipo="destello", p=0.1), dict(tipo="destello", p=0.35)],
        cam=[[6.3, 2.5, 2.2, -2.6, 1.15, 1.8, 50], [6.0, 2.2, 1.9, -2.6, 1.25, 1.8, 48]],
        e=dict(qrLuz={"4": 0.6, "9": 0.6, "2": 0.6}),
        orbis={"o7": dict(pos=O7, voz=False), "o4": dict(pos=O4, nace=[0.2, 1.2], mira=[[0, "cam"], [1.4, 0]]),
               "o9": dict(pos=O9, nace=[0.6, 1.6], voz=False), "o2": dict(pos=O2, nace=[1.0, 2.0], voz=False)},
        actores={**SALON, "jairo": dict(pos=JAIRO, gesto="baja", emo="sorpresa", mira=-20), "brayan": dict(pos=BRAYAN, rot=150, emo="sorpresa", mira=-30)},
        lineas=[L("orbi", "Mesa cuatro: atendida.", 2.0, pedido=True)]),
   # ¿quién lo contrató?
   dict(set="restaurante", musica="esperanza", cola=0.9, mano=0.01,
        cam=[sobre(BRAYAN, JAIRO, 1.25, 0.72, 0.12, 38), sobre(BRAYAN, JAIRO, 1.0, 0.72, 0.1, 36)],
        e=dict(tablet={"pedidos": [PEDIDO4, PEDIDO7], "nuevo": True}, comandas=6),
        actores={"jairo": dict(pos=JAIRO, gesto="baja", mira=[[0, -35], ["l0", "brayan"], ["l2", -35]], emo=[[0, "sorpresa"], ["l0", "serio"], ["l2", "neutro"]]),
                 "brayan": dict(pos=BRAYAN, rot=[[0, 160], ["l1-0.3", 180]], mira=[[0, -30], ["l1-0.3", "jairo"]], emo=[[0, "sorpresa"], ["l1", "neutro"]])},
        lineas=[L("jairo", "¿Y eso… quién lo contrató?", 0.6), L("brayan", "Usted, don Jairo. El lunes.", 0.4), L("jairo", "Ah.", 1.0)]),
   # un tinto para el mesero
   dict(set="restaurante", musica="esperanza", cola=1.1,
        cam=[sobre(BRAYAN, JAIRO, 1.25, -0.72, 0.1, 38), sobre(BRAYAN, JAIRO, 1.0, -0.72, 0.08, 36)],
        orbis={"o7": dict(pos=O7, voz=False), "o4": dict(pos=O4, voz=False)},
        actores={"jairo": dict(pos=JAIRO, gesto=[[0, "reposo"], ["l0", "tinto"]], mira="brayan", emo=[[0, "neutro"], ["l2", "feliz"]]),
                 "brayan": dict(pos=BRAYAN, rot=180, mira=[[0, "jairo"], ["f1", -60], ["f2", "jairo"]], emo=[[0, "neutro"], ["f2", "feliz"]], inclina=0.04)},
        lineas=[L("jairo", "Brayan. Tómese un tinto.", 0.5), L("brayan", "¿Y las mesas?", 0.4), L("jairo", "Ya están atendidas.", 0.8)]),
   dict(set="restaurante", musica="pelicula", min=6.0, trans="negro",
        cam=[[6.2, 2.8, 2.0, -2.6, 1.1, 1.6, 50], [6.0, 2.6, 1.8, -2.6, 1.1, 1.6, 50]],
        orbis={"o7": dict(pos=O7, voz=False), "o4": dict(pos=O4, voz=False), "o9": dict(pos=O9, voz=False), "o2": dict(pos=O2, voz=False)},
        actores={**SALON, "jairo": dict(pos=JAIRO, gesto="reposo", emo="feliz"), "brayan": dict(pos=BRAYAN, rot=180, gesto="tinto", emo="feliz")},
        final=dict(marca="Apex Play", frase="Un asistente de IA en cada mesa.", desde=0.6,
                   detalle="Toma el pedido, recomienda y lo manda a la caja.<br>Cotización según sus mesas y su carta<br>Clientes nuevos: 50 % de descuento")),
  ]),

 # ─────────── Capítulo 2 · «La comisión» (Apex Domicilios)
 "la-comision": dict(producto="dom", reparto=REPARTO, elenco=ELENCO, extras=EXTRAS,
  copy="Lunes, 11:40 p. m. Marcela tiene que darle una noticia a don Jairo. Turno de noche, capítulo 2. 🎬",
  hashtags="#Restaurantes #Domicilios #Emprendedores #Tulua #TurnoDeNoche",
  planos=[
   dict(set="oficina", titulo=["Lunes · 11:40 p. m.", "Turno de noche"], musica="misterio", min=3.6, mano=0.015,
        cam=[[2.9, 2.1, 2.7, -0.1, 1.1, 0.3, 44], [2.5, 1.9, 2.3, -0.1, 1.15, 0.3, 42]], fx=[dict(tipo="lluvia", k=1.6), dict(tipo="rayo", p=0.55)],
        e=dict(rayos=[[2.0, 0.7]], portatil={"titulo": "Domicilios · este mes"}),
        actores={"marcela": dict(pos=[0, 0.85], rot=180, sentado=True, gesto="teclea", mira=0, miraY=0.25, emo="serio")}),
   dict(set="oficina", musica="misterio", cola=0.5,
        cam=[[-2.3, 1.8, 2.6, 0.4, 1.3, -0.2, 34], [-2.0, 1.75, 2.4, 0.4, 1.3, -0.2, 34]],
        e=dict(portatil={"titulo": "Domicilios · este mes"}),
        actores={"marcela": dict(pos=[0, 0.85], rot=180, sentado=True, gesto="teclea", mira=0, miraY=0.25, emo="serio"),
                 "jairo": dict(pos=[[0, 2.6, -1.9], [1.6, 0.75, -1.45]], rot=[[0, -60], [1.4, -20]], gesto="reposo", mira="marcela", emo="neutro")},
        lineas=[L("marcela", "Don Jairo. Siéntese.", 1.4)]),
   dict(set="oficina", musica="misterio", cola=0.5,
        cam=[cerca([0.75, -1.45], -20, 2.4, 10), cerca([0.75, -1.45], -20, 2.1, 8)],
        actores={"jairo": dict(pos=[0.75, -1.45], rot=-20, mira="marcela", emo=[[0, "neutro"], ["l0", "duda"]]),
                 "marcela": dict(pos=[0, 0.85], rot=180, sentado=True, gesto="teclea", emo="serio")},
        lineas=[L("jairo", "Nadie dice «siéntese» para algo bueno.", 0.2)]),
   dict(set="oficina", musica="misterio", cola=0.5,
        cam=[sobre(JAI2, MAR, 1.0, 0.72, 0.2, 36, 1.38, 1.38), sobre(JAI2, MAR, 1.0, 0.72, 0.18, 34, 1.38, 1.38)],
        e=dict(lapRot=[[0, -0.15], ["f0", 2.9]], portatil={"titulo": "Domicilios · este mes", "filas": [["Ventas por domicilio", "$ 4.200.000", "#bff3ff"]]}),
        actores={"marcela": dict(pos=[0, 0.85], rot=180, sentado=True, gesto=[[0, "teclea"], ["f0-0.4", "explica"]], mira=[[0, "jairo"]], emo="serio"),
                 "jairo": dict(pos=[0, -0.75], rot=0, sentado=True, mira="marcela", emo="neutro")},
        lineas=[L("marcela", "Este mes vendimos cuatro millones doscientos en domicilios.", 0.3)]),
   dict(set="oficina", musica="misterio", cola=0.6,
        cam=[sobre(MAR, JAI2, 1.0, -0.72, 0.2, 36, 1.38, 1.38), sobre(MAR, JAI2, 1.0, -0.72, 0.18, 34, 1.38, 1.38)],
        e=dict(lapRot=2.9, portatil={"titulo": "Domicilios · este mes", "filas": [["Ventas por domicilio", "$ 4.200.000", "#bff3ff"]]}),
        actores={"jairo": dict(pos=[0, -0.75], rot=0, sentado=True, mira=[[0, "marcela"]], emo=[[0, "neutro"], ["l0", "feliz"]], gesto="explica"),
                 "marcela": dict(pos=[0, 0.85], rot=180, sentado=True, emo="serio")},
        lineas=[L("jairo", "¡Eso es bueno!", 0.3)]),
   dict(set="oficina", musica="tension", cola=0.4, fx=[dict(tipo="rayo", linea=0, dt=1.4)],
        cam=[cerca(MAR, 180, 2.3, 32, 0.08, 34, 1.38), cerca(MAR, 180, 2.0, 30, 0.06, 34, 1.38)],
        e=dict(lapRot=2.9, rayos=[["l0+1.4", 0.8]], rojo=[[0, False], ["l0+1.0", True]],
               portatil=[[0, {"titulo": "Domicilios · este mes", "filas": [["Ventas por domicilio", "$ 4.200.000", "#bff3ff"]]}],
                         ["l0+1.0", {"titulo": "Domicilios · este mes", "filas": [["Ventas por domicilio", "$ 4.200.000", "#bff3ff"], ["Comisión de la app (25 %)", "− $ 1.050.000", "#ff8a90"]],
                                     "alerta": "Se descuenta de cada pedido"}]]),
        actores={"marcela": dict(pos=[0, 0.85], rot=180, sentado=True, mira="jairo", emo="serio"), "jairo": dict(pos=[0, -0.75], rot=0, sentado=True, mira="marcela", emo="feliz")},
        lineas=[L("marcela", "La aplicación se quedó con un millón cincuenta.", 0.3)]),
   dict(set="oficina", musica="tension", cola=0.3, mano=0.006,
        cam=[cerca(JAI2, 0, 2.6, -30, 0.04, 34, 1.38), cerca(JAI2, 0, 1.9, -28, 0.02, 34, 1.38)],
        e=dict(lapRot=2.9, rojo=True),
        actores={"jairo": dict(pos=[0, -0.75], rot=0, sentado=True, mira="marcela", emo=[[0, "feliz"], [0.6, "sorpresa"], ["f1", "cansado"]]),
                 "marcela": dict(pos=[0, 0.85], rot=180, sentado=True, emo="serio")},
        lineas=[L("jairo", "¿Un millón?", 1.6), L("marcela", "Cincuenta.", 0.5)]),
   dict(set="oficina", musica="tension", cola=0.7,
        cam=[sobre(JAI2, MAR, 1.25, -0.72, 0.2, 38, 1.38, 1.38), sobre(JAI2, MAR, 1.1, -0.72, 0.18, 36, 1.38, 1.38)],
        e=dict(lapRot=2.9, rojo=True),
        actores={"jairo": dict(pos=[0, -0.75], rot=0, sentado=True, mira="marcela", emo="cansado"), "marcela": dict(pos=[0, 0.85], rot=180, sentado=True, mira="jairo", emo="serio")},
        lineas=[L("jairo", "¿Y eso por qué?", 0.3), L("marcela", "Por cada pedido.", 0.4)]),
   # el asistente sale del portátil
   dict(set="oficina", musica="esperanza", cola=0.6, fx=[dict(tipo="destello", p=0.1)],
        cam=[[-1.35, 1.8, 2.1, 0.1, 1.3, -0.25, 38], [-1.2, 1.74, 1.85, 0.1, 1.3, -0.25, 36]],
        e=dict(lapRot=2.9, rojo=[[0, True], [0.8, False]], portatil={"titulo": "Su propio link de pedidos", "filas": [["Comisión por pedido", "$ 0", "#bff3ff"]]}),
        orbis={"oo": dict(pos=[0.15, 1.32, -0.05], nace=[0.2, 1.6], r=0.15, luz=0.45, mira=[[0, "cam"], ["f0", "jairo"]])},
        actores={"jairo": dict(pos=[0, -0.75], rot=0, sentado=True, mira=[[0, "marcela"], [0.6, "oo"]], emo=[[0, "cansado"], [0.8, "sorpresa"]]),
                 "marcela": dict(pos=[0, 0.85], rot=180, sentado=True, mira=[[0, "jairo"], [0.7, "oo"]], emo="neutro")},
        lineas=[L("orbi", "Con su propio link de pedidos, la comisión es cero.", 1.7)]),
   dict(set="oficina", musica="esperanza", cola=0.8,
        cam=[sobre(MAR, JAI2, 1.0, 0.72, 0.2, 38, 1.38, 1.38), sobre(MAR, JAI2, 1.0, 0.72, 0.18, 36, 1.38, 1.38)],
        e=dict(lapRot=2.9, portatil={"titulo": "Su propio link de pedidos", "filas": [["Comisión por pedido", "$ 0", "#bff3ff"]]}),
        orbis={"oo": dict(pos=[0.15, 1.32, -0.05], r=0.15, luz=0.45, mira="jairo")},
        actores={"jairo": dict(pos=[0, -0.75], rot=0, sentado=True, mira="oo", emo=[[0, "sorpresa"], ["l0", "serio"]]),
                 "marcela": dict(pos=[0, 0.85], rot=180, sentado=True, mira="oo", emo="neutro")},
        lineas=[L("jairo", "Repítalo despacio.", 0.3), L("orbi", "Ce. Ro.", 0.6)]),
   dict(set="oficina", musica="esperanza", min=2.6, mano=0.006,
        cam=[cerca(JAI2, 0, 2.2, -34, 0.02, 34, 1.38), cerca(JAI2, 0, 1.8, -32, 0.01, 34, 1.38)],
        e=dict(lapRot=2.9),
        orbis={"oo": dict(pos=[0.15, 1.32, -0.05], r=0.15, luz=0.45, mira="jairo", voz=False)},
        actores={"jairo": dict(pos=[0, -0.75], rot=0, sentado=True, mira=[[0, "oo"], [0.7, "cam"]], miraDur=1.0, emo=[[0, "serio"], [1.6, "feliz"]]),
                 "marcela": dict(pos=[0, 0.85], rot=180, sentado=True, mira="oo")}),
   dict(set="oficina", musica="pelicula", min=6.0, trans="negro",
        cam=[[1.6, 2.1, 2.8, 0, 1.1, 0.0, 38], [1.3, 1.9, 2.3, 0, 1.1, 0.0, 38]], e=dict(lapRot=2.9),
        orbis={"oo": dict(pos=[0.15, 1.32, -0.05], r=0.15, luz=0.45, voz=False)},
        actores={"jairo": dict(pos=[0, -0.75], rot=0, sentado=True, mira="oo", emo="feliz"), "marcela": dict(pos=[0, 0.85], rot=180, sentado=True, mira="oo", emo="neutro")},
        nota="Ejemplo: 120 domicilios de $ 35.000 al mes con 25 % de comisión. Precios de lanzamiento para clientes nuevos.",
        final=dict(marca="Apex Domicilios", frase="Sus domicilios, sin comisión.", desde=0.6,
                   detalle="Su propio link de pedidos, con asistente de IA.<br>Clientes nuevos: 50 % · Montaje $ 450.000<br>$ 60.000 al mes los primeros 12 meses")),
  ]),
}
