"""Guiones de «La Liga de la Cocina»: un equipo de superhéroes hechos de comida. Cine alegre y épico.
Parodias sin nombres, logos ni personajes registrados. Formato de planos de «heroes» (ver heroes/episodios.py).
Actores: tipo="fruta" (props de heroeFruta: fruta, capa, antifaz, emblema, tiara, anillo, ciber, lazo, rayos, alas), "lord", "orbi", "comi", "rosa", "porcentaje"."""

def A(v0, v1, p0=0, p1=1, c="ease"): return {"anim": [v0, v1, p0, p1, c]}
def F(id, x, piso, s=1.0, cara=None, **k):
    d = dict(id=id, tipo="fruta", x=x, y=piso - 170 * s, s=s)
    for c in ("a", "de", "hasta", "curva", "aparece", "desaparece", "flota", "r", "voz"):
        if c in k: d[c] = k.pop(c)
    if "a" in d and "piso" in d["a"]: d["a"]["y"] = d["a"].pop("piso") - 170 * d["a"].get("s", s)
    d["props"] = k
    if cara: d["cara"] = cara
    return d
def O(x, y, s=0.8, cara="orgulloso", **k):
    d = dict(id="orbi", tipo="orbi", x=x, y=y, s=s, cara=cara, props=dict(traje="capa", viento=k.pop("viento", 0.7)))
    d.update(k); return d

EMPANADA = dict(fruta="empanada", capa="url(#capaRoja)", emblema=dict(letra="E", fondo="#ffd166", color="#c01b2c"))
AREPA = dict(fruta="arepa", tiara=True, acc=["aretes"], emblema=dict(letra="A", fondo="#c01b2c", color="#ffd166"))
TINTO = dict(fruta="tinto", antifaz="#c01b2c", alas=True, emblema=dict(letra="R", fondo="#c01b2c", color="#ffd166"))
AGUACATE = dict(fruta="aguacate", antifaz="#1f6a1f", anillo=True, emblema=dict(letra="G", fondo="#7cff6a", color="#14361a"))
PAPA = dict(fruta="papa", ciber=True, emblema=dict(letra="C", fondo="#9aa3b0", color="#111"))
V = {
 "narrador": dict(nombre="NARRADOR", color="#ffd166", voz=("es-CO-GonzaloNeural", "-8%", "-14Hz"), fx="narrador"),
 "orbi": dict(nombre="ORBI", color="#5fc9f1", voz=("es-CO-GonzaloNeural", "+0%", "-6Hz")),
 "empanada": dict(nombre="SÚPER EMPANADA", color="#ff6b6b", voz=("es-PE-CamilaNeural", "+6%", "+4Hz")),
 "arepa": dict(nombre="MUJER AREPA", color="#ffd166", voz=("es-CO-SalomeNeural", "+4%", "+0Hz")),
 "tinto": dict(nombre="RELÁMPAGO TINTO", color="#ff9a6b", voz=("es-VE-SebastianNeural", "+28%", "+6Hz")),
 "aguacate": dict(nombre="GUARDIÁN AGUACATE", color="#7cff6a", voz=("es-MX-JorgeNeural", "-6%", "-10Hz")),
 "papa": dict(nombre="CIBER-PAPA", color="#c7ccd6", voz=("es-AR-TomasNeural", "-4%", "-8Hz"), fx="radio"),
 "lord": dict(nombre="LORD COMISIÓN", color="#c48aff", voz=("es-CU-ManuelNeural", "-16%", "-24Hz"), fx="villano"),
 "comi": dict(nombre="COMI", color="#ff8fd3", voz=("es-MX-DaliaNeural", "+12%", "+6Hz"), fx="villano"),
 "rosa": dict(nombre="DOÑA ROSA", color="#7fd3c7", voz=("es-CO-SalomeNeural", "+4%", "-6Hz")),
 "julian": dict(nombre="JULIÁN, EL MESERO", color="#ffd166", voz=("es-MX-JorgeNeural", "+8%", "+2Hz")),
 "p27": dict(nombre="EL 27", color="#ff9a6b", voz=("es-CU-ManuelNeural", "-2%", "-12Hz"), fx="villano"),
 "pan": dict(nombre="PADRE PAN", color="#e8b070", voz=("es-ES-AlvaroNeural", "-6%", "-8Hz")),
}
LIGA = lambda piso, s=0.62: [O(540, piso - 470, 0.62, viento=0.8),
    F("empanada", 130, piso, s, cara="orgullo", **EMPANADA), F("arepa", 330, piso, s, cara="orgullo", **AREPA), F("tinto", 750, piso, s, cara="guino", **TINTO),
    F("aguacate", 950, piso, s, cara="orgullo", **AGUACATE), F("papa", 540, piso + 60, s, cara="normal", **PAPA)]

EPISODIOS = {
 "liga-cap1": dict(
  gancho="Cinco héroes. Una cocina. Cero comisiones.", producto="dom", selloTraje="capa", frase="La Liga de la Cocina volverá.",
  copy="¿Quién es tu favorito de la Liga? 🦸‍♀️🥟☕🥑 Comenta su nombre y le damos su propia película.",
  hashtags="#Superheroes #Comedia #Comida #Restaurante #HumorColombiano",
  reparto=V,
  planos=[
   dict(fondo="ciudad", cam=[[540, 700, 1.0, 0], [540, 1100, 1.25, 0]], grado="noche", musica="misterio", min=4.6, fx=[dict(tipo="rayo", p=0.55, x=300, y=1200)], actores=[],
        lineas=[("narrador", "Cuando la ciudad tuvo hambre…", 0.8, {}), ("narrador", "…la cocina respondió.", 0.6, {})]),
   dict(fondo="ciudad", fondoOp=dict(tormenta=True), dof=7, cam=[[540, 900, 1.1, 0], [540, 900, 1.2, 0]], grado="epico", titulo=["La Liga de la Cocina", "Capítulo 1 · El llamado"], trans="flash", min=3.0, actores=[], lineas=[]),
   dict(fondo="cuartel", cam=[[540, 1050, 1.15, 0], [540, 1000, 1.25, 0]], grado="frio", musica="tension", letrero="CUARTEL DE LA LIGA · 9:00 P. M.",
        actores=[O(540, 980, 0.95, cara="enojado")],
        lineas=[("orbi", "Lord Comisión volvió.", 0.5, {}), ("orbi", "Y quiere quedarse con el veintisiete por ciento de todo.", 0.3, {})]),
   dict(fondo="ciudad", cam=[[540, 1100, 1.2, 0], [540, 1150, 1.1, 0]], grado="epico", musica="heroe", trans="barrido", min=2.6, letrero="SÚPER EMPANADA · FUERZA DE HORNO",
        fx=[dict(tipo="destello", p=0.35, x=540, y=1100)],
        actores=[F("empanada", 540, 1500, 1.4, cara="orgullo", a=dict(y=1500 - 170 * 1.4), de=0, hasta=0.3, curva="out", brazo="arriba", **EMPANADA)],
        lineas=[("empanada", "¿Alguien pidió algo crujiente?", 0.6, {})]),
   dict(fondo="azotea", cam=[[540, 1150, 1.15, 0], [540, 1150, 1.25, 0]], grado="epico", musica="heroe", trans="flash", min=2.6, letrero="MUJER AREPA · LAZO DE QUESO",
        actores=[F("arepa", 400, 1460, 1.3, cara="orgullo", lazo=[520, 120], **AREPA)],
        lineas=[("arepa", "Con mi lazo de queso, nadie miente.", 0.4, {})]),
   dict(fondo="ciudad", cam=[[540, 1150, 1.1, 0], [540, 1150, 1.15, 0]], grado="epico", musica="accion", trans="barrido", min=2.6, letrero="RELÁMPAGO TINTO · SÚPER VELOCIDAD",
        fx=[dict(tipo="velocidad", p=0, p1=0.5)],
        actores=[F("tinto", -300, 1500, 1.3, cara="guino", rayos=True, a=dict(x=540), de=0, hasta=0.35, curva="out", **TINTO)],
        lineas=[("tinto", "Ya llegué. Ya me fui. Y ya volví.", 0.6, {})]),
   dict(fondo="cuartel", cam=[[540, 1150, 1.2, 0], [540, 1100, 1.1, 0]], grado="epico", musica="heroe", trans="flash", min=2.6, letrero="GUARDIÁN AGUACATE · ANILLO VERDE",
        actores=[F("aguacate", 540, 1520, 1.25, cara="orgullo", **AGUACATE)],
        lineas=[("aguacate", "Ninguna comisión escapa a mi vista.", 0.4, {})]),
   dict(fondo="taller", cam=[[540, 1150, 1.2, 0], [540, 1150, 1.3, 0]], grado="frio", musica="tension", trans="barrido", min=2.6, letrero="CIBER-PAPA · MITAD PAPA, MITAD MÁQUINA",
        actores=[F("papa", 540, 1520, 1.3, cara="normal", **PAPA)],
        lineas=[("papa", "Sistema de domicilios propios: activado.", 0.4, {})]),
   dict(fondo="azotea", fondoOp=dict(senal=dict(x=640, y=430, x0=330, y0=1300, k=1)), cam=[[540, 1000, 1.05, 0], [540, 980, 1.12, 0]], grado="epico", musica="heroe", trans="flash",
        fx=[dict(tipo="destello", linea=0, x=540, y=900), dict(tipo="confeti", linea=1)],
        actores=LIGA(1180),
        lineas=[("orbi", "Juntos somos la Liga de la Cocina.", 0.5, {}), ("orbi", "Domicilios propios. Cero comisión.", 0.3, {})]),
   dict(fondo="callejon", cam=[[540, 900, 1.0, 0], [540, 1000, 1.18, 0]], grado="noche", musica="villano", trans="negro", min=4.0,
        fx=[dict(tipo="rayo", linea=0, dt=-0.3, x=540, y=900), dict(tipo="lluvia", k=0.6)],
        actores=[dict(id="lord", tipo="lord", x=540, y=1200, s=1.2, props={})],
        lineas=[("lord", "¡Ningún restaurante escapará de mi comisión!", 0.5, {})]),
  ]),
 "liga-cap2": dict(
  gancho="La batalla del 27 % empieza ahora", producto="dom", selloTraje="capa", frase="Misión cumplida: cero comisión.",
  copy="La Liga contra Lord Comisión 💥 ¿Qué poder te gustaría tener para tu restaurante?",
  hashtags="#Superheroes #Comedia #Domicilios #Restaurante #Emprendedores",
  reparto=V,
  planos=[
   dict(fondo="ciudad", cam=[[540, 1000, 1.0, 0], [540, 1050, 1.12, 0]], grado="noche", musica="villano", mano=6,
        fx=[dict(tipo="rayo", p=0.1, x=800, y=1100)],
        actores=[dict(id="lord", tipo="lord", x=540, y=1050, s=1.0, props={}),
                 dict(id="p15", tipo="porcentaje", x=170, y=1380, s=0.6, props=dict(n=15)), dict(id="p30", tipo="porcentaje", x=910, y=1380, s=0.6, props=dict(n=30))],
        lineas=[("lord", "¡Restaurantes de la ciudad: ríndanse y paguen!", 0.5, {})]),
   dict(fondo="ciudad", fondoOp=dict(tormenta=True), dof=7, cam=[[540, 900, 1.1, 0], [540, 900, 1.2, 0]], grado="epico", titulo=["La Liga de la Cocina", "Capítulo 2 · La batalla del 27 %"], trans="flash", min=3.0, actores=[], lineas=[]),
   dict(fondo="restaurante", fondoOp=dict(luz=0.8), cam=[[540, 1250, 1.1, 0], [540, 1200, 1.05, 0]], grado="calido", musica="heroe",
        actores=[dict(id="rosa", tipo="rosa", x=330, y=1560, s=0.75, props=dict(mostrador=True, billetes=4, cejas="triste")),
                 O(780, 900, 0.75, cara="orgulloso", aparece=0.3)],
        lineas=[("rosa", "¡Se quieren llevar todas mis ventas!", 0.4, {}), ("orbi", "¡Liga… a sus puestos!", 0.5, {})]),
   dict(fondo="ciudad", cam=[[0, 540, 1150, 1.05, -3], [0.5, 560, 1150, 1.12, 3], [1, 540, 1150, 1.05, 0]], grado="epico", musica="accion", mano=10, trans="barrido",
        fx=[dict(tipo="pum", linea=0, dt=0.6, texto="¡PUM!", x=820, y=1050, a="p30"), dict(tipo="velocidad", linea=1, p1=0.95),
            dict(tipo="pum", linea=1, dt=0.8, texto="¡ZAS!", x=260, y=1050, a="p15", dir=-1)],
        actores=[F("empanada", 560, 1500, 0.9, cara="enojo", brazo="arriba", **EMPANADA),
                 dict(id="p30", tipo="porcentaje", x=850, y=1280, s=0.7, props=dict(n=30), desaparece=0.4),
                 F("tinto", 1300, 1520, 0.8, cara="guino", rayos=True, a=dict(x=420), de=0.45, hasta=0.65, **TINTO),
                 dict(id="p15", tipo="porcentaje", x=230, y=1280, s=0.7, props=dict(n=15), desaparece=0.8)],
        lineas=[("empanada", "¡Fuera de mi ciudad, treinta por ciento!", 0.2, {}), ("tinto", "¡Y tú también, quince! ¡Muy lento!", 0.4, {})]),
   dict(fondo="callejon", cam=[[540, 1100, 1.1, 0], [540, 1100, 1.18, 0]], grado="noche", musica="tension",
        actores=[F("arepa", 300, 1520, 0.95, cara="enojo", lazo=[460, 40], **AREPA), dict(id="p27", tipo="porcentaje", x=780, y=1300, s=0.8, props=dict(n=27), cara="shock")],
        lineas=[("arepa", "¡Confiesa! ¿Cuánto cobras?", 0.3, {}), ("p27", "¡Está bien! ¡Me llevo una de cada cuatro ventas!", 0.3, {})]),
   dict(fondo="ciudad", cam=[[540, 1050, 1.0, 0], [540, 1050, 1.08, 0]], grado="epico", musica="accion", trans="flash", mano=6,
        fx=[dict(tipo="disparo", linea=2, dt=0.1, de=[330, 820], a=[600, 980], golpea="lord", texto="0 %"), dict(tipo="pum", linea=2, dt=0.5, texto="¡CERO!", x=600, y=760)],
        actores=[dict(id="lord", tipo="lord", x=640, y=1100, s=0.95, props={}, a=dict(s=0.35, y=1350), de=0.75, hasta=0.95),
                 F("aguacate", 160, 1560, 0.75, cara="orgullo", **AGUACATE), F("papa", 920, 1560, 0.75, cara="normal", **PAPA), O(330, 760, 0.6, cara="enojado")],
        lineas=[("lord", "¡Soy invencible!", 0.3, {}), ("papa", "Conectando domicilios propios… listo.", 0.3, {}), ("orbi", "Cero por ciento.", 0.3, {})]),
   dict(fondo="restaurante", fondoOp=dict(luz=1), cam=[[540, 1250, 1.05, 0], [540, 1220, 1.1, 0]], grado="calido", musica="heroe",
        fx=[dict(tipo="confeti", linea=0)],
        actores=[dict(id="rosa", tipo="rosa", x=320, y=1560, s=0.75, props=dict(mostrador=True, billetes=12, cejas="arriba", boca=0.9)),
                 O(800, 880, 0.7, cara="feliz")],
        lineas=[("rosa", "¡Mis domicilios ahora son míos!", 0.4, {"pedido": "Domicilio propio · Pedido #27|0 % de comisión · Todo queda en caja"}), ("orbi", "Misión cumplida.", 0.4, {"caras": {"orbi": "guino"}})]),
  ]),
 "super-empanada": dict(
  gancho="Llegó de otro planeta… para salvar tu restaurante", producto="play", selloTraje="capa", frase="Más rápida que un mesero.",
  copy="El origen de la Súper Empanada 🥟🦸‍♀️ ¿Ya sabías que tenía identidad secreta?",
  hashtags="#Superheroes #Empanada #Comedia #Restaurante #HumorColombiano",
  reparto=V,
  planos=[
   dict(fondo="espacio", fondoOp=dict(explota=A(0, 1, 0.55, 1, "in")), cam=[[540, 900, 1.0, 0], [540, 850, 1.1, 0]], grado="epico", musica="misterio", min=5.0,
        actores=[F("pan", 540, 1660, 0.85, cara="triste", fruta="pan", capa="url(#capaRoja)", emblema=dict(letra="E", fondo="#ffd166", color="#c01b2c"))],
        lineas=[("narrador", "En el planeta Horno, a punto de apagarse…", 0.6, {}), ("pan", "Hija mía, en la Tierra serás… crujiente.", 0.4, {})]),
   dict(fondo="espacio", fondoOp=dict(explota=1), dof=6, cam=[[540, 900, 1.1, 0], [540, 900, 1.2, 0]], grado="epico", titulo=["Súper Empanada", "El origen"], trans="flash", min=3.0,
        fx=[dict(tipo="velocidad", p=0, p1=1)], actores=[F("bebe", 200, 1600, 0.35, cara="feliz", fruta="empanada", a=dict(x=900, y=500, s=0.2), curva="lineal")], lineas=[]),
   dict(fondo="restaurante", fondoOp=dict(luz=1), cam=[[540, 1200, 1.1, 0], [540, 1200, 1.15, 0]], grado="calido", musica="romcom", letrero="AÑOS DESPUÉS · LA FONDA",
        actores=[F("empanada", 760, 1520, 0.95, cara="nervioso", fruta="empanada", acc=["gafas"]), dict(id="julian", tipo="julian", x=300, y=1180, s=0.95, props=dict(sudor=True, ojos="grandes"))],
        lineas=[("julian", "¡Treinta mesas esperando! ¿Dónde está la Súper Empanada cuando uno la necesita?", 0.4, {}), ("empanada", "Ni idea… yo solo trabajo aquí.", 0.3, {})]),
   dict(fondo="restaurante", fondoOp=dict(mesas=[[200, 1260, True], [880, 1260, True], [540, 1560, True]], luz=1), cam=[[540, 1100, 1.0, 0], [540, 1080, 1.06, 0]], grado="epico", musica="heroe", trans="flash",
        fx=[dict(tipo="destello", p=0.02, x=540, y=760), dict(tipo="qr", linea=0, linea1=1, de=[540, 760], mesas=[[200, 1260], [880, 1260], [540, 1560]], cocina=[1180, 700])],
        actores=[F("empanada", 540, 900, 0.9, cara="orgullo", flota=14, brazo="arriba", **EMPANADA)],
        lineas=[("empanada", "¡Esto es trabajo para… la Súper Empanada!", 0.3, {}),
                ("empanada", "Cada mesa pide sola desde su celular.", 0.4, {"pedido": "Mesa 9 · Enviado a cocina ✓|Ajiaco · pidió desde el QR"})]),
   dict(fondo="restaurante", fondoOp=dict(luz=1), cam=[[540, 1200, 1.1, 0], [540, 1200, 1.15, 0]], grado="calido", musica="romcom", trans="barrido",
        actores=[F("empanada", 760, 1520, 0.95, cara="guino", fruta="empanada", acc=["gafas"]), dict(id="julian", tipo="julian", x=300, y=1180, s=0.95, props=dict(ojos="grandes"))],
        lineas=[("julian", "¡Lo hizo de nuevo! ¿Y tú dónde estabas?", 0.4, {}), ("empanada", "¿Yo? En el baño. ¿Me perdí de algo?", 0.4, {})]),
  ]),
 "relampago-tinto": dict(
  gancho="El ser más rápido del mundo… ¿o no?", producto="play", selloTraje="capa", frase="Más rápido que el Relámpago: el QR.",
  copy="Treinta mesas en tres segundos ⚡☕ …y todas mal. ¿Te ha pasado con un mesero?",
  hashtags="#Superheroes #Cafe #Mesero #Comedia #HumorColombiano",
  reparto=V,
  planos=[
   dict(fondo="restaurante", fondoOp=dict(mesas=[[200, 1260, True], [880, 1260, True]], luz=1, manos=True), cam=[[540, 1150, 1.05, 0], [540, 1150, 1.1, 0]], grado="epico", musica="accion", mano=6,
        fx=[dict(tipo="velocidad", p=0.1, p1=0.9)],
        actores=[F("tinto", -200, 1500, 0.95, cara="guino", rayos=True, a=dict(x=1300), curva="lineal", **TINTO)],
        lineas=[("narrador", "Él es el ser más rápido del mundo.", 0.4, {}), ("tinto", "¡Treinta mesas en tres segundos!", 0.2, {})]),
   dict(fondo="ciudad", dof=6, cam=[[540, 900, 1.1, 0], [540, 900, 1.2, 0]], grado="epico", titulo=["Relámpago Tinto", "el más rápido… casi"], trans="flash", min=3.0, fx=[dict(tipo="velocidad", p=0, p1=1)], actores=[], lineas=[]),
   dict(fondo="restaurante", fondoOp=dict(mesas=[[200, 1260, True], [880, 1260, True]], luz=1, manos=True), cam=[[540, 1150, 1.15, -4], [540, 1150, 1.25, 4]], grado="calido", musica="comico", mano=10,
        fx=[dict(tipo="pum", linea=1, dt=0.3, texto="¡CRASH!", x=540, y=900)],
        actores=[F("tinto", 540, 1500, 1.1, cara="shock", r=0, a=dict(r=360), de=0.1, hasta=0.6, **TINTO)],
        lineas=[("tinto", "¿Quién pidió la limonada sin hielo? ¿Y el ajiaco sin pollo?", 0.3, {}), ("tinto", "¡Me mareé!", 0.3, {})]),
   dict(fondo="restaurante", fondoOp=dict(mesas=[[200, 1260, True], [880, 1260, True], [540, 1560, True]], luz=1), cam=[[540, 1100, 1.0, 0], [540, 1080, 1.06, 0]], grado="epico", musica="heroe", trans="flash",
        fx=[dict(tipo="qr", linea=0, p1=0.85, de=[540, 720], mesas=[[200, 1260], [880, 1260], [540, 1560]], cocina=[1180, 700])],
        actores=[O(540, 700, 0.75, cara="sarcastico")],
        lineas=[("orbi", "Relájese, Tinto. Cada mesa ya pidió sola desde el QR.", 0.4, {"pedido": "Mesa 4 · Enviado a cocina ✓|Limonada sin hielo · justo como la pidió"})]),
   dict(fondo="restaurante", fondoOp=dict(luz=1), cam=[[540, 1200, 1.1, 0], [540, 1200, 1.15, 0]], grado="calido", musica="romcom",
        actores=[F("tinto", 320, 1520, 1.0, cara="feliz", **TINTO), O(780, 1000, 0.7, cara="guino")],
        lineas=[("tinto", "¿O sea que… me puedo tomar un descanso?", 0.4, {}), ("orbi", "Siéntese, Tinto. Que no se le enfríe.", 0.3, {})]),
  ]),
 "mujer-arepa": dict(
  gancho="Con su lazo de queso, nadie puede mentir", producto="dom", selloTraje="capa", frase="La verdad sabe mejor.",
  copy="El lazo de queso no perdona 🧀✨ ¿Qué le preguntarías tú a la app que te cobra comisión?",
  hashtags="#Superheroes #Arepa #Comedia #Domicilios #Emprendedores",
  reparto=V,
  planos=[
   dict(fondo="callejon", cam=[[540, 1100, 1.0, 0], [540, 1100, 1.1, 0]], grado="noche", musica="accion", mano=8,
        fx=[dict(tipo="lluvia", k=0.5)],
        actores=[dict(id="comi", tipo="comi", x=760, y=1240, s=0.7, cara="diva", a=dict(x=1300), de=0.55, hasta=0.9),
                 F("arepa", 250, 1520, 0.95, cara="enojo", a=dict(x=520), de=0.6, hasta=0.95, **AREPA)],
        lineas=[("comi", "¡Nunca me vas a atrapar, Arepita!", 0.4, {}), ("arepa", "Eso lo veremos.", 0.3, {})]),
   dict(fondo="ciudad", dof=6, cam=[[540, 900, 1.1, 0], [540, 900, 1.2, 0]], grado="epico", titulo=["Mujer Arepa", "y el lazo de la verdad"], trans="flash", min=3.0, actores=[], lineas=[]),
   dict(fondo="callejon", cam=[[600, 1100, 1.1, 0], [600, 1100, 1.18, 0]], grado="noche", musica="tension",
        actores=[F("arepa", 260, 1520, 0.95, cara="orgullo", lazo=[500, -40], **AREPA), dict(id="comi", tipo="comi", x=760, y=1240, s=0.7, cara="shock")],
        lineas=[("arepa", "Con el lazo de queso nadie miente. ¿Cuánto les cobras?", 0.3, {}),
                ("comi", "Veinte… ¡Veintisiete por ciento! ¡Y tarifa por lluvia!", 0.3, {"caras": {"comi": "llanto"}}), ("comi", "¡Y cargo por existir!", 0.2, {})]),
   dict(fondo="callejon", cam=[[600, 1100, 1.2, 3], [600, 1100, 1.3, -3]], grado="noche", musica="comico",
        actores=[F("arepa", 260, 1520, 0.95, cara="enojo", lazo=[500, -40], **AREPA), dict(id="comi", tipo="comi", x=760, y=1240, s=0.7, cara="llanto")],
        lineas=[("arepa", "¿Y quién cocina?", 0.3, {}), ("comi", "¡El restaurante! ¡Yo solo me llevo la plata!", 0.3, {})]),
   dict(fondo="restaurante", fondoOp=dict(luz=1), cam=[[540, 1220, 1.05, 0], [540, 1200, 1.1, 0]], grado="calido", musica="heroe", trans="flash",
        fx=[dict(tipo="confeti", linea=1)],
        actores=[dict(id="rosa", tipo="rosa", x=300, y=1560, s=0.72, props=dict(mostrador=True, billetes=12, cejas="arriba", boca=0.9)),
                 F("arepa", 820, 1540, 0.85, cara="orgullo", **AREPA), O(560, 820, 0.6, cara="feliz")],
        lineas=[("orbi", "Con domicilios propios, la verdad es simple: lo que se vende, se queda.", 0.4, {"pedido": "Domicilio propio · Pedido #77|0 % de comisión · La verdad en su caja"}),
                ("arepa", "Justicia… con queso.", 0.4, {})]),
  ]),
}
