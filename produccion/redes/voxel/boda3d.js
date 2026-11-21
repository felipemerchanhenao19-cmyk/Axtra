// «Boda»: jardín al aire libre a la hora dorada. Pasto, árboles redondeados, cielo cálido con sol bajo, arco de flores,
// sillas blancas, mesa redonda con mantel, bufé, torta de tres pisos y guirnaldas de luces entre los árboles.
// Coordenadas locales: mesa principal en el centro (0, 0); el arco de la ceremonia al fondo (z = -7).
function boda(escena) {
  const B = new THREE.Group(); B.position.set(60, 0, 0); escena.add(B); const U = {}, r = semilla(808);
  U.fondo = 0xf3d2a4; U.niebla = [0xf1d7b4, 0.018];
  const M = (col, rg = 0.8, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: col, roughness: rg }, o));
  const add = (geo, m, x, y, z, padre = B) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; padre.add(o); return o; };
  const lienzo = (w, h, f, rep = 1) => { const c = document.createElement("canvas"); c.width = w; c.height = h; f(c.getContext("2d"), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    if (rep > 1) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep, rep); } return t; };
  const blanda = (() => { const c = document.createElement("canvas"); c.width = c.height = 128; const g = c.getContext("2d"), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.3, "rgba(255,255,255,.45)"); gr.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })();
  // cielo: cúpula con degradado de la hora dorada y el sol bajo detrás de los árboles
  const cielo = new THREE.Mesh(new THREE.SphereGeometry(70, 48, 24), new THREE.MeshBasicMaterial({ side: THREE.BackSide, fog: false, map: lienzo(16, 512, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, "#5f9fe0"); gr.addColorStop(0.36, "#a9cdee"); gr.addColorStop(0.48, "#f7dcb0"); gr.addColorStop(0.53, "#f6c48a"); gr.addColorStop(1, "#e9b47c");
    g.fillStyle = gr; g.fillRect(0, 0, w, h); }) })); B.add(cielo);
  const sol = new THREE.Sprite(new THREE.SpriteMaterial({ map: blanda, color: 0xfff1cf, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, fog: false })); sol.position.set(-22, 7, -40); sol.scale.setScalar(26); B.add(sol);
  const nucleo = new THREE.Sprite(new THREE.SpriteMaterial({ map: blanda, color: 0xffffff, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, fog: false })); nucleo.position.copy(sol.position); nucleo.scale.setScalar(6); B.add(nucleo);
  // nubes suaves
  for (let i = 0; i < 9; i++) { const n = new THREE.Sprite(new THREE.SpriteMaterial({ map: blanda, color: 0xfff6ea, transparent: true, opacity: 0.55, depthWrite: false, fog: false }));
    n.position.set(-40 + r() * 80, 14 + r() * 10, -45 - r() * 10); n.scale.set(14 + r() * 10, 4 + r() * 2, 1); B.add(n); }
  // luces: sol cálido de contraluz con sombras suaves y cielo azul desde arriba
  const luzSol = new THREE.DirectionalLight(0xffd29a, 2.6); luzSol.position.set(-9, 7, -10); luzSol.target.position.set(0, 0, 0); luzSol.castShadow = true;
  luzSol.shadow.mapSize.set(2048, 2048); Object.assign(luzSol.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 40 }); luzSol.shadow.bias = -0.0004; luzSol.shadow.radius = 4;
  B.add(luzSol); B.add(luzSol.target);
  B.add(new THREE.HemisphereLight(0xcfe6ff, 0x6f8a3c, 1.05));
  const frente = new THREE.DirectionalLight(0xfff0dc, 0.75); frente.position.set(4, 5, 8); B.add(frente);
  // pasto con textura suave y colinas lejanas
  const pasto = add(new THREE.CircleGeometry(60, 64), M(0x7aa64a, 0.95, { map: lienzo(256, 256, (g, w, h) => { g.fillStyle = "#7aa64a"; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 3500; i++) { const v = r(); g.fillStyle = v < 0.5 ? "rgba(70,110,40,.35)" : "rgba(170,200,100,.3)"; g.fillRect(r() * w, r() * h, 2, 3 + r() * 4); } }, 18) }), 0, 0, 0); pasto.rotation.x = -PI / 2;
  [[-30, -45, 22, 0x86a85a], [10, -50, 26, 0x7b9f52], [38, -42, 18, 0x8fb062], [-55, -25, 20, 0x87a95c]].forEach(([x, z, s, col]) => { const c = add(new THREE.SphereGeometry(s, 32, 16), M(col, 1), x, -s * 0.72, z); c.scale.y = 0.55; c.castShadow = false; });
  // árboles redondeados (copas de varias esferas en tonos de verde)
  const verdes = [0x4f8a3a, 0x5f9a42, 0x6fae4a, 0x467e34, 0x7ab857];
  const arbol = (x, z, s) => { const g = new THREE.Group(); g.position.set(x, 0, z); B.add(g); add(new THREE.CylinderGeometry(0.1 * s, 0.17 * s, 1.7 * s, 12), M(0x6b4a30, 0.9), 0, 0.85 * s, 0, g);
    for (let i = 0; i < 7; i++) { const a = r() * PI * 2, d = r() * 0.55 * s; add(new THREE.SphereGeometry((0.55 + r() * 0.35) * s, 20, 14), M(verdes[Math.floor(r() * verdes.length)], 0.92), Math.cos(a) * d, (1.9 + r() * 0.7) * s, Math.sin(a) * d, g); }
    return g; };
  U.arboles = [[-5.5, -3, 1.4], [5.8, -3.6, 1.5], [-7.5, 2.5, 1.6], [7.2, 2.0, 1.3], [-3.8, -9.5, 1.7], [4.5, -10, 1.8], [-10, -6, 1.9], [10, -7, 1.7], [-9, 7, 1.5], [9, 8, 1.6], [0, -13, 2.0], [-13, 0, 2], [13, -1, 2]].map(([x, z, s]) => arbol(x, z, s));
  // guirnaldas de luces entre los árboles (bombillos cálidos)
  U.bombillos = []; const guirnalda = (a, b, n, cuelga) => { for (let i = 0; i <= n; i++) { const k = i / n, x = a[0] + (b[0] - a[0]) * k, z = a[2] + (b[2] - a[2]) * k, y = a[1] + (b[1] - a[1]) * k - Math.sin(k * PI) * cuelga;
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: blanda, color: 0xffd9a0, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); s.position.set(x, y, z); s.scale.setScalar(0.32); B.add(s); U.bombillos.push(s);
    add(new THREE.SphereGeometry(0.03, 8, 6), new THREE.MeshBasicMaterial({ color: 0xfff1c8 }), x, y, z).castShadow = false; } };
  guirnalda([-5.5, 3.2, -3], [5.8, 3.3, -3.6], 26, 0.7); guirnalda([-7.5, 3.3, 2.5], [5.8, 3.3, -3.6], 28, 0.8); guirnalda([7.2, 3.1, 2.0], [-5.5, 3.2, -3], 28, 0.8);
  // mesa principal redonda con mantel, centro de flores, platos y copas
  const mantel = M(0xf7f3ec, 0.85); add(new THREE.CylinderGeometry(0.95, 1.08, 0.74, 48), mantel, 0, 0.37, 0); add(new THREE.CylinderGeometry(0.97, 0.97, 0.02, 48), mantel, 0, 0.75, 0);
  add(new THREE.CylinderGeometry(0.08, 0.06, 0.18, 16), M(0xe9e2d6, 0.2, { transparent: true, opacity: 0.6 }), 0, 0.85, 0);
  const flores = [0xf2a7b8, 0xffffff, 0xf7d36b, 0xe86f8a, 0xf6c6d6];
  for (let i = 0; i < 16; i++) { const a = r() * PI * 2, d = r() * 0.12; add(new THREE.SphereGeometry(0.045 + r() * 0.025, 12, 10), M(flores[i % flores.length], 0.7), Math.cos(a) * d, 0.97 + r() * 0.08, Math.sin(a) * d); }
  for (let i = 0; i < 6; i++) { const a = (i / 6) * PI * 2 + 0.3; add(new THREE.CylinderGeometry(0.13, 0.11, 0.012, 28), M(0xffffff, 0.3), Math.sin(a) * 0.68, 0.765, Math.cos(a) * 0.68);
    add(new THREE.CylinderGeometry(0.025, 0.012, 0.12, 12), M(0xe6f2ff, 0.05, { transparent: true, opacity: 0.45 }), Math.sin(a) * 0.55 + 0.12, 0.83, Math.cos(a) * 0.55); }
  // sillas blancas alrededor de la mesa principal
  const silla = (x, z, rot) => { const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = rot; B.add(g); const m = M(0xfafafa, 0.45);
    add(new THREE.BoxGeometry(0.46, 0.05, 0.44), m, 0, 0.47, 0, g); add(new THREE.BoxGeometry(0.46, 0.5, 0.04), m, 0, 0.74, -0.21, g); [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([a, b]) => add(new THREE.CylinderGeometry(0.018, 0.018, 0.46, 8), m, a * 0.2, 0.23, b * 0.19, g)); };
  U.sillas = []; for (let i = 0; i < 6; i++) { const a = (i / 6) * PI * 2 + 0.3; silla(Math.sin(a) * 1.3, Math.cos(a) * 1.3, a + PI); }
  // otras mesas del banquete (fondo)
  [[-3.4, -2.6], [3.0, 2.8], [-3.2, 3.0]].forEach(([x, z]) => { add(new THREE.CylinderGeometry(0.85, 0.98, 0.74, 40), mantel, x, 0.37, z); add(new THREE.CylinderGeometry(0.87, 0.87, 0.02, 40), mantel, x, 0.75, z);
    for (let i = 0; i < 8; i++) add(new THREE.SphereGeometry(0.05, 10, 8), M(flores[i % 5], 0.7), x + (r() - 0.5) * 0.2, 0.86 + r() * 0.06, z + (r() - 0.5) * 0.2); });
  // bufé del chef: mesa larga con bandejas tapadas
  add(new THREE.BoxGeometry(2.2, 0.76, 0.7), mantel, 3.4, 0.38, -1.6); [-0.7, 0, 0.7].forEach((dx) => { add(new THREE.CylinderGeometry(0.22, 0.22, 0.04, 24), M(0xc9ccd2, 0.25, { metalness: 0.9 }), 3.4 + dx, 0.8, -1.6);
    add(new THREE.SphereGeometry(0.21, 24, 12, 0, PI * 2, 0, PI / 2), M(0xd8dbe0, 0.2, { metalness: 0.95 }), 3.4 + dx, 0.81, -1.6); });
  // torta de tres pisos
  [[0.32, 0.22, 0], [0.24, 0.2, 0.22], [0.16, 0.18, 0.42]].forEach(([rr, h, y]) => add(new THREE.CylinderGeometry(rr, rr, h, 40), M(0xfff8ee, 0.55), -2.2, 0.86 + y + h / 2, -1.0));
  add(new THREE.CylinderGeometry(0.42, 0.42, 0.75, 32), mantel, -2.2, 0.375, -1.0); for (let i = 0; i < 10; i++) add(new THREE.SphereGeometry(0.035, 10, 8), M(flores[i % 5], 0.7), -2.2 + Math.cos(i) * 0.26, 1.08 + (i % 3) * 0.21, -1.0 + Math.sin(i) * 0.26);
  // arco de flores y sillas de la ceremonia al fondo
  const arco = add(new THREE.TorusGeometry(1.5, 0.07, 12, 40, PI), M(0xf4efe6, 0.6), 0, 0, -7.5);
  for (let i = 0; i < 60; i++) { const a = r() * PI, rr = 1.5 + (r() - 0.5) * 0.18; add(new THREE.SphereGeometry(0.09 + r() * 0.07, 12, 10), M(i % 4 ? flores[i % 5] : 0x6fae4a, 0.75), Math.cos(a) * rr, Math.sin(a) * rr, -7.5 + (r() - 0.5) * 0.2); }
  for (let f = 0; f < 4; f++) for (const lado of [-1, 1]) for (let k = 0; k < 3; k++) silla(lado * (0.9 + k * 0.55), -5.6 + f * 0.75, PI);
  // flores sueltas en el pasto
  for (let i = 0; i < 160; i++) { const a = r() * PI * 2, d = 4 + r() * 14; const f = add(new THREE.SphereGeometry(0.035, 6, 5), M(flores[i % 5], 0.8), Math.cos(a) * d, 0.04, Math.sin(a) * d); f.castShadow = false; }
  // polen y pelusas que flotan en la luz
  const n = 240, pp = new Float32Array(n * 3); U.motas = []; for (let i = 0; i < n; i++) U.motas.push([(r() - 0.5) * 14, 0.4 + r() * 3.2, (r() - 0.5) * 14, r() * 10]);
  const pg = new THREE.BufferGeometry(); pg.setAttribute("position", new THREE.BufferAttribute(pp, 3));
  U.polvo = new THREE.Points(pg, new THREE.PointsMaterial({ color: 0xfff1cc, size: 0.035, transparent: true, opacity: 0.8, depthWrite: false, blending: THREE.AdditiveBlending })); B.add(U.polvo);
  B.userData = U;
  U.paso = (tt) => {
    U.bombillos.forEach((s, i) => { s.material.opacity = 0.55 + 0.35 * Math.sin(tt * 2.5 + i * 0.7); });
    const p = U.polvo.geometry.attributes.position; U.motas.forEach(([x, y, z, f], i) => p.setXYZ(i, x + Math.sin(tt * 0.3 + f) * 0.4, y + Math.sin(tt * 0.5 + f * 1.3) * 0.15, z + Math.cos(tt * 0.25 + f) * 0.4)); p.needsUpdate = true;
    U.arboles.forEach((g, i) => { g.rotation.z = Math.sin(tt * 0.8 + i) * 0.008; });
  };
  return B;
}
