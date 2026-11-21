"""Bocetos del robot «Play»: cuatro diseños, cada uno con vista completa (saludando) y primer plano (hablando).
  python robot.py  →  entregables/redes/bocetos/robot-play.png"""
import os, json, asyncio, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ = motor.RAIZ; SALIDA = RAIZ + "entregables/redes/bocetos/"; THREE = motor.TRABAJO + "three/package/build/three.min.js"
OPCIONES = [
    dict(fn="robotPlayCaja", cfg=dict(cuerpo="#1b2440", borde="#36e0ff", ojoI="#36e0ff", ojoD="#ff4fd8", bola="#ff3b3b"), letra="A", nombre="Caja arcade · Noche", desc="Azul oscuro con bordes de neón turquesa. Ojo izquierdo turquesa, ojo derecho fucsia. Palanca roja en la cabeza.", cara=0.82, alto=0.62),
    dict(fn="robotPlayCaja", cfg=dict(cuerpo="#f3f3f5", borde="#ff7a2e", ojoI="#ff7a2e", ojoD="#3b9bff", bola="#ff7a2e"), letra="B", nombre="Caja arcade · Blanca", desc="Blanco brillante con bordes naranjas. Ojo naranja y ojo azul. Limpia y moderna, combina con la marca.", cara=0.82, alto=0.62),
    dict(fn="robotPlayCaja", cfg=dict(cuerpo="#d6312b", borde="#ffd23b", ojoI="#3bff8a", ojoD="#ffd23b", bola="#ffd23b"), letra="C", nombre="Caja arcade · Roja", desc="Rojo arcade con bordes dorados. Ojo verde y ojo amarillo. La más llamativa y divertida.", cara=0.82, alto=0.62),
    dict(fn="robotPlayCaja", cfg=dict(cuerpo="#5b2ca8", borde="#9dff3b", ojoI="#9dff3b", ojoD="#36e0ff", bola="#9dff3b"), letra="D", nombre="Caja arcade · Morada", desc="Morado con neón verde lima. Ojo verde y ojo turquesa. Atrevida y muy de videojuego.", cara=0.82, alto=0.62),
]

def pagina(W):
    leer = lambda p: open(p).read()
    tarjetas = "".join(f'''<div class="t"><div class="fotos"><img id="a{o["letra"]}"><img id="b{o["letra"]}"></div>
      <h2><span>Opción {o["letra"]}</span> Play · {o["nombre"]}</h2><p>{o["desc"]}</p></div>''' for o in OPCIONES)
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}<style>
body{{margin:0;background:#0d1118;color:#eef2f6;font-family:Figtree;width:1800px}} h1{{font:800 56px Figtree;margin:40px 50px 4px}} .sub{{margin:0 50px 30px;color:#8a98a8;font:500 26px Figtree}}
.g{{display:grid;grid-template-columns:repeat(2,1fr);gap:26px;padding:0 50px 50px}} .t{{background:#161c26;border-radius:26px;padding:18px 18px 24px}}
.fotos{{display:flex;gap:10px}} .fotos img{{width:50%;border-radius:18px}} h2{{font:800 36px Figtree;margin:16px 6px 0}} h2 span{{font:700 20px Figtree;letter-spacing:.18em;text-transform:uppercase;color:#e8a04a;margin-right:10px}}
p{{font:500 23px/1.4 Figtree;color:#b9c4d0;margin:8px 6px 0}}</style></head><body>
<h1>Play · el robot de Apex</h1><div class="sub">Caja con ojos luminosos de colores distintos y brazos cortos, con estilo arcade de los 80. Cuatro combinaciones de color.</div><div class="g">{tarjetas}</div>
<canvas id="lienzo" width="600" height="800" style="display:none"></canvas>
<script src="file://{THREE}"></script>
<script>const PI = Math.PI; const OPS = {json.dumps(OPCIONES, ensure_ascii=False)};
{leer(AQUI + "robot3d.js")}
const REN = new THREE.WebGLRenderer({{ canvas: document.getElementById("lienzo"), antialias: true, preserveDrawingBuffer: true }});
REN.setSize(600, 800, false); REN.shadowMap.enabled = true; REN.toneMapping = THREE.ACESFilmicToneMapping; REN.toneMappingExposure = 1.2; REN.outputColorSpace = THREE.SRGBColorSpace;
const ESC = new THREE.Scene(); ESC.background = new THREE.Color(0x121620);
const piso = new THREE.Mesh(new THREE.CircleGeometry(5, 48), new THREE.MeshStandardMaterial({{ color: 0x232833, roughness: 0.7 }})); piso.rotation.x = -PI / 2; piso.receiveShadow = true; ESC.add(piso);
const llave = new THREE.SpotLight(0xffe8d0, 70, 14, 0.5, 0.6, 2); llave.position.set(-2.4, 4.0, 3.0); llave.castShadow = true; llave.shadow.mapSize.set(1024, 1024); ESC.add(llave);
const contra = new THREE.SpotLight(0x9fd0ff, 55, 14, 0.6, 0.7, 2); contra.position.set(2.6, 3.0, -2.8); ESC.add(contra);
ESC.add(new THREE.HemisphereLight(0xfff4e8, 0x101418, 0.7));
const CAM = new THREE.PerspectiveCamera(34, 600 / 800, 0.05, 50);
OPS.forEach((o) => {{
  const R = window[o.fn](o.cfg || {{}}); ESC.add(R.raiz); llave.target = R.raiz; contra.target = R.raiz;
  R.animar(1.7, {{ saluda: true, gesto: "feliz" }}); CAM.fov = 34; CAM.position.set(1.5, 1.3 * o.alto, 2.9 * o.alto); CAM.lookAt(0, 0.95 * o.alto, 0); CAM.updateProjectionMatrix();
  REN.render(ESC, CAM); document.getElementById("a" + o.letra).src = REN.domElement.toDataURL("image/jpeg", 0.92);
  R.animar(2.3, {{ gesto: "normal", voz: 0.8, mira: 0.25 }}); CAM.fov = 30; CAM.position.set(0.75, o.cara + 0.15, 1.95); CAM.lookAt(0, o.cara, 0); CAM.updateProjectionMatrix();
  REN.render(ESC, CAM); document.getElementById("b" + o.letra).src = REN.domElement.toDataURL("image/jpeg", 0.92); ESC.remove(R.raiz);
}});
</script></body></html>'''
    open(W + "robot.html", "w").write(html)

async def main():
    from playwright.async_api import async_playwright
    W = motor.TRABAJO + "bocetos/"; os.makedirs(W, exist_ok=True); os.makedirs(SALIDA, exist_ok=True); pagina(W)
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path=motor.CHROME, args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = await br.new_page(viewport={"width": 1800, "height": 1000}); pg.on("pageerror", lambda e: print("ERR", e))
        await pg.goto("file://" + W + "robot.html"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=SALIDA + "robot-play.png", full_page=True); await br.close()
    print("listo", SALIDA + "robot-play.png")

if __name__ == "__main__": asyncio.run(main())
