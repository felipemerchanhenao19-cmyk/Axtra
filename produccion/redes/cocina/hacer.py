"""«Orbi en la cocina»: arma un capítulo completo (voces, imagen 1080x1920, música, efectos y mezcla).
  python hacer.py <id|todos> [<id> ...]        →  entregables/redes/cocina/<id>.mp4
  PRUEBA=1,4.5,9 python hacer.py <id>          →  solo cuadros de prueba en la carpeta de trabajo
Los guiones están en episodios.py."""
import sys, os, json, asyncio, subprocess, hashlib, time
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, AQUI)
from episodios import EPISODIOS
RAIZ = os.path.abspath(AQUI + "../../..") + "/"
TRABAJO = os.getenv("TRABAJO", "/tmp/orbi_cocina") + "/"
SALIDA = RAIZ + "entregables/redes/cocina/"
FPS, SR, COLA_SELLO = 24, 48000, 3.0
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
dur = lambda f: float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))

# ---------- Voces (Microsoft, edge-tts) con caché por texto y voz
async def voces(ep, W):
    import edge_tts
    os.makedirs(W + "voces", exist_ok=True); os.makedirs(TRABAJO + "cache", exist_ok=True)
    for i, (q, txt, _, _) in enumerate(ep["lineas"]):
        voz, vel, tono = ep["reparto"][q]["voz"]
        h = hashlib.md5(f"{voz}{vel}{tono}{txt}".encode()).hexdigest(); c = TRABAJO + f"cache/{h}.wav"
        if not os.path.exists(c):
            for intento in range(4):
                try: await edge_tts.Communicate(txt, voz, rate=vel, pitch=tono, proxy=os.getenv("HTTPS_PROXY")).save(c + ".mp3"); break
                except Exception as e: print("reintento voz", e); await asyncio.sleep(2 ** intento)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", c + ".mp3", "-af",
                "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                "highpass=f=80,acompressor=threshold=-20dB:ratio=2.5,loudnorm=I=-16:TP=-1.5,aresample=48000", "-ac", "1", c], check=True)
        subprocess.run(["cp", c, W + f"voces/l{i:02d}.wav"], check=True)
    t, lineas = 0.35, []
    for i, (q, txt, pausa, _) in enumerate(ep["lineas"]):
        t += pausa; d = round(dur(W + f"voces/l{i:02d}.wav"), 2)
        lineas.append({"i": i, "quien": q, "txt": txt, "ini": round(t, 2), "fin": round(t + d, 2)}); t += d
    sello = round(t + 0.9, 2)
    return {"lineas": lineas, "sello": sello, "dur": round(sello + COLA_SELLO, 2)}

# ---------- Página HTML que dibuja cada cuadro
def pagina(ep, lin, W):
    css = open(AQUI + "estilo.css").read()
    html = f'''<!doctype html><html><head><meta charset="utf-8">{open(RAIZ + "produccion/videos/fuentes.html").read()}<style>{css}</style></head><body>
<div id="escena"></div><div id="tinte"></div><div id="rayas"></div>
<div id="serie"></div><div id="gancho"></div><div id="sub"></div><div id="chip"></div><div id="pedido"></div>
<div id="sello"><div id="o-final"></div><div id="frase"></div><div id="logo"><b></b><span></span></div></div>
<div id="vineta"></div><canvas id="grano" width="360" height="640"></canvas>
<script>
const EP = {json.dumps(ep, ensure_ascii=False)};
const LINEA = {json.dumps(lin, ensure_ascii=False)};
{open(RAIZ + "produccion/redes/orbi.js").read()}
{open(RAIZ + "produccion/redes/comision2/personajes_comi.js").read().split("function rosa")[0]}
{open(AQUI + "personajes.js").read()}
{open(AQUI + "escena.js").read()}
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
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", seg], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        br, pg = await abrir(p, W)
        for f in range(a, b): await pg.evaluate("([t,f]) => render(t,f)", [f / FPS, f]); ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
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

# ---------- Sonido: música sintetizada por estilo, efectos por evento y voces con «ducking»
def sonido(ep, lin, W):
    DUR = lin["dur"] + 0.2; N = int(DUR * SR); rng = np.random.default_rng(7)
    M, FX, VZ = (np.zeros((N, 2)) for _ in range(3))
    def hz(n):
        d = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
        return 440 * 2 ** ((d[n[:-1]] + (int(n[-1]) - 4) * 12) / 12)
    lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
    hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
    def pon(buf, x, a, g=1.0, pan=0.0):
        i = int(a * SR); n = min(len(x), N - i)
        if n > 0 and i >= 0: buf[i:i + n, 0] += x[:n] * g * (1 - pan); buf[i:i + n, 1] += x[:n] * g * (1 + pan)
    def tono(f, d, caida=6, armo=(1, .3, .1), g=1.0):
        n = int(d * SR); tl = np.arange(n) / SR
        return sum(a * np.sin(2 * np.pi * f * (k + 1) * tl) for k, a in enumerate(armo)) * np.exp(-tl * caida) * np.minimum(1, tl / 0.004) * g
    def cuerdas(notas, d, g=0.1, corte=2200):
        n = int(d * SR); tl = np.arange(n) / SR; x = np.zeros(n)
        for nota in notas:
            for dd in (0.996, 1.004):
                f = hz(nota) * dd * (1 + 0.004 * np.sin(2 * np.pi * 5.3 * tl)); x += 2 * ((np.cumsum(np.full(n, f)) / SR + rng.random()) % 1) - 1
        return lp(x, corte) * g / len(notas) * np.minimum(1, tl / 0.25) * np.minimum(1, np.maximum(0, d - tl) / 0.5)
    def golpe(f=55, d=0.8, g=1.0):
        n = int(d * SR); tl = np.arange(n) / SR
        return (np.sin(2 * np.pi * (f * 1.6 * np.exp(-tl * 12) + f) * tl) * np.exp(-tl * 5) + lp(rng.standard_normal(n), 1500) * np.exp(-tl * 25) * 0.3) * g
    def ruido(d, a, b, g): n = int(d * SR); return lp(hp(rng.standard_normal(n), a), b) * g
    def patron(ini, fin, bpm, notas, g, caida=9, armo=(1, .25, .1), cada=1, buf=None):
        paso = 60 / bpm / 2; k = 0; tt = ini
        while tt < fin - 0.05:
            if k % cada == 0: pon(M if buf is None else buf, tono(hz(notas[k % len(notas)]), 0.6, caida, armo, g), tt, 1, 0.2 * np.sin(k))
            tt += paso; k += 1
    def acordes(ini, fin, seq, d, g, corte=2000):
        tt, k = ini, 0
        while tt < fin - 0.1: pon(M, cuerdas(seq[k % len(seq)], min(d + 0.4, fin - tt + 0.3), g, corte), tt); tt += d; k += 1
    def hihat(ini, fin, bpm, g=0.03):
        tt = ini
        while tt < fin: pon(M, ruido(0.05, 6000, 12000, g) * np.exp(-np.arange(int(0.05 * SR)) / SR * 60), tt); tt += 60 / bpm / 2
    def alegre(ini, fin):
        patron(ini, fin, 128, ["C4", "E4", "G4", "A4", "F4", "A4", "C5", "A4", "G4", "B4", "D5", "B4"], 0.09, 10)
        patron(ini, fin, 64, ["C3", "F3", "G3", "C3"], 0.12, 4, (1, .5, .2)); hihat(ini, fin, 128, 0.025)
    L, S = lin["lineas"], lin["sello"]; ev = lambda l: ep["lineas"][l["i"]][3]
    giro = next((l["ini"] - 0.2 for l in L if ev(l).get("pedido")), S)
    m = ep.get("musica", "novela")
    if m == "novela":
        pon(M, cuerdas(["A2", "E3", "A3", "C4", "E4"], 2.2, 0.4), 0.0); pon(FX, golpe(45, 1.6, 0.7), 0.0)
        patron(1.2, giro, 96, ["A3", "C4", "E4", "C4", "D3", "F3", "A3", "F3", "E3", "G#3", "B3", "G#3"], 0.1, 6, (1, .35, .15))
        acordes(1.2, giro, [["A2", "E3", "C4"], ["D3", "A3", "F4"], ["E3", "B3", "G#4"]], 2.0, 0.06)
    elif m == "triste":
        patron(0.0, giro, 72, ["A3", "E4", "C5", "E4", "F3", "C4", "A4", "C4", "G3", "D4", "B4", "D4"], 0.1, 3, (1, .4, .2))
        acordes(0.0, giro, [["A2", "E3", "C4"], ["F2", "C3", "A3"], ["G2", "D3", "B3"]], 2.6, 0.05, 1500)
    elif m == "suave":
        patron(0.0, giro, 84, ["F3", "A3", "C4", "E4", "D3", "F3", "A3", "C4", "G3", "B3", "D4", "F4"], 0.08, 4, (1, .4, .2))
        hihat(0.0, giro, 84, 0.015)
    elif m == "debate":
        patron(0.0, giro, 124, ["A2", "A2", "A2", "C3", "A2", "A2", "G2", "A2"], 0.16, 7, (1, .6, .3))
        tt = 0.0
        while tt < giro: pon(FX, golpe(48, 0.6, 0.35), tt); tt += 60 / 124 * 4
        acordes(0.0, giro, [["A3", "E4"], ["A3", "F4"]], 1.94, 0.05, 2600)
    elif m == "terror":
        pon(M, cuerdas(["A1", "A#1", "E2"], giro + 0.5, 0.18, 600), 0.0)
        tt = 0.4
        while tt < giro: pon(FX, golpe(40, 0.25, 0.5), tt); pon(FX, golpe(38, 0.25, 0.35), tt + 0.22); tt += 1.1
        patron(0.0, giro, 50, ["E6", "C6", "D#6", "B5", "E6", "G6", "F#6", "B5"], 0.05, 3, (1, .1, 0))
        n = int(1.6 * SR); pon(FX, hp(rng.standard_normal(n), 2500) * np.linspace(0, 1, n) ** 2 * np.exp(-np.linspace(0, 1, n) * 0.5) * 0.06, 0.0)
    elif m == "reinado":
        for k, n in enumerate(["C4", "E4", "G4", "C5"]): pon(M, tono(hz(n), 0.8, 3, (1, .6, .4, .2), 0.18), k * 0.14)
        pon(M, cuerdas(["C3", "G3", "C4", "E4", "G4"], 1.6, 0.18, 3000), 0.56)
        patron(1.2, giro, 112, ["C4", "E4", "G4", "E4", "F4", "A4", "C5", "A4"], 0.08, 8); hihat(1.2, giro, 112, 0.02)
        for k in range(20): pon(FX, tono(hz("C7") * (1 + 0.05 * k), 0.4, 6, g=0.03), 0.3 + k * 0.05)
    alegre(giro, S)
    # Efectos por evento
    for l in L:
        e, a = ev(l), l["ini"]
        if "orbi" in e.get("entra", []): pon(FX, tono(hz("E6"), 1.8, 2.5, g=0.3), a - 0.25); pon(FX, tono(hz("B6"), 1.8, 2.5, g=0.18), a - 0.2)
        elif e.get("entra"):
            n = int(0.5 * SR); pon(FX, hp(rng.standard_normal(n), 1500) * np.sin(np.linspace(0, np.pi, n)) * 0.08, a - 0.3)
        if e.get("drama"):
            for k, (n1, n2) in enumerate([("D3", "A3"), ("D#3", "A3"), ("D3", "A#3")]): pon(M, cuerdas([n1, n2], 0.7 if k < 2 else 1.3, 0.5), a + k * 0.32); pon(FX, golpe(50 + 4 * k, 1.0, 0.7 + 0.1 * k), a + k * 0.32)
        if e.get("temblor"): pon(FX, golpe(42, 1.0, 1.0), a); pon(FX, ruido(0.4, 80, 1200, 0.25), a)
        if e.get("chip"):
            if e.get("chipok") or "%" in e["chip"]:
                for k in range(4): pon(FX, ruido(0.08, 2500, 9000, 0.05), a + 0.2 + k * 0.06)
                pon(FX, tono(hz("C7"), 0.6, 5, g=0.2), a + 0.45); pon(FX, tono(hz("G6"), 0.7, 5, g=0.15), a + 0.5)
            else: pon(FX, tono(hz("A5"), 0.3, 8, g=0.15), a + 0.2)
        if e.get("pedido"): pon(FX, tono(hz("G5"), 0.5, 5, g=0.22), a); pon(FX, tono(hz("D6"), 0.8, 4, g=0.22), a + 0.12)
        if e.get("sale"):
            n = int(0.6 * SR); pon(FX, hp(rng.standard_normal(n), 900) * np.sin(np.linspace(0, np.pi, n)) * 0.12, a + 0.5); pon(FX, golpe(60, 0.8, 0.8), a + 1.3)
        for q, p in e.get("poses", {}).items():
            if p == "desmayo":
                n = int(0.8 * SR); tl = np.arange(n) / SR; pon(FX, np.sin(2 * np.pi * np.cumsum(1400 - 1100 * tl / 0.8) / SR) * 0.12 * np.exp(-tl * 1.5), a - 0.2); pon(FX, golpe(70, 0.5, 0.6), a + 0.45)
            if p == "brinco":
                for k in range(3):
                    n = int(0.25 * SR); tl = np.arange(n) / SR; pon(FX, np.sin(2 * np.pi * np.cumsum(220 + 500 * tl / 0.25) / SR) * 0.1 * np.exp(-tl * 6), a - 0.25 + k * 0.39)
    if ep.get("continuara"): pon(M, cuerdas(["A2", "E3", "A3", "C4"], 1.4, 0.35), S - 0.3); pon(FX, golpe(45, 1.2, 0.6), S - 0.3)
    pon(FX, tono(hz("E6"), 2.0, 2, g=0.3), S + 0.3); pon(FX, tono(hz("B6"), 2.0, 2, g=0.2), S + 0.35)
    pon(M, cuerdas(["C3", "G3", "C4", "E4", "G4"], COLA_SELLO, 0.14, 2800), S + 0.3)
    for l in L:
        sr, v = wavfile.read(W + f"voces/l{l['i']:02d}.wav"); v = v.astype(float) / 32767
        x = ep["reparto"][l["quien"]].get("x", 540); pon(VZ, v if v.ndim == 1 else v.mean(1), l["ini"], 1.0, float(np.clip((x - 540) / 1400, -0.25, 0.25)))
    activo = np.convolve((np.abs(VZ[:, 0]) > 0.02).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    duck = 1 - 0.55 * np.clip(activo * 4, 0, 1)
    ir = rng.standard_normal(SR) * np.exp(-np.linspace(0, 8, SR)) * 0.03
    for buf in (M, FX):
        for c in range(2): buf[:, c] += fftconvolve(buf[:, c], ir)[:N] * 0.5
    t = np.arange(N) / SR
    mez = M * duck[:, None] + FX * 0.9 + VZ * 1.6
    mez *= np.minimum(1, np.maximum(0, DUR - t) / 0.8)[:, None]
    mez /= np.max(np.abs(mez)) / 0.92
    wavfile.write(W + "sonido.wav", SR, (mez * 32767).astype(np.int16))
    # Versión sin música (para Instagram de empresa: se le pone un audio comercial desde la app)
    sm = FX * 0.6 + VZ * 1.6; sm /= np.max(np.abs(sm)) / 0.92
    wavfile.write(W + "sonido_sin_musica.wav", SR, (sm * 32767).astype(np.int16))

def hacer(eid):
    ep = EPISODIOS[eid]; W = TRABAJO + eid + "/"; os.makedirs(W, exist_ok=True); t0 = time.time()
    lin = asyncio.run(voces(ep, W)); json.dump(lin, open(W + "linea.json", "w"), ensure_ascii=False, indent=1)
    pagina(ep, lin, W)
    if os.getenv("PRUEBA"): asyncio.run(prueba(W, [float(x) for x in os.getenv("PRUEBA").split(",")])); print("pruebas en", W); return
    asyncio.run(imagen(W, lin["dur"])); sonido(ep, lin, W)
    os.makedirs(SALIDA, exist_ok=True)
    for son, nombre in (("sonido.wav", f"{eid}.mp4"), ("sonido_sin_musica.wav", f"{eid}-sin-musica.mp4")):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + son, "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", SALIDA + nombre], check=True)
    print("listo", eid, lin["dur"], "s de video en", round(time.time() - t0), "s")

if __name__ == "__main__":
    ids = list(EPISODIOS) if sys.argv[1:] == ["todos"] else sys.argv[1:]
    for eid in ids: hacer(eid)
