"""Interfaz de ondas de mar: se mueven suaves en reposo y se agitan cuando Axtra piensa y razona.

Estados: reposo, escuchando, pensando, hablando. Cualquier parte de Axtra llama set_state().
Se abre sola con el Protocolo de Inteligencia Avanzada, o por voz: "muestra las ondas" / "cierra las ondas".
"""
import math
import time

_state = {"estado": "reposo", "detalle": "", "open": False, "titulo": "J A R V I S"}
# (amplitud, velocidad, brillo) por estado
STYLE = {"reposo": (7, 0.6, 0.55), "escuchando": (13, 1.1, 0.75), "pensando": (26, 2.6, 1.0),
         "hablando": (17, 1.6, 0.9)}
LABEL = {"reposo": "En espera", "escuchando": "Escuchando...", "pensando": "Razonando...",
         "hablando": "Hablando..."}


def set_state(estado: str, detalle: str = None) -> None:
    _state["estado"] = estado if estado in STYLE else "reposo"
    if detalle is not None:
        _state["detalle"] = detalle


def is_open() -> bool:
    return _state["open"]


def open_window(titulo: str = "J A R V I S") -> str:
    _state["titulo"] = titulo
    if _state["open"]:
        return "Las ondas ya están en pantalla, señor."
    _state["open"] = True
    import ui

    ui.call(_build)
    return "Mostrando mis ondas, señor."


def close_window() -> str:
    _state["open"] = False   # la ventana se cierra sola en el siguiente cuadro
    return "Ondas cerradas, señor."


def _mix(hex1: str, hex2: str, t: float) -> str:
    a = [int(hex1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(x + (y - x) * t):02x}" for x, y in zip(a, b))


def _build(master) -> None:
    import tkinter as tk

    W, H = 640, 300
    BG = "#050b18"
    win = tk.Toplevel(master)
    win.title("AXTRA · Ondas")
    win.configure(bg=BG)
    win.geometry(f"{W}x{H}")
    win.minsize(360, 200)
    cv = tk.Canvas(win, bg=BG, highlightthickness=0)
    cv.pack(fill="both", expand=True)
    layers = [  # (color, fase, frecuencia, altura base %, factor de amplitud)
        ("#0a2a5c", 0.0, 1.3, 0.66, 0.8),
        ("#0b4a8f", 1.7, 1.8, 0.70, 1.0),
        ("#0888c9", 3.1, 2.3, 0.75, 1.15),
        ("#00d2ff", 4.4, 2.9, 0.80, 0.9),
    ]
    polys = [cv.create_polygon(0, 0, 0, 0, fill=c, outline="") for c, *_ in layers]
    crest = cv.create_line(0, 0, 0, 0, fill="#aef6ff", width=2, smooth=True)
    title = cv.create_text(W / 2, 34, text="", fill="#00e5ff", font=("Segoe UI", 16, "bold"))
    status = cv.create_text(W / 2, 64, text="", fill="#8fb8ff", font=("Segoe UI", 11))
    detail = cv.create_text(W / 2, 88, text="", fill="#6c7fa8", font=("Segoe UI", 9))
    cur = {"amp": 7.0, "spd": 0.6, "bri": 0.55, "t": 0.0, "last": time.time()}

    def on_close():
        _state["open"] = False

    win.protocol("WM_DELETE_WINDOW", on_close)

    def frame():
        if not _state["open"]:
            try:
                win.destroy()
            except tk.TclError:
                pass
            return
        try:
            w = max(200, cv.winfo_width())
            h = max(150, cv.winfo_height())
        except tk.TclError:
            return
        now = time.time()
        dt = min(0.1, now - cur["last"])
        cur["last"] = now
        amp, spd, bri = STYLE[_state["estado"]]
        k = 0.08   # transición suave entre estados
        cur["amp"] += (amp - cur["amp"]) * k
        cur["spd"] += (spd - cur["spd"]) * k
        cur["bri"] += (bri - cur["bri"]) * k
        cur["t"] += dt * cur["spd"]
        t = cur["t"]
        pulse = 1 + (0.25 * math.sin(now * 9) if _state["estado"] == "hablando" else 0)
        n = 56
        top_line = None
        for idx, (color, phase, freq, base, fac) in enumerate(layers):
            pts = []
            for i in range(n + 1):
                x = w * i / n
                u = i / n * math.pi * 2
                y = (h * base
                     + cur["amp"] * fac * pulse * math.sin(u * freq + t * (1.2 + idx * 0.35) + phase)
                     + cur["amp"] * 0.45 * fac * math.sin(u * freq * 2.3 - t * 1.7 + phase * 2)
                     + (cur["amp"] * 0.25 * math.sin(u * 7 + t * 4) if _state["estado"] == "pensando" else 0))
                pts += [x, y]
            if idx == len(layers) - 1:
                top_line = list(pts)
            cv.coords(polys[idx], 0, h, *pts, w, h)
            cv.itemconfigure(polys[idx], fill=_mix("#050b18", color, min(1.0, cur["bri"] + idx * 0.05)))
        if top_line:
            cv.coords(crest, *top_line)
            cv.itemconfigure(crest, fill=_mix("#050b18", "#aef6ff", cur["bri"]))
        cv.coords(title, w / 2, 34)
        cv.coords(status, w / 2, 64)
        cv.coords(detail, w / 2, 88)
        cv.itemconfigure(title, text=_state["titulo"])
        cv.itemconfigure(status, text=LABEL[_state["estado"]])
        cv.itemconfigure(detail, text=_state["detalle"][:90])
        win.after(40, frame)

    frame()
