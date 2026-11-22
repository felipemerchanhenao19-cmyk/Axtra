"""Renderiza al Personaje 01 (low-poly) con delantal, de pie y con el brazo abierto, sobre fondo transparente (PNG 1400x1800)."""
import os, sys, asyncio, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
_s = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_s); _s.loader.exec_module(motor)
VOX = AQUI + "../voxel/"; THREE = motor.TRABAJO + "three/package/build/three.min.js"; SAL = sys.argv[1]
HTML = f"""<!doctype html><html><body style="margin:0;background:transparent"><canvas id="c" width="1400" height="1800"></canvas>
<script src="file://{THREE}"></script><script>const PI = Math.PI; {open(VOX + "personajes3d.js").read().split(chr(10))[4]}
{open(VOX + "lowpoly3d.js").read()}
const REN = new THREE.WebGLRenderer({{ canvas: document.getElementById("c"), antialias: true, alpha: true, preserveDrawingBuffer: true }});
REN.setPixelRatio(1.5); REN.setSize(1400, 1800, false); REN.setClearColor(0x000000, 0); REN.shadowMap.enabled = true;
REN.toneMapping = THREE.ACESFilmicToneMapping; REN.toneMappingExposure = 1.25; REN.outputColorSpace = THREE.SRGBColorSpace;
const E = new THREE.Scene();
const P = personaLowPoly({{ semilla: 31, fuerte: true, peinado: "definitivo", barbaNivel: 0.95, detalle: true, piel: "#c98e6b", pelo: "#16100c", barba: "#1a120e", camisa: "#6b4a34", iris: "#3a281a", delantal: "#5f646b" }});
E.add(P.raiz); P.raiz.rotation.y = -0.32;
P.pose({{ mira: 0.22, miraY: 0.04, ladea: 0.06, bd: [-0.35, 0.22, -0.9], bi: [0.05, -0.12, -0.2], cejas: 0.2 }});
const llave = new THREE.DirectionalLight(0xffe4c8, 2.0); llave.position.set(-0.6, 2.0, 3.0); E.add(llave);
const contra = new THREE.DirectionalLight(0x7fd4ff, 2.2); contra.position.set(1.8, 2.2, -2.0); E.add(contra);
const rim2 = new THREE.DirectionalLight(0xffb070, 1.2); rim2.position.set(-2.4, 1.6, -1.6); E.add(rim2);
E.add(new THREE.HemisphereLight(0xfff1e0, 0x3a2e24, 1.3));
const C = new THREE.PerspectiveCamera(30, 1400 / 1800, 0.05, 30); C.position.set(0.18, 1.6, 1.85); C.lookAt(0.05, 1.36, 0);
REN.render(E, C);
</script></body></html>"""
async def main():
    from playwright.async_api import async_playwright
    W = motor.TRABAJO + "carrusel/"; os.makedirs(W, exist_ok=True); open(W + "p.html", "w").write(HTML)
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path=motor.CHROME, args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await br.new_page(viewport={"width": 1400, "height": 1800}); pg.on("pageerror", lambda e: print("ERR", e))
        await pg.goto("file://" + W + "p.html"); await pg.wait_for_timeout(1500)
        await pg.locator("#c").screenshot(path=SAL, omit_background=True); await br.close()
asyncio.run(main()); print("listo", SAL)
