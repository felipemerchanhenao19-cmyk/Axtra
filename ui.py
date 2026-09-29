"""Un solo hilo para todas las ventanas de Axtra (escritorio, ondas, cuadrícula).

Tkinter falla si hay varias ventanas raíz en hilos distintos; por eso todas se crean aquí como
Toplevel de una raíz oculta, y el resto del programa les manda órdenes con call().
"""
import queue
import threading

_q = queue.Queue()
_ready = threading.Event()
_thread = None
root = None


def _run():
    global root
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()

    def poll():
        try:
            while True:
                fn = _q.get_nowait()
                try:
                    fn(root)
                except Exception as e:
                    print(f"  (ventana: {e})")
        except queue.Empty:
            pass
        root.after(30, poll)

    poll()
    _ready.set()
    root.mainloop()


def ensure() -> bool:
    global _thread
    if _thread is None:
        _thread = threading.Thread(target=_run, daemon=True)
        _thread.start()
    return _ready.wait(5)


def call(fn) -> None:
    """Ejecuta fn(root) dentro del hilo de las ventanas."""
    ensure()
    _q.put(fn)
