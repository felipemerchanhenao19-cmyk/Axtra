# Publicar Axtra (guía paso a paso)

Al terminar tendrás Axtra en tu dominio (por ejemplo `https://axtra.app`), solo para tu cuenta de Google, instalada en tu celular y conectada con tu Axtra del PC.

**Tiempo:** 1 a 2 horas. **Costo:** dominio (~US$15 al año) + servidor (~US$5 al mes) + lo que gastes en Claude (con tope).

---

## Parte A. Claves (se puede hacer ya, sin dominio)

| Clave | Dónde | ¿Ya la tienes? |
|---|---|---|
| `GROQ_API_KEY` | console.groq.com → API Keys (gratis) | Sí, en el `.env` del PC |
| `GEMINI_API_KEY` | aistudio.google.com → Get API key (gratis) | Probablemente sí |
| `OPENROUTER_API_KEY` | openrouter.ai → Keys (gratis) | Revisa tu `.env` |
| `CEREBRAS_API_KEY` | cloud.cerebras.ai → API Keys (gratis) | Nueva (opcional, respaldo) |
| `TAVILY_API_KEY` | tavily.com (1000 búsquedas gratis al mes) | Opcional |
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys | Sí. Pon un límite de gasto mensual en *Billing* |
| `XAI_API_KEY` (Grok) | console.x.ai | Más adelante |

Guárdalas en un lugar seguro (por ejemplo, una nota protegida). **Nunca** las mandes por chat.

## Parte B. El servidor

1. Crea una cuenta en **hetzner.com/cloud** (o DigitalOcean / Vultr, cualquiera sirve).
2. Crea un servidor: **Ubuntu 24.04**, el plan más pequeño (2 GB de RAM alcanzan, ~US$5 al mes).
3. Anota su dirección IP y la contraseña de `root` (o configura una llave SSH).
4. Conéctate desde PowerShell: `ssh root@LA_IP`

## Parte C. El dominio (el paso final que falta)

1. Crea una cuenta gratis en **cloudflare.com**.
2. **Domain Registration → Register Domains** → busca `axtra` y compra el primero libre (`axtra.app`, `axtraia.com`, …).

## Parte D. El túnel (conecta el servidor con tu dominio sin abrir puertos)

1. En Cloudflare: **Zero Trust → Networks → Tunnels → Create a tunnel → Cloudflared**. Nombre: `axtra`.
2. Copia el **token** que aparece (el texto largo después de `--token`). Es tu `TUNNEL_TOKEN`.
3. En **Public Hostname**: tu dominio (ej. `axtra.app`), servicio **HTTP**, URL `axtra:8080`. Guarda.

## Parte E. Que solo entres tú (Cloudflare Access)

1. **Zero Trust → Access → Applications → Add an application → Self-hosted**.
   - Nombre: `Axtra`. Dominio: el tuyo. Duración de la sesión: 1 mes.
2. **Política 1** — Acción *Allow*, Incluir *Emails*: `felipemerchanhenao19@gmail.com`.
3. **Inicio de sesión:** en *Settings → Authentication* agrega **Google** (o deja *One-time PIN*: te llega un código al correo).
4. Copia el **Application Audience (AUD) Tag** → `CF_ACCESS_AUD`.
5. Tu **nombre de equipo** está en *Settings → Custom pages* (`TU-EQUIPO.cloudflareaccess.com`) → `CF_ACCESS_EQUIPO` (solo `TU-EQUIPO`).

### Token para el Axtra del PC
1. **Access → Service Auth → Create Service Token**. Nombre: `axtra-pc`, duración: sin vencimiento.
2. Copia el **Client ID** y el **Client Secret** (el secreto solo se muestra una vez).
3. En la aplicación Axtra agrega la **Política 2** — Acción *Service Auth*, Incluir *Service Token* `axtra-pc`.
4. El Client ID va en el servidor como `CF_ACCESS_SERVICIO_ID`; los dos van en el `.env` del PC (Parte H).

## Parte F. Instalar Axtra en el servidor

Conectado por SSH al servidor:
```bash
curl -fsSLO https://raw.githubusercontent.com/felipemerchanhenao19-cmyk/Axtra/main/servidor/despliegue/instalar_servidor.sh
bash instalar_servidor.sh
```
(Si el repositorio es privado y `curl` no puede descargarlo, copia el archivo desde GitHub y pégalo con `nano instalar_servidor.sh`.)

El instalador:
1. Instala Docker.
2. Te muestra una **llave** para agregar en GitHub → *Axtra → Settings → Deploy keys* (sin permiso de escritura).
3. Descarga Axtra y abre el archivo de claves: pega las de la Parte A, `TUNNEL_TOKEN`, `CF_ACCESS_EQUIPO`, `CF_ACCESS_AUD` y `CF_ACCESS_SERVICIO_ID`.
4. Arranca Axtra y el túnel.
5. Programa las **actualizaciones automáticas** (cada 10 minutos revisa GitHub) y una **copia de seguridad diaria** de tus datos (en `/opt/axtra-respaldos`, guarda 14 días).
6. Cierra todos los puertos menos SSH.

## Parte G. En tu celular (Samsung A32)

1. Abre tu dominio en **Chrome**. Inicia sesión con tu Google.
2. Menú ⋮ → **Agregar a pantalla de inicio** → Instalar. Queda el ícono del orbe.
3. En la app: **Yo → Notificaciones** → Permitir. Te llega una de prueba.
4. Prueba: *"¿Cómo se dice hola, cómo estás en ruso?"* y *"Recuérdame en 2 minutos tomar agua"*.

## Parte H. Conectar el Axtra del PC

En el `.env` del PC (`notepad .env`):
```
AXTRA_NUBE_URL=https://TU-DOMINIO
CF_ACCESS_CLIENT_ID=el Client ID de la Parte E
CF_ACCESS_CLIENT_SECRET=el Client Secret de la Parte E
```
Luego `.\venv\Scripts\python.exe axtra.py nube`. Debe decir **LISTO**. Desde ahí, cada vez que arranques Axtra en el PC sube tus datos solo, cada 10 minutos.

## Más adelante: activar Grok
En el servidor: `nano /opt/axtra/servidor/.env` → pega `XAI_API_KEY` (y el modelo y precios de la consola de xAI) → `cd /opt/axtra/servidor/despliegue && docker compose up -d`.

## Si algo falla
- **La página no abre:** en Cloudflare, el túnel debe decir *Healthy*. En el servidor: `cd /opt/axtra/servidor/despliegue && docker compose logs -f`.
- **"No tengo un cerebro disponible":** revisa las claves en `/opt/axtra/servidor/.env` y reinicia con `docker compose up -d`.
- **El PC dice que la nube rechazó el acceso:** revisa el Client ID/Secret y que la Política 2 (Service Auth) exista.
- **Restaurar una copia:** `ls /opt/axtra-respaldos` y pídemela; te doy el comando exacto.
