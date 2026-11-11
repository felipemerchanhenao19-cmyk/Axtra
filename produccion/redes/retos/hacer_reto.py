"""«Retos a la IA»: monta un video vertical con una grabación REAL del asistente de Apex (pantalla y respuestas del sistema en producción).
  python hacer_reto.py <carpeta de la grabación> <id>     →  entregables/redes/retos/<id>.mp4 (+ sin música y liviano)
  PRUEBA=1 …                                              →  solo cuadros de prueba
La grabación la hace grabar_reto.py (registro.json, cuadros/, c<i>.wav del cliente y orbi<i>.mp3 del asistente).
Solo se recortan las esperas entre turnos; lo que el asistente oye, responde y muestra no se toca."""
import sys, os, json, asyncio, subprocess, importlib.util
import numpy as np
from scipy.io import wavfile
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ, FPS, SR = motor.RAIZ, motor.FPS, motor.SR
dur = motor.dur

def linea_de_tiempo(G, reg, cfg):
    """Tramos [t_video, t_grabación, duración, quién, texto]: gancho, cada turno (cliente → asistente) y el recibo."""
    tr, t = [], 0.0
    tr.append(dict(v=t, g=reg["marcas"]["entrar"] + 1.2, d=cfg.get("gancho_seg", 2.4), quien="", txt="")); t += tr[-1]["d"]
    for l, r in zip(reg["linea"], reg["respuestas"]):
        d = l["dur"] + 0.25; tr.append(dict(v=t, g=l["ini"] - 0.1, d=d, quien="cliente", txt=l["txt"], k=l["i"])); t += d
        do = dur(G + f"orbi{r['k']}.mp3") + 0.35; tr.append(dict(v=t, g=l["habla"] - 0.15, d=do, quien="orbi", txt=r["texto"], k=r["k"])); t += do
    tr.append(dict(v=t, g=reg["marcas"]["fin"] - 2.4, d=2.2, quien="", txt="")); t += 2.2
    return tr, t

def sonido(G, W, tr, total, fin):
    ep = dict(reparto={}, planos=[dict(musica="tension", fx=[dict(tipo="pum", p=0.0)]), dict(musica="esperanza"), dict(musica="pelicula")])
    corte = tr[-1]["v"]; lin = dict(planos=[dict(ini=0, fin=corte - 4, lineas=[]), dict(ini=corte - 4, fin=total, lineas=[]), dict(ini=total, fin=total + fin - motor.COLA_SELLO, lineas=[])],
                                    sello=total + fin - motor.COLA_SELLO, dur=total + fin)
    motor.sonido(ep, lin, W)
    sr, m = wavfile.read(W + "sonido.wav"); m = m.astype(float) / 32767; N = len(m); V = np.zeros((N, 2))
    def pon(f, t0, g=1.0):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f, "-af", "loudnorm=I=-16:TP=-1.5", "-ar", str(SR), "-ac", "1", W + "_v.wav"], check=True)
        _, x = wavfile.read(W + "_v.wav"); x = x.astype(float) / 32767 * g; a = int(t0 * SR); x = x[:max(0, N - a)]; V[a:a + len(x)] += x[:, None]
    for s in tr:
        if s["quien"] == "cliente": pon(G + f"c{s['k']}.wav", s["v"] + 0.1)
        if s["quien"] == "orbi": pon(G + f"orbi{s['k']}.mp3", s["v"] + 0.15)
    act = np.convolve((np.abs(V[:, 0]) > 0.02).astype(float), np.ones(int(0.3 * SR)) / int(0.3 * SR), "same"); duck = 1 - 0.75 * np.clip(act * 4, 0, 1)
    fin_ = lambda x: (np.clip(x, -1, 1) * 32767).astype(np.int16)
    wavfile.write(W + "final.wav", SR, fin_(m * duck[:, None] * 0.55 + V * 1.25)); wavfile.write(W + "final_sin_musica.wav", SR, fin_(V * 1.25))

CSS = '''* { box-sizing: border-box; margin: 0; padding: 0; } html, body { width: 1080px; height: 1920px; overflow: hidden; background: #050a14; font-family: "Figtree", sans-serif; color: #fff; }
#fondo { position: absolute; inset: 0; background: radial-gradient(90% 55% at 50% 45%, #12305a 0%, #0a1424 55%, #04070d 100%); }
#cel { position: absolute; left: 50%; top: 318px; width: 672px; height: 1445px; margin-left: -336px; border-radius: 64px; border: 14px solid #1b222d; background: #000; overflow: hidden;
  box-shadow: 0 0 0 3px #4a5668, 0 50px 140px rgba(0,0,0,.75), 0 0 150px rgba(47,187,232,.3); transform-origin: 50% 40%; }
#cel img { width: 100%; height: 100%; display: block; }
#gancho { position: absolute; left: 50px; right: 50px; top: 70px; text-align: center; z-index: 5; }
#gancho span { display: inline; font: 900 60px/1.34 "Figtree"; color: #111; background: #fff; padding: 6px 18px; border-radius: 12px; -webkit-box-decoration-break: clone; box-decoration-break: clone; }
#chip { position: absolute; left: 0; right: 0; top: 246px; text-align: center; font: 800 28px/1 "Figtree"; letter-spacing: .26em; text-transform: uppercase; color: #7fd8f0; z-index: 5; }
#sub { position: absolute; left: 70px; right: 70px; top: 1385px; z-index: 6; text-align: center; opacity: 0; }
#sub div { display: inline-block; max-width: 900px; padding: 20px 30px 24px; border-radius: 22px; font: 700 44px/1.25 "Figtree"; box-shadow: 0 20px 60px rgba(0,0,0,.6); }
#sub small { display: block; font: 800 22px/1 "Figtree"; letter-spacing: .24em; margin-bottom: 10px; }
#sub.cliente div { background: #fff; color: #0b1626; } #sub.cliente small { color: #5a6b85; }
#sub.orbi div { background: #0b2a4a; color: #e8fbff; border: 2px solid #2fbbe8; } #sub.orbi small { color: #7fd8f0; }
#pie { position: absolute; left: 0; right: 0; top: 1800px; text-align: center; font: 600 23px/1.4 "Figtree"; color: #8a9cb0; z-index: 5; }
#cortina { position: absolute; inset: 0; background: rgba(3,7,14,.93); opacity: 0; z-index: 8; }
#final { position: absolute; left: 0; right: 0; top: 420px; text-align: center; opacity: 0; z-index: 9; }
#final .tres b { display: block; font: 400 84px/1.2 "Italiana", Georgia, serif; opacity: 0; }
#final .logo { display: inline-flex; align-items: center; gap: 24px; font: 800 96px/1 "Figtree"; margin-top: 90px; }
.pin { display: inline-block; width: 92px; height: 92px; border-radius: 26px; background: #2fbbe8; position: relative; box-shadow: 0 0 60px rgba(47,187,232,.7); }
.pin::after { content: ""; position: absolute; left: 27px; top: 20px; width: 38px; height: 38px; border-radius: 50% 50% 50% 0; background: #0b1626; transform: rotate(-45deg); }
#final .detalle { font: 600 34px/1.4 "Figtree"; color: #9fdcf0; margin: 34px 80px 50px; }
#final .wa { display: inline-flex; align-items: center; gap: 26px; background: #fff; color: #0b1626; border-radius: 30px; padding: 26px 42px; }
#final .wa small { display: block; font: 700 28px/1 "Figtree"; color: #3a4658; text-align: left; } #final .wa b { display: block; font: 900 68px/1.05 "Figtree"; }
#final .wa i { width: 88px; height: 88px; border-radius: 24px; background: #25d366; position: relative; flex: none; }
#final .wa i::after { content: ""; position: absolute; left: 20px; top: 18px; width: 42px; height: 42px; border: 7px solid #fff; border-radius: 50% 50% 50% 8px; }
#final .pie { margin-top: 50px; font: 600 24px/1 "Figtree"; letter-spacing: .3em; color: #6a7c90; text-transform: uppercase; }'''
JS = r'''
const $ = (s) => document.querySelector(s), cl = (x) => Math.max(0, Math.min(1, x)), img = $("#cel img");
let ult = -1;
async function render(t, f) {
  let s = TR[TR.length - 1]; for (const x of TR) if (t >= x.v && t < x.v + x.d) { s = x; break; }
  const tg = t >= TOTAL ? TR[TR.length - 1].g + TR[TR.length - 1].d : s.g + (t - s.v);
  let lo = 0, hi = CU.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (CU[m].t <= tg) lo = m; else hi = m - 1; }
  if (CU[lo].cuadro !== ult) { ult = CU[lo].cuadro; img.src = "cuadros/" + String(ult).padStart(5, "0") + ".jpg"; await img.decode().catch(() => {}); }
  const sub = $("#sub"), act = t < TOTAL && s.quien;
  if (act) { sub.className = s.quien; sub.innerHTML = `<div><small>${s.quien === "cliente" ? "CLIENTE" : "ASISTENTE APEX · RESPUESTA REAL"}</small>${s.txt}</div>`; }
  sub.style.opacity = act ? cl((t - s.v) / 0.15) : 0;
  const n = TR.filter((x) => x.quien === "cliente" && x.v <= t).length;
  $("#chip").textContent = t < TOTAL ? (n ? CFG.chips[Math.min(n, CFG.chips.length) - 1] : CFG.chip0) : "";
  $("#gancho").style.opacity = 1 - cl((t - 3.6) / 0.4);
  $("#cel").style.transform = `scale(${1 + 0.03 * cl(t / 3)})`;
  const k = t - TOTAL; $("#cortina").style.opacity = cl(k / 0.5); $("#final").style.opacity = cl(k / 0.4);
  document.querySelectorAll("#final .tres b").forEach((b, i) => { b.style.opacity = cl((k - 0.3 - i * 0.75) / 0.3); });
  $("#final .abajo").style.opacity = cl((k - 2.9) / 0.5);
}'''

def pagina(G, W, tr, total, cfg, reg):
    leer = lambda p: open(p).read()
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}<style>{CSS}</style></head><body>
<div id="fondo"></div><div id="gancho"><span>{cfg["gancho"]}</span></div><div id="chip"></div><div id="cel"><img></div><div id="sub"></div>
<div id="pie">Demostración real: pantalla y respuestas del asistente en producción.<br>Solo se recortaron las esperas entre turnos.</div>
<div id="cortina"></div><div id="final"><div class="tres">{"".join(f"<b>{x}</b>" for x in cfg["remate"])}</div>
<div class="abajo"><div class="logo"><i class="pin"></i>Apex Play</div><div class="detalle">{cfg["detalle"]}</div>
<div class="wa"><i></i><div><small>Escríbanos por WhatsApp</small><b>310 789 7960</b></div></div><div class="pie">Apex Corporation</div></div></div>
<script>const TR = {json.dumps(tr, ensure_ascii=False)}, TOTAL = {total}, CFG = {json.dumps(cfg, ensure_ascii=False)}, CU = {json.dumps(reg["cuadros"])};{JS}</script></body></html>'''
    open(W + "cuadro.html", "w").write(html)
    if not os.path.exists(W + "cuadros"): os.symlink(os.path.abspath(G + "cuadros"), W + "cuadros")

def hacer(G, rid):
    G = os.path.abspath(G) + "/"; reg = json.load(open(G + "registro.json")); cfg = json.load(open(G + "reto.json"))
    W = motor.TRABAJO + "reto_" + rid + "/"; os.makedirs(W, exist_ok=True); FIN = 7.5
    tr, total = linea_de_tiempo(G, reg, cfg); pagina(G, W, tr, total, cfg, reg)
    if os.getenv("PRUEBA"):
        ts = [1.0] + [s["v"] + s["d"] * 0.6 for s in tr[1:]] + [total + 2.0, total + 6.5]; asyncio.run(motor.prueba(W, [round(x, 2) for x in ts])); print("pruebas en", W); return
    sonido(G, W, tr, total, FIN); asyncio.run(motor.imagen(W, total + FIN))
    S = RAIZ + "entregables/redes/retos/"; os.makedirs(S, exist_ok=True)
    for son, nombre, extra in (("final.wav", f"{rid}.mp4", ["-crf", "19"]), ("final_sin_musica.wav", f"{rid}-sin-musica.mp4", ["-crf", "19"]), ("final.wav", f"{rid}-liviano.mp4", ["-crf", "27", "-vf", "scale=720:-2"])):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + son, "-c:v", "libx264", "-preset", "slow", *extra, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", S + nombre], check=True)
    print("listo", rid, round(total + FIN, 1), "s")

if __name__ == "__main__": hacer(sys.argv[1], sys.argv[2])
