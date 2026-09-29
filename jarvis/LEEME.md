# JARVIS

Asistente de voz personal: se activa diciendo **"Jarvis"** en español y solo obedece **tu voz**. Es analista financiero, asistente de ventas, secretario y compañero de estudio.

## Qué hace
- Palabra de activación "Jarvis" en español. Puedes decir todo seguido: "Jarvis, ¿qué hora es?"
- Verificación de voz: si no eres tú, responde "Acceso denegado"
- Entiende español con Google (gratis, más preciso) y Whisper local de respaldo
- Cerebro híbrido: órdenes directas sin IA, cerebro local gratis en tu PC (Ollama) y Claude solo para lo difícil
- Voz de mayordomo gratis (edge-tts) o voz de ElevenLabs
- Conversación continua: después de responder escucha 10 segundos más sin repetir "Jarvis"
- Interrúmpelo mientras habla: *"Jarvis, para"*, *"detente"* o *"Jarvis, para, mejor dime el clima"* (funciona mejor con audífonos o volumen moderado)
- Para terminar: "eso es todo" o "gracias Jarvis"

## Instalación en tu ASUS Vivobook Go (Windows)

1. Descomprime el zip (clic derecho → "Extraer todo") y entra a la carpeta `jarvis`.
2. Clic derecho en un espacio vacío de la carpeta → **"Abrir en Terminal"**.
3. Escribe y presiona Enter:
   ```
   python instalar.py
   ```
   Tarda 10 a 20 minutos. Al final te dice si todo quedó bien.
4. **Clave de API:** entra a console.anthropic.com, carga unos US$5 y crea una API key. Abre el archivo `.env` con el Bloc de notas y pégala en `ANTHROPIC_API_KEY=`.
5. Registra tu voz:
   ```
   python jarvis.py registrar
   ```
6. Inicia Jarvis:
   ```
   python jarvis.py
   ```
   Di: *"Jarvis, ¿cómo está el clima hoy?"*

La primera vez descarga el modelo Whisper (~500 MB).

## Cerebro híbrido: gastar menos saldo (o nada)
Jarvis tiene tres niveles y elige solo:
1. **Órdenes directas (sin IA, gratis, instantáneas):** hora, fecha, clima de Tuluá, recordatorios y alarmas, tareas, poner o controlar música, "¿qué canción es esta?", abrir sitios y apps, "no me hables por una hora", "¿cuánto he gastado?", empezar una clase de idiomas o un dictado.
2. **Cerebro local (gratis, sin internet):** charla, opiniones, chistes, preguntas generales, el modo compañero, el briefing matutino y **las clases de idiomas**. Corre en tu PC con Ollama.
3. **Claude (gasta saldo):** bolsa y finanzas, búsquedas en internet, noticias, correos y agenda, CRM y propuestas, bocetos, cámara y documentos, memoria de conversaciones.

- Si una pregunta necesita a Claude y no hay saldo o internet, responde el cerebro local y te avisa.
- Para forzar a Claude di *"piénsalo bien"*, *"a fondo"* o *"investiga"*.
- El estudio autónomo y la reflexión nocturna solo funcionan con saldo; sin saldo se pausan solos.

**Instalar el cerebro local (una vez, unos 10 minutos):**
```
winget install -e --id Ollama.Ollama
```
Cierra y abre la terminal, entra a la carpeta jarvis y escribe:
```
python jarvis.py cerebro
```
Descarga el modelo (unos 2 GB) y lo prueba. Ollama queda encendido solo con Windows.

- Con 8 GB de RAM, el modelo `qwen2.5:3b` tarda unos segundos por respuesta. Si es muy lento, pon `JARVIS_MODELO_LOCAL=qwen2.5:1.5b` en `.env` y repite `python jarvis.py cerebro`.
- `JARVIS_CEREBRO=local` en `.env`: nunca gasta saldo (sin finanzas en vivo, búsquedas ni cámara).
- `JARVIS_CEREBRO_IDIOMAS=claude`: clases con Claude (mejor calidad, gasta saldo).
- Cierra programas pesados (Chrome con muchas pestañas) si Jarvis va lento.

## Memoria permanente
Jarvis recuerda lo importante aunque lo apagues. Todo se guarda solo en tu PC, en la carpeta `data`:
- `recuerdos.json`: datos sobre ti. Prueba: *"Jarvis, recuerda que mi negocio se llama Apex Closure"*.
- `historial.json`: la última conversación, para seguir donde quedaron.
- `conversaciones/`: registro diario. Prueba: *"Jarvis, ¿qué hablamos ayer sobre TSMC?"*.
- Para borrar algo: *"Jarvis, olvida lo de ..."*.

## Habilidades
- Recordatorios y alarmas: *"Recuérdame en 20 minutos sacar la ropa"* · *"Despiértame mañana a las 6:30"* (lo dice en voz alta a su hora; Jarvis debe estar encendido)
- Tareas: *"Agrega a mis tareas llamar a los clientes"* · *"¿Qué tengo pendiente?"*
- Abrir cosas: *"Abre YouTube"* · *"Abre WhatsApp"* · *"Abre la calculadora"* · *"Busca en Google recetas de pasta"*

## Modo compañero
Mientras usas el computador, Jarvis te habla por iniciativa propia más o menos cada 45 minutos:
te saluda la primera vez del día, te pregunta cómo va tu día, te recuerda algo de tu agenda o tus
clientes, te comenta algo del mercado o algo que aprendió, o te sugiere una pausa si llevas mucho rato.
- **Le puedes responder sin decir "Jarvis"** durante 15 segundos después de que te habla.
- No habla si estás en videollamada (Zoom, Meet, Teams, Discord), con música puesta, en clase o dictado, ni justo después de que hablaron.
- *"Jarvis, no me hables por una hora"* · *"Háblame más seguido, cada 20 minutos"* · *"Háblame menos"*.
- Ajustes en `.env`: `JARVIS_CONVERSADOR=0` para apagarlo, `JARVIS_CONVERSADOR_MINUTOS=45`, `JARVIS_HORAS_ACTIVAS=08:00-22:30`.
- Privacidad: solo mira el tipo de programa que usas (navegador, Word, código...), nunca el contenido de tu pantalla.
- Costo: menos de medio centavo de dólar por cada vez que te habla.

## Cámara y visión
- *"Jarvis, ¿qué ves?"* · *"¿Qué tengo en la mano?"* · *"¿Cómo me veo?"*: toma una foto y la analiza.
- *"Jarvis, lee este documento"* · *"Explícame este ejercicio"* · *"Resume esta página"*: cuenta 3 segundos, toma la foto y lo lee. Las fotos quedan en `mis_documentos/capturas`.
- **Saludo al llegar:** registra tu cara una vez con `python jarvis.py cara` (20 segundos frente a la cámara). Desde ahí, cuando llegues después de 10 minutos sin verte, te saluda y te dice si tiene avisos.
- Desactiva el saludo con `JARVIS_CAMARA_SALUDO=0`. Con el saludo activo, la luz de la cámara queda encendida mientras Jarvis está prendido.
- Privacidad: nada de video se guarda; solo reconoce TU cara, y todo se procesa en tu PC (menos las fotos que le pides analizar, que van a Claude).

## Música
- *"Jarvis, pon música lo-fi para estudiar"* · *"Pon Bad Bunny"*: busca en YouTube y reproduce en tu navegador.
- *"Pausa la música"* · *"Siguiente"* · *"Sube el volumen"* · *"Baja el volumen"*: usa las teclas multimedia de Windows.
- *"Jarvis, ¿qué canción es esta?"*: escucha 10 segundos y te dice canción, artista, álbum y año (como Shazam). *"¿Qué canciones has reconocido?"* te da el historial.
- Cuando le hablas con música puesta por él, la pausa y la reanuda al terminar.
- Con música alta le cuesta escucharte: habla más fuerte o baja el volumen.

## Idiomas (inglés y más)
- *"Jarvis, quiero practicar inglés"* · *"Clase de inglés para entrevistas de trabajo"* · *"Practiquemos francés, nivel básico"*.
- Te habla con una voz nativa, conversa sobre tus temas (negocios, bolsa, tecnología), te corrige lo importante y siempre te hace preguntas para que hables más que él.
- Guarda tu vocabulario nuevo y tus errores frecuentes, y los repasa en la siguiente clase. Estima tu nivel (A1 a C1).
- Para terminar: *"fin de la clase"* o *"end the lesson"*. Pregunta *"¿Cómo va mi inglés?"* para ver tu progreso.
- Idiomas: inglés, francés, portugués, alemán, italiano, mandarín y japonés.

## Rutinas automáticas
- **Briefing matutino** a las 6:30 (cámbialo con `JARVIS_BRIEFING_HORA`): suena una alarma y te da clima, agenda de las primeras 3 horas, tareas, clientes a contactar, correos y mercado. Si enciendes a Jarvis más tarde (antes del mediodía), te lo da al encender. También puedes pedirlo: *"Jarvis, dame mi briefing"*.
- **Informe del mercado** de lunes a viernes a las 4:15 p. m. (`JARVIS_INFORME_MERCADO_HORA`): te lo resume en voz y lo guarda en `mis_documentos`.

## Negocio
- **CRM:** *"Agrega a Don Pepe de la salchipapería Mr Papa, teléfono 300..."* · *"Pasa a Mr Papa a propuesta, lo llamo el viernes"* · *"¿A quién debo llamar hoy?"* · *"¿Cómo va mi embudo de ventas?"*
- **Prospectos:** *"Busca restaurantes en Tuluá sin página web"* (categorías: restaurantes, tiendas, salud, belleza, servicios, hoteles, gimnasios). Usa OpenStreetMap, que no tiene todos los negocios, así que complementa con Google Maps.
- **Bocetos web:** *"Haz un boceto para la Panadería La Espiga, colores cálidos"*. Lo diseña en 1-2 minutos, lo abre en el navegador y lo guarda en `mis_documentos/bocetos`. El formulario valida los datos pero no envía nada hasta que el cliente pague.
- **Propuestas:** *"Redacta una propuesta para Mr Papa: página web a 300 mil, entrega en 5 días"*. Te abre un Word listo.

## Universidad: modo dictado
*"Jarvis, quiero dictar mi ensayo de comercio internacional"*. Hablas con calma y dices *"nuevo párrafo"* para separar, *"borra lo último"* para corregir y *"fin del dictado"* para terminar. Jarvis corrige ortografía y puntuación y organiza el texto, **sin cambiar tus ideas ni agregar contenido**. Te abre el Word y guarda aparte el dictado original.

## Google Calendar y Gmail (una sola vez, unos 10 minutos)
1. Entra a **console.cloud.google.com** con tu cuenta de Gmail y crea un proyecto llamado "Jarvis".
2. En "APIs y servicios" → **Biblioteca**, activa **Google Calendar API** y **Gmail API**.
3. En **Pantalla de consentimiento OAuth**: tipo "Externo", nombre "Jarvis", tu correo. En **Usuarios de prueba**, agrega tu propio Gmail.
4. En **Credenciales** → Crear credenciales → **ID de cliente de OAuth** → tipo **App de escritorio**. Descarga el JSON.
5. Cambia el nombre del archivo a `credentials.json` y ponlo en la carpeta `jarvis`.
6. En la terminal: `python jarvis.py google`. Se abre el navegador; elige tu cuenta y acepta. Si sale "Google no verificó esta app", toca "Continuar", porque la app es tuya.
7. Listo: *"¿Qué tengo hoy en el calendario?"* · *"¿Tengo correos importantes?"* · *"Agenda reunión con Mr Papa el viernes a las 10"* · *"Redacta un correo para ... "* (queda en borradores, nunca se envía solo).

## Analista financiero
- *"Jarvis, ¿cómo va Nvidia hoy?"* · *"Hazme un análisis técnico de TSMC"*
- *"Registra que compré 2 acciones de Apple a 230"* · *"¿Cómo va mi portafolio?"*
- *"Agrega AMD a mi lista de seguimiento"* · *"Avísame si el S&P 500 baja de 6000"*
- *"Hazme un análisis fundamental de Apple"* (datos oficiales de la SEC; para mejores resultados pon tu correo en `JARVIS_CONTACTO_SEC`)
- *"Muéstrame la gráfica de Nvidia a 6 meses comparada con AMD"*: se abre en pantalla.
- **Simulador con dinero ficticio:** *"Reinicia el simulador con 10 mil dólares"* · *"En el simulador compra 10 acciones de Microsoft"* · *"¿Cómo va mi simulador contra el S&P 500?"*
- Con tu dinero real, Jarvis analiza y opina pero **nunca compra ni vende**: la decisión siempre es tuya.

## Aprendizaje autónomo
Mientras Jarvis está encendido, trabaja solo:
- **Estudia** cada 3 horas (máx. 6 veces al día) un tema tuyo o una acción de tu lista, y guarda la nota en `data/conocimiento/`. Cada estudio deja preguntas nuevas que se convierten en el siguiente tema.
- **Reflexiona** cada noche (después de las 9 p. m.) sobre lo que hablaron y guarda lecciones para responderte mejor (`data/habilidades.json`).
- **Vigila** tus alertas de precio cada 15 minutos y te avisa la próxima vez que le hables.
- Pídele: *"Jarvis, estudia a fondo las opciones financieras"* o *"¿Qué aprendiste hoy?"*.
- Por defecto estudia hasta 3 veces al día (cada 4 horas). Cada estudio cuesta unos 5 a 10 centavos de dólar. Ajusta `JARVIS_ESTUDIOS_POR_DIA` o apágalo con `JARVIS_AUTONOMIA=0`.

## Gastos
- Pregúntale: *"Jarvis, ¿cuánto has gastado hoy?"* y te dice el gasto estimado y cuántos días te dura el saldo.
- El registro está en `data/gastos.json`. El saldo exacto siempre está en console.anthropic.com.
- Recomendado: en console.anthropic.com pon un límite de gasto mensual.

## Dónde quedan tus archivos
Todo lo que crea Jarvis (propuestas, bocetos, dictados, gráficas, informes) está en la carpeta `mis_documentos`.

## Estilo de voz (gratis)
En el `.env`: `JARVIS_VOZ_ESTILO=mayordomo` (voz grave, mayor y pausada, estilo Alfred), `colombiano` o `mexicano`.
Si tienes una línea `JARVIS_VOICE=...`, bórrala para que el estilo funcione.

## Voz clonada o diseñada (ElevenLabs)
Solo con la voz de alguien que **te dé permiso**.
1. Graba a esa persona 1 a 3 minutos (celular, cuarto silencioso, sin música, hablando natural).
2. En elevenlabs.io: Voices → Add a new voice → Instant Voice Clone → sube el audio y confirma que tienes permiso.
3. Copia el **Voice ID** de la voz y tu **API key** (Developers → API Keys).
4. En el `.env` agrega:
   ```
   JARVIS_TTS_PROVIDER=elevenlabs
   ELEVENLABS_API_KEY=tu_clave
   ELEVENLABS_VOICE_ID=el_id_de_la_voz
   ```
5. Reinicia Jarvis. Si algo falla, vuelve a la voz gratis sola.

## Ajustes (archivo `.env`)
| Ajuste | Para qué |
|---|---|
| `JARVIS_VOICE_THRESHOLD` | Qué tan estricto es con tu voz. Si otra persona pasa, súbelo (0.80). Si a ti te rechaza, bájalo (0.70) |
| `JARVIS_WAKE_MODE` | `es` = decir "Jarvis" en español (por defecto); `en` = decir "Hey Jarvis" en inglés |
| `JARVIS_PAUSA_FINAL` | Segundos de silencio para saber que terminaste (1.6). Si te corta, súbelo a 2.2 |
| `JARVIS_RECONOCIMIENTO` | `google` (mejor, gratis, en la nube) o `whisper` (local, privado) |
| `JARVIS_INTERRUMPIR` | `1` para poder interrumpirlo, `0` para desactivar |
| `JARVIS_WHISPER_MODEL` | `small` entiende mejor; `base` es más rápido si tu PC va lento |
| `JARVIS_VOICE` | Voz de Jarvis: `es-CO-GonzaloNeural`, `es-MX-JorgeNeural`, `es-ES-AlvaroNeural` |

## Problemas comunes
- **Error con la búsqueda web:** en console.anthropic.com revisa que la búsqueda web (web search) esté habilitada para tu organización.
- **No escucha:** revisa en Windows que el micrófono predeterminado sea el correcto.
- **Responde lento:** usa `JARVIS_WHISPER_MODEL=base`.

## Seguridad
- La verificación por voz es para comodidad, **no es seguridad fuerte**: una grabación de tu voz podría engañarla. Para apagar alarmas y cambiar configuraciones usaremos tu **huella** (fase 4).
- Nunca compartas tu archivo `.env`: ahí está tu clave de pago.

## Costo aproximado
Uso personal: unos US$5 a 20 al mes en Claude (modelo Haiku). La voz, el oído y el clima son gratis.

## Si el PC queda encendido 24/7
En la app **MyASUS**, activa el modo de carga "Balanceado" o "Vida útil máxima" para que la batería no se dañe al estar siempre conectada.

## Siguientes fases
2. Despertador + informe matutino (clima + tareas de las 3 primeras horas con Google Calendar/Tasks)
3. Cámara con giro + saludo por reconocimiento facial
4. Modo vigilancia + alarma + apagado solo con tu huella (Samsung A32)
5. Orbe animado en pantalla
