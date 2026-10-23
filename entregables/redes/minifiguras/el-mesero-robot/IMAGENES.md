# «El mesero robot»: imágenes para animar cuadro a cuadro (stop-motion)

Así se hacen las películas de figuras de juguete (*brickfilms*): fotos seguidas a **12 imágenes por segundo**, cambiando solo lo que se mueve.
Usted me envía las imágenes y yo me encargo de:
- **Labios sincronizados con la voz:** elijo la boca de cada cuadro según el volumen real del audio.
- **Parpadeos, tiempos y movimientos de cámara.**
- **Sonido, subtítulos, gancho y cierre.**

## Regla de oro: que solo cambie lo que se mueve
Si entre una imagen y otra cambia la luz, el fondo, el tamaño o un detalle de la ropa, el video «tiembla».
Por eso cada imagen nueva se pide como **edición de la anterior**, no como imagen nueva desde cero.

**Texto para editar en Gemini** (suba la imagen base y pida el cambio):
> Usa esta misma imagen y cambia SOLO [la boca: ligeramente abierta]. No cambies nada más: misma posición, mismo encuadre, misma luz, mismo fondo, mismos colores. Sin texto ni logos.

**Formato:**
- Vertical 9:16 (ideal 1080 × 1920). Si no se puede, cuadrado, pero todas las de una toma del mismo tamaño.
- Nombre cada archivo como `t1_base.png`, `t1_boca_media.png`, `t1_gafas_2.png`…, o me dice en el chat cuál es cuál.

## Bocas (las necesita cada personaje que habla, en cada toma)
| Archivo | Qué cambia |
|---|---|
| `_base` | boca cerrada, la imagen original |
| `_boca_media` | boca entreabierta |
| `_boca_abierta` | boca bien abierta, como diciendo «a» |
| `_ojos_cerrados` | parpadeo (ojos cerrados, todo lo demás igual) |

## Lista por toma (≈ 36 imágenes)
| Toma | Imagen base | Imágenes que necesito |
|---|---|---|
| 1 · Gancho | Iván de cuerpo entero en el taller (`taller.jpg`) | 3 bocas + parpadeo · **ponerse las gafas:** 3 poses (gafas en la mano → subiendo → puestas) |
| 2 · Socio bravo | el de traje (`socios.jpg`) | 3 bocas (la abierta puede ser gritando) + parpadeo · **señalar:** brazo abajo → brazo señalando |
| 3 · La excusa | Iván de cerca, mano en la barbilla (`ingeniero.jpg`) | 3 bocas + parpadeo · ceja levantada (1) |
| 4 · El robot falla | el brazo robótico del taller | 5 poses: brazo con plato → plato temblando → plato en el aire → plato cayendo → piezas en el suelo · Iván con cara de dolor (1) |
| 5 · La solución | el socio calmado (`socios.jpg`) | 3 bocas + parpadeo · socio bravo ya tranquilo (1) |
| 6 · La pregunta | Iván muy de cerca | gafas puestas → gafas a media nariz → gafas abajo (3) · 3 bocas |
| 7 · Remate | taller completo | Iván mirando al robot (1) · brazo robótico arriba → a medio caer → caído (3) |

**Consejo:** empiece por la **toma 1** (son 7 imágenes). Yo la animo y le muestro cómo queda antes de que haga las demás; así confirmamos que se ve fluido.
