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
