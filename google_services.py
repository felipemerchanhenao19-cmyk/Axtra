"""Google Calendar y Gmail.

Configuración (una sola vez): ver LEEME.md → "Conectar Google". Luego:
    python axtra.py google
Se abre el navegador, das permiso y queda guardado en data/google_token.json.

Permisos que pide: ver/crear eventos del calendario, leer correos y crear BORRADORES.
Axtra nunca envía correos por su cuenta: los deja en borradores para que tú los revises.
"""
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

from config import BASE_DIR, DATA_DIR, TIMEZONE

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
CREDS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = DATA_DIR / "google_token.json"
CAL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
GMAIL = "https://gmail.googleapis.com/gmail/v1/users/me"
_session = None


def connect_interactive() -> None:
    """Primera conexión: abre el navegador para dar permiso."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not CREDS_PATH.exists():
        raise SystemExit("Falta credentials.json en la carpeta axtra. Sigue la guía del LEEME.")
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    print("Google conectado. Ya puedes iniciar Axtra.")


def available() -> bool:
    return TOKEN_PATH.exists()


def _s():
    global _session
    if _session is None:
        from google.auth.transport.requests import AuthorizedSession, Request
        from google.oauth2.credentials import Credentials

        if not TOKEN_PATH.exists():
            raise RuntimeError("Google no está conectado. Ejecuta: python axtra.py google")
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        if not creds.valid and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        _session = AuthorizedSession(creds)
    return _session


def _get(url, **params):
    r = _s().get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def _tz():
    return ZoneInfo(TIMEZONE)


# ---------- Calendario ----------
def agenda(horas: float = 24, desde_ahora: bool = True) -> dict:
    now = datetime.now(_tz())
    start = now if desde_ahora else now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=float(horas))
    data = _get(CAL, timeMin=start.isoformat(), timeMax=end.isoformat(),
                singleEvents="true", orderBy="startTime", maxResults=20)
    eventos = []
    for e in data.get("items", []):
        st = e["start"].get("dateTime") or e["start"].get("date")
        hora = datetime.fromisoformat(st).astimezone(_tz()).strftime("%I:%M %p") if "T" in st else "todo el día"
        eventos.append({"hora": hora, "evento": e.get("summary", "(sin título)"),
                        "lugar": e.get("location", "")})
    return {"eventos": eventos or ["No hay eventos en ese periodo."]}


def crear_evento(titulo: str, fecha: str, hora: str, duracion_min: float = 60, descripcion: str = "") -> dict:
    """fecha: AAAA-MM-DD, hora: HH:MM (24 h)."""
    start = datetime.fromisoformat(f"{fecha}T{hora}").replace(tzinfo=_tz())
    end = start + timedelta(minutes=float(duracion_min))
    body = {"summary": titulo, "description": descripcion,
            "start": {"dateTime": start.isoformat(), "timeZone": TIMEZONE},
            "end": {"dateTime": end.isoformat(), "timeZone": TIMEZONE}}
    r = _s().post(CAL, json=body, timeout=20)
    r.raise_for_status()
    return {"ok": True, "evento": titulo, "inicio": start.strftime("%Y-%m-%d %I:%M %p")}


# ---------- Gmail ----------
def correos(buscar: str = "is:unread newer_than:2d", maximo: int = 8) -> dict:
    """buscar usa la sintaxis de Gmail: is:unread, from:alguien, subject:factura, newer_than:1d..."""
    data = _get(f"{GMAIL}/messages", q=buscar, maxResults=int(maximo))
    out = []
    for m in data.get("messages", []):
        msg = _get(f"{GMAIL}/messages/{m['id']}", format="metadata",
                   metadataHeaders=["From", "Subject", "Date"])
        h = {x["name"]: x["value"] for x in msg["payload"].get("headers", [])}
        out.append({"de": h.get("From", ""), "asunto": h.get("Subject", ""),
                    "fecha": h.get("Date", ""), "resumen": msg.get("snippet", "")[:200]})
    return {"correos": out or ["No hay correos con ese filtro."]}


def borrador_correo(para: str, asunto: str, mensaje: str) -> dict:
    msg = MIMEText(mensaje, "plain", "utf-8")
    msg["to"], msg["subject"] = para, asunto
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    r = _s().post(f"{GMAIL}/drafts", json={"message": {"raw": raw}}, timeout=20)
    r.raise_for_status()
    return {"ok": True, "nota": "Quedó en tus BORRADORES de Gmail para que lo revises y lo envíes."}


TOOL_SCHEMAS = [
    {"name": "agenda", "description": "Eventos del Google Calendar de Felipe en las próximas horas (por defecto 24).",
     "input_schema": {"type": "object", "properties": {"horas": {"type": "number"}}}},
    {"name": "crear_evento", "description": "Crea un evento en Google Calendar. fecha AAAA-MM-DD, hora HH:MM (24 h).",
     "input_schema": {"type": "object", "properties": {"titulo": {"type": "string"}, "fecha": {"type": "string"}, "hora": {"type": "string"}, "duracion_min": {"type": "number"}, "descripcion": {"type": "string"}}, "required": ["titulo", "fecha", "hora"]}},
    {"name": "correos", "description": "Lee correos de Gmail. 'buscar' usa sintaxis de Gmail (ej: 'is:unread newer_than:1d', 'from:banco').",
     "input_schema": {"type": "object", "properties": {"buscar": {"type": "string"}, "maximo": {"type": "integer"}}}},
    {"name": "borrador_correo", "description": "Redacta un correo y lo guarda en BORRADORES de Gmail (nunca lo envía).",
     "input_schema": {"type": "object", "properties": {"para": {"type": "string"}, "asunto": {"type": "string"}, "mensaje": {"type": "string"}}, "required": ["para", "asunto", "mensaje"]}},
]
FUNCS = {"agenda": agenda, "crear_evento": crear_evento, "correos": correos, "borrador_correo": borrador_correo}
