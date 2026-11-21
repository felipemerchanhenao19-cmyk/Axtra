"""Bocetos del personaje principal en acabado low-poly: seis opciones para elegir (retrato de tres cuartos y cuerpo entero).
  python lowpoly.py  →  entregables/redes/bocetos/personaje-principal.png"""
import os, json, asyncio, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
_spec = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(motor)
RAIZ = motor.RAIZ; SALIDA = RAIZ + "entregables/redes/bocetos/"; THREE = motor.TRABAJO + "three/package/build/three.min.js"
OPCIONES = [
    dict(letra="01", nombre="", desc="Tupé despeinado, barba de pocos días, camisa negra. Mandíbula marcada y mirada segura.", cfg=dict(semilla=11, fuerte=True, peinado="tupe", barbaNivel=0.75)),
    dict(letra="02", nombre="", desc="Pelo hacia atrás, barba corta y definida, camisa blanca. Elegante y un poco arrogante.",
         cfg=dict(semilla=21, fuerte=True, peinado="atras", barbaNivel=0.95, piel="#c88e6c", camisa="#ecebe7", pelo="#15100d", barba="#1c1410")),
    dict(letra="03", nombre="", desc="Corte corto con volumen, barba de varios días, camisa verde oscuro. Moderno y directo.",
         cfg=dict(semilla=22, fuerte=True, peinado="corto", barbaNivel=0.85, piel="#b27a58", camisa="#24382c", pelo="#0f0c0a", barba="#16110e")),
    dict(letra="04", nombre="", desc="Pelo largo ondulado hacia atrás, barba llena, camisa de jean. Galán de película.",
         cfg=dict(semilla=23, fuerte=True, peinado="largo", barbaNivel=1.0, piel="#c99474", camisa="#34537a", pelo="#2a1b13", barba="#2a1b13")),
    dict(letra="05", nombre="", desc="Pelo despeinado, sin barba, camisa negra. Rasgos fuertes y cara limpia.",
         cfg=dict(semilla=24, fuerte=True, peinado="despeinado", barbaNivel=0.25, piel="#d7a684", camisa="#18191d", pelo="#1e1410")),
    dict(letra="06", nombre="", desc="Moño alto, barba llena, camisa beige. Seguro, creativo y con estilo.",
         cfg=dict(semilla=25, fuerte=True, peinado="mono", barbaNivel=1.0, piel="#bf8766", camisa="#c9b79a", pelo="#1a120d", barba="#1a120d")),
]
def main():
    leer = lambda p: open(p).read(); W = motor.TRABAJO + "bocetos/"; os.makedirs(W, exist_ok=True); os.makedirs(SALIDA, exist_ok=True)
    tarjetas = "".join(f'<div class="t"><div class="fotos"><img id="r{o["letra"]}"><img id="c{o["letra"]}"></div><h2><span>Opción</span> {o["letra"]}</h2><p>{o["desc"]}</p></div>' for o in OPCIONES)
    html = f'''<!doctype html><html><head><meta charset="utf-8">{leer(RAIZ + "produccion/videos/fuentes.html")}<style>
body{{margin:0;background:#0b1020;color:#eef2f6;font-family:Figtree;width:1800px}} h1{{font:800 56px Figtree;margin:40px 50px 4px}} .sub{{margin:0 50px 26px;color:#8a98a8;font:500 25px Figtree}}
.g{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;padding:0 50px 50px}} .t{{background:#141b2e;border-radius:24px;padding:16px 16px 22px}}
.fotos{{display:flex;gap:10px}} .fotos img{{width:50%;border-radius:16px}} h2{{font:800 34px Figtree;margin:14px 6px 0}} h2 span{{font:700 18px Figtree;letter-spacing:.18em;text-transform:uppercase;color:#e8a04a;margin-right:8px}}
p{{font:500 21px/1.35 Figtree;color:#b9c4d0;margin:6px 6px 0}}</style></head><body>
<h1>Personaje principal · hombre, rasgos fuertes</h1><div class="sub">Seis opciones masculinas con el acabado del video de referencia: mandíbula cuadrada, pómulos marcados, tabique recto, hombros anchos.</div><div class="g">{tarjetas}</div>
<canvas id="lienzo" width="600" height="800" style="display:none"></canvas>
<script src="file://{THREE}"></script>
<script>const PI = Math.PI; function semilla(s) {{ return () => {{ s |= 0; s = (s + 0x6d2b79f5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }}; }}
const OPS = {json.dumps(OPCIONES, ensure_ascii=False)};
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
const CAM = new THREE.PerspectiveCamera(30, 600 / 800, 0.05, 60);
OPS.forEach((o) => {{ const P = personaLowPoly(o.cfg); ESC.add(P.raiz); lampara.target = P.cabeza;
  P.pose({{ mira: 0.25, cejas: 0.3 }}); CAM.fov = 30; CAM.position.set(0.55, 1.72, 0.9); CAM.lookAt(0, 1.66, 0); CAM.updateProjectionMatrix(); REN.render(ESC, CAM); document.getElementById("r" + o.letra).src = REN.domElement.toDataURL("image/jpeg", 0.92);
  P.pose({{ mira: 0.3, bd: [-0.2, 0.25, -1.4] }}); CAM.fov = 34; CAM.position.set(1.1, 1.25, 3.3); CAM.lookAt(0, 0.95, 0); CAM.updateProjectionMatrix(); REN.render(ESC, CAM); document.getElementById("c" + o.letra).src = REN.domElement.toDataURL("image/jpeg", 0.92);
  ESC.remove(P.raiz); }});
</script></body></html>'''
    open(W + "lowpoly.html", "w").write(html)
    async def foto():
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            br = await p.chromium.launch(executable_path=motor.CHROME, args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
            pg = await br.new_page(viewport={"width": 1800, "height": 1000}); pg.on("pageerror", lambda e: print("ERR", e))
            await pg.goto("file://" + W + "lowpoly.html"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=SALIDA + "personaje-principal.png", full_page=True); await br.close()
    asyncio.run(foto()); print("listo", SALIDA + "personaje-principal.png")
if __name__ == "__main__": main()
