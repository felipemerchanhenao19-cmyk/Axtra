"""«Películas Apex»: cortometrajes verticales para dueños de restaurante, con escenarios, luces, cámara de cine y el sistema real en pantalla.
  python hacer.py <id|todos>               →  entregables/redes/peliculas/<id>.mp4 (+ sin música y liviano)
  PRUEBA=planos python hacer.py <id>       →  un cuadro por plano para revisar
Usa las voces, la música y el render del motor de «heroes». Las grabaciones reales están en produccion/videos/grabaciones/."""
import sys, os, json, asyncio, subprocess, time
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, AQUI)
from episodios import EPISODIOS
import importlib.util
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ = motor.RAIZ
GRAB = RAIZ + "produccion/videos/grabaciones/"
SALIDA = RAIZ + "entregables/redes/peliculas/"
MEDIOS = motor.TRABAJO + "medios/"

def medios(ep):
    """Copia las grabaciones a WebM con cuadros clave seguidos (Chromium no trae H.264) para saltar a cualquier segundo exacto al dibujar."""
    for pl in ep["planos"]:
        d = pl.get("dispositivo")
        if not d or d["video"].endswith("_k.webm"): continue
        dst = MEDIOS + d["video"].replace(".webm", "_k.webm"); os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", GRAB + d["video"], "-c:v", "libvpx", "-b:v", "6M", "-crf", "8", "-g", "6", "-deadline", "good", "-cpu-used", "4", "-an", dst], check=True)
        d["video"] = d["video"].replace(".webm", "_k.webm")

def pagina(ep, lin, W):
    leer = lambda p: open(p).read()
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}<style>{leer(AQUI + "estilo.css")}</style></head><body>
<div id="mundo"><div id="lejos"></div><div id="medio"></div><div id="cerca"></div><div id="tinte"></div></div>
<div id="destello"></div><div id="polvo"></div><div id="fuga"></div><div id="vineta"></div><div id="dispositivo"></div>
<div id="texto"></div><div id="cifra"></div><div id="palabras"></div><div id="final"></div><div id="sub"></div><div id="nota"></div>
<div id="barras"></div><div id="blanco"></div><div id="negro"></div><canvas id="grano" width="360" height="640"></canvas>
<script>const EP = {json.dumps(ep, ensure_ascii=False)}; const LINEA = {json.dumps(lin, ensure_ascii=False)}; const GRAB = {json.dumps(MEDIOS)};
{leer(AQUI + "mundo.js")}
{leer(AQUI + "escena.js")}</script></body></html>'''
    open(W + "cuadro.html", "w").write(html)

def hacer(eid):
    ep = EPISODIOS[eid]; W = motor.TRABAJO + "peli_" + eid + "/"; os.makedirs(W, exist_ok=True); t0 = time.time()
    lin = asyncio.run(motor.voces(ep, W)); json.dump(lin, open(W + "linea.json", "w"), ensure_ascii=False)
    medios(ep); pagina(ep, lin, W)
    if os.getenv("PRUEBA"):
        ts = [round(p["ini"] + (p["fin"] - p["ini"]) * 0.8, 2) for p in lin["planos"]] if os.getenv("PRUEBA") == "planos" else [float(x) for x in os.getenv("PRUEBA").split(",")]
        asyncio.run(motor.prueba(W, ts)); print("pruebas en", W, ts); return
    motor.sonido(ep, lin, W); asyncio.run(motor.imagen(W, lin["dur"]))
    os.makedirs(SALIDA, exist_ok=True)
    for son, nombre, extra in (("sonido.wav", f"{eid}.mp4", ["-crf", "19"]), ("sonido_sin_musica.wav", f"{eid}-sin-musica.mp4", ["-crf", "19"]),
                               ("sonido.wav", f"{eid}-liviano.mp4", ["-crf", "27", "-vf", "scale=720:-2"])):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + son, "-c:v", "libx264", "-preset", "slow", *extra, "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", SALIDA + nombre], check=True)
    print("listo", eid, lin["dur"], "s de video en", round(time.time() - t0), "s")

if __name__ == "__main__":
    for eid in (list(EPISODIOS) if sys.argv[1:] == ["todos"] else sys.argv[1:]): hacer(eid)
