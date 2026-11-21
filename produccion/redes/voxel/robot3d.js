// «Chispa» v2: robot mesero moderno y elegante (no es el orbe). Flota sobre un anillo de luz naranja, cuerpo blanco perlado
// con placas grafito, hombros anchos y cintura fina, casco con visor negro brillante donde los ojos son luces LED que cambian de gesto,
// aletas laterales con franjas de neón y un núcleo encendido en el pecho.
function robot3d(cfg = {}) {
  const c = Object.assign({ blanco: "#f2f3f5", grafito: "#25282e", neon: "#ff7a2e", neon2: "#ffd08a" }, cfg);
  const raiz = new THREE.Group(), cuerpo = new THREE.Group(); raiz.add(cuerpo);
  const P = (col, r, m = 0, cc = 0) => new THREE.MeshPhysicalMaterial({ color: col, roughness: r, metalness: m, clearcoat: cc, clearcoatRoughness: 0.15 });
  const mB = P(c.blanco, 0.32, 0.05, 1), mG = P(c.grafito, 0.38, 0.6, 0.6), mN = new THREE.MeshBasicMaterial({ color: c.neon, toneMapped: false });
  const add = (geo, m, x, y, z, padre = cuerpo) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; padre.add(o); return o; };
  const resplandor = (() => { const cv = document.createElement("canvas"); cv.width = cv.height = 128; const g = cv.getContext("2d"), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, "rgba(255,170,90,1)"); gr.addColorStop(0.35, "rgba(255,122,46,.45)"); gr.addColorStop(1, "rgba(255,122,46,0)"); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(cv); })();
  const brilla = (x, y, z, s, padre = cuerpo, op = 0.8) => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: resplandor, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false })); sp.position.set(x, y, z); sp.scale.setScalar(s); padre.add(sp); return sp; };
  // base flotante: falda cónica que termina en un anillo de luz
  const falda = add(new THREE.LatheGeometry([[0.001, 0.38], [0.12, 0.36], [0.2, 0.42], [0.25, 0.55], [0.27, 0.66], [0.001, 0.66]].map(([r, h]) => new THREE.Vector2(r, h)), 48), mB, 0, 0, 0);
  const anillo = add(new THREE.TorusGeometry(0.14, 0.02, 12, 48), mN, 0, 0.36, 0); anillo.rotation.x = PI / 2;
  const halo = brilla(0, 0.3, 0, 0.9, cuerpo, 0.9);
  const haz = add(new THREE.ConeGeometry(0.22, 0.34, 32, 1, true), new THREE.MeshBasicMaterial({ color: c.neon, transparent: true, opacity: 0.07, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }), 0, 0.17, 0); haz.rotation.x = PI;
  // torso en V: hombros anchos, cintura fina; placas grafito y núcleo en el pecho
  const torso = add(new THREE.LatheGeometry([[0.001, 0.64], [0.2, 0.64], [0.19, 0.74], [0.24, 0.92], [0.33, 1.1], [0.34, 1.2], [0.26, 1.3], [0.12, 1.34], [0.001, 1.35]].map(([r, h]) => new THREE.Vector2(r, h)), 56), mB, 0, 0, 0);
  torso.scale.z = 0.72;
  // (placa de pecho retirada: se veía como una franja)
  const nucleo = add(new THREE.TorusGeometry(0.055, 0.014, 12, 40), mN, 0, 1.06, 0.245); const nucleoIn = add(new THREE.CircleGeometry(0.04, 32), new THREE.MeshBasicMaterial({ color: c.neon2, toneMapped: false }), 0, 1.06, 0.244);
  brilla(0, 1.06, 0.27, 0.28);
  add(new THREE.TorusGeometry(0.205, 0.012, 10, 48), mG, 0, 0.66, 0).rotation.x = PI / 2;
  // hombros, brazos segmentados con franja de neón y manos de tres dedos
  const brazos = [-1, 1].map((d) => { const p = new THREE.Group(); p.position.set(d * 0.37, 1.18, 0); cuerpo.add(p);
    const hombro = add(new THREE.SphereGeometry(0.095, 28, 20), mB, 0, 0, 0, p); add(new THREE.SphereGeometry(0.1, 28, 14, 0, 2 * PI, 0, PI * 0.45), mG, 0, 0.01, 0, p);
    add(new THREE.CapsuleGeometry(0.052, 0.2, 8, 20), mB, 0, -0.18, 0, p); const codo = new THREE.Group(); codo.position.set(0, -0.32, 0); p.add(codo);
    add(new THREE.SphereGeometry(0.05, 20, 14), mG, 0, 0, 0, codo); add(new THREE.CapsuleGeometry(0.048, 0.18, 8, 20), mG, 0, -0.14, 0, codo);
    add(new THREE.BoxGeometry(0.012, 0.16, 0.05), mN, d * 0.046, -0.14, 0, codo);
    const mano = new THREE.Group(); mano.position.set(0, -0.28, 0); codo.add(mano); add(new THREE.SphereGeometry(0.055, 20, 14), mB, 0, 0, 0, mano).scale.set(1, 0.8, 0.7);
    [-1, 0, 1].forEach((k) => add(new THREE.CapsuleGeometry(0.013, 0.05, 4, 10), mG, k * 0.022, -0.06, 0.01, mano)); add(new THREE.CapsuleGeometry(0.014, 0.04, 4, 10), mG, -d * 0.05, -0.02, 0.02, mano).rotation.z = d * 0.8;
    return { p, codo, mano }; });
  // cuello y casco con visor negro brillante y ojos LED
  add(new THREE.CylinderGeometry(0.06, 0.08, 0.1, 24), mG, 0, 1.38, 0);
  const cabeza = new THREE.Group(); cabeza.position.set(0, 1.58, 0); cuerpo.add(cabeza);
  const casco = add(new THREE.SphereGeometry(0.2, 48, 32), mB, 0, 0, 0, cabeza); casco.scale.set(1.12, 0.92, 1.0);
  const cv = document.createElement("canvas"); cv.width = 512; cv.height = 256; const gx = cv.getContext("2d"), texV = new THREE.CanvasTexture(cv); texV.colorSpace = THREE.SRGBColorSpace;
  const visor = add(new THREE.SphereGeometry(0.205, 48, 24, PI * 0.18, PI * 0.64, PI * 0.33, PI * 0.36), new THREE.MeshPhysicalMaterial({ map: texV, emissiveMap: texV, emissive: 0xffffff, emissiveIntensity: 1.1, color: 0x050608, roughness: 0.08, clearcoat: 1 }), 0, 0, 0, cabeza);
  visor.scale.set(1.13, 0.93, 1.02);
  [-1, 1].forEach((d) => { const aleta = add(new THREE.BoxGeometry(0.035, 0.2, 0.12), mG, d * 0.23, 0.02, -0.02, cabeza); aleta.rotation.z = -d * 0.18;
    add(new THREE.BoxGeometry(0.012, 0.16, 0.02), mN, d * 0.25, 0.02, 0.03, cabeza).rotation.z = -d * 0.18; });
  add(new THREE.CapsuleGeometry(0.012, 0.09, 4, 8), mG, 0.07, 0.22, -0.02, cabeza).rotation.z = -0.35; const punta = add(new THREE.SphereGeometry(0.022, 14, 10), mN, 0.095, 0.28, -0.02, cabeza);
  brilla(0.095, 0.28, -0.02, 0.14, cabeza);
  // ojos LED: dibujados en el visor; gestos: «feliz», «guiño», «enfoca», «hablando»
  function ojos(t, gesto, voz) {
    gx.fillStyle = "#030406"; gx.fillRect(0, 0, 512, 256); gx.save(); gx.shadowColor = c.neon; gx.shadowBlur = 26; gx.fillStyle = c.neon2; gx.strokeStyle = c.neon2; gx.lineWidth = 22; gx.lineCap = "round";
    const parp = (t % 3.6) < 0.12;
    [[180, -1], [332, 1]].forEach(([x, d]) => {
      if (parp) { gx.beginPath(); gx.moveTo(x - 36, 128); gx.lineTo(x + 36, 128); gx.stroke(); return; }
      if (gesto === "feliz" || (gesto === "guiño" && d > 0)) { gx.beginPath(); gx.arc(x, 145, 38, PI * 1.15, PI * 1.85); gx.stroke(); return; }
      const h = gesto === "enfoca" ? 36 : 64; gx.beginPath(); gx.roundRect(x - 30, 128 - h / 2, 60, h, 26); gx.fill();
      gx.fillStyle = "rgba(255,255,255,.85)"; gx.beginPath(); gx.arc(x + 12, 128 - h / 4, 8, 0, 2 * PI); gx.fill(); gx.fillStyle = c.neon2; });
    if (voz > 0.05) { gx.lineWidth = 8; gx.beginPath(); for (let i = 0; i <= 20; i++) { const xx = 196 + i * 6; gx.lineTo(xx, 205 + Math.sin(i * 1.3 + t * 18) * 14 * voz); } gx.stroke(); }
    gx.restore(); texV.needsUpdate = true;
  }
  function animar(t, s = {}) {
    cuerpo.position.y = 0.05 + Math.sin(t * 1.6) * 0.025; cuerpo.rotation.z = Math.sin(t * 0.9) * 0.02;
    cabeza.rotation.set(Math.sin(t * 0.8) * 0.04 + (s.cabeceo || 0), s.mira ?? Math.sin(t * 0.5) * 0.18, s.ladea ?? 0.08);
    brazos[0].p.rotation.set(-0.15, 0, -0.16); brazos[0].codo.rotation.x = -0.35;
    if (s.saluda) { brazos[1].p.rotation.set(-0.3, 0, 2.5); brazos[1].codo.rotation.set(0, 0, 0.4 + Math.sin(t * 7) * 0.35); }
    else { brazos[1].p.rotation.set(-0.15, 0, 0.16); brazos[1].codo.rotation.x = -0.35; }
    const pulso = 0.75 + 0.25 * Math.sin(t * 4); halo.material.opacity = 0.7 * pulso; anillo.scale.setScalar(1 + 0.05 * Math.sin(t * 4)); nucleoIn.material.color.setHSL(0.07, 1, 0.55 + 0.15 * pulso);
    punta.scale.setScalar(0.8 + 0.4 * Math.abs(Math.sin(t * 3))); ojos(t, s.gesto || "normal", s.voz || 0);
  }
  return { raiz, animar };
}

// ═══════════ «Play»: variantes de diseño (bocetos B, C y D). robot3d() es la variante A (clásico flotante). ═══════════
const PLAY = {};
PLAY.P = (col, r, m = 0, cc = 0) => new THREE.MeshPhysicalMaterial({ color: col, roughness: r, metalness: m, clearcoat: cc, clearcoatRoughness: 0.15 });
PLAY.brillo = (() => { let t = null; return () => { if (t) return t; const cv = document.createElement("canvas"); cv.width = cv.height = 128; const g = cv.getContext("2d"), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.35, "rgba(255,255,255,.4)"); gr.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return (t = new THREE.CanvasTexture(cv)); }; })();
// cara de pantalla con ojos LED (gestos: normal, feliz, guiño, enfoca) y onda al hablar
PLAY.cara = (ancho, alto, col) => { const cv = document.createElement("canvas"); cv.width = 512; cv.height = Math.round(512 * alto / ancho); const g = cv.getContext("2d"), tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const dibujar = (t, gesto = "normal", voz = 0) => { const W = cv.width, H = cv.height, cy = H * 0.46; g.fillStyle = "#040507"; g.fillRect(0, 0, W, H);
    g.save(); g.shadowColor = col; g.shadowBlur = 28; g.fillStyle = col; g.strokeStyle = col; g.lineWidth = H * 0.085; g.lineCap = "round"; const parp = (t % 3.4) < 0.12;
    [[W * 0.33, -1], [W * 0.67, 1]].forEach(([x, d]) => { const r = H * 0.16;
      if (parp) { g.beginPath(); g.moveTo(x - r, cy); g.lineTo(x + r, cy); g.stroke(); return; }
      if (gesto === "feliz" || (gesto === "guiño" && d > 0)) { g.beginPath(); g.arc(x, cy + r * 0.45, r, PI * 1.15, PI * 1.85); g.stroke(); return; }
      const h = gesto === "enfoca" ? r * 1.0 : r * 1.9; g.beginPath(); g.roundRect(x - r * 0.75, cy - h / 2, r * 1.5, h, r * 0.7); g.fill();
      g.fillStyle = "rgba(255,255,255,.85)"; g.beginPath(); g.arc(x + r * 0.28, cy - h * 0.22, r * 0.22, 0, 2 * PI); g.fill(); g.fillStyle = col; });
    if (voz > 0.05) { g.lineWidth = H * 0.03; g.beginPath(); for (let i = 0; i <= 20; i++) g.lineTo(W * 0.4 + i * W * 0.01, H * 0.8 + Math.sin(i * 1.3 + t * 18) * H * 0.05 * voz); g.stroke(); }
    else { g.lineWidth = H * 0.03; g.beginPath(); g.arc(W / 2, H * 0.72, H * 0.09, PI * 0.15, PI * 0.85); g.stroke(); }
    g.restore(); tex.needsUpdate = true; };
  return { tex, dibujar }; };
PLAY.malla = (padre, geo, m, x = 0, y = 0, z = 0) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; padre.add(o); return o; };

// B · «Compacto»: cápsula menta y blanca, visor ancho, manos flotantes (sin brazos) y una antena-hoja
function robotPlayB() {
  const raiz = new THREE.Group(), cuerpo = new THREE.Group(); raiz.add(cuerpo); const P = PLAY.P, A = PLAY.malla;
  const mBl = P("#f6f7f8", 0.3, 0, 1), mMe = P("#5fd3b5", 0.35, 0.05, 1), mOs = P("#20262d", 0.4, 0.4, 0.5);
  const cap = A(cuerpo, new THREE.CapsuleGeometry(0.33, 0.42, 16, 48), mBl, 0, 0.98, 0); cap.scale.set(1, 1, 0.9);
  const banda = A(cuerpo, new THREE.CylinderGeometry(0.335, 0.335, 0.2, 48, 1, true), mMe, 0, 0.72, 0); banda.scale.z = 0.9;
  const cara = PLAY.cara(1.4, 1.0, "#7ff0d2"); const visor = A(cuerpo, new THREE.CylinderGeometry(0.338, 0.338, 0.34, 48, 1, true, -PI * 0.32, PI * 0.64), new THREE.MeshPhysicalMaterial({ map: cara.tex, emissiveMap: cara.tex, emissive: 0xffffff, emissiveIntensity: 1, color: 0x050608, roughness: 0.06, clearcoat: 1 }), 0, 1.03, 0); visor.scale.z = 0.905;
  const hoja = new THREE.Group(); hoja.position.set(0, 1.62, 0); cuerpo.add(hoja); A(hoja, new THREE.CylinderGeometry(0.01, 0.012, 0.16, 8), mOs, 0, 0.08, 0);
  const lam = A(hoja, new THREE.SphereGeometry(0.07, 24, 12), mMe, 0.05, 0.18, 0); lam.scale.set(1, 0.35, 0.6); lam.rotation.z = -0.5;
  const manos = [-1, 1].map((d) => { const m = new THREE.Group(); cuerpo.add(m); A(m, new THREE.SphereGeometry(0.075, 24, 16), mMe, 0, 0, 0).scale.set(1, 0.85, 0.7);
    [-1, 0, 1].forEach((k) => A(m, new THREE.CapsuleGeometry(0.018, 0.04, 4, 10), mMe, k * 0.03, -0.07, 0.01)); return m; });
  const base = A(cuerpo, new THREE.TorusGeometry(0.16, 0.025, 12, 40), new THREE.MeshBasicMaterial({ color: 0x7ff0d2, toneMapped: false }), 0, 0.42, 0); base.rotation.x = PI / 2;
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: PLAY.brillo(), color: 0x7ff0d2, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending, depthWrite: false })); halo.position.set(0, 0.36, 0); halo.scale.setScalar(0.9); cuerpo.add(halo);
  function animar(t, s = {}) { cuerpo.position.y = 0.04 + Math.sin(t * 1.8) * 0.03; hoja.rotation.z = Math.sin(t * 2.2) * 0.2;
    manos[0].position.set(-0.5, 0.95 + Math.sin(t * 2) * 0.03, 0.12); manos[1].position.set(0.5, s.saluda ? 1.45 + Math.sin(t * 8) * 0.03 : 0.95 + Math.sin(t * 2 + 1) * 0.03, 0.12); manos[1].rotation.z = s.saluda ? Math.sin(t * 8) * 0.4 : 0;
    cara.dibujar(t, s.gesto, s.voz || 0); }
  return { raiz, animar };
}

// C · «Retro-moderno»: cabeza de pantalla cuadrada redondeada (cara de emoji), cuerpo rojo y crema, orugas pequeñas y brazo-bandeja
function robotPlayC() {
  const raiz = new THREE.Group(), cuerpo = new THREE.Group(); raiz.add(cuerpo); const P = PLAY.P, A = PLAY.malla;
  const mR = P("#d9443a", 0.32, 0.05, 1), mCr = P("#f1e7d4", 0.35, 0, 0.8), mOs = P("#2a2c31", 0.45, 0.5, 0.4), mOr = P("#c9a24a", 0.25, 0.9, 0.6);
  [-1, 1].forEach((d) => { const o = A(cuerpo, new THREE.CapsuleGeometry(0.08, 0.26, 8, 20), mOs, d * 0.18, 0.1, 0); o.rotation.x = PI / 2; });
  const tor = A(cuerpo, new THREE.CylinderGeometry(0.3, 0.26, 0.62, 40), mR, 0, 0.55, 0); tor.scale.z = 0.8;
  A(cuerpo, new THREE.CylinderGeometry(0.305, 0.305, 0.06, 40), mOr, 0, 0.84, 0).scale.z = 0.8;
  const pecho = A(cuerpo, new THREE.CylinderGeometry(0.12, 0.12, 0.02, 32), mCr, 0, 0.6, 0.24); pecho.rotation.x = PI / 2;
  [0.62, 0.56, 0.5].forEach((y, i) => A(cuerpo, new THREE.SphereGeometry(0.018, 12, 8), [mOr, mOs, mOr][i], -0.03 + i * 0.03, y + 0.02, 0.255));
  A(cuerpo, new THREE.CylinderGeometry(0.06, 0.08, 0.1, 20), mOs, 0, 0.92, 0);
  const cabeza = new THREE.Group(); cabeza.position.set(0, 1.18, 0); cuerpo.add(cabeza);
  const caja = A(cabeza, new THREE.BoxGeometry(0.5, 0.38, 0.34), mCr, 0, 0, 0); [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([a, b]) => A(cabeza, new THREE.CylinderGeometry(0.06, 0.06, 0.34, 16), mCr, a * 0.22, b * 0.16, 0).rotation.x = PI / 2);
  const cara = PLAY.cara(0.42, 0.3, "#ffd27a"); A(cabeza, new THREE.PlaneGeometry(0.42, 0.3), new THREE.MeshBasicMaterial({ map: cara.tex, toneMapped: false }), 0, 0, 0.172);
  A(cabeza, new THREE.TorusGeometry(0.23, 0.012, 8, 4), mOr, 0, 0, 0.17).rotation.z = PI / 4;
  [-1, 1].forEach((d) => A(cabeza, new THREE.CylinderGeometry(0.05, 0.05, 0.05, 20), mR, d * 0.28, 0, 0).rotation.z = PI / 2);
  const ant = A(cabeza, new THREE.CylinderGeometry(0.008, 0.008, 0.16, 8), mOs, 0.12, 0.27, 0); const bola = A(cabeza, new THREE.SphereGeometry(0.03, 14, 10), new THREE.MeshBasicMaterial({ color: 0xffd27a, toneMapped: false }), 0.12, 0.36, 0);
  const brazos = [-1, 1].map((d) => { const p = new THREE.Group(); p.position.set(d * 0.33, 0.78, 0); cuerpo.add(p); A(p, new THREE.SphereGeometry(0.06, 20, 14), mOr);
    A(p, new THREE.CapsuleGeometry(0.035, 0.32, 6, 14), mCr, 0, -0.2, 0); const m = A(p, new THREE.SphereGeometry(0.055, 18, 12), mR, 0, -0.42, 0); return p; });
  function animar(t, s = {}) { cuerpo.position.y = Math.abs(Math.sin(t * 3)) * 0.01; cabeza.rotation.set(Math.sin(t * 0.8) * 0.05, s.mira ?? Math.sin(t * 0.5) * 0.15, s.ladea ?? 0.08);
    brazos[0].rotation.z = -0.2; brazos[1].rotation.set(s.saluda ? 0 : -0.3, 0, s.saluda ? 2.4 + Math.sin(t * 7) * 0.3 : 0.2); bola.scale.setScalar(0.8 + 0.4 * Math.abs(Math.sin(t * 3))); cara.dibujar(t, s.gesto, s.voz || 0); }
  return { raiz, animar };
}

// D · «Elegante»: alto y esbelto, colores de esmoquin (negro y blanco), corbatín dorado, cara ovalada negra brillante con ojos LED dorados
function robotPlayD() {
  const raiz = new THREE.Group(), cuerpo = new THREE.Group(); raiz.add(cuerpo); const P = PLAY.P, A = PLAY.malla;
  const mN = P("#16181c", 0.3, 0.3, 1), mBl = P("#f4f4f2", 0.32, 0, 1), mOr = P("#d4af37", 0.22, 0.95, 0.8);
  const falda = A(cuerpo, new THREE.LatheGeometry([[0.001, 0.32], [0.1, 0.3], [0.2, 0.42], [0.22, 0.6], [0.001, 0.6]].map(([r, h]) => new THREE.Vector2(r, h)), 40), mN);
  const anillo = A(cuerpo, new THREE.TorusGeometry(0.11, 0.016, 10, 40), new THREE.MeshBasicMaterial({ color: 0xffd76a, toneMapped: false }), 0, 0.3, 0); anillo.rotation.x = PI / 2;
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: PLAY.brillo(), color: 0xffd76a, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending, depthWrite: false })); halo.position.set(0, 0.26, 0); halo.scale.setScalar(0.7); cuerpo.add(halo);
  const tor = A(cuerpo, new THREE.LatheGeometry([[0.001, 0.58], [0.17, 0.58], [0.2, 0.75], [0.27, 1.0], [0.29, 1.12], [0.2, 1.22], [0.08, 1.26], [0.001, 1.27]].map(([r, h]) => new THREE.Vector2(r, h)), 48), mN); tor.scale.z = 0.7;
  const camisa = A(cuerpo, new THREE.LatheGeometry([[0.12, 0.8], [0.2, 1.0], [0.22, 1.14], [0.12, 1.22]].map(([r, h]) => new THREE.Vector2(r + 0.012, h)), 30, -PI * 0.16, PI * 0.32), mBl); camisa.scale.z = 0.7;
  [-1, 1].forEach((d) => A(cuerpo, new THREE.SphereGeometry(0.045, 16, 12), mOr, d * 0.045, 1.17, 0.17).scale.set(1.3, 0.8, 0.6)); A(cuerpo, new THREE.SphereGeometry(0.022, 12, 8), mOr, 0, 1.17, 0.185);
  [1.04, 0.94].forEach((y) => A(cuerpo, new THREE.SphereGeometry(0.014, 10, 8), mOr, 0, y, 0.2));
  A(cuerpo, new THREE.CylinderGeometry(0.045, 0.06, 0.1, 20), mN, 0, 1.3, 0);
  const cabeza = new THREE.Group(); cabeza.position.set(0, 1.5, 0); cuerpo.add(cabeza);
  A(cabeza, new THREE.SphereGeometry(0.17, 40, 28), mBl).scale.set(0.95, 1.18, 0.95);
  const cara = PLAY.cara(1.0, 1.0, "#ffd76a"); const vis = A(cabeza, new THREE.SphereGeometry(0.172, 40, 24, PI * 0.22, PI * 0.56, PI * 0.25, PI * 0.42), new THREE.MeshPhysicalMaterial({ map: cara.tex, emissiveMap: cara.tex, emissive: 0xffffff, emissiveIntensity: 1, color: 0x050608, roughness: 0.06, clearcoat: 1 })); vis.scale.set(0.96, 1.19, 0.96);
  [-1, 1].forEach((d) => A(cabeza, new THREE.CylinderGeometry(0.03, 0.03, 0.03, 16), mOr, d * 0.165, 0, 0).rotation.z = PI / 2);
  const brazos = [-1, 1].map((d) => { const p = new THREE.Group(); p.position.set(d * 0.31, 1.1, 0); cuerpo.add(p); A(p, new THREE.SphereGeometry(0.065, 20, 14), mN);
    A(p, new THREE.CapsuleGeometry(0.038, 0.24, 6, 14), mN, 0, -0.18, 0); const c = new THREE.Group(); c.position.set(0, -0.34, 0); p.add(c); A(c, new THREE.CapsuleGeometry(0.034, 0.2, 6, 14), mN, 0, -0.13, 0);
    A(c, new THREE.CylinderGeometry(0.042, 0.042, 0.03, 16), mBl, 0, -0.25, 0); A(c, new THREE.SphereGeometry(0.048, 18, 12), mBl, 0, -0.3, 0).scale.set(1, 0.85, 0.7); return { p, c }; });
  function animar(t, s = {}) { cuerpo.position.y = 0.05 + Math.sin(t * 1.5) * 0.02; cabeza.rotation.set(Math.sin(t * 0.7) * 0.03, s.mira ?? Math.sin(t * 0.45) * 0.15, s.ladea ?? 0.06);
    brazos[0].p.rotation.set(-0.1, 0, -0.1); brazos[0].c.rotation.x = -0.25; if (s.saluda) { brazos[1].p.rotation.set(-0.3, 0, 2.3); brazos[1].c.rotation.z = 0.4 + Math.sin(t * 7) * 0.3; } else { brazos[1].p.rotation.set(-0.6, 0, 0.1); brazos[1].c.rotation.x = -1.2; }
    halo.material.opacity = 0.55 + 0.2 * Math.sin(t * 4); cara.dibujar(t, s.gesto, s.voz || 0); }
  return { raiz, animar };
}

// E · «Caja arcade»: caja con bordes redondeados, pantalla con ojos de píxeles de colores distintos, bordes de neón,
// palanca de juego en la cabeza, brazos cortos y pies redondos. Inspiración arcade de los 80 (sin copiar personajes).
function robotPlayCaja(cfg = {}) {
  const c = Object.assign({ cuerpo: "#1b2440", borde: "#36e0ff", ojoI: "#36e0ff", ojoD: "#ff4fd8", bola: "#ff3b3b" }, cfg);
  const raiz = new THREE.Group(), cuerpo = new THREE.Group(); raiz.add(cuerpo); const P = PLAY.P, A = PLAY.malla;
  const mC = P(c.cuerpo, 0.3, 0.1, 1), mO = P("#1a1c22", 0.4, 0.4, 0.6), mNe = new THREE.MeshBasicMaterial({ color: c.borde, toneMapped: false });
  // caja redondeada (extrusión con bisel)
  const L = 0.62, R = 0.09, f = new THREE.Shape(); f.moveTo(-L / 2 + R, -L / 2); f.lineTo(L / 2 - R, -L / 2); f.quadraticCurveTo(L / 2, -L / 2, L / 2, -L / 2 + R); f.lineTo(L / 2, L / 2 - R);
  f.quadraticCurveTo(L / 2, L / 2, L / 2 - R, L / 2); f.lineTo(-L / 2 + R, L / 2); f.quadraticCurveTo(-L / 2, L / 2, -L / 2, L / 2 - R); f.lineTo(-L / 2, -L / 2 + R); f.quadraticCurveTo(-L / 2, -L / 2, -L / 2 + R, -L / 2);
  const geo = new THREE.ExtrudeGeometry(f, { depth: 0.46, bevelEnabled: true, bevelSize: 0.05, bevelThickness: 0.05, bevelSegments: 8, curveSegments: 12 }); geo.translate(0, 0, -0.23);
  const caja = A(cuerpo, geo, mC, 0, 0.78, 0);
  // pantalla con ojos de píxeles (cada ojo de un color) y boca de píxeles
  const cv = document.createElement("canvas"); cv.width = cv.height = 256; const g = cv.getContext("2d"), tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  A(cuerpo, new THREE.PlaneGeometry(0.5, 0.5), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }), 0, 0.8, 0.282);
  [[0, 0.255, 0.52, 0.018], [0, -0.255, 0.52, 0.018], [0.255, 0, 0.018, 0.52], [-0.255, 0, 0.018, 0.52]].forEach(([x, y, w, h]) => A(cuerpo, new THREE.BoxGeometry(w, h, 0.012), mNe, x, 0.8 + y, 0.284));
  const luzI = new THREE.PointLight(c.ojoI, 0.6, 1.0, 2); luzI.position.set(-0.12, 0.85, 0.4); cuerpo.add(luzI); const luzD = new THREE.PointLight(c.ojoD, 0.6, 1.0, 2); luzD.position.set(0.12, 0.85, 0.4); cuerpo.add(luzD);
  function pantalla(t, gesto, voz) {
    g.fillStyle = "#05060a"; g.fillRect(0, 0, 256, 256); g.fillStyle = "rgba(255,255,255,.03)"; for (let y = 0; y < 256; y += 6) g.fillRect(0, y, 256, 2);
    const pix = 16, parp = (t % 3.2) < 0.12, ojo = (cx, col, d) => { g.save(); g.shadowColor = col; g.shadowBlur = 18; g.fillStyle = col;
      if (parp) { g.fillRect(cx - 32, 100, 64, pix); g.restore(); return; }
      if (gesto === "feliz" || (gesto === "guiño" && d > 0)) { [[-32, 104], [-16, 88], [0, 80], [16, 88], [32, 104]].forEach(([dx, y]) => g.fillRect(cx + dx - 8, y, pix, pix)); g.restore(); return; }
      const h = gesto === "enfoca" ? 32 : 64; g.fillRect(cx - 24, 108 - h / 2, 48, h); g.fillStyle = "rgba(255,255,255,.9)"; g.fillRect(cx + 4, 108 - h / 2 + 6, 12, 12); g.restore(); };
    ojo(80, c.ojoI, -1); ojo(176, c.ojoD, 1);
    g.save(); g.fillStyle = "#e8f6ff"; g.shadowColor = "#e8f6ff"; g.shadowBlur = 10; const ab = voz > 0.05 ? Math.round(1 + 2 * Math.abs(Math.sin(t * 16)) * voz) : 0;
    if (ab) { g.fillRect(104, 180, 48, pix * ab); } else { [[96, 176], [112, 184], [128, 184], [144, 176]].forEach(([x, y]) => g.fillRect(x, y, pix, 8)); } g.restore();
    tex.needsUpdate = true; }
  // detalles arcade: ranura de moneda y botones a un lado; palanca de juego encima
  A(cuerpo, new THREE.BoxGeometry(0.012, 0.09, 0.03), mNe, 0.36, 0.7, 0.1); [[0.1, "#ff3b3b"], [0.0, "#ffd23b"], [-0.1, "#3bff8a"]].forEach(([z, col]) => A(cuerpo, new THREE.CylinderGeometry(0.025, 0.025, 0.02, 16), new THREE.MeshBasicMaterial({ color: col, toneMapped: false }), 0.365, 0.88, z).rotation.z = PI / 2);
  A(cuerpo, new THREE.CylinderGeometry(0.06, 0.07, 0.03, 24), mO, 0.08, 1.15, -0.05); const palo = A(cuerpo, new THREE.CylinderGeometry(0.012, 0.012, 0.16, 10), mO, 0.08, 1.24, -0.05);
  const bola = A(cuerpo, new THREE.SphereGeometry(0.045, 20, 14), P(c.bola, 0.2, 0, 1), 0.08, 1.33, -0.05);
  // brazos cortos y manos redondas; piernas cortas con pies
  const brazos = [-1, 1].map((d) => { const p = new THREE.Group(); p.position.set(d * 0.42, 0.74, 0.02); cuerpo.add(p); A(p, new THREE.SphereGeometry(0.05, 16, 12), mO);
    A(p, new THREE.CapsuleGeometry(0.038, 0.1, 6, 12), mO, 0, -0.08, 0); A(p, new THREE.SphereGeometry(0.068, 18, 14), P("#f2f2f2", 0.3, 0, 1), 0, -0.19, 0); return p; });
  [-1, 1].forEach((d) => { A(cuerpo, new THREE.CapsuleGeometry(0.04, 0.08, 6, 12), mO, d * 0.15, 0.36, 0); A(cuerpo, new THREE.SphereGeometry(0.08, 20, 14), P("#f2f2f2", 0.3, 0, 1), d * 0.15, 0.27, 0.04).scale.set(1, 0.55, 1.3); });
  function animar(t, s = {}) { const salto = Math.abs(Math.sin(t * 3)) * 0.02; cuerpo.position.y = salto; cuerpo.rotation.z = Math.sin(t * 1.5) * 0.03;
    brazos[0].rotation.set(0, 0, -0.55 + Math.sin(t * 3) * 0.1); brazos[1].rotation.set(0, 0, s.saluda ? 2.5 + Math.sin(t * 8) * 0.35 : 0.55 - Math.sin(t * 3) * 0.1);
    palo.rotation.z = Math.sin(t * 2.4) * 0.25; bola.position.x = 0.08 - Math.sin(t * 2.4) * 0.04; luzI.intensity = luzD.intensity = 0.5 + (s.voz || 0) * 0.6; pantalla(t, s.gesto || "normal", s.voz || 0); }
  return { raiz, animar };
}

// F · «Orbe adorable»: Play pequeño (≈ 0,9 m). Cuerpo de esfera brillante, visor negro con dos ojos grandes de colores distintos,
// brazos y piernas de tubo redondo que se doblan (estilo manguera), manos y pies redondos, antena corta con bolita.
function robotPlayOrbe(cfg = {}) {
  const c = Object.assign({ cuerpo: "#f4f5f7", acento: "#9fb4c8", ojoI: "#36e0ff", ojoD: "#ff5fd2", mejillas: "#ff8fb3" }, cfg);
  const raiz = new THREE.Group(), cuerpo = new THREE.Group(); raiz.add(cuerpo); const P = PLAY.P, A = PLAY.malla;
  const mC = P(c.cuerpo, 0.25, 0.02, 1), mA = P(c.acento, 0.3, 0.1, 1);
  const Y = 0.58, R = 0.27;                                            // centro y radio del orbe
  A(cuerpo, new THREE.SphereGeometry(R, 64, 48), mC, 0, Y, 0);
  const yb = 0.2, aro = A(cuerpo, new THREE.TorusGeometry(Math.sqrt(R * R - yb * yb) + 0.004, 0.013, 12, 64), mA, 0, Y - yb, 0); aro.rotation.x = PI / 2;
  // visor y cara
  const cv = document.createElement("canvas"); cv.width = 512; cv.height = 512; const g = cv.getContext("2d"), tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const capa = new THREE.SphereGeometry(R * 1.006, 56, 28, 0, 2 * PI, 0, PI * 0.26); capa.rotateX(PI / 2);
  { const pz = capa.attributes.position, uv = capa.attributes.uv, k = R * 1.006 * Math.sin(PI * 0.26); for (let i = 0; i < pz.count; i++) uv.setXY(i, pz.getX(i) / (2 * k) + 0.5, pz.getY(i) / (2 * k) + 0.5); uv.needsUpdate = true; }
  const caraG = new THREE.Group(); caraG.position.set(0, Y, 0); caraG.rotation.x = -0.14; cuerpo.add(caraG);
  const visor = A(caraG, capa, new THREE.MeshPhysicalMaterial({ map: tex, emissiveMap: tex, emissive: 0xffffff, emissiveIntensity: 1.05, color: 0x050608, roughness: 0.05, clearcoat: 1 }), 0, 0, 0);
  const borde = A(caraG, new THREE.TorusGeometry(R * 1.006 * Math.sin(PI * 0.26), 0.012, 10, 56), mA, 0, 0, R * 1.006 * Math.cos(PI * 0.26));
  function cara(t, gesto, voz) {
    g.fillStyle = "#040507"; g.fillRect(0, 0, 512, 512); const parp = (t % 3.3) < 0.12, cy = 230;
    [[180, c.ojoI, -1], [332, c.ojoD, 1]].forEach(([x, col, d]) => { g.save(); g.shadowColor = col; g.shadowBlur = 30; g.fillStyle = col; g.strokeStyle = col; g.lineWidth = 22; g.lineCap = "round";
      if (parp) { g.beginPath(); g.moveTo(x - 38, cy); g.lineTo(x + 38, cy); g.stroke(); }
      else if (gesto === "feliz" || (gesto === "guiño" && d > 0)) { g.beginPath(); g.arc(x, cy + 22, 40, PI * 1.12, PI * 1.88); g.stroke(); }
      else { const ry = gesto === "enfoca" ? 26 : 52; g.beginPath(); g.ellipse(x, cy, 42, ry, 0, 0, 2 * PI); g.fill();
        g.shadowBlur = 0; g.fillStyle = "rgba(255,255,255,.95)"; g.beginPath(); g.arc(x + 14, cy - ry * 0.35, 13, 0, 2 * PI); g.fill(); g.beginPath(); g.arc(x - 12, cy + ry * 0.3, 6, 0, 2 * PI); g.fill(); }
      g.restore(); });
    g.save(); g.fillStyle = c.mejillas; g.globalAlpha = 0.55; g.shadowColor = c.mejillas; g.shadowBlur = 20; [[118, 318], [394, 318]].forEach(([x, y]) => { g.beginPath(); g.ellipse(x, y, 30, 14, 0, 0, 2 * PI); g.fill(); }); g.restore();
    g.save(); g.strokeStyle = "#e9f6ff"; g.fillStyle = "#e9f6ff"; g.shadowColor = "#e9f6ff"; g.shadowBlur = 12; g.lineWidth = 12; g.lineCap = "round";
    if (voz > 0.05) { g.beginPath(); g.ellipse(256, 336, 26, 8 + 18 * voz * Math.abs(Math.sin(t * 15)), 0, 0, 2 * PI); g.fill(); } else { g.beginPath(); g.arc(256, 314, 28, PI * 0.2, PI * 0.8); g.stroke(); }
    g.restore(); tex.needsUpdate = true; }
  // antena corta con bolita
  A(cuerpo, new THREE.CylinderGeometry(0.008, 0.01, 0.09, 8), mA, 0.05, Y + R + 0.03, 0).rotation.z = -0.25; const bola = A(cuerpo, new THREE.SphereGeometry(0.025, 16, 12), new THREE.MeshBasicMaterial({ color: c.ojoD, toneMapped: false }), 0.075, Y + R + 0.085, 0);
  // brazos y piernas de tubo que se doblan: se reconstruyen cada cuadro sobre una curva suave
  const mT = P(c.acento, 0.3, 0.15, 1), mM = P(c.cuerpo, 0.25, 0.02, 1);
  const tubos = [0, 1, 2, 3].map(() => { const m = new THREE.Mesh(new THREE.BufferGeometry(), mT); m.castShadow = true; cuerpo.add(m); return m; });
  const manos = [-1, 1].map(() => A(cuerpo, new THREE.SphereGeometry(0.05, 20, 14), mM)), pies = [-1, 1].map(() => { const p = A(cuerpo, new THREE.SphereGeometry(0.062, 20, 14), mM); p.scale.set(1, 0.6, 1.35); return p; });
  const tubo = (m, pts, r) => { m.geometry.dispose(); m.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map((p) => new THREE.Vector3(...p))), 20, r, 10, false); };
  function animar(t, s = {}) {
    const rebote = Math.abs(Math.sin(t * 3.2)) * 0.025; cuerpo.position.y = rebote; cuerpo.rotation.z = Math.sin(t * 1.6) * 0.04;
    [-1, 1].forEach((d, i) => {   // brazos: salen de los lados del orbe y se curvan como manguera
      const saluda = s.saluda && d > 0, ox = d * R * 0.95, oy = Y - 0.02;
      const fin = saluda ? [d * 0.42, Y + 0.3 + Math.sin(t * 8) * 0.03, 0.05] : [d * 0.36, Y - 0.22 + Math.sin(t * 2.4 + i) * 0.02, 0.06];
      const med = saluda ? [d * 0.42, Y + 0.05, 0.02] : [d * 0.38, Y - 0.08, 0.02];
      tubo(tubos[i], [[ox, oy, 0], med, fin], 0.022); manos[i].position.set(...fin);
      const paso = Math.sin(t * 3.2 + i * PI) * 0.03, cad = [d * 0.11, Y - R * 0.9, 0], pie = [d * 0.13, 0.04, 0.03 + paso];   // piernas cortas
      tubo(tubos[2 + i], [cad, [d * 0.14, (cad[1] + pie[1]) / 2, 0.01 + paso * 0.5], pie], 0.025); pies[i].position.set(pie[0], pie[1], pie[2] + 0.02);
    });
    bola.scale.setScalar(0.85 + 0.3 * Math.abs(Math.sin(t * 3))); cara(t, s.gesto || "normal", s.voz || 0);
  }
  return { raiz, animar };
}
