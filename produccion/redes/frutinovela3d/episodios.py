"""Frutinovelas 3D de Orbi: personajes humanoides (cabeza de comida u objeto, cuerpo humano) y guiones por tomas.
Cada toma lleva el prompt de imagen, quiénes salen (para mantenerlos iguales con sus fichas de referencia),
el movimiento de cámara sobre la imagen y las líneas de diálogo.
Reglas: nada de marcas reales, nada de caricaturas raciales ni cuerpos sexualizados (lo que tumbó a las frutinovelas originales)."""

ESTILO = ("3D animated feature film still, stylized realism, expressive cartoon faces, cinematic lighting, shallow depth of field, "
          "rich detailed textures, soft global illumination, vertical 9:16 composition, no text, no logos, no watermark")

# Fichas de personaje: se generan una vez y se usan como referencia en todas las tomas para que no cambien
PERSONAJES = {
 "orbi": ("Orbi, a humanoid waiter whose head is a glossy deep-blue sphere like a small planet, with big expressive white eyes with dark pupils, "
          "soft blue eyebrows and a friendly smile, a thin luminous light-blue ring orbiting diagonally around the head like Saturn's ring, "
          "slim young adult body, crisp white shirt, elegant black vest, small blue bow tie, black trousers, black shoes, hands are smooth glossy blue"),
 "arepa": ("Doña Arepa, a humanoid middle-aged woman whose head is a round golden toasted Colombian arepa with grill marks and slightly charred spots, "
           "expressive cartoon eyes with long lashes and eyebrows, pink hair curlers on top, gold hoop earrings, "
           "wearing a turquoise blouse with a floral kitchen apron, modest and warm, dramatic telenovela expressions"),
 "chorizo": ("Don Chorizo, a humanoid man whose head is a glossy reddish-brown chorizo sausage standing vertically with a small twine knot on top, "
             "thick black mustache, charming flirty eyes and eyebrows, wearing a white guayabera shirt, beige trousers and brown loafers"),
 "comi": ("Comi, a villain diva whose head is a shiny magenta food-delivery backpack box with a cute angry face, long eyelashes and a small golden crown, "
          "wearing an elegant magenta business suit and heels, holding a pink folding fan, arrogant telenovela villain attitude, fully clothed and elegant"),
 "aguacate": ("Aguacate, a humanoid gossip neighbor whose head is a whole green avocado with bumpy dark-green skin and wide curious eyes, "
              "wearing a beige knitted sweater vest over a light shirt, always holding a smartphone"),
}

EPISODIOS = {
 "arepanovela-3d-1": dict(
  gancho="Doña Arepa descubrió la traición 😱", producto="dom", frase="Continuará…",
  copy="¿Perdonamos a Don Chorizo? 🌭💔 Comenta SÍ o NO y tú decides el capítulo 2.",
  hashtags="#Frutinovelas #Arepanovelas #Telenovela #Comedia #HumorColombiano",
  reparto={
   "arepa": dict(nombre="DOÑA AREPA", color="#f0b84a", voz=("es-CO-SalomeNeural", "+6%", "+0Hz")),
   "chorizo": dict(nombre="DON CHORIZO", color="#e0603f", voz=("es-MX-JorgeNeural", "+4%", "-6Hz")),
   "comi": dict(nombre="COMI", color="#ff8fd3", voz=("es-MX-DaliaNeural", "+12%", "+6Hz"), fx="villano"),
   "aguacate": dict(nombre="AGUACATE, EL CHISMOSO", color="#7cc142", voz=("es-VE-SebastianNeural", "+14%", "+8Hz")),
   "orbi": dict(nombre="ORBI", color="#5fc9f1", voz=("es-CO-GonzaloNeural", "+6%", "+0Hz")),
  },
  planos=[
   dict(salen=["arepa"], musica="misterio", cam=[[0.5, 0.45, 1.0], [0.5, 0.42, 1.12]], min=3.0,
        prompt="Doña Arepa cooking at the stove of a small cozy Colombian home kitchen at night, steam rising, warm tungsten light, she smiles humming, medium shot",
        lineas=[("arepa", "Ay, hoy le hice a mi Chorizo su desayuno favorito…", 0.4, {})]),
   dict(salen=["aguacate", "arepa"], musica="tension", cam=[[0.4, 0.4, 1.15], [0.45, 0.4, 1.0]], trans="barrido",
        prompt="Aguacate bursting through the kitchen door breathless and shocked, holding up his smartphone, Doña Arepa turning around surprised holding a wooden spoon, dynamic angle",
        lineas=[("aguacate", "¡Arepa! ¡Vi a tu Chorizo con otra!", 0.2, {}), ("arepa", "¿Con otra? ¿Con quién?", 0.2, {})]),
   dict(salen=["chorizo", "comi"], musica="villano", cam=[[0.5, 0.5, 1.2], [0.5, 0.45, 1.0]], trans="flash", fx=[dict(tipo="pum", p=0.05, texto="¡¿QUÉ?!", x=540, y=700)],
        prompt="Don Chorizo stepping out of a magenta luxury car at night in a colorful Colombian street, Comi the magenta delivery-box diva holding his arm, city lights bokeh, low angle dramatic shot",
        lineas=[("comi", "Conmigo, mi amor. Yo lo llevo a todas partes.", 0.6, {})]),
   dict(salen=["arepa"], musica="tension", cam=[[0.5, 0.35, 1.0], [0.5, 0.33, 1.35]], fx=[dict(tipo="rayo", p=0.2, x=540, y=900)],
        prompt="extreme close-up of Doña Arepa's face in shock, tears welling in her eyes, dramatic red telenovela lighting, rain on the window behind her",
        lineas=[("arepa", "¡Chorizo! ¿Cómo pudiste?", 0.4, {})]),
   dict(salen=["chorizo", "comi", "arepa"], musica="villano", cam=[[0.5, 0.45, 1.0], [0.55, 0.45, 1.1]],
        prompt="living room confrontation: Doña Arepa with hands on hips facing Don Chorizo who looks guilty, Comi smirking and fanning herself behind him, telenovela drama staging, warm lamp light",
        lineas=[("chorizo", "Arepa… ella me lleva a todas partes.", 0.3, {}), ("comi", "Y solo me quedo con el veintisiete por ciento.", 0.2, {}),
                ("arepa", "¿El veintisiete por ciento de qué?", 0.2, {}), ("comi", "De ti, mi reina.", 0.2, {})]),
   dict(salen=["arepa", "aguacate"], musica="comico", cam=[[0.5, 0.5, 1.1], [0.5, 0.55, 1.0]], fx=[dict(tipo="pum", p=0.15, texto="¡PLOP!", x=540, y=900)],
        prompt="Doña Arepa fainting dramatically onto a sofa with the back of her hand on her forehead, Aguacate catching her and fanning her with his phone, comedic telenovela moment",
        lineas=[("arepa", "¡Me desmayo!", 0.3, {})]),
   dict(salen=["orbi", "arepa"], musica="heroe", cam=[[0.5, 0.4, 1.2], [0.5, 0.42, 1.0]], trans="flash", fx=[dict(tipo="destello", p=0.1, x=540, y=600)],
        prompt="Orbi the blue-sphere-headed waiter appearing in the living room in a soft blue glow, kneeling and offering Doña Arepa a handkerchief, kind smile, magical warm atmosphere",
        lineas=[("orbi", "Doña Arepa, levántese. Usted no necesita que la lleven.", 0.4, {}),
                ("orbi", "Con domicilios propios usted se lleva sola. Y sin comisión.", 0.2, {"pedido": "Domicilio propio · Pedido #31|0 % de comisión · Contra entrega"})]),
   dict(salen=["arepa", "chorizo", "comi"], musica="heroe", cam=[[0.5, 0.4, 1.0], [0.5, 0.4, 1.15]],
        prompt="Doña Arepa standing tall and proud with arms crossed, pointing to the door, Don Chorizo looking shocked, Comi furious stomping out the door, triumphant telenovela lighting",
        lineas=[("arepa", "Chorizo… vete con ella.", 0.4, {}), ("comi", "¡Esto no se queda así!", 0.2, {})]),
   dict(salen=["chorizo", "aguacate"], musica="triste", cam=[[0.5, 0.45, 1.25], [0.5, 0.45, 1.05]], trans="negro",
        prompt="Don Chorizo alone outside in the rain at night, soaked, holding a single wilted flower, sad puppy eyes, Aguacate peeking from a window above recording with his phone",
        lineas=[("chorizo", "Arepa… ¿me abre?", 0.5, {}), ("aguacate", "Uy… esto se puso bueno.", 0.4, {})]),
  ]),
}
