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
    const fu = c.fuerte ? 1 : 0;
    if (y < 0) { const k = 1 - (c.mujer ? 0.3 : fu ? 0.2 : 0.36) * Math.pow(-y, fu ? 1.8 : 1.3); x *= k; z = z > 0 ? z * (1 - 0.05 * -y) : z * k; }   // mandíbula (cuadrada si es fuerte)
    if (fu) { x *= 1 + 0.07 * Math.exp(-Math.pow(y + 0.58, 2) / 0.012) * (Math.abs(x) > 0.3 ? 1 : 0);                                 // ángulo de la mandíbula
      x *= 1 - 0.05 * Math.exp(-Math.pow(y + 0.3, 2) / 0.01) * fr;                                                                  // mejilla hundida bajo el pómulo
      z += 0.07 * Math.exp(-(x * x) / 0.004 - Math.pow(y + 0.0, 2) / 0.06) * (z > 0.6 ? 1 : 0); }                                    // tabique recto
    x *= 1 + 0.07 * Math.exp(-Math.pow(y + 0.02, 2) / 0.03) * fr;                                                                   // pómulos
    if (y < -0.68 && z > 0) z += (fu ? 0.13 : 0.16) * Math.exp(-(x * x) / (fu ? 0.14 : 0.06)) * (fu ? 1 - 0.35 * Math.exp(-(x * x) / 0.002) : 1);                                                                   // mentón
    z += (c.mujer ? 0.2 : 0.3) * g(x, y + 0.08, 0.007, 0.045) * (z > 0.5 ? 1 : 0);                                                                      // nariz
    z -= 0.09 * (g(x - 0.36, y - 0.12, 0.02, 0.012) + g(x + 0.36, y - 0.12, 0.02, 0.012)) * fr;                                     // cuencas
    z += (fu ? 0.1 : 0.06) * Math.exp(-Math.pow(y - 0.27, 2) / 0.008) * fr * (Math.abs(x) < 0.7 ? 1 : 0);                                        // ceja ósea
    if (y > 0.7) y = 0.7 + (y - 0.7) * 0.8;                                                                                         // coronilla un poco plana
    p.setXYZ(i, x * 0.86, y * 1.16, z * 0.98);
    // color por vértice: piel, barba de pocos días en mandíbula y bigote, labios
    let cc = piel.clone(); const yb = y;
    const fbz = c.barbaNivel ?? (c.mujer ? 0 : 0.7), nariz = Math.abs(x) < 0.22 && yb > -0.34 && z > 0.78, bigote = Math.abs(x) < 0.24 && yb <= -0.34 && yb > -0.42 && z > 0.78, zonaBarba = !nariz && ((yb < -0.26 && z > -0.3) || (fbz >= 0.85 && bigote));
    const fb = c.barbaNivel ?? (c.mujer ? 0 : 0.7); if (zonaBarba && fb > 0) cc.lerp(barba, Math.min(0.92, fb * Math.min(1, (-0.26 - yb) * 5 + 0.45 + (fb > 0.85 ? 0.4 : 0))));
    if (yb < -0.4 && yb > -0.49 && Math.abs(x) < 0.2 && z > 0.84) cc = fbz > 0.85 ? lab.clone().lerp(barba, 0.35) : lab.clone();
    col.push(cc.r, cc.g, cc.b);
  }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3)); geo.computeVertexNormals(); geo.scale(R, R, R);
  const cuello = new THREE.Group(); cuello.position.set(0, 1.5, 0); cuerpo.add(cuello);
  add(new THREE.CylinderGeometry(c.fuerte ? 0.064 : 0.055, c.fuerte ? 0.075 : 0.065, 0.12, 8), F(c.piel), 0, 0.03, 0, cuello);
  const cabeza = new THREE.Group(); cabeza.position.set(0, 0.2, 0.01); cuello.add(cabeza);
  add(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.62, flatShading: true }), 0, 0, 0, cabeza);
  [-1, 1].forEach((d) => { const o = add(new THREE.SphereGeometry(0.03, 6, 5), F(c.piel), d * R * 0.86, -0.005, -0.01, cabeza); o.scale.set(0.45, 1, 0.8); });
  // ojos: almendra blanca, iris oscuro con brillo, párpado y pestaña
  const ojos = [-1, 1].map((d) => { const e = new THREE.Group(); e.position.set(d * R * 0.31, R * 0.13, R * 0.84); e.rotation.y = d * 0.22; cabeza.add(e);
    add(new THREE.SphereGeometry(0.017, 10, 6), F("#efe9e2", 0.35), 0, 0, 0, e).scale.set(1.35, 0.62, 0.5);
    const iris = add(new THREE.CircleGeometry(0.0098, 10), new THREE.MeshStandardMaterial({ color: c.iris, roughness: 0.2 }), 0, -0.001, 0.0086, e);
    add(new THREE.CircleGeometry(0.0048, 8), new THREE.MeshBasicMaterial({ color: 0x050403 }), 0, -0.001, 0.0088, e);
    add(new THREE.CircleGeometry(0.0022, 6), new THREE.MeshBasicMaterial({ color: 0xffffff }), 0.003, 0.003, 0.009, e);
    const lid = add(new THREE.BoxGeometry(c.mujer ? 0.048 : 0.044, c.mujer ? 0.009 : 0.006, 0.012), F(c.mujer ? "#0d0a09" : c.pelo, 0.6), 0, 0.009, 0.004, e); lid.rotation.z = d * (c.mujer ? -0.12 : 0.08);
    const ceja = add(new THREE.BoxGeometry(c.mujer ? 0.044 : 0.046, c.mujer ? 0.004 : 0.0075, 0.01), F(c.pelo, 0.7), d * 0.002, c.mujer ? 0.03 : 0.026, 0.006, e); ceja.rotation.z = c.mujer ? -d * 0.16 : -d * 0.05;
    return { e, iris, ceja }; });
  const boca = add(new THREE.BoxGeometry(R * 0.32, R * 0.03, R * 0.05), new THREE.MeshBasicMaterial({ color: 0x1a0c0a }), 0, -R * 0.53, R * 0.86, cabeza);
  // pelo: mechones facetados despeinados (más volumen arriba y adelante)
  const mP = F(c.pelo, 0.6), r = semilla(c.semilla || 11);
  const tapa = add(new THREE.SphereGeometry(R * 1.04, 12, 8, 0, 2 * PI, 0, PI * 0.36), mP, 0, R * 0.14, -R * 0.06, cabeza); tapa.scale.set(0.92, 1.05, 1.02); tapa.rotation.x = -0.28;
  add(new THREE.SphereGeometry(R * 1.03, 12, 8, PI * 1.08, PI * 0.84, 0, PI * 0.64), mP, 0, R * 0.05, -R * 0.03, cabeza).scale.set(0.9, 1.08, 1.0);
  [-1, 1].forEach((d) => { const lado = add(new THREE.IcosahedronGeometry(R * 0.34, 0), mP, d * R * 0.8, R * 0.42, -R * 0.12, cabeza); lado.scale.set(0.45, 0.9, 1.1); });
  const peinado = c.peinado || "despeinado", mech = (n, rad, yBase, desv, esc) => { for (let i = 0; i < n; i++) { const a = r() * PI * 2, el = 0.3 + r() * 0.55;
      const m = add(new THREE.IcosahedronGeometry(R * rad * (0.8 + r() * 0.4), 0), mP, Math.cos(a) * Math.sin(el) * R * 0.8, R * (yBase + Math.cos(el) * 0.42), Math.sin(a) * Math.sin(el) * R * 0.8 + desv, cabeza);
      m.scale.set(...esc); m.rotation.set(r() * 1.2 - 0.6, a, r() * 0.8 - 0.4); } };
  if (peinado === "despeinado") { for (let i = 0; i < 16; i++) { const a = r() * PI * 2, el = 0.35 + r() * 0.5; const m = add(new THREE.IcosahedronGeometry(R * (0.32 + r() * 0.16), 0), mP,
      Math.cos(a) * Math.sin(el) * R * 0.78, R * (0.7 + Math.cos(el) * 0.42), Math.sin(a) * Math.sin(el) * R * 0.78 - R * 0.02, cabeza); m.scale.set(1, 0.55, 1.5); m.rotation.set(r() * 1.2 - 0.6, a, r() * 0.8 - 0.4); }
  for (let i = 0; i < 3; i++) { const m = add(new THREE.IcosahedronGeometry(R * 0.3, 0), mP, R * (-0.3 + i * 0.28), R * 0.86, R * 0.55, cabeza); m.scale.set(0.9, 0.45, 1.3); m.rotation.set(0.5, 0, -0.4 + i * 0.35); } }
  if (peinado === "tupe") { mech(8, 0.24, 0.66, -R * 0.06, [1, 0.38, 1.3]);
    for (let i = 0; i < 9; i++) { const x0 = R * (-0.42 + (i % 5) * 0.21), m = add(new THREE.IcosahedronGeometry(R * (0.3 + r() * 0.08), 0), mP, x0, R * (0.95 + r() * 0.12 + (i > 4 ? 0.08 : 0)), R * (0.42 - (i > 4 ? 0.35 : 0)), cabeza); m.scale.set(0.8, 0.6, 1.6); m.rotation.set(-0.7 - r() * 0.3, (r() - 0.5) * 0.4, (r() - 0.5) * 0.3); } }
  if (peinado === "atras") { for (let i = 0; i < 14; i++) { const x0 = R * (-0.5 + (i % 7) * 0.165), z0 = R * (0.35 - Math.floor(i / 7) * 0.6), m = add(new THREE.IcosahedronGeometry(R * 0.3, 0), mP, x0, R * (0.85 - Math.abs(x0 / R) * 0.25 - Math.floor(i / 7) * 0.06), z0, cabeza);
      m.scale.set(0.7, 0.42, 2.0); m.rotation.set(0.15, x0 / R * -0.4, 0); } }
  if (peinado === "definitivo") {   // tupé peinado hacia atrás que termina en un moño alto; lados cortos
    for (let i = 0; i < 10; i++) { const x0 = R * (-0.42 + (i % 5) * 0.21), z0 = R * (0.3 - Math.floor(i / 5) * 0.55), m = add(new THREE.IcosahedronGeometry(R * 0.3, 0), mP, x0, R * (0.9 - Math.abs(x0 / R) * 0.25 - Math.floor(i / 5) * 0.02), z0, cabeza);
      m.scale.set(0.72, 0.45, 2.0); m.rotation.set(0.1, x0 / R * -0.35, 0); }
    for (let i = 0; i < 5; i++) { const x0 = R * (-0.32 + i * 0.16), m = add(new THREE.IcosahedronGeometry(R * (0.3 + r() * 0.04), 0), mP, x0, R * (0.97 + r() * 0.04), R * 0.42, cabeza); m.scale.set(0.8, 0.42, 1.7); m.rotation.set(-0.22, (r() - 0.5) * 0.25, (r() - 0.5) * 0.15); }
    const mono = add(new THREE.IcosahedronGeometry(R * 0.36, 1), mP, 0, R * 1.0, -R * 0.62, cabeza); mono.scale.set(1, 0.85, 1);
    add(new THREE.TorusGeometry(R * 0.2, R * 0.05, 4, 8), F("#0b0908", 0.5), 0, R * 0.92, -R * 0.45, cabeza).rotation.x = 1.1;
    [-1, 1].forEach((d) => { const lado = add(new THREE.IcosahedronGeometry(R * 0.34, 0), F(c.pelo, 0.7), d * R * 0.8, R * 0.38, -R * 0.15, cabeza); lado.scale.set(0.4, 0.75, 1.1); }); }
  if (peinado === "corto") { mech(10, 0.26, 0.74, -R * 0.02, [1, 0.4, 1.3]); }
  if (peinado === "rizado") { for (let i = 0; i < 40; i++) { const a = r() * PI * 2, el = r() * 1.25; const m = add(new THREE.IcosahedronGeometry(R * (0.17 + r() * 0.07), 0), mP,
      Math.cos(a) * Math.sin(el) * R * 1.0, R * (0.25 + Math.cos(el) * 0.85), Math.sin(a) * Math.sin(el) * R * 0.98 - R * 0.05, cabeza); m.rotation.set(r() * 3, r() * 3, r() * 3); } }
  if (peinado === "largo" || peinado === "melena") { mech(12, 0.3, 0.7, -R * 0.02, [1, 0.5, 1.4]); const larg = peinado === "melena" ? 1.7 : 1.05;
    for (let i = 0; i < 14; i++) { const a = PI * (0.62 + r() * 0.76), m = add(new THREE.IcosahedronGeometry(R * 0.32, 0), mP, Math.cos(a) * R * 0.86 * (i % 2 ? 1 : -1) * 0.95 + (r() - 0.5) * R * 0.2, -R * (0.1 + r() * 0.75 * larg), -Math.abs(Math.sin(a)) * R * 0.55 - R * 0.1, cabeza); m.scale.set(0.8, 1.5, 0.9); m.rotation.set(r() * 0.4, r() * 2, r() * 0.3); }
    if (peinado === "melena") [-1, 1].forEach((d) => { for (let k = 0; k < 4; k++) { const m = add(new THREE.IcosahedronGeometry(R * 0.26, 0), mP, d * R * 0.82, -R * (0.05 + k * 0.32), R * 0.05 - k * R * 0.05, cabeza); m.scale.set(0.6, 1.5, 0.9); } }); }
  if (peinado === "coleta") { mech(8, 0.24, 0.76, -R * 0.04, [1, 0.38, 1.3]); for (let k = 0; k < 6; k++) { const m = add(new THREE.IcosahedronGeometry(R * (0.3 - k * 0.025), 0), mP, 0, R * (0.75 - k * 0.32), -R * (1.05 + k * 0.08), cabeza); m.scale.set(0.9, 1.4, 0.9); } }
  if (peinado === "mono") { mech(8, 0.24, 0.76, -R * 0.04, [1, 0.38, 1.3]); add(new THREE.IcosahedronGeometry(R * 0.42, 1), mP, 0, R * 1.08, -R * 0.35, cabeza).scale.set(1, 0.8, 1); }
  if (c.gafas) { const mg = F(c.gafas, 0.3); [-1, 1].forEach((d) => { const ar = add(new THREE.TorusGeometry(R * 0.2, R * 0.03, 4, 8), mg, d * R * 0.31, R * 0.13, R * 0.97, cabeza); ar.rotation.z = PI / 8; ar.scale.y = 0.8; });
    add(new THREE.BoxGeometry(R * 0.2, R * 0.04, R * 0.04), mg, 0, R * 0.16, R * 1.0, cabeza); [-1, 1].forEach((d) => add(new THREE.BoxGeometry(R * 0.04, R * 0.04, R * 0.8), mg, d * R * 0.52, R * 0.15, R * 0.55, cabeza)); }
  // ---------- cuerpo (proporciones reales, pocas caras)
  const mCam = F(c.camisa, 0.85), mPan = F(c.pantalon, 0.85), mPiel = F(c.piel, 0.65);
  const torso = new THREE.Group(); torso.position.set(0, 0.95, 0); cuerpo.add(torso);
  const t = add(new THREE.CylinderGeometry(c.mujer ? 0.175 : c.fuerte ? 0.225 : 0.2, c.mujer ? 0.13 : 0.15, 0.55, 10), mCam, 0, 0.27, 0, torso); t.scale.z = 0.62;
  if (c.delantal) { const dl = add(new THREE.BoxGeometry(0.3, 0.75, 0.02), F(c.delantal, 0.9), 0, 0.02, 0.13, torso); [-1, 1].forEach((d) => add(new THREE.BoxGeometry(0.02, 0.22, 0.012), F(c.delantal, 0.9), d * 0.09, 0.47, 0.12, torso).rotation.z = d * 0.25); }
  add(new THREE.CylinderGeometry(0.15, 0.16, 0.14, 10), mCam, 0, -0.02, 0, torso).scale.z = 0.66;
  add(new THREE.SphereGeometry(0.2, 10, 5, 0, 2 * PI, 0, PI * 0.5), mCam, 0, 0.54, 0, torso).scale.set(1.05, 0.3, 0.64);
  const v = add(new THREE.ConeGeometry(0.045, 0.1, 3), mPiel, 0, 0.5, 0.115, torso); v.rotation.set(PI + 0.25, 0, 0);
  [-1, 1].forEach((d) => { const cuel = add(new THREE.BoxGeometry(0.06, 0.03, 0.012), mCam, d * 0.04, 0.545, 0.11, torso); cuel.rotation.z = d * 0.6; });
  for (let i = 0; i < 3; i++) add(new THREE.SphereGeometry(0.006, 6, 4), F("#d9d4cc", 0.4), 0, 0.42 - i * 0.1, 0.128 - i * 0.004, torso);
  const brazos = [-1, 1].map((d) => { const h = new THREE.Group(); h.position.set(d * (c.mujer ? 0.19 : c.fuerte ? 0.24 : 0.215), 0.5, 0); torso.add(h); add(new THREE.SphereGeometry(0.065, 8, 6), mCam, 0, 0, 0, h);
    add(new THREE.CylinderGeometry(0.055, 0.046, 0.3, 8), mCam, 0, -0.16, 0, h); const codo = new THREE.Group(); codo.position.set(0, -0.31, 0); h.add(codo);
    add(new THREE.CylinderGeometry(0.046, 0.038, 0.27, 8), mCam, 0, -0.13, 0, codo); add(new THREE.CylinderGeometry(0.036, 0.034, 0.05, 8), mPiel, 0, -0.28, 0, codo);
    const mano = add(new THREE.BoxGeometry(0.06, 0.09, 0.03), mPiel, 0, -0.34, 0.005, codo); add(new THREE.BoxGeometry(0.018, 0.045, 0.02), mPiel, -d * 0.032, -0.325, 0.012, codo).rotation.z = d * 0.5;
    return { h, codo, mano }; });
  const piernas = [-1, 1].map((d) => { const l = new THREE.Group(); l.position.set(d * 0.09, 0.92, 0); cuerpo.add(l); add(new THREE.CylinderGeometry(0.075, 0.06, 0.45, 8), mPan, 0, -0.22, 0, l);
    add(new THREE.CylinderGeometry(0.058, 0.048, 0.42, 8), mPan, 0, -0.66, 0, l); add(new THREE.BoxGeometry(0.09, 0.07, 0.24), F(c.zapatos, 0.5), 0, -0.88, 0.05, l); return l; });
  const taza = new THREE.Group(); brazos[1].codo.add(taza); taza.position.set(0, -0.36, 0.05); add(new THREE.CylinderGeometry(0.04, 0.035, 0.1, 10), F("#e8e2d8", 0.5), 0, 0, 0, taza);
  add(new THREE.TorusGeometry(0.025, 0.007, 4, 8), F("#e8e2d8", 0.5), 0.045, 0, 0, taza).rotation.y = PI / 2; taza.visible = false;
  function pose(s = {}) {
    taza.visible = !!s.taza; taza.rotation.x = -(s.bd?.[0] ?? 0) - (s.bd?.[2] ?? 0);
    boca.scale.y = 1 + (s.voz || 0) * 5; boca.position.y = -R * 0.53 - (s.voz || 0) * R * 0.04;
    if (s.sentado) { cuerpo.position.y = -0.43; piernas.forEach((l) => l.rotation.x = -1.5); } else { cuerpo.position.y = 0; piernas.forEach((l) => l.rotation.x = 0); }
    cabeza.rotation.set(s.miraY || 0, s.mira || 0, s.ladea || 0); torso.rotation.x = s.inclina || 0;
    brazos[0].h.rotation.set(s.bi?.[0] ?? 0.05, 0, s.bi?.[1] ?? -0.08); brazos[0].codo.rotation.x = s.bi?.[2] ?? -0.15;
    brazos[1].h.rotation.set(s.bd?.[0] ?? 0.05, 0, s.bd?.[1] ?? 0.08); brazos[1].codo.rotation.x = s.bd?.[2] ?? -0.15;
    ojos.forEach(({ iris, ceja }, i) => { iris.position.x = (s.ojosX || 0) * 0.004; ceja.position.y = 0.026 + (s.cejas || 0) * 0.004; });
  }
  pose();
  return { raiz, cabeza, torso, brazos, piernas, pose };
}
