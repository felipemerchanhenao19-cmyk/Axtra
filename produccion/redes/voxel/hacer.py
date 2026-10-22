"""«Turno de noche»: series en 3D real (personajes de bloques) para Apex. Tono serio, humor seco, el producto resuelve la escena.
  python hacer.py <id|todos>               →  entregables/redes/voxel/<id>.mp4 (+ sin música y liviano)
  PRUEBA=planos python hacer.py <id>       →  un cuadro por plano para revisar   (PRUEBA=3.5,8 → cuadros sueltos)
Usa las voces y el sonido del motor de «heroes». three.js se descarga con npm pack en la carpeta de trabajo (no se guarda en el repo)."""
import sys, os, json, asyncio, subprocess, time, shutil
import numpy as np
from scipy.io import wavfile
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, AQUI)
from episodios import EPISODIOS
import importlib.util
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ, FPS = motor.RAIZ, motor.FPS
SALIDA = RAIZ + "entregables/redes/voxel/"
THREE = motor.TRABAJO + "three/package/build/three.min.js"
ARGS = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]

def three():
    if os.path.exists(THREE): return
    d = motor.TRABAJO + "three/"; os.makedirs(d, exist_ok=True)
    subprocess.run(["npm", "pack", "three@0.160.0"], cwd=d, check=True, capture_output=True)
    subprocess.run(["tar", "xzf", "three-0.160.0.tgz"], cwd=d, check=True)

def envolventes(lin, W):
    """Volumen de cada voz, cuadro a cuadro (0..1), para mover la boca con el audio real."""
    for L in lin["planos"]:
        for l in L["lineas"]:
            sr, x = wavfile.read(W + f"voces/l{l['k']:02d}.wav"); x = x.astype(float); x = x if x.ndim == 1 else x.mean(1)
            n = sr // FPS; rms = np.array([np.sqrt(np.mean(x[i:i + n] ** 2)) for i in range(0, len(x), n)])
            rms = rms / (np.percentile(rms, 92) + 1e-9); rms = np.convolve(rms, [0.25, 0.5, 0.25], "same")
            l["env"] = [round(float(min(1, max(0, (v - 0.12) * 1.25)) ** 0.8), 2) for v in rms]

def playfair():
    """Playfair Display (cursiva) para las piezas de marca; se descarga con npm pack en la carpeta de trabajo."""
    d = motor.TRABAJO + "fuentes/"
    if not os.path.exists(d + "package"):
        os.makedirs(d, exist_ok=True); subprocess.run(["npm", "pack", "@fontsource/playfair-display@5.0.21"], cwd=d, check=True, capture_output=True)
        subprocess.run("tar xzf fontsource-playfair-display-*.tgz", shell=True, cwd=d, check=True)
    import base64
    caras = [("italic", 700, "latin-700-italic"), ("italic", 800, "latin-800-italic"), ("normal", 700, "latin-700-normal")]
    return "<style>" + "".join(f"@font-face {{ font-family: 'Playfair'; font-style: {e}; font-weight: {p}; src: url(data:font/woff2;base64,"
        + base64.b64encode(open(d + f"package/files/playfair-display-{n}.woff2", "rb").read()).decode() + ") format('woff2'); }" for e, p, n in caras) + "</style>"

def pagina(ep, lin, W):
    leer = lambda p: open(p).read()
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}{playfair()}<style>{leer(AQUI + "estilo.css")}</style></head><body>
<canvas id="lienzo" width="1080" height="1920"></canvas><div id="vineta"></div><canvas id="grano" width="360" height="640"></canvas>
<div id="titulo"></div><div id="gancho"></div><div id="info"></div><div id="sub"></div><div id="cortina"></div><div id="final"></div><div id="nota"></div><div id="blanco"></div><div id="negro"></div>
<script src="file://{THREE}"></script>
<script>const EP = {json.dumps(ep, ensure_ascii=False)}; const LINEA = {json.dumps(lin, ensure_ascii=False)};
{leer(AQUI + "personajes3d.js")}
{leer(AQUI + "sets3d.js")}
{leer(AQUI + "escena3d.js")}</script></body></html>'''
    open(W + "cuadro.html", "w").write(html)
    shutil.copytree(RAIZ + "produccion/redes/pelicula/fotos", W + "fotos", dirs_exist_ok=True)

async def abrir(p, W):
    br = await p.chromium.launch(executable_path=motor.CHROME, args=ARGS)
    pg = await br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
    await pg.goto("file://" + W + "cuadro.html"); await pg.wait_for_timeout(1500); return br, pg

async def obrero(W, i, a, b):
    from playwright.async_api import async_playwright
    seg = W + f"seg{i}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", seg], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        br, pg = await abrir(p, W)
        for f in range(a, b): await pg.evaluate("t => render(t)", f / FPS); ff.stdin.write(await pg.screenshot(type="jpeg", quality=94))
        await br.close()
    ff.stdin.close(); ff.wait(); return seg

async def imagen(W, total):
    n = int(os.getenv("OBREROS", "4")); ncu = int(total * FPS); tr = ncu // n + 1
    segs = await asyncio.gather(*[obrero(W, i, i * tr, min(ncu, (i + 1) * tr)) for i in range(n)])
    open(W + "segs.txt", "w").write("".join(f"file '{s}'\n" for s in segs))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", W + "segs.txt", "-c", "copy", W + "imagen.mp4"], check=True)

async def prueba(W, ts):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br, pg = await abrir(p, W)
        for t in ts: await pg.evaluate("t => render(t)", t); await pg.screenshot(path=W + f"p_{t:05.2f}.jpg", type="jpeg", quality=82)
        await br.close()

def hacer(eid):
    ep = EPISODIOS[eid]; W = motor.TRABAJO + "voxel_" + eid + "/"; os.makedirs(W, exist_ok=True); t0 = time.time(); three()
    lin = asyncio.run(motor.voces(ep, W)); envolventes(lin, W); json.dump(lin, open(W + "linea.json", "w"), ensure_ascii=False)
    pagina(ep, lin, W)
    if os.getenv("PRUEBA"):
        ts = [round(p["ini"] + (p["fin"] - p["ini"]) * 0.6, 2) for p in lin["planos"]] if os.getenv("PRUEBA") == "planos" else [float(x) for x in os.getenv("PRUEBA").split(",")]
        asyncio.run(prueba(W, ts)); print("pruebas en", W, ts); return
    motor.sonido(ep, lin, W); asyncio.run(imagen(W, lin["dur"]))
    os.makedirs(SALIDA, exist_ok=True)
    for son, nombre, extra in (("sonido.wav", f"{eid}.mp4", ["-crf", "19"]), ("sonido_sin_musica.wav", f"{eid}-sin-musica.mp4", ["-crf", "19"]),
                               ("sonido.wav", f"{eid}-liviano.mp4", ["-crf", "27", "-vf", "scale=720:-2"])):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + son, "-c:v", "libx264", "-preset", "slow", *extra, "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", SALIDA + nombre], check=True)
    print("listo", eid, lin["dur"], "s de video en", round(time.time() - t0), "s")

if __name__ == "__main__":
    for eid in (list(EPISODIOS) if sys.argv[1:] == ["todos"] else sys.argv[1:]): hacer(eid)
