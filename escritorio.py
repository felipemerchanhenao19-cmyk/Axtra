"""Escritorio de Axtra: una ventana para ESCRIBIRLE, y él siempre responde en voz alta.

Se abre por voz: "Axtra, activa escritorio" (o "abre el escritorio", "modo escritorio").
Se cierra con "Axtra, cierra el escritorio" o con la X de la ventana.
- Escribes abajo y presionas Enter.
- Axtra responde hablando y también lo ves escrito en la ventana.
- Botón "Reportar fallo": guarda la conversación reciente en data/reporte_fallos.md para corregirlo.
"""
import queue
import threading
import time
from datetime import datetime

from config import DATA_DIR

brain = tts = stt = None           # los conecta main.py
REPORT_PATH = DATA_DIR / "reporte_fallos.md"
_ui_q = queue.Queue()               # órdenes para la ventana (solo el hilo de la ventana la toca)
_answers = queue.Queue()            # respuestas escritas durante una sesión de sincronización
_state = {"open": False, "thread": None, "session": False, "busy": False}


def is_open() -> bool:
    return _state["open"]


def open_window() -> str:
    if brain is None or tts is None:
        return "El escritorio no está listo todavía, señor."
    if _state["open"]:
        _ui_q.put(("front", None))
        return "El escritorio ya está abierto, señor. Puede escribirme."
    _state["open"] = True
    import ui

    ui.call(_ui)
    return "Escritorio activado, señor. Escríbame y le responderé en voz alta."


def close_window() -> str:
    if not _state["open"]:
        return "El escritorio ya estaba cerrado, señor."
    _ui_q.put(("close", None))
    return "Escritorio cerrado, señor."


def _log(who: str, text: str) -> None:
    _ui_q.put(("msg", (who, text)))


class _SpeakAndShow:
    """Como tts, pero además escribe en la ventana (para la sesión de sincronización)."""

    def say(self, text, **k):
        _log("Axtra", text)
        tts.say(text)


def _process(text: str) -> None:
    import dictation
    import language
    import quick
    import sync
    import voices

    _state["busy"] = True
    _ui_q.put(("status", "Axtra está pensando..."))
    try:
        answer = brain.ask(text)
    except Exception as e:
        answer = f"Señor, tuve un problema: {e}"
    try:
        if answer == quick.SHUTDOWN:
            _log("Axtra", "Desconectando sistemas. Hasta luego, señor.")
            tts.say("Desconectando sistemas. Hasta luego, señor.")
            import os

            os._exit(0)
        if answer and answer.strip():
            _log("Axtra", answer)
            _ui_q.put(("status", "Axtra está hablando..."))
            tts.say(answer)                      # siempre en voz alta
        if voices.pending_demo:
            voices.demo(tts)
        if sync.pending:
            _state["session"] = True
            _ui_q.put(("status", "Sesión de sincronización: responda escribiendo (o 'paso')"))
            try:
                sync.run_session(_SpeakAndShow(), stt, get_answer=lambda: _answers.get())
            finally:
                _state["session"] = False
        import aprendizaje

        if aprendizaje.pending is not None:
            _state["session"] = True
            _ui_q.put(("status", "Protocolo de inteligencia avanzada: responda escribiendo"))
            try:
                aprendizaje.run(_SpeakAndShow(), lambda: _answers.get())
            finally:
                _state["session"] = False
        if dictation.pending or language.pending:
            dictation.pending = None
            language.pending = None
            msg = "El dictado y las clases de idiomas funcionan por voz, señor. Pídamelos hablando."
            _log("Axtra", msg)
            tts.say(msg)
    finally:
        _state["busy"] = False
        _ui_q.put(("status", "Listo. Escriba su mensaje y presione Enter."))


def _report() -> None:
    recent = [m for m in brain.history[-6:] if isinstance(m.get("content"), str)]
    lines = [f"\n## {datetime.now():%Y-%m-%d %H:%M} — reporte desde el escritorio"]
    for m in recent:
        who = "Felipe" if m["role"] == "user" else "Axtra"
        lines.append(f"- **{who}:** {m['content'][:500]}")
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    _log("Sistema", f"Reporte guardado en {REPORT_PATH}. Envíeselo a Claude para corregir el fallo.")


def _ui(master) -> None:
    import tkinter as tk

    BG, PANEL, FG, CYAN, GOLD = "#0b1020", "#131a2e", "#e6ecff", "#00e5ff", "#ffd400"
    root = tk.Toplevel(master)
    root.title("AXTRA · Escritorio")
    root.configure(bg=BG)
    root.geometry("560x640")
    root.minsize(420, 420)

    head = tk.Label(root, text="J A R V I S", bg=BG, fg=CYAN, font=("Segoe UI", 18, "bold"))
    head.pack(pady=(12, 0))
    sub = tk.Label(root, text="Escriba y le respondo en voz alta", bg=BG, fg="#8a96b8", font=("Segoe UI", 10))
    sub.pack(pady=(0, 8))

    frame = tk.Frame(root, bg=BG)
    frame.pack(fill="both", expand=True, padx=12)
    log = tk.Text(frame, bg=PANEL, fg=FG, wrap="word", font=("Segoe UI", 11), relief="flat", height=8,
                  padx=10, pady=10, state="disabled", insertbackground=FG)
    scroll = tk.Scrollbar(frame, command=log.yview)
    log.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")
    log.pack(side="left", fill="both", expand=True)
    log.tag_configure("Felipe", foreground=GOLD, font=("Segoe UI", 11, "bold"))
    log.tag_configure("Axtra", foreground=CYAN, font=("Segoe UI", 11, "bold"))
    log.tag_configure("Sistema", foreground="#8a96b8", font=("Segoe UI", 10, "italic"))

    status = tk.Label(root, text="Listo. Escriba su mensaje y presione Enter.", bg=BG, fg="#8a96b8",
                      font=("Segoe UI", 9), anchor="w")
    status.pack(fill="x", padx=14, pady=(6, 0))

    bottom = tk.Frame(root, bg=BG)
    bottom.pack(fill="x", padx=12, pady=10)
    entry = tk.Entry(bottom, bg=PANEL, fg=FG, insertbackground=FG, relief="flat", font=("Segoe UI", 12))
    entry.pack(side="left", fill="x", expand=True, ipady=8)

    def add(who, text):
        log.configure(state="normal")
        log.insert("end", f"{who}: ", who)
        log.insert("end", text.strip() + "\n\n")
        log.configure(state="disabled")
        log.see("end")

    def send(_event=None):
        text = entry.get().strip()
        if not text:
            return
        entry.delete(0, "end")
        add("Felipe", text)
        if _state["session"]:
            _answers.put(text)          # respuesta a una pregunta de sincronización
            return
        if _state["busy"]:
            add("Sistema", "Un momento, todavía estoy respondiendo lo anterior.")
            return
        threading.Thread(target=_process, args=(text,), daemon=True).start()

    tk.Button(bottom, text="Enviar", command=send, bg=CYAN, fg="#001018", relief="flat",
              font=("Segoe UI", 10, "bold"), padx=14).pack(side="left", padx=(8, 0), ipady=4)
    tk.Button(root, text="Reportar fallo", command=_report, bg=BG, fg="#8a96b8", relief="flat",
              font=("Segoe UI", 9), activebackground=PANEL).pack(pady=(0, 8))
    entry.bind("<Return>", send)

    def on_close():
        _state["open"] = False
        root.destroy()
        while not _ui_q.empty():   # vacía órdenes viejas para la próxima vez
            try:
                _ui_q.get_nowait()
            except queue.Empty:
                break

    root.protocol("WM_DELETE_WINDOW", on_close)

    def poll():
        try:
            while True:
                kind, data = _ui_q.get_nowait()
                if kind == "msg":
                    add(*data)
                elif kind == "status":
                    status.configure(text=data)
                elif kind == "front":
                    root.deiconify()
                    root.lift()
                    entry.focus_force()
                elif kind == "close":
                    on_close()
                    return
        except tk.TclError:
            return
        except queue.Empty:
            pass
        root.after(80, poll)

    add("Sistema", "Escritorio activado. Escriba y presione Enter; Axtra responde en voz alta.")
    root.attributes("-topmost", True)
    root.after(600, lambda: root.attributes("-topmost", False))
    entry.focus_force()
    poll()
