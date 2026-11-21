// «Vinil»: personajes 3D redondeados tipo juguete de vinil (cabeza grande, pelo esculpido, cejas gruesas, ojos con brillo).
// Mismo esqueleto que persona() (piernas, brazos, torso, cuello, cabeza, objetos), así animarPersona() y las cámaras funcionan igual.
var VINIL = typeof EP !== "undefined" && EP.estilo === "vinil";
var LISO = VINIL;   // escenarios sin textura de píxeles

const VIN = {};
VIN.mat = (col, o = {}) => new THREE.MeshStandardMaterial({ color: col, roughness: o.r ?? 0.58, metalness: o.m ?? 0, bumpMap: o.bump || null, bumpScale: o.bs ?? 0.6,
  emissive: o.e ?? 0, emissiveIntensity: o.ei ?? 1, transparent: o.op !== undefined, opacity: o.op ?? 1, side: o.lado || THREE.FrontSide });
VIN.surcos = (() => { const c = document.createElement("canvas"); c.width = 512; c.height = 64; const g = c.getContext("2d");
  for (let x = 0; x < 512; x++) { const v = 128 + 110 * Math.pow(Math.abs(Math.sin(x * PI / 16)), 0.6) * (Math.sin(x * 0.013) * 0.15 + 0.85); g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(x, 0, 1, 64); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t; })();
VIN.malla = (geo, m, x = 0, y = 0, z = 0, padre = null) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = true; o.receiveShadow = true; if (padre) padre.add(o); return o; };
VIN.esfera = (r, m, x, y, z, padre, sx = 1, sy = 1, sz = 1, seg = 40) => { const o = VIN.malla(new THREE.SphereGeometry(r, seg, Math.round(seg * 0.75)), m, x, y, z, padre); o.scale.set(sx, sy, sz); return o; };
VIN.capsula = (r, l, m, x, y, z, padre) => VIN.malla(new THREE.CapsuleGeometry(r, l, 10, 24), m, x, y, z, padre);
VIN.torno = (perfil, m, padre, y = 0, sz = 0.74, phi0 = 0, phiL = 2 * PI) => { const o = VIN.malla(new THREE.LatheGeometry(perfil.map(([r, h]) => new THREE.Vector2(r, h)), 48, phi0, phiL), m, 0, y, 0, padre); o.scale.z = sz; return o; };
// perfil del torso: de la cadera a los hombros (radio, alto)
VIN.TORSO = [[0.001, -0.02], [0.2, -0.01], [0.25, 0.08], [0.265, 0.24], [0.255, 0.42], [0.22, 0.55], [0.14, 0.63], [0.075, 0.67], [0.001, 0.68]];
VIN.TORSO_F = [[0.001, -0.02], [0.225, -0.01], [0.255, 0.07], [0.205, 0.25], [0.238, 0.41], [0.215, 0.54], [0.14, 0.63], [0.07, 0.67], [0.001, 0.68]];
VIN.crecer = (perfil, d) => perfil.map(([r, h]) => [r > 0.01 ? r + d : r, h]);

function personaVinil(cfg) {
  const c = Object.assign({ piel: "#d9a27e", pelo: "#2b1d16", cejas: "#1c1410", camisa: "#e7e1d6", pantalon: "#2c3442", zapatos: "#1a1a1a", alto: 1, iris: "#3a2416" }, cfg);
  const raiz = new THREE.Group(), cuerpo = pivote(0, 0, 0, raiz); raiz.scale.setScalar(c.alto);
  const M = VIN.mat, mPiel = M(c.piel, { r: 0.62 }), mCamisa = M(c.camisa, { r: 0.75 }), mPant = M(c.pantalon, { r: 0.7 });
  const mPelo = M(c.pelo, { r: 0.5, bump: VIN.surcos, bs: 1.2 });
  // piernas y zapatos
  const piernas = [-1, 1].map((d) => { const p = pivote(d * 0.12, 0.78, 0, cuerpo); VIN.capsula(0.095, 0.5, mPant, 0, -0.36, 0, p);
    VIN.esfera(0.1, M(c.zapatos, { r: 0.35 }), 0, -0.74, 0.05, p, 1.05, 0.62, 1.5); return p; });
  // torso redondeado (ropa) con prendas encima
  const torso = pivote(0, 0.78, 0, cuerpo);
  const PERFIL = c.torsoF ? VIN.TORSO_F : VIN.TORSO; VIN.torno(PERFIL, mCamisa, torso); if (c.hombros) torso.scale.x = c.hombros;
  if (c.chaleco) { const m = M(c.chaleco, { r: 0.6 }); VIN.torno(VIN.crecer(PERFIL.slice(1, 6), 0.012), m, torso, 0, 0.75, PI * 0.2, PI * 1.6); }
  if (c.saco) { const m = M(c.saco, { r: 0.65 }); VIN.torno(VIN.crecer(PERFIL, 0.018), m, torso, 0, 0.76, PI * 0.14, PI * 1.72); }
  if (c.delantal) { const m = M(c.delantal, { r: 0.8, lado: THREE.DoubleSide }); VIN.torno(VIN.crecer([[0.2, -0.2], [0.26, 0.0], [0.272, 0.2], [0.262, 0.4]], 0.014), m, torso, 0, 0.76, -PI * 0.3, PI * 0.6);
    VIN.capsula(0.012, 0.3, m, -0.12, 0.55, 0.14, torso).rotation.z = 0.35; VIN.capsula(0.012, 0.3, m, 0.12, 0.55, 0.14, torso).rotation.z = -0.35; }
  if (c.corbatin) { const m = M(c.corbatin, { r: 0.4 }); [-1, 1].forEach((d) => VIN.esfera(0.045, m, d * 0.045, 0.63, 0.16, torso, 1.1, 0.75, 0.6)); VIN.esfera(0.022, m, 0, 0.63, 0.175, torso); }
  if (c.corbata) { const m = M(c.corbata, { r: 0.45 }); VIN.capsula(0.032, 0.3, m, 0, 0.42, 0.19, torso).scale.z = 0.4; VIN.esfera(0.04, m, 0, 0.62, 0.18, torso, 1, 0.8, 0.6); }
  if (c.carnet) { const m = M("#e9e4da"); const cd = VIN.malla(new THREE.BoxGeometry(0.09, 0.12, 0.01), m, 0, 0.3, 0.2, torso); cd.rotation.x = -0.12; }
  // brazos: hombro redondo, manga y mano
  const brazos = [-1, 1].map((d) => { const p = pivote(d * 0.3, 0.56, 0, torso); const manga = M(c.saco || c.camisa, { r: 0.72 });
    VIN.esfera(0.1, manga, 0, 0, 0, p); VIN.capsula(0.078, 0.34, manga, 0, -0.24, 0, p);
    if (c.mangaCorta) VIN.capsula(0.07, 0.14, mPiel, 0, -0.42, 0, p);
    VIN.esfera(0.075, mPiel, 0, -0.6, 0.01, p, 0.9, 1.05, 0.8); VIN.esfera(0.03, mPiel, d * -0.05, -0.57, 0.05, p, 1, 1.4, 1); return p; });
  // cuello y cabeza grande
  const cuello = pivote(0, 0.64, 0, torso); VIN.capsula(0.075, 0.06, mPiel, 0, 0.04, 0, cuello);
  const cabeza = pivote(0, 0.07, 0, cuello), H = new THREE.Group(); H.position.set(0, 0.29, 0.01); cabeza.add(H);
  VIN.esfera(0.3, mPiel, 0, 0, 0, H, 1, 1.06, 0.96, 56);
  [-1, 1].forEach((d) => VIN.esfera(0.06, mPiel, d * 0.29, -0.01, -0.02, H, 0.5, 1, 0.85));   // orejas
  // pelo esculpido
  const casquete = (rad, th0, thL, ph0 = 0, phL = 2 * PI) => { const o = VIN.malla(new THREE.SphereGeometry(rad, 48, 24, ph0, phL, th0, thL), mPelo, 0, 0, 0, H); o.scale.set(1, 1.06, 0.98); return o; };
  if (!c.calvo) {
    casquete(0.312, 0, PI * 0.36).rotation.x = -0.32;                    // tapa
    casquete(0.31, 0, PI * 0.62, PI * 0.85, PI * 1.3).rotation.x = -0.05;   // nuca y lados (abierto al frente)
    if (c.peinado === "copete") { const cp = VIN.esfera(0.17, mPelo, 0, 0.24, 0.12, H, 1.35, 0.75, 1.05); cp.rotation.x = -0.35; VIN.esfera(0.12, mPelo, 0, 0.3, -0.02, H, 1.45, 0.6, 1.2); }
    if (c.peinado === "moño") VIN.esfera(0.11, mPelo, 0, 0.2, -0.28, H, 1, 1, 0.9);
    if (c.peinado === "largo") { const l = VIN.malla(new THREE.CylinderGeometry(0.29, 0.31, 0.42, 40, 1, true, PI * 0.62, PI * 0.76), M(c.pelo, { r: 0.5, bump: VIN.surcos, bs: 1.2, lado: THREE.DoubleSide }), 0, -0.2, -0.02, H); }
    if (c.peinado === "flequillo") { const f = VIN.esfera(0.2, mPelo, 0, 0.2, 0.16, H, 1.3, 0.38, 0.8); f.rotation.x = 0.3; }
    if (c.peinado === "ondas") { const mL = M(c.pelo, { r: 0.45, bump: VIN.surcos, bs: 1.2, lado: THREE.DoubleSide });
      VIN.malla(new THREE.CylinderGeometry(0.3, 0.36, 0.62, 40, 1, true, PI * 0.58, PI * 0.84), mL, 0, -0.3, -0.03, H);
      [-1, 1].forEach((d) => { for (let i = 0; i < 4; i++) VIN.esfera(0.085 - i * 0.006, mPelo, d * (0.27 + (i % 2) * 0.03), -0.06 - i * 0.13, -0.02 - i * 0.02, H, 0.8, 1.1, 0.9); });
      const fl = VIN.esfera(0.19, mPelo, -0.08, 0.22, 0.13, H, 1.3, 0.42, 0.85); fl.rotation.set(0.25, 0, 0.35); }
    if (c.peinado === "engominado") { const e2 = VIN.esfera(0.2, mPelo, 0, 0.25, 0.04, H, 1.45, 0.5, 1.4); e2.rotation.x = -0.45; }
    if (c.peinado === "bob") { const mL = M(c.pelo, { r: 0.45, bump: VIN.surcos, bs: 1.2, lado: THREE.DoubleSide });
      VIN.malla(new THREE.CylinderGeometry(0.315, 0.34, 0.34, 40, 1, true, PI * 0.36, PI * 1.28), mL, 0, -0.1, -0.01, H);
      const fl = VIN.esfera(0.2, mPelo, 0.05, 0.21, 0.14, H, 1.35, 0.4, 0.8); fl.rotation.set(0.3, 0, -0.25); }
    if (c.peinado === "rapado") { /* solo el casquete */ }
    if (c.peinado === "normal" || !c.peinado) VIN.esfera(0.16, mPelo, 0.04, 0.24, 0.1, H, 1.4, 0.45, 1.0).rotation.x = -0.2;
  }
  // cara: ojos con párpado, cejas gruesas, nariz, boca y bigote
  const mBlanco = M("#f6f3ee", { r: 0.25 }), mIris = M(c.iris, { r: 0.2 }), mPupila = M("#0b0807", { r: 0.15 }), mBrillo = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const mPar = M(c.piel, { r: 0.62 }), mCeja = M(c.cejas, { r: 0.55 });
  const ojos = [-1, 1].map((d) => { const g = new THREE.Group(); g.position.set(d * 0.108, 0.035, 0.235); H.add(g);
    const bola = new THREE.Group(); g.add(bola); if (c.almendra) g.scale.set(1.12, 0.86, 1); VIN.esfera(0.07, mBlanco, 0, 0, 0, bola, 1, 1.12, 0.8);
    VIN.esfera(0.042, mIris, 0, 0, 0.042, bola, 1, 1.05, 0.5); VIN.esfera(0.022, mPupila, 0, 0, 0.058, bola, 1, 1, 0.4);
    const br = VIN.esfera(0.011, mBrillo, 0.014, 0.018, 0.066, bola); br.castShadow = false;
    const par = VIN.malla(new THREE.SphereGeometry(0.076, 32, 16, 0, 2 * PI, 0, PI / 2), mPar, 0, 0, 0, g); par.scale.set(1.02, 1.14, 1.1);
    const parInf = VIN.malla(new THREE.SphereGeometry(0.075, 32, 16, 0, 2 * PI, PI / 2, PI / 2), mPar, 0, 0, 0, g); parInf.scale.set(1.02, 1.1, 1.1); parInf.rotation.x = 0.5;
    const ceja = VIN.capsula(0.026, 0.09, mCeja, 0, 0.115, 0.03, g); ceja.rotation.z = PI / 2; ceja.scale.set(1, 1, 0.7);
    return { g, bola, par, parInf, ceja, d }; });
  if (c.narizFina) VIN.esfera(0.036, mPiel, 0, -0.04, 0.29, H, 0.8, 1.1, 1.0); else VIN.esfera(0.052, mPiel, 0, -0.045, 0.285, H, 0.85, 1.0, 1.05);   // nariz
  if (c.narizGrande) VIN.esfera(0.068, mPiel, 0, -0.05, 0.285, H, 0.85, 1.05, 1.1);
  const mBoca = M("#3a1414", { r: 0.4 }), boca = VIN.esfera(0.055, mBoca, 0, -0.15, 0.255, H, 1.3, 0.3, 0.45);
  let labioInf = null; const sonrisa = VIN.malla(new THREE.TorusGeometry(0.055, 0.011, 8, 28, PI * 0.62), M("#5a2420", { r: 0.4 }), 0, -0.13, 0.268, H);
  if (c.bigote) { const mb = M(c.bigote, { r: 0.5, bump: VIN.surcos, bs: 0.8 }); [-1, 1].forEach((d) => { const b = VIN.capsula(0.034, 0.1, mb, d * 0.065, -0.1, 0.27, H); b.rotation.z = d * 1.15; b.scale.z = 0.7; }); }
  if (c.bigoteFino) { const b = VIN.capsula(0.01, 0.1, M(c.bigoteFino), 0, -0.098, 0.283, H); b.rotation.z = PI / 2; }
  if (c.gafas) { const mg = M(c.gafas, { r: 0.3 }); ojos.forEach(({ g }) => { const ar = VIN.malla(new THREE.TorusGeometry(0.085, 0.011, 8, 36), mg, 0, 0, 0.045, g); ar.scale.y = 0.85; });
    VIN.capsula(0.008, 0.05, mg, 0, 0.035, 0.29, H).rotation.z = PI / 2; }
  if (c.barba) { const mb = new THREE.MeshStandardMaterial({ color: c.barba, roughness: 0.95, transparent: true, opacity: 0.38, bumpMap: VIN.surcos, bumpScale: 0.5 });
    const bb = VIN.malla(new THREE.SphereGeometry(0.304, 48, 16, PI * 0.1, PI * 0.8, PI * 0.74, PI * 0.2), mb, 0, 0, 0, H); bb.scale.set(1, 1.06, 0.965); bb.castShadow = false; }
  if (c.pestanas) { const mp = M(c.pestanas, { r: 0.35 }); ojos.forEach(({ par, d }) => {   // delineado sobre el párpado y una «colita» hacia afuera
      const arco = VIN.malla(new THREE.TorusGeometry(0.077, 0.0085, 8, 30, PI * 0.95), mp, 0, 0.004, 0, par); arco.rotation.set(PI / 2, 0, PI * 0.025);
      const cola = VIN.capsula(0.007, 0.03, mp, d * 0.078, 0.012, 0.012, par); cola.rotation.set(0, 0, -d * 1.1); }); }
  if (c.labios) { sonrisa.material.color.set(c.labios); sonrisa.geometry = new THREE.TorusGeometry(0.055, 0.016, 10, 28, PI * 0.62);
    labioInf = VIN.esfera(0.04, M(c.labios, { r: 0.35 }), 0, -0.162, 0.262, H, 1.1, 0.42, 0.5); }
  if (c.aretes) [-1, 1].forEach((d) => VIN.esfera(0.022, M(c.aretes, { r: 0.2, m: 0.85 }), d * 0.3, -0.085, 0.0, H));
  if (c.cadena) { const ca = VIN.malla(new THREE.TorusGeometry(0.115, 0.009, 8, 40), M(c.cadena, { r: 0.2, m: 0.9 }), 0, 0.6, 0.06, torso); ca.rotation.x = PI / 2 - 0.5; }
  // objetos en la mano derecha (mismos nombres que persona(), más recibo y bandeja)
  const mano = pivote(0, -0.62, 0.05, brazos[1]), objetos = {};
  objetos.vaso = VIN.malla(new THREE.CylinderGeometry(0.05, 0.04, 0.14, 16), new THREE.MeshStandardMaterial({ color: 0xdfefff, roughness: 0.05, transparent: true, opacity: 0.55 }), 0, -0.02, 0.06);
  objetos.trapo = VIN.malla(new THREE.BoxGeometry(0.12, 0.02, 0.16), M("#d8d2c4", { r: 0.9 }), 0.02, -0.02, 0.1);
  objetos.celular = VIN.malla(new THREE.BoxGeometry(0.08, 0.15, 0.015), M("#11161d", { r: 0.3 }), 0, 0, 0.1);
  const pt = new THREE.Mesh(new THREE.PlaneGeometry(0.07, 0.13), new THREE.MeshBasicMaterial({ color: 0x9fe6ff })); pt.position.z = 0.009; objetos.celular.add(pt);
  objetos.tinto = VIN.malla(new THREE.CylinderGeometry(0.045, 0.04, 0.09, 16), M("#f2efe8"), 0, 0, 0.06);
  // recibo larguísimo: cuelga desde la mano; animarPersona lo endereza y lo desenrolla con «rollo»
  const tr = (() => { const cv = document.createElement("canvas"); cv.width = 128; cv.height = 1024; const g = cv.getContext("2d"); g.fillStyle = "#f3f0e8"; g.fillRect(0, 0, 128, 1024);
    g.fillStyle = "#8a8478"; const r = semilla(9); for (let y = 30; y < 1010; y += 18) g.fillRect(12, y, 40 + r() * 70, 5); return new THREE.CanvasTexture(cv); })();
  const reciboGeo = new THREE.PlaneGeometry(0.13, 1.25, 1, 12); reciboGeo.translate(0, -0.625, 0);
  objetos.recibo = new THREE.Mesh(reciboGeo, new THREE.MeshStandardMaterial({ map: tr, roughness: 0.9, side: THREE.DoubleSide })); objetos.recibo.position.set(0, 0.02, 0.09);
  objetos.bandeja = new THREE.Group(); objetos.bandeja.position.set(0, 0.02, 0.12);
  VIN.malla(new THREE.CylinderGeometry(0.21, 0.2, 0.015, 40), M("#9aa0a6", { r: 0.25, m: 0.7 }), 0, 0, 0.14, objetos.bandeja);
  [[-0.08, 0.1], [0.08, 0.18]].forEach(([x, z]) => { VIN.malla(new THREE.CylinderGeometry(0.075, 0.06, 0.02, 32), M("#f4f1ea", { r: 0.3 }), x, 0.018, z, objetos.bandeja);
    VIN.esfera(0.05, M("#c98a3a", { r: 0.7 }), x, 0.035, z, objetos.bandeja, 1, 0.45, 1); });
  Object.values(objetos).forEach((o) => { o.visible = false; mano.add(o); });
  const r = semilla(c.semilla || 3), fase = r() * 10;
  return { raiz, cuerpo, torso, capa: null, piernas, brazos, cuello, cabeza, objetos, c, fase, vinil: true,
    cara(s) {
      const e = EMOS[s.emo] || EMOS.neutro, e2 = EMOS[s.emo2] || e, k = s.mezcla ?? 1, mix = (a, b) => lerp(a, b, k);
      const lid = s.parpadeo ? 1 : mix(e2.lid, e.lid), alto = mix(e2.ceja[0], e.ceja[0]), inc = mix(e2.ceja[1], e.ceja[1]), ojo = mix(e2.ojo, e.ojo) / 8;
      const curva = mix(e2.curva, e.curva) + (s.sonrisa || 0), ab = cl(s.voz || 0);
      ojos.forEach(({ g, bola, par, parInf, ceja, d }) => {
        bola.rotation.set(-(s.my || 0) * 0.25, (s.mx || 0) * 0.35, 0); const eo = 0.92 + 0.08 * ojo; g.scale.set(eo * (c.almendra ? 1.12 : 1), eo * (c.almendra ? 0.86 : 1), eo);
        par.rotation.x = lerp(-1.0, 1.6, Math.pow(cl(lid), 1.7)); parInf.rotation.x = lerp(0.62, 0.35, cl(lid));
        const asim = e.asim && d > 0 ? 1 : 0;
        ceja.position.y = 0.112 - alto * 0.0075 + asim * 0.018; ceja.rotation.z = PI / 2 + inc * d * 1.25 * (asim ? -1.4 : 1);
      });
      boca.scale.set(1.25 - ab * 0.25, 0.08 + ab * 0.85, 0.45); boca.visible = ab > 0.05;
      sonrisa.visible = ab <= 0.05; const sg = curva >= 0 ? 1 : -1;
      sonrisa.rotation.z = sg > 0 ? -PI / 2 - PI * 0.31 : PI / 2 - PI * 0.31; sonrisa.scale.set(1, 0.25 + Math.min(1, Math.abs(curva)) * 0.75, 1);
      sonrisa.position.y = -0.13 + (sg > 0 ? 0.03 : -0.035) * Math.min(1, Math.abs(curva) + 0.2);
      const ld = mix(e2.ladeo || 0, e.ladeo || 0); sonrisa.position.x = ld * 0.02; sonrisa.rotation.z += ld * 0.28; if (labioInf) { labioInf.visible = ab <= 0.05; labioInf.position.x = ld * 0.015; }
    } };
}
