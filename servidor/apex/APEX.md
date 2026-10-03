# Orbes de negocios (Apex Play), con Axtra como tarjeta madre

El cliente escanea el QR de su mesa, toca **«Toque para comenzar»** y el orbe lo atiende **solo por voz**. Los pedidos llegan al **panel del mesero**, que también abre y cierra las mesas. Tú ves cada negocio en la pantalla **«Negocios»** de tu app de Axtra.

## Cómo está armado

```
                 ┌──────────────── AXTRA (tarjeta madre) ────────────────┐
                 │ Todas las claves (.env): Groq, Gemini, Google, Claude… │
                 │ y los PIN de los paneles. Pantalla «Negocios».         │
                 │   axtra.chat (8080, privado con Access)                │
                 │   ranura privada (8090, el túnel NO la publica):       │
                 │     /oido  Groq Whisper        voz → texto             │
                 │     /pensar Groq gpt-oss → Gemini (respaldo)           │
                 │     /voz   Google TTS → voz gratis de Axtra (respaldo) │
                 └───────────────────────────┬────────────────────────────┘
                                             │ (dentro del servidor)
                 ┌───────────────────────────┴────────────────────────────┐
                 │ PUERTA PÚBLICA api.axtra.chat (8081) · SIN claves       │
                 │ mesas, conversaciones, herramientas, pedidos, costo $   │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                        Teléfono del cliente: menú + orbe (apex-voz.js)
```

**Una vuelta de conversación:**
1. El teléfono detecta cuándo el cliente termina de hablar y manda solo ese pedacito de audio.
2. Axtra lo pasa a texto (oído).
3. Lo responde con el menú, la personalidad del restaurante y las herramientas (cerebro).
4. Convierte la respuesta en voz.
5. El orbe la dice y vuelve a escuchar.

Si el cliente habla mientras el orbe habla, el orbe se calla y lo escucha.

**Frases fijas grabadas:** saludo, «Muy buena elección», despedida, «¿me repite?» y otras. Se generan **una sola vez** y quedan guardadas, así que suenan al instante y **no cuestan**. Los botones «Pedir» usan frases fijas, así que **no gastan cerebro**.

## Costo real por pieza (medido)

Precios en pesos, con el dólar a 4.000 COP:

| Pieza | Servicio | Costo por respuesta del orbe |
|---|---|---|
| Oído | Groq Whisper turbo (mínimo 10 s) | ~0,4 COP |
| Cerebro | Groq gpt-oss-20b (2 pasos con herramientas) | ~1,6 COP |
| Voz | Google Neural2 (~80 caracteres) | ~5 COP |
| **Total** | | **~7 COP por respuesta** |

Una conversación típica tiene unas 3 respuestas habladas, unos **20–25 COP**. A eso se suman los botones y las frases fijas, que no cuestan.

| Restaurante | Conversaciones al mes | Costo de API al mes |
|---|---|---|
| Pequeño | 450 | ~10.000 COP |
| Mediano | 1.200 | ~26.000 COP |
| Grande | 3.000 | ~65.000 COP |

Además, **Google regala 1 millón de caracteres de voz al mes** (unas 12.000 respuestas), así que el costo real es menor. Ese regalo se comparte entre todos los negocios.

**Tipo de voz**, en `restaurantes/<id>.json`, campo `"voz"`:
- **Neural2** (por defecto): natural, 16 US$ por millón de caracteres.
- **Chirp3-HD**: la más humana, 30 US$ por millón. Para un plan premium.
- **Standard**: robótica, 4 US$ por millón.

## Seguridad y control de gasto

| Riesgo | Qué hace el sistema |
|---|---|
| Robo de claves | La puerta pública **no tiene ninguna clave**. Todas, incluidos los PIN, viven en el `.env` de Axtra. La ranura no publica nada hacia internet y rechaza lo que llegue por Cloudflare. |
| Pedidos falsos con una foto del QR | Con la mesa **cerrada** no hay conversación ni pedidos. Al cerrarla, se corta. |
| Dos teléfonos en la misma mesa | **Una conversación activa por mesa.** El mismo teléfono puede recargar sin bloquearse. |
| Otras páginas usando la puerta | Solo se aceptan los **dominios del restaurante** (CORS y revisión en el servidor). |
| Abuso | Límite de peticiones por IP, por mesa y por conversación. Hay bloqueo tras 8 PIN incorrectos. |
| Gasto | **Tope mensual en pesos por restaurante** (80.000 por defecto). Al llegar, el orbe solo usa frases grabadas y «Llamar al mesero». Además hay tope de minutos y de respuestas por conversación. |
| Caídas | Groq → **Gemini**. Google → **voz gratis de Axtra**. Todo caído → **«Llamar al mesero»** resaltado, que siempre funciona. |

## Un restaurante = un archivo

`servidor/apex/restaurantes/<id>.json` contiene:
- nombre, personalidad, voz, frases fijas;
- menú, mesas, dominios permitidos y tope mensual en pesos.

Para agregar un restaurante, copia `demo.json`, cámbialo y agrega su PIN en el `.env` de Axtra como `APEX_PIN_<ID>`.

## Ponerlo en marcha (una vez)

1. **Claves en el `.env` de Axtra**, todas en el mismo archivo:
   - `GROQ_API_KEY`: ya la tienes; oído y cerebro.
   - `GEMINI_API_KEY`: ya la tienes; respaldo del cerebro.
   - `GOOGLE_TTS_API_KEY`: la voz natural. Créala en Google Cloud → APIs → *Cloud Text-to-Speech API* → Habilitar → Credenciales → Crear clave de API, y **restríngela** a esa API. Mientras no exista, el orbe usa la voz gratis de Axtra.
   - `APEX_PIN_DEMO`: el PIN del panel, de 4 a 6 números.
2. **Ruta pública en el túnel de Cloudflare:** Zero Trust → Networks → Tunnels → `axtra` → *Published application routes* → **Add**, con estos datos:
   - Subdomain: `api`
   - Domain: `axtra.chat`
   - Type: `HTTP`
   - URL: `apex:8081`

   **No** crees una aplicación de Access para `api`.
3. **Probar:** abre `https://api.axtra.chat` en el celular. Es el **modelo de ejemplo** para mostrar la idea a los clientes
   (`"ejemplo": true` en `demo.json`): sin mesas, sin caja y sin PIN; cada persona que abre el link tiene su propia
   conversación. El botón «Mostrar código QR» de la entrada (o `https://api.axtra.chat/qr`) da el QR para que otra persona
   lo pruebe en su celular.

### Cómo funciona el modelo de demostración
- Tocar el orbe abre la carta. El cliente puede **hablarle** o solo **tocar botones** (si no da permiso del micrófono, igual funciona y el orbe le habla).
- «Pedir», «−», «Quitar», «Confirmar pedido» y la oferta responden con **frases grabadas**: no gastan cerebro ni voz nueva.
- Al pedir un plato fuerte sin bebida, sugiere la bebida una vez (`ventas.sugerir`). Al confirmar sin el postre del día, lo ofrece una vez (`ventas.oferta`); «No, enviar así» lo manda a la caja.
- Solo cuando el cliente **habla** se usa el oído y el cerebro de Axtra.

## Integrarlo en el menú de cada restaurante

```html
<script src="https://api.axtra.chat/web/apex-voz.js"></script>
<script>
  const orbe = new ApexVoz({ api: "https://api.axtra.chat", restaurante: "demo", mesa: MESA_DEL_QR });
  orbe.onestado = (e) => {};   // conectando, escuchando, oyendo, pensando, hablando, dormido, apagado
  orbe.onnivel = (n) => {};    // 0..1 para que el orbe palpite
  orbe.onpedido = (p) => {};   // el pedido cambió
  orbe.onsinvoz = () => {};    // resaltar «Llamar al mesero»
  botonComenzar.onclick = () => orbe.iniciar();
  botonPedir.onclick = () => orbe.pedirPlato("ajiaco");
  botonQuitar.onclick = () => orbe.quitarPlato("ajiaco");
  botonConfirmar.onclick = async () => { const r = await orbe.confirmar(); /* r.oferta: ofrecer; r.despedida: enviado */ };
  botonMesero.onclick = () => orbe.llamarMesero();
</script>
```

Agrega el dominio de ese menú a `"dominios"` en el archivo del restaurante.

## Siguiente fase
- Dominio propio por restaurante con **Cloudflare for SaaS** (custom hostnames) apuntando al menú.
- Un panel para crear restaurantes desde Axtra, sin editar archivos.
- Plan premium opcional con voz Chirp3-HD o voz a voz de OpenAI.
