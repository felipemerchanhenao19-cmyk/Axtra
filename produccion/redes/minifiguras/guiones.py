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

# ─────────── «El mesero robot», cuadro a cuadro con las imágenes del cliente (cuadros/ = 01…20 en el orden en que llegaron)
CARA_T = [438, 298, 572, 408]; OJOS_T = [440, 318, 570, 350]       # Iván en el taller (imágenes 1024 × 1024)
BOCA_T = dict(quien="ingeniero", sobre="modelos/taller.jpg", media="cuadros/01.jpg", abierta="cuadros/02.jpg", zona=CARA_T)
BOCA_T2 = dict(quien="ingeniero", sobre="cuadros/11.jpg", media="cuadros/12.jpg", abierta="cuadros/13.jpg", zona=CARA_T)
GUIONES["el-mesero-robot-cc"] = dict(producto="play", reparto=VOCES, carpeta="el-mesero-robot/cuadros",
  gancho=["Pasó 3 meses construyendo un mesero robot…", "y sus socios tenían otra idea"],
  paneles={"izq19": ["cuadros/19.jpg", [0, 0, 686, 768]], "der19": ["cuadros/19.jpg", [690, 0, 1376, 768]], "der20": ["cuadros/20.jpg", [690, 0, 1376, 768]]},
  tomas=[
   dict(poses=[[0, "modelos/taller.jpg"], ["f0+0.15", "cuadros/04.jpg"], ["f0+0.55", "cuadros/05.jpg"]], bocas=BOCA_T, ojos=dict(img="cuadros/03.jpg", zona=OJOS_T, sobre="modelos/taller.jpg"),
        de=[505, 520, 900], a=[505, 430, 640], musica="comico", fx=[dict(tipo="pum", p=0.0)], cola=1.2,
        lineas=[L("ingeniero", "Tres meses construyendo un mesero robot.", 0.2)]),
   dict(poses="cc/izq19.jpg", de=[343, 420, 768], a=[330, 400, 600], musica="comico", trans="flash", min=2.6,
        lineas=[L("ingeniero", "Cada tornillo… lo puse yo.", 0.3)]),
   dict(poses=[[0, "cuadros/08.jpg"], [1.0, "cuadros/09.jpg"], [1.5, "cuadros/10.jpg"]], de=[330, 470, 820], a=[360, 500, 700], temblor=18, golpe=1.05,
        musica="comico", fx=[dict(tipo="vidrios", p=0.3)], min=2.6),
   dict(poses="cuadros/11.jpg", bocas=BOCA_T2, ojos=dict(img="cuadros/14.jpg", zona=OJOS_T, sobre="cuadros/11.jpg"), de=[500, 470, 760], a=[505, 420, 560], musica="comico", cola=0.6,
        lineas=[L("ingeniero", "…Casi.", 0.5)]),
   dict(poses=[[0, "cc/der19.jpg"], ["f0+0.2", "cc/der20.jpg"]], de=[300, 420, 768], a=[285, 430, 560], musica="tension", trans="flash", fx=[dict(tipo="pum", p=0.05)],
        lineas=[L("socio_bravo", "¿Tres meses? ¡Un robot que tira la comida!", 0.2)]),
   dict(imagen="socios.jpg", de=[330, 560, 820], a=[320, 480, 600], musica="esperanza",
        lineas=[L("socio_calmado", "Nosotros pusimos un código en cada mesa. El asistente toma el pedido y lo manda a la caja.", 0.3)]),
   dict(poses=[[0, "cuadros/11.jpg"], ["f1+0.3", "cuadros/14.jpg"]], bocas=BOCA_T2, de=[505, 420, 620], a=[505, 400, 480], musica="esperanza", cola=0.8,
        lineas=[L("ingeniero", "¿Y en cuánto tiempo lo instalaron?", 0.3), L("socio_calmado", "Una semana.", 0.5)]),
   dict(poses=[[0, "cuadros/14.jpg"], ["f0+0.4", "cuadros/15.jpg"], ["l1-0.3", "cuadros/16.jpg"]], bocas=dict(quien="ingeniero", sobre="cuadros/16.jpg", media="cuadros/17.jpg", zona=CARA_T), de=[505, 470, 900], a=[505, 440, 700], musica="comico", cola=1.2,
        lineas=[L("ingeniero", "…Apágalo.", 0.4), L("ingeniero", "Pero que quede claro: el mío tiene más estilo.", 0.9)]),
   dict(imagen="cuadros/16.jpg", de=[512, 512, 1024], a=[512, 512, 980], musica="pelicula", min=6.0, trans="negro",
        final=dict(marca="Apex Play", frase="Un asistente de IA en cada mesa.", detalle="Sin construir robots: un código en cada mesa y listo.<br>Cotización según sus mesas y su carta · Clientes nuevos: 50 %")),
  ])
