"""Boceto del robot «Chispa»: hoja con vista de tres cuartos, de frente, de perfil y primer plano de la cabeza.
  python robot.py  →  entregables/redes/bocetos/robot.png"""
import os, json, asyncio, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ = motor.RAIZ; SALIDA = RAIZ + "entregables/redes/bocetos/"; THREE = motor.TRABAJO + "three/package/build/three.min.js"
VISTAS = [("saluda", [1.5, 1.35, 2.8], [0, 1.0, 0], 34, dict(saluda=True, gesto="feliz")), ("de frente", [0, 1.2, 3.1], [0, 1.0, 0], 34, dict(gesto="normal", mira=0, ladea=0)),
          ("de perfil", [3.1, 1.25, 0.6], [0, 1.0, 0], 34, dict(gesto="enfoca", mira=0.5)), ("hablando", [0.7, 1.75, 1.35], [0, 1.62, 0], 30, dict(gesto="normal", voz=0.8, mira=0.25))]

def pagina(W):
    leer = lambda p: open(p).read()
    imgs = "".join(f'<figure><img id="v{i}"><figcaption>{n}</figcaption></figure>' for i, (n, *_) in enumerate(VISTAS))
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}<style>
body{{margin:0;background:#0d1118;color:#eef2f6;font-family:Figtree;width:1800px}} h1{{font:800 56px Figtree;margin:40px 50px 4px}} h3{{font:700 22px Figtree;letter-spacing:.2em;color:#e8a04a;margin:0 50px}}
p{{font:500 26px/1.4 Figtree;color:#b9c4d0;margin:14px 50px 26px;max-width:1500px}} .g{{display:flex;gap:18px;padding:0 50px 50px}} figure{{margin:0;flex:1;background:#161c26;border-radius:22px;padding:12px}}
img{{width:100%;border-radius:14px}} figcaption{{font:700 20px Figtree;letter-spacing:.16em;text-transform:uppercase;color:#8a98a8;margin:10px 6px 2px}}</style></head><body>
<h1>Chispa</h1><h3>EL ROBOT MESERO · BOCETO V2</h3>
<p>Moderno y elegante: flota sobre un anillo de luz naranja, cuerpo blanco perlado con placas grafito, hombros anchos y cintura fina, núcleo encendido en el pecho y un casco con visor negro brillante donde sus ojos son luces LED que cambian de gesto: feliz, guiño, enfoca y una onda cuando habla.</p>
<div class="g">{imgs}</div><canvas id="lienzo" width="600" height="800" style="display:none"></canvas>
<script src="file://{THREE}"></script>
<script>const PI = Math.PI; const VISTAS = {json.dumps([[list(a), list(b), f, e] for (_, a, b, f, e) in VISTAS])};
{leer(AQUI + "robot3d.js")}
const REN = new THREE.WebGLRenderer({{ canvas: document.getElementById("lienzo"), antialias: true, preserveDrawingBuffer: true }});
REN.setSize(600, 800, false); REN.shadowMap.enabled = true; REN.toneMapping = THREE.ACESFilmicToneMapping; REN.toneMappingExposure = 1.2; REN.outputColorSpace = THREE.SRGBColorSpace;
const ESC = new THREE.Scene(); ESC.background = new THREE.Color(0x101318);
const piso = new THREE.Mesh(new THREE.CircleGeometry(5, 48), new THREE.MeshStandardMaterial({{ color: 0x232833, roughness: 0.7 }})); piso.rotation.x = -PI / 2; piso.receiveShadow = true; ESC.add(piso);
const llave = new THREE.SpotLight(0xffe2c0, 70, 14, 0.5, 0.6, 2); llave.position.set(-2.4, 4.0, 3.0); llave.castShadow = true; llave.shadow.mapSize.set(1024, 1024); ESC.add(llave);
const contra = new THREE.SpotLight(0x7fd8ff, 55, 14, 0.6, 0.7, 2); contra.position.set(2.6, 3.0, -2.8); ESC.add(contra);
ESC.add(new THREE.HemisphereLight(0xfff0e0, 0x101418, 0.6));
const R = robot3d(); ESC.add(R.raiz); llave.target = R.raiz; contra.target = R.raiz; 
const CAM = new THREE.PerspectiveCamera(34, 600 / 800, 0.05, 50);
VISTAS.forEach(([p, t, f, e], i) => {{ R.animar(1.7, e); CAM.fov = f; CAM.position.set(...p); CAM.lookAt(...t); CAM.updateProjectionMatrix(); REN.render(ESC, CAM); document.getElementById("v" + i).src = REN.domElement.toDataURL("image/jpeg", 0.92); }});
</script></body></html>'''
    open(W + "robot.html", "w").write(html)

async def main():
    from playwright.async_api import async_playwright
    W = motor.TRABAJO + "bocetos/"; os.makedirs(W, exist_ok=True); os.makedirs(SALIDA, exist_ok=True); pagina(W)
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path=motor.CHROME, args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = await br.new_page(viewport={"width": 1800, "height": 1000}); pg.on("pageerror", lambda e: print("ERR", e))
        await pg.goto("file://" + W + "robot.html"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=SALIDA + "robot.png", full_page=True); await br.close()
    print("listo", SALIDA + "robot.png")

if __name__ == "__main__": asyncio.run(main())
