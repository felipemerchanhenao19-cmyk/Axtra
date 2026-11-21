// «Low-poly»: personaje de proporciones reales con acabado facetado (sombreado plano), como animación 3D estilizada.
// La cabeza es una esfera de pocas caras esculpida por vértices (mandíbula, pómulos, nariz, cuencas, mentón) y pintada con
// colores por vértice (barba de pocos días, labios). Pelo de mechones facetados, ropa de pocas caras.
function personaLowPoly(cfg = {}) {
  const c = Object.assign({ piel: "#c99272", barba: "#3a2a22", labios: "#a8645a", pelo: "#1c1512", camisa: "#1d1f24", pantalon: "#23262d", zapatos: "#141416", iris: "#3b2a1e", alto: 1 }, cfg);
  const F = (col, r = 0.75, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: col, roughness: r, flatShading: true }, o));
  const add = (geo, m, x = 0, y = 0, z = 0, padre) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; padre.add(o); return o; };
  const raiz = new THREE.Group(), cuerpo = new THREE.Group(); raiz.add(cuerpo); raiz.scale.setScalar(c.alto);
  // ---------- cabeza esculpida
  const R = 0.118, geo = new THREE.SphereGeometry(1, 22, 16), p = geo.attributes.position, col = [], piel = new THREE.Color(c.piel), barba = new THREE.Color(c.barba), lab = new THREE.Color(c.labios);
  const g = (x, y, sx, sy) => Math.exp(-(x * x) / sx - (y * y) / sy);
  for (let i = 0; i < p.count; i++) {
    let x = p.getX(i), y = p.getY(i), z = p.getZ(i); const fr = Math.max(0, z);
    if (y < 0) { const k = 1 - 0.36 * Math.pow(-y, 1.3); x *= k; z = z > 0 ? z * (1 - 0.05 * -y) : z * k; }                       // mandíbula
    x *= 1 + 0.07 * Math.exp(-Math.pow(y + 0.02, 2) / 0.03) * fr;                                                                   // pómulos
    if (y < -0.68 && z > 0) z += 0.16 * Math.exp(-(x * x) / 0.06);                                                                   // mentón
    z += 0.3 * g(x, y + 0.08, 0.008, 0.05) * (z > 0.5 ? 1 : 0);                                                                      // nariz
    z -= 0.09 * (g(x - 0.36, y - 0.12, 0.02, 0.012) + g(x + 0.36, y - 0.12, 0.02, 0.012)) * fr;                                     // cuencas
    z += 0.06 * Math.exp(-Math.pow(y - 0.27, 2) / 0.008) * fr * (Math.abs(x) < 0.7 ? 1 : 0);                                        // ceja ósea
    if (y > 0.7) y = 0.7 + (y - 0.7) * 0.8;                                                                                         // coronilla un poco plana
    p.setXYZ(i, x * 0.86, y * 1.16, z * 0.98);
    // color por vértice: piel, barba de pocos días en mandíbula y bigote, labios
    let cc = piel.clone(); const yb = y;
    const zonaBarba = (yb < -0.14 && z > -0.3) && !(Math.abs(x) < 0.16 && yb > -0.32 && z > 0.85);
    if (zonaBarba) cc.lerp(barba, 0.7 * Math.min(1, (-0.14 - yb) * 4 + 0.35));
    if (yb < -0.36 && yb > -0.5 && Math.abs(x) < 0.28 && z > 0.82) cc = lab.clone();
    col.push(cc.r, cc.g, cc.b);
  }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3)); geo.computeVertexNormals(); geo.scale(R, R, R);
  const cuello = new THREE.Group(); cuello.position.set(0, 1.5, 0); cuerpo.add(cuello);
  add(new THREE.CylinderGeometry(0.055, 0.065, 0.12, 8), F(c.piel), 0, 0.03, 0, cuello);
  const cabeza = new THREE.Group(); cabeza.position.set(0, 0.2, 0.01); cuello.add(cabeza);
  add(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.62, flatShading: true }), 0, 0, 0, cabeza);
  [-1, 1].forEach((d) => { const o = add(new THREE.SphereGeometry(0.03, 6, 5), F(c.piel), d * R * 0.86, -0.005, -0.01, cabeza); o.scale.set(0.45, 1, 0.8); });
  // ojos: almendra blanca, iris oscuro con brillo, párpado y pestaña
  const ojos = [-1, 1].map((d) => { const e = new THREE.Group(); e.position.set(d * R * 0.31, R * 0.13, R * 0.84); e.rotation.y = d * 0.22; cabeza.add(e);
    add(new THREE.SphereGeometry(0.017, 10, 6), F("#efe9e2", 0.35), 0, 0, 0, e).scale.set(1.35, 0.62, 0.5);
    const iris = add(new THREE.CircleGeometry(0.0098, 10), new THREE.MeshStandardMaterial({ color: c.iris, roughness: 0.2 }), 0, -0.001, 0.0086, e);
    add(new THREE.CircleGeometry(0.0048, 8), new THREE.MeshBasicMaterial({ color: 0x050403 }), 0, -0.001, 0.0088, e);
    add(new THREE.CircleGeometry(0.0022, 6), new THREE.MeshBasicMaterial({ color: 0xffffff }), 0.003, 0.003, 0.009, e);
    const lid = add(new THREE.BoxGeometry(0.044, 0.006, 0.012), F(c.pelo, 0.6), 0, 0.009, 0.004, e); lid.rotation.z = d * 0.08;
    const ceja = add(new THREE.BoxGeometry(0.046, 0.0075, 0.01), F(c.pelo, 0.7), d * 0.002, 0.026, 0.006, e); ceja.rotation.z = -d * 0.12;
    return { e, iris, ceja }; });
  // pelo: mechones facetados despeinados (más volumen arriba y adelante)
  const mP = F(c.pelo, 0.6), r = semilla(c.semilla || 11);
  const tapa = add(new THREE.SphereGeometry(R * 1.04, 12, 8, 0, 2 * PI, 0, PI * 0.36), mP, 0, R * 0.14, -R * 0.06, cabeza); tapa.scale.set(0.92, 1.05, 1.02); tapa.rotation.x = -0.28;
  add(new THREE.SphereGeometry(R * 1.03, 12, 8, PI * 1.08, PI * 0.84, 0, PI * 0.64), mP, 0, R * 0.05, -R * 0.03, cabeza).scale.set(0.9, 1.08, 1.0);
  [-1, 1].forEach((d) => { const lado = add(new THREE.IcosahedronGeometry(R * 0.34, 0), mP, d * R * 0.8, R * 0.42, -R * 0.12, cabeza); lado.scale.set(0.45, 0.9, 1.1); });
  for (let i = 0; i < 16; i++) { const a = r() * PI * 2, el = 0.35 + r() * 0.5; const m = add(new THREE.IcosahedronGeometry(R * (0.32 + r() * 0.16), 0), mP,
      Math.cos(a) * Math.sin(el) * R * 0.78, R * (0.7 + Math.cos(el) * 0.42), Math.sin(a) * Math.sin(el) * R * 0.78 - R * 0.02, cabeza); m.scale.set(1, 0.55, 1.5); m.rotation.set(r() * 1.2 - 0.6, a, r() * 0.8 - 0.4); }
  for (let i = 0; i < 3; i++) { const m = add(new THREE.IcosahedronGeometry(R * 0.3, 0), mP, R * (-0.3 + i * 0.28), R * 0.86, R * 0.55, cabeza); m.scale.set(0.9, 0.45, 1.3); m.rotation.set(0.5, 0, -0.4 + i * 0.35); }
  // ---------- cuerpo (proporciones reales, pocas caras)
  const mCam = F(c.camisa, 0.85), mPan = F(c.pantalon, 0.85), mPiel = F(c.piel, 0.65);
  const torso = new THREE.Group(); torso.position.set(0, 0.95, 0); cuerpo.add(torso);
  const t = add(new THREE.CylinderGeometry(0.2, 0.15, 0.55, 10), mCam, 0, 0.27, 0, torso); t.scale.z = 0.62;
  add(new THREE.CylinderGeometry(0.15, 0.16, 0.14, 10), mCam, 0, -0.02, 0, torso).scale.z = 0.66;
  add(new THREE.SphereGeometry(0.2, 10, 5, 0, 2 * PI, 0, PI * 0.5), mCam, 0, 0.54, 0, torso).scale.set(1.05, 0.3, 0.64);
  const v = add(new THREE.ConeGeometry(0.045, 0.1, 3), mPiel, 0, 0.5, 0.115, torso); v.rotation.set(PI + 0.25, 0, 0);
  [-1, 1].forEach((d) => { const cuel = add(new THREE.BoxGeometry(0.06, 0.03, 0.012), mCam, d * 0.04, 0.545, 0.11, torso); cuel.rotation.z = d * 0.6; });
  for (let i = 0; i < 3; i++) add(new THREE.SphereGeometry(0.006, 6, 4), F("#d9d4cc", 0.4), 0, 0.42 - i * 0.1, 0.128 - i * 0.004, torso);
  const brazos = [-1, 1].map((d) => { const h = new THREE.Group(); h.position.set(d * 0.215, 0.5, 0); torso.add(h); add(new THREE.SphereGeometry(0.065, 8, 6), mCam, 0, 0, 0, h);
    add(new THREE.CylinderGeometry(0.055, 0.046, 0.3, 8), mCam, 0, -0.16, 0, h); const codo = new THREE.Group(); codo.position.set(0, -0.31, 0); h.add(codo);
    add(new THREE.CylinderGeometry(0.046, 0.038, 0.27, 8), mCam, 0, -0.13, 0, codo); add(new THREE.CylinderGeometry(0.036, 0.034, 0.05, 8), mPiel, 0, -0.28, 0, codo);
    const mano = add(new THREE.BoxGeometry(0.06, 0.09, 0.03), mPiel, 0, -0.34, 0.005, codo); add(new THREE.BoxGeometry(0.018, 0.045, 0.02), mPiel, -d * 0.032, -0.325, 0.012, codo).rotation.z = d * 0.5;
    return { h, codo }; });
  const piernas = [-1, 1].map((d) => { const l = new THREE.Group(); l.position.set(d * 0.09, 0.92, 0); cuerpo.add(l); add(new THREE.CylinderGeometry(0.075, 0.06, 0.45, 8), mPan, 0, -0.22, 0, l);
    add(new THREE.CylinderGeometry(0.058, 0.048, 0.42, 8), mPan, 0, -0.66, 0, l); add(new THREE.BoxGeometry(0.09, 0.07, 0.24), F(c.zapatos, 0.5), 0, -0.88, 0.05, l); return l; });
  function pose(s = {}) {
    cabeza.rotation.set(s.miraY || 0, s.mira || 0, s.ladea || 0); torso.rotation.x = s.inclina || 0;
    brazos[0].h.rotation.set(s.bi?.[0] ?? 0.05, 0, s.bi?.[1] ?? -0.08); brazos[0].codo.rotation.x = s.bi?.[2] ?? -0.15;
    brazos[1].h.rotation.set(s.bd?.[0] ?? 0.05, 0, s.bd?.[1] ?? 0.08); brazos[1].codo.rotation.x = s.bd?.[2] ?? -0.15;
    ojos.forEach(({ iris, ceja }, i) => { iris.position.x = (s.ojosX || 0) * 0.004; ceja.position.y = 0.026 + (s.cejas || 0) * 0.004; });
  }
  pose();
  return { raiz, cabeza, torso, brazos, piernas, pose };
}
