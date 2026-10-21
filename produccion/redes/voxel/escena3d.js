// Motor de «Turno de noche»: cámara de cine, actores con claves de tiempo, voces con labios sincronizados, subtítulos y cortes.
// Tiempos de las claves: número (segundos desde el inicio del plano) o "l1" / "l1+0.5" (inicio de la línea 1 del plano) o "f1" (fin de la línea 1).
const $ = (s) => document.querySelector(s);
const REN = new THREE.WebGLRenderer({ canvas: $("#lienzo"), antialias: true, preserveDrawingBuffer: true });
REN.setPixelRatio(1); REN.setSize(1080, 1920, false); REN.shadowMap.enabled = true; REN.shadowMap.type = THREE.PCFSoftShadowMap;
REN.toneMapping = THREE.ACESFilmicToneMapping; REN.toneMappingExposure = 1.35; REN.outputColorSpace = THREE.SRGBColorSpace;
const ESC = new THREE.Scene(); ESC.background = new THREE.Color(0x060504); ESC.fog = new THREE.FogExp2(0x0a0806, 0.02);
const CAM = new THREE.PerspectiveCamera(38, 1080 / 1920, 0.05, 90);
const RELLENO = new THREE.DirectionalLight(0xffe6cc, 0.55); ESC.add(RELLENO); ESC.add(RELLENO.target);   // luz suave desde la cámara para leer las caras
const SETS = { restaurante: restaurante(ESC), oficina: oficina(ESC) };
const ACT = {}, ORBIS = {};
Object.entries(EP.elenco).forEach(([id, cfg]) => { ACT[id] = persona(cfg); ESC.add(ACT[id].raiz); });
const EXTRAS = (EP.extras || []).map((x, i) => { const P = persona({ semilla: 100 + i, ...x.cfg }); ESC.add(P.raiz); return { P, x }; });

// ---------- Claves de tiempo
function tClave(k, L) {
  if (typeof k === "number") return k;
  const m = /^([lf])(\d+)([+-][\d.]+)?$/.exec(k); if (!m) return 0;
  const l = L.lineas[+m[2]]; if (!l) return 0; return (m[1] === "l" ? l.ini : l.fin) - L.ini + (m[3] ? parseFloat(m[3]) : 0);
}
// valor discreto con mezcla: devuelve [anterior, actual, mezcla]
function discreto(spec, tt, L, d = 0.45) {
  if (!Array.isArray(spec) || !Array.isArray(spec[0])) return [spec, spec, 1];
  let i = -1; spec.forEach((s, j) => { if (tClave(s[0], L) <= tt) i = j; });
  if (i < 0) return [spec[0][1], spec[0][1], 1];
  const prev = i > 0 ? spec[i - 1][1] : spec[i][1]; return [prev, spec[i][1], suave((tt - tClave(spec[i][0], L)) / d)];
}
// valor continuo (números o vectores) entre claves, con aceleración suave; también da la velocidad
function continuo(spec, tt, L) {
  if (!Array.isArray(spec) || !Array.isArray(spec[0])) return [spec, 0];
  const ks = spec.map((s) => [tClave(s[0], L), s.slice(1)]);
  if (tt <= ks[0][0]) return [ks[0][1].length === 1 ? ks[0][1][0] : ks[0][1], 0];
  for (let j = 0; j < ks.length - 1; j++) if (tt < ks[j + 1][0]) {
    const [t0, a] = ks[j], [t1, b] = ks[j + 1], k = suave((tt - t0) / (t1 - t0)), v = a.map((x, n) => lerp(x, b[n], k));
    const dist = Math.hypot(...a.map((x, n) => b[n] - x).slice(0, 2)), vel = dist / Math.max(0.01, t1 - t0) * (1 - Math.abs(2 * ((tt - t0) / (t1 - t0)) - 1) * 0.6);
    return [v.length === 1 ? v[0] : v, vel];
  }
  const u = ks[ks.length - 1][1]; return [u.length === 1 ? u[0] : u, 0];
}
const ang = (a) => { while (a > PI) a -= 2 * PI; while (a < -PI) a += 2 * PI; return a; };
// voz de cada personaje: envolvente real del audio, cuadro a cuadro
function voz(quien, t) {
  for (const L of LINEA.planos) for (const l of L.lineas) if (l.quien === quien && t >= l.ini && t < l.fin) { const e = l.env || []; return e[Math.min(e.length - 1, Math.floor((t - l.ini) * 30))] || 0; }
  return 0;
}
function origen(set) { return SETS[set].position; }
function posMundo(id, pl, tt, L) {
  const o = origen(pl.set);
  if (id === "cam") return CAM.position.clone();
  if (pl.orbis && pl.orbis[id]) { const p = pl.orbis[id].pos; return new THREE.Vector3(p[0] + o.x, p[1], p[2] + o.z); }
  const a = pl.actores && pl.actores[id]; if (!a) return null;
  const [p] = continuo(a.pos, tt, L); return new THREE.Vector3(p[0] + o.x, a.sentado ? 1.38 : 1.72, p[1] + o.z);
}
function yawHacia(P, T) { return Math.atan2(T.x - P.x, T.z - P.z); }

// ---------- Cuadro
let grano = null;
function render(t) {
  const PL = EP.planos, LP = LINEA.planos; let i = LP.findIndex((L) => t < L.fin); if (i < 0) i = LP.length - 1;
  const pl = PL[i], L = LP[i], tt = t - L.ini, dur = L.fin - L.ini, p = cl(tt / dur);
  Object.entries(SETS).forEach(([n, s]) => { s.visible = n === pl.set; });
  const o = origen(pl.set), est = pl.e || {};
  // estado del escenario: rayos, pantallas, comandas
  let rayo = 0; (est.rayos || []).forEach(([k, d]) => { const r0 = tClave(k, L), x = tt - r0; if (x >= 0 && x < (d || 0.6)) rayo = Math.max(rayo, (x < 0.08 || (x > 0.18 && x < 0.26) ? 1 : 0.35) * (1 - x / (d || 0.6))); });
  const eTab = discreto(est.tablet || {}, tt, L)[1], ePort = discreto(est.portatil || {}, tt, L)[1];
  const qrLuz = {}; Object.entries(est.qrLuz || {}).forEach(([n, s]) => { qrLuz[n] = continuo(s, tt, L)[0]; });
  SETS[pl.set].userData.paso(t, { lapRot: est.lapRot !== undefined ? continuo(est.lapRot, tt, L)[0] : undefined, rayo, comandas: est.comandas, tablet: eTab, portatil: ePort, qrLuz, rojo: discreto(est.rojo || false, tt, L)[1] });
  // cámara (claves [x,y,z, tx,ty,tz, fov]) con cámara en mano
  const [c] = continuo(pl.cam.map((k, j) => k.length === 8 ? k : [j === 0 ? 0 : dur * j / (pl.cam.length - 1), ...k]), tt, L);
  const mano = pl.mano ?? 0.012, hx = mano * (Math.sin(t * 1.1) + 0.5 * Math.sin(t * 2.7)), hy = mano * Math.cos(t * 0.9);
  CAM.position.set(c[0] + o.x + hx, c[1] + hy, c[2] + o.z); CAM.lookAt(c[3] + o.x + hx * 0.5, c[4] + hy * 0.5, c[5] + o.z); CAM.fov = c[6] || 38;
  RELLENO.position.copy(CAM.position).add(new THREE.Vector3(0.6, 0.8, 0)); RELLENO.target.position.set(c[3] + o.x, c[4], c[5] + o.z); RELLENO.intensity = pl.relleno ?? 0.55;
  if (pl.giro) CAM.rotateZ(continuo(pl.giro, tt, L)[0] * PI / 180);
  CAM.updateProjectionMatrix();
  // actores
  Object.entries(ACT).forEach(([id, P]) => {
    const a = pl.actores && pl.actores[id]; P.raiz.visible = !!a; if (!a) return;
    const [pos, vel] = continuo(a.pos, tt, L), [r0, r1, kr] = discreto(a.rot ?? 0, tt, L, a.giroDur ?? 0.6);
    const rot = lerp(r0, r1, kr) * PI / 180, [g0, g1, kg] = discreto(a.gesto || "reposo", tt, L), [e0, e1, ke] = discreto(a.emo || "neutro", tt, L, 0.3);
    const P0 = new THREE.Vector3(pos[0] + o.x, a.sentado ? 1.38 : 1.72, pos[1] + o.z);
    const mira = (m) => { if (m === null || m === undefined) return [0, 0]; if (typeof m === "number") return [m * PI / 180, 0];
      const T = posMundo(m, pl, tt, L); if (!T) return [0, 0]; return [ang(yawHacia(P0, T) - rot), -Math.atan2(T.y - P0.y, Math.hypot(T.x - P0.x, T.z - P0.z)) * 0.7]; };
    const [m0, m1, km] = discreto(a.mira ?? null, tt, L, a.miraDur ?? 0.5), [y0, p0] = mira(m0), [y1, p1] = mira(m1);
    animarPersona(P, { x: pos[0] + o.x, z: pos[1] + o.z, rot, gesto: g1, gesto2: g0, mezclaG: kg, camina: vel, sentado: a.sentado, voz: voz(id, t),
      emo: e1, emo2: e0, mezcla: ke, mira: lerp(y0, y1, km), miraY: lerp(p0, p1, km) + (a.miraY || 0), inclina: continuo(a.inclina || 0, tt, L)[0], ladea: a.ladea, manos: a.manos, sonrisa: a.sonrisa }, t);
  });
  // extras del salón (clientes sentados que conversan)
  EXTRAS.forEach(({ P, x }, j) => { P.raiz.visible = x.set === pl.set && !(pl.sinExtras || []).includes(j);
    if (!P.raiz.visible) return; const habla = x.charla ? Math.max(0, Math.sin(t * 2.1 + j * 1.7)) * (0.3 + 0.5 * Math.abs(Math.sin(t * 9 + j))) : 0;
    const gx = (pl.extrasGesto || {})[j]; animarPersona(P, { x: x.x + o.x, z: x.z + o.z, rot: (x.rot || 0) * PI / 180, gesto: gx || x.gesto || "manos_mesa", sentado: true, voz: habla > 0.25 ? habla : 0, emo: x.emo || "neutro", mira: Math.sin(t * 0.3 + j) * 0.3 }, t); });
  // Orbis
  Object.values(ORBIS).forEach((O) => { O.raiz.visible = false; });
  Object.entries(pl.orbis || {}).forEach(([id, d], j) => {
    if (!ORBIS[id]) { ORBIS[id] = orbi3d(d.r || 0.17); ESC.add(ORBIS[id].raiz); }
    const O = ORBIS[id], nace = d.nace ? cl((tt - tClave(d.nace[0], L)) / (tClave(d.nace[1], L) - tClave(d.nace[0], L))) : 1;
    const v = d.voz !== false ? voz("orbi", t) : 0, [s0, s1] = discreto(d.estado || "reposo", tt, L);
    const P0 = new THREE.Vector3(d.pos[0] + o.x, d.pos[1], d.pos[2] + o.z), [m0, m1, km] = discreto(d.mira || "cam", tt, L);
    const yaw = (m) => { const T = m === "cam" ? CAM.position : posMundo(m, pl, tt, L); return T ? yawHacia(P0, T) : 0; };
    O.animar({ x: P0.x, y: P0.y, z: P0.z, rot: lerp(yaw(m0), yaw(m1), km), nace, estado: v > 0.02 ? "habla" : s1, voz: v, fase: j * 1.3, luz: d.luz }, t);
  });
  REN.render(ESC, CAM);
  // color de cine, viñeta, subtítulos, título, negro y destellos
  $("#lienzo").style.filter = pl.grado || "contrast(1.08) saturate(1.06)";
  const linea = L.lineas.find((l) => t >= l.ini - 0.05 && t < l.fin + 0.25), sub = $("#sub");
  sub.textContent = linea ? linea.txt : ""; sub.style.opacity = linea ? 1 : 0;
  const ti = $("#titulo");
  if (pl.titulo) { const a = cl((tt - 0.4) / 0.6) * cl((dur - 0.4 - tt) / 0.5); ti.innerHTML = `<small>${pl.titulo[0]}</small><b>${pl.titulo[1] || ""}</b>`; ti.style.opacity = a; } else ti.style.opacity = 0;
  let negro = 0; if (pl.trans === "negro") negro = Math.max(negro, 1 - cl(tt / 0.6)); if (PL[i + 1] && PL[i + 1].trans === "negro") negro = Math.max(negro, cl((tt - dur + 0.45) / 0.45));
  if (i === 0) negro = Math.max(negro, 1 - cl(tt / 0.8)); $("#negro").style.opacity = negro;
  $("#blanco").style.opacity = pl.trans === "flash" ? Math.max(0, 0.8 - tt * 3) : 0;
  const fi = $("#final");
  if (pl.final) { const f = pl.final; if (fi.dataset.i !== String(i)) { fi.dataset.i = i; fi.innerHTML = `<div class="logo"><i class="pin"></i>${f.marca}</div><div class="frase">${f.frase}</div>${f.detalle ? `<div class="detalle">${f.detalle}</div>` : ""}<div class="wa"><i></i><div><small>Escríbanos por WhatsApp</small><b>310 789 7960</b></div></div><div class="pie">Apex Corporation · Tuluá</div>`; }
    fi.style.opacity = cl((tt - (f.desde || 0.3)) / 0.7); $("#cortina").style.opacity = 0.78 * cl((tt - (f.desde || 0.3) + 0.3) / 0.8); } else { fi.style.opacity = 0; $("#cortina").style.opacity = 0; }
  $("#nota").textContent = pl.nota || "";
  // grano de película
  const gc = $("#grano"), gg = gc.getContext("2d"); if (!grano) grano = gg.createImageData(360, 640); const r = semilla(Math.floor(t * 30) + 1);
  for (let k = 0; k < grano.data.length; k += 4) { const v = r() * 255; grano.data[k] = grano.data[k + 1] = grano.data[k + 2] = v; grano.data[k + 3] = 255; } gg.putImageData(grano, 0, 0);
}
