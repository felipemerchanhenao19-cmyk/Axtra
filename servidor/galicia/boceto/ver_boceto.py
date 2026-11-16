"""Abre la página de la Hacienda La Galicia en el navegador: http://localhost:8000

Desde la carpeta de Axtra:   python servidor/galicia/boceto/ver_boceto.py
Para cerrarlo: Ctrl+C en la terminal.
"""
import functools
import http.server
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
PUERTO = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    manejador = functools.partial(Silencioso, directory=str(CARPETA))
    with socketserver.TCPServer(("127.0.0.1", PUERTO), manejador) as servidor:
        direccion = f"http://localhost:{PUERTO}"
        print(f"Boceto de la Hacienda La Galicia en {direccion}  (Ctrl+C para cerrar)")
        threading.Timer(0.8, lambda: webbrowser.open(direccion)).start()
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("\nCerrado.")


if __name__ == "__main__":
    main()
