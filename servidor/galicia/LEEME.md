# Galicia: el asistente contable de la Hacienda La Galicia

Es un bot de **Telegram** que lleva la contabilidad y la administración de la hacienda: gastos e ingresos, tarjetas de crédito, cuotas y créditos, el cultivo de papa, el ganado y la leche. Cada mañana avisa lo que está por vencer. Vive en el mismo servidor de Axtra (otro contenedor) y piensa con **Groq**, usando la misma clave.

## Cómo se usa (desde el celular)

| Qué | Cómo |
|---|---|
| Registrar un gasto o ingreso | Escribir o mandar una nota de voz: *«Pagué 4 jornales a 70 mil para desyerbar el lote 2»* |
| Factura de papel | Mandar la **foto**. El bot muestra lo que leyó y los botones 🥔 Papa · 🐄 Ganado · 🥛 Leche · 🌾 General · 🏠 Personal · ✅ Guardar |
| Factura electrónica | Reenviar el **XML o el ZIP** del correo: se lee exacto, sin IA |
| Extracto de tarjeta | Mandar el **PDF** cada mes. Saca la fecha límite, el pago total, el mínimo, el cupo y las compras a cuotas, y deja programado el aviso |
| Créditos y vencimientos | *«Registra la cuota del crédito Finagro: 2.300.000 cada 6 meses, la próxima el 20 de marzo»*, *«el predial vence el 30 de abril»* |
| Papa | *«Sembramos el lote El Alto, 2 hectáreas de pastusa»*, *«Fumigamos el lote 2 con Curzate, toca otra vez en 8 días»*, *«Salieron 180 bultos del lote 2 a 95 mil»* |
| Leche | *«Hoy 320 litros»*, *«Colanta pagó 6.100.000 de la primera quincena, 4.450 litros»* (lo compara con lo anotado) |
| Ganado | *«Inseminamos la vaca 15»* (avisa el parto a los 283 días), *«Vacunamos todo el hato contra aftosa»*, *«Vendimos el novillo 32 en 2,8 millones»* |
| Preguntar | *«¿Cuánto llevamos gastado en papa este año?»*, *«¿Cuánto pagamos al veterinario en octubre?»* |
| Corregir | Botón **↩️ Deshacer** debajo de cada registro, o `/deshacer` |

Comandos: `/pendientes` · `/resumen` · `/tarjetas` · `/excel` · `/deshacer` · `/ayuda` (los cuatro primeros funcionan aunque la IA esté caída).

**Alertas:** cada mañana (7 a. m.) avisa los pagos que vencen en 7, 3 y 1 días y el mismo día; lo vencido lo recuerda a diario hasta que alguien toque **✅ Ya pagué**. También avisa las labores de la papa que tocan, los partos esperados, las vacunas pendientes, las tarjetas que pasan del 90 % del cupo y si falta anotar la leche de ayer. El día 1 de cada mes manda el cierre del mes anterior con el Excel.

**El Excel** (`/excel`) trae las hojas Inicio, Resumen mensual, Movimientos, Por categoría, Vencimientos, Tarjetas, Papa, Labores, Ganado, Eventos ganado, Leche y Pagos de leche. Es lo que se le pasa al contador.

## Cómo piensa
- **La IA propone y la persona confirma:** las facturas y los extractos quedan pendientes hasta que alguien toque Guardar.
- **Aprende:** si una factura de un proveedor se guarda como "ganado", las siguientes de ese NIT llegan ya clasificadas así.
- **No duplica:** avisa si una factura ya estaba registrada (por CUFE o NIT y número), y al importar un extracto se salta las compras que ya estaban.
- **Separa hacienda y personal** en todo: resumen, Excel y alertas.
- **Pago de tarjeta ≠ gasto:** las compras con la tarjeta ya son el gasto; pagar la tarjeta solo mueve la fecha del próximo pago. Las cuotas de créditos, impuestos y seguros sí cuentan como gasto.
- **Si Groq no responde** (sin cupo o caído), el mensaje o la foto quedan en cola y se procesan solos apenas vuelva.

## Ponerlo a funcionar

1. **Crear el bot:** en Telegram, buscar **@BotFather** → `/newbot` → nombre `Hacienda La Galicia` → usuario, por ejemplo `LaGaliciaBot`. Copiar el **token**.
2. **En el `.env` del servidor** (`nano /opt/axtra/servidor/.env`):
   ```
   GALICIA_TELEGRAM_TOKEN=el token de BotFather
   GALICIA_USUARIOS=
   ```
   (la `GROQ_API_KEY` ya está).
3. **Arrancar:** `cd /opt/axtra/servidor/despliegue && docker compose up -d --build galicia`
4. **Dar acceso a la pareja:** que cada uno abra el bot en Telegram y le escriba "hola". El bot responde con su **número de Telegram**. Ponerlos en el `.env`:
   ```
   GALICIA_USUARIOS=123456789:Carlos,987654321:María
   ```
   y reiniciar: `docker compose up -d galicia`. Solo esos números pueden usarlo.
5. **Extractos con clave:** si los PDF del banco piden contraseña (Bancolombia suele usar la cédula), agregarlas: `GALICIA_CLAVES_PDF=12345678,87654321`.
6. **Primeros datos:** registrar las tarjetas (mejor: mandar el último extracto de cada una), los créditos con su próxima cuota, los lotes sembrados y el ganado.

Las actualizaciones llegan solas desde GitHub (como Axtra) y la copia de seguridad diaria incluye la base de datos y las fotos de las facturas (`/opt/axtra-respaldos/galicia-FECHA.tgz`).

Para ver qué está haciendo: `docker compose logs -f galicia`

## Archivos
- `bot.py`: mensajes, fotos, notas de voz, botones, cola y alertas de la mañana.
- `agente.py`: la conversación con la IA (Groq) y sus reglas.
- `herramientas.py`: todo lo que el asistente sabe hacer (registrar, pagar, consultar...).
- `documentos.py`: facturas (foto, PDF, XML DIAN, ZIP) y extractos.
- `alertas.py`: lo que vence y los textos de /pendientes, /resumen y /tarjetas.
- `excel.py`: el libro de Excel.
- `db.py`: la base de datos SQLite (con "deshacer").
- `cerebro.py`: Groq (texto, visión y oído), con modelos de respaldo.
- `telegram.py`: conexión con Telegram (sin librerías extra).

Pruebas: `python -m pytest servidor/tests/test_galicia.py`
