# Orbi en la cocina: plantilla de videos con comida que habla

Orbi conversa con la comida del restaurante (Doña Arepa, Don Chorizo, la Empanada, Don Tinto, Don Pan, la Hamburguesa, la Papa y el Aguacate chismoso). Comi es una app **ficticia**.
La publicidad va escondida: el problema es el chiste, y Apex Play (QR en la mesa) o Apex Domicilios (0 % de comisión) es el remate.

## Hacer un capítulo
```bash
python3 hacer.py arepanovela-1          # un capítulo
python3 hacer.py todos                  # todos los de episodios.py
PRUEBA=1,8,15 python3 hacer.py <id>     # solo cuadros de prueba (rápido) para revisar el encuadre
```
Salen dos archivos en `entregables/redes/cocina/`:
- `<id>.mp4`, con música (para TikTok y X).
- `<id>-sin-musica.mp4`, solo con voces y efectos (para Instagram de empresa, donde se le pone un audio comercial desde la app).

Cada capítulo tarda unos 4 minutos en hacerse. Necesita `edge-tts`, `playwright`, `numpy`, `scipy` y `ffmpeg`.

## Escribir uno nuevo
Copie un capítulo de `episodios.py` y cambie las líneas. Cada línea es `(quien, texto, pausa, eventos)`:

| Evento | Qué hace |
|---|---|
| `caras={"arepa": "llanto"}` | normal, feliz, triste, enojo, shock, llanto, diva, orgullo, nervioso, guino |
| `poses={"arepa": "desmayo"}` | abajo, arriba, cabeza, jarra, dos, saluda, desmayo, brinco |
| `entra=[...]`, `sale=[...]`, `mueve={"x": 600}` | entradas, salidas y movimientos |
| `drama=True` | triple zoom de telenovela con tinte rojo |
| `temblor=True` | sacudida |
| `chip="27 %"` (`chipok=True` = verde) | letrero grande |
| `pedido="Título\|detalle"` | tarjeta de pedido de Apex (aquí entra la publicidad y la música se vuelve alegre) |
| `acc={"papa": ["fantasma"]}` | rulos, bigote, gafas, corbatin, aretes, corona, sombrero, banda, fantasma |

Fondos: `cocina`, `vitrina`, `consultorio`, `estudio` (con `atriles`), `terror` y `pasarela`. Músicas: `novela`, `triste`, `suave`, `debate`, `terror` y `reinado`.

Reglas de la casa: el chiste va primero; el producto aparece una sola vez, en el remate. No se usan cuerpos, colores de piel ni doble sentido sexual, que fue lo que hizo caer a las frutinovelas originales.
