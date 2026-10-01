"""Notificaciones al celular (Web Push). Las llaves se crean solas la primera vez en la carpeta de datos."""
import base64
import json

from . import config, db

LLAVE = config.DATA_DIR / "push_privada.pem"


def _llaves():
    from cryptography.hazmat.primitives import serialization
    from py_vapid import Vapid

    if not LLAVE.exists():
        v = Vapid()
        v.generate_keys()
        v.save_key(str(LLAVE))
    v = Vapid.from_file(str(LLAVE))
    crudo = v.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return v, base64.urlsafe_b64encode(crudo).decode().rstrip("=")


def clave_publica() -> str:
    return _llaves()[1]


def enviar(titulo: str, cuerpo: str, url: str = "/") -> int:
    """Envía a todos tus teléfonos suscritos. Devuelve a cuántos llegó."""
    from pywebpush import WebPushException, webpush

    _llaves()
    enviados = 0
    for sub in db.suscripciones():
        try:
            webpush(subscription_info=sub, data=json.dumps({"titulo": titulo, "cuerpo": cuerpo, "url": url}),
                    vapid_private_key=str(LLAVE),
                    vapid_claims={"sub": f"mailto:{config.CORREO_PERMITIDO or 'axtra@example.com'}"}, ttl=3600)
            enviados += 1
        except WebPushException as e:
            if e.response is not None and e.response.status_code in (404, 410):
                db.borrar_suscripcion(sub["endpoint"])   # el teléfono ya no la usa
            else:
                print(f"  (notificación falló: {e})")
    return enviados
