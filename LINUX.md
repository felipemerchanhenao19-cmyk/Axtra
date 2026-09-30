# Cambiar Windows por Linux (y llevar a Axtra)

Guía para tu ASUS Vivobook Go. Al final tendrás **Linux Mint** en lugar de Windows y Axtra funcionando igual.

> **Importante:** instalar Linux de esta forma **borra todo el disco**: Windows, programas y archivos.
> No empieces sin hacer el Paso 1 completo.

**Qué necesitas:** una memoria USB de 8 GB o más (se borrará), el cargador conectado, buen internet y unas 2 horas.

**Por qué Linux Mint (edición Cinnamon):** se parece mucho a Windows (menú de inicio, barra de tareas), es estable, gasta menos memoria que Windows 11 y usa X11, que Axtra necesita para mover el mouse y leer la pantalla. Si después lo sientes lento, la edición **Xfce** es más liviana y se instala igual.

---

## Paso 1. Respaldo (en Windows, antes de todo)

1. **Actualiza Axtra** para que traiga el soporte de Linux. En PowerShell, dentro de la carpeta de Axtra:
   ```powershell
   git pull origin claude/axtra-continuacion-p5n98r
   ```
2. **Copia a la USB o a Google Drive la carpeta completa de Axtra**, sobre todo:
   - `.env` (tus claves: no está en GitHub)
   - `data` (tu voz registrada, memoria, recuerdos, sincronización, CRM, simulador)
   - `mis_documentos` y `perfil`
   - `credentials.json` y `token.json` si conectaste Google
   - **No hace falta** copiar la carpeta `venv`: en Linux se crea una nueva.
3. **Copia tus otros archivos personales:** Documentos, Descargas, Escritorio, Imágenes, Videos.
4. **Contraseñas del navegador:** inicia sesión en Chrome, Brave o Edge para que se sincronicen, o expórtalas.
5. Anota la contraseña de tu Wi-Fi.

> La USB del respaldo **no** puede ser la misma que usarás para instalar Linux (esa se borra).

## Paso 2. Crear la USB de instalación (en Windows)

1. Descarga Linux Mint en **linuxmint.com → Download → Cinnamon Edition** (un archivo `.iso` de unos 3 GB).
2. Descarga **Rufus** en **rufus.ie** (la versión portable no se instala).
3. Conecta la USB, abre Rufus y elige:
   - **Dispositivo:** tu USB
   - **Elección de arranque:** el `.iso` de Linux Mint
   - **Esquema de partición:** GPT · **Sistema de destino:** UEFI
4. Pulsa **Empezar**. Si pregunta por el modo de escritura, elige **"Escribir en modo Imagen ISO"**. Acepta que borre la USB.

## Paso 3. Arrancar desde la USB y PROBAR (sin instalar todavía)

1. Apaga el PC con la USB conectada.
2. Préndelo y presiona **Esc** repetidamente hasta que salga el menú de arranque; elige la USB (a veces aparece como "UEFI: ..."). Si no sale ese menú, presiona **F2** al prender para entrar al BIOS y, en **Boot**, pon la USB de primera.
3. Si no arranca o sale un error de seguridad: en el BIOS (F2) ve a **Security → Secure Boot** y ponlo en **Disabled**; guarda con F10.
4. En el menú de la USB elige **"Start Linux Mint"**. Arranca en modo prueba: nada se instala todavía.
5. **Prueba antes de instalar**, porque es tu última oportunidad de arrepentirte sin perder nada:
   - **Wi-Fi:** conéctate (icono abajo a la derecha).
   - **Sonido:** pon un video de YouTube.
   - **Micrófono:** Menú → **Sonido** → pestaña **Entrada**: habla y mira que la barra se mueva.
   - **Cámara**, si usas el saludo con la cara.

   Si el Wi-Fi o el micrófono **no funcionan**, **no instales**: apaga, quita la USB y Windows sigue intacto. Avísame y buscamos una solución.

## Paso 4. Instalar Linux Mint (esto borra Windows)

1. En el escritorio de prueba, doble clic en **"Install Linux Mint"**.
2. **Idioma:** Español. **Teclado:** Spanish (Latin American), o prueba escribiendo ñ y tildes en el recuadro.
3. Marca **"Instalar códecs multimedia"**.
4. **Tipo de instalación:** **"Borrar disco e instalar Linux Mint"**. Confirma.
5. **Zona horaria:** Bogotá.
6. **Tu usuario:** nombre, nombre del equipo y contraseña. La contraseña te la pedirá para instalar cosas: no la olvides.
7. Al terminar, reinicia y **quita la USB** cuando lo pida.

## Paso 5. Primeros ajustes en Linux

1. Conéctate al Wi-Fi.
2. Menú → **Gestor de actualizaciones** → instala todo y reinicia.
3. Menú → **Gestor de controladores**: si recomienda alguno, instálalo.
4. En la pantalla donde escribes la contraseña al prender, deja la sesión normal **Cinnamon**, no "Cinnamon (Wayland)". Axtra necesita la normal.

## Paso 6. Instalar Axtra

1. Conecta la USB del respaldo y copia la carpeta de Axtra a tu carpeta personal, con el nombre `axtra` (queda en `/home/tu_usuario/axtra`). Si copiaste la carpeta `venv`, bórrala.
2. Abre la **Terminal** (Ctrl+Alt+T) y escribe:
   ```bash
   cd ~/axtra
   bash instalar_linux.sh
   ```
   Pide tu contraseña una vez, instala los programas del sistema y las librerías de Axtra (10 a 20 minutos) y al final te ofrece instalar **Ollama**, el cerebro local gratis.
3. **Micrófono:** los nombres cambian en Linux. Ejecuta:
   ```bash
   python3 axtra.py microfono
   ```
   Si tu `.env` tiene una línea `JARVIS_MICROFONO=...`, cámbiala por el nombre o número que aparezca, o bórrala para usar el predeterminado.
4. **Vuelve a registrar tu voz**, porque en Linux el micrófono suena distinto:
   ```bash
   python3 axtra.py registrar
   python3 axtra.py voz probar
   ```
5. **Prueba los cerebros** y, si instalaste Ollama, descarga el modelo:
   ```bash
   python3 axtra.py cerebros
   python3 axtra.py cerebro
   ```
6. **Inicia Axtra:**
   ```bash
   python3 axtra.py
   ```

Para editar el `.env` en Linux: `xed ~/axtra/.env` (es como el Bloc de notas).

## Paso 7 (opcional). Que Axtra arranque solo al prender el PC

Menú → **Aplicaciones al inicio** → **+** → **Comando personalizado**:
- **Nombre:** Axtra
- **Comando:** `gnome-terminal -- bash -c "cd ~/axtra && python3 axtra.py; exec bash"`
- **Retraso:** 10 segundos, para que primero se conecte el Wi-Fi.

---

## Qué cambia con Axtra en Linux

| Función | En Linux |
|---|---|
| Voz, oído, cerebros, memoria, finanzas, negocio, idiomas, dictado | Igual que en Windows |
| Volumen ("volumen al 40", "silencia") | Igual |
| Música: pausar, siguiente, "¿qué está sonando?" | Igual (usa `playerctl`, que funciona con YouTube en el navegador y con Spotify) |
| Mouse por voz, cuadrícula, teclado | Igual |
| "Haz clic en Enviar" | Solo lee el texto de la pantalla (Windows además buscaba los botones por dentro). Si no lo encuentra, usa la cuadrícula |
| "Minimiza", "maximiza", "captura de pantalla" | Pueden no funcionar: esos atajos del teclado cambian en Linux |
| Abrir apps: calculadora, bloc de notas, explorador | Abre las de Linux (Calculadora, Xed, Nemo). "Paint" abre **Drawing** si lo instalas: `sudo apt install drawing` |
| Propuestas en Word | Se abren con LibreOffice, que viene instalado |
| Modo compañero (ve qué programa usas) | Igual |
| Ahorro de batería de la cámara | Igual |
| Voz sin internet (respaldo) | Más robótica que la de Windows (usa espeak) |
| MyASUS (modo de carga de la batería) | No existe en Linux |

## Si quieres volver a Windows

Descarga "Windows 11" en **microsoft.com/software-download/windows11**, crea la USB con la herramienta de Microsoft e instálalo borrando el disco. La licencia de tu ASUS está guardada en el equipo y se activa sola.
