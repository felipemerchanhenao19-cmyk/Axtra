"""«Orbi: universo de héroes»: arma un capítulo cinematográfico (voces, imagen 1080x1920 a 30 cuadros, música, efectos y mezcla).
  python hacer.py <id|todos> [<id> ...]       →  entregables/redes/heroes/<id>.mp4 (+ versión sin música)
  PRUEBA=1,8,15 python hacer.py <id>          →  solo cuadros de prueba en la carpeta de trabajo
Los guiones están en episodios.py."""
import sys, os, json, asyncio, subprocess, hashlib, time
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, AQUI)
from episodios import EPISODIOS
RAIZ = os.path.abspath(AQUI + "../../..") + "/"
REDES = RAIZ + "produccion/redes/"
TRABAJO = os.getenv("TRABAJO", "/tmp/orbi_heroes") + "/"
SALIDA = RAIZ + "entregables/redes/heroes/"
FPS, SR, COLA_SELLO = 30, 48000, 3.4
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
dur = lambda f: float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x)
rng = np.random.default_rng(11)
def sala(x, seg=1.2, g=0.25):
    n = int(seg * SR); ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n)); ir = lp(ir, 5000)
    return x + fftconvolve(x, ir)[:len(x)] * g / np.sqrt(n) * 30

# ---------- Voces (Microsoft, edge-tts) con caché y efecto por personaje
async def voces(ep, W):
    import edge_tts
    os.makedirs(W + "voces", exist_ok=True); os.makedirs(TRABAJO + "cache", exist_ok=True)
    k = 0
    for pl in ep["planos"]:
        for (q, txt, _, _) in pl.get("lineas", []):
            voz, vel, tono = ep["reparto"][q]["voz"]
            h = hashlib.md5(f"{voz}{vel}{tono}{txt}".encode()).hexdigest(); c = TRABAJO + f"cache/{h}.wav"
            if not os.path.exists(c):
                for intento in range(4):
                    try: await edge_tts.Communicate(txt, voz, rate=vel, pitch=tono, proxy=os.getenv("HTTPS_PROXY")).save(c + ".mp3"); break
                    except Exception as e: print("reintento voz", e); await asyncio.sleep(2 ** intento)
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", c + ".mp3", "-af",
                    "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                    "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5,loudnorm=I=-16:TP=-1.5,aresample=48000", "-ac", "1", c], check=True)
            subprocess.run(["cp", c, W + f"voces/l{k:02d}.wav"], check=True); k += 1
    t, k, planos = 0.0, 0, []
    for pl in ep["planos"]:
        ini, lineas = t, []
        for (q, txt, pausa, _) in pl.get("lineas", []):
            t += pausa; d = round(dur(W + f"voces/l{k:02d}.wav"), 2)
            lineas.append({"k": k, "quien": q, "txt": txt, "ini": round(t, 2), "fin": round(t + d, 2)}); t += d; k += 1
        fin = max(ini + pl.get("min", 0), t + pl.get("cola", 0.45)); t = fin
        planos.append({"ini": round(ini, 3), "fin": round(fin, 3), "lineas": lineas})
    return {"planos": planos, "sello": round(t, 2), "dur": round(t + COLA_SELLO, 2)}

# ---------- Página que dibuja cada cuadro
def pagina(ep, lin, W):
    leer = lambda p: open(p).read()
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}<style>{leer(AQUI + "estilo.css")}</style></head><body>
<div id="cine"><div id="fondo"></div><div id="mundo"></div></div><div id="pantalla"></div><div id="vineta"></div>
<div id="titulo"><b></b><small></small></div><div id="letrero"></div><div id="pedido"></div><div id="sub"></div>
<div id="flash"></div><div id="negro"></div><div id="barras"></div><div id="gancho"></div>
<div id="sello"><div id="o-final"></div><div id="frase"></div><div id="logo"><b></b><span></span></div></div>
<canvas id="grano" width="360" height="640"></canvas>
<script>
const EP = {json.dumps(ep, ensure_ascii=False)};
const LINEA = {json.dumps(lin, ensure_ascii=False)};
{leer(REDES + "orbi.js")}
{leer(REDES + "hierro/armadura.js")}
{leer(REDES + "viernes/personajes.js")}
{leer(REDES + "comision2/personajes_comi.js")}
{leer(AQUI + "personajes.js")}
{leer(AQUI + "escenarios.js")}
{leer(AQUI + "escena.js")}
</script></body></html>'''
    open(W + "cuadro.html", "w").write(html)

async def abrir(p, W):
    br = await p.chromium.launch(executable_path=CHROME)
    pg = await br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
    await pg.goto("file://" + W + "cuadro.html"); await pg.wait_for_timeout(900); return br, pg

async def obrero(W, i, a, b):
    from playwright.async_api import async_playwright
    seg = W + f"seg{i}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", seg], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        br, pg = await abrir(p, W)
        for f in range(a, b): await pg.evaluate("([t,f]) => render(t,f)", [f / FPS, f]); ff.stdin.write(await pg.screenshot(type="jpeg", quality=95))
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
        for t in ts: await pg.evaluate("([t,f]) => render(t,f)", [t, int(t * FPS)]); await pg.screenshot(path=W + f"p_{t:05.2f}.jpg", type="jpeg", quality=80)
        await br.close()

# ---------- Sonido de cine: música por plano, efectos por evento y voces con su tratamiento
def sonido(ep, lin, W):
    DUR = lin["dur"] + 0.2; N = int(DUR * SR)
    M, FX, VZ = (np.zeros((N, 2)) for _ in range(3))
    def hz(n):
        d = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
        return 440 * 2 ** ((d[n[:-1]] + (int(n[-1]) - 4) * 12) / 12)
    def pon(buf, x, a, g=1.0, pan=0.0):
        i = int(a * SR); n = min(len(x), N - i)
        if i < 0: x = x[-i:]; n = min(len(x), N); i = 0
        if n > 0: buf[i:i + n, 0] += x[:n] * g * (1 - pan); buf[i:i + n, 1] += x[:n] * g * (1 + pan)
    def env(n, at=0.004, caida=6): tl = np.arange(n) / SR; return np.exp(-tl * caida) * np.minimum(1, tl / at)
    def tono(f, d, caida=6, armo=(1, .3, .1), g=1.0):
        n = int(d * SR); tl = np.arange(n) / SR
        return sum(a * np.sin(2 * np.pi * f * (k + 1) * tl) for k, a in enumerate(armo)) * env(n, 0.004, caida) * g
    def sierra(f, d, corte=1800, g=0.1, at=0.05, rel=0.3, vib=0.004):
        n = int(d * SR); tl = np.arange(n) / SR; x = np.zeros(n)
        for dd in (0.995, 1.0, 1.005): x += 2 * ((np.cumsum(f * dd * (1 + vib * np.sin(2 * np.pi * 5.2 * tl))) / SR + rng.random()) % 1) - 1
        return lp(x, corte) * g / 3 * np.minimum(1, tl / at) * np.minimum(1, np.maximum(0, d - tl) / rel)
    def acorde(notas, d, g=0.1, corte=2000, at=0.25): return sum(sierra(hz(n), d, corte, g / len(notas), at, 0.5) for n in notas)
    def metal(notas, d, g=0.12):   # metales: sierra con ataque suave
        n = int(d * SR); tl = np.arange(n) / SR; x = np.zeros(n)
        for nt in notas: x += 2 * ((np.cumsum(np.full(n, hz(nt))) / SR) % 1) - 1
        y = lp(x, 2400) * (0.5 + 0.5 * np.minimum(1, tl / 0.08))
        return y * g / len(notas) * np.minimum(1, np.maximum(0, d - tl) / 0.15)
    def taiko(f=55, d=1.0, g=1.0):
        n = int(d * SR); tl = np.arange(n) / SR
        return (np.sin(2 * np.pi * (f * 2.2 * np.exp(-tl * 18) + f) * tl) * np.exp(-tl * 4) + lp(rng.standard_normal(n), 900) * np.exp(-tl * 30) * 0.5) * g
    def caja(g=0.3): n = int(0.25 * SR); return bp(rng.standard_normal(n), 900, 6000) * env(n, 0.001, 18) * g + tono(190, 0.25, 20, (1,), g * 0.6)
    def ruido(d, a, b, g): n = int(d * SR); return bp(rng.standard_normal(n), a, b) * g
    def braam(a, g=0.5, d=3.0):
        n = int(d * SR); tl = np.arange(n) / SR; x = np.zeros(n)
        for nt in ("A1", "A2", "E2"): x += 2 * ((np.cumsum(np.full(n, hz(nt) * (1 + 0.002 * rng.standard_normal()))) / SR) % 1) - 1
        x = lp(x, 900) * np.minimum(1, tl / 0.05) * np.exp(-tl * 0.9); pon(M, x * g / 3, a); pon(FX, taiko(42, 1.6, 0.9), a)
    def ostinato(a, b, bpm, notas, g=0.07, corte=2200):
        paso = 60 / bpm / 4; tt, k = a, 0
        while tt < b - 0.05: pon(M, sierra(hz(notas[k % len(notas)]), paso * 0.9, corte, g, 0.005, 0.03), tt, 1, 0.15 * np.sin(k)); tt += paso; k += 1
    def tambores(a, b, bpm, g=0.6):
        compas = 60 / bpm * 4; tt = a
        while tt < b - 0.1:
            for off, gg in ((0, 1), (60 / bpm * 1.5, 0.6), (60 / bpm * 2, 0.8)): pon(FX, taiko(50, 0.8, g * gg), tt + off)
            pon(FX, caja(0.22 * g), tt + 60 / bpm); pon(FX, caja(0.22 * g), tt + 60 / bpm * 3); tt += compas
    def piano(a, b, notas, cada, g=0.12):
        tt, k = a, 0
        while tt < b - 0.1: pon(M, tono(hz(notas[k % len(notas)]), 2.0, 2.2, (1, .45, .2, .1), g), tt, 1, 0.2 * np.sin(k)); tt += cada; k += 1
    CUES = {}
    def cue(nombre):
        def r(f): CUES[nombre] = f; return f
        return r
    @cue("misterio")
    def _(a, b): pon(M, acorde(["A1", "E2", "A2"], b - a + 0.6, 0.22, 500, 0.8), a); piano(a + 0.3, b, ["E5", "C5", "B4", "G4"], 1.3, 0.07)
    @cue("tension")
    def _(a, b): ostinato(a, b, 132, ["A2", "A2", "C3", "A2"], 0.06, 1500); pon(M, acorde(["A1", "E2"], b - a + 0.4, 0.15, 400, 0.5), a)
    @cue("titulo")
    def _(a, b): braam(a + 0.15, 0.6, b - a + 1.5); pon(M, acorde(["A3", "C4", "E4", "A4"], b - a + 0.8, 0.08, 3000, 0.6), a + 0.2)
    @cue("villano")
    def _(a, b):
        paso, tt, k = 60 / 112 / 2, a, 0
        notas = ["D2", "D2", "F2", "E2", "D2", "A1", "C#2", "D2"]
        while tt < b - 0.05: pon(M, sierra(hz(notas[k % 8]), paso * 0.8, 700, 0.22, 0.01, 0.05), tt); tt += paso; k += 1
        piano(a, b, ["D5", "F5", "A5", "G#5"], 60 / 112, 0.05)
    @cue("heroe")
    def _(a, b):
        seq = [["C3", "G3", "C4", "E4"], ["G2", "D3", "G3", "B3"], ["A2", "E3", "A3", "C4"], ["F2", "C3", "F3", "A3"]]
        tt, k = a, 0
        while tt < b - 0.1: pon(M, acorde(seq[k % 4], min(2.4, b - tt + 0.4), 0.14, 2600, 0.15), tt); pon(FX, taiko(46, 1.0, 0.5), tt); tt += 1.9; k += 1
        mel = [("G4", 0.3), ("C5", 0.3), ("E5", 0.6), ("D5", 0.3), ("C5", 0.3), ("G5", 1.2)]; tt = a + 0.1
        for nt, d in mel:
            if tt > b: break
            pon(M, metal([nt, nt[:-1] + str(int(nt[-1]) - 1)], d + 0.1, 0.22), tt); tt += d
    @cue("accion")
    def _(a, b): ostinato(a, b, 150, ["D3", "D3", "F3", "D3", "A3", "D3", "G3", "F3"], 0.07, 2600); tambores(a, b, 150, 0.7); pon(M, acorde(["D2", "A2"], b - a, 0.12, 600, 0.1), a)
    @cue("triste")
    def _(a, b): piano(a, b, ["A4", "E5", "C5", "B4", "F4", "C5", "A4", "G4"], 0.75, 0.1); pon(M, acorde(["A2", "E3", "C4"], b - a + 0.5, 0.08, 1200, 1.0), a)
    @cue("comico")
    def _(a, b):
        n = int(2.4 * SR); tl = np.arange(n) / SR; f = 233 * 2 ** (-tl / 2.4 * 0.6) * (1 + 0.02 * np.sin(2 * np.pi * 6 * tl))
        pon(M, lp(2 * ((np.cumsum(f) / SR) % 1) - 1, 1200) * 0.12 * np.minimum(1, (2.4 - tl) / 0.3), a + 0.1)
    @cue("novela")
    def _(a, b): pon(M, acorde(["A2", "E3", "A3", "C4", "E4"], b - a + 0.4, 0.2, 2200, 0.05), a); pon(FX, taiko(45, 1.4, 0.7), a); piano(a + 0.4, b, ["A4", "C5", "E5", "C5", "B4", "D5", "G#4", "B4"], 0.32, 0.06)
    @cue("romance")
    def _(a, b):
        seq = [["F3", "A3", "C4", "E4"], ["D3", "F3", "A3", "C4"], ["A#2", "D3", "F3", "A3"], ["C3", "E3", "G3", "C4"]]; tt, k = a, 0
        while tt < b - 0.1: pon(M, acorde(seq[k % 4], min(2.6, b - tt + 0.5), 0.07, 1600, 0.6), tt); tt += 2.2; k += 1
        piano(a + 0.2, b, ["A4", "C5", "F5", "E5", "D5", "C5", "A4", "G4"], 0.55, 0.08)
    @cue("jazz")
    def _(a, b):
        bajo = ["D2", "F2", "A2", "C3", "G2", "B2", "D3", "F3", "C2", "E2", "G2", "B2"]; paso, tt, k = 60 / 132, a, 0
        while tt < b - 0.05:
            pon(M, tono(hz(bajo[k % 12]), paso * 0.95, 4, (1, .5, .2), 0.22), tt)
            if k % 2 == 1: pon(FX, ruido(0.08, 6000, 12000, 0.03) * np.exp(-np.arange(int(0.08 * SR)) / SR * 40), tt)
            if k % 4 == 0: pon(M, acorde([["F4", "A4", "C5", "E5"], ["B3", "D4", "F4", "A4"], ["E4", "G4", "B4", "D5"]][(k // 4) % 3], paso * 1.6, 0.05, 3000, 0.01), tt + paso * 0.66)
            tt += paso; k += 1
        piano(a + 0.5, b, ["A5", "G5", "E5", "D5", "C5", "D5", "E5", "G5"], 60 / 132 * 1.5, 0.06)
    @cue("synth")
    def _(a, b):
        seq = [["D2", "A2", "D3", "F3"], ["A#1", "F2", "A#2", "D3"], ["C2", "G2", "C3", "E3"]]; tt, k = a, 0
        while tt < b - 0.1: pon(M, sala(acorde(seq[k % 3], min(4.0, b - tt + 1.0), 0.16, 1400, 1.2), 2.5, 0.5), tt); tt += 3.2; k += 1
        pon(M, sala(metal(["D4", "A4"], min(3.0, b - a), 0.12), 3.0, 0.6), a + 0.8)
    @cue("romcom")
    def _(a, b):
        tt, k, notas = a, 0, ["C5", "E5", "G5", "E5", "F5", "A5", "C6", "A5", "G5", "B5", "D6", "B5"]
        while tt < b - 0.05: pon(M, tono(hz(notas[k % 12]), 0.25, 14, (1, .3), 0.09), tt, 1, 0.2 * np.sin(k)); tt += 60 / 140 / 2; k += 1
        ostinato(a, b, 140, ["C3", "C3", "G2", "G2", "A2", "A2", "F2", "G2"], 0.05, 900)
    @cue("corporativo")
    def _(a, b):
        seq = [["C3", "G3", "D4", "E4"], ["A2", "E3", "B3", "C4"], ["F2", "C3", "G3", "A3"], ["G2", "D3", "A3", "B3"]]; tt, k = a, 0
        while tt < b - 0.1: pon(M, acorde(seq[k % 4], min(2.9, b - tt + 0.6), 0.09, 1800, 0.5), tt); tt += 2.4; k += 1
        notas = ["E5", "G5", "D5", "G5", "C5", "G5", "B4", "G5"]; tt, k = a + 0.1, 0
        while tt < b - 0.05: pon(M, tono(hz(notas[k % 8]), 0.9, 4, (1, .35, .12), 0.045), tt, 1, 0.25 * np.sin(k)); tt += 60 / 100 / 2; k += 1
        tt = a
        while tt < b - 0.1: pon(FX, taiko(52, 0.5, 0.18), tt); tt += 60 / 100
    @cue("pelicula")
    def _(a, b):
        pon(M, acorde(["D2", "A2", "D3"], b - a + 0.8, 0.16, 700, 1.2), a)
        tt = a + 0.2
        while tt < b - 0.1: pon(FX, taiko(44, 0.7, 0.32), tt); pon(FX, taiko(44, 0.5, 0.18), tt + 0.34); tt += 1.3
        piano(a + 0.5, b, ["D5", "A4", "F5", "E5", "D5", "A4", "C5", "A4"], 0.65, 0.06)
        n = int(min(2.0, b - a) * SR); pon(FX, hp(rng.standard_normal(n), 2500) * np.linspace(0, 1, n) ** 3 * 0.05, max(a, b - 2.0))
    @cue("esperanza")
    def _(a, b):
        seq = [["D3", "A3", "D4", "F#4"], ["B2", "F#3", "B3", "D4"], ["G2", "D3", "G3", "B3"], ["A2", "E3", "A3", "C#4"]]; tt, k = a, 0
        while tt < b - 0.1: pon(M, acorde(seq[k % 4], min(2.8, b - tt + 0.6), 0.13, 2600, 0.4), tt); pon(FX, taiko(46, 0.9, 0.25), tt); tt += 2.2; k += 1
        piano(a + 0.2, b, ["F#5", "A5", "D6", "A5", "E5", "A5", "C#6", "A5"], 0.275, 0.05)
    @cue("fin")
    def _(a, b): pon(M, acorde(["C3", "G3", "C4", "E4", "G4"], b - a + 1.0, 0.18, 3000, 0.1), a); pon(FX, taiko(44, 1.6, 0.9), a)
    P = lin["planos"]
    for pl, L in zip(ep["planos"], P):
        a, b = L["ini"], L["fin"]
        if pl.get("titulo"): CUES["titulo"](a, b)
        if pl.get("musica"): CUES[pl["musica"]](a, b)
        if pl.get("trans") in ("flash", "barrido"): n = int(0.5 * SR); pon(FX, hp(rng.standard_normal(n), 1500) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.12, a - 0.25)
        tF = lambda fx, c="": (L["lineas"][fx["linea" + c]]["ini"] + fx.get("dt" + c, 0)) if fx.get("linea" + c) is not None else (a + fx.get("p" + c, 0 if not c else 1) * (b - a))
        for fx in pl.get("fx", []):
            T0, T1, ty = tF(fx), tF(fx, "1"), fx["tipo"]
            if ty == "lluvia": pon(FX, ruido(b - a + 0.3, 400, 7000, 0.05 * fx.get("k", 1)), a - 0.1)
            if ty == "rayo": pon(FX, ruido(0.15, 1500, 9000, 0.5), T0); pon(FX, lp(rng.standard_normal(int(3 * SR)), 180) * np.exp(-np.linspace(0, 4, int(3 * SR))) * 2.5, T0 + 0.1)
            if ty == "vidrios":
                pon(FX, ruido(0.4, 3000, 12000, 0.6) * env(int(0.4 * SR), 0.001, 8), T0); pon(FX, taiko(60, 0.6, 0.8), T0)
                for i in range(14): pon(FX, tono(2500 + rng.random() * 3000, 0.3, 14, (1, .5), 0.08), T0 + 0.2 + rng.random() * 1.0)
            if ty == "pum": pon(FX, taiko(48, 0.9, 1.0), T0); pon(FX, ruido(0.2, 800, 8000, 0.5) * env(int(0.2 * SR), 0.001, 20), T0)
            if ty == "paginas":
                for i in range(fx.get("n", 10)): pon(FX, ruido(0.18, 1500, 6000, 0.08) * np.sin(np.linspace(0, np.pi, int(0.18 * SR))), T0 + (T1 - T0) * 0.7 * i / fx.get("n", 10), 1, 0.3 * np.sin(i))
            if ty == "radar":
                tt = T0
                while tt < T1: pon(FX, sala(tono(1250, 0.8, 5, (1,), 0.1), 1.5, 0.6), tt); tt += 1.4
            if ty == "onda":
                tt = T0
                while tt < T1: pon(FX, tono(880, 0.4, 8, (1,), 0.04), tt); tt += 0.9
            if ty == "qr":
                for i in range(len(fx["mesas"])): tt = T0 + (T1 - T0) * i / len(fx["mesas"]) + 0.3; pon(FX, tono(hz("E6"), 0.25, 10, (1,), 0.15), tt); pon(FX, tono(hz("B6"), 0.35, 8, (1,), 0.12), tt + 0.07)
            if ty == "disparo":
                n = int(0.35 * SR); tl = np.arange(n) / SR; pon(FX, np.sin(2 * np.pi * np.cumsum(300 + 2600 * tl / 0.35) / SR) * 0.15, T0 - 0.05)
                pon(FX, taiko(40, 1.4, 1.1), T0 + 0.32); pon(FX, ruido(0.6, 200, 5000, 0.4) * env(int(0.6 * SR), 0.002, 6), T0 + 0.32)
                for i in range(8): pon(FX, tono(hz("E6") * (1 + 0.1 * rng.random()), 0.3, 10, (1, .6), 0.06), T0 + 0.5 + i * 0.07)
            if ty == "monedas":
                for i in range(fx.get("n", 12)): pon(FX, tono(hz("C7") * (1 + 0.08 * rng.random()), 0.3, 9, (1, .5), 0.07), T0 + (T1 - T0) * i / fx.get("n", 12))
            if ty == "velocidad": n = int((T1 - T0) * SR); pon(FX, bp(rng.standard_normal(n), 200, 3000) * np.sin(np.linspace(0, np.pi, n)) * 0.35, T0)
            if ty == "confeti": pon(FX, ruido(0.1, 500, 6000, 0.4), T0); [pon(FX, tono(hz(nn), 0.5, 5, (1, .3), 0.1), T0 + 0.1 + i * 0.08) for i, nn in enumerate(["C6", "E6", "G6", "C7"])]
            if ty == "destello": [pon(FX, tono(hz("C7") * (1 + 0.5 * i), 1.2, 3, (1,), 0.05), T0 + i * 0.05) for i in range(5)]
        for k_, (q, txt, _, e) in enumerate(pl.get("lineas", [])):
            if e.get("pedido"): t0 = L["lineas"][k_]["ini"]; pon(FX, tono(hz("G5"), 0.5, 5, g=0.22), t0); pon(FX, tono(hz("D6"), 0.8, 4, g=0.22), t0 + 0.12)
    S = lin["sello"]; CUES["fin"](S, S + COLA_SELLO); pon(FX, tono(hz("E6"), 2.0, 2, g=0.25), S + 0.4); pon(FX, tono(hz("B6"), 2.0, 2, g=0.18), S + 0.45)
    # Voces con su tratamiento
    for pl, L in zip(ep["planos"], P):
        for l in L["lineas"]:
            sr, v = wavfile.read(W + f"voces/l{l['k']:02d}.wav"); v = v.astype(float) / 32767; v = v if v.ndim == 1 else v.mean(1)
            efecto = ep["reparto"][l["quien"]].get("fx")
            if efecto == "narrador": v = sala(lp(v, 7000) + 0.25 * lp(v, 220), 0.8, 0.12)
            elif efecto == "villano": v = sala(v + 0.3 * lp(v, 250), 1.6, 0.35)
            elif efecto == "radio": v = np.tanh(bp(v, 350, 3400) * 2.2) * 0.7; v = sala(v, 0.6, 0.1)
            elif efecto == "susurro": v = sala(hp(v, 300) * 0.55, 2.0, 0.6)
            else: v = sala(v, 0.9, 0.15)
            pon(VZ, v, l["ini"], 1.0, ep["reparto"][l["quien"]].get("pan", 0))
    activo = np.convolve((np.abs(VZ[:, 0]) > 0.02).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    duck = 1 - 0.6 * np.clip(activo * 4, 0, 1)
    t = np.arange(N) / SR
    def final(m):
        m = np.tanh(m * 1.1) * 0.95; m *= np.minimum(1, np.maximum(0, DUR - t) / 0.8)[:, None]; return m / (np.max(np.abs(m)) / 0.93)
    wavfile.write(W + "sonido.wav", SR, (final(M * duck[:, None] * 0.9 + FX * 0.8 + VZ * 1.5) * 32767).astype(np.int16))
    wavfile.write(W + "sonido_sin_musica.wav", SR, (final(FX * 0.6 + VZ * 1.5) * 32767).astype(np.int16))

def hacer(eid):
    ep = EPISODIOS[eid]; W = TRABAJO + eid + "/"; os.makedirs(W, exist_ok=True); t0 = time.time()
    lin = asyncio.run(voces(ep, W)); json.dump(lin, open(W + "linea.json", "w"), ensure_ascii=False, indent=1)
    pagina(ep, lin, W)
    if os.getenv("PRUEBA"):
        ts = [float(x) for x in os.getenv("PRUEBA").split(",")] if os.getenv("PRUEBA") != "planos" else [round((p["ini"] + p["fin"]) / 2, 2) for p in lin["planos"]]
        asyncio.run(prueba(W, ts)); print("pruebas en", W, ts); return
    sonido(ep, lin, W); asyncio.run(imagen(W, lin["dur"]))
    os.makedirs(SALIDA, exist_ok=True)
    for son, nombre in (("sonido.wav", f"{eid}.mp4"), ("sonido_sin_musica.wav", f"{eid}-sin-musica.mp4")):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + son, "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", SALIDA + nombre], check=True)
    print("listo", eid, lin["dur"], "s de video en", round(time.time() - t0), "s")

if __name__ == "__main__":
    ids = list(EPISODIOS) if sys.argv[1:] == ["todos"] else sys.argv[1:]
    for eid in ids: hacer(eid)
