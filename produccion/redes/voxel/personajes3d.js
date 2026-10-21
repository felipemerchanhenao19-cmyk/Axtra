// «Turno de noche»: personajes de bloques (voxel) en 3D real con three.js.
// Cara dibujada en una textura de píxeles (ojos, cejas, boca que habla con la voz real), nariz en relieve,
// brazos y piernas con pivotes para gestos. Orbi (el asistente de Apex) es la esfera con la cara nueva de la app.
const PI = Math.PI;
function semilla(s) { return () => { s |= 0; s = (s + 0x6d2b79f5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const lerp = (a, b, k) => a + (b - a) * k, cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), suave = (x) => { x = cl(x); return x * x * (3 - 2 * x); };
// Textura de ruido compartida: da el aspecto de bloque con tela/madera de los videos voxel
const RUIDO = (() => { const c = document.createElement("canvas"); c.width = c.height = 16; const g = c.getContext("2d"), r = semilla(7);
  for (let i = 0; i < 256; i++) { const v = 205 + Math.floor(r() * 50); g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(i % 16, Math.floor(i / 16), 1, 1); }
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.colorSpace = THREE.SRGBColorSpace; return t; })();
function mat(color, o = {}) {
  return new THREE.MeshStandardMaterial({ color, map: o.liso ? null : RUIDO, roughness: o.r ?? 0.85, metalness: o.m ?? 0, emissive: o.e ?? 0, emissiveIntensity: o.ei ?? 1,
    transparent: o.op !== undefined, opacity: o.op ?? 1 });
}
function caja(w, h, d, m, x = 0, y = 0, z = 0, padre = null, sombra = true) {
  const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m && (m.isMaterial || Array.isArray(m)) ? m : mat(m));
  b.position.set(x, y, z); b.castShadow = sombra; b.receiveShadow = true; if (padre) padre.add(b); return b;
}
function pivote(x, y, z, padre) { const g = new THREE.Group(); g.position.set(x, y, z); padre.add(g); return g; }

// ---------- Cara de píxeles (64×64)
const EMOS = {   // cejas: [alto, inclinación], ojos: alto, párpado (0 abierto, 1 cerrado), boca: curva (+ sonrisa, − tristeza)
  neutro: { ceja: [0, 0], ojo: 8, lid: 0, curva: 0 }, serio: { ceja: [1, 0.22], ojo: 7, lid: 0.15, curva: -0.3 },
  sorpresa: { ceja: [-4, -0.05], ojo: 10, lid: 0, curva: 0 }, cansado: { ceja: [1, -0.1], ojo: 8, lid: 0.55, curva: -0.2 },
  cerrados: { ceja: [1, 0], ojo: 8, lid: 1, curva: 0 }, feliz: { ceja: [-2, 0], ojo: 8, lid: 0.1, curva: 1 },
  triste: { ceja: [-1, -0.3], ojo: 8, lid: 0.25, curva: -1 }, duda: { ceja: [-1, 0.15], ojo: 8, lid: 0, curva: -0.2, asim: true },
};
function dibujarCaraVoxel(g, c, s) {
  const e = EMOS[s.emo] || EMOS.neutro, e2 = EMOS[s.emo2] || e, k = s.mezcla ?? 1;
  const mix = (a, b) => lerp(a, b, k), ceja = [mix(e2.ceja[0], e.ceja[0]), mix(e2.ceja[1], e.ceja[1])];
  const lid = s.parpadeo ? 1 : mix(e2.lid, e.lid), ojo = mix(e2.ojo, e.ojo), curva = mix(e2.curva, e.curva) + (s.sonrisa || 0);
  g.fillStyle = c.piel; g.fillRect(0, 0, 64, 64);
  g.fillStyle = c.sombraPiel; g.fillRect(0, 52, 64, 12); g.fillRect(0, 0, 3, 64); g.fillRect(61, 0, 3, 64);
  [-1, 1].forEach((d) => {
    const ex = 32 + d * 12, ey = 29;
    if (lid < 0.95) {
      g.fillStyle = "#f4f1ea"; g.fillRect(ex - 5, ey - ojo / 2, 10, ojo);
      g.fillStyle = c.iris || "#1c2430"; const px = Math.round(ex - 2 + (s.mx || 0) * 2.5), py = Math.round(ey - 3 + (s.my || 0) * 1.5); g.fillRect(px, py, 4, 6);
      g.fillStyle = "rgba(255,255,255,.85)"; g.fillRect(px + 2, py + 1, 1, 1);
      if (lid > 0.02) { g.fillStyle = c.piel; g.fillRect(ex - 6, ey - ojo / 2 - 1, 12, Math.round((ojo + 1) * lid)); g.fillStyle = c.sombraPiel; g.fillRect(ex - 5, ey - ojo / 2 - 1 + Math.round((ojo + 1) * lid), 10, 1); }
    } else { g.fillStyle = c.cejas; g.fillRect(ex - 5, ey, 10, 2); }
    // cejas inclinadas
    const inc = (e.asim && d > 0 ? -1.6 : 1) * ceja[1] * d, by = 19 + ceja[0] + (e.asim && d > 0 ? -2 : 0);
    g.save(); g.translate(ex, by); g.rotate(inc); g.fillStyle = c.cejas; g.fillRect(-6, -1.5, 12, 3); g.restore();
    if (c.gafas) { g.strokeStyle = c.gafas; g.lineWidth = 1.6; g.strokeRect(ex - 7, ey - 6, 14, 12); }
  });
  if (c.gafas) { g.fillStyle = c.gafas; g.fillRect(29, 26, 6, 1.6); }
  // boca: abre con la voz real; la curva da sonrisa o tristeza
  const ab = cl(s.voz || 0), w = 16 + Math.round(ab * 2), mx = 32, my = 46;
  if (ab > 0.06) {
    const h = 2 + Math.round(ab * 7);
    g.fillStyle = "#3a1212"; g.fillRect(mx - w / 2, my - 1, w, h);
    g.fillStyle = "#e9e4da"; g.fillRect(mx - w / 2 + 2, my - 1, w - 4, 1.5);
    g.fillStyle = "#b8505a"; if (h > 4) g.fillRect(mx - 4, my + h - 3, 8, 2);
  } else {
    g.fillStyle = c.labios || "#8a2f2a"; g.fillRect(mx - w / 2, my, w, 2);
    if (curva > 0.3) { g.fillRect(mx - w / 2 - 2, my - 2, 3, 2); g.fillRect(mx + w / 2 - 1, my - 2, 3, 2); }
    if (curva < -0.4) { g.fillRect(mx - w / 2 - 2, my + 2, 3, 2); g.fillRect(mx + w / 2 - 1, my + 2, 3, 2); }
  }
}

// ---------- Persona de bloques
function persona(cfg) {
  const c = Object.assign({ piel: "#c98d6b", sombraPiel: "#b47a5a", pelo: "#2b1d16", cejas: "#2b1d16", camisa: "#e7e1d6", pantalon: "#2c3442", zapatos: "#1a1a1a", alto: 1 }, cfg);
  const raiz = new THREE.Group(), cuerpo = pivote(0, 0, 0, raiz); raiz.scale.setScalar(c.alto);
  const mPiel = mat(c.piel), mCamisa = mat(c.camisa), mPant = mat(c.pantalon), mPelo = mat(c.pelo);
  // piernas
  const piernas = [-1, 1].map((d) => { const p = pivote(d * 0.11, 0.78, 0, cuerpo); caja(0.18, 0.66, 0.21, mPant, 0, -0.33, 0, p); caja(0.19, 0.12, 0.27, mat(c.zapatos), 0, -0.72, 0.03, p); return p; });
  // torso
  const torso = pivote(0, 0.78, 0, cuerpo);
  caja(0.52, 0.64, 0.29, mCamisa, 0, 0.32, 0, torso);
  if (c.delantal) caja(0.46, 0.78, 0.02, mat(c.delantal), 0, 0.2, 0.155, torso);
  if (c.chaleco) { caja(0.17, 0.6, 0.3, mat(c.chaleco), -0.18, 0.33, 0, torso); caja(0.17, 0.6, 0.3, mat(c.chaleco), 0.18, 0.33, 0, torso); }
  if (c.saco) { caja(0.55, 0.62, 0.31, mat(c.saco), 0, 0.33, -0.005, torso); caja(0.14, 0.4, 0.02, mCamisa, 0, 0.45, 0.16, torso); }
  if (c.corbatin) { caja(0.14, 0.07, 0.04, mat(c.corbatin), 0, 0.6, 0.16, torso); }
  if (c.cadena) caja(0.2, 0.03, 0.02, mat("#c9a24a", { r: 0.3, m: 0.8 }), 0, 0.56, 0.16, torso);
  // brazos (pivote en el hombro) con mano
  const brazos = [-1, 1].map((d) => { const p = pivote(d * 0.345, 0.6, 0, torso); const manga = c.saco || c.camisa;
    caja(0.16, 0.42, 0.19, mat(manga), 0, -0.2, 0, p); caja(0.15, 0.2, 0.18, c.mangaCorta ? mPiel : mat(manga), 0, -0.5, 0, p); caja(0.14, 0.13, 0.17, mPiel, 0, -0.66, 0, p); return p; });
  // cabeza: cara en textura de píxeles
  const cuello = pivote(0, 0.64, 0, torso); caja(0.2, 0.08, 0.2, mPiel, 0, 0.03, 0, cuello);
  const cabeza = pivote(0, 0.07, 0, cuello);
  const lienzo = document.createElement("canvas"); lienzo.width = lienzo.height = 64; const g2 = lienzo.getContext("2d");
  const texCara = new THREE.CanvasTexture(lienzo); texCara.magFilter = THREE.NearestFilter; texCara.minFilter = THREE.LinearFilter; texCara.colorSpace = THREE.SRGBColorSpace;
  const mCara = new THREE.MeshStandardMaterial({ map: texCara, roughness: 0.85 });
  caja(0.52, 0.52, 0.48, [mPiel, mPiel, mPiel, mPiel, mCara, mPiel], 0, 0.26, 0, cabeza);
  caja(0.08, 0.09, 0.05, mPiel, 0, 0.22, 0.265, cabeza);   // nariz
  if (c.bigote) caja(0.24, 0.04, 0.03, mat(c.bigote), 0, 0.15, 0.25, cabeza);
  // pelo / gorra / coleta
  if (c.calvo) { caja(0.54, 0.16, 0.5, mPelo, 0, 0.36, -0.03, cabeza).scale.set(1, 1, 0.3); }
  else if (c.peinado !== "ninguno") { caja(0.55, 0.1, 0.51, mPelo, 0, 0.55, 0, cabeza); caja(0.55, 0.42, 0.08, mPelo, 0, 0.32, -0.23, cabeza);
    caja(0.04, 0.22, 0.4, mPelo, -0.275, 0.42, -0.03, cabeza); caja(0.04, 0.22, 0.4, mPelo, 0.275, 0.42, -0.03, cabeza);
    if (c.peinado === "copete") caja(0.4, 0.08, 0.2, mPelo, 0, 0.62, 0.12, cabeza);
    if (c.peinado === "largo") { caja(0.55, 0.62, 0.1, mPelo, 0, 0.2, -0.26, cabeza); caja(0.06, 0.5, 0.2, mPelo, -0.28, 0.2, -0.12, cabeza); caja(0.06, 0.5, 0.2, mPelo, 0.28, 0.2, -0.12, cabeza); }
    if (c.peinado === "moño") caja(0.22, 0.2, 0.2, mPelo, 0, 0.6, -0.22, cabeza);
    if (c.peinado === "flequillo") caja(0.5, 0.08, 0.05, mPelo, 0, 0.5, 0.245, cabeza); }
  if (c.gorra) { caja(0.57, 0.15, 0.53, mat(c.gorra), 0, 0.57, 0, cabeza); caja(0.5, 0.03, 0.2, mat(c.gorra), 0, 0.51, c.gorraAtras ? -0.34 : 0.34, cabeza); }
  if (c.gorroChef) { caja(0.54, 0.1, 0.5, mat("#f2efe8"), 0, 0.56, 0, cabeza); caja(0.46, 0.3, 0.44, mat("#f2efe8"), 0, 0.76, 0, cabeza); }
  // objetos en la mano derecha
  const mano = pivote(0, -0.72, 0.05, brazos[1]), objetos = {};
  objetos.vaso = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.04, 0.14, 12), new THREE.MeshStandardMaterial({ color: 0xdfefff, roughness: 0.05, metalness: 0.1, transparent: true, opacity: 0.55 }));
  objetos.trapo = caja(0.12, 0.02, 0.16, mat("#d8d2c4"), 0.02, -0.02, 0.1, null);
  objetos.celular = caja(0.08, 0.15, 0.015, mat("#11161d", { r: 0.3 }), 0, 0, 0.1, null);
  const pant = new THREE.Mesh(new THREE.PlaneGeometry(0.07, 0.13), new THREE.MeshBasicMaterial({ color: 0x9fe6ff })); pant.position.z = 0.009; objetos.celular.add(pant);
  objetos.tinto = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.04, 0.09, 12), mat("#f2efe8"));
  objetos.vaso.position.set(0, -0.02, 0.06); objetos.tinto.position.set(0, 0, 0.06);
  Object.values(objetos).forEach((o) => { o.visible = false; o.castShadow = true; mano.add(o); });
  const r = semilla(c.semilla || 3), fase = r() * 10;
  return { raiz, cuerpo, torso, piernas, brazos, cuello, cabeza, objetos, c, fase,
    cara(s) { dibujarCaraVoxel(g2, c, s); texCara.needsUpdate = true; } };
}

// ---------- Gestos: ángulos de brazos [hombro X, hombro Z] izquierdo y derecho, inclinación de torso, piernas
const GESTOS = {
  reposo: { bi: [0.05, -0.08], bd: [0.05, 0.08] },
  vaso: { bi: [-0.95, -0.35], bd: [-1.15, 0.3], obj: "vaso" },
  trapo: { bi: [-0.95, -0.35], bd: [-1.15, 0.3], obj: "vaso" },
  baja: { bi: [-0.4, -0.1], bd: [-0.55, 0.1], obj: "vaso" },
  señala: { bi: [0.05, -0.08], bd: [-1.45, -0.1] },
  hombro: { bi: [0.05, -0.08], bd: [-1.25, -0.35] },
  cabeza: { bi: [-2.7, -0.55], bd: [-2.7, 0.55], torso: 0.08 },
  cruzado: { bi: [-1.2, 0.75], bd: [-1.25, -0.75] },
  cadera: { bi: [0.1, -0.6], bd: [0.1, 0.6] },
  explica: { bi: [-0.7, -0.2], bd: [-0.9, 0.25] },
  celular: { bi: [0.05, -0.08], bd: [-1.35, -0.25], obj: "celular" },
  tinto: { bi: [0.05, -0.08], bd: [-1.6, -0.2], obj: "tinto" },
  manos_mesa: { bi: [-1.1, -0.1], bd: [-1.1, 0.1], torso: 0.12 },
  rendido: { bi: [0.15, -0.15], bd: [0.15, 0.15], torso: 0.18 },
  mano_arriba: { bi: [-0.9, -0.1], bd: [-2.9, -0.15] },
  teclea: { bi: [-1.0, -0.15], bd: [-1.0, 0.15], torso: 0.1 },
};

function animarPersona(P, s, t) {
  // s: {x, z, rot, gesto, gesto2, mezclaG, camina (velocidad), sentado, voz, emo, emo2, mezcla, mira (yaw relativo), miraY, parpadeo...}
  const { raiz, piernas, brazos, torso, cuello, cabeza, objetos } = P, f = P.fase;
  raiz.position.set(s.x, s.y || 0, s.z); raiz.rotation.y = s.rot || 0;
  const G1 = GESTOS[s.gesto] || GESTOS.reposo, G0 = GESTOS[s.gesto2] || G1, k = s.mezclaG ?? 1, m = (a, b) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k)];
  let bi = m(G0.bi, G1.bi), bd = m(G0.bd, G1.bd);
  const respira = Math.sin(t * 1.9 + f) * 0.012, habla = s.voz || 0;
  // al hablar, las manos acompañan
  if (habla > 0.05 && !G1.obj && s.gesto !== "cabeza") { bd = [bd[0] - 0.25 * Math.max(0, Math.sin(t * 3.1 + f)) * (s.manos ?? 1), bd[1]]; bi = [bi[0] - 0.12 * Math.max(0, Math.sin(t * 2.3 + f + 1)) * (s.manos ?? 1), bi[1]]; }
  if (s.gesto === "trapo") { bd = [bd[0] + 0.12 * Math.sin(t * 5), bd[1] + 0.08 * Math.cos(t * 5)]; }
  if (s.gesto === "teclea") { bi = [bi[0] + 0.06 * Math.sin(t * 13), bi[1]]; bd = [bd[0] + 0.06 * Math.sin(t * 11 + 1), bd[1]]; }
  brazos[0].rotation.set(bi[0] + respira, 0, bi[1]); brazos[1].rotation.set(bd[0] + respira, 0, bd[1]);
  Object.entries(objetos).forEach(([n, o]) => { o.visible = (G1.obj === n && k > 0.4) || (G0.obj === n && k <= 0.4) || (n === "trapo" && s.gesto === "trapo"); });
  // caminar
  const v = s.camina || 0, paso = Math.sin(t * 9 + f) * Math.min(0.55, v * 0.45);
  if (s.sentado) { piernas.forEach((p) => p.rotation.set(-1.45, 0, 0)); P.cuerpo.position.y = -0.33; }
  else { piernas[0].rotation.set(paso, 0, 0); piernas[1].rotation.set(-paso, 0, 0); P.cuerpo.position.y = Math.abs(Math.sin(t * 9 + f)) * Math.min(0.05, v * 0.04); }
  if (v > 0.05) { brazos[0].rotation.x = -paso * 0.8; brazos[1].rotation.x = G1.obj ? bd[0] : paso * 0.8; }
  torso.rotation.x = lerp(G0.torso || 0, G1.torso || 0, k) + (v > 0.05 ? 0.08 : 0) + (s.inclina || 0);
  torso.scale.y = 1 + respira * 0.6;
  // cabeza: mira, asiente al hablar
  cuello.rotation.y = cl(s.mira || 0, -1.1, 1.1);
  cuello.rotation.x = (s.miraY || 0) + habla * 0.05 * Math.sin(t * 7 + f) + Math.sin(t * 0.7 + f) * 0.015;
  cuello.rotation.z = Math.sin(t * 0.5 + f) * 0.02 + (s.ladea || 0);
  const mx = Math.sin(t * 0.45 + f) * 0.3 + (s.ojosX || 0), parp = ((t + f) % (3.2 + (f % 1.5))) < 0.12;
  P.cara({ emo: s.emo, emo2: s.emo2, mezcla: s.mezcla, voz: habla, parpadeo: parp && s.emo !== "cerrados", mx, my: s.ojosY || 0, sonrisa: s.sonrisa });
}

// ---------- Orbi en 3D: esfera con la cara nueva (textura equirectangular), anillo inclinado bajo la cara, halo y luz propia
function texturaRadial(colorCentro, colorBorde) {
  const c = document.createElement("canvas"); c.width = c.height = 128; const g = c.getContext("2d"), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, colorCentro); gr.addColorStop(1, colorBorde); g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
function orbi3d(r = 0.2) {
  const raiz = new THREE.Group(), cuerpo = new THREE.Group(); raiz.add(cuerpo);
  const lienzo = document.createElement("canvas"); lienzo.width = 1024; lienzo.height = 512; const g = lienzo.getContext("2d");
  const tex = new THREE.CanvasTexture(lienzo); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  const esfera = new THREE.Mesh(new THREE.SphereGeometry(r, 48, 32), new THREE.MeshStandardMaterial({ map: tex, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: 0.75, roughness: 0.22, metalness: 0.05 }));
  cuerpo.add(esfera);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: texturaRadial("rgba(90,215,255,0.55)", "rgba(40,160,255,0)"), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true }));
  halo.scale.setScalar(r * 5.5); raiz.add(halo);
  const anillo = new THREE.Group(); anillo.position.y = -r * 0.38; cuerpo.add(anillo);
  const aro = new THREE.Mesh(new THREE.TorusGeometry(r * 1.32, r * 0.022, 8, 96), new THREE.MeshBasicMaterial({ color: 0x8be9ff, transparent: true, opacity: 0.85 }));
  aro.scale.set(1, 1, 1); aro.rotation.x = PI / 2; anillo.add(aro); anillo.rotation.set(0.32, 0, -0.22);
  const punto = new THREE.Mesh(new THREE.SphereGeometry(r * 0.06, 12, 8), new THREE.MeshBasicMaterial({ color: 0xe8fbff })); anillo.add(punto);
  const luz = new THREE.PointLight(0x5fd4ff, 1.2, 3.5, 2); raiz.add(luz);
  const chispas = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ color: 0xbff6ff, size: 0.025, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
  const rr = semilla(11), N = 60, base = []; for (let i = 0; i < N; i++) base.push([rr() * PI * 2, rr() * PI, 1 + rr() * 6]);
  chispas.geometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 3), 3)); raiz.add(chispas);
  // la cara: mismo dibujo que la app (dibujarOrbe/dibujarCara), centrada en el frente de la esfera (u = 0.25)
  const CX = 256, CY = 256, R = 163 * 0.98;
  function pintar(t, estado, extra) {
    const gr = g.createLinearGradient(0, 0, 0, 512);
    gr.addColorStop(0, "#bff3ff"); gr.addColorStop(0.32, "#5fd0ff"); gr.addColorStop(0.55, "#2a9fe0"); gr.addColorStop(0.8, "#0b3d91"); gr.addColorStop(1, "#061a3d");
    g.fillStyle = gr; g.fillRect(0, 0, 1024, 512);
    const piensa = estado === "piensa", oye = estado === "escucha", habla = estado === "habla";
    const parpadeo = (t % 3.7) < 0.13 && !piensa, ap = parpadeo ? 0.1 : oye ? 1.15 : 1;
    const mx = piensa ? R * 0.06 : Math.sin(t * 0.55) * R * 0.05, my = piensa ? -R * 0.07 : Math.sin(t * 0.37) * R * 0.02;
    const ey = CY - R * 0.1, sep = R * 0.33;
    [-1, 1].forEach((s) => {
      const ex = CX + s * sep;
      g.fillStyle = "#f4fbff"; g.beginPath(); g.ellipse(ex, ey, R * 0.14, R * 0.2 * ap, 0, 0, PI * 2); g.fill();
      if (ap > 0.3) { g.fillStyle = "#071a33"; g.beginPath(); g.ellipse(ex + mx, ey + my + R * 0.02, R * 0.075, R * 0.1 * Math.min(1, ap), 0, 0, PI * 2); g.fill();
        g.fillStyle = "#fff"; g.beginPath(); g.arc(ex + mx + R * 0.03, ey + my - R * 0.03, R * 0.028, 0, PI * 2); g.fill(); }
      const alza = oye ? R * 0.07 : piensa && s > 0 ? R * 0.09 : 0, inc = piensa ? s * 0.18 : oye ? -s * 0.08 : 0;
      g.save(); g.translate(ex, ey - R * 0.3 - alza); g.rotate(inc); g.strokeStyle = "#06244f"; g.lineWidth = R * 0.06; g.lineCap = "round";
      g.beginPath(); g.moveTo(-R * 0.13, R * 0.02); g.quadraticCurveTo(0, -R * 0.04, R * 0.13, R * 0.02); g.stroke(); g.restore();
    });
    const by = CY + R * 0.3; g.lineCap = "round";
    if (habla && extra > 0.04) {
      const alto = R * (0.06 + 0.1 * Math.min(1, extra * 1.6));
      g.fillStyle = "#071a33"; g.beginPath(); g.moveTo(CX - R * 0.21, by - R * 0.03); g.quadraticCurveTo(CX, by + R * 0.01, CX + R * 0.21, by - R * 0.03);
      g.quadraticCurveTo(CX, by + alto * 2.1, CX - R * 0.21, by - R * 0.03); g.fill();
      g.save(); g.clip(); g.fillStyle = "#ff7b8a"; g.beginPath(); g.ellipse(CX, by + alto * 1.2, R * 0.09, alto * 0.5, 0, 0, PI * 2); g.fill(); g.restore();
    } else if (piensa) { g.strokeStyle = "#071a33"; g.lineWidth = R * 0.055; g.beginPath(); g.moveTo(CX - R * 0.1, by + R * 0.02); g.lineTo(CX + R * 0.12, by - R * 0.02); g.stroke(); }
    else if (oye) { g.fillStyle = "#071a33"; g.beginPath(); g.ellipse(CX, by, R * 0.07, R * 0.08, 0, 0, PI * 2); g.fill(); }
    else { g.strokeStyle = "#071a33"; g.lineWidth = R * 0.055; g.beginPath(); g.moveTo(CX - R * 0.2, by - R * 0.02); g.quadraticCurveTo(CX, by + R * 0.16, CX + R * 0.2, by - R * 0.02); g.stroke(); }
    tex.needsUpdate = true;
  }
  return { raiz, cuerpo, r,
    animar(s, t) {   // s: {x,y,z, rot, nace 0..1, estado, voz}
      const nace = s.nace ?? 1, extra = s.estado === "habla" ? (s.voz || 0) : s.estado === "escucha" ? 0.3 : 0;
      raiz.visible = nace > 0.001; raiz.position.set(s.x, s.y + Math.sin(t * 1.6 + (s.fase || 0)) * 0.03, s.z);
      cuerpo.rotation.y = s.rot || 0; const k = (0.2 + 0.8 * suave(nace)) * (1 + 0.035 * Math.sin(t * 1.8) + extra * 0.1); cuerpo.scale.setScalar(k);
      esfera.material.opacity = 1; halo.material.opacity = (0.6 + extra * 0.5) * nace; luz.intensity = (1.0 + extra * 1.2) * nace * (s.luz ?? 1);
      anillo.rotation.z = -0.22 + 0.06 * Math.sin(t * 1.3);
      const giro = s.estado === "piensa" ? 2.6 : 0.9, a = t * giro; punto.position.set(Math.cos(a) * r * 1.32, 0, Math.sin(a) * r * 1.32);
      const pos = chispas.geometry.attributes.position; chispas.visible = nace < 1;
      base.forEach(([a1, a2, d], i) => { const dd = r * (1 + d * (1 - nace)); pos.setXYZ(i, Math.cos(a1 + t) * Math.sin(a2) * dd, Math.cos(a2) * dd, Math.sin(a1 + t) * Math.sin(a2) * dd); });
      pos.needsUpdate = true; chispas.material.opacity = nace;
      pintar(t, s.estado || "reposo", extra);
    } };
}
