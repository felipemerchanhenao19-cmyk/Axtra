// «Laboratorio»: experimento de física sobre piso cuadriculado azul (estilo simulación), para ganchos de curiosidad.
// Una bola de luz recorre un tubo metálico en espiral; al salir NO sigue girando: sigue en línea recta (tangente) hasta «tu restaurante».
// Estado: e.bola (0..1 dentro del tubo, >1 fuera, en línea recta), e.idea (0..1 arco rojo «lo que la gente cree»),
// e.real (0..1 línea verde, trayectoria real), e.impacto (0..1 el local se ilumina), e.tarjeta (0..1) y e.tarjeta2 (0..1) carteles del producto.
function laboratorio(escena) {
  const G = new THREE.Group(); G.position.set(-200, 0, 0); escena.add(G); const U = {};
  U.fondo = 0x1d63f0; U.niebla = [0x2a6ef5, 0.012];
  // piso y ciclorama con cuadrícula (textura de canvas)
  const rejilla = (rep) => { const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d");
    g.fillStyle = "#1f62ef"; g.fillRect(0, 0, 256, 256); g.strokeStyle = "rgba(170,215,255,.85)"; g.lineWidth = 3; g.strokeRect(0, 0, 256, 256);
    g.strokeStyle = "rgba(150,200,255,.35)"; g.lineWidth = 1.5; for (let i = 64; i < 256; i += 64) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 256); g.moveTo(0, i); g.lineTo(256, i); g.stroke(); }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); t.anisotropy = 8; t.colorSpace = THREE.SRGBColorSpace; return t; };
  const piso = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.MeshStandardMaterial({ map: rejilla([40, 40]), roughness: 0.55, metalness: 0.0, emissive: 0x1a4fd0, emissiveIntensity: 0.55 }));
  piso.rotation.x = -PI / 2; piso.receiveShadow = true; G.add(piso);
  const ciclo = new THREE.Mesh(new THREE.CylinderGeometry(30, 30, 30, 64, 1, true), new THREE.MeshBasicMaterial({ map: rejilla([48, 18]), side: THREE.BackSide, color: 0xbcd4ff }));
  ciclo.position.set(0, 15, -2); G.add(ciclo);
  // reflejos para el metal: un entorno pequeño (cielo azul, piso claro y dos paneles de luz) pasado por PMREM
  const envE = new THREE.Scene(); const cielo = new THREE.Mesh(new THREE.SphereGeometry(10, 24, 12), new THREE.MeshBasicMaterial({ side: THREE.BackSide, vertexColors: true }));
  const cols = []; const pos = cielo.geometry.attributes.position; for (let i = 0; i < pos.count; i++) { const y = pos.getY(i) / 10; const c = new THREE.Color(0x2e74ff).lerp(new THREE.Color(0xeaf3ff), Math.max(0, y)).lerp(new THREE.Color(0x0b2a7a), Math.max(0, -y)); cols.push(c.r, c.g, c.b); }
  cielo.geometry.setAttribute("color", new THREE.Float32BufferAttribute(cols, 3)); envE.add(cielo);
  [[4, 6, 2], [-5, 4, -3]].forEach(([x, y, z]) => { const p = new THREE.Mesh(new THREE.PlaneGeometry(4, 2), new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide })); p.position.set(x, y, z); p.lookAt(0, 0, 0); envE.add(p); });
  const pm = new THREE.PMREMGenerator(REN); const env = pm.fromScene(envE, 0.02).texture;
  // trayectoria: entrada recta + hélice suave (1¼ vueltas) + salida
  const R = 1.2, Y0 = 1.2, SUBE = 0.3, FI = 2 * PI + PI / 2;
  const hel = (f) => new THREE.Vector3(R * Math.sin(f), Y0 + SUBE * f / (2 * PI), R * Math.cos(f));
  const pts = []; for (let i = 0; i <= 12; i++) pts.push(new THREE.Vector3(-4 + i * 4 / 12, Y0, R)); for (let i = 1; i <= 120; i++) pts.push(hel(FI * i / 120));
  const curva = new THREE.CatmullRomCurve3(pts, false, "centripetal"), LARGO = curva.getLength(), FIN = curva.getPointAt(1), DIR = curva.getTangentAt(1).setY(0).normalize();
  U.curva = curva; U.fin = FIN; U.dir = DIR;
  const metal = new THREE.MeshStandardMaterial({ color: 0x9aa3b0, metalness: 1.0, roughness: 0.2, envMap: env, envMapIntensity: 0.7 });
  const tubo = new THREE.Mesh(new THREE.TubeGeometry(curva, 480, 0.085, 20, false), metal); tubo.castShadow = true; G.add(tubo);
  const tuboIn = new THREE.Mesh(new THREE.TubeGeometry(curva, 480, 0.078, 20, false), new THREE.MeshStandardMaterial({ color: 0x2a2f38, metalness: 0.6, roughness: 0.5, side: THREE.BackSide })); G.add(tuboIn);
  // soportes del tubo
  for (let i = 0; i < 6; i++) { const p = hel(FI * (0.08 + i * 0.17)); const s = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, p.y, 8), metal); s.position.set(p.x, p.y / 2, p.z); s.castShadow = true; G.add(s); }
  // bola de luz con estela
  const glow = (() => { const c = document.createElement("canvas"); c.width = c.height = 128; const g = c.getContext("2d"), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, "rgba(255,255,240,1)"); gr.addColorStop(0.25, "rgba(255,200,110,.9)"); gr.addColorStop(1, "rgba(255,120,30,0)"); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })();
  const bola = new THREE.Mesh(new THREE.SphereGeometry(0.06, 16, 12), new THREE.MeshBasicMaterial({ color: 0xfff4dc })); G.add(bola);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false })); halo.scale.setScalar(0.38); G.add(halo);
  const luzBola = new THREE.PointLight(0xffb060, 3, 2.5, 2); G.add(luzBola);
  const estela = []; for (let i = 0; i < 18; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, opacity: 0.5 * (1 - i / 18) })); s.scale.setScalar(0.24 * (1 - i / 22)); G.add(s); estela.push(s); }
  const posBola = (s) => s <= 1 ? curva.getPointAt(Math.max(0, s)) : FIN.clone().addScaledVector(DIR, (s - 1) * LARGO);
  U.posBola = posBola;
  // puntos: arco rojo (lo que la gente cree) y línea verde (lo que pasa)
  const puntos = (lista, color) => { const m = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0, fog: false }); const g = new THREE.Group();
    lista.forEach((p) => { const d = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 6), m); d.position.copy(p); g.add(d); }); G.add(g); return { g, m, n: lista.length }; };
  const arco = []; for (let i = 1; i <= 34; i++) { const f = FI + i * 0.14; arco.push(new THREE.Vector3(R * Math.sin(f), FIN.y, R * Math.cos(f))); }
  const recta = []; for (let i = 1; i <= 60; i++) recta.push(FIN.clone().addScaledVector(DIR, i * 0.16));
  const pIdea = puntos(arco, 0xff4b4b), pReal = puntos(recta, 0x4cff8a);
  const marcaX = new THREE.Group(); [1, -1].forEach((k) => { const b = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.07, 0.07), new THREE.MeshBasicMaterial({ color: 0xff3b3b, fog: false })); b.rotation.z = k * PI / 4; marcaX.add(b); });
  marcaX.position.copy(arco[10]).add(new THREE.Vector3(0, 0.25, 0)); marcaX.scale.setScalar(0.001); G.add(marcaX);
  // «tu restaurante»: fachada low-poly al final de la línea recta
  const F = (c, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.7, flatShading: true }, o));
  const local = new THREE.Group(); const dLocal = 9.5; local.position.copy(FIN).addScaledVector(DIR, dLocal).setY(0); local.rotation.y = Math.atan2(-DIR.x, -DIR.z); G.add(local); U.local = local;   // la fachada (+z) mira hacia la bola
  const caja = (w, h, d, m, x, y, z) => { const o = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; local.add(o); return o; };
  caja(3.4, 2.8, 2, F(0xe9dcc6), 0, 1.4, -1); caja(3.6, 0.2, 2.2, F(0x5a3a26), 0, 2.9, -1); caja(3.5, 0.25, 0.1, F(0x5a3a26), 0, 0.12, 0.02);
  const vidrio = F(0x3a2614, { emissive: 0xffb45a, emissiveIntensity: 0.5 }); caja(1.0, 1.2, 0.05, vidrio, -1.05, 1.25, 0.01); caja(1.0, 1.2, 0.05, vidrio, 1.05, 1.25, 0.01); caja(0.8, 1.9, 0.05, vidrio, 0, 0.95, 0.01);
  const toldo = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 3.3, 3, 1, false, 0, PI), F(0xe8a04a)); toldo.rotation.z = PI / 2; toldo.position.set(0, 2.1, 0.12); local.add(toldo);
  const letrero = (U.letrero = () => { const c = document.createElement("canvas"); c.width = 1024; c.height = 192; const g = c.getContext("2d"); g.fillStyle = "#14100c"; g.fillRect(0, 0, 1024, 192);
    g.font = "800 104px Figtree"; g.textAlign = "center"; g.fillStyle = "#ffcf7a"; g.shadowColor = "#ff9a2a"; g.shadowBlur = 30; g.fillText("TU RESTAURANTE", 512, 132); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; });
  const cartel = new THREE.Mesh(new THREE.PlaneGeometry(3.0, 0.56), new THREE.MeshBasicMaterial({ toneMapped: false })); cartel.position.set(0, 2.55, 0.03); local.add(cartel);
  U.cartel = cartel; const luzLocal = new THREE.PointLight(0xffb45a, 0, 6, 2); luzLocal.position.set(0, 1.4, 1.2); local.add(luzLocal);
  // carteles del producto (tarjetas flotantes)
  const pendientes = [];
  const tarjeta = (dibujar) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(1.65, 1.0), new THREE.MeshBasicMaterial({ transparent: true, toneMapped: false, fog: false })); m.scale.setScalar(0.001); G.add(m);
    pendientes.push(() => { const c = document.createElement("canvas"); c.width = 1024; c.height = 620; const g = c.getContext("2d"); const rr = (x, y, w, h, r) => { g.beginPath(); g.roundRect(x, y, w, h, r); };
    rr(8, 8, 1008, 604, 48); g.fillStyle = "rgba(9,14,26,.94)"; g.fill(); g.lineWidth = 6; g.strokeStyle = "rgba(76,255,138,.8)"; g.stroke(); dibujar(g, rr);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; m.material.map = t; m.material.needsUpdate = true; }); return m; };
  const T = (g, s, x, y, f, c, al = "left") => { g.font = f; g.fillStyle = c; g.textAlign = al; g.fillText(s, x, y); };
  const t1 = tarjeta((g, rr) => { T(g, "PEDIDO NUEVO", 70, 120, "800 46px Figtree", "#7d8b99"); T(g, "Directo a tu restaurante", 70, 220, "800 66px Figtree", "#ffffff");
    T(g, "Apps en el medio:", 70, 340, "600 48px Figtree", "#9fb0c2"); T(g, "ninguna", 954, 340, "800 52px Figtree", "#4cff8a", "right");
    T(g, "Comisión:", 70, 440, "600 48px Figtree", "#9fb0c2"); T(g, "$ 0", 954, 440, "800 60px Figtree", "#ffcf7a", "right"); });
  const t2 = tarjeta((g, rr) => { g.fillStyle = "#36c2f5"; rr(70, 70, 70, 70, 18); g.fill(); T(g, "Apex Domicilios", 165, 128, "800 62px Figtree", "#ffffff");
    ["Tu propio link de pedidos", "Pago con Wompi o comprobante", "Aviso automático: «ya salió»"].forEach((s, i) => { T(g, "✓", 80, 260 + i * 110, "800 56px Figtree", "#4cff8a"); T(g, s, 150, 260 + i * 110, "700 52px Figtree", "#eef4fa"); }); });
  let listo = false;
  U.paso = (tt, e = {}) => {
    if (!listo) { listo = true; cartel.material.map = U.letrero(); cartel.material.needsUpdate = true; pendientes.forEach((f) => f()); }
    const s = e.bola ?? 0, p = posBola(s); bola.position.copy(p); halo.position.copy(p); luzBola.position.copy(p);
    const dentro = s > 0.002 && s < 1; halo.material.opacity = dentro ? 0.75 : 1; luzBola.intensity = dentro ? 1.6 : 3;
    estela.forEach((m, i) => { const q = s - (i + 1) * 0.006 * (s > 1 ? 1.6 : 1); m.visible = s > 0.01 && q > 0; if (m.visible) m.position.copy(posBola(q)); });
    pIdea.m.opacity = Math.min(1, e.idea ?? 0); pIdea.g.children.forEach((d, i) => { d.visible = i / pIdea.n <= (e.idea ?? 0) * 1.05; });
    pReal.m.opacity = Math.min(1, e.real ?? 0); pReal.g.children.forEach((d, i) => { d.visible = i / pReal.n <= (e.real ?? 0) * 1.05; });
    marcaX.scale.setScalar(Math.max(0.001, Math.min(1, (e.tache ?? 0) * 1.2)) * (1 + 0.15 * Math.sin(tt * 9) * (e.tache > 0 && e.tache < 1 ? 1 : 0)));
    const im = e.impacto ?? 0; vidrio.emissiveIntensity = 0.5 + 1.4 * im; luzLocal.intensity = 9 * im;
    [[t1, e.tarjeta ?? 0], [t2, e.tarjeta2 ?? 0]].forEach(([m, k]) => { const a = Math.min(1, k); const pop = a <= 0 ? 0.001 : (a < 1 ? 1 + 0.12 * Math.sin(a * PI) : 1) * a;
      m.scale.setScalar(Math.max(0.001, pop)); m.position.copy(local.position).add(new THREE.Vector3(0, 3.75 + 0.04 * Math.sin(tt * 2), 0)).addScaledVector(DIR, -0.6); m.lookAt(CAM.position); });
  };
  G.userData = U; return G;
}
