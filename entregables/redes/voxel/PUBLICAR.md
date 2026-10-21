# «Turno de noche»: serie en 3D de Apex

Miniserie vertical (1080×1920) en 3D real, con personajes de bloques, para Instagram Reels, TikTok y X.
Una fonda de Tuluá vista por dentro: don Jairo (el dueño), Brayan (el mesero) y Marcela (la administradora).

**El tono:** drama serio con humor seco, como «The Office» o los videos de bloques que se vuelven virales.
Nadie hace chistes. La gracia sale de la situación: la hora pico con un solo mesero, la comisión de la app.
Los personajes la viven en serio, y el asistente de Apex (Orbi, con la cara nueva de la app) la resuelve sin hacer ruido.

## Por qué funciona para Apex
- **No es infantil:** son adultos con problemas reales de restaurante. El dueño que lo ve se reconoce.
- **El producto es el desenlace,** no un anuncio pegado al final. Se entiende qué hace Apex sin una sola métrica en pantalla.
- **Es una serie:** la gente vuelve por los personajes. Cada capítulo deja una frase que se comenta: «¿Y el otro?» / «También yo.» o «Repítalo despacio.» / «Ce. Ro.»
- **Lo que hay que cuidar:**
  - Que nunca se burle del cliente ni del mesero.
  - Que los precios del cierre sean siempre los oficiales.

## Capítulos

| Archivo | Producto | Duración | Gancho (primeros 2 s) |
|---|---|---|---|
| `mesa-siete.mp4` | Apex Play | ~1 min | «Viernes · 8:00 p. m.»: salón lleno, lluvia, manos levantadas |
| `la-comision.mp4` | Apex Domicilios | ~50 s | «Lunes · 11:40 p. m.»: oficina, tormenta, Marcela frente al portátil |

Cada capítulo viene en tres versiones:
- **Principal:** con música y subtítulos.
- **`-sin-musica`:** para poner un sonido en tendencia dentro de la app.
- **`-liviano`:** 720p, para WhatsApp.

### Textos para publicar
**Capítulo 1 · Mesa siete**
> Viernes, 8 p. m. Un solo mesero. Veinticinco minutos de espera en la mesa cuatro. Turno de noche, capítulo 1. 🎬
> #Restaurantes #Emprendedores #Tulua #Negocios #TurnoDeNoche

**Capítulo 2 · La comisión**
> Lunes, 11:40 p. m. Marcela tiene que darle una noticia a don Jairo. Turno de noche, capítulo 2. 🎬
> #Restaurantes #Domicilios #Emprendedores #Tulua #TurnoDeNoche

**Comentario fijado (los dos):** «¿Su restaurante también tiene turno de noche? Escríbanos: 310 789 7960»

## Recomendaciones
- Publicar el capítulo 1 un jueves o viernes entre 6 y 8 p. m., que es cuando el dueño vive la hora pico. El capítulo 2, el lunes siguiente.
- En TikTok, usar la versión sin música con un sonido de suspenso en tendencia a volumen bajo; los diálogos tienen que oírse.
- Portada: el primer plano de don Jairo con los ojos cerrados (cap. 1) o Marcela con la luz roja del portátil (cap. 2).
- Responder comentarios en el tono de la serie: serio y breve («Don Jairo dice que gracias»).

## Precios que salen en los cierres
- **Apex Play:** según las mesas y la carta; clientes nuevos con 50 % de descuento.
- **Apex Domicilios** (clientes nuevos, 50 %):
  - Montaje: $ 450.000, o $ 550.000 con el lector de comprobantes de Nequi.
  - Mensualidad: $ 60.000 los primeros 12 meses (normal $ 120.000).

## Cómo se hacen
`produccion/redes/voxel/`:
- **`episodios.py`:** guion, cámaras, gestos y expresiones.
- **`personajes3d.js`:** los personajes y Orbi.
- **`sets3d.js`:** el restaurante y la oficina.
- **`escena3d.js`:** cámara, subtítulos y cortes.

```
python hacer.py <capítulo|todos>            # video final
PRUEBA=planos python hacer.py <capítulo>    # un cuadro por plano para revisar
```
Las bocas se mueven con el volumen real de cada voz. Las voces son de Microsoft (edge-tts) y la música es sintetizada.
