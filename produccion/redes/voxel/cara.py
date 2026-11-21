"""Personaje 01 · cara definitiva (low-poly, rasgos fuertes): mezcla de los rasgos 01, 02 y 06 de los bocetos.
  python cara.py  →  entregables/redes/bocetos/personaje-01.png"""
import os, json, asyncio, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ = motor.RAIZ; SALIDA = RAIZ + "entregables/redes/bocetos/"; THREE = motor.TRABAJO + "three/package/build/three.min.js"
P01 = dict(semilla=31, fuerte=True, peinado="definitivo", barbaNivel=0.95, piel="#c98e6b", pelo="#16100c", barba="#1a120e", camisa="#17181c", iris="#3a281a")
VISTAS = [("Frente", [0, 1.7, 0.78], [0, 1.68, 0], 30, dict()), ("Tres cuartos", [0.5, 1.71, 0.62], [0, 1.68, 0], 30, dict(mira=0.15)),
          ("Perfil", [0.8, 1.7, 0.05], [0, 1.68, 0], 30, dict()), ("Mirada a cámara", [-0.42, 1.68, 0.68], [0, 1.68, 0], 30, dict(mira=-0.45, miraY=-0.05)),
          ("Cuerpo entero", [1.1, 1.25, 3.3], [0, 0.95, 0], 34, dict(mira=0.3, bd=[-0.2, 0.25, -1.4]))]
def main():
    leer = lambda p: open(p).read(); W = motor.TRABAJO + "bocetos/"; os.makedirs(W, exist_ok=True); os.makedirs(SALIDA, exist_ok=True)
    imgs = "".join(f'<figure><img id="v{i}"><figcaption>{n}</figcaption></figure>' for i, (n, *_) in enumerate(VISTAS))
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}<style>
body{{margin:0;background:#0b1020;color:#eef2f6;font-family:Figtree;width:1800px}} h1{{font:800 60px Figtree;margin:40px 50px 4px}} h3{{font:700 22px Figtree;letter-spacing:.2em;color:#e8a04a;margin:0 50px}}
p{{font:500 25px/1.4 Figtree;color:#b9c4d0;margin:14px 50px 26px;max-width:1650px}} .g{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;padding:0 50px 50px}} figure{{margin:0;background:#141b2e;border-radius:20px;padding:10px}}
img{{width:100%;border-radius:12px}} figcaption{{font:700 18px Figtree;letter-spacing:.14em;text-transform:uppercase;color:#8a98a8;margin:8px 4px 2px}}</style></head><body>
<h1>Personaje 01</h1><h3>CARA DEFINITIVA · LOW-POLY</h3>
<p>Rasgos del 01 (tupé, mirada segura), del 02 (pelo hacia atrás, barba corta y definida) y del 06 (moño alto, barba llena). Mandíbula cuadrada, pómulos marcados, tabique recto, ceja fuerte y hombros anchos. Camisa negra.</p>
<div class="g">{imgs}</div><canvas id="lienzo" width="600" height="800" style="display:none"></canvas>
<script src="file://{THREE}"></script>
<script>const PI = Math.PI; function semilla(s) {{ return () => {{ s |= 0; s = (s + 0x6d2b79f5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }}; }}
const VISTAS = {json.dumps([[a, b, f, e] for (_, a, b, f, e) in VISTAS])}; const P01 = {json.dumps(P01)};
{leer(AQUI + "lowpoly3d.js")}
const REN = new THREE.WebGLRenderer({{ canvas: document.getElementById("lienzo"), antialias: true, preserveDrawingBuffer: true }});
REN.setSize(600, 800, false); REN.shadowMap.enabled = true; REN.toneMapping = THREE.ACESFilmicToneMapping; REN.toneMappingExposure = 1.15; REN.outputColorSpace = THREE.SRGBColorSpace;
const ESC = new THREE.Scene(); ESC.background = new THREE.Color(0x0a1438); ESC.fog = new THREE.Fog(0x0a1438, 6, 22);
const bok = (() => {{ const cv = document.createElement("canvas"); cv.width = cv.height = 64; const g = cv.getContext("2d"), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, "rgba(255,255,255,.95)"); gr.addColorStop(0.6, "rgba(255,255,255,.55)"); gr.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(cv); }})();
const rr = semilla(5); for (let i = 0; i < 220; i++) {{ const s = new THREE.Sprite(new THREE.SpriteMaterial({{ map: bok, color: rr() < 0.65 ? 0x6f9bff : 0xffc37a, transparent: true, opacity: 0.25 + rr() * 0.5, depthWrite: false }}));
  s.position.set((rr() - 0.5) * 16, rr() * 6, -6 - rr() * 6); s.scale.setScalar(0.08 + rr() * 0.3); ESC.add(s); }}
const piso = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), new THREE.MeshStandardMaterial({{ color: 0x141a2e, roughness: 0.6 }})); piso.rotation.x = -PI / 2; piso.receiveShadow = true; ESC.add(piso);
ESC.add(new THREE.HemisphereLight(0x5a78d8, 0x3a3550, 1.1));
const lampara = new THREE.SpotLight(0xffd2a0, 9, 6, 0.6, 0.6, 1.6); lampara.position.set(-0.9, 1.9, 1.3); lampara.castShadow = true; ESC.add(lampara);
const relleno = new THREE.DirectionalLight(0xffe2c8, 1.1); relleno.position.set(0.6, 1.9, 3.0); ESC.add(relleno);
const contra = new THREE.DirectionalLight(0x6f8fff, 1.6); contra.position.set(1.5, 2.5, -2.5); ESC.add(contra);
const P = personaLowPoly(P01); ESC.add(P.raiz); lampara.target = P.cabeza;
const CAM = new THREE.PerspectiveCamera(30, 600 / 800, 0.05, 60);
VISTAS.forEach(([pp, tt, f, e], i) => {{ P.pose(e); CAM.fov = f; CAM.position.set(...pp); CAM.lookAt(...tt); CAM.updateProjectionMatrix(); REN.render(ESC, CAM); document.getElementById("v" + i).src = REN.domElement.toDataURL("image/jpeg", 0.92); }});
</script></body></html>'''
    open(W + "cara.html", "w").write(html)
    async def foto():
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            br = await p.chromium.launch(executable_path=motor.CHROME, args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
            pg = await br.new_page(viewport={"width": 1800, "height": 1000}); pg.on("pageerror", lambda e: print("ERR", e))
            await pg.goto("file://" + W + "cara.html"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=SALIDA + "personaje-01.png", full_page=True); await br.close()
    asyncio.run(foto()); print("listo", SALIDA + "personaje-01.png")
if __name__ == "__main__": main()
