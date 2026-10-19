"""«Cine Apex»: homenajes elegantes al cine (zombis, romance, jazz, ciencia ficción) con Orbi y la publicidad escondida.
Usa el motor de «heroes» (planos, cámara, efectos, voces, música y mezcla) con personajes humanos nuevos y escenarios propios.
  python hacer.py <id|todos>               →  entregables/redes/cine/<id>.mp4 (+ sin música y liviano)
  PRUEBA=planos python hacer.py <id>       →  un cuadro por plano para revisar el encuadre"""
import sys, os, json, asyncio, subprocess, time
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, AQUI); sys.path.append(AQUI + "../heroes")
from episodios import EPISODIOS
import importlib.util
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ, REDES = motor.RAIZ, motor.REDES
SALIDA = RAIZ + "entregables/redes/cine/"

def pagina(ep, lin, W):
    leer = lambda p: open(p).read()
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}{leer(REDES + "expediente28/fuentes_noir.html")}<style>{leer(AQUI + "estilo.css")}</style></head><body>
<div id="cine"><div id="fondo"></div><div id="mundo"></div></div><div id="pantalla"></div><div id="vineta"></div>
<div id="titulo"><b></b><small></small></div><div id="letrero"></div><div id="pedido"></div><div id="sub"></div>
<div id="flash"></div><div id="negro"></div><div id="barras"></div><div id="gancho"></div>
<div id="sello"><div id="o-final"></div><div id="frase"></div><div id="logo"><b></b><span></span></div></div>
<canvas id="grano" width="360" height="640"></canvas><svg width="0" height="0" style="position:absolute" id="defs"></svg>
<script>
const EP = {json.dumps(ep, ensure_ascii=False)};
const LINEA = {json.dumps(lin, ensure_ascii=False)};
{leer(REDES + "orbi.js")}
{leer(REDES + "hierro/armadura.js")}
{leer(REDES + "viernes/personajes.js")}
{leer(REDES + "comision2/personajes_comi.js")}
{leer(REDES + "heroes/personajes.js")}
{leer(REDES + "heroes/escenarios.js")}
{leer(AQUI + "personajes.js")}
{leer(AQUI + "escenarios.js")}
document.getElementById("defs").innerHTML = CINE_DEFS;
{leer(REDES + "heroes/escena.js")}
</script></body></html>'''
    open(W + "cuadro.html", "w").write(html)

def hacer(eid):
    ep = EPISODIOS[eid]; W = motor.TRABAJO + "cine_" + eid + "/"; os.makedirs(W, exist_ok=True); t0 = time.time()
    lin = asyncio.run(motor.voces(ep, W)); json.dump(lin, open(W + "linea.json", "w"), ensure_ascii=False)
    pagina(ep, lin, W)
    if os.getenv("PRUEBA"):
        ts = [round((p["ini"] + p["fin"]) / 2, 2) for p in lin["planos"]] if os.getenv("PRUEBA") == "planos" else [float(x) for x in os.getenv("PRUEBA").split(",")]
        asyncio.run(motor.prueba(W, ts)); print("pruebas en", W, ts); return
    motor.sonido(ep, lin, W); asyncio.run(motor.imagen(W, lin["dur"]))
    os.makedirs(SALIDA, exist_ok=True)
    for son, nombre, extra in (("sonido.wav", f"{eid}.mp4", ["-crf", "20"]), ("sonido_sin_musica.wav", f"{eid}-sin-musica.mp4", ["-crf", "20"]),
                               ("sonido.wav", f"{eid}-liviano.mp4", ["-crf", "27", "-vf", "scale=720:-2"])):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + son, "-c:v", "libx264", "-preset", "slow", *extra, "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", SALIDA + nombre], check=True)
    print("listo", eid, lin["dur"], "s de video en", round(time.time() - t0), "s")

if __name__ == "__main__":
    for eid in (list(EPISODIOS) if sys.argv[1:] == ["todos"] else sys.argv[1:]): hacer(eid)
