# AXTRA

Asistente de voz personal: se activa diciendo **"Axtra"** en español y solo obedece **tu voz**. Es analista financiero, asistente de ventas, secretario y compañero de estudio.

## Qué hace
- Palabra de activación "Axtra" en español. Puedes decir todo seguido: "Axtra, ¿qué hora es?"
- Verificación de voz: si no eres tú, responde "Acceso denegado"
- Entiende español con Google (gratis, más preciso) y Whisper local de respaldo
- Cerebro híbrido: órdenes directas sin IA, cerebro local gratis en tu PC (Ollama) y Claude solo para lo difícil
- Voz de mayordomo gratis (edge-tts) o voz de ElevenLabs
- Conversación continua: después de responder escucha 10 segundos más sin repetir "Axtra"
- Interrúmpelo mientras habla: *"Axtra, para"*, *"detente"* o *"Axtra, para, mejor dime el clima"* (funciona mejor con audífonos o volumen moderado)
- Para terminar: "eso es todo" o "gracias Axtra"

## Instalación en tu ASUS Vivobook Go (Windows)

1. Descomprime el zip (clic derecho → "Extraer todo") y entra a la carpeta `axtra`.
2. Clic derecho en un espacio vacío de la carpeta → **"Abrir en Terminal"**.
3. Escribe y presiona Enter:
   ```
   python instalar.py
   ```
   Tarda 10 a 20 minutos. Al final te dice si todo quedó bien.
4. **Clave de API:** entra a console.anthropic.com, carga unos US$5 y crea una API key. Abre el archivo `.env` con el Bloc de notas y pégala en `ANTHROPIC_API_KEY=`.
5. Registra tu voz:
   ```
   python axtra.py registrar
   ```
6. Inicia Axtra:
   ```
   python axtra.py
   ```
   Di: *"Axtra, ¿cómo está el clima hoy?"*

La primera vez descarga el modelo Whisper (~500 MB).

## Cerebro híbrido: gastar menos saldo (o nada)
Axtra tiene tres niveles y elige solo:
1. **Órdenes directas (sin IA, gratis, instantáneas):** hora, fecha, clima de Tuluá, recordatorios y alarmas, tareas, poner o controlar música, "¿qué canción es esta?", abrir sitios y apps, "no me hables por una hora", "¿cuánto he gastado?", empezar una clase de idiomas o un dictado.
2. **Cerebro local (gratis, sin internet):** solo charla: saludos, cómo estás, opiniones, chistes, consejos, el modo compañero, el briefing matutino y **las clases de idiomas**. Corre en tu PC con Ollama.
3. **Claude (gasta saldo):** bolsa y finanzas, búsquedas en internet, noticias, correos y agenda, CRM y propuestas, bocetos, cámara y documentos, memoria de conversaciones.

- Si una pregunta necesita a Claude y no hay saldo o internet, responde el cerebro local y te avisa.
- Si el cerebro local responde "no puedo" o "lo siento", Axtra le pasa la pregunta a Claude automáticamente.
- Para apagar a Axtra por voz: *"Axtra, apágate"*.
- Para forzar a Claude di *"piénsalo bien"*, *"a fondo"* o *"investiga"*.
- El estudio autónomo y la reflexión nocturna solo funcionan con saldo; sin saldo se pausan solos.

**Instalar el cerebro local (una vez, unos 10 minutos):**
```
winget install -e --id Ollama.Ollama
```
Cierra y abre la terminal, entra a la carpeta axtra y escribe:
```
python axtra.py cerebro
```
Descarga el modelo (unos 2 GB) y lo prueba. Ollama queda encendido solo con Windows.

- Con 8 GB de RAM, el modelo `qwen2.5:3b` tarda unos segundos por respuesta. Si es muy lento, pon `JARVIS_MODELO_LOCAL=qwen2.5:1.5b` en `.env` y repite `python axtra.py cerebro`.
- `JARVIS_CEREBRO=local` en `.env`: nunca gasta saldo (sin finanzas en vivo, búsquedas ni cámara).
- `JARVIS_CEREBRO_IDIOMAS=claude`: clases con Claude (mejor calidad, gasta saldo).
- Cierra programas pesados (Chrome con muchas pestañas) si Axtra va lento.

## Gemini: segundo cerebro gratis
1. Entra a **aistudio.google.com** con tu Gmail → **Get API key** → **Create API key**. Copia la clave.
2. Ábre `.env` con el Bloc de notas y pégala en `GEMINI_API_KEY=` (si no existe la línea, agrégala).
3. Prueba: `python axtra.py gemini`. Debe decir "GEMINI LISTO".

Con Gemini la charla y las clases de idiomas salen más inteligentes y rápidas que con el cerebro local, y tu PC trabaja menos (menos RAM, menos batería). Si se acaba la cuota gratis del día o no hay internet, Axtra usa el cerebro local.
- **Privacidad:** en el plan gratis Google puede usar lo que se le envía para mejorar sus productos. Por eso Gemini solo recibe la charla: nunca tus recuerdos, notas, nombres de clientes, agenda ni correos (eso lo manejan Claude o el cerebro local).
- Para no usarlo: deja `GEMINI_API_KEY=` vacío.

## Modo autónomo con Gemini (gratis)
Los estudios, el informe del mercado, el briefing y la reflexión nocturna usan Gemini con búsqueda de Google, así que no gastan saldo de Claude. Las notas guardan las fuentes consultadas.
- Si se acaban las búsquedas gratis del día, el estudio se reintenta más tarde y el informe sale solo con los datos del mercado.
- Privacidad: el briefing (agenda, correos, clientes) y la reflexión (tus conversaciones del día) se envían a Gemini. Si prefieres que eso no salga de tu PC ni de Claude, pon `JARVIS_CEREBRO_AUTONOMO=claude`.

## Preguntas de conocimiento (historia, ciencia, noticias)
*"¿Quién fue Simón Bolívar?"* · *"Explícame la Revolución Francesa"*: las responde Gemini con su conocimiento (gratis). *"Últimas noticias de IA"* · *"¿Quién ganó el partido?"*: Gemini busca en Google (las búsquedas gratis son limitadas, por eso solo se usan para lo actual). En pantalla verás las fuentes. Si se acaban las búsquedas gratis del día, responde Claude. El cerebro local ya no responde preguntas de datos, porque se los inventa.

## Micrófono y volumen
- `python axtra.py microfono`: muestra tus micrófonos y qué tan fuerte te oye. Si te oye bajo, sube el "volumen de entrada" en Windows (Configuración > Sistema > Sonido > Entrada).
- Para elegir el micrófono USB: en `.env`, `JARVIS_MICROFONO=USB` (o parte de su nombre). Si no encuentra ese nombre, al arrancar te muestra la lista completa con un número al lado de cada uno (`[0] Micrófono...`, `[1] USB...`); también puedes poner ese número directamente: `JARVIS_MICROFONO=1`.
- Axtra aprende solo el ruido de tu cuarto para no obligarte a gritar, y sube la voz bajita antes de entenderla.
- También entiende "Hola Chávez", "Hola Travis" o "Hola James" como "Hola Axtra" (errores típicos del reconocimiento).
- Volumen real: *"volumen al 40"*, *"sube el volumen"*, *"¿cuánto está el volumen?"*, *"silencia el sonido"*, *"activa el sonido"*.
- Si el PC queda silenciado o casi en cero, Axtra lo arregla solo antes de hablar: nunca queda mudo.
- Si el micrófono deja de mandar sonido (se desconecta, un driver falla), Axtra ya no se queda congelado ni ignora Ctrl+C: lo detecta, avisa en pantalla y reabre el oído solo, sin que tengas que cerrar la ventana a la fuerza.

## Protocolo de inteligencia avanzada (aprender desde cero)
Di *"Axtra, activa protocolo de inteligencia avanzada"* (o *"... en neurociencia"*, *"... sobre programación en Python"*). También funciona desde el Escritorio, respondiendo por escrito.
1. La primera vez de cada habilidad te pregunta qué sabes y para qué la quieres, y **diseña una ruta** de 6 a 9 módulos desde los fundamentos (por ejemplo, neurociencia empieza por biología celular).
2. Cada sesión empieza con un **repaso espaciado**: preguntas de lo que ya viste, que vuelven a los 1, 2, 4, 8, 16 y 32 días. Recordar con esfuerzo es lo que fija el conocimiento.
3. **Lección estilo Feynman**: explicación corta con analogía y ejemplo, luego una pregunta para que **tú lo expliques**. No avanza hasta que lo entiendes; si no, lo explica de otra forma.
4. Guarda tarjetas de repaso, detecta lo que te cuesta y escribe tus notas en `mis_documentos/aprendizaje/`.
- Dentro del protocolo: *"siguiente"*, *"repite"*, *"más simple"*, *"más profundo"*, *"dame un ejemplo"*, *"¿cómo voy?"*, *"fin del protocolo"*.
- Fuera: *"¿Cómo voy en neurociencia?"*.
- Usa los cerebros gratis (Gemini/Groq) pensando a fondo; si fallan y el cerebro avanzado está activo, usa Claude.
- Rigor: está instruido para no inventar y avisar cuando algo es debatido, pero para temas científicos serios complementa con un buen libro o curso.

## Ondas de mar
Una ventana con olas que se mueven suaves en espera, se agitan cuando Axtra **razona**, laten cuando **habla** y se animan cuando **escucha**. Se abre sola con el protocolo; también: *"muestra las ondas"* / *"cierra las ondas"*.

## Escritorio: escríbele a Axtra
- Di *"Axtra, activa escritorio"* (o *"abre el escritorio"*, *"modo escritorio"*, *"quiero escribirte"*). Se abre una ventana.
- Escribe abajo y presiona **Enter**: Axtra **siempre responde en voz alta** y también lo ves escrito.
- La sesión de sincronización también funciona aquí: respondes escribiendo ("paso" para saltar, "termina" para acabar).
- Botón **Reportar fallo**: guarda la conversación reciente en `data/reporte_fallos.md`. Envíamelo y lo corrijo más rápido.
- Ciérralo con la X o diciendo *"Axtra, cierra el escritorio"*. (*"Muestra el escritorio"* sigue minimizando las ventanas de Windows.)

## Sincronización (inspirada en Atlas)
Una barra de 0 a 100 % que mide, con datos reales, qué tan bien te conoce Axtra. Todo se guarda en `data/sincronizacion.json`.
- **Identidad (10):** voz registrada 4, cara registrada 3, datos básicos 3.
- **Conocimiento (35):** 7 áreas (rutina, metas, negocios, estudios, gustos, forma de trabajar contigo, personas importantes), 1 punto por dato hasta 5 por área. Entra con "recuerda que...", la reflexión nocturna y las sesiones.
- **Experiencia (20):** 0.5 por día de uso (máx. 15) y 0.1 por conversación (máx. 1 al día, 5 en total). Baja 1 por semana sin usarlo.
- **Precisión (20):** "exacto", "bien" suman; "te equivocaste", "eso no es así" restan.
- **Confianza (15):** Google 4, perfil de Apex 3, CRM con 3+ clientes 2, sesiones de sincronización 1 c/u (máx. 4), modo compañero 2.

Niveles: **20 Reconocimiento** (saludo y briefing personalizados) · **40 Sintonía** (compañero personal) · **60 Anticipación** (cada tarde a las 7 revisa tu día siguiente y te propone qué preparar) · **80 Copiloto** ("lo de siempre" repite lo que sueles pedir a esa hora) · **100 Sincronización total** (informe semanal los domingos).

Órdenes: *"Axtra, nivel de sincronización"* · *"Sincronicemos"* (5 preguntas del área que menos conoce; di "paso" para saltar) · *"¿Qué sabes de mí?"*

## Núcleo de identidad
- `data/yo.md`: quién es Axtra, su fecha de "nacimiento", valores y personalidad. Puedes editarlo.
- **Diario:** cada noche escribe en `data/diario/` qué pasó, qué aprendió y cómo van sus metas. *"Axtra, ¿qué escribiste en tu diario?"*
- **Estado interno:** curiosidad (sube al estudiar), preocupación (alertas, pendientes), satisfacción (aciertos, subir de nivel). Cambia su tono.
- **Metas propias** (`data/metas_jarvis.json`): *"Axtra, ¿cuáles son tus metas?"*
- No es conciencia real: si le preguntas si siente, responde con honestidad.

## Elegir la voz
- *"Axtra, muéstrame las voces"*: escuchas las 10 voces gratis.
- *"Usa la voz 3"* · *"Voz más grave"* · *"Más aguda"* · *"Habla más rápido"* · *"Habla más despacio"* · *"Voz original"*.
- *"Activa / desactiva el filtro Axtra"*: eco y ecualización suaves, estilo IA de película.
- Las respuestas largas empieza a decirlas por frases: habla antes.
- La elección se guarda en `data/voz.json`.

## Cambiar el cerebro por voz
- *"Axtra, desactiva el cerebro avanzado"* (o *"no uses Claude"*, *"modo gratis"*): nunca usa Claude, cero saldo. La bolsa y las noticias las responde con búsqueda gratis; la agenda, correos, CRM, cámara, documentos y memoria no están disponibles en este modo.
- *"Axtra, activa el cerebro avanzado"*: vuelve al modo híbrido.
- *"Axtra, usa solo el cerebro local"*: todo en tu PC.
- *"Axtra, ¿qué cerebro estás usando?"* · *"¿Qué puedes hacer?"*
- El modo se guarda: sigue igual aunque apagues a Axtra.

## Más cerebros gratis y búsqueda gratis
Si Gemini se queda sin cuota, Axtra pasa solo a **Groq** y luego a **OpenRouter**. Las búsquedas en internet ya no dependen de Gemini: usa **DuckDuckGo** (gratis, sin clave) y, si pones la clave, **Tavily** (1000 búsquedas gratis al mes).

Claves gratis (pégalas en `.env`):
- **Groq:** console.groq.com → entra con Google → **API Keys** → Create API Key → `GROQ_API_KEY=`. Unas 1000 respuestas gratis al día; muy rápido.
- **OpenRouter:** openrouter.ai → entra con Google → **Keys** → Create Key → `OPENROUTER_API_KEY=`. Unas 50 respuestas gratis al día con modelos ":free".
- **Tavily (opcional):** tavily.com → Sign up → copia tu API key → `TAVILY_API_KEY=`.

Prueba todo con `python axtra.py cerebros`: dice cuáles funcionan.
- Privacidad: en planes gratis, algunos proveedores pueden usar lo que reciben. Axtra nunca les envía tus recuerdos, clientes, agenda ni correos; sí el perfil de Apex cuando pides ideas de negocio.

## Asesor de negocio con Gemini (gratis)
*"¿Qué es Apex Corporation?"* · *"Dame ideas para mejorar Apex"* · *"¿Cómo le vendo los orbes a un restaurante?"* · *"¿Cuánto debería cobrar por un orbe?"* · *"¿Qué estrategia de marketing me recomiendas para Apex Marketplace?"*: responde Gemini como socio estratégico, usando todo tu perfil de `perfil/apex.md`. En pantalla: "(Gemini, asesor de negocio: gratis)".
- Las acciones (agregar al CRM, redactar propuestas, hacer bocetos, buscar prospectos, tu agenda) siguen con Claude porque necesitan herramientas.
- Privacidad: el perfil de Apex se envía a Gemini; en el plan gratis Google puede usarlo para mejorar sus productos. Para que lo responda Claude: `JARVIS_CEREBRO_NEGOCIO=claude`.

## Batería
Con el cargador desconectado, Axtra apaga la cámara de fondo (el saludo al llegar) y la vuelve a prender al conectarlo. Desactívalo con `JARVIS_AHORRO_BATERIA=0`.

## Perfil de tus empresas y memoria de estudio
- En la carpeta `perfil` está `apex.md` con todo sobre Apex Corporation, los orbes, Apex Marketplace, las páginas web y Apex Closure. Ábrelo con el Bloc de notas para corregir o agregar datos; Axtra lo lee al instante.
- Puedes crear más archivos `.md` en `perfil` (por ejemplo `clientes.md` o `metas.md`).
- La sección "Detalles sugeridos por Claude" son ideas por confirmar: cámbialas o bórralas.
- El cerebro local consulta `perfil` y las notas que Axtra estudia (data/conocimiento) antes de responder, pero solo lo relacionado con tu pregunta, para no volverse lento. En pantalla verás "(consultó su memoria de estudio)".

## Memoria permanente
Axtra recuerda lo importante aunque lo apagues. Todo se guarda solo en tu PC, en la carpeta `data`:
- `recuerdos.json`: datos sobre ti. Prueba: *"Axtra, recuerda que mi negocio se llama Apex Closure"*.
- `historial.json`: la última conversación, para seguir donde quedaron.
- `conversaciones/`: registro diario. Prueba: *"Axtra, ¿qué hablamos ayer sobre TSMC?"*.
- Para borrar algo: *"Axtra, olvida lo de ..."*.

## Habilidades
- Recordatorios y alarmas: *"Recuérdame en 20 minutos sacar la ropa"* · *"Despiértame mañana a las 6:30"* (lo dice en voz alta a su hora; Axtra debe estar encendido)
- Tareas: *"Agrega a mis tareas llamar a los clientes"* · *"¿Qué tengo pendiente?"*
- Abrir cosas: *"Abre YouTube"* · *"Abre WhatsApp"* · *"Abre la calculadora"* · *"Busca en Google recetas de pasta"*

## Modo compañero
Mientras usas el computador, Axtra te habla por iniciativa propia más o menos cada 45 minutos:
te saluda la primera vez del día, te pregunta cómo va tu día, te recuerda algo de tu agenda o tus
clientes, te comenta algo del mercado o algo que aprendió, o te sugiere una pausa si llevas mucho rato.
- **Le puedes responder sin decir "Axtra"** durante 15 segundos después de que te habla.
- No habla si estás en videollamada (Zoom, Meet, Teams, Discord), con música puesta, en clase o dictado, ni justo después de que hablaron.
- *"Axtra, no me hables por una hora"* · *"Háblame más seguido, cada 20 minutos"* · *"Háblame menos"*.
- Ajustes en `.env`: `JARVIS_CONVERSADOR=0` para apagarlo, `JARVIS_CONVERSADOR_MINUTOS=45`, `JARVIS_HORAS_ACTIVAS=08:00-22:30`.
- Privacidad: solo mira el tipo de programa que usas (navegador, Word, código...), nunca el contenido de tu pantalla.
- Costo: menos de medio centavo de dólar por cada vez que te habla.

## Controlar el computador con la voz (gratis, sin IA)
Después de la primera orden, Axtra te sigue escuchando 30 segundos sin repetir "Axtra", así encadenas órdenes: *"Axtra, cuadrícula"* → *"cinco"* → *"tres"* → *"clic"*.
- **Mouse:** *"mueve el mouse a la derecha"* · *"más arriba"* · *"un poco a la izquierda"* · *"abajo mucho"* · *"mouse al centro"* · *"clic"* · *"doble clic"* · *"clic derecho"* · *"arrastra"* … *"suelta"*.
- **Página:** *"baja la página"* · *"sube un poco"* · *"baja mucho"*.
- **Cuadrícula (lo más preciso):** *"cuadrícula"* divide la pantalla en 9 cuadros numerados. Di un número (o varios: *"cinco tres"*) para acercarte y *"clic"* para hacer clic. *"Cancela"* la cierra.
- **Clic por nombre:** *"haz clic en Enviar"* · *"clic en Archivo"* · *"doble clic en Fotos"* · *"clic derecho en Descargas"*. Busca los botones de Windows y, si no, lee el texto de la pantalla.
- **Teclado:** *"escribe aquí: hola, ¿cómo estás?"* (escribe con tildes y ñ) · *"presiona enter"* · *"copia"* · *"pega"* · *"deshacer"* · *"selecciona todo"* · *"guarda"* · *"nueva pestaña"* · *"cierra la pestaña"* · *"atrás"* · *"recarga"* · *"cambia de ventana"* · *"minimiza"* · *"maximiza"* · *"escritorio"* · *"cierra la ventana"* · *"captura de pantalla"*.
- En modo mouse Axtra no te responde con voz: suena un pitido para que sepas que ya lo hizo.
- La voz se verifica al empezar; las órdenes cortas que siguen no se vuelven a verificar mientras usas el mouse.

## Cámara y visión
- *"Axtra, ¿qué ves?"* · *"¿Qué tengo en la mano?"* · *"¿Cómo me veo?"*: toma una foto y la analiza.
- *"Axtra, lee este documento"* · *"Explícame este ejercicio"* · *"Resume esta página"*: cuenta 3 segundos, toma la foto y lo lee. Las fotos quedan en `mis_documentos/capturas`.
- **Saludo al llegar:** registra tu cara una vez con `python axtra.py cara` (20 segundos frente a la cámara). Desde ahí, cuando llegues después de 10 minutos sin verte, te saluda y te dice si tiene avisos.
- Desactiva el saludo con `JARVIS_CAMARA_SALUDO=0`. Con el saludo activo, la luz de la cámara queda encendida mientras Axtra está prendido.
- Privacidad: nada de video se guarda; solo reconoce TU cara, y todo se procesa en tu PC (menos las fotos que le pides analizar, que van a Claude).

## Música
- *"Axtra, pon música lo-fi para estudiar"* · *"Pon Bad Bunny"*: busca en YouTube y reproduce en tu navegador.
- *"Pausa la música"* · *"Siguiente"* · *"Sube el volumen"* · *"Baja el volumen"*: usa las teclas multimedia de Windows.
- *"Axtra, ¿qué canción es esta?"*: escucha 10 segundos y te dice canción, artista, álbum y año (como Shazam). *"¿Qué canciones has reconocido?"* te da el historial.
- Cuando le hablas con música puesta por él, la pausa y la reanuda al terminar.
- Con música alta le cuesta escucharte: habla más fuerte o baja el volumen.

## Idiomas (inglés y más)
- *"Axtra, quiero practicar inglés"* · *"Clase de inglés para entrevistas de trabajo"* · *"Practiquemos francés, nivel básico"*.
- Te habla con una voz nativa, conversa sobre tus temas (negocios, bolsa, tecnología), te corrige lo importante y siempre te hace preguntas para que hables más que él.
- Guarda tu vocabulario nuevo y tus errores frecuentes, y los repasa en la siguiente clase. Estima tu nivel (A1 a C1).
- Para terminar: *"fin de la clase"* o *"end the lesson"*. Pregunta *"¿Cómo va mi inglés?"* para ver tu progreso.
- Idiomas: inglés, francés, portugués, alemán, italiano, mandarín y japonés.

## Rutinas automáticas
- **Briefing matutino** a las 6:30 (cámbialo con `JARVIS_BRIEFING_HORA`): suena una alarma y te da clima, agenda de las primeras 3 horas, tareas, clientes a contactar, correos y mercado. Si enciendes a Axtra más tarde (antes del mediodía), te lo da al encender. También puedes pedirlo: *"Axtra, dame mi briefing"*.
- **Informe del mercado** de lunes a viernes a las 4:15 p. m. (`JARVIS_INFORME_MERCADO_HORA`): te lo resume en voz y lo guarda en `mis_documentos`.

## Negocio
- **CRM:** *"Agrega a Don Pepe de la salchipapería Mr Papa, teléfono 300..."* · *"Pasa a Mr Papa a propuesta, lo llamo el viernes"* · *"¿A quién debo llamar hoy?"* · *"¿Cómo va mi embudo de ventas?"*
- **Prospectos:** *"Busca restaurantes en Tuluá sin página web"* (categorías: restaurantes, tiendas, salud, belleza, servicios, hoteles, gimnasios). Usa OpenStreetMap, que no tiene todos los negocios, así que complementa con Google Maps.
- **Bocetos web:** *"Haz un boceto para la Panadería La Espiga, colores cálidos"*. Lo diseña en 1-2 minutos, lo abre en el navegador y lo guarda en `mis_documentos/bocetos`. El formulario valida los datos pero no envía nada hasta que el cliente pague.
- **Propuestas:** *"Redacta una propuesta para Mr Papa: página web a 300 mil, entrega en 5 días"*. Te abre un Word listo.

## Universidad: modo dictado
*"Axtra, quiero dictar mi ensayo de comercio internacional"*. Hablas con calma y dices *"nuevo párrafo"* para separar, *"borra lo último"* para corregir y *"fin del dictado"* para terminar. Axtra corrige ortografía y puntuación y organiza el texto, **sin cambiar tus ideas ni agregar contenido**. Te abre el Word y guarda aparte el dictado original.

## Google Calendar y Gmail (una sola vez, unos 10 minutos)
1. Entra a **console.cloud.google.com** con tu cuenta de Gmail y crea un proyecto llamado "Axtra".
2. En "APIs y servicios" → **Biblioteca**, activa **Google Calendar API** y **Gmail API**.
3. En **Pantalla de consentimiento OAuth**: tipo "Externo", nombre "Axtra", tu correo. En **Usuarios de prueba**, agrega tu propio Gmail.
4. En **Credenciales** → Crear credenciales → **ID de cliente de OAuth** → tipo **App de escritorio**. Descarga el JSON.
5. Cambia el nombre del archivo a `credentials.json` y ponlo en la carpeta `axtra`.
6. En la terminal: `python axtra.py google`. Se abre el navegador; elige tu cuenta y acepta. Si sale "Google no verificó esta app", toca "Continuar", porque la app es tuya.
7. Listo: *"¿Qué tengo hoy en el calendario?"* · *"¿Tengo correos importantes?"* · *"Agenda reunión con Mr Papa el viernes a las 10"* · *"Redacta un correo para ... "* (queda en borradores, nunca se envía solo).

## Analista financiero
- *"Axtra, ¿cómo va Nvidia hoy?"* · *"Hazme un análisis técnico de TSMC"*
- *"Registra que compré 2 acciones de Apple a 230"* · *"¿Cómo va mi portafolio?"*
- *"Agrega AMD a mi lista de seguimiento"* · *"Avísame si el S&P 500 baja de 6000"*
- *"Hazme un análisis fundamental de Apple"* (datos oficiales de la SEC; para mejores resultados pon tu correo en `JARVIS_CONTACTO_SEC`)
- *"Muéstrame la gráfica de Nvidia a 6 meses comparada con AMD"*: se abre en pantalla.
- **Simulador con dinero ficticio:** *"Reinicia el simulador con 10 mil dólares"* · *"En el simulador compra 10 acciones de Microsoft"* · *"¿Cómo va mi simulador contra el S&P 500?"*
- Con tu dinero real, Axtra analiza y opina pero **nunca compra ni vende**: la decisión siempre es tuya.

## Aprendizaje autónomo
Mientras Axtra está encendido, trabaja solo:
- **Estudia** cada 3 horas (máx. 6 veces al día) un tema tuyo o una acción de tu lista, y guarda la nota en `data/conocimiento/`. Cada estudio deja preguntas nuevas que se convierten en el siguiente tema.
- **Reflexiona** cada noche (después de las 9 p. m.) sobre lo que hablaron y guarda lecciones para responderte mejor (`data/habilidades.json`).
- **Vigila** tus alertas de precio cada 15 minutos y te avisa la próxima vez que le hables.
- Pídele: *"Axtra, estudia a fondo las opciones financieras"* o *"¿Qué aprendiste hoy?"*.
- Por defecto estudia hasta 3 veces al día (cada 4 horas). Cada estudio cuesta unos 5 a 10 centavos de dólar. Ajusta `JARVIS_ESTUDIOS_POR_DIA` o apágalo con `JARVIS_AUTONOMIA=0`.

## Gastos
- Pregúntale: *"Axtra, ¿cuánto has gastado hoy?"* y te dice el gasto estimado y cuántos días te dura el saldo.
- El registro está en `data/gastos.json`. El saldo exacto siempre está en console.anthropic.com.
- Recomendado: en console.anthropic.com pon un límite de gasto mensual.

## Dónde quedan tus archivos
Todo lo que crea Axtra (propuestas, bocetos, dictados, gráficas, informes) está en la carpeta `mis_documentos`.

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
5. Reinicia Axtra. Si algo falla, vuelve a la voz gratis sola.

## Ajustes (archivo `.env`)
| Ajuste | Para qué |
|---|---|
| `JARVIS_VOICE_THRESHOLD` | Qué tan estricto es con tu voz. Si otra persona pasa, súbelo (0.80). Si a ti te rechaza, bájalo (0.70) |
| `JARVIS_WAKE_MODE` | `es` = decir "Axtra" en español (por defecto); `en` = decir "Hey Axtra" en inglés |
| `JARVIS_PAUSA_FINAL` | Segundos de silencio para saber que terminaste (0.5). Si te corta a mitad de frase, súbelo a 0.8 |
| `JARVIS_RECONOCIMIENTO` | `google` (mejor, gratis, en la nube) o `whisper` (local, privado) |
| `JARVIS_INTERRUMPIR` | `1` para poder interrumpirlo, `0` para desactivar |
| `JARVIS_WHISPER_MODEL` | `small` entiende mejor; `base` es más rápido si tu PC va lento |
| `JARVIS_VOICE` | Voz de Axtra: `es-CO-GonzaloNeural`, `es-MX-JorgeNeural`, `es-ES-AlvaroNeural` |

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
