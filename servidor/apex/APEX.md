# Apex Play: el orbe de voz para restaurantes

El cliente escanea el QR de su mesa, toca **«Toque para comenzar»** y el orbe lo atiende **solo por voz** (OpenAI Realtime, voz a voz, como el modo de voz de ChatGPT). Los pedidos llegan al **panel del mesero**, que también abre y cierra las mesas.

## Cómo está armado

```
Teléfono del cliente ──(menú: la página del restaurante)
   │  1. POST /v1/sesion  {restaurante, mesa}          ┌──────────────────────────────┐
   ├──────────────────────────────────────────────────▶│ api.axtra.chat (contenedor   │
   │  ◀── token efímero de 60 s (ek_…)                 │ "apex", SIN Cloudflare Access)│
   │                                                   │  · revisa que la mesa esté   │
   │  2. WebRTC con el token ──▶ OpenAI Realtime       │    ABIERTA y el origen       │
   │     (la voz va directo, sin pasar por el servidor)│  · pide el token a OpenAI    │
   │                                                   │    con SU llave (nunca sale) │
   │  3. herramientas: agregar_plato, ver_pedido,      │  · ejecuta las herramientas  │
   │     confirmar_pedido, llamar_mesero ─────────────▶│  · guarda pedidos y uso      │
   │                                                   │  · cuelga llamadas largas    │
   └───────────────────────────────────────────────────└──────────────────────────────┘
Panel del mesero: https://api.axtra.chat/panel?r=demo   (PIN)
```

- **Axtra sigue privado.** La puerta corre en otro contenedor, con otra base de datos y otro archivo de claves (`apex.env`). Desde `api.axtra.chat` no se llega a nada de Axtra.
- **La llave de OpenAI nunca llega al navegador.** El servidor entrega un token que solo sirve 60 segundos para conectarse.
- **El orbe no muestra texto.** Solo se escucha.

## Seguridad y control de gasto

| Riesgo | Qué hace la puerta |
|---|---|
| Pedidos falsos con una foto del QR | Con la mesa **cerrada** no hay sesión ni pedidos. El mesero la abre desde el panel al sentar a los clientes. Al cerrarla, la conversación se corta. |
| Dos teléfonos en la misma mesa | **Una conversación activa por mesa.** El mismo teléfono puede recargar la página sin quedar bloqueado. |
| Otras páginas usando la puerta | Solo se aceptan peticiones de los **dominios del restaurante** (CORS y revisión del origen en el servidor). |
| Abuso | **Límite de peticiones**: 6 sesiones por minuto por IP, 4 por mesa y 60 herramientas por minuto. Hay bloqueo tras 8 PIN incorrectos. |
| Conversaciones eternas | **Tope de minutos por sesión** (8 por defecto). El servidor **cuelga la llamada** en OpenAI aunque el teléfono no colabore. También cierra las sesiones que no conectan. |
| Gasto del mes | **Topes por restaurante**: conversaciones, minutos y US$ al mes. Al llegar al tope, el orbe dice que un mesero lo atenderá. El panel muestra el uso del mes. |

El costo en US$ es una **estimación** con los tokens que reporta OpenAI y los precios de `config.py`. Revísalos en la página de precios de OpenAI. Pon además un **límite de gasto mensual en la cuenta de OpenAI** (Settings → Limits): ese es el tope duro.

**Precios de referencia** (USD por millón de tokens de audio, a octubre de 2026; verifícalos):
- `gpt-realtime-2.1-mini`: entrada 10, salida 20.
- `gpt-realtime-2.1`: entrada 32, salida 64.

En la práctica, el mini cuesta unos **US$0.02–0.15 por minuto** de conversación.

## Un restaurante = un archivo

`servidor/apex/restaurantes/<id>.json` contiene:
- nombre, personalidad del orbe, voz (`marin`, `cedar`, …) y modelo;
- frases del guion (saludo, «Muy buena elección», despedida);
- menú, mesas, dominios permitidos y topes.

Para cambiar al modelo completo: `"modelo": "gpt-realtime-2.1"`. El PIN del panel va en `apex.env` como `APEX_PIN_<ID>` y **nunca** en GitHub.

## Ponerlo en marcha (una vez)

1. **Llave de OpenAI:**
   - Entra a platform.openai.com → **API keys** → *Create new secret key*.
   - Carga saldo en **Billing**.
   - En **Limits**, pon un tope mensual (por ejemplo US$10).
2. **Claves en el servidor.** Usa el mismo método del Bloc de notas: reemplaza lo que está en MAYÚSCULAS y pégalo en la terminal del servidor.
   ```
   cat > /opt/axtra/servidor/apex.env <<'FIN'
   OPENAI_API_KEY=PEGA_AQUI_LA_LLAVE_DE_OPENAI
   APEX_MODELO=gpt-realtime-2.1-mini
   APEX_PIN_DEMO=ELIGE_UN_PIN_DE_4_A_6_NUMEROS
   FIN
   chmod 600 /opt/axtra/servidor/apex.env
   cd /opt/axtra/servidor/despliegue && docker compose up -d --build
   ```
3. **Ruta pública en el túnel de Cloudflare:**
   - Ve a Zero Trust → Networks → Tunnels → `axtra` → **Published application routes** (o *Public Hostname*) → **Add**.
   - Subdomain: `api`
   - Domain: `axtra.chat`
   - Type: `HTTP`
   - URL: `apex:8081`

   La aplicación de Access protege solo `axtra.chat`, así que `api.axtra.chat` queda **pública**. **No** crees una aplicación de Access para `api`.
4. **Probar:**
   - En el PC, abre `https://api.axtra.chat/panel?r=demo`, entra con el PIN y toca la **mesa 1** para abrirla.
   - En el celular, abre `https://api.axtra.chat/demo?r=demo&mesa=1`, toca «Toque para comenzar» y habla.
   - El pedido aparece en el panel.

## Integrarlo en el menú de cada restaurante

En la página del menú (por ejemplo, la que está en Cloudflare Workers):
```html
<script src="https://api.axtra.chat/web/apex-voz.js"></script>
<script>
  const orbe = new ApexVoz({ api: "https://api.axtra.chat", restaurante: "demo", mesa: MESA_DEL_QR });
  orbe.onestado = (e) => { /* animar el orbe: conectando, escuchando, pensando, hablando, apagado */ };
  orbe.onnivel = (n) => { /* 0..1: volumen de la voz, para que el orbe palpite */ };
  orbe.onerror = (msg) => { /* mostrar aviso */ };
  botonComenzar.onclick = () => orbe.iniciar();
  botonPedir.onclick = () => orbe.pedirPlato("ajiaco");
  botonPedirTodo.onclick = () => orbe.pedirTodo();
</script>
```
Agrega el dominio de ese menú a `"dominios"` en el archivo del restaurante.

## Siguiente fase: varios restaurantes con su propio dominio

- Cada restaurante es un archivo JSON con sus datos separados por `restaurante` en la base de datos.
- Su dominio (por ejemplo `menu.restaurante.com`) apunta al Worker del menú con **Cloudflare for SaaS (custom hostnames)**. El Worker llama a `api.axtra.chat`, y ese dominio se agrega a `"dominios"`.
- Más adelante: un panel de administración para crear restaurantes sin editar archivos.
