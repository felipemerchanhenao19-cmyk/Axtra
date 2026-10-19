"""Guiones de «Orbi en la cocina»: Orbi conversa con la comida del restaurante. Comi es una app FICTICIA (no es ninguna marca real).
Cada línea: (quien, texto, pausa antes, eventos). Los eventos cambian el estado desde esa línea en adelante:
  caras {quien: cara} · poses {quien: abajo|arriba|cabeza|jarra|dos|saluda|desmayo|brinco} · entra [..] · sale [..]
  drama (zoom triple y tinte rojo) · temblor · chip "texto" (verde si chipok) · pedido "título|detalle" · acc {quien: [..]}
Caras: normal feliz triste enojo shock llanto diva orgullo nervioso guino. Expresiones de Orbi: normal feliz sarcastico sorprendido triste enojado guino orgulloso."""

ORBI = dict(tipo="orbi", nombre="ORBI", voz=("es-CO-GonzaloNeural", "+8%", "+2Hz"))
COMI = dict(tipo="comi", nombre="COMI · LA APP DE SIEMPRE", voz=("es-MX-DaliaNeural", "+12%", "+6Hz"))
AREPA = dict(tipo="arepa", nombre="DOÑA AREPA", voz=("es-CO-SalomeNeural", "+6%", "+0Hz"), acc=["rulos", "aretes"])
CHORIZO = dict(tipo="chorizo", nombre="DON CHORIZO", voz=("es-MX-JorgeNeural", "+4%", "-6Hz"), acc=["bigote"])
AGUACATE = dict(tipo="aguacate", nombre="AGUACATE, EL CHISMOSO", voz=("es-VE-SebastianNeural", "+14%", "+8Hz"))
EMPANADA = dict(tipo="empanada", nombre="LA EMPANADA", voz=("es-PE-CamilaNeural", "+8%", "+10Hz"))
TINTO = dict(tipo="tinto", nombre="DON TINTO", voz=("es-CO-GonzaloNeural", "-6%", "-14Hz"), acc=["gafas"])
PAN = dict(tipo="pan", nombre="DON PAN", voz=("es-ES-AlvaroNeural", "+4%", "-4Hz"), acc=["corbatin"])
HAMBURGUESA = dict(tipo="hamburguesa", nombre="LA HAMBURGUESA", voz=("es-DO-RamonaNeural", "+8%", "+2Hz"))
PAPA = dict(tipo="papa", nombre="LA PAPA", voz=("es-AR-TomasNeural", "+6%", "+4Hz"))

def con(base, **k): d = dict(base); d.update(k); return d

EPISODIOS = {
 "arepanovela-1": dict(
  serie="LAS AREPANOVELAS · CAP. 1", gancho="Cuando Doña Arepa descubre la traición", producto="dom", fondo="cocina", musica="novela", continuara=True,
  copy="¿Perdonamos a Don Chorizo? 🌭💔 Comenta SÍ o NO y tú decides el capítulo 2.",
  hashtags="#Arepanovelas #Frutinovelas #Telenovela #Comedia #ApexDomicilios",
  reparto={"arepa": con(AREPA, x=230), "aguacate": con(AGUACATE, x=760), "chorizo": con(CHORIZO, x=1250), "comi": con(COMI, x=1250), "orbi": con(ORBI, x=560)},
  inicio=["arepa", "aguacate"],
  lineas=[
   ("aguacate", "¡Arepa! ¡Arepa! ¡Vi a tu Chorizo con otra!", 0.25, dict(caras={"aguacate": "shock", "arepa": "normal"}, poses={"aguacate": "dos"})),
   ("arepa", "¿Con otra? ¿Con quién?", 0.2, dict(caras={"arepa": "shock", "aguacate": "nervioso"}, poses={"aguacate": "abajo", "arepa": "cabeza"})),
   ("comi", "Conmigo, mi amor.", 0.5, dict(entra=["chorizo", "comi"], mueve={"chorizo": 680, "comi": 900, "aguacate": 450}, drama=True, caras={"comi": "diva", "chorizo": "nervioso"})),
   ("chorizo", "Arepa… ella me lleva a todas partes.", 0.3, dict(caras={"arepa": "llanto"}, poses={"arepa": "abajo"})),
   ("comi", "Y solo me quedo con el veintisiete por ciento.", 0.2, dict(chip="27 %")),
   ("arepa", "¿El veintisiete por ciento de qué?", 0.2, dict(caras={"arepa": "enojo"}, poses={"arepa": "jarra"})),
   ("comi", "De ti, mi reina.", 0.25, dict(drama=True, caras={"comi": "diva"})),
   ("arepa", "¡Me desmayo!", 0.2, dict(caras={"arepa": "llanto"}, poses={"arepa": "desmayo"})),
   ("orbi", "Doña Arepa, levántese. Usted no necesita que la lleven.", 0.5, dict(entra=["orbi"], caras={"orbi": "orgulloso", "comi": "shock"})),
   ("orbi", "Con domicilios propios usted se lleva sola. Y sin comisión.", 0.2, dict(poses={"arepa": "abajo"}, caras={"arepa": "shock"}, pedido="Domicilio propio · Pedido #31|0 % de comisión · Contra entrega", chip="0 %", chipok=True)),
   ("arepa", "Chorizo… vete con ella.", 0.4, dict(caras={"arepa": "diva", "chorizo": "shock"}, poses={"arepa": "jarra"})),
   ("comi", "¡Esto no se queda así!", 0.2, dict(caras={"comi": "enojo"}, sale=["comi"])),
   ("chorizo", "¿Y yo qué? ¿Me espera?", 0.3, dict(caras={"chorizo": "triste"})),
   ("aguacate", "Uy… esto se puso bueno.", 0.3, dict(caras={"aguacate": "guino", "arepa": "orgullo"})),
  ]),
 "empanada-olvidada": dict(
  serie="ORBI EN LA COCINA", gancho="Tres horas en la vitrina y nadie la pide", producto="play", fondo="vitrina", musica="triste",
  copy="Las empanadas también tienen sentimientos 🥟 ¿A cuál le darías el sí?",
  hashtags="#Empanada #Comedia #Restaurante #HumorColombiano #ApexPlay",
  reparto={"empanada": con(EMPANADA, x=360), "tinto": con(TINTO, x=760), "orbi": con(ORBI, x=560)},
  inicio=["empanada", "tinto"],
  lineas=[
   ("empanada", "Tres horas en esta vitrina. Nadie me ve.", 0.3, dict(caras={"empanada": "triste", "tinto": "normal"})),
   ("tinto", "Tranquila, mija. A mí me sirvieron hace una hora y nadie me ha tomado.", 0.25, dict(caras={"tinto": "triste"})),
   ("empanada", "Es que el mesero nunca pasa por aquí.", 0.2, dict(caras={"empanada": "llanto"})),
   ("tinto", "El mesero anda con cinco platos y cero ganas.", 0.2, dict(caras={"tinto": "orgullo", "empanada": "triste"})),
   ("orbi", "¿Alguien dijo que no la ven?", 0.5, dict(entra=["orbi"], caras={"orbi": "guino", "empanada": "shock", "tinto": "shock"})),
   ("orbi", "La puse de primera en la carta del QR. Con foto y todo.", 0.2, dict(pedido="Carta QR · ⭐ Recomendado|Empanada de la casa · $ 4.500", caras={"orbi": "orgulloso"})),
   ("empanada", "¿Con foto? ¡No me arreglé!", 0.2, dict(caras={"empanada": "nervioso"}, poses={"empanada": "cabeza"})),
   ("orbi", "Mesa cuatro. Tres empanadas. Enviado a cocina.", 0.3, dict(pedido="Mesa 4 · Enviado a cocina ✓|3 empanadas · pidió desde el QR", chip="10 SEGUNDOS", chipok=True, caras={"orbi": "feliz"})),
   ("empanada", "¡Me pidieron! ¡Me pidieron!", 0.2, dict(caras={"empanada": "feliz"}, poses={"empanada": "brinco"})),
   ("tinto", "¿Y a mí quién me pide?", 0.3, dict(caras={"tinto": "triste"})),
   ("orbi", "Usted ya está frío, don Tinto.", 0.25, dict(caras={"orbi": "sarcastico"}, poses={"empanada": "abajo"})),
   ("tinto", "Siempre lo mismo.", 0.2, dict(caras={"tinto": "llanto"})),
  ]),
 "tinto-terapia": dict(
  serie="ORBI EN LA COCINA", gancho="El tinto fue a terapia y no lo vas a creer", producto="play", fondo="consultorio", musica="suave",
  copy="Don Tinto merece ser feliz ☕ Etiqueta a quien siempre deja enfriar el café.",
  hashtags="#Tinto #Cafe #Terapia #Comedia #ApexPlay",
  reparto={"tinto": con(TINTO, x=380), "orbi": con(ORBI, x=800, y=880)},
  inicio=["tinto", "orbi"],
  lineas=[
   ("orbi", "Cuénteme, don Tinto. ¿Qué lo trae por aquí?", 0.3, dict(caras={"orbi": "normal", "tinto": "triste"})),
   ("tinto", "Doctor, todos los días me pasa lo mismo.", 0.25, dict()),
   ("tinto", "Me sirven calientico… y el cliente se queda esperando el azúcar.", 0.2, dict(poses={"tinto": "dos"})),
   ("orbi", "¿Cuánto tiempo?", 0.2, dict(caras={"orbi": "sorprendido"}, poses={"tinto": "abajo"})),
   ("tinto", "Veinte minutos. ¡Me enfrié, doctor! ¡Me enfrié!", 0.2, dict(caras={"tinto": "llanto"}, drama=True, poses={"tinto": "cabeza"})),
   ("orbi", "Eso tiene nombre.", 0.3, dict(caras={"orbi": "sarcastico"}, poses={"tinto": "abajo"})),
   ("tinto", "¿Qué tengo?", 0.15, dict(caras={"tinto": "shock"})),
   ("orbi", "Síndrome del mesero que nunca voltea a mirar.", 0.3, dict(chip="DIAGNÓSTICO", caras={"orbi": "orgulloso"})),
   ("orbi", "Tratamiento: el cliente pide el azúcar desde el QR. Le llega en un minuto.", 0.3, dict(pedido="Mesa 2 · Enviado ✓|Azúcar y servilletas · desde el QR", caras={"orbi": "feliz"})),
   ("tinto", "¿O sea que me toman calientico?", 0.25, dict(caras={"tinto": "feliz"}, poses={"tinto": "dos"})),
   ("orbi", "Calientico. Son ochenta mil la consulta.", 0.3, dict(caras={"orbi": "guino"}, poses={"tinto": "abajo"})),
   ("tinto", "¡Ahora sí me enfrié!", 0.15, dict(caras={"tinto": "shock"}, temblor=True, poses={"tinto": "cabeza"})),
  ]),
 "debate-arepa-pan": dict(
  serie="EL GRAN DEBATE", gancho="El debate que divide a Colombia", producto="play", fondo="estudio", musica="debate", atriles=[290, 790],
  copy="Defiende tu postura en los comentarios 😤 ¿La arepa es pan?",
  hashtags="#Debate #Arepa #Colombia #Comedia #ApexPlay",
  reparto={"arepa": con(AREPA, x=290), "pan": con(PAN, x=790), "orbi": con(ORBI, x=540, y=840)},
  inicio=["arepa", "pan", "orbi"],
  lineas=[
   ("orbi", "Buenas noches. Hoy, el debate que divide al país.", 0.3, dict(caras={"orbi": "normal", "arepa": "orgullo", "pan": "orgullo"})),
   ("orbi", "¿La arepa… es pan?", 0.3, dict(drama=True, caras={"orbi": "sorprendido"})),
   ("pan", "Obviamente. Es masa, se calienta y se come con mantequilla. Es pan.", 0.3, dict(caras={"pan": "diva", "arepa": "enojo"}, poses={"pan": "arriba"})),
   ("arepa", "¡Respete! Yo soy de maíz. Usted es de trigo, señor.", 0.2, dict(caras={"arepa": "enojo"}, poses={"arepa": "jarra", "pan": "abajo"})),
   ("pan", "Detalles técnicos.", 0.2, dict(caras={"pan": "orgullo"})),
   ("arepa", "¿Detalles? A mí me hacen en la casa. A usted lo venden en bolsa.", 0.2, dict(temblor=True, chip="¡UY!", caras={"arepa": "diva"})),
   ("pan", "¡Eso fue personal!", 0.2, dict(caras={"pan": "shock"}, poses={"pan": "cabeza"})),
   ("orbi", "Mientras ustedes debatían, la mesa cinco pidió las dos cosas por el QR.", 0.4, dict(pedido="Mesa 5 · Enviado ✓|Arepa con queso + pan · desde el QR", caras={"orbi": "guino"})),
   ("arepa", "¿Las dos?", 0.2, dict(caras={"arepa": "shock", "pan": "shock"}, poses={"arepa": "abajo", "pan": "abajo"})),
   ("pan", "Entonces… ¿empate?", 0.2, dict(caras={"pan": "nervioso"})),
   ("orbi", "No. Gana el que tiene hambre. Comente quién tiene la razón.", 0.3, dict(caras={"orbi": "feliz", "arepa": "orgullo", "pan": "orgullo"}, chip="¿AREPA O PAN?", chipok=True)),
  ]),
 "fantasma-comision": dict(
  serie="ESPECIAL DE HALLOWEEN", gancho="El disfraz más aterrador para un restaurante", producto="dom", fondo="terror", musica="terror",
  copy="Cuéntale esta historia a un dueño de restaurante y mira su cara 👻🎃",
  hashtags="#Halloween #Terror #Comedia #Restaurante #ApexDomicilios",
  reparto={"hamburguesa": con(HAMBURGUESA, x=300), "empanada": con(EMPANADA, x=780), "papa": con(PAPA, x=1300, acc=["fantasma"]), "orbi": con(ORBI, x=330, y=800)},
  inicio=["hamburguesa", "empanada"],
  lineas=[
   ("hamburguesa", "¿Escucharon eso?", 0.4, dict(caras={"hamburguesa": "nervioso", "empanada": "nervioso"})),
   ("empanada", "Dicen que en esta cocina espantan…", 0.3, dict(caras={"empanada": "shock"})),
   ("papa", "Uuuuuh… soy el fantasma de la comisión.", 0.5, dict(entra=["papa"], mueve={"papa": 540, "hamburguesa": 220, "empanada": 860}, drama=True, chip="27 %", caras={"hamburguesa": "shock", "empanada": "shock"}, poses={"hamburguesa": "cabeza", "empanada": "cabeza"})),
   ("hamburguesa", "¡No! ¡El veintisiete por ciento no!", 0.2, dict(temblor=True, caras={"hamburguesa": "llanto"})),
   ("papa", "Me llevo una de cada cuatro ventas. Uuuuuh.", 0.2, dict(poses={"papa": "dos"})),
   ("empanada", "¡Mamá!", 0.15, dict(caras={"empanada": "llanto"}, poses={"empanada": "brinco"})),
   ("orbi", "Tranquilos. Es la Papa disfrazada.", 0.5, dict(entra=["orbi"], caras={"orbi": "sarcastico"}, acc={"papa": []}, poses={"papa": "abajo", "empanada": "abajo", "hamburguesa": "abajo"})),
   ("papa", "¡Feliz Halloween!", 0.2, dict(caras={"papa": "feliz", "hamburguesa": "enojo", "empanada": "shock"}, poses={"papa": "dos"})),
   ("hamburguesa", "¡Casi me da algo, Papa!", 0.2, dict(caras={"hamburguesa": "enojo"}, poses={"hamburguesa": "jarra"})),
   ("orbi", "Lo único que asusta de verdad es pagar comisión. Por eso aquí los domicilios son propios.", 0.3, dict(caras={"orbi": "orgulloso"}, pedido="Domicilio propio · Pedido #13|0 % de comisión · Llega en 25 min", chip="0 %", chipok=True, poses={"papa": "abajo"})),
   ("empanada", "¿Y ahora qué va a hacer con el disfraz?", 0.3, dict(caras={"empanada": "normal", "hamburguesa": "normal"}, poses={"hamburguesa": "abajo"})),
   ("papa", "Me voy a asustar a la competencia.", 0.2, dict(caras={"papa": "guino"}, acc={"papa": ["fantasma"]})),
  ]),
 "senorita-cocina": dict(
  serie="SEÑORITA COCINA 2026", gancho="El reinado más sabroso de Colombia", producto="play", fondo="pasarela", musica="reinado",
  copy="¿Quién merecía la corona? 👑 Vota con 🫓 🥟 o 🍔",
  hashtags="#Reinado #MissColombia #Comedia #Comida #ApexPlay",
  reparto={"arepa": con(AREPA, x=230, acc=["rulos", "aretes", "banda"], banda="ANTIOQUIA"), "empanada": con(EMPANADA, x=540, acc=["banda"], banda="VALLE"),
           "hamburguesa": con(HAMBURGUESA, x=850, acc=["banda"], banda="BOGOTÁ"), "orbi": con(ORBI, x=540, y=830)},
  inicio=["arepa", "empanada", "hamburguesa", "orbi"],
  lineas=[
   ("orbi", "¡Bienvenidos a Señorita Cocina dos mil veintiséis!", 0.3, dict(caras={"orbi": "feliz", "arepa": "diva", "empanada": "feliz", "hamburguesa": "diva"}, poses={"arepa": "saluda", "empanada": "saluda", "hamburguesa": "saluda"})),
   ("orbi", "Señorita Arepa. ¿Qué haría usted por la paz mundial?", 0.3, dict(caras={"orbi": "normal"}, poses={"arepa": "abajo", "empanada": "abajo", "hamburguesa": "abajo"})),
   ("arepa", "Acompañaría todos los desayunos del país. Con quesito.", 0.2, dict(caras={"arepa": "diva"}, poses={"arepa": "jarra"})),
   ("orbi", "Hermoso. Señorita Empanada, su turno.", 0.2, dict(poses={"arepa": "abajo"})),
   ("empanada", "Eh… yo… ¿puedo ir con ají?", 0.2, dict(caras={"empanada": "nervioso"})),
   ("orbi", "Señorita Hamburguesa. ¿Cuál es su mayor talento?", 0.3, dict(caras={"empanada": "triste"})),
   ("hamburguesa", "Llegar caliente a la mesa en diez minutos.", 0.2, dict(caras={"hamburguesa": "orgullo"}, poses={"hamburguesa": "arriba"})),
   ("arepa", "¿Diez minutos? ¡Eso es trampa!", 0.2, dict(caras={"arepa": "shock", "empanada": "shock"}, poses={"hamburguesa": "abajo"})),
   ("hamburguesa", "No es trampa, mi amor. Me pidieron por el QR.", 0.2, dict(caras={"hamburguesa": "diva", "arepa": "enojo"}, pedido="Mesa 7 · Enviado a cocina ✓|Hamburguesa de la casa · desde el QR")),
   ("orbi", "Y la nueva Señorita Cocina es…", 0.3, dict(drama=True, caras={"orbi": "sorprendido", "arepa": "nervioso", "empanada": "nervioso", "hamburguesa": "nervioso"})),
   ("orbi", "¡Usted decide en los comentarios!", 0.6, dict(caras={"orbi": "guino"}, chip="VOTE AQUÍ ⬇", chipok=True)),
   ("empanada", "Yo voto por mí.", 0.3, dict(caras={"empanada": "guino", "arepa": "shock", "hamburguesa": "shock"})),
  ]),
}
