"""Frutinovelas 3D de Orbi: genera las imágenes con IA (Gemini) y arma el video vertical con voces, subtítulos, música y efectos.
Necesita la variable GEMINI_API_KEY (Google AI Studio) y que la red permita generativelanguage.googleapis.com.
  python generar.py fichas                  → una ficha de referencia por personaje (se generan una sola vez)
  python generar.py tomas <id>              → una imagen por toma del episodio (usa las fichas para que los personajes no cambien)
  python generar.py video <id>              → arma el video: entregables/redes/frutinovela3d/<id>.mp4 (+ sin música)
  python generar.py todo <id>               → las tres cosas
El modelo de imagen se cambia con IA_MODELO_IMAGEN. Las voces, la música y los efectos salen del motor de «heroes»."""
import sys, os, json, base64, asyncio, subprocess, time, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, AQUI); sys.path.append(AQUI + "../heroes")
from episodios import EPISODIOS, PERSONAJES, ESTILO
RAIZ = os.path.abspath(AQUI + "../../..") + "/"
TRABAJO = os.getenv("TRABAJO", "/tmp/orbi_frutinovela3d") + "/"
FICHAS, TOMAS, SALIDA = AQUI + "fichas/", AQUI + "tomas/", RAIZ + "entregables/redes/frutinovela3d/"
MODELO = os.getenv("IA_MODELO_IMAGEN", "gemini-2.5-flash-image")
FPS = 30

def imagen_ia(texto, refs, destino):
    clave = os.getenv("GEMINI_API_KEY")
    if not clave: sys.exit("Falta GEMINI_API_KEY en el entorno.")
    partes = [{"text": texto}] + [{"inline_data": {"mime_type": "image/png", "data": base64.b64encode(open(r, "rb").read()).decode()}} for r in refs]
    cuerpo = {"contents": [{"parts": partes}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "9:16"}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"
    for intento in range(4):
        try:
            req = urllib.request.Request(url, json.dumps(cuerpo).encode(), {"Content-Type": "application/json", "x-goog-api-key": clave})
            r = json.load(urllib.request.urlopen(req, timeout=180))
            for p in r["candidates"][0]["content"]["parts"]:
                d = p.get("inlineData") or p.get("inline_data")
                if d: open(destino, "wb").write(base64.b64decode(d["data"])); print("imagen", destino); return
            print("sin imagen en la respuesta:", json.dumps(r)[:300])
        except Exception as e: print("reintento imagen", e); time.sleep(4 * 2 ** intento)
    sys.exit("No se pudo generar " + destino)

def fichas():
    os.makedirs(FICHAS, exist_ok=True)
    for pid, desc in PERSONAJES.items():
        f = FICHAS + pid + ".png"
        if os.path.exists(f): continue
        imagen_ia(f"Character reference sheet, single full-body front view, standing, neutral light-grey studio background. {desc}. {ESTILO}", [], f)

def tomas(eid):
    os.makedirs(TOMAS, exist_ok=True); ep = EPISODIOS[eid]
    for i, pl in enumerate(ep["planos"]):
        f = TOMAS + f"{eid}_{i:02d}.png"
        if os.path.exists(f): continue
        quienes = " ".join(f"[{q}] {PERSONAJES[q]}." for q in pl["salen"])
        texto = (f"{ESTILO}. Scene: {pl['prompt']}. Characters in this scene (keep each one exactly as in the attached reference images, same head, face, "
                 f"colors and clothes): {quienes} Human bodies with arms and legs, natural varied skin tones for any background extras.")
        imagen_ia(texto, [FICHAS + q + ".png" for q in pl["salen"]], f)

ESCENA = r"""
const $ = (s) => document.querySelector(s), cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), lerp = (a, b, k) => a + (b - a) * k;
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3), ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const rebote = (x) => { x = cl(x); return 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2); };
const P = LINEA.planos, SELLO = LINEA.sello, TODAS = P.flatMap((p) => p.lineas);
let ultSub = "", ultPed = "";
function render(t, f) {
  let i = 0; P.forEach((p, k) => { if (t >= p.ini) i = k; });
  const pl = EP.planos[i], L = P[i], p = cl((t - L.ini) / (L.fin - L.ini)), tt = t - L.ini, fin = L.fin - t;
  const [a, b] = pl.cam || [[0.5, 0.5, 1], [0.5, 0.5, 1.1]], k = ease(p), x = lerp(a[0], b[0], k), y = lerp(a[1], b[1], k), z = lerp(a[2], b[2], k);
  let sh = 0, flash = 0, pum = "";
  for (const fx of pl.fx || []) { const d = t - (L.ini + (fx.p || 0) * (L.fin - L.ini));
    if (fx.tipo === "rayo" && d > 0 && d < 0.4) { flash = Math.max(flash, d < 0.08 ? 0.9 : d > 0.16 && d < 0.24 ? 0.6 : 0); sh = Math.max(sh, 8); }
    if (fx.tipo === "destello" && d > 0 && d < 0.6) flash = Math.max(flash, 0.5 * (1 - d / 0.6));
    if (fx.tipo === "pum" && d > 0 && d < 0.8) { sh = Math.max(sh, 20 * (1 - d / 0.4)); const q = rebote(d / 0.18) * (1 - cl((d - 0.6) / 0.2));
      const pts = Array.from({ length: 24 }, (_, j) => { const r = j % 2 ? 120 : 220, an = (j / 24) * Math.PI * 2; return `${Math.cos(an) * r},${Math.sin(an) * r * 0.8}`; }).join(" ");
      pum = `<svg viewBox="0 0 1080 1920" width="1080" height="1920"><g transform="translate(${fx.x} ${fx.y}) rotate(-8) scale(${q})"><polygon points="${pts}" fill="#ffd166" stroke="#111" stroke-width="10"/>
        <text y="30" text-anchor="middle" font-size="92" font-weight="900" fill="#c01b2c" stroke="#111" stroke-width="5" paint-order="stroke" font-family="Figtree" font-style="italic">${fx.texto}</text></g></svg>`; } }
  pintar(i, pl, t, x, y, z, sh * Math.sin(f * 7.1), sh * Math.cos(f * 5.3));
  $("#pantalla").innerHTML = pum;
  const sig = EP.planos[i + 1]; let negro = pl.trans === "negro" ? 1 - cl(tt / 0.35) : 0;
  if (sig && sig.trans === "negro") negro = Math.max(negro, 1 - cl(fin / 0.3)); if (t >= SELLO - 0.4) negro = Math.max(negro, cl((t - SELLO + 0.4) / 0.4));
  $("#negro").style.opacity = negro; $("#flash").style.opacity = Math.max(flash, pl.trans === "flash" ? 1 - cl(tt / 0.25) : 0);
  $("#cine").style.filter = pl.trans === "barrido" && tt < 0.25 ? `blur(${(1 - tt / 0.25) * 14}px)` : "none";
  $("#gancho").style.opacity = cl((3.0 - t) / 0.3);
  $("#tinte").style.background = pl.tinte ? `radial-gradient(70% 60% at 50% 40%, rgba(255,255,255,0) 30%, ${pl.tinte} 100%)` : "none"; $("#tinte").style.opacity = pl.tinte ? 0.55 : 0;
  const ti = $("#titulo");
  if (pl.cartel) { $("#titulo b").textContent = pl.cartel[0]; $("#titulo small").textContent = pl.cartel[1] || ""; ti.style.opacity = out3((tt - 0.5) / 0.4) * cl((fin - 0.1) / 0.3);
    $("#titulo b").style.backgroundPosition = `${120 - 140 * p}% 0`; ti.style.transform = `translate(-50%,-50%) scale(${1.08 - 0.08 * out3((tt - 0.5) / 1.5)})`; } else ti.style.opacity = 0;
  const l = TODAS.find((q) => t >= q.ini - 0.05 && t < q.fin + 0.25), sub = $("#sub");
  if (l && t < SELLO) { if (ultSub !== l.txt + l.ini) { ultSub = l.txt + l.ini; const rp = EP.reparto[l.quien]; sub.innerHTML = `<small style="color:${rp.color}">${rp.nombre}</small>${l.txt}`; }
    sub.style.opacity = out3((t - l.ini + 0.05) / 0.12) * cl((l.fin + 0.25 - t) / 0.12); } else sub.style.opacity = 0;
  let ped = null; EP.planos.forEach((pp, j) => pp.lineas.forEach((ln, kk) => { const e = ln[3] || {}; if (e.pedido && t >= P[j].lineas[kk].ini && t < P[j].lineas[kk].ini + 3.4) ped = [e.pedido, P[j].lineas[kk].ini]; }));
  const pe = $("#pedido"); if (ped) { const [a1, b1] = ped[0].split("|"); if (ultPed !== a1) { ultPed = a1; pe.innerHTML = `<i></i><b>${a1}</b><span>${b1 || ""}</span>`; }
    pe.style.opacity = out3((t - ped[1]) / 0.25); pe.style.transform = `translateX(-50%) translateY(${50 * (1 - out3((t - ped[1]) / 0.35))}px)`; } else pe.style.opacity = 0;
  if (t >= SELLO) { const s = t - SELLO; $("#sello").style.opacity = out3(s / 0.5); $("#frase").style.opacity = out3((s - 0.3) / 0.4); $("#logo").style.opacity = out3((s - 0.8) / 0.5);
    $("#o-final").style.transform = `scale(${1.05 - 0.05 * out3(s / 1.5)})`; } else $("#sello").style.opacity = 0;
}
// ---------- Actuación: la boca se abre con el volumen de la voz, la mandíbula baja y el cuerpo respira
const BOCAS = BOCAS_JSON;
function apertura(q, t) {
  const l = TODAS.find((x) => x.quien === q && t >= x.ini && t < x.fin + 0.05); if (!l || !l.env) return 0;
  const k = (t - l.ini) * 30, a = l.env[Math.floor(k)] ?? 0, b = l.env[Math.floor(k) + 1] ?? 0; return lerp(a, b, k % 1);
}
function boca(ctx, im, [mx, my, mw, cy, modo], a) {
  const d = a * mw * 0.5;
  if (modo === "dibuja") {   // personaje sin boca en la imagen: se le dibuja una
    ctx.fillStyle = "#1f3310"; ctx.beginPath();
    if (d < 2) { ctx.lineWidth = 5; ctx.strokeStyle = "#1f3310"; ctx.moveTo(mx - mw * 0.45, my); ctx.quadraticCurveTo(mx, my + mw * 0.22, mx + mw * 0.45, my); ctx.stroke(); return; }
    ctx.ellipse(mx, my + d * 0.3, mw * 0.42, d * 0.75 + 3, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#7a2a2a"; ctx.beginPath(); ctx.ellipse(mx, my + d * 0.6, mw * 0.25, d * 0.3 + 1, 0, 0, Math.PI * 2); ctx.fill(); return;
  }
  if (d < 0.6) return;
  const rx = mw * 1.25, top = my - 2, bot = cy + 10;
  ctx.save(); ctx.beginPath(); ctx.ellipse(mx, (top + bot) / 2 + d / 2, rx, (bot - top) / 2 + d, 0, 0, Math.PI * 2); ctx.clip();
  ctx.fillStyle = "#2a0a0e"; ctx.beginPath(); ctx.ellipse(mx, my + d / 2, mw * 0.4 * (1 + 0.15 * a), d / 2 + 0.5, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "#8a2f3a"; ctx.beginPath(); ctx.ellipse(mx, my + d * 0.8, mw * 0.24, d * 0.22 + 0.5, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "#f4efe6"; ctx.fillRect(mx - mw * 0.24, my, mw * 0.48, Math.min(d * 0.18, 4));
  const bw = Math.max(4, rx / 10);
  for (let x0 = mx - rx; x0 < mx + rx; x0 += bw) {
    const fx = Math.cos(Math.min(1, Math.abs(x0 + bw / 2 - mx) / rx) * Math.PI / 2);
    for (let y0 = my + 1; y0 < bot; y0 += 2) {
      const s = d * fx * Math.pow(1 - (y0 - my) / (bot - my), 0.6);
      ctx.drawImage(im, x0, y0, bw + 0.5, 2.5, x0, y0 + s, bw + 0.5, 2.5);
    }
  }
  ctx.restore();
}
function pintar(i, pl, t, x, y, z, sx, sy) {
  const im = document.querySelectorAll(".toma")[i], cv = $("#lienzo"), ctx = cv.getContext("2d");
  const iw = im.naturalWidth, ih = im.naturalHeight, k0 = Math.max(1080 / iw, 1920 / ih), bx = (1080 - iw * k0) / 2, by = (1920 - ih * k0) / 2, ox = x * 1080, oy = y * 1920;
  const bocas = pl.bocas || (pl.imagen ? { [pl.voz || pl.imagen.split("/").pop().split(".")[0]]: BOCAS[pl.imagen.split("/").pop().split(".")[0]] } : {});
  let habla = 0; for (const q in bocas) habla = Math.max(habla, apertura(q, t));
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = "#000"; ctx.fillRect(0, 0, 1080, 1920);
  // respiración, balanceo y un leve cabeceo al hablar (todo alrededor de los pies)
  const r = 0.006 * Math.sin(t * 1.1 + i) + 0.01 * habla * Math.sin(t * 9), resp = 1 + 0.006 * Math.sin(t * 2.2);
  ctx.translate(540 + sx, 1920 + sy); ctx.rotate(r); ctx.scale(1, resp); ctx.translate(-540, -1920 - habla * 6);
  ctx.transform(z * k0, 0, 0, z * k0, ox + z * (bx - ox), oy + z * (by - oy));
  ctx.drawImage(im, 0, 0);
  for (const q in bocas) if (bocas[q]) boca(ctx, im, bocas[q], apertura(q, t));
}
const PROD = { dom: ["Apex Domicilios", "Sus domicilios, sin comisiones"], play: ["Apex Play", "Pida desde la mesa con un QR"] }[EP.producto];
$("#gancho").innerHTML = EP.gancho; $("#logo b").innerHTML = `<i></i>${PROD[0]}`; $("#logo span").textContent = PROD[1]; $("#frase").textContent = EP.frase || "";
"""

# Boca de cada ficha en píxeles de la imagen: [centro x, centro y, ancho, barbilla y, modo]
BOCAS = {"orbi": [384, 319, 70, 380], "arepa": [384, 402, 60, 480], "chorizo": [384, 412, 44, 490], "comi": [384, 342, 55, 390], "aguacate": [384, 380, 50, 420, "dibuja"]}

def envolvente(wav):
    """Volumen de la voz a 30 cuadros por segundo, de 0 a 1, para abrir la boca."""
    import numpy as np
    from scipy.io import wavfile
    sr, v = wavfile.read(wav); v = v.astype(float) / 32767; v = v if v.ndim == 1 else v.mean(1)
    n = sr // FPS; e = np.array([np.sqrt(np.mean(v[i:i + n] ** 2)) for i in range(0, len(v), n)])
    e = np.clip((e - 0.01) / (np.percentile(e, 92) + 1e-6), 0, 1); e = np.convolve(e, [0.25, 0.5, 0.25], "same")
    return [round(float(x), 3) for x in e]

def video(eid):
    import hacer as motor   # motor de «heroes»: voces de Microsoft, música por escena y mezcla
    ep = EPISODIOS[eid]; W = TRABAJO + eid + "/"; os.makedirs(W, exist_ok=True); motor.TRABAJO = TRABAJO
    lin = asyncio.run(motor.voces(ep, W))
    for p in lin["planos"]:
        for l in p["lineas"]: l["env"] = envolvente(W + f"voces/l{l['k']:02d}.wav")
    json.dump(lin, open(W + "linea.json", "w"), ensure_ascii=False)
    css = open(AQUI + "../heroes/estilo.css").read() + """
      .toma { display: none; } #lienzo { position: absolute; inset: 0; }
      #tinte { position: absolute; inset: 0; mix-blend-mode: multiply; opacity: 0; }
      #titulo { top: 87%; width: 1080px; padding: 26px 0 30px; background: linear-gradient(rgba(0,0,0,0), rgba(0,0,0,.72) 25%, rgba(0,0,0,.72) 75%, rgba(0,0,0,0)); } #titulo small { margin-top: 12px; } #titulo b { font: 400 120px/1 "Italiana", Georgia, serif; text-transform: none; letter-spacing: 0;
        background: linear-gradient(100deg, #b8862b 0%, #fff1c4 40%, #fff 50%, #fff1c4 60%, #b8862b 100%); background-size: 300% 100%; -webkit-background-clip: text; background-clip: text; }
      #o-final img { width: 560px; height: 760px; object-fit: cover; border-radius: 40px; box-shadow: 0 0 60px rgba(47,187,232,.5); }"""
    tomas_html = "".join(f'<img class="toma" src="file://{AQUI + pl["imagen"] if pl.get("imagen") else TOMAS + f"{eid}_{i:02d}.png"}">' for i, pl in enumerate(ep["planos"]))
    html = f'''<!doctype html><html><head><meta charset="utf-8">{open(RAIZ + "produccion/videos/fuentes.html").read()}<style>{css}</style></head><body>
<div id="cine"><canvas id="lienzo" width="1080" height="1920"></canvas>{tomas_html}<div id="tinte"></div></div><div id="titulo"><b></b><small></small></div><div id="pantalla"></div><div id="vineta"></div><div id="pedido"></div><div id="sub"></div>
<div id="flash"></div><div id="negro"></div><div id="barras"></div><div id="gancho"></div>
<div id="sello"><div id="o-final"><img src="file://{FICHAS}orbi.png"></div><div id="frase"></div><div id="logo"><b></b><span></span></div></div>
<canvas id="grano" width="360" height="640"></canvas>
<script>const EP = {json.dumps(ep, ensure_ascii=False)};const BOCAS_JSON = {json.dumps(BOCAS)}; const LINEA = {json.dumps(lin, ensure_ascii=False)};{ESCENA}</script></body></html>'''
    open(W + "cuadro.html", "w").write(html)
    motor.FPS = FPS; motor.sonido(ep, lin, W); asyncio.run(motor.imagen(W, lin["dur"]))
    os.makedirs(SALIDA, exist_ok=True)
    for son, nombre in (("sonido.wav", f"{eid}.mp4"), ("sonido_sin_musica.wav", f"{eid}-sin-musica.mp4")):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + son, "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", SALIDA + nombre], check=True)
    print("listo", SALIDA + f"{eid}.mp4")

if __name__ == "__main__":
    accion, eid = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else None)
    if accion in ("fichas", "todo"): fichas()
    if accion in ("tomas", "todo"): tomas(eid)
    if accion in ("video", "todo"): video(eid)
