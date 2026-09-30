"""Axtra en el navegador: una página estilo Gemini con el mismo cerebro, memoria y herramientas.

    python axtra.py web      -> abre http://localhost:8765 en tu navegador

- Todo lo que Axtra responde lo lee en voz alta (con su misma voz).
- Crea imágenes ("crea una imagen de...") y documentos Word ("haz un documento sobre...").
- Las propuestas, bocetos y gráficas que Axtra crea con sus herramientas aparecen para descargar.
- Micrófono: le hablas desde la página y te entiende con su mismo oído.
- Por seguridad solo se abre en este PC. Para usarlo desde el celular en tu Wi-Fi:
  JARVIS_WEB_RED=1 y JARVIS_WEB_CLAVE=una_clave en el .env (el micrófono solo funciona en el PC).
"""
import hashlib
import hmac
import io
import json
import mimetypes
import os
import re
import tempfile
import threading
import time
import uuid
import wave
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from config import BASE_DIR, DATA_DIR, DOCS_DIR, USER_NAME

PORT = int(os.getenv("JARVIS_WEB_PUERTO", "8765"))
LAN = os.getenv("JARVIS_WEB_RED", "0") == "1"
PASSWORD = os.getenv("JARVIS_WEB_CLAVE", "").strip()
HOST = "0.0.0.0" if LAN else "127.0.0.1"
PAGE = BASE_DIR / "web" / "index.html"
CHATS_PATH = DATA_DIR / "web_chats.json"

_chats_lock = threading.Lock()
_brain = None
_brain_lock = threading.Lock()
_stt = None
_tts = None

# "crea una imagen de un gato astronauta", "dibújame un logo para Apex", "genera un fondo de pantalla..."
IMAGE_RE = re.compile(r"^(?:axtra,? )?(?:por favor )?(?:crea|creame|genera|generame|dibuja|dibujame|haz|hazme|"
                      r"disena|disename|pinta|pintame|quiero)\s+(?:una?\s+)?(?:nueva\s+)?(?:imagen|foto|dibujo|"
                      r"ilustracion|logo|logotipo|fondo de pantalla|poster|afiche|portada)\b")
# "haz un documento sobre...", "redacta un informe de...", "escríbeme una carta para..."
DOC_RE = re.compile(r"^(?:axtra,? )?(?:por favor )?(?:crea|creame|genera|generame|haz|hazme|redacta|redactame|"
                    r"escribe|escribeme|prepara|preparame)\s+(?:una?\s+)?(?:documento|word|informe|reporte|"
                    r"carta|guia|manual|plan|resumen en word|articulo)\b")


# ---------------- Piezas de Axtra (se cargan una vez) ----------------
def brain():
    global _brain
    with _brain_lock:
        if _brain is None:
            from brain import Brain

            _brain = Brain()
        return _brain


def stt():
    global _stt
    if _stt is None:
        from speech import STT

        _stt = STT()
    return _stt


def tts():
    """Motor de voz de Axtra (edge-tts, filtro o ElevenLabs, como en la voz). None si no carga."""
    global _tts
    if _tts is None:
        try:
            from speech import TTS

            _tts = TTS()
        except Exception as e:
            print(f"  (voz: uso la básica: {e})")
            _tts = False
    return _tts or None


# ---------------- Conversaciones guardadas ----------------
def _load_chats() -> list:
    try:
        return json.loads(CHATS_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_chats(chats: list) -> None:
    tmp = CHATS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(chats, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(CHATS_PATH)


def _add_to_chat(chat_id: str, user_text: str, reply: dict) -> str:
    with _chats_lock:
        chats = _load_chats()
        chat = next((c for c in chats if c["id"] == chat_id), None)
        if chat is None:
            chat = {"id": chat_id or uuid.uuid4().hex[:12], "titulo": user_text[:60], "mensajes": []}
            chats.insert(0, chat)
        chat["mensajes"] += [{"rol": "usuario", "texto": user_text},
                             {"rol": "axtra", **{k: reply[k] for k in ("texto", "archivos", "markdown") if k in reply}}]
        chat["actualizado"] = time.time()
        chats.sort(key=lambda c: c.get("actualizado", 0), reverse=True)
        _save_chats(chats[:200])
        return chat["id"]


# ---------------- Archivos que crea Axtra ----------------
def _snapshot() -> dict:
    return {p: p.stat().st_mtime for p in DOCS_DIR.rglob("*") if p.is_file()}


def _file_info(path: Path) -> dict:
    rel = path.resolve().relative_to(DOCS_DIR.resolve()).as_posix()
    kind = "imagen" if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp") else "archivo"
    return {"url": "/archivos/" + rel, "nombre": path.name, "tipo": kind}


def _new_files(before: dict) -> list:
    after = _snapshot()
    changed = [p for p, t in after.items() if before.get(p) != t]
    return [_file_info(p) for p in sorted(changed, key=lambda p: after[p])[-5:]]


# ---------------- Responder ----------------
def _norm(text: str) -> str:
    import quick

    return quick.norm(text)


def _speech_chunks(text: str) -> list:
    from speech import clean_for_speech, split_sentences

    clean = clean_for_speech(re.sub(r"[#|]+", " ", text))
    return split_sentences(clean) if clean else []


def _after_brain_sessions() -> str:
    """Lo que en la voz abre una sesión (dictado, clases, sincronización...) aquí se explica."""
    import aprendizaje
    import dictation
    import language
    import sync
    import voices

    note = ""
    if dictation.pending or language.pending:
        dictation.pending = language.pending = None
        note = "El dictado y las clases de idiomas funcionan por voz, señor. Pídamelos hablando."
    if sync.pending or aprendizaje.pending is not None:
        sync.pending = False
        aprendizaje.pending = None
        note = "Las sesiones de sincronización y el protocolo de aprendizaje funcionan en el Escritorio de Axtra, señor."
    voices.pending_demo = False
    return note


def _sync_history(b) -> None:
    """Toma también lo que se habló por voz mientras tanto (la voz y la web comparten memoria)."""
    import memory
    from brain import MAX_HISTORY

    b.history = memory.load_history()[-MAX_HISTORY:]


def responder(texto: str, modo: str = "auto") -> dict:
    import quick

    t = _norm(texto)
    b = brain()
    if modo == "imagen" or (modo == "auto" and IMAGE_RE.search(t)):
        import creador

        img = creador.crear_imagen(texto)
        msg = f"Listo, señor. Aquí tiene la imagen (creada con {img['fuente']})."
        with b.lock:
            _sync_history(b)
            b._remember(texto, msg)
        return {"texto": msg, "archivos": [_file_info(img["ruta"])]}

    if modo == "documento" or (modo == "auto" and DOC_RE.search(t)):
        import creador

        doc = creador.crear_documento(texto)
        msg = f"Listo, señor. Le preparé el documento «{doc['titulo']}». Puede leerlo aquí o descargarlo en Word."
        with b.lock:
            _sync_history(b)
            b._remember(texto, msg)
        return {"texto": msg, "markdown": doc["markdown"], "archivos": [_file_info(doc["ruta"])]}

    with b.lock:
        _sync_history(b)
        before = _snapshot()
        answer = b.ask(texto)
        files = _new_files(before)
    if answer == quick.SHUTDOWN:
        answer = "Desde la página no me apago, señor. Cierre la ventana de la terminal donde corro."
    elif not answer or not answer.strip():
        answer = "Hecho, señor."
    note = _after_brain_sessions()
    if note:
        answer = f"{answer} {note}".strip()
    return {"texto": answer, "archivos": files}


def sintetizar(texto: str):
    """Convierte texto en audio con la voz de Axtra. Devuelve (bytes, tipo)."""
    from speech import clean_for_speech

    texto = clean_for_speech(texto)[:1500]
    tmp = Path(tempfile.gettempdir()) / f"axtra_web_{uuid.uuid4().hex}.mp3"
    out = str(tmp)
    try:
        engine = tts()
        if engine:
            out = engine._prepare(texto, str(tmp))
        else:
            import asyncio

            import edge_tts
            import voices

            voice, rate, pitch = voices.current()
            asyncio.run(edge_tts.Communicate(texto, voice, rate=rate, pitch=pitch).save(out))
        data = Path(out).read_bytes()
        return data, ("audio/wav" if str(out).endswith(".wav") else "audio/mpeg")
    finally:
        for f in {tmp, Path(out)}:
            try:
                f.unlink(missing_ok=True)
            except OSError:
                pass


def transcribir(wav_bytes: bytes) -> str:
    import numpy as np

    with wave.open(io.BytesIO(wav_bytes)) as w:
        if w.getsampwidth() != 2 or w.getnchannels() != 1:
            raise ValueError("el audio debe ser WAV mono de 16 bits")
        rate = w.getframerate()
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    audio = pcm.astype(np.float32) / 32768.0
    from config import SAMPLE_RATE

    if rate != SAMPLE_RATE:   # el navegador casi siempre ya lo manda a 16 kHz
        n = int(len(audio) * SAMPLE_RATE / rate)
        audio = np.interp(np.linspace(0, len(audio), n, endpoint=False), np.arange(len(audio)), audio)
        audio = audio.astype(np.float32)
    return stt().transcribe(audio)


# ---------------- Servidor ----------------
def _token() -> str:
    return hashlib.sha256(("axtra-web|" + PASSWORD).encode()).hexdigest()


class Handler(BaseHTTPRequestHandler):
    server_version = "Axtra"

    def log_message(self, fmt, *args):   # sin ruido en la terminal
        pass

    # --- utilidades ---
    def _send(self, code: int, body: bytes, ctype: str, headers: dict = None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data, code: int = 200, headers: dict = None):
        self._send(code, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8",
                   headers)

    def _body(self, limit: int = 20_000_000) -> bytes:
        n = int(self.headers.get("Content-Length") or 0)
        if n > limit:
            raise ValueError("mensaje demasiado grande")
        return self.rfile.read(n) if n else b""

    def _authorized(self) -> bool:
        if not LAN:
            return True
        cookie = self.headers.get("Cookie", "")
        m = re.search(r"axtra_sesion=([0-9a-f]{64})", cookie)
        return bool(m) and hmac.compare_digest(m.group(1), _token())

    def _host_ok(self) -> bool:
        """Solo acepta peticiones dirigidas a este PC (evita que una página maliciosa use otro nombre
        de dominio que apunte aquí)."""
        if LAN:
            return True
        host = self.headers.get("Host", "")
        return host in (f"localhost:{PORT}", f"127.0.0.1:{PORT}", f"[::1]:{PORT}")

    def _same_origin(self) -> bool:
        """Evita que otra página web abierta en el navegador le mande órdenes a Axtra."""
        origin = self.headers.get("Origin")
        return origin is None or urlparse(origin).netloc == self.headers.get("Host", "")

    # --- rutas ---
    def do_GET(self):
        path = urlparse(self.path).path
        if not self._host_ok():
            return self._json({"error": "host no permitido"}, 403)
        if path in ("/", "/index.html"):
            return self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if path == "/api/estado":
            return self._json({"usuario": USER_NAME, "necesita_clave": not self._authorized()})
        if not self._authorized():
            return self._json({"error": "clave"}, 401)
        if path == "/api/chats":
            with _chats_lock:
                chats = _load_chats()
            return self._json([{"id": c["id"], "titulo": c["titulo"]} for c in chats])
        m = re.fullmatch(r"/api/chats/([0-9a-f]+)", path)
        if m:
            with _chats_lock:
                chat = next((c for c in _load_chats() if c["id"] == m.group(1)), None)
            return self._json(chat or {"error": "no existe"}, 200 if chat else 404)
        if path.startswith("/archivos/"):
            target = (DOCS_DIR / unquote(path[len("/archivos/"):])).resolve()
            if not target.is_file() or not target.is_relative_to(DOCS_DIR.resolve()):
                return self._json({"error": "no existe"}, 404)
            ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            return self._send(200, target.read_bytes(), ctype)
        self._json({"error": "no existe"}, 404)

    def do_DELETE(self):
        if not self._host_ok() or not self._authorized() or not self._same_origin():
            return self._json({"error": "clave"}, 401)
        m = re.fullmatch(r"/api/chats/([0-9a-f]+)", urlparse(self.path).path)
        if not m:
            return self._json({"error": "no existe"}, 404)
        with _chats_lock:
            _save_chats([c for c in _load_chats() if c["id"] != m.group(1)])
        self._json({"ok": True})

    def do_POST(self):
        path = urlparse(self.path).path
        if not self._host_ok() or not self._same_origin():
            return self._json({"error": "origen no permitido"}, 403)
        try:
            if path == "/api/login":
                data = json.loads(self._body(10_000) or b"{}")
                if LAN and hmac.compare_digest(str(data.get("clave", "")), PASSWORD):
                    return self._json({"ok": True}, headers={
                        "Set-Cookie": f"axtra_sesion={_token()}; HttpOnly; SameSite=Strict; Path=/; Max-Age=2592000"})
                time.sleep(1)   # frena a quien intente adivinar la clave
                return self._json({"error": "clave incorrecta"}, 401)
            if not self._authorized():
                return self._json({"error": "clave"}, 401)
            if path == "/api/chat":
                data = json.loads(self._body(200_000) or b"{}")
                texto = str(data.get("texto", "")).strip()
                if not texto:
                    return self._json({"error": "mensaje vacío"}, 400)
                print(f"Tú (web): {texto}")
                try:
                    reply = responder(texto, data.get("modo", "auto"))
                except Exception as e:
                    reply = {"texto": f"Señor, tuve un problema: {e}", "archivos": []}
                print(f"Axtra (web): {reply['texto'][:200]}")
                reply["chat_id"] = _add_to_chat(str(data.get("chat_id") or ""), texto, reply)
                reply["voz"] = _speech_chunks(reply["texto"])
                return self._json(reply)
            if path == "/api/voz":
                data = json.loads(self._body(50_000) or b"{}")
                audio, ctype = sintetizar(str(data.get("texto", "")))
                return self._send(200, audio, ctype)
            if path == "/api/escuchar":
                return self._json({"texto": transcribir(self._body())})
        except Exception as e:
            print(f"  (web: {e})")
            return self._json({"error": str(e)}, 500)
        self._json({"error": "no existe"}, 404)


def main():
    if LAN and not PASSWORD:
        raise SystemExit("Para abrir Axtra en la red pon una clave: JARVIS_WEB_CLAVE=... en el .env")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"=== AXTRA WEB en {url} ===")
    if LAN:
        import socket

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            print(f"  Desde el celular (mismo Wi-Fi): http://{s.getsockname()[0]}:{PORT}  (pide la clave)")
            s.close()
        except OSError:
            pass
    print("  Cargando el cerebro de Axtra...")
    threading.Thread(target=brain, daemon=True).start()
    if os.getenv("JARVIS_WEB_ABRIR", "1") == "1":
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print("  Para cerrar: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAxtra web cerrado.")


if __name__ == "__main__":
    main()
