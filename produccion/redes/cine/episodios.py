"""Guiones de «Cine Apex»: homenajes elegantes al cine. Ningún nombre, logo ni personaje registrado: solo el tono y los guiños.
Mismo formato de planos que «heroes» (ver heroes/episodios.py). Los actores nuevos son tipo="humano" con props de humano() (cine/personajes.js)."""

def A(v0, v1, p0=0, p1=1, c="ease"): return {"anim": [v0, v1, p0, p1, c]}
def H(id, x, y, s=1.25, cara=None, voz=None, **k):
    d = dict(id=id, tipo="humano", x=x, y=y, s=s, props=k.pop("props", {}))
    for clave in ("a", "de", "hasta", "curva", "aparece", "desaparece", "flota", "r"):
        if clave in k: d[clave] = k.pop(clave)
    d["props"] = {**d["props"], **k}
    if cara: d["cara"] = cara
    if voz: d["voz"] = voz
    return d

ORBI = dict(cabeza="orbi", ropa="mesero", c2="#2f6fd6", pant="#121418")
COMI = dict(cabeza="comi", ropa="sastre", c1="#b5179e", c2="#ffd6ef", piel="#e6b08a")
ROSA = dict(piel="#e3b48c", pelo="recogido", colorPelo="#a8a8a8", ropa="delantal", c1="#2a9d8f", edad=1, lentes=True)
ZOMBI = lambda c1, pelo="corto": dict(zombi=True, ropa="harapos", c1=c1, pant="#33332e", pelo=pelo, colorPelo="#2a2a20", pose="zombi", camina=True)
V = {
 "narrador": dict(nombre="NARRADOR", color="#d8c08a", voz=("es-CO-GonzaloNeural", "-10%", "-16Hz"), fx="narrador"),
 "orbi": dict(nombre="ORBI", color="#7fd0f5", voz=("es-CO-GonzaloNeural", "-2%", "-6Hz")),
 "comi": dict(nombre="COMI", color="#ff8fd3", voz=("es-MX-DaliaNeural", "+10%", "+4Hz"), fx="villano"),
 "rosa": dict(nombre="DOÑA ROSA", color="#7fd3c7", voz=("es-CO-SalomeNeural", "+2%", "-6Hz")),
}

EPISODIOS = {
 # ───────────── Homenaje a la guerra mundial de los muertos vivientes
 "hambre-mundial-z": dict(
  gancho="No era un virus. Era el hambre.", producto="dom", frase="La cura llega en 25 minutos.",
  copy="Dos horas esperando un domicilio y la ciudad cambió para siempre 🧟‍♂️🍔 ¿Cuánto es lo máximo que has esperado un pedido?",
  hashtags="#Zombies #Cine #Domicilios #Comedia #Bogota",
  reparto={**V, "z1": dict(nombre="HAMBRIENTO", color="#a8b88a", voz=("es-MX-JorgeNeural", "-18%", "-22Hz"), fx="villano"),
           "z2": dict(nombre="HAMBRIENTA", color="#a8b88a", voz=("es-PE-CamilaNeural", "-15%", "-18Hz"), fx="villano"),
           "andres": dict(nombre="ANDRÉS, SOBREVIVIENTE", color="#e8c38a", voz=("es-CO-GonzaloNeural", "+10%", "+4Hz"))},
  planos=[
   dict(fondo="ruinas", cam=[[540, 800, 1.0, 0], [540, 1100, 1.25, 0]], grado="apocalipsis", musica="tension", letrero="BOGOTÁ · VIERNES · 8:47 P. M.", min=6.0,
        fx=[dict(tipo="polvo")], actores=[],
        lineas=[("narrador", "Empezó un viernes, a las ocho de la noche.", 0.8, {}), ("narrador", "Nadie entendía por qué los pedidos no llegaban.", 0.5, {})]),
   dict(fondo="muro", fondoOp=dict(altura=0.5), dof=6, cam=[[540, 900, 1.1, 0], [540, 900, 1.2, 0]], grado="apocalipsis", titulo=["Hambre Mundial Z", "una historia de domicilios"], trans="negro", min=3.2, actores=[], lineas=[]),
   dict(fondo="muro", fondoOp=dict(altura=A(0.3, 1.05)), cam=[[540, 1300, 1.0, 0], [540, 820, 1.05, 0]], grado="apocalipsis", musica="tension", min=4.6,
        actores=[], lineas=[("narrador", "Dos horas esperando un domicilio… y la gente empezó a cambiar.", 0.6, {})]),
   dict(fondo="ruinas", cam=[[540, 1150, 1.0, 0], [540, 1100, 1.12, 0]], grado="apocalipsis", musica="accion", mano=8, trans="barrido",
        actores=[H("z1", 260, 1480, 1.0, a=dict(x=330, y=1560, s=1.15), **ZOMBI("#4a5a6a")), H("z2", 760, 1420, 0.9, a=dict(x=700, y=1520, s=1.05), **ZOMBI("#6a4a5a", "largo")),
                 H("andres", 540, 1700, 1.35, cara="miedo", piel="#c98e62", pelo="corto", colorPelo="#1a120c", ropa="chaqueta", c1="#3a2a20", c2="#d8d0c0", pant="#2a3446", pose="telefono", prop="telefono")],
        lineas=[("z1", "Hambreeee…", 0.3, {}), ("andres", "¡Mi pedido salió hace dos horas!", 0.2, {}), ("z2", "La app dice… «está cerca»…", 0.3, {})]),
   dict(fondo="ruinas", fondoOp=dict(helicoptero=False), cam=[[540, 1050, 1.35, 0], [540, 1080, 1.15, 0]], grado="audaz", musica="heroe", trans="flash",
        fx=[dict(tipo="destello", p=0.05, x=540, y=900)],
        actores=[H("orbi", 540, 1600, 1.4, cara="orgulloso", pose="ofrece", prop="bandeja", **ORBI)],
        lineas=[("orbi", "Los domicilios propios llegan en veinticinco minutos.", 0.6, {}),
                ("orbi", "Y sin comisión.", 0.2, {"pedido": "Domicilio propio · Pedido #212|Llega en 25 min · 0 % de comisión"})]),
   dict(fondo="ruinas", fondoOp=dict(helicoptero=False), cam=[[540, 1150, 1.05, 0], [540, 1150, 1.1, 0]], grado="nostalgia", musica="romance",
        actores=[H("z1", 300, 1560, 1.15, cara="sorpresa", piel="#c98e62", ropa="harapos", c1="#4a5a6a", pant="#33332e", pelo="corto", colorPelo="#2a2a20", pose="mano_pecho"),
                 H("orbi", 760, 1560, 1.15, cara="normal", pose="reposo", **ORBI)],
        lineas=[("z1", "¿Qué… qué me pasó?", 0.5, {}), ("orbi", "Comió.", 0.4, {"caras": {"orbi": "guino"}})]),
   dict(fondo="muro", fondoOp=dict(altura=0.2), dof=5, cam=[[540, 900, 1.0, 0], [540, 860, 1.06, 0]], grado="apocalipsis", musica="fin", min=3.6, trans="negro",
        actores=[], lineas=[("narrador", "La cura no era una vacuna. Era un domicilio propio.", 0.6, {})]),
  ]),
 # ───────────── Homenaje a los que caminan
 "los-que-esperan": dict(
  gancho="Llevaban 40 minutos sin que nadie los atendiera…", producto="play", frase="Aquí nadie vuelve a esperar.",
  copy="No eran zombis… eran clientes esperando al mesero 🧟 ¿Tú en qué minuto te conviertes?",
  hashtags="#Zombies #Series #Restaurante #Comedia #HumorColombiano",
  reparto={**V, "sheriff": dict(nombre="EL COMISARIO", color="#e8c38a", voz=("es-MX-JorgeNeural", "-4%", "-8Hz")),
           "mujer": dict(nombre="LA SOBREVIVIENTE", color="#e8b0a0", voz=("es-CO-SalomeNeural", "-4%", "-10Hz")),
           "cliente": dict(nombre="CLIENTE DE LA MESA 3", color="#a8b88a", voz=("es-VE-SebastianNeural", "-14%", "-18Hz"), fx="villano")},
  planos=[
   dict(fondo="carretera", cam=[[540, 1000, 1.0, 0], [540, 1150, 1.18, 0]], grado="caminantes", musica="misterio", letrero="DÍA 1 · AFUERAS DE LA CIUDAD", min=5.2,
        actores=[H("sheriff", 540, 1560, 1.2, cara="serio", piel="#c99a72", pelo="corto", colorPelo="#2a1a10", barba="sombra", ropa="camisa", c1="#c9b79a", pant="#33465e", chaleco="#6b4a2a", sombrero="vaquero", camina=True, a=dict(y=1640, s=1.35))],
        lineas=[("sheriff", "Me desperté… y el mundo ya no era el mismo.", 0.8, {})]),
   dict(fondo="refugio", fondoOp=dict(manos=True), cam=[[540, 1000, 1.0, 0], [540, 1050, 1.12, 0]], grado="caminantes", musica="tension", mano=5,
        actores=[H("cliente", 540, 1420, 0.95, **ZOMBI("#5a6a5a")),
                 H("sheriff", 250, 1640, 1.3, cara="serio", piel="#c99a72", pelo="corto", colorPelo="#2a1a10", barba="sombra", ropa="camisa", c1="#c9b79a", pant="#33465e", chaleco="#6b4a2a", sombrero="vaquero"),
                 H("mujer", 830, 1640, 1.3, cara="serio", piel="#7a4b2e", pelo="rizado", colorPelo="#140c08", ropa="chaqueta", c1="#2a2a2a", c2="#6a5a4a", pant="#2a2622")],
        lineas=[("cliente", "Meseeerooo…", 0.4, {}), ("sheriff", "¿Cuánto llevan esperando?", 0.3, {}), ("mujer", "Cuarenta minutos. Ya no son personas.", 0.3, {})]),
   dict(fondo="carretera", dof=6, cam=[[540, 900, 1.1, 0], [540, 900, 1.18, 0]], grado="caminantes", titulo=["Los que esperan", "temporada 1"], trans="negro", min=3.0, actores=[], lineas=[]),
   dict(fondo="refugio", fondoOp=dict(manos=True), cam=[[540, 900, 1.1, -3], [540, 960, 1.2, 3]], grado="caminantes", musica="accion", mano=10,
        fx=[dict(tipo="pum", linea=1, dt=0.6, texto="¡CRAC!", x=540, y=520, color="#e8d8b0")],
        actores=[H("sheriff", 300, 1640, 1.3, cara="enojo", piel="#c99a72", pelo="corto", colorPelo="#2a1a10", barba="sombra", ropa="camisa", c1="#c9b79a", pant="#33465e", chaleco="#6b4a2a", sombrero="vaquero", pose="ofrece", prop="linterna"),
                 H("mujer", 800, 1640, 1.3, cara="miedo", piel="#7a4b2e", pelo="rizado", colorPelo="#140c08", ropa="chaqueta", c1="#2a2a2a", c2="#6a5a4a", pant="#2a2622")],
        lineas=[("sheriff", "¡Necesitamos un mesero!", 0.3, {}), ("mujer", "No hay meseros. Solo quedamos nosotros.", 0.3, {})]),
   dict(fondo="refugio", cam=[[540, 1100, 1.0, 0], [540, 1080, 1.06, 0]], grado="audaz", musica="heroe", trans="flash",
        fx=[dict(tipo="qr", linea=0, linea1=1, de=[540, 900], mesas=[[540, 1500], [150, 1150], [930, 1150]]), dict(tipo="destello", p=0.04, x=540, y=900)],
        actores=[H("orbi", 540, 1700, 1.4, cara="orgulloso", pose="ofrece", **ORBI)],
        lineas=[("orbi", "No necesitan un mesero. Necesitan un QR.", 0.5, {}), ("orbi", "Cada mesa pide sola, en diez segundos.", 0.3, {"pedido": "Mesa 3 · Enviado a cocina ✓|Bandeja paisa · pidió desde el QR"})]),
   dict(fondo="refugio", cam=[[540, 1100, 1.1, 0], [540, 1100, 1.16, 0]], grado="nostalgia", musica="romance",
        actores=[H("cliente", 330, 1640, 1.3, cara="sonrisa", piel="#c98e62", ropa="harapos", c1="#5a6a5a", pant="#33332e", pelo="corto", colorPelo="#2a2a20", pose="telefono", prop="telefono"),
                 H("sheriff", 800, 1640, 1.3, cara="sorpresa", piel="#c99a72", pelo="corto", colorPelo="#2a1a10", barba="sombra", ropa="camisa", c1="#c9b79a", pant="#33465e", chaleco="#6b4a2a", sombrero="vaquero")],
        lineas=[("cliente", "Una bandeja paisa, por favor.", 0.4, {}), ("sheriff", "Están… pidiendo.", 0.4, {}), ("sheriff", "Por primera vez… hay esperanza.", 0.6, {})]),
  ]),
 # ───────────── Homenaje al diario del amor eterno
 "el-diario-de-orbi": dict(
  gancho="Él le lee todos los días la misma historia…", producto="play", frase="Hay historias que merecen ser atendidas.",
  copy="Un amor que esperó años… a que le tomaran el pedido 💌☕ Etiqueta a esa persona con la que siempre vas a La Fonda.",
  hashtags="#Romance #Cine #AmorVerdadero #Restaurante #HumorColombiano",
  reparto={**V, "noe": dict(nombre="NOÉ", color="#e8c38a", voz=("es-CO-GonzaloNeural", "-12%", "-20Hz")), "ali": dict(nombre="ALICIA", color="#f0b0c0", voz=("es-CO-SalomeNeural", "-10%", "-8Hz")),
           "noej": dict(nombre="NOÉ, 1996", color="#e8c38a", voz=("es-CO-GonzaloNeural", "+6%", "+2Hz")), "alij": dict(nombre="ALICIA, 1996", color="#f0b0c0", voz=("es-CO-SalomeNeural", "+8%", "+6Hz"))},
  planos=[
   dict(fondo="residencia", cam=[[540, 1050, 1.0, 0], [540, 1050, 1.12, 0]], grado="nostalgia", musica="romance", letrero="HOGAR SAN RAFAEL · HOY",
        actores=[H("noe", 330, 1640, 1.3, cara="serio", piel="#d8a882", pelo="peinado", colorPelo="#d8d8d8", edad=1, ropa="traje", c1="#5a5a5a", c2="#3a2a20", lentes=True, pose="leer", prop="libro"),
                 H("ali", 790, 1640, 1.3, cara="triste", piel="#efc8a8", pelo="recogido", colorPelo="#e0e0e0", edad=1, ropa="vestido", c1="#8a9ab8", collar=True)],
        lineas=[("noe", "Ella ya no recuerda nada.", 0.7, {}), ("noe", "Así que todos los días le leo nuestra historia.", 0.4, {})]),
   dict(fondo="lago", fondoOp=dict(bote=False), dof=6, cam=[[540, 900, 1.1, 0], [540, 900, 1.2, 0]], grado="nostalgia", titulo=["El diario de Orbi", "una historia de amor"], trans="negro", min=3.2, actores=[], lineas=[]),
   dict(fondo="lago", fondoOp=dict(bote=False), cam=[[540, 1100, 1.05, 0], [540, 1100, 1.15, 0]], grado="nostalgia", musica="romance", letrero="VERANO DE 1996",
        actores=[H("noej", 330, 1620, 1.3, cara="sonrisa", piel="#d8a882", pelo="peinado", colorPelo="#2a1a10", ropa="camisa", c1="#f2ede2", pant="#8a7a5a"),
                 H("alij", 780, 1620, 1.3, cara="sonrisa", piel="#efc8a8", pelo="ondas", colorPelo="#b8752a", ropa="vestido", c1="#f4f0e6")],
        lineas=[("noej", "¿Cuál es tu plato favorito?", 0.5, {}), ("alij", "No sé… en La Fonda nunca nos alcanzan a atender.", 0.3, {})]),
   dict(fondo="lago", fondoOp=dict(bote=False), cam=[[540, 1050, 1.25, 0], [540, 1000, 1.4, 0]], grado="frio", musica="romance", trans="barrido",
        fx=[dict(tipo="lluvia"), dict(tipo="rayo", p=0.05, x=900, y=800)],
        actores=[H("alij", 380, 1620, 1.3, cara="enojo", piel="#efc8a8", pelo="ondas", colorPelo="#b8752a", ropa="vestido", c1="#f4f0e6"),
                 H("noej", 720, 1620, 1.3, cara="triste", piel="#d8a882", pelo="peinado", colorPelo="#2a1a10", ropa="camisa", c1="#f2ede2", pant="#8a7a5a")],
        lineas=[("alij", "¿Por qué no volviste?", 0.3, {}), ("noej", "¡Volví todos los días! A La Fonda.", 0.2, {}), ("alij", "¿Y?", 0.2, {}), ("noej", "Nunca nos tomaron el pedido.", 0.3, {})]),
   dict(fondo="residencia", cam=[[540, 1050, 1.05, 0], [540, 1050, 1.12, 0]], grado="nostalgia", musica="romance", trans="negro",
        actores=[H("noe", 280, 1640, 1.25, cara="sonrisa", piel="#d8a882", pelo="peinado", colorPelo="#d8d8d8", edad=1, ropa="traje", c1="#5a5a5a", c2="#3a2a20", lentes=True, pose="reposo"),
                 H("ali", 540, 1640, 1.25, cara="sorpresa", piel="#efc8a8", pelo="recogido", colorPelo="#e0e0e0", edad=1, ropa="vestido", c1="#8a9ab8", collar=True),
                 H("orbi", 860, 1640, 1.25, cara="feliz", pose="ofrece", prop="bandeja", aparece=0.35, **ORBI)],
        lineas=[("ali", "¿Y ahora sí nos atienden?", 0.5, {}), ("orbi", "Dos tintos, como en el noventa y seis.", 0.5, {"pedido": "Mesa 1 · Enviado ✓|Dos tintos · pidieron desde el QR"})]),
   dict(fondo="residencia", cam=[[420, 1000, 1.3, 0], [420, 980, 1.45, 0]], grado="nostalgia", musica="romance", min=4.0,
        actores=[H("noe", 280, 1640, 1.25, cara="sonrisa", piel="#d8a882", pelo="peinado", colorPelo="#d8d8d8", edad=1, ropa="traje", c1="#5a5a5a", c2="#3a2a20", lentes=True),
                 H("ali", 540, 1640, 1.25, cara="sonrisa", piel="#efc8a8", pelo="recogido", colorPelo="#e0e0e0", edad=1, ropa="vestido", c1="#8a9ab8", collar=True, pose="mano_pecho")],
        lineas=[("ali", "Noé… eres tú.", 0.6, {}), ("noe", "Siempre fui yo.", 0.6, {})]),
  ]),
 # ───────────── Homenaje a la comedia romántica de los diez días
 "perder-un-cliente": dict(
  gancho="Cómo perder un cliente en 10 días (paso a paso)", producto="dom", frase="Para no perderlo, cúmplale.",
  copy="Día 1: comisión. Día 5: cargo por lluvia. Día 10: adiós 💔 ¿En qué día te habrías ido tú?",
  hashtags="#Comedia #Romcom #Domicilios #Emprendedores #Restaurante",
  reparto={**V, "andres": dict(nombre="ANDRÉS, EL CLIENTE", color="#e8c38a", voz=("es-CO-GonzaloNeural", "+8%", "+2Hz"))},
  planos=[
   dict(fondo="oficina", fondoOp=dict(dias=0), cam=[[540, 1050, 1.0, 0], [540, 1050, 1.08, 0]], grado="romcom", musica="romcom", letrero="REVISTA «TODO A DOMICILIO»",
        actores=[H("comi", 380, 1640, 1.35, cara="diva", pose="saluda", **COMI)],
        lineas=[("comi", "Hola, soy Comi. Columnista y experta en clientes.", 0.4, {}), ("comi", "Hoy les enseño a perder uno en diez días.", 0.2, {})]),
   dict(fondo="oficina", fondoOp=dict(dias=0), dof=6, cam=[[540, 900, 1.1, 0], [540, 900, 1.18, 0]], grado="romcom", titulo=["Cómo perder un cliente", "en 10 días"], trans="flash", min=3.0, actores=[], lineas=[]),
   dict(fondo="oficina", fondoOp=dict(dias=A(0, 3, 0.1, 0.9, "lineal")), cam=[[700, 900, 1.15, 0], [700, 900, 1.2, 0]], grado="romcom", musica="romcom",
        actores=[H("comi", 300, 1640, 1.3, cara="diva", pose="senala", **COMI)],
        lineas=[("comi", "Día uno: le cobras el veintisiete por ciento.", 0.3, {}), ("comi", "Día tres: la comida le llega fría.", 0.3, {})]),
   dict(fondo="oficina", fondoOp=dict(dias=A(3, 7, 0.1, 0.7, "lineal")), cam=[[540, 1050, 1.05, 0], [540, 1050, 1.1, 0]], grado="romcom", musica="romcom",
        actores=[H("comi", 300, 1640, 1.3, cara="diva", pose="senala", **COMI),
                 H("andres", 790, 1640, 1.3, cara="enojo", piel="#c98e62", pelo="peinado", colorPelo="#1a120c", barba="sombra", ropa="traje", c1="#2b3346", c2="#7a1f2a", pose="telefono", prop="telefono")],
        lineas=[("comi", "Día cinco: inventas un cargo por lluvia.", 0.3, {}), ("andres", "¿Cargo por lluvia? ¡Si está haciendo sol!", 0.2, {})]),
   dict(fondo="oficina", fondoOp=dict(dias=A(7, 10, 0, 0.5, "lineal")), cam=[[600, 1050, 1.1, 0], [600, 1050, 1.15, 0]], grado="romcom", musica="tension",
        fx=[dict(tipo="pum", linea=1, dt=0.4, texto="¡ADIÓS!", x=780, y=700, color="#ffd6ef")],
        actores=[H("comi", 300, 1640, 1.3, cara="diva", **COMI),
                 H("andres", 790, 1640, 1.3, cara="serio", piel="#c98e62", pelo="peinado", colorPelo="#1a120c", barba="sombra", ropa="traje", c1="#2b3346", c2="#7a1f2a", a=dict(x=1300), de=0.7, hasta=1, camina=True)],
        lineas=[("comi", "Y día diez…", 0.3, {}), ("andres", "Me voy. Desde hoy le pido directo al restaurante.", 0.2, {"caras": {"comi": "shock"}})]),
   dict(fondo="refugio", cam=[[540, 1100, 1.05, 0], [540, 1100, 1.1, 0]], grado="calido", musica="heroe", trans="barrido",
        actores=[H("rosa", 330, 1640, 1.3, cara="sonrisa", pose="mano_pecho", **ROSA), H("orbi", 790, 1640, 1.3, cara="orgulloso", pose="ofrece", prop="bandeja", **ORBI)],
        lineas=[("rosa", "Domicilio propio, sin comisión, y llega caliente.", 0.3, {"pedido": "Domicilio propio · Pedido #10|0 % de comisión · Llega caliente"}),
                ("orbi", "A un cliente no se le pierde. Se le cumple.", 0.3, {})]),
  ]),
 # ───────────── Homenaje al musical de la ciudad de las estrellas
 "ciudad-de-las-luces": dict(
  gancho="Ella soñaba con un restaurante lleno. Él, con tocar jazz.", producto="play", frase="Aquí, nadie espera.",
  copy="Una vista horrible, ¿cierto? 🌆🎷 La peor. Comenta 🎹 si viste el guiño.",
  hashtags="#Musical #Cine #Jazz #Restaurante #Romance",
  reparto={**V, "mia": dict(nombre="MÍA", color="#ffd27a", voz=("es-CO-SalomeNeural", "+6%", "+4Hz")), "seb": dict(nombre="SEBASTIÁN", color="#a8c8ff", voz=("es-MX-JorgeNeural", "+2%", "-4Hz"))},
  planos=[
   dict(fondo="colina", cam=[[540, 1100, 1.0, 0], [540, 1150, 1.1, 0]], grado="lalaland", musica="jazz", letrero="EL MIRADOR · ATARDECER",
        actores=[H("mia", 330, 1700, 1.2, cara="sonrisa", piel="#f0c8a8", pelo="ondas", colorPelo="#7a3a1a", ropa="vestido", c1="#f2c94c", collar=True, camina=True, a=dict(x=420)),
                 H("seb", 780, 1700, 1.2, cara="serio", piel="#e8bc98", pelo="peinado", colorPelo="#5a3a1a", ropa="traje", c1="#e8e4da", c2="#2a2a3a", pant="#2a2a3a", camina=True, a=dict(x=700))],
        lineas=[("seb", "Es una vista horrible.", 0.6, {}), ("mia", "La peor.", 0.3, {"caras": {"seb": "sonrisa"}})]),
   dict(fondo="colina", dof=6, cam=[[540, 1000, 1.1, 0], [540, 1000, 1.18, 0]], grado="lalaland", titulo=["La ciudad de las luces", "un musical de restaurante"], trans="flash", min=3.0, actores=[], lineas=[]),
   dict(fondo="colina", cam=[[540, 1150, 1.1, 0], [540, 1120, 1.2, 0]], grado="lalaland", musica="jazz", mano=3,
        fx=[dict(tipo="destello", linea=1, x=540, y=900)],
        actores=[H("mia", 400, 1700, 1.2, cara="triste", piel="#f0c8a8", pelo="ondas", colorPelo="#7a3a1a", ropa="vestido", c1="#f2c94c", collar=True, pose="baile"),
                 H("seb", 680, 1700, 1.2, cara="sonrisa", piel="#e8bc98", pelo="peinado", colorPelo="#5a3a1a", ropa="traje", c1="#e8e4da", c2="#2a2a3a", pant="#2a2a3a", pose="baile")],
        lineas=[("mia", "Mi restaurante se llena… pero la gente espera una hora para pedir.", 0.4, {}), ("seb", "Entonces que no esperen.", 0.3, {})]),
   dict(fondo="club", cam=[[540, 1100, 1.05, 0], [540, 1080, 1.12, 0]], grado="calido", musica="jazz", trans="barrido",
        actores=[H("seb", 300, 1720, 1.25, cara="sonrisa", piel="#e8bc98", pelo="peinado", colorPelo="#5a3a1a", ropa="traje", c1="#e8e4da", c2="#2a2a3a", pant="#2a2a3a"),
                 H("orbi", 760, 1720, 1.25, cara="feliz", pose="saluda", **ORBI)],
        lineas=[("seb", "Es como el jazz: cada mesa toca su parte.", 0.4, {}), ("orbi", "Y yo llevo el ritmo. Cada mesa pide desde su celular.", 0.3, {"pedido": "Mesa 6 · Enviado a cocina ✓|Dos limonadas · pidieron desde el QR"})]),
   dict(fondo="colina", cam=[[540, 1100, 1.15, 0], [540, 1050, 1.3, 0]], grado="lalaland", musica="romance", min=4.4, trans="negro",
        actores=[H("mia", 420, 1700, 1.2, cara="sonrisa", piel="#f0c8a8", pelo="ondas", colorPelo="#7a3a1a", ropa="vestido", c1="#f2c94c", collar=True, pose="mano_pecho"),
                 H("seb", 680, 1700, 1.2, cara="sonrisa", piel="#e8bc98", pelo="peinado", colorPelo="#5a3a1a", ropa="traje", c1="#e8e4da", c2="#2a2a3a", pant="#2a2a3a")],
        lineas=[("mia", "¿Y si lo hubiéramos tenido desde el principio?", 0.5, {}), ("seb", "Habríamos tenido más tiempo para bailar.", 0.4, {})]),
  ]),
 # ───────────── Homenaje a la ciudad de neón y los replicantes
 "blade-mesero-2049": dict(
  gancho="¿Es humano… o es una app que cobra comisión?", producto="dom", frase="Más humano que humano.",
  copy="He visto cosas que ustedes no creerían… domicilios sin comisión 🌧️🌃 ¿Pasarías la prueba?",
  hashtags="#CienciaFiccion #Cine #Domicilios #Cyberpunk #Emprendedores",
  reparto={**V, "cazador": dict(nombre="EL CAZADOR", color="#e8c38a", voz=("es-MX-JorgeNeural", "-10%", "-14Hz"), fx="narrador"),
           "sospechoso": dict(nombre="EL SOSPECHOSO", color="#ff8fd3", voz=("es-MX-DaliaNeural", "+0%", "-6Hz"))},
  planos=[
   dict(fondo="neon", cam=[[540, 900, 1.0, 0], [540, 1150, 1.15, 0]], grado="neon", musica="synth", letrero="BOGOTÁ · 2049", min=6.0,
        fx=[dict(tipo="lluvia")],
        actores=[H("cazador", 540, 1780, 1.3, voz="narrador", cara="serio", piel="#b5835a", pelo="corto", colorPelo="#141010", barba="sombra", ropa="gabardina", c1="#4a3a2a", c2="#d8d2c4", camina=True, a=dict(y=1820, s=1.45))],
        lineas=[("narrador", "En el dos mil cuarenta y nueve, las apps ya parecían humanas.", 0.8, {}), ("narrador", "Mi trabajo era encontrarlas.", 0.4, {})]),
   dict(fondo="neon", dof=6, cam=[[540, 900, 1.1, 0], [540, 900, 1.18, 0]], grado="neon", titulo=["Blade Mesero 2049", "más humano que humano"], trans="negro", min=3.2, fx=[dict(tipo="lluvia")], actores=[], lineas=[]),
   dict(fondo="interrogatorio", cam=[[540, 1100, 1.05, 0], [540, 1100, 1.15, 0]], grado="audaz", musica="tension",
        actores=[H("cazador", 220, 1720, 1.25, cara="serio", piel="#b5835a", pelo="corto", colorPelo="#141010", barba="sombra", ropa="gabardina", c1="#4a3a2a", c2="#d8d2c4", voz="cazador"),
                 H("sospechoso", 860, 1720, 1.25, cara="serio", piel="#e6b08a", pelo="recogido", colorPelo="#2a0a1a", ropa="sastre", c1="#5a1048", c2="#ffd6ef", lentes="sol", voz="sospechoso")],
        lineas=[("cazador", "Le haré unas preguntas. Es una prueba de rutina.", 0.5, {}), ("sospechoso", "Adelante.", 0.3, {}),
                ("cazador", "Un restaurante vende cien mil pesos. ¿Cuánto se queda usted?", 0.4, {}), ("sospechoso", "Solo veintisiete mil. Es lo normal.", 0.4, {})]),
   dict(fondo="interrogatorio", cam=[[700, 1000, 1.2, 3], [700, 1020, 1.3, -3]], grado="neon", musica="accion", mano=8,
        fx=[dict(tipo="rayo", linea=0, dt=-0.2, x=860, y=900), dict(tipo="disparo", linea=2, dt=0.1, de=[420, 1240], a=[860, 1250], golpea="comi", texto="0 %", color="#ff5fa8")],
        actores=[H("cazador", 220, 1720, 1.25, cara="enojo", piel="#b5835a", pelo="corto", colorPelo="#141010", barba="sombra", ropa="gabardina", c1="#4a3a2a", c2="#d8d2c4", pose="apunta", prop="escaner", voz="cazador"),
                 H("comi", 860, 1720, 1.25, cara="enojo", desaparece=0.85, **COMI)],
        lineas=[("comi", "¡Sí! ¡Soy una app! ¡Y cobro comisión!", 0.4, {}), ("cazador", "Lo sabía.", 0.3, {}), ("cazador", "Cero por ciento.", 0.3, {})]),
   dict(fondo="neon", fondoOp=dict(holoX=800, holoY=600), cam=[[540, 1150, 1.25, 0], [540, 1080, 1.45, 0]], grado="neon", musica="synth", min=5.0, trans="barrido",
        fx=[dict(tipo="lluvia")],
        actores=[H("orbi", 420, 1760, 1.3, cara="normal", **ORBI)],
        lineas=[("orbi", "He visto cosas que ustedes no creerían.", 0.6, {}), ("orbi", "Domicilios llegar calientes… sin comisión.", 0.4, {"pedido": "Domicilio propio · Pedido #2049|0 % de comisión · Todo queda en caja"}),
                ("orbi", "Todos esos momentos… se quedan en la caja del restaurante.", 0.4, {})]),
  ]),
}
