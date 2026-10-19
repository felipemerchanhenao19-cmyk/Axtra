# Frutinovelas 3D de Orbi · Kit de producción

Es el estilo de las frutinovelas que están pegando: personajes en 3D con cabeza de comida u objeto y cuerpo humano, con brazos y piernas. **Orbi también tiene cuerpo:** es un mesero con cabeza de planeta azul.

## Cómo producirlas

**Opción A, automática (la recomendada):** con acceso a la IA de Google, todo sale con un solo comando:
```bash
python3 produccion/redes/frutinovela3d/generar.py todo arepanovela-3d-1
```
Primero genera una ficha por personaje (para que se vean igual en todas las tomas), después una imagen por toma, y al final arma el video con movimiento de cámara, voces, subtítulos, música, efectos y la tarjeta del pedido. Para que funcione, en la configuración del entorno de la nube hay que:
1. Agregar la variable **`GEMINI_API_KEY`** (la clave se saca gratis en Google AI Studio).
2. Permitir el dominio **`generativelanguage.googleapis.com`** en el acceso a red.

**Opción B, manual desde el celular:** pegar los prompts de abajo en un generador de imágenes (la app de Gemini, Meta AI o la que uses). Primero se generan las fichas, y luego cada toma adjuntando las fichas de quienes salen. Las imágenes se guardan en `produccion/redes/frutinovela3d/tomas/` con los nombres `arepanovela-3d-1_00.png`, `_01`… y `fichas/orbi.png`, y con eso yo armo el video (`generar.py video arepanovela-3d-1`).

**Para que se muevan de verdad (opcional):** cada imagen se puede animar con un generador de video (Veo, Kling, Hailuo…) a partir de la imagen. El video que arma el script mueve la cámara sobre cada imagen; si después quieres animación de verdad, se cambian las imágenes por esos clips.

## Reglas para no meternos en problemas
- **Nada de marcas reales** en las imágenes, como la de la hamburguesería de la captura. Pueden bajar el video o traer un reclamo.
- **Nada de caricaturas raciales ni de cuerpos sexualizados.** Por eso criticaron y tumbaron la cuenta original. Nos quedamos con el drama, la traición y los cliffhangers.

## Estilo (va al final de cada prompt)
> 3D animated feature film still, stylized realism, expressive cartoon faces, cinematic lighting, shallow depth of field, rich detailed textures, soft global illumination, vertical 9:16 composition, no text, no logos, no watermark

## Fichas de personaje
Se generan con: *«Character reference sheet, single full-body front view, standing, neutral light-grey studio background. [descripción]. [estilo]»*

| Personaje | Descripción (va en el prompt) |
|---|---|
| **Orbi** | a humanoid waiter whose head is a glossy deep-blue sphere like a small planet, with big expressive white eyes with dark pupils, soft blue eyebrows and a friendly smile, a thin luminous light-blue ring orbiting diagonally around the head like Saturn's ring, slim young adult body, crisp white shirt, elegant black vest, small blue bow tie, black trousers, black shoes, hands are smooth glossy blue |
| **Doña Arepa** | a humanoid middle-aged woman whose head is a round golden toasted Colombian arepa with grill marks and slightly charred spots, expressive cartoon eyes with long lashes and eyebrows, pink hair curlers on top, gold hoop earrings, wearing a turquoise blouse with a floral kitchen apron |
| **Don Chorizo** | a humanoid man whose head is a glossy reddish-brown chorizo sausage standing vertically with a small twine knot on top, thick black mustache, charming flirty eyes, white guayabera shirt, beige trousers, brown loafers |
| **Comi** (villana) | a villain diva whose head is a shiny magenta food-delivery backpack box with a cute angry face, long eyelashes and a small golden crown, elegant magenta business suit and heels, pink folding fan, fully clothed and elegant |
| **Aguacate, el chismoso** | a humanoid gossip neighbor whose head is a whole green avocado with bumpy dark-green skin and wide curious eyes, beige knitted sweater vest over a light shirt, always holding a smartphone |

## Capítulo 1 en 3D: «La traición» (unos 45 s · Apex Domicilios escondido)

| # | Salen | Toma (prompt de la escena) | Diálogo |
|---|---|---|---|
| 0 | Arepa | Doña Arepa cooking at the stove of a small cozy Colombian home kitchen at night, steam rising, warm tungsten light, she smiles humming, medium shot | AREPA: «Ay, hoy le hice a mi Chorizo su desayuno favorito…» |
| 1 | Aguacate, Arepa | Aguacate bursting through the kitchen door breathless and shocked, holding up his smartphone, Doña Arepa turning around surprised holding a wooden spoon, dynamic angle | AGUACATE: «¡Arepa! ¡Vi a tu Chorizo con otra!» / AREPA: «¿Con otra? ¿Con quién?» |
| 2 | Chorizo, Comi | Don Chorizo stepping out of a magenta luxury car at night in a colorful Colombian street, Comi holding his arm, city lights bokeh, low angle dramatic shot | COMI: «Conmigo, mi amor. Yo lo llevo a todas partes.» |
| 3 | Arepa | extreme close-up of Doña Arepa's face in shock, tears welling in her eyes, dramatic red telenovela lighting, rain on the window behind her | AREPA: «¡Chorizo! ¿Cómo pudiste?» |
| 4 | Chorizo, Comi, Arepa | living room confrontation: Doña Arepa with hands on hips facing Don Chorizo who looks guilty, Comi smirking and fanning herself behind him, warm lamp light | CHORIZO: «Arepa… ella me lleva a todas partes.» / COMI: «Y solo me quedo con el 27 %.» / AREPA: «¿El 27 % de qué?» / COMI: «De ti, mi reina.» |
| 5 | Arepa, Aguacate | Doña Arepa fainting dramatically onto a sofa with the back of her hand on her forehead, Aguacate catching her and fanning her with his phone, comedic | AREPA: «¡Me desmayo!» |
| 6 | Orbi, Arepa | Orbi appearing in the living room in a soft blue glow, kneeling and offering Doña Arepa a handkerchief, kind smile, magical warm atmosphere | ORBI: «Doña Arepa, levántese. Usted no necesita que la lleven. Con domicilios propios usted se lleva sola. Y sin comisión.» *(sale la tarjeta: Domicilio propio · 0 % de comisión)* |
| 7 | Arepa, Chorizo, Comi | Doña Arepa standing tall and proud with arms crossed, pointing to the door, Don Chorizo shocked, Comi furious stomping out the door | AREPA: «Chorizo… vete con ella.» / COMI: «¡Esto no se queda así!» |
| 8 | Chorizo, Aguacate | Don Chorizo alone outside in the rain at night, soaked, holding a single wilted flower, sad puppy eyes, Aguacate peeking from a window above recording with his phone | CHORIZO: «Arepa… ¿me abre?» / AGUACATE: «Uy… esto se puso bueno.» → **Continuará…** |

**Texto para publicar:** ¿Perdonamos a Don Chorizo? 🌭💔 Comenta SÍ o NO y tú decides el capítulo 2.
#Frutinovelas #Arepanovelas #Telenovela #Comedia #HumorColombiano
