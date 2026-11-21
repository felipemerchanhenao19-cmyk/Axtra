"""Bocetos de personajes de vinil: una hoja con cada personaje (retrato y cuerpo entero) para elegir antes de producir.
  python bocetos.py  →  entregables/redes/bocetos/personajes.png (y un PNG por personaje)"""
import os, json, asyncio, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ = motor.RAIZ; SALIDA = RAIZ + "entregables/redes/bocetos/"; THREE = motor.TRABAJO + "three/package/build/three.min.js"

from modelos import PERSONAJES

def pagina(W):
    leer = lambda p: open(p).read()
    tarjetas = "".join(f'''<div class="t"><div class="fotos"><img id="r_{p["id"]}"><img id="c_{p["id"]}"></div>
      <h2>{p["nombre"]}</h2><h3>{p["rol"]}</h3><p>{p["frase"]}</p></div>''' for p in PERSONAJES)
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}<style>
body{{margin:0;background:#0d1118;color:#eef2f6;font-family:Figtree;width:1800px}} h1{{font:800 52px Figtree;margin:40px 50px 6px}} .sub{{margin:0 50px 30px;color:#8a98a8;font:500 24px Figtree}}
.g{{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;padding:0 50px 50px}} .t{{background:#161c26;border-radius:26px;padding:18px 18px 22px}}
.fotos{{display:flex;gap:10px}} .fotos img{{width:50%;border-radius:18px;background:#222}} h2{{font:800 36px Figtree;margin:16px 6px 0}} h3{{font:700 20px Figtree;letter-spacing:.18em;text-transform:uppercase;color:#e8a04a;margin:6px 6px}}
p{{font:500 22px/1.35 Figtree;color:#b9c4d0;margin:8px 6px 0}}</style></head><body>
<h1>Bocetos de personajes · Apex</h1><div class="sub">Versión 3: barba esculpida, cabello largo, cejas finas arqueadas y ojos con brillo.</div><div class="g">{tarjetas}</div>
<canvas id="lienzo" width="600" height="800" style="display:none"></canvas>
<script src="file://{THREE}"></script>
<script>const EP = {{ estilo: "vinil" }}; const PERS = {json.dumps(PERSONAJES, ensure_ascii=False)};
{leer(AQUI + "personajes3d.js")}
{leer(AQUI + "vinil3d.js")}
const REN = new THREE.WebGLRenderer({{ canvas: document.getElementById("lienzo"), antialias: true, preserveDrawingBuffer: true }});
REN.setSize(600, 800, false); REN.shadowMap.enabled = true; REN.toneMapping = THREE.ACESFilmicToneMapping; REN.toneMappingExposure = 1.25; REN.outputColorSpace = THREE.SRGBColorSpace;
const ESC = new THREE.Scene(); ESC.background = new THREE.Color(0x1b1410);
const piso = new THREE.Mesh(new THREE.CircleGeometry(4, 48), new THREE.MeshStandardMaterial({{ color: 0x2a211b, roughness: 0.8 }})); piso.rotation.x = -Math.PI / 2; piso.receiveShadow = true; ESC.add(piso);
const llave = new THREE.SpotLight(0xffd2a8, 60, 12, 0.5, 0.6, 2); llave.position.set(-2.2, 3.6, 3.2); llave.castShadow = true; ESC.add(llave);
const contra = new THREE.SpotLight(0x8fb4ff, 45, 12, 0.6, 0.7, 2); contra.position.set(2.4, 2.8, -2.6); ESC.add(contra);
ESC.add(new THREE.HemisphereLight(0xffe8d0, 0x201810, 0.55));
const CAM = new THREE.PerspectiveCamera(30, 600 / 800, 0.05, 50);
window.hacer = () => {{
  PERS.forEach((p) => {{
    const P = personaVinil(p.cfg); ESC.add(P.raiz); llave.target = P.raiz; contra.target = P.raiz;
    animarPersona(P, {{ x: 0, z: 0, rot: 0.32, gesto: p.pose.gesto, emo: p.pose.emo, mezcla: 1, mira: (p.pose.mira || 0) * Math.PI / 180, miraY: p.pose.miraY || 0, voz: 0 }}, 1.3);
    const h = 1.78 * (p.cfg.alto || 1);
    CAM.position.set(0.6, h + 0.02, 2.35); CAM.lookAt(0, h - 0.12, 0); CAM.updateProjectionMatrix(); REN.render(ESC, CAM); document.getElementById("r_" + p.id).src = REN.domElement.toDataURL("image/jpeg", 0.92);
    CAM.position.set(1.4, 1.25, 4.4); CAM.lookAt(0, 0.98, 0); CAM.updateProjectionMatrix(); REN.render(ESC, CAM); document.getElementById("c_" + p.id).src = REN.domElement.toDataURL("image/jpeg", 0.92);
    ESC.remove(P.raiz);
  }});
}};
</script></body></html>'''
    open(W + "bocetos.html", "w").write(html)

async def main():
    from playwright.async_api import async_playwright
    W = motor.TRABAJO + "bocetos/"; os.makedirs(W, exist_ok=True); os.makedirs(SALIDA, exist_ok=True); pagina(W)
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path=motor.CHROME, args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = await br.new_page(viewport={"width": 1800, "height": 1000}, device_scale_factor=1); pg.on("pageerror", lambda e: print("ERR", e))
        await pg.goto("file://" + W + "bocetos.html"); await pg.evaluate("document.fonts.ready"); await pg.evaluate("hacer()"); await pg.wait_for_timeout(800)
        await pg.screenshot(path=SALIDA + "personajes.png", full_page=True)
        for i, per in enumerate(PERSONAJES): await pg.locator(".t").nth(i).screenshot(path=SALIDA + f"{per['id']}.png")
        await br.close()
    print("listo", SALIDA)

if __name__ == "__main__": asyncio.run(main())
