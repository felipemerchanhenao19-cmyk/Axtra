"""Acceso: solo entra tu cuenta de Google, verificada por Cloudflare Access.

Cloudflare Access pone la página detrás de tu inicio de sesión de Google. Aun así, el servidor revisa en
cada petición la firma que manda Cloudflare (por si alguien intentara llegar al servidor por otro camino).
"""
import time

from . import config

_cache = {"cliente": None}


def _cliente():
    if _cache["cliente"] is None:
        from jwt import PyJWKClient

        _cache["cliente"] = PyJWKClient(
            f"https://{config.CF_ACCESS_EQUIPO}.cloudflareaccess.com/cdn-cgi/access/certs", cache_keys=True)
    return _cache["cliente"]


def configurado() -> bool:
    return bool(config.CF_ACCESS_EQUIPO and config.CF_ACCESS_AUD and config.CORREO_PERMITIDO)


def verificar(token: str) -> str:
    """Devuelve el correo si el token es válido y es el tuyo. Lanza PermissionError si no."""
    import jwt

    if not token:
        raise PermissionError("sin sesión")
    try:
        clave = _cliente().get_signing_key_from_jwt(token).key
        datos = jwt.decode(token, clave, algorithms=["RS256"], audience=config.CF_ACCESS_AUD,
                           issuer=f"https://{config.CF_ACCESS_EQUIPO}.cloudflareaccess.com",
                           options={"require": ["exp", "iat", "aud", "iss"]}, leeway=30)
    except jwt.PyJWTError as e:
        raise PermissionError(f"sesión inválida ({type(e).__name__})")
    correo = str(datos.get("email", "")).lower()
    servicio = str(datos.get("common_name", ""))
    if not correo and config.CF_SERVICIO_ID and servicio == config.CF_SERVICIO_ID:
        return "pc"            # el Axtra del PC, con su token de servicio
    if not correo or correo != config.CORREO_PERMITIDO:
        raise PermissionError("cuenta no autorizada")
    if datos.get("exp", 0) < time.time() - 30:
        raise PermissionError("sesión vencida")
    return correo


def usuario_de(headers: dict, cookies: dict) -> str:
    if config.MODO_DESARROLLO:
        return config.CORREO_PERMITIDO or "desarrollo"
    if not configurado():
        raise PermissionError("falta configurar el acceso (Cloudflare Access)")
    token = headers.get("cf-access-jwt-assertion") or cookies.get("CF_Authorization", "")
    return verificar(token)
