"""«Línea de luz»: video explicativo de Apex Domicilios en gráfico animado (estilo línea de neón, palabras clave en mayúsculas).
  python hacer.py               →  entregables/redes/linea/apex-domicilios-diciembre.mp4 (+ sin música y liviano)
  PRUEBA=1,4,8 python hacer.py  →  cuadros sueltos para revisar
Usa el sonido del motor de «heroes» (música y efectos), sin voz: el texto cuenta la historia."""
import os, sys, asyncio, subprocess, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ, FPS = motor.RAIZ, motor.FPS
NOMBRE = "apex-domicilios-diciembre"; SALIDA = RAIZ + "entregables/redes/linea/"; W = motor.TRABAJO + "linea_" + NOMBRE + "/"
# segmentos de sonido alineados con las escenas de linea.js
SEG = [(0.0, 2.7, "tension", [dict(tipo="pum", p=0.0), dict(tipo="destello", p=0.2)]), (2.7, 5.4, "tension", [dict(tipo="pum", p=0.62)]),
       (5.4, 6.6, "heroe", [dict(tipo="pum", p=0.0), dict(tipo="destello", p=0.3)]), (6.6, 9.4, "synth", [dict(tipo="destello", p=0.0)]),
       (9.4, 12.6, "synth", [dict(tipo="destello", p=0.0), dict(tipo="monedas", p=0.45)]), (12.6, 15.0, "synth", [dict(tipo="destello", p=0.0)]),
       (15.0, 18.4, "synth", [dict(tipo="destello", p=0.0)]), (18.4, 21.4, "pelicula", [dict(tipo="pum", p=0.0), dict(tipo="monedas", p=0.55)]),
       (21.4, 25.0, "corporativo", [dict(tipo="destello", p=0.0)])]
SELLO = 21.6

def pagina():
    leer = lambda p: open(p).read()
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}<style>
html,body{{margin:0;background:#000;overflow:hidden}} #c{{position:absolute;inset:0;width:1080px;height:1920px}}
#g{{position:absolute;inset:0;width:1080px;height:1920px;opacity:.07;mix-blend-mode:overlay}}
#v{{position:absolute;inset:0;background:radial-gradient(80% 65% at 50% 48%,rgba(0,0,0,0) 55%,rgba(0,0,0,.65) 100%)}}</style></head><body>
<canvas id="c" width="1080" height="1920"></canvas><div id="v"></div><canvas id="g" width="360" height="640"></canvas>
<script>{leer(AQUI + "linea.js")}</script></body></html>'''
    open(W + "cuadro.html", "w").write(html)

async def abrir(p):
    br = await p.chromium.launch(executable_path=motor.CHROME, args=["--force-color-profile=srgb"])
    pg = await br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
    await pg.goto("file://" + W + "cuadro.html")
    await pg.evaluate("Promise.all(['400','500','600','700','800'].map(w => document.fonts.load(w + ' 40px Figtree')))"); await pg.wait_for_timeout(800); return br, pg

async def obrero(i, a, b):
    from playwright.async_api import async_playwright
    seg = W + f"seg{i}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", seg], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        br, pg = await abrir(p)
        for f in range(a, b): await pg.evaluate("t => render(t)", f / FPS); ff.stdin.write(await pg.screenshot(type="jpeg", quality=94))
        await br.close()
    ff.stdin.close(); ff.wait(); return seg

async def imagen(total):
    n = 4; ncu = int(total * FPS); tr = ncu // n + 1
    segs = await asyncio.gather(*[obrero(i, i * tr, min(ncu, (i + 1) * tr)) for i in range(n)])
    open(W + "segs.txt", "w").write("".join(f"file '{s}'\n" for s in segs))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", W + "segs.txt", "-c", "copy", W + "imagen.mp4"], check=True)

async def prueba(ts):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br, pg = await abrir(p)
        for t in ts: await pg.evaluate("t => render(t)", t); await pg.screenshot(path=W + f"p_{t:05.2f}.jpg", type="jpeg", quality=82)
        await br.close()

def main():
    os.makedirs(W, exist_ok=True); pagina()
    if os.getenv("PRUEBA"): ts = [float(v) for v in os.getenv("PRUEBA").split(",")]; asyncio.run(prueba(ts)); print("pruebas en", W); return
    ep = {"planos": [dict(musica=m, fx=fx) for (_, _, m, fx) in SEG], "reparto": {}}
    lin = {"planos": [{"ini": a, "fin": b, "lineas": []} for (a, b, _, _) in SEG], "sello": SELLO, "dur": SELLO + motor.COLA_SELLO}
    motor.sonido(ep, lin, W); asyncio.run(imagen(lin["dur"]))
    os.makedirs(SALIDA, exist_ok=True)
    for son, nombre, extra in (("sonido.wav", f"{NOMBRE}.mp4", ["-crf", "18"]), ("sonido_sin_musica.wav", f"{NOMBRE}-sin-musica.mp4", ["-crf", "18"]),
                               ("sonido.wav", f"{NOMBRE}-liviano.mp4", ["-crf", "26", "-vf", "scale=720:-2"])):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + son, "-c:v", "libx264", "-preset", "slow", *extra, "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", SALIDA + nombre], check=True)
    print("listo", NOMBRE, lin["dur"], "s")

if __name__ == "__main__": main()
