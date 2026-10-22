// Escenarios 3D de «Turno de noche»: el restaurante (salón, barra, cocina al fondo, ventana con lluvia) y la oficina.
// Todo con bloques, luces de cine (lámparas colgantes con sombra, velas, neón de la calle) y texturas de píxel.
function texCanvas(w, h, dibujo, rep = [1, 1], pixel = true) {
  const c = document.createElement("canvas"); c.width = w; c.height = h; dibujo(c.getContext("2d"), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]);
  if (pixel) { t.magFilter = THREE.NearestFilter; } t.anisotropy = 4; t.userData = { c, dibujo }; return t;
}
function plano(w, h, material, x, y, z, rx = 0, ry = 0, padre) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), material); m.position.set(x, y, z); m.rotation.set(rx, ry, 0); m.receiveShadow = true; padre.add(m); return m;
}
const TEX = {
  madera: () => texCanvas(64, 64, (g) => { const r = semilla(3); for (let i = 0; i < 8; i++) { const v = 70 + r() * 25; g.fillStyle = `rgb(${v + 40},${v + 12},${v - 18})`; g.fillRect(0, i * 8, 64, 8);
    g.fillStyle = "rgba(0,0,0,.35)"; g.fillRect(0, i * 8 + 7, 64, 1); g.fillRect(Math.floor(r() * 64), i * 8, 1, 8); } }, [10, 10]),
  ladrillo: () => texCanvas(64, 64, (g) => { const r = semilla(5); g.fillStyle = "#3b2520"; g.fillRect(0, 0, 64, 64);
    for (let y = 0; y < 8; y++) for (let x = -1; x < 4; x++) { const v = r() * 30; g.fillStyle = `rgb(${120 + v},${62 + v * 0.5},${48 + v * 0.3})`; g.fillRect(x * 16 + (y % 2) * 8 + 1, y * 8 + 1, 14, 6); } }, [6, 2]),
  baldosa: () => texCanvas(32, 32, (g) => { g.fillStyle = "#e8e2d4"; g.fillRect(0, 0, 32, 32); g.fillStyle = "#2c2a28"; g.fillRect(0, 0, 16, 16); g.fillRect(16, 16, 16, 16); }, [8, 8]),
  pared: (c1, c2) => texCanvas(32, 32, (g) => { g.fillStyle = c1; g.fillRect(0, 0, 32, 32); const r = semilla(9); for (let i = 0; i < 60; i++) { g.fillStyle = c2; g.fillRect(Math.floor(r() * 32), Math.floor(r() * 32), 1, 1); } }, [6, 2]),
};
// QR de mesa (patrón fijo, como el de las películas)
function texQR(n) {
  return texCanvas(64, 80, (g) => { g.fillStyle = "#f4f8fb"; g.fillRect(0, 0, 64, 80); const r = semilla(n * 7 + 1);
    for (let y = 0; y < 9; y++) for (let x = 0; x < 9; x++) if (r() > 0.5) { g.fillStyle = "#0b1626"; g.fillRect(5 + x * 6, 5 + y * 6, 6, 6); }
    [[5, 5], [41, 5], [5, 41]].forEach(([x, y]) => { g.fillStyle = "#0b1626"; g.fillRect(x, y, 18, 18); g.fillStyle = "#f4f8fb"; g.fillRect(x + 3, y + 3, 12, 12); g.fillStyle = "#0b1626"; g.fillRect(x + 6, y + 6, 6, 6); });
    g.fillStyle = "#0b1626"; g.font = "bold 11px sans-serif"; g.textAlign = "center"; g.fillText("MESA " + n, 32, 75); });
}
// Foto real del plato: la bandeja paisa recortada (fotos/bandeja.png) sobre un disco
let TEX_BANDEJA = null;
function platoBandeja() {
  if (!TEX_BANDEJA) { TEX_BANDEJA = new THREE.TextureLoader().load("fotos/bandeja.png"); TEX_BANDEJA.colorSpace = THREE.SRGBColorSpace; }
  const m = new THREE.Mesh(new THREE.CircleGeometry(0.17, 40), new THREE.MeshStandardMaterial({ map: TEX_BANDEJA, transparent: true, roughness: 0.6 }));
  m.rotation.x = -PI / 2; m.receiveShadow = true; return m;
}

// ---------- Mesa con sillas, vela, QR y (opcional) platos reales
function mesa(n, x, z, padre, o = {}) {
  const g = new THREE.Group(); g.position.set(x, 0, z); padre.add(g);
  const mMadera = mat("#6b4a32"), mMantel = mat(o.mantel || "#7a2a2a");
  caja(1.1, 0.06, 1.1, mMantel, 0, 0.76, 0, g); caja(1.14, 0.12, 1.14, mMantel, 0, 0.7, 0, g).scale.set(1, 1, 1);
  caja(0.1, 0.7, 0.1, mMadera, 0, 0.35, 0, g); caja(0.5, 0.04, 0.5, mMadera, 0, 0.02, 0, g);
  if (o.sillas !== false) [[0, 0.75], [0, -0.75]].forEach(([sx, sz]) => { const s = new THREE.Group(); s.position.set(sx, 0, sz); s.rotation.y = sz > 0 ? PI : 0; g.add(s);
    caja(0.46, 0.06, 0.44, mMadera, 0, 0.46, 0, s); caja(0.46, 0.55, 0.06, mMadera, 0, 0.75, -0.21, s); [[-0.2, -0.19], [0.2, -0.19], [-0.2, 0.19], [0.2, 0.19]].forEach(([a, b]) => caja(0.05, 0.46, 0.05, mMadera, a, 0.23, b, s)); });
  // vela con luz
  caja(0.06, 0.12, 0.06, mat("#efe6d0"), -0.25, 0.85, -0.2, g);
  const llama = new THREE.Mesh(new THREE.SphereGeometry(0.022, 8, 6), new THREE.MeshBasicMaterial({ color: 0xffc56a })); llama.scale.y = 1.8; llama.position.set(-0.25, 0.94, -0.2); g.add(llama);
  if (o.luz !== false) { const l = new THREE.PointLight(0xffa04a, 1.2, 2.6, 2); l.position.set(-0.25, 1.0, -0.2); g.add(l); g.userData.vela = l; }
  g.userData.llama = llama;
  // QR en su base de acrílico
  const qr = new THREE.Group(); qr.position.set(0.32, 0.79, -0.25); g.add(qr);
  caja(0.16, 0.02, 0.08, mat("#cfe6f5", { op: 0.6, r: 0.1 }), 0, 0, 0, qr);
  const placa = new THREE.Mesh(new THREE.PlaneGeometry(0.13, 0.16), new THREE.MeshStandardMaterial({ map: texQR(n), roughness: 0.4, emissive: 0x2fbbe8, emissiveIntensity: 0 }));
  placa.position.y = 0.09; placa.rotation.y = o.qrRot || 0; qr.add(placa); g.userData.qr = placa;
  if (o.platos) o.platos.forEach(([px, pz]) => { const p = platoBandeja(); p.position.set(px, 0.795, pz); g.add(p); });
  if (o.limonada) { const v = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.035, 0.15, 12), mat("#f4f6f0", { r: 0.2, liso: true })); v.position.set(0.1, 0.87, 0.2); v.castShadow = true; g.add(v); }
  return g;
}
// ---------- Lámpara colgante con foco de sombra
function lampara(x, z, padre, o = {}) {
  const g = new THREE.Group(); g.position.set(x, 0, z); padre.add(g);
  caja(0.02, 0.9, 0.02, mat("#111"), 0, 3.1, 0, g, false);
  const pantalla = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.24, 12, 1, true), new THREE.MeshStandardMaterial({ color: 0x1d2a24, side: THREE.DoubleSide, roughness: 0.6, metalness: 0.4 }));
  pantalla.position.y = 2.55; g.add(pantalla);
  const foco = new THREE.Mesh(new THREE.SphereGeometry(0.07, 10, 8), new THREE.MeshBasicMaterial({ color: 0xffe2b0 })); foco.position.y = 2.46; g.add(foco);
  const l = new THREE.SpotLight(o.color || 0xffc48a, (o.i ?? 18) * 3.2, 10, 0.8, 0.55, 1.4); l.position.set(0, 2.45, 0); l.target.position.set(0, 0, 0); g.add(l); g.add(l.target);
  if (o.sombra !== false) { l.castShadow = true; l.shadow.mapSize.set(1024, 1024); l.shadow.bias = -0.0008; l.shadow.radius = 4; }
  g.userData.luz = l; return g;
}
// Lluvia en la ventana: textura que se redibuja cada cuadro
function ventanaLluvia(w, h) {
  const t = texCanvas(128, 160, () => {}, [1, 1], false), c = t.userData.c, g = c.getContext("2d"), r = semilla(21), gotas = Array.from({ length: 90 }, () => [r() * 128, r() * 160, 0.5 + r()]);
  t.userData.paso = (tt, rayo = 0) => {
    const gr = g.createLinearGradient(0, 0, 0, 160); gr.addColorStop(0, `rgb(${18 + rayo * 180},${30 + rayo * 190},${58 + rayo * 190})`); gr.addColorStop(1, `rgb(${8 + rayo * 120},${14 + rayo * 130},${30 + rayo * 140})`);
    g.fillStyle = gr; g.fillRect(0, 0, 128, 160);
    // luces de la calle desenfocadas
    [[20, 120, "255,170,80"], [70, 130, "80,200,255"], [105, 115, "255,90,120"], [45, 140, "255,210,140"]].forEach(([x, y, col], i) => {
      const rr = g.createRadialGradient(x, y, 0, x, y, 22); rr.addColorStop(0, `rgba(${col},${0.55 + 0.1 * Math.sin(tt * 2 + i)})`); rr.addColorStop(1, `rgba(${col},0)`); g.fillStyle = rr; g.fillRect(0, 0, 128, 160); });
    g.strokeStyle = "rgba(190,220,255,.35)"; g.lineWidth = 1;
    gotas.forEach(([x, y, v]) => { const yy = (y + tt * 60 * v) % 170 - 10; g.beginPath(); g.moveTo(x, yy); g.lineTo(x - 1, yy + 8 * v); g.stroke(); });
    t.needsUpdate = true;
  };
  return t;
}
// Pantalla con texto (tablet de la caja, portátil): se redibuja según la escena
function pantallaTexto(w, h, pintar) {
  const t = texCanvas(w, h, () => {}, [1, 1], false); t.userData.pintar = (estado, tt) => { pintar(t.userData.c.getContext("2d"), w, h, estado, tt); t.needsUpdate = true; }; return t;
}

// ---------- Restaurante «La Fonda de Don Jairo»
function restaurante(escena) {
  const R = new THREE.Group(); escena.add(R); const U = {};
  const piso = plano(20, 20, new THREE.MeshStandardMaterial({ map: TEX.madera(), roughness: 0.75 }), 0, 0, 0, -PI / 2, 0, R);
  const mLadrillo = new THREE.MeshStandardMaterial({ map: TEX.ladrillo(), roughness: 0.9 }), mPared = new THREE.MeshStandardMaterial({ map: TEX.pared("#6f5a44", "#5e4b38"), roughness: 0.95 });
  plano(14, 3.4, mLadrillo, 0, 1.7, -6, 0, 0, R);                    // pared del fondo
  plano(14, 3.4, mPared, 6.5, 1.7, 0, 0, -PI / 2, R);                 // pared derecha
  // pared izquierda con ventana grande
  const izq = new THREE.Group(); izq.position.set(-6, 0, 0); izq.rotation.y = PI / 2; R.add(izq);
  plano(14, 0.9, mPared, 0, 0.45, 0, 0, 0, izq); plano(14, 0.6, mPared, 0, 3.1, 0, 0, 0, izq); plano(4, 1.9, mPared, -5, 1.85, 0, 0, 0, izq); plano(4, 1.9, mPared, 5, 1.85, 0, 0, 0, izq);
  U.lluvia = ventanaLluvia(); const vidrio = plano(6, 1.9, new THREE.MeshBasicMaterial({ map: U.lluvia }), 0, 1.85, -0.05, 0, 0, izq);
  [-3, -1, 1, 3].forEach((x) => caja(0.08, 1.95, 0.12, mat("#2a1d14"), x, 1.85, 0, izq)); caja(6.1, 0.1, 0.25, mat("#2a1d14"), 0, 0.9, 0.05, izq);
  const luna = new THREE.DirectionalLight(0x6f9cff, 0.35); luna.position.set(-10, 6, 2); R.add(luna);
  plano(14, 14, new THREE.MeshStandardMaterial({ color: 0x1a120c, roughness: 1 }), 0, 3.4, 0, PI / 2, 0, R);   // techo
  // barra con estantería de botellas y la cocina al fondo
  const mBarra = mat("#4a2f1e"), mTope = mat("#2b1b12", { r: 0.4 });
  caja(4.2, 1.05, 0.7, mBarra, 0.8, 0.525, -3.6, R); caja(4.4, 0.06, 0.85, mTope, 0.8, 1.08, -3.6, R);
  for (let i = 0; i < 6; i++) caja(4.2 / 6 - 0.08, 0.8, 0.02, mat("#5c3c27"), 0.8 - 2.1 + (i + 0.5) * 0.7, 0.5, -3.24, R);
  caja(3.4, 0.05, 0.35, mat("#3a2618"), 1.2, 1.6, -5.8, R); caja(3.4, 0.05, 0.35, mat("#3a2618"), 1.2, 2.1, -5.8, R);
  const rb = semilla(31); for (let i = 0; i < 22; i++) { const col = ["#3f6b3a", "#7a3b1d", "#c9a24a", "#2a4a6a", "#8a2a3a", "#d8d0b8"][Math.floor(rb() * 6)];
    const b = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.05, 0.28 + rb() * 0.08, 8), new THREE.MeshStandardMaterial({ color: col, roughness: 0.15, metalness: 0.1, emissive: col, emissiveIntensity: 0.12 }));
    b.position.set(-0.4 + (i % 11) * 0.32, i < 11 ? 1.78 : 2.28, -5.78); R.add(b); }
  // ventana de la cocina (pase) con luz naranja y comandas colgando
  caja(2.2, 0.08, 0.3, mat("#2a1d14"), -2.6, 1.15, -5.9, R); const pase = plano(2.2, 1.0, new THREE.MeshBasicMaterial({ map: texCanvas(64, 32, (g) => { const gr = g.createLinearGradient(0, 0, 0, 32); gr.addColorStop(0, '#5a2a10'); gr.addColorStop(1, '#c0602a'); g.fillStyle = gr; g.fillRect(0, 0, 64, 32); g.fillStyle = 'rgba(20,10,5,.6)'; g.fillRect(6, 12, 10, 20); g.fillRect(40, 8, 12, 24); g.fillStyle = '#ffb060'; g.fillRect(24, 22, 10, 3); }) }), -2.6, 1.7, -5.98, 0, 0, R);
  const luzCocina = new THREE.PointLight(0xff7a2a, 4, 6, 2); luzCocina.position.set(-2.6, 1.7, -5.5); R.add(luzCocina); U.luzCocina = luzCocina;
  U.comandas = []; for (let i = 0; i < 6; i++) { const c = plano(0.16, 0.22, new THREE.MeshStandardMaterial({ color: 0xf4efe2, side: THREE.DoubleSide }), -3.4 + i * 0.32, 2.05, -5.85, 0, 0, R); U.comandas.push(c); }
  // tableta de la caja sobre la barra (aquí llegan los pedidos)
  U.tablet = pantallaTexto(256, 180, (g, w, h, e = {}) => {
    g.fillStyle = "#0b1626"; g.fillRect(0, 0, w, h); g.fillStyle = "#7fd8f0"; g.font = "bold 16px sans-serif"; g.fillText("APEX · CAJA", 14, 26);
    g.fillStyle = "#4a5668"; g.fillRect(14, 36, w - 28, 1);
    (e.pedidos || []).forEach((p, i) => { const y = 50 + i * 44, nuevo = i === 0 && e.nuevo; g.fillStyle = nuevo ? "rgba(47,187,232,.25)" : "rgba(255,255,255,.06)"; g.fillRect(14, y, w - 28, 38);
      g.fillStyle = nuevo ? "#bff3ff" : "#e4eef6"; g.font = "bold 14px sans-serif"; g.fillText(p[0], 22, y + 16); g.fillStyle = "#9fb4c8"; g.font = "12px sans-serif"; g.fillText(p[1], 22, y + 31); });
    if (!(e.pedidos || []).length) { g.fillStyle = "#6a7c90"; g.font = "13px sans-serif"; g.fillText("Esperando pedidos…", 22, 70); }
  });
  const tab = new THREE.Group(); tab.position.set(1.7, 1.12, -3.45); tab.rotation.set(-0.55, -0.35, 0); R.add(tab);
  caja(0.36, 0.26, 0.02, mat("#111821", { r: 0.3 }), 0, 0.13, 0, tab); const ptab = new THREE.Mesh(new THREE.PlaneGeometry(0.33, 0.23), new THREE.MeshBasicMaterial({ map: U.tablet })); ptab.position.set(0, 0.13, 0.011); tab.add(ptab);
  caja(0.1, 0.12, 0.06, mat("#111821"), 0, 0.03, -0.06, tab);
  // cuadros en la pared derecha y planta
  [[-2, "#8a5a2a"], [1.5, "#2a5a6a"]].forEach(([z, c]) => { caja(0.05, 0.8, 1.1, mat("#2a1d14"), 6.45, 1.9, z, R); caja(0.02, 0.66, 0.96, mat(c), 6.42, 1.9, z, R); });
  caja(0.4, 0.4, 0.4, mat("#5c3c27"), 5.8, 0.2, -5.4, R); caja(0.6, 0.9, 0.6, mat("#2f5a2a"), 5.8, 0.85, -5.4, R);
  // mesas: 4, 7, 9 y 2 (con su número para el QR)
  U.mesas = { 7: mesa(7, -2.6, 0.6, R, { platos: [], qrRot: 0.4 }), 4: mesa(4, 2.4, 0.4, R, { qrRot: -0.4 }), 9: mesa(9, -2.4, 3.4, R, { luz: false }), 2: mesa(2, 2.6, 3.2, R, { luz: false }) };
  U.lamparas = [lampara(-2.6, 0.6, R), lampara(2.4, 0.4, R), lampara(0.8, -3.4, R, { i: 14 }), lampara(-2.4, 3.4, R, { i: 10, sombra: false }), lampara(2.6, 3.2, R, { i: 10, sombra: false })];
  const amb = new THREE.HemisphereLight(0x8a96b0, 0x4a3020, 1.1); R.add(amb);
  R.userData = U;
  U.paso = (tt, e = {}) => {
    U.lluvia.userData.paso(tt, e.rayo || 0);
    Object.values(U.mesas).forEach((m, i) => { if (m.userData.vela) m.userData.vela.intensity = 1.2 + 0.25 * Math.sin(tt * 11 + i * 2) + 0.06 * Math.sin(tt * 23 + i); m.userData.llama.scale.y = 1.8 + 0.25 * Math.sin(tt * 13 + i); });
    U.comandas.forEach((c, i) => { c.rotation.z = 0.06 * Math.sin(tt * 1.5 + i); c.visible = i < (e.comandas ?? 3); });
    luzCocina.intensity = 2.0 + 0.4 * Math.sin(tt * 7) * Math.sin(tt * 3.3);
    U.tablet.userData.pintar(e.tablet || {}, tt);
    Object.entries(U.mesas).forEach(([n, m]) => { m.userData.qr.material.emissiveIntensity = (e.qrLuz && e.qrLuz[n]) || 0; });
  };
  return R;
}

// ---------- Oficina de atrás: escritorio, portátil con las cifras, lámpara, ventana con tormenta
function oficina(escena) {
  const O = new THREE.Group(); escena.add(O); const U = {};
  O.position.set(40, 0, 0);
  plano(10, 10, new THREE.MeshStandardMaterial({ map: TEX.baldosa(), roughness: 0.6 }), 0, 0, 0, -PI / 2, 0, O);
  const mPared = new THREE.MeshStandardMaterial({ map: TEX.pared("#3c4a52", "#33414a"), roughness: 0.95 });
  plano(10, 3.2, mPared, 0, 1.6, -3, 0, 0, O); plano(10, 3.2, mPared, -3.5, 1.6, 0, 0, PI / 2, O); plano(10, 3.2, mPared, 3.5, 1.6, 0, 0, -PI / 2, O);
  plano(10, 10, new THREE.MeshStandardMaterial({ color: 0x151a1e }), 0, 3.2, 0, PI / 2, 0, O);
  // ventana con tormenta en la pared del fondo
  U.lluvia = ventanaLluvia(); plano(1.6, 1.2, new THREE.MeshBasicMaterial({ map: U.lluvia }), 1.6, 1.8, -2.98, 0, 0, O);
  caja(1.7, 0.08, 0.1, mat("#1e2428"), 1.6, 1.2, -2.95, O); caja(1.7, 0.08, 0.1, mat("#1e2428"), 1.6, 2.4, -2.95, O); caja(0.06, 1.2, 0.1, mat("#1e2428"), 1.6, 1.8, -2.95, O);
  U.rayo = new THREE.DirectionalLight(0xc8dcff, 0); U.rayo.position.set(1.6, 3, -6); U.rayo.target.position.set(0, 0, 1); O.add(U.rayo); O.add(U.rayo.target);
  // escritorio, portátil, papeles, calculadora, taza
  const mEsc = mat("#5a3e2a");
  caja(1.8, 0.06, 0.85, mEsc, 0, 0.76, 0, O); [[-0.82, -0.36], [0.82, -0.36], [-0.82, 0.36], [0.82, 0.36]].forEach(([x, z]) => caja(0.07, 0.73, 0.07, mEsc, x, 0.365, z, O));
  U.portatil = pantallaTexto(512, 330, (g, w, h, e = {}) => {
    g.fillStyle = "#0b1626"; g.fillRect(0, 0, w, h); g.fillStyle = "#7fd8f0"; g.font = "bold 20px sans-serif"; g.fillText(e.titulo || "Domicilios · este mes", 28, 44);
    g.fillStyle = "#33414a"; g.fillRect(28, 60, w - 56, 2);
    (e.filas || []).forEach(([a, b, color], i) => { const y = 108 + i * 64; g.fillStyle = "#c8d6e4"; g.font = "18px sans-serif"; g.fillText(a, 28, y);
      g.fillStyle = color || "#ffffff"; g.font = "bold 34px sans-serif"; g.textAlign = "right"; g.fillText(b, w - 28, y + 6); g.textAlign = "left"; });
    if (e.alerta) { g.fillStyle = "rgba(255,70,80,.18)"; g.fillRect(20, h - 70, w - 40, 50); g.fillStyle = "#ff8a90"; g.font = "bold 18px sans-serif"; g.fillText(e.alerta, 36, h - 38); }
  });
  const lap = new THREE.Group(); lap.position.set(0.15, 0.79, -0.05); lap.rotation.y = -0.15; O.add(lap);
  caja(0.62, 0.025, 0.42, mat("#2a3138", { r: 0.35, m: 0.3 }), 0, 0.012, 0, lap);
  const tapa = new THREE.Group(); tapa.position.set(0, 0.02, -0.2); tapa.rotation.x = -0.25; lap.add(tapa);
  caja(0.62, 0.42, 0.02, mat("#2a3138", { r: 0.35, m: 0.3 }), 0, 0.21, 0, tapa);
  const pl = new THREE.Mesh(new THREE.PlaneGeometry(0.58, 0.37), new THREE.MeshBasicMaterial({ map: U.portatil })); pl.position.set(0, 0.21, 0.011); tapa.add(pl);
  U.luzPantalla = new THREE.PointLight(0x6fc8ff, 2.0, 2.6, 2); U.luzPantalla.position.set(0, 0.3, 0.2); lap.add(U.luzPantalla);
  U.puntoPantalla = new THREE.Vector3(); lap.updateMatrixWorld(); U.lap = lap; U.tapa = tapa;
  caja(0.3, 0.01, 0.4, mat("#efeae0"), -0.6, 0.795, 0.1, O).rotation.y = 0.2; caja(0.28, 0.01, 0.38, mat("#e4ddd0"), -0.58, 0.805, 0.08, O).rotation.y = -0.1;
  caja(0.14, 0.03, 0.2, mat("#1d1f22"), 0.62, 0.805, 0.12, O);
  const taza = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.045, 0.1, 12), mat("#f2efe8")); taza.position.set(-0.45, 0.84, -0.25); taza.castShadow = true; O.add(taza);
  // lámpara de escritorio (luz cálida principal) y sillas
  caja(0.12, 0.03, 0.12, mat("#1d1f22"), -0.7, 0.8, -0.3, O); caja(0.025, 0.45, 0.025, mat("#1d1f22"), -0.7, 1.02, -0.3, O);
  const cab = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.14, 10, 1, true), new THREE.MeshStandardMaterial({ color: 0x2a4a3a, side: THREE.DoubleSide, metalness: 0.4, roughness: 0.4 })); cab.position.set(-0.6, 1.25, -0.25); cab.rotation.z = 0.7; O.add(cab);
  const lam = new THREE.SpotLight(0xffc27a, 22, 6, 0.95, 0.6, 1.3); lam.position.set(-0.58, 1.24, -0.24); lam.target.position.set(0.1, 0.78, 0.15); lam.castShadow = true; lam.shadow.mapSize.set(1024, 1024); lam.shadow.bias = -0.0008; O.add(lam); O.add(lam.target);
  const techo = new THREE.SpotLight(0x8fa8c8, 18, 9, 0.9, 0.8, 1.3); techo.position.set(0.5, 3.1, 1.2); techo.target.position.set(0, 0, 0); techo.castShadow = true; techo.shadow.mapSize.set(1024, 1024); O.add(techo); O.add(techo.target);
  const silla = (x, z, ry) => { const s = new THREE.Group(); s.position.set(x, 0, z); s.rotation.y = ry; O.add(s); const m = mat("#22262b");
    caja(0.5, 0.08, 0.5, m, 0, 0.48, 0, s); caja(0.5, 0.6, 0.07, m, 0, 0.82, -0.23, s); caja(0.06, 0.44, 0.06, m, 0, 0.24, 0, s); caja(0.5, 0.04, 0.5, m, 0, 0.03, 0, s); };
  silla(0, -0.75, 0); silla(0, 0.85, PI);
  // estante con carpetas y un calendario
  caja(1.2, 0.04, 0.3, mat("#3a2a1e"), -2.2, 1.5, -2.85, O); const rr = semilla(41);
  for (let i = 0; i < 9; i++) caja(0.08, 0.3, 0.24, mat(["#7a2a2a", "#2a4a6a", "#c9a24a", "#2f5a2a"][i % 4]), -2.7 + i * 0.11, 1.67, -2.85, O).rotation.z = (rr() - 0.5) * 0.1;
  caja(0.5, 0.6, 0.02, mat("#efeae0"), -1.0, 1.9, -2.98, O);
  O.add(new THREE.HemisphereLight(0x7a8aaa, 0x3a3028, 0.9));
  O.userData = U;
  U.paso = (tt, e = {}) => { U.lluvia.userData.paso(tt, e.rayo || 0); U.rayo.intensity = (e.rayo || 0) * 6; U.portatil.userData.pintar(e.portatil || {}, tt); U.luzPantalla.intensity = 2.0 + (e.rojo ? 0.8 : 0); U.luzPantalla.color.set(e.rojo ? 0xff6a70 : 0x6fc8ff); U.lap.rotation.y = e.lapRot ?? -0.15; };
  return O;
}

// ---------- Sala de juntas de Apex: piso de bloques con botones, mesa larga, ventanal de ciudad de noche y el letrero de la marca
function sala(escena) {
  const S = new THREE.Group(); escena.add(S); const U = {};
  S.position.set(-40, 0, 0);
  const botones = texCanvas(32, 32, (g) => { g.fillStyle = "#1b2433"; g.fillRect(0, 0, 32, 32); const r = g.createRadialGradient(13, 13, 2, 16, 16, 11);
    r.addColorStop(0, "#3a4a63"); r.addColorStop(0.7, "#243048"); r.addColorStop(1, "#141b28"); g.fillStyle = r; g.beginPath(); g.arc(16, 16, 10, 0, PI * 2); g.fill(); }, [60, 60], false);
  plano(24, 24, new THREE.MeshStandardMaterial({ map: botones, roughness: 0.35, metalness: 0.1 }), 0, 0, 0, -PI / 2, 0, S);
  const mMuro = new THREE.MeshStandardMaterial({ color: 0x141a24, roughness: 0.6 });
  plano(16, 4, mMuro, 0, 2, 6, 0, PI, S); plano(16, 4, mMuro, 5, 2, 0, 0, -PI / 2, S);
  // muro izquierdo con el letrero
  plano(16, 4, mMuro, -5, 2, 0, 0, PI / 2, S);
  const letrero = texCanvas(512, 128, (g) => { g.fillStyle = "rgba(0,0,0,0)"; g.clearRect(0, 0, 512, 128); g.fillStyle = "#e8eef8"; g.font = "600 46px Figtree, sans-serif";
    g.textAlign = "center"; g.fillText("A P E X   C O R P O R A T I O N", 256, 78); }, [1, 1], false);
  const let_ = plano(3.6, 0.9, new THREE.MeshBasicMaterial({ map: letrero, transparent: true }), -4.98, 2.4, -0.6, 0, PI / 2, S);
  const luzLetrero = new THREE.PointLight(0xbfd8ff, 1.2, 3, 2); luzLetrero.position.set(-4.5, 2.4, -0.6); S.add(luzLetrero);
  // ventanal del fondo: ciudad de noche
  U.ciudad = ventanaLluvia(); plano(10, 3.2, new THREE.MeshBasicMaterial({ map: U.ciudad }), 0, 1.9, -3.98, 0, 0, S);
  for (let i = -5; i <= 5; i += 1.25) caja(0.06, 3.3, 0.08, mat("#0b0f16", { liso: true, r: 0.3, m: 0.6 }), i, 1.9, -3.95, S);
  caja(10, 0.1, 0.1, mat("#0b0f16", { liso: true }), 0, 0.3, -3.95, S);
  plano(16, 16, new THREE.MeshStandardMaterial({ color: 0x0b0f16 }), 0, 3.6, 0, PI / 2, 0, S);
  // mesa larga brillante y sillas
  const mMesa = mat("#2a1a12", { liso: true, r: 0.18, m: 0.1 });
  caja(1.5, 0.07, 4.2, mMesa, 0, 0.76, 1.1, S); caja(0.12, 0.72, 3.6, mat("#0e0f12", { liso: true }), 0, 0.36, 1.1, S);
  for (let z = -0.4; z <= 2.8; z += 1.05) [-1, 1].forEach((d) => { const s = new THREE.Group(); s.position.set(d * 1.05, 0, z); s.rotation.y = -d * PI / 2; S.add(s);
    const m = mat("#0e0f12", { liso: true, r: 0.35 }); caja(0.5, 0.08, 0.5, m, 0, 0.5, 0, s); caja(0.5, 0.7, 0.08, m, 0, 0.88, -0.23, s); caja(0.06, 0.46, 0.06, m, 0, 0.25, 0, s); });
  [[-0.3, 0.3], [0.35, 1.6], [-0.2, 2.6]].forEach(([x, z]) => { caja(0.3, 0.012, 0.42, mat("#f4f1ea", { liso: true }), x, 0.8, z, S); });
  // luces: cenitales frías, contraluz y el ventanal
  const foco = (x, z, i, col) => { const l = new THREE.SpotLight(col, i, 9, 0.5, 0.6, 1.3); l.position.set(x, 3.5, z); l.target.position.set(x, 0, z); l.castShadow = true; l.shadow.mapSize.set(1024, 1024); l.shadow.bias = -0.0008; S.add(l); S.add(l.target); return l; };
  U.focoDirector = foco(0, -1.1, 75, 0xfff1dc); foco(0, 1.2, 14, 0xdfe8ff); foco(-0.9, -2.2, 16, 0xdfe8ff); foco(0.9, -2.2, 16, 0xdfe8ff);
  const contra = new THREE.DirectionalLight(0x6f9cff, 0.8); contra.position.set(0, 3, -6); contra.target.position.set(0, 1, 0); S.add(contra); S.add(contra.target);
  S.add(new THREE.HemisphereLight(0x5a6a8a, 0x1a1410, 0.5));
  S.userData = U;
  U.paso = (tt, e = {}) => { U.ciudad.userData.paso(tt, e.rayo || 0); };
  return S;
}
