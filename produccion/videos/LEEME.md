# Videos cinematográficos de Apex Play y Apex Domicilios

Formato horizontal 1920×1080 a 24 cuadros, con voz de narrador, música propia y el sistema real en pantalla.

```
./hacer.sh play          # → entregables/Apex-Play-cine.mp4 (+ versión liviana -whatsapp)
./hacer.sh domicilios    # → entregables/Apex-Domicilios-cine.mp4
```

| Archivo | Qué hace |
|---|---|
| `guion_cine.py` | Lo que dice el narrador en cada escena. `*palabra*` = con énfasis. |
| `escenas.py` | Lo que se ve: textos en pantalla, ángulos del celular, qué parte de la grabación sale en la pantalla. |
| `linea.py` | Tiempos de cada escena (salen de la duración real de la voz). |
| `voz_cine.py` | Narración. Con `GOOGLE_TTS_API_KEY` usa la voz de Google `es-US-Studio-B` (cambiar con `VOZ_GOOGLE`). |
| `musica.py` | Música sintetizada: colchón grave, latido, subidas, impactos en la revelación y el logo. |
| `render.py` + `escenario.js` | Imagen cuadro a cuadro en Chromium: celular y tablet en 3D, luces, cámara, grano y viñeta. |
| `mezcla.py` | Voz + música (se baja sola cuando habla el narrador) + imagen. |
| `grabaciones/` | Grabaciones reales del demo (celular y caja) y sus marcas de tiempo. |
| `grabar_play.py`, `grabar_dom.py`, `ranura_falsa.py` | Para volver a grabar el demo (servidor apex local + ranura falsa). |

**La clave de Google** va solo en el entorno (configuración de la sesión → secretos), nunca en el código ni en el chat.

Para volver a grabar el demo (solo si cambia la página): levantar `ranura_falsa.py` en el puerto 8090 y el servidor apex en el 8081
con `APEX_MODO=desarrollo`, crear un restaurante sin `"ejemplo"` (los grabadores usan `video` y `videodom`), descargar
`@google/model-viewer` con `npm pack` para el visor 3D y ajustar las rutas del principio de `grabar_*.py`.
