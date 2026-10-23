"""Animática de los videos con minifiguras: arma el montaje con las imágenes de los modelos (movimientos de cámara sobre la imagen,
gancho, subtítulos, voces provisionales, música y cierre de Apex) para ver ritmo e historia antes de generar los clips con IA.
  python animatica.py <id>                  →  entregables/redes/minifiguras/<id>/animatica.mp4
  PRUEBA=planos python animatica.py <id>    →  un cuadro por toma para revisar
Las tomas están en guiones.py. Cada toma: imagen, cuadro inicial y final [cx, cy, alto] en píxeles de la imagen, temblor, líneas."""
import sys, os, json, asyncio, subprocess, shutil, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, AQUI)
from guiones import GUIONES
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ = motor.RAIZ
SALIDA = RAIZ + "entregables/redes/minifiguras/"

PAGINA = r'''
const $ = (s) => document.querySelector(s), cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), suave = (x) => { x = cl(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, k) => a + (b - a) * k;
const IMGS = {}, ruta = (n) => n.includes("/") ? n : "modelos/" + n;
EP.tomas.forEach((tm) => [tm.imagen, ...(PLAN[EP.tomas.indexOf(tm)] || []).map((p) => p[1])].forEach((n) => { if (n && !IMGS[n]) { const im = new Image(); im.src = ruta(n); im.className = "foto"; $("#lienzo").appendChild(im); IMGS[n] = im; } }));
function render(t) {
  const LP = LINEA.planos; let i = LP.findIndex((L) => t < L.fin); if (i < 0) i = LP.length - 1;
  const tm = EP.tomas[i], L = LP[i], tt = t - L.ini, dur = L.fin - L.ini, p = suave(tt / dur);
  // cuadro a cuadro: la imagen de este instante sale del plan (12 por segundo)
  let actual = tm.imagen; const plan = PLAN[i]; if (plan && plan.length) { const k = Math.floor(tt * 12); actual = plan[Math.min(plan.length - 1, k)][1]; }
  Object.entries(IMGS).forEach(([n, im]) => { im.style.display = n === actual ? "block" : "none"; });
  if (actual) {
    const im = IMGS[actual], [x0, y0, h0] = tm.de, [x1, y1, h1] = tm.a || tm.de, cx = lerp(x0, x1, p), cy = lerp(y0, y1, p), h = lerp(h0, h1, p), s = 1920 / h;
    let sx = 0, sy = 0; if (tm.temblor) { const k = tm.temblor * Math.max(0, 1 - Math.abs(tt - (tm.golpe || 0.6)) * 2.5); sx = k * Math.sin(t * 90); sy = k * Math.cos(t * 77); }
    const bx = 0.6 * Math.sin(t * 0.9), by = 0.6 * Math.cos(t * 1.1);   // cámara en mano muy leve
    im.style.transform = `translate(${540 - cx * s + sx + bx}px, ${960 - cy * s + sy + by}px) scale(${s})`;
    im.style.filter = tm.grado || "contrast(1.05) saturate(1.08)";
  }
  const linea = L.lineas.find((l) => t >= l.ini - 0.05 && t < l.fin + 0.25), sub = $("#sub");
  sub.textContent = linea ? linea.txt : ""; sub.style.opacity = linea ? 1 : 0;
  const gch = $("#gancho"); if (EP.gancho) { if (!gch.dataset.ok) { gch.dataset.ok = 1; gch.innerHTML = `<span>${EP.gancho[0]}</span>${EP.gancho[1] ? `<small>${EP.gancho[1]}</small>` : ""}`; }
    gch.style.opacity = 1 - cl((t - 3.2) / 0.4); }
  let negro = 0; if (tm.trans === "negro") negro = 1 - cl(tt / 0.5); if (EP.tomas[i + 1] && EP.tomas[i + 1].trans === "negro") negro = Math.max(negro, cl((tt - dur + 0.4) / 0.4));
  $("#negro").style.opacity = negro; $("#blanco").style.opacity = tm.trans === "flash" ? Math.max(0, 0.85 - tt * 3) : 0;
  const fi = $("#final");
  if (tm.final) { const f = tm.final; if (!fi.dataset.ok) { fi.dataset.ok = 1; fi.innerHTML = `<div class="logo"><i class="pin"></i>${f.marca}</div><div class="frase">${f.frase}</div><div class="detalle">${f.detalle}</div><div class="wa"><i></i><div><small>Escríbanos por WhatsApp</small><b>310 789 7960</b></div></div><div class="pie">Apex Corporation</div>`; }
    fi.style.opacity = cl((tt - 0.3) / 0.7); $("#cortina").style.opacity = 0.8 * cl((tt) / 0.8); } else { fi.style.opacity = 0; $("#cortina").style.opacity = 0; }
  $("#marca").textContent = EP.marcaAgua === false ? "" : (tm.imagen ? "ANIMÁTICA · TOMA " + (i + 1) : "");
}
'''
CSS = '''#lienzo { position: absolute; inset: 0; overflow: hidden; background: #111; } .foto { position: absolute; left: 0; top: 0; transform-origin: 0 0; display: none; }
#marca { position: absolute; left: 40px; top: 1840px; font: 700 22px/1 "Figtree"; letter-spacing: .2em; color: rgba(255,255,255,.55); z-index: 12; }'''

def pagina(ep, lin, W, plan=None):
    leer = lambda p: open(p).read(); V = AQUI + "../voxel/"
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}<style>{leer(V + "estilo.css")}{CSS}</style></head><body>
<div id="lienzo"></div><div id="vineta"></div><div id="gancho"></div><div id="sub"></div><div id="cortina"></div><div id="final"></div><div id="marca"></div>
<div id="blanco"></div><div id="negro"></div>
<script>const EP = {json.dumps(ep, ensure_ascii=False)}; const LINEA = {json.dumps(lin, ensure_ascii=False)}; const PLAN = {json.dumps(plan or [], ensure_ascii=False)};
{PAGINA}</script></body></html>'''
    open(W + "cuadro.html", "w").write(html)
    shutil.copytree(AQUI + "modelos", W + "modelos", dirs_exist_ok=True)
    if os.path.isdir(AQUI + gid_carpeta(ep)): shutil.copytree(AQUI + gid_carpeta(ep), W + "cuadros", dirs_exist_ok=True)

def gid_carpeta(ep): return ep.get("carpeta", "") or "__ninguna__"

def hacer(gid):
    g = GUIONES[gid]; ep = dict(g, planos=g["tomas"]); W = motor.TRABAJO + "mini_" + gid + "/"; os.makedirs(W, exist_ok=True)
    lin = asyncio.run(motor.voces(ep, W)); json.dump(lin, open(W + "linea.json", "w"), ensure_ascii=False)
    pagina(ep, lin, W)
    if os.getenv("PRUEBA"):
        ts = [round(p["ini"] + (p["fin"] - p["ini"]) * 0.5, 2) for p in lin["planos"]]
        asyncio.run(motor.prueba(W, ts)); print("pruebas en", W, ts); return
    motor.sonido(ep, lin, W); asyncio.run(motor.imagen(W, lin["dur"]))
    d = SALIDA + gid + "/"; os.makedirs(d, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + "sonido.wav", "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", d + "animatica.mp4"], check=True)
    print("listo", d + "animatica.mp4", lin["dur"], "s")

if __name__ == "__main__":
    hacer(sys.argv[1])
