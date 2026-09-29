"""Modo texto con código de acceso: escríbele a Jarvis en la terminal y te responde con su voz.

Sirve para lugares públicos (con audífonos) y para probar y mejorar a Jarvis más rápido.
- Presiona Enter en la ventana de Jarvis -> pide tu código (no se ve al escribirlo).
- El código se crea la primera vez y se guarda cifrado (hash) en data/acceso.json,
  o puedes fijarlo en .env con JARVIS_CODIGO_ACCESO.
- Después de 3 intentos fallidos se bloquea 5 minutos. Se cierra solo tras 30 min sin escribir.

Comandos dentro del modo texto:
  /voz      responde hablando y escrito (por defecto)
  /mudo     responde solo escrito (sin voz)
  /reporte  <qué falló>  guarda un reporte de fallo con la conversación reciente
  /salir    cierra el modo texto (vuelve a pedir el código)
  /ayuda    muestra estos comandos
"""
import getpass
import hashlib
import json
import os
import secrets
import threading
import time
from datetime import datetime

from config import DATA_DIR

ACCESS_PATH = DATA_DIR / "acceso.json"
REPORT_PATH = DATA_DIR / "reporte_fallos.md"
IDLE_LOCK_SECONDS = 30 * 60


def _hash(code: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", code.strip().encode(), salt.encode(), 200_000).hex()


def _check(code: str) -> bool:
    env = os.getenv("JARVIS_CODIGO_ACCESO", "").strip()
    if env:
        return secrets.compare_digest(code.strip(), env)
    try:
        d = json.loads(ACCESS_PATH.read_text(encoding="utf-8"))
        return secrets.compare_digest(_hash(code, d["salt"]), d["hash"])
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return False


def _has_code() -> bool:
    return bool(os.getenv("JARVIS_CODIGO_ACCESO", "").strip()) or ACCESS_PATH.exists()


def _create_code() -> bool:
    print("\n  === Crear tu código de acceso (solo esta vez) ===")
    print("  Mínimo 6 caracteres. No se verá mientras lo escribes.")
    a = getpass.getpass("  Nuevo código: ")
    if len(a.strip()) < 6:
        print("  Muy corto. Presiona Enter para intentarlo de nuevo.")
        return False
    b = getpass.getpass("  Repite el código: ")
    if a != b:
        print("  No coinciden. Presiona Enter para intentarlo de nuevo.")
        return False
    salt = secrets.token_hex(16)
    ACCESS_PATH.write_text(json.dumps({"salt": salt, "hash": _hash(a, salt)}), encoding="utf-8")
    print("  Código guardado. Si lo olvidas, borra el archivo data/acceso.json y crea uno nuevo.\n")
    return True


def _report(brain, note: str) -> None:
    recent = [m for m in brain.history[-6:] if isinstance(m.get("content"), str)]
    lines = [f"\n## {datetime.now():%Y-%m-%d %H:%M} — {note or '(sin descripción)'}"]
    for m in recent:
        who = "Felipe" if m["role"] == "user" else "Jarvis"
        lines.append(f"- **{who}:** {m['content'][:500]}")
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  Reporte guardado en {REPORT_PATH}. Envíaselo a Claude para corregirlo.")


def _loop(brain, tts, stt):
    unlocked, fails, blocked_until, last_use, voice = False, 0, 0.0, 0.0, True
    while True:
        try:
            line = input()
        except (EOFError, RuntimeError):
            return
        now = time.time()
        if unlocked and now - last_use > IDLE_LOCK_SECONDS:
            unlocked = False
            print("  (modo texto cerrado por inactividad)")
        if not unlocked:
            if now < blocked_until:
                print(f"  Bloqueado por intentos fallidos. Espera {int(blocked_until - now) // 60 + 1} min.")
                continue
            if not _has_code():
                _create_code()
                continue
            code = getpass.getpass("  Código de acceso: ")
            if _check(code):
                unlocked, fails, last_use = True, 0, now
                print("  ✔ Acceso concedido. Escribe y presiona Enter. /ayuda para ver comandos.")
            else:
                fails += 1
                print("  ✘ Código incorrecto.")
                if fails >= 3:
                    blocked_until, fails = now + 300, 0
                    print("  Demasiados intentos: bloqueado 5 minutos.")
            continue
        text = line.strip()
        last_use = now
        if not text:
            continue
        cmd = text.lower()
        if cmd in ("/salir", "/cerrar"):
            unlocked = False
            print("  Modo texto cerrado.")
            continue
        if cmd == "/mudo":
            voice = False
            print("  Responderé solo por escrito.")
            continue
        if cmd == "/voz":
            voice = True
            print("  Responderé con voz y por escrito.")
            continue
        if cmd in ("/ayuda", "/help"):
            print(__doc__.split("Comandos dentro del modo texto:")[1])
            continue
        if cmd.startswith("/reporte"):
            _report(brain, text[len("/reporte"):].strip())
            continue
        try:
            answer = brain.ask(text)
        except Exception as e:
            answer = f"Señor, tuve un problema: {e}"
        import quick
        import sync
        import voices

        if answer == quick.SHUTDOWN:
            tts.say("Desconectando sistemas. Hasta luego, señor.")
            os._exit(0)
        if answer and answer.strip():
            if voice:
                tts.say(answer)
            else:
                print(f"Jarvis: {answer}")
        if voices.pending_demo:
            if voice:
                voices.demo(tts)
            else:
                voices.pending_demo = False
                print("  " + voices.catalog_text())
        if sync.pending:
            say = tts.say if voice else (lambda t, **k: print(f"Jarvis: {t}"))

            class _T:  # misma interfaz que tts para la sesión
                pass
            t = _T()
            t.say = say
            sync.run_session(t, stt, get_answer=lambda: input("  Tu respuesta: "))
        import dictation
        import language

        if dictation.pending or language.pending:
            dictation.pending = None
            language.pending = None
            print("  El dictado y las clases de idiomas funcionan por voz. Dímelo hablando.")


def start(brain, tts, stt) -> None:
    threading.Thread(target=_loop, args=(brain, tts, stt), daemon=True).start()
    print("  - Modo texto: presiona Enter en esta ventana para escribirle a Jarvis (pide tu código)")
