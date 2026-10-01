# Axtra en la nube (servidor)

El cerebro que usará la app del celular. Vive en un servidor en internet, detrás de tu inicio de sesión de Google, y decide qué inteligencia artificial responde cada mensaje.

## Qué cerebro responde

| Pedido | Cerebro | Costo |
|---|---|---|
| Charla y preguntas sencillas | Groq rápido (`gpt-oss-20b`) → Cerebras → Gemini → OpenRouter | Gratis |
| Explicar, resumir, planear, comparar | Groq grande (`gpt-oss-120b`) pensando más → Cerebras → Gemini | Gratis |
| Actualidad y tendencias | Búsqueda gratis en internet + Grok (si está activo) o Groq | Gratis sin Grok |
| Imágenes | Gemini; si no hay cuota, un servicio gratis | Gratis |
| Algo personal (clientes, Apex, CRM, agenda, portafolio) | **Solo** Claude o Grok; nunca los gratis | Pago |
| Documentos (se entregan en Word) | Claude | Pago |
| Documentos importantes (propuestas, contratos, "piénsalo bien") | **Equipo:** Claude escribe → Grok revisa → Claude entrega | Pago |
| Análisis de inversión | **Equipo:** dos análisis + en qué coinciden y en qué no | Pago |
| "Piénsalo bien" en general | Claude Opus | Pago |

- Mientras Grok no esté activo, revisa y opina Gemini o Groq; si el tema es privado, Claude Opus.
- Si un cerebro falla o se queda sin cuota, se pausa un rato y responde el siguiente.
- Si todos los gratis fallan, responde Claude Haiku (barato) y la app te avisa. Se apaga con `PAGO_DE_RESPALDO=0`.
- **Topes de gasto:** `TOPE_CLAUDE_USD` y `TOPE_GROK_USD` (US$10 cada uno por defecto). Al llegar, ese cerebro se pausa hasta el mes siguiente.
- Con Claude Opus 5.5 y Sonnet 5.5 está activado el **respaldo de seguridad de Anthropic**: si rechaza algo por sus filtros, la API lo reintenta sola con otro modelo de Claude.

## Activar Grok más adelante
Crea la cuenta en console.x.ai, carga saldo y pon en el `.env` del servidor `XAI_API_KEY=...` y el `GROK_MODELO` y precios que muestre la consola. Reinicia: el enrutador lo usa solo.

## Seguridad
- La página queda detrás de **Cloudflare Access**: solo entra tu cuenta de Google (`AXTRA_CORREO`).
- El servidor además revisa en cada petición la firma de Cloudflare: si alguien llega por otro camino, no entra.
- Sin `CF_ACCESS_EQUIPO`, `CF_ACCESS_AUD` y `AXTRA_CORREO`, el servidor no deja entrar a nadie.

## Probar en tu computador
Desde la carpeta de Axtra:
```
pip install -r servidor/requirements.txt
copy servidor\.env.ejemplo servidor\.env      (y pon tus claves)
set AXTRA_MODO=desarrollo
uvicorn servidor.app:app --reload
```
`AXTRA_MODO=desarrollo` desactiva el inicio de sesión: **úsalo solo en tu PC, nunca en el servidor**.

Pruebas automáticas: `python -m pytest servidor/tests`

## Archivos
- `enrutador.py`: decide qué cerebro responde (la tabla de arriba).
- `proveedores.py`: la conexión con cada cerebro.
- `busqueda.py`: búsqueda gratis en internet (Tavily y DuckDuckGo).
- `creacion.py`: imágenes y documentos Word.
- `seguridad.py`: verificación de tu cuenta.
- `db.py`: conversaciones y gasto del mes (SQLite, en la carpeta `datos`).
- `app.py`: la API que usa la app del celular.
- `Dockerfile`: para publicarlo en el servidor (paso 5).
