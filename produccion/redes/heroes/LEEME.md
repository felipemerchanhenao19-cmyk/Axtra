# Orbi: universo de héroes, motor de episodios cinematográficos

Parodias del cine de superhéroes (sin nombres ni logos de ninguna editorial): Orbi con capa, con antifaz rojo, con chaleco del «0 %» o con armadura enfrenta a villanos del restaurante (el Cuaderno, la Hora Pico, los Porcentajes y Lady Factura). La publicidad va escondida en el remate: la tarjeta del pedido de Apex Play o de Apex Domicilios.

```bash
python3 hacer.py orbi-nocturno               # un episodio  → entregables/redes/heroes/
python3 hacer.py todos
PRUEBA=planos python3 hacer.py <id>          # un cuadro por plano para revisar el encuadre (rápido)
```

Calidad: 1080 × 1920 a 30 cuadros, fondo con desenfoque y paralaje, corrección de color por plano, franjas de cine, grano, voces con efecto (narrador, villano, radio, susurro), música por escena y efectos de sonido por evento.

## Escribir un episodio (episodios.py)
Un episodio es una lista de **planos**. Cada plano lleva:
- `fondo`: ciudad, azotea, restaurante, callejon, taller o negro, con sus opciones en `fondoOp` (señal en el cielo, mesas, ventana rota…).
- `cam`: `[[x, y, zoom, giro] inicio, fin]` o fotogramas `[[avance, x, y, zoom, giro], …]`. `mano` es el temblor de cámara en mano y `dof` el desenfoque del fondo.
- `grado`: noche, calido, sepia (para recuerdos), radar (visión del héroe), frio o epico.
- `trans`: flash, negro o barrido. Además `titulo=[título, subtítulo]`, `letrero` (texto a máquina), `musica` (misterio, tension, villano, heroe, accion, triste, comico) y `min` (duración mínima).
- `actores`: tipos orbi (traje: capa, sinmiedo, castigador, armadura), cuaderno, horaPico, porcentaje, factura, sofia, comi, rosa, julian y persona. Se mueven con `a`, `de`, `hasta` y `curva`, y aparecen o desaparecen con `aparece` y `desaparece`.
- `fx`: lluvia, rayo, paginas, vidrios, pum (onomatopeya con golpe), radar, onda, qr, disparo, monedas, velocidad, confeti, destello y polvo. El momento se marca con `p` (avance del plano) o con `linea`.
- `lineas`: `(quien, texto, pausa, {caras, props, pedido})`.

Los valores pueden animarse con `A(v0, v1, p0, p1)`.
