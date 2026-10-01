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

## La app del celular (`app_movil/`)
El mismo servidor entrega la app. En el celular se abre la dirección de Axtra y se instala con **Agregar a pantalla de inicio**: queda con su ícono y en pantalla completa.
- **Orbe** con el diseño aprobado: cambia al escuchar, pensar y hablar. Tócalo para hablarle.
- **Voz:** todo lo que responde lo dice en voz alta, con la voz de mayordomo (se puede apagar en *Yo*).
- **Micrófono:** te entiende con Groq Whisper (gratis) y, de respaldo, el reconocedor de Google.
- **Herramientas (+):** Imagen, Documento, Documento importante y Piénsalo bien.
- **Idiomas:** *"¿Cómo se dice hola, cómo estás en ruso?"* → la frase, cómo suena escrito en español (sílaba fuerte en MAYÚSCULAS), voz nativa, versión lenta y **Repetir**: te escucha en ese idioma, compara palabra por palabra, da un puntaje y un consejo. Ruso, inglés, francés, portugués, alemán, italiano, japonés, chino, coreano y árabe. Todo gratis.
- **Progreso por idioma de 0 a 100 %** en *Aprender*: frases dominadas (80 puntos o más) sobre una meta de 500. Nivel aproximado: A1 hasta 50 frases, A2 hasta 150, B1 hasta 300, B2 hasta 500 y C1 desde ahí.
- **Yo:** gasto del mes, topes y qué cerebros están activos.
- **Aprender:** tu Sincronización (con sus cinco partes), los temas del Protocolo de inteligencia avanzada y tus idiomas.
- **Recordatorios:** *"Recuérdame en 20 minutos sacar la ropa"*, *"Despiértame mañana a las 6:30"*, *"¿Qué recordatorios tengo?"*. Llegan como **notificación** al celular aunque la app esté cerrada (actívalas en *Yo*).

## Conexión con el Axtra del PC
El Axtra del PC (`nube.py`) sube cada 10 minutos tus recuerdos, el perfil de tus empresas, el CRM, tareas, Sincronización y Protocolo. Entra con su propio **token de servicio** de Cloudflare: tu cuenta no puede subir datos en su nombre y nadie más tampoco. En la nube esos datos **solo** se le dan a Claude o Grok (de pago); los cerebros gratis nunca los ven. Prueba: `python axtra.py nube`.

## Publicar
Todo lo necesario está en `despliegue/`: el servidor con el túnel seguro de Cloudflare (sin puertos abiertos), actualizaciones automáticas desde GitHub cada 10 minutos y copias de seguridad diarias. Sigue **`despliegue/DESPLIEGUE.md`**.

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
- `voz.py`, `oido.py`: la voz de Axtra (edge-tts) y entender tu voz (Groq Whisper / Google).
- `idiomas.py`: lecciones, pronunciación y progreso.
- `app_movil/`: la app del celular (página instalable, funciona en el A32).
- `contexto.py`: tus datos del PC para los cerebros de pago. `recordatorios.py` y `push.py`: recordatorios y notificaciones.
- `Dockerfile` y `despliegue/`: para publicarlo (guía en `despliegue/DESPLIEGUE.md`).
