// «Chispa»: robot mesero retro, raro y único (no es el orbe). Cuerpo de huevo esmaltado crema con bandas de cobre,
// una sola rueda, cuello de fuelle que se estira, cabeza de tambor con un ojo-lente enorme y otro diminuto, dos antenas desparejas,
// una oreja-antena parabólica, brazos largos de tres dedos y una ventanilla en la barriga con engranajes que brillan.
function robot3d(cfg = {}) {
  const c = Object.assign({ esmalte: "#efe4cf", cobre: "#c8743a", acento: "#2bb3a8", ojo: "#ffb347" }, cfg);
  const raiz = new THREE.Group(), M = (col, r = 0.4, m = 0) => new THREE.MeshStandardMaterial({ color: col, roughness: r, metalness: m });
  const mE = M(c.esmalte, 0.28), mC = M(c.cobre, 0.32, 0.85), mN = M("#1a1b1f", 0.5), mA = M(c.acento, 0.35, 0.2), mG = new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.05, transmission: 0.6, transparent: true, opacity: 0.35 });
  const add = (geo, m, x, y, z, padre = raiz) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; padre.add(o); return o; };
  // rueda
  const rueda = add(new THREE.TorusGeometry(0.17, 0.065, 18, 40), mN, 0, 0.235, 0); rueda.rotation.y = PI / 2;
  const cubo = add(new THREE.CylinderGeometry(0.1, 0.1, 0.1, 28), mC, 0, 0.235, 0); cubo.rotation.z = PI / 2;
  add(new THREE.CylinderGeometry(0.035, 0.05, 0.22, 16), mC, 0, 0.42, 0);
  // cuerpo de huevo invertido
  const perfil = [[0.001, 0.0], [0.16, 0.02], [0.3, 0.12], [0.38, 0.3], [0.4, 0.48], [0.36, 0.66], [0.26, 0.8], [0.12, 0.87], [0.001, 0.88]].map(([r, h]) => new THREE.Vector2(r, h));
  const cuerpo = add(new THREE.LatheGeometry(perfil, 56), mE, 0, 0.5, 0);
  [[0.74, 0.365], [1.2, 0.34]].forEach(([y, r]) => { const b = add(new THREE.TorusGeometry(r, 0.018, 10, 56), mC, 0, y, 0); b.rotation.x = PI / 2; });
  // ventanilla con engranajes
  const cv = document.createElement("canvas"); cv.width = cv.height = 256; const g = cv.getContext("2d"); const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const ventana = add(new THREE.CircleGeometry(0.13, 40), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }), 0, 0.98, 0.402);
  const aro = add(new THREE.TorusGeometry(0.135, 0.022, 12, 40), mC, 0, 0.98, 0.4);
  for (let i = 0; i < 8; i++) { const a = (i / 8) * 2 * PI; add(new THREE.SphereGeometry(0.012, 10, 8), mC, Math.cos(a) * 0.135, 0.82 + Math.sin(a) * 0.135 + 0.16, 0.42); }
  // perillas y botones
  [[-0.14, 1.27, mA], [-0.06, 1.29, M("#e2463a", 0.4)], [0.13, 1.28, mC]].forEach(([x, y, m]) => add(new THREE.SphereGeometry(0.028, 14, 10), m, x, y, Math.sqrt(Math.max(0, 0.27 * 0.27 - x * x)) + 0.005));
  // brazos: hombro de bola, segmentos largos, pinza de tres dedos
  const brazos = [-1, 1].map((d) => { const p = new THREE.Group(); p.position.set(d * 0.38, 1.0, 0); raiz.add(p); add(new THREE.SphereGeometry(0.07, 18, 14), mC, 0, 0, 0, p);
    const s1 = add(new THREE.CapsuleGeometry(0.035, 0.3, 6, 14), mE, 0, -0.2, 0, p); const codo = new THREE.Group(); codo.position.set(0, -0.38, 0); p.add(codo);
    add(new THREE.SphereGeometry(0.05, 14, 10), mC, 0, 0, 0, codo); add(new THREE.CapsuleGeometry(0.03, 0.26, 6, 14), mE, 0, -0.17, 0, codo);
    const mano = new THREE.Group(); mano.position.set(0, -0.34, 0); codo.add(mano); add(new THREE.CylinderGeometry(0.045, 0.035, 0.05, 16), mC, 0, 0, 0, mano);
    [0, 2.1, 4.2].forEach((a) => { const f = add(new THREE.CapsuleGeometry(0.012, 0.07, 4, 8), mN, Math.cos(a) * 0.03, -0.06, Math.sin(a) * 0.03, mano); f.rotation.set(Math.sin(a) * 0.4, 0, -Math.cos(a) * 0.4); });
    return { p, codo, mano }; });
  // bandeja con una tacita en la mano derecha
  const bandeja = new THREE.Group(); brazos[1].mano.add(bandeja); bandeja.position.set(0, -0.1, 0.1);
  add(new THREE.CylinderGeometry(0.17, 0.16, 0.014, 40), M("#b9bec4", 0.2, 0.9), 0, 0, 0.06, bandeja);
  add(new THREE.CylinderGeometry(0.04, 0.032, 0.06, 20), M("#f4f1ea", 0.3), 0.03, 0.035, 0.07, bandeja);
  // cuello de fuelle
  const cuello = new THREE.Group(); cuello.position.set(0, 1.38, 0); raiz.add(cuello);
  for (let i = 0; i < 6; i++) { const t = add(new THREE.TorusGeometry(0.075 - (i % 2) * 0.012, 0.025, 10, 28), i % 2 ? mN : mC, 0, i * 0.045, 0, cuello); t.rotation.x = PI / 2; }
  // cabeza de tambor (cilindro acostado), ojo-lente enorme y ojo diminuto
  const cabeza = new THREE.Group(); cabeza.position.set(0, 0.36, 0); cuello.add(cabeza);
  const tambor = add(new THREE.CylinderGeometry(0.24, 0.24, 0.46, 48), mE, 0, 0, 0, cabeza); tambor.rotation.z = PI / 2;
  [-1, 1].forEach((d) => { const tapa = add(new THREE.CylinderGeometry(0.245, 0.245, 0.03, 48), mC, d * 0.24, 0, 0, cabeza); tapa.rotation.z = PI / 2; });
  const ojo = new THREE.Group(); ojo.position.set(-0.07, 0.02, 0.2); cabeza.add(ojo);
  const barril = add(new THREE.CylinderGeometry(0.14, 0.15, 0.12, 40), mN, 0, 0, 0.04, ojo); barril.rotation.x = PI / 2;
  const aroOjo = add(new THREE.TorusGeometry(0.145, 0.02, 12, 40), mC, 0, 0, 0.1, ojo);
  const iris = add(new THREE.CircleGeometry(0.1, 40), new THREE.MeshBasicMaterial({ color: c.ojo, toneMapped: false }), 0, 0, 0.101, ojo);
  const pupila = add(new THREE.CircleGeometry(0.045, 32), new THREE.MeshBasicMaterial({ color: 0x120a04 }), 0, 0, 0.102, ojo);
  const cristal = add(new THREE.SphereGeometry(0.13, 32, 16, 0, 2 * PI, 0, PI / 2), mG, 0, 0, 0.09, ojo); cristal.rotation.x = PI / 2; cristal.scale.z = 0.5;
  const brillo = add(new THREE.CircleGeometry(0.02, 16), new THREE.MeshBasicMaterial({ color: 0xffffff }), 0.04, 0.05, 0.135, ojo);
  const luzOjo = new THREE.PointLight(c.ojo, 0.8, 1.2, 2); luzOjo.position.set(0, 0, 0.25); ojo.add(luzOjo);
  const ojito = new THREE.Group(); ojito.position.set(0.15, 0.08, 0.215); cabeza.add(ojito);
  const b2 = add(new THREE.CylinderGeometry(0.035, 0.04, 0.05, 20), mN, 0, 0, 0.0, ojito); b2.rotation.x = PI / 2;
  add(new THREE.CircleGeometry(0.024, 20), new THREE.MeshBasicMaterial({ color: c.acento, toneMapped: false }), 0, 0, 0.026, ojito);
  // boca: rejilla de altavoz
  for (let i = 0; i < 5; i++) add(new THREE.BoxGeometry(0.012, 0.05, 0.01), mN, 0.08 + i * 0.022, -0.13, 0.205, cabeza);
  // antenas desparejas con bombillo y oreja parabólica
  const ant1 = add(new THREE.CylinderGeometry(0.008, 0.008, 0.32, 8), mC, -0.12, 0.38, -0.02, cabeza); ant1.rotation.z = 0.25;
  const bomb1 = add(new THREE.SphereGeometry(0.035, 16, 12), new THREE.MeshBasicMaterial({ color: 0xffd27a, toneMapped: false }), -0.16, 0.54, -0.02, cabeza);
  const ant2 = new THREE.Group(); ant2.position.set(0.12, 0.22, 0); cabeza.add(ant2);
  const a2a = add(new THREE.CylinderGeometry(0.007, 0.007, 0.14, 8), mC, 0, 0.07, 0, ant2); const a2b = add(new THREE.CylinderGeometry(0.007, 0.007, 0.12, 8), mC, 0.05, 0.16, 0, ant2); a2b.rotation.z = -1.0;
  const bomb2 = add(new THREE.SphereGeometry(0.022, 14, 10), new THREE.MeshBasicMaterial({ color: c.acento, toneMapped: false }), 0.1, 0.19, 0, ant2);
  const oreja = new THREE.Group(); oreja.position.set(0.27, 0.05, 0); cabeza.add(oreja);
  const plato = add(new THREE.SphereGeometry(0.11, 28, 12, 0, 2 * PI, 0, PI * 0.35), mE, 0.04, 0, 0, oreja); plato.rotation.z = -PI / 2;
  add(new THREE.CylinderGeometry(0.006, 0.006, 0.08, 6), mC, 0.06, 0, 0, oreja).rotation.z = PI / 2;
  function animar(t, s = {}) {
    const habla = s.voz || 0; cuello.scale.y = 1 + 0.15 * Math.sin(t * 1.3) * 0.3 + (s.estira || 0); cabeza.rotation.set(Math.sin(t * 0.9) * 0.05, s.mira ?? Math.sin(t * 0.6) * 0.25, Math.sin(t * 0.7) * 0.06 + (s.ladea || 0));
    oreja.rotation.x = t * 3; bomb1.material.color.setHSL(0.11, 1, 0.55 + 0.25 * Math.abs(Math.sin(t * 4))); bomb2.material.color.setHSL(0.48, 0.8, 0.4 + 0.3 * Math.abs(Math.sin(t * 6 + 1)));
    const z = 1 + 0.25 * Math.sin(t * 2.5) * (s.enfoca ?? 0.4); iris.scale.setScalar(z); pupila.scale.setScalar(1.4 - 0.5 * z); luzOjo.intensity = 0.6 + habla * 1.2;
    brazos[0].p.rotation.set(-0.3 + Math.sin(t * 1.1) * 0.08, 0, -0.25); brazos[0].codo.rotation.x = -0.5; brazos[1].p.rotation.set(-0.9, 0, 0.15); brazos[1].codo.rotation.x = -0.9;
    bandeja.rotation.x = 0.9 + 0.9 - 0.0; bandeja.rotation.x = -(brazos[1].p.rotation.x + brazos[1].codo.rotation.x);
    g.fillStyle = "#1a0f06"; g.fillRect(0, 0, 256, 256);
    [[90, 110, 70, 10, 1], [170, 150, 50, 8, -1.6], [120, 190, 36, 7, 2.2]].forEach(([x, y, r, n, v]) => { g.save(); g.translate(x, y); g.rotate(t * v); g.fillStyle = "#ffb347"; g.shadowColor = "#ff8a00"; g.shadowBlur = 18;
      g.beginPath(); for (let i = 0; i < n * 2; i++) { const a = (i / (n * 2)) * 2 * PI, rr = i % 2 ? r : r * 0.78; g.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); } g.closePath(); g.fill();
      g.fillStyle = "#1a0f06"; g.beginPath(); g.arc(0, 0, r * 0.3, 0, 2 * PI); g.fill(); g.restore(); });
    tex.needsUpdate = true; rueda.rotation.x = t * 2;
  }
  return { raiz, animar };
}
