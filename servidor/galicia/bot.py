"""El bot de Telegram de la hacienda: recibe texto, notas de voz, fotos y archivos, y los botones."""
import logging
import threading
import time
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from . import agente, alertas, cerebro, config, db, documentos, excel, herramientas, telegram

log = logging.getLogger("galicia")
_candados = defaultdict(threading.Lock)       # un mensaje a la vez por chat (así no se cruzan las respuestas)

AYUDA = f"""👋 Soy el asistente de la *{config.NOMBRE}*. Puedes escribirme o mandarme notas de voz como le hablarías a un contador:

• «Pagué 4 jornales a 70 mil para desyerbar el lote 2»
• «Compré 3 bultos de sal a 85 mil con la Visa Bancolombia»
• «Hoy salieron 320 litros de leche»
• «Vendimos 180 bultos del lote El Alto a 95 mil»
• «Vacuné la vaca 15 contra aftosa»
• «Registra la cuota del crédito Finagro: 2.300.000 cada 6 meses, la próxima el 20 de marzo»
• «¿Cuánto llevamos gastado en papa este año?»

📸 *Facturas:* mándame la foto (bien derecha y con luz), el PDF o el XML/ZIP de la factura electrónica.
💳 *Extractos:* mándame el PDF del extracto de cada tarjeta cada mes y yo saco la fecha de pago, el mínimo y las cuotas.
⏰ Cada mañana te aviso lo que está por vencer.

Comandos: /pendientes /resumen /tarjetas /excel /deshacer"""

BOTONES_ACTIVIDAD = [("🥔 Papa", "papa"), ("🐄 Ganado", "ganado"), ("🥛 Leche", "leche"), ("🌾 General", "general"), ("🏠 Personal", "personal")]


def botones_factura(pid: int, d: dict) -> list:
    actual = "personal" if d.get("ambito") == "personal" else d.get("actividad")
    marcar = lambda t, v: ("• " + t + " •" if v == actual else t, f"a:{pid}:{v}")  # noqa: E731
    return [[marcar(*b) for b in BOTONES_ACTIVIDAD[:3]], [marcar(*b) for b in BOTONES_ACTIVIDAD[3:]],
            [("✅ Guardar", f"g:{pid}"), ("❌ Descartar", f"x:{pid}")]]


def botones_extracto(pid: int, d: dict) -> list:
    filas = [[("✅ Guardar pagos y cuotas", f"e:{pid}:0")]]
    if d.get("nuevos"):
        filas.append([(f"📥 Guardar e importar {d['nuevos']} compras", f"e:{pid}:1")])
    filas.append([("❌ Descartar", f"x:{pid}")])
    return filas


def boton_deshacer(acciones: list) -> list:
    return [[("↩️ Deshacer", f"u:{acciones[-1]}")]] if acciones else None


def usuario(u: dict) -> str:
    return config.USUARIOS.get(u.get("id"))


# ---------------- Mensajes ----------------
def atender(update: dict):
    if "callback_query" in update:
        return atender_boton(update["callback_query"])
    m = update.get("message")
    if not m or m.get("chat", {}).get("type") != "private":
        return
    chat, quien = m["chat"]["id"], usuario(m.get("from", {}))
    if not quien:
        telegram.enviar(chat, f"Hola. Este asistente es privado de la {config.NOMBRE}.\n"
                              f"Tu número de Telegram es `{m['from']['id']}`: pásaselo al administrador si debes tener acceso.")
        return
    with _candados[chat]:
        try:
            _atender_mensaje(m, chat, quien)
        except Exception as e:                       # nunca dejar a la persona sin respuesta
            log.exception("error atendiendo mensaje")
            telegram.enviar(chat, f"😕 Algo falló: {e}\nIntenta de nuevo en un momento.", markdown=False)


def _atender_mensaje(m: dict, chat: int, quien: str):
    texto = (m.get("text") or "").strip()
    if texto.startswith("/"):
        return comando(texto.split()[0].split("@")[0].lower(), chat, quien)
    if "voice" in m or "audio" in m:
        telegram.escribiendo(chat)
        archivo = m.get("voice") or m.get("audio")
        audio, _ = telegram.descargar(archivo["file_id"])
        try:
            texto = cerebro.transcribir(audio)
        except cerebro.SinCerebro as e:
            telegram.enviar(chat, f"No pude escuchar la nota de voz ahora ({e}). Escríbemelo, por favor.", markdown=False)
            return
        if not texto:
            telegram.enviar(chat, "No entendí la nota de voz. ¿Me la repites?")
            return
        telegram.enviar(chat, f"🎙️ _{texto}_")
        return conversar(texto, chat, quien, origen="voz")
    if "photo" in m:
        foto = m["photo"][-1]                       # la de mayor resolución
        return documento(foto["file_id"], "foto.jpg", "image/jpeg", chat, quien, m.get("caption", ""))
    if "document" in m:
        d = m["document"]
        nombre, mime = d.get("file_name", "archivo"), d.get("mime_type", "")
        if not (mime.startswith("image/") or nombre.lower().endswith((".pdf", ".xml", ".zip", ".jpg", ".jpeg", ".png"))):
            telegram.enviar(chat, "Ese tipo de archivo no lo sé leer. Mándame foto, PDF, XML o ZIP de la factura.")
            return
        if d.get("file_size", 0) > 19_000_000:
            telegram.enviar(chat, "El archivo es muy pesado (máximo 19 MB).")
            return
        return documento(d["file_id"], nombre, mime, chat, quien, m.get("caption", ""))
    if texto:
        return conversar(texto, chat, quien)


def conversar(texto: str, chat: int, quien: str, origen: str = "chat"):
    telegram.escribiendo(chat)
    try:
        r = agente.responder(texto, quien, chat, origen)
    except cerebro.SinCerebro as e:
        log.warning("sin cerebro: %s", e)
        db.guardar_pendiente(chat, "mensaje", {"texto": texto, "usuario": quien, "origen": origen})
        telegram.enviar(chat, "📥 La IA no está disponible en este momento. Guardé tu mensaje y lo registro apenas vuelva "
                              "(te aviso). Mientras tanto funcionan /pendientes, /resumen y /tarjetas.")
        return
    telegram.enviar(chat, r["texto"], botones=boton_deshacer(r["acciones"]))
    for pid in dict.fromkeys(r["refrescar"]):
        p = db.pendiente(pid)
        if p:
            telegram.enviar(chat, documentos.tarjeta_factura(p["datos"]), botones=botones_factura(pid, p["datos"]))
    for ruta in r["archivos"]:
        telegram.enviar_archivo(chat, ruta, "📗 Libro de la hacienda")


def documento(file_id: str, nombre: str, mime: str, chat: int, quien: str, nota: str = ""):
    telegram.escribiendo(chat)
    contenido, ruta_tg = telegram.descargar(file_id)
    extension = (nombre.rsplit(".", 1)[-1] if "." in nombre else ruta_tg.rsplit(".", 1)[-1]).lower()
    soporte = documentos.guardar_soporte(contenido, extension)
    telegram.enviar(chat, "🔎 Leyendo el documento…")
    try:
        leido = documentos.leer(contenido, nombre, mime)
    except cerebro.SinCerebro as e:
        log.warning("sin cerebro para documento: %s", e)
        db.guardar_pendiente(chat, "archivo", {"soporte": soporte, "nombre": nombre, "mime": mime, "usuario": quien, "nota": nota})
        telegram.enviar(chat, "📥 Guardé el documento, pero la IA no está disponible ahora. Lo leo apenas vuelva y te muestro la factura.")
        return
    except PermissionError:
        telegram.enviar(chat, "🔒 El PDF tiene clave. Pídele al administrador que la agregue (GALICIA_CLAVES_PDF) "
                              "o mándame una foto o captura del extracto.")
        return
    except Exception as e:
        log.exception("no se pudo leer el documento")
        telegram.enviar(chat, f"No pude leer ese documento ({e}). Prueba con una foto más clara.", markdown=False)
        return
    mostrar_lectura(leido, chat, soporte, nota, quien)


def mostrar_lectura(leido: dict, chat: int, soporte: str, nota: str, quien: str):
    p = documentos.preparar(leido, chat, soporte)
    if p["tipo"] == "factura":
        texto = documentos.tarjeta_factura(p["datos"])
        if p["aviso"]:
            texto = p["aviso"] + "\n\n" + texto
        telegram.enviar(chat, texto, botones=botones_factura(p["id"], p["datos"]))
        if nota:                                     # lo que escribieron junto a la foto: «pagada con la visa, es del lote 3»
            conversar(f"Sobre la factura que acabo de enviar: {nota}", chat, quien)
    elif p["tipo"] == "extracto":
        telegram.enviar(chat, documentos.tarjeta_extracto(p["datos"]), botones=botones_extracto(p["id"], p["datos"]))
    else:
        telegram.enviar(chat, "No parece una factura ni un extracto. Si es un gasto, cuéntame qué fue y cuánto costó.")


# ---------------- Comandos ----------------
def comando(cmd: str, chat: int, quien: str):
    if cmd in ("/start", "/ayuda", "/help"):
        telegram.enviar(chat, f"Hola, {quien}.\n\n" + AYUDA)
    elif cmd == "/pendientes":
        texto, botones = alertas.texto_pendientes(30)
        telegram.enviar(chat, texto, botones=botones)
    elif cmd == "/resumen":
        telegram.enviar(chat, alertas.texto_resumen())
    elif cmd == "/tarjetas":
        telegram.enviar(chat, alertas.texto_tarjetas())
    elif cmd == "/excel":
        telegram.escribiendo(chat)
        hoy = db.hoy()
        ruta = excel.generar(hoy.replace(month=1, day=1).isoformat(), hoy.isoformat())
        telegram.enviar_archivo(chat, str(ruta), f"📗 Libro de la hacienda {hoy.year}")
    elif cmd == "/deshacer":
        hecho = db.deshacer(usuario=quien)
        telegram.enviar(chat, f"↩️ Deshice: {hecho}" if hecho else "No hay nada tuyo para deshacer.", markdown=False)
    elif cmd == "/olvidar":
        agente.olvidar(chat)
        telegram.enviar(chat, "Listo, empecemos de cero la conversación (los registros siguen guardados).")
    else:
        telegram.enviar(chat, "No conozco ese comando. Escribe /ayuda.")


# ---------------- Botones ----------------
def atender_boton(q: dict):
    quien = usuario(q.get("from", {}))
    if not quien:
        telegram.contestar_boton(q["id"], "No autorizado")
        return
    chat = q["message"]["chat"]["id"]
    mensaje = q["message"]["message_id"]
    partes = (q.get("data") or "").split(":")
    ctx = {"usuario": quien, "chat": chat}
    with _candados[chat]:
        try:
            _boton(partes, q, chat, mensaje, quien, ctx)
        except ValueError as e:
            telegram.contestar_boton(q["id"], str(e))
            telegram.enviar(chat, f"⚠️ {e}", markdown=False)
        except Exception as e:
            log.exception("error en botón")
            telegram.contestar_boton(q["id"], f"Falló: {e}")


def _boton(partes, q, chat, mensaje, quien, ctx):
    accion = partes[0]
    if accion == "a":                                  # cambiar actividad / personal de la factura
        pid, valor = int(partes[1]), partes[2]
        p = db.pendiente(pid)
        if not p:
            raise ValueError("esa factura ya no está pendiente")
        d = p["datos"]
        if valor == "personal":
            d["ambito"], d["actividad"] = "personal", "general"
        else:
            d["ambito"], d["actividad"] = "hacienda", valor
        db.cambiar_pendiente(pid, d)
        telegram.contestar_boton(q["id"], "Cambiado")
        telegram.editar(chat, mensaje, documentos.tarjeta_factura(d), botones_factura(pid, d))
    elif accion == "g":
        r = documentos.guardar_factura(int(partes[1]), ctx)
        telegram.contestar_boton(q["id"], "Guardada")
        telegram.editar(chat, mensaje, r["texto"], boton_deshacer([r["accion"]]))
    elif accion == "e":
        r = documentos.guardar_extracto(int(partes[1]), ctx, importar=partes[2] == "1")
        telegram.contestar_boton(q["id"], "Guardado")
        telegram.editar(chat, mensaje, r["texto"], boton_deshacer([r["accion"]]))
    elif accion == "x":
        db.borrar_pendiente(int(partes[1]))
        telegram.contestar_boton(q["id"], "Descartado")
        telegram.editar(chat, mensaje, "❌ Descartado.")
    elif accion == "u":
        hecho = db.deshacer(accion_id=int(partes[1]))
        telegram.contestar_boton(q["id"], "Deshecho" if hecho else "Ya estaba deshecho")
        if hecho:
            telegram.editar(chat, mensaje, f"↩️ Deshecho: {hecho}")
    elif accion == "p":                                # «Ya pagué» desde una alerta
        o = db.fila("SELECT * FROM obligaciones WHERE id=? AND activa=1", (int(partes[1]),))
        if not o:
            raise ValueError("ese pago ya estaba registrado")
        if not o["monto"]:
            telegram.contestar_boton(q["id"])
            telegram.enviar(chat, f"¿Cuánto pagaste de «{o['nombre']}»? Escríbeme, por ejemplo: «pagué 850 mil de {o['nombre']}».",
                            markdown=False)
            return
        r = herramientas.pagar_obligacion(ctx, obligacion=str(o["id"]))
        telegram.contestar_boton(q["id"], "Pago registrado")
        siguiente = f" Próximo: {r['proximo_vencimiento']}." if r.get("proximo_vencimiento") else " ¡Deuda terminada! 🎉"
        telegram.enviar(chat, f"✅ Registré el pago de {o['nombre']}: {r['pagado']}.{siguiente}",
                        botones=boton_deshacer(ctx.get("acciones", [])), markdown=False)
    else:
        telegram.contestar_boton(q["id"])


# ---------------- Lo que quedó en cola cuando la IA no estaba ----------------
def reintentar_cola():
    if not cerebro.disponible():
        return
    for p in db.filas("SELECT * FROM pendientes WHERE tipo IN ('mensaje','archivo') ORDER BY id LIMIT 10"):
        p = db.pendiente(p["id"])
        chat, d = p["chat"], p["datos"]
        with _candados[chat]:
            try:
                if p["tipo"] == "mensaje":
                    r = agente.responder(d["texto"], d["usuario"], chat, d.get("origen", "chat"))
                    db.borrar_pendiente(p["id"])
                    telegram.enviar(chat, f"📥 Sobre tu mensaje «{d['texto'][:80]}»:\n{r['texto']}",
                                    botones=boton_deshacer(r["acciones"]))
                else:
                    contenido = (config.DATA_DIR / d["soporte"]).read_bytes()
                    leido = documentos.leer(contenido, d["nombre"], d["mime"])
                    db.borrar_pendiente(p["id"])
                    telegram.enviar(chat, "📥 Ya pude leer el documento que mandaste antes:")
                    mostrar_lectura(leido, chat, d["soporte"], d.get("nota", ""), d["usuario"])
            except cerebro.SinCerebro:
                return                                  # sigue sin IA: se intenta más tarde
            except Exception:
                log.exception("no se pudo procesar un pendiente de la cola")
                db.borrar_pendiente(p["id"])


# ---------------- Alertas de la mañana ----------------
def enviar_a_todos(texto: str, botones: list = None, archivo: str = None):
    for chat in config.USUARIOS:
        try:
            telegram.enviar(chat, texto, botones=botones)
            if archivo:
                telegram.enviar_archivo(chat, archivo, "📗 Libro del mes")
        except Exception:
            log.exception("no se pudo avisar a %s", chat)


def tarea_diaria():
    hoy = db.hoy().isoformat()
    hora = datetime.now(ZoneInfo(config.ZONA_HORARIA)).hour
    if hora < config.HORA_ALERTAS or db.leer_estado("alertas_dia") == hoy:
        return
    db.poner_estado("alertas_dia", hoy)
    texto, botones = alertas.revision_diaria()
    if texto:
        enviar_a_todos(texto, botones)
    mensual = alertas.informe_mensual()
    if mensual:
        texto, desde, hasta = mensual
        enviar_a_todos(texto, archivo=str(excel.generar(desde, hasta)))


def vigilante():
    """Hilo de fondo: alertas de la mañana y reintentos de la cola."""
    while True:
        for tarea in (tarea_diaria, reintentar_cola):
            try:
                tarea()
            except Exception:
                log.exception("falló %s", tarea.__name__)
        time.sleep(120)


def correr():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s galicia %(levelname)s %(message)s")
    if not config.TELEGRAM_TOKEN:
        raise SystemExit("Falta GALICIA_TELEGRAM_TOKEN en el .env (créalo con @BotFather en Telegram).")
    if not config.USUARIOS:
        log.warning("GALICIA_USUARIOS está vacío: el bot no le responderá a nadie (escríbele y te dirá tu número).")
    db.conn()
    try:
        telegram.configurar_comandos()
    except Exception:
        log.exception("no se pudieron configurar los comandos")
    threading.Thread(target=vigilante, daemon=True).start()
    desde = 0
    log.info("Galicia escuchando en Telegram (%d usuarios)", len(config.USUARIOS))
    while True:
        try:
            for u in telegram.actualizaciones(desde):
                desde = u["update_id"] + 1
                threading.Thread(target=atender, args=(u,), daemon=True).start()
        except Exception as e:
            log.warning("Telegram: %s", e)
            time.sleep(5)
