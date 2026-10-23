"""Guiones de los videos con minifiguras (modelos propios del cliente, en modelos/). Las voces de aquí son provisionales:
en la versión final hablan con la voz que genere la herramienta de video con IA (Veo 3) o con ElevenLabs.
Toma: imagen, de/a = [cx, cy, alto] del recorte en píxeles de la imagen, temblor (golpe), lineas, musica, fx, trans, final."""

def L(quien, txt, pausa=0.4, **e): return (quien, txt, pausa, e)

VOCES = {
    "ingeniero": dict(voz=("es-MX-JorgeNeural", "+2%", "-2Hz")),
    "socio_bravo": dict(voz=("es-CO-GonzaloNeural", "+10%", "+4Hz")),
    "socio_calmado": dict(voz=("es-VE-SebastianNeural", "-4%", "+0Hz")),
    "hincha": dict(voz=("es-CO-SalomeNeural", "+4%", "+2Hz")),
    "chaleco": dict(voz=("es-ES-AlvaroNeural", "-6%", "-10Hz")),
}

GUIONES = {
 # ─────────── 1 · «El mesero robot» (Apex Play)
 "el-mesero-robot": dict(producto="play", reparto=VOCES, gancho=["Pasó 3 meses construyendo un mesero robot…", "y sus socios tenían otra idea"],
  copy="Tres meses construyendo un mesero robot. Sus socios lo resolvieron en una semana. 🤖",
  hashtags="#Restaurantes #Emprendedores #Tecnologia #Humor #Colombia",
  tomas=[
   dict(imagen="taller.jpg", de=[512, 520, 1024], a=[520, 470, 760], musica="comico", fx=[dict(tipo="pum", p=0.0)],
        lineas=[L("ingeniero", "Tres meses construyendo un mesero robot.", 0.2)]),
   dict(imagen="socios.jpg", de=[800, 560, 820], a=[830, 470, 560], musica="comico", trans="flash",
        lineas=[L("socio_bravo", "¿Tres meses? ¡Y el restaurante lleno!", 0.2)]),
   dict(imagen="ingeniero.jpg", de=[540, 560, 1024], a=[545, 500, 820], musica="comico",
        lineas=[L("ingeniero", "Paciencia. La buena tecnología toma su tiempo.", 0.3)]),
   dict(imagen="taller.jpg", de=[230, 420, 760], a=[250, 430, 620], temblor=16, golpe=0.7, musica="comico", fx=[dict(tipo="vidrios", p=0.25)],
        lineas=[L("ingeniero", "…Casi.", 1.4)], min=3.0),
   dict(imagen="socios.jpg", de=[330, 560, 820], a=[320, 480, 600], musica="esperanza",
        lineas=[L("socio_calmado", "Nosotros pusimos un código en cada mesa. El asistente toma el pedido y lo manda a la caja.", 0.3)]),
   dict(imagen="ingeniero.jpg", de=[545, 440, 620], a=[545, 420, 480], musica="esperanza",
        lineas=[L("ingeniero", "¿Y en cuánto tiempo lo instalaron?", 0.3), L("socio_calmado", "Una semana.", 0.4)]),
   dict(imagen="taller.jpg", de=[520, 520, 1024], a=[520, 500, 900], musica="comico", cola=1.0,
        lineas=[L("ingeniero", "…Apágalo.", 0.9)]),
   dict(imagen="taller.jpg", de=[520, 520, 1024], a=[520, 520, 1000], musica="pelicula", min=6.0, trans="negro",
        final=dict(marca="Apex Play", frase="Un asistente de IA en cada mesa.", detalle="Sin construir robots: un código en cada mesa y listo.<br>Cotización según sus mesas y su carta · Clientes nuevos: 50 %")),
  ]),
}
