"""Cliente mínimo de la API de Telegram (sin librerías extra). El bot pregunta a Telegram por mensajes nuevos
(long polling): no hay que abrir puertos ni tocar el túnel de Cloudflare."""
import json

import requests

from . import config

API = "https://api.telegram.org"


class ErrorTelegram(RuntimeError):
    pass


def _url(metodo: str) -> str:
    return f"{API}/bot{config.TELEGRAM_TOKEN}/{metodo}"


def llamar(metodo: str, espera_http: float = 30, archivos: dict = None, **datos):
    datos = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in datos.items() if v is not None}
    r = requests.post(_url(metodo), data=datos, files=archivos, timeout=espera_http)
    try:
        cuerpo = r.json()
    except ValueError:
        raise ErrorTelegram(f"{metodo}: {r.status_code}")
    if not cuerpo.get("ok"):
        raise ErrorTelegram(f"{metodo}: {cuerpo.get('description')}")
    return cuerpo["result"]


def actualizaciones(desde: int, espera: int = 50) -> list:
    return llamar("getUpdates", espera_http=espera + 10, offset=desde, timeout=espera,
                  allowed_updates=["message", "callback_query"])


def teclado(filas: list) -> dict:
    """filas: [[("Texto", "dato"), ...], ...] → botones debajo del mensaje."""
    return {"inline_keyboard": [[{"text": t, "callback_data": d[:64]} for t, d in fila] for fila in filas]}


def enviar(chat: int, texto: str, botones: list = None, markdown: bool = True):
    for i in range(0, max(1, len(texto)), 4000):           # Telegram corta en 4096 caracteres
        parte = texto[i:i + 4000]
        ultimo = i + 4000 >= len(texto)
        try:
            return_ = llamar("sendMessage", chat_id=chat, text=parte, parse_mode="Markdown" if markdown else None,
                             reply_markup=teclado(botones) if botones and ultimo else None)
        except ErrorTelegram as e:
            if markdown and "parse" in str(e).lower():       # un * o _ suelto rompe el formato: mandarlo plano
                return_ = llamar("sendMessage", chat_id=chat, text=parte,
                                 reply_markup=teclado(botones) if botones and ultimo else None)
            else:
                raise
    return return_


def editar(chat: int, mensaje: int, texto: str, botones: list = None):
    try:
        return llamar("editMessageText", chat_id=chat, message_id=mensaje, text=texto[:4000], parse_mode="Markdown",
                      reply_markup=teclado(botones) if botones else None)
    except ErrorTelegram as e:
        if "not modified" in str(e):
            return None
        return llamar("editMessageText", chat_id=chat, message_id=mensaje, text=texto[:4000],
                      reply_markup=teclado(botones) if botones else None)


def contestar_boton(id_: str, texto: str = ""):
    try:
        llamar("answerCallbackQuery", callback_query_id=id_, text=texto[:190] or None)
    except ErrorTelegram:
        pass


def escribiendo(chat: int):
    try:
        llamar("sendChatAction", chat_id=chat, action="typing", espera_http=10)
    except (ErrorTelegram, requests.RequestException):
        pass


def enviar_archivo(chat: int, ruta: str, texto: str = ""):
    with open(ruta, "rb") as f:
        return llamar("sendDocument", espera_http=120, archivos={"document": (ruta.rsplit("/", 1)[-1], f)}, chat_id=chat,
                      caption=texto[:1000] or None)


def descargar(file_id: str) -> tuple:
    """Baja un archivo que mandaron al chat. Devuelve (bytes, ruta_en_telegram)."""
    info = llamar("getFile", file_id=file_id)
    r = requests.get(f"{API}/file/bot{config.TELEGRAM_TOKEN}/{info['file_path']}", timeout=120)
    r.raise_for_status()
    return r.content, info["file_path"]


def configurar_comandos():
    llamar("setMyCommands", commands=[
        {"command": "pendientes", "description": "Lo que vence pronto"},
        {"command": "resumen", "description": "Ingresos y gastos del mes"},
        {"command": "tarjetas", "description": "Tarjetas, cupos y cuotas"},
        {"command": "excel", "description": "Libro de Excel del año"},
        {"command": "deshacer", "description": "Borrar mi último registro"},
        {"command": "ayuda", "description": "Qué puedo hacer"},
    ])
