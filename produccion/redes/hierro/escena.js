// «Orbi · Mark I». render(t, f)
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const rebote = (x) => { x = cl(x); return 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
const E = LINEA.escenas, L = LINEA.lineas;
const escenaDe = (t) => Object.keys(E).find((k) => t >= E[k][0] && t < E[k][1]) || "sello";
const habla = (q, t) => L.some((l) => l.quien === q && t >= l.ini && t < l.fin);
const lin = (q, esc, n = 0) => L.filter((l) => l.quien === q && (!esc || l.esc === esc))[n];
const g = (x, y, s, c, op = 1, rot = 0) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})" opacity="${op}">${c}</g>`;
const azar = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
function orbiCara(t, nombre, h, extra = {}) {
  const base = { ...EXPRESIONES[nombre], ...extra };
  if (h) { const a = 0.25 + 0.55 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 5.3)); base.boca = nombre === "feliz" ? [0.9, 1.2, Math.max(0.2, a)] : [0.3, 0.8, a * 0.8]; }
  if ((t % 3.4) < 0.12 && base.oi > 0) { base.oi = 0.08; if (base.od > 0) base.od = 0.08; }
  return orbi(nombre, { e: base, anillo: -10 + 4 * Math.sin(t * 1.3), brillo: 0.4 }).replace("<svg ", '<svg width="380" height="380" ');
}
const DEFS = ARMA_DEFS + `<defs>
  <linearGradient id="noche" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#02040c"/><stop offset=".55" stop-color="#0a1836"/><stop offset="1" stop-color="#22305a"/></linearGradient>
  <linearGradient id="mar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16244a"/><stop offset="1" stop-color="#03060f"/></linearGradient>
  <radialGradient id="luna"><stop offset="0" stop-color="#fffbe8"/><stop offset=".08" stop-color="#fff3cc"/><stop offset=".25" stop-color="rgba(255,240,200,.25)"/><stop offset="1" stop-color="rgba(255,240,200,0)"/></radialGradient>
  <linearGradient id="piso" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1f27"/><stop offset="1" stop-color="#07080b"/></linearGradient>
  <linearGradient id="desvanece" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".32"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <mask id="reflejo"><rect x="-900" y="1250" width="2880" height="900" fill="url(#desvanece)"/></mask>
  <radialGradient id="holo" cx="50%" cy="100%" r="100%"><stop offset="0" stop-color="rgba(80,220,255,.45)"/><stop offset="1" stop-color="rgba(80,220,255,0)"/></radialGradient>
  <radialGradient id="polvo"><stop offset="0" stop-color="rgba(220,200,170,.6)"/><stop offset="1" stop-color="rgba(220,200,170,0)"/></radialGradient>
  <radialGradient id="nube"><stop offset="0" stop-color="rgba(120,140,190,.35)"/><stop offset="1" stop-color="rgba(120,140,190,0)"/></radialGradient>
</defs>`;
// ---------- Exterior: mar de noche con luna (se ve por el ventanal) ----------
function marNoche(t, x0, y0, w, h) {
  const hz = y0 + h * 0.62;
  let s = `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="url(#noche)"/>`;
  for (let i = 0; i < 90; i++) s += `<circle cx="${x0 + azar(i) * w}" cy="${y0 + azar(i + 50) * (hz - y0)}" r="${0.8 + azar(i + 9) * 1.8}" fill="#fff" opacity="${(0.25 + 0.6 * azar(i + 3)) * (0.7 + 0.3 * Math.sin(t * 2 + i))}"/>`;
  s += `<circle cx="${x0 + w * 0.72}" cy="${y0 + h * 0.24}" r="260" fill="url(#luna)"/><circle cx="${x0 + w * 0.72}" cy="${y0 + h * 0.24}" r="34" fill="#fff8e0"/>`;
  s += `<rect x="${x0}" y="${hz}" width="${w}" height="${y0 + h - hz}" fill="url(#mar)"/>`;
  for (let i = 0; i < 40; i++) { const yy = hz + 6 + Math.pow(i / 40, 1.6) * (y0 + h - hz), ww = 20 + i * 5, xx = x0 + w * 0.72 + Math.sin(t * 1.5 + i * 1.7) * (8 + i * 2);
    s += `<rect x="${xx - ww / 2}" y="${yy}" width="${ww}" height="${2 + i * 0.12}" fill="#fff3cc" opacity="${0.55 - i * 0.011}"/>`; }
  for (let i = 0; i < 60; i++) s += `<circle cx="${x0 + azar(i + 200) * w * 0.55}" cy="${hz - 4 - azar(i + 300) * 10}" r="${1 + azar(i) * 1.6}" fill="#ffd38a" opacity=".7"/>`;
  return s;
}
// ---------- Taller del genio ----------
function brazo(x, y, a1, a2, pieza = "", esc = 0.62) {
  return `<g transform="translate(${x} ${y}) scale(${esc})"><rect x="-60" y="-30" width="120" height="60" rx="14" fill="#2a2e36"/><circle r="34" fill="#3a3f49" stroke="#e8a33a" stroke-width="5"/>
    <g transform="rotate(${a1})"><rect x="-22" y="-360" width="44" height="360" rx="18" fill="#4a505c"/><rect x="-8" y="-340" width="16" height="320" rx="6" fill="#2a2e36"/>
      <g transform="translate(0 -360) rotate(${a2})"><circle r="30" fill="#3a3f49" stroke="#e8a33a" stroke-width="5"/><rect x="-18" y="-280" width="36" height="280" rx="14" fill="#5a616e"/>
        <g transform="translate(0 -290)"><path d="M-40 0 L -26 -46 M40 0 L 26 -46" stroke="#9aa3ad" stroke-width="12" stroke-linecap="round"/><circle r="22" fill="#2a2e36"/>${pieza}</g></g></g></g>`;
}
function holograma(t, x, y, k = 1, verdes = 0) {
  let s = `<g transform="translate(${x} ${y})"><ellipse cx="0" cy="40" rx="250" ry="56" fill="#0d1118" stroke="#1d2a38" stroke-width="6"/><ellipse cx="0" cy="34" rx="230" ry="46" fill="none" stroke="#50dcff" stroke-width="3" opacity=".8" filter="url(#brillo)"/>
    <path d="M-220 30 L -260 -520 L 260 -520 L 220 30Z" fill="url(#holo)" opacity="${0.55 * k}"/><g opacity="${k}" filter="url(#brillo)">`;
  // plano del restaurante en perspectiva, 14 mesas
  for (let i = 0; i < 14; i++) { const cx = ((i % 5) - 2) * 80 + (Math.floor(i / 5) % 2) * 40, cy = -210 + Math.floor(i / 5) * 60, ok = i < verdes;
    s += `<ellipse cx="${cx}" cy="${cy}" rx="26" ry="10" fill="none" stroke="${ok ? "#4dff9a" : "#ff4a5a"}" stroke-width="3" opacity="${ok ? 1 : 0.5 + 0.5 * Math.sin(t * 8 + i)}"/>`; }
  s += `<path d="M-230 -300 L 230 -300 L 200 -120 L -200 -120Z" fill="none" stroke="#50dcff" stroke-width="2" opacity=".6"/>`;
  for (let r = 0; r < 3; r++) s += `<ellipse cx="0" cy="-360" rx="${150 + r * 40}" ry="${36 + r * 10}" fill="none" stroke="#50dcff" stroke-width="2" stroke-dasharray="${20 + r * 10} ${14 + r * 6}" stroke-dashoffset="${(t * (40 + r * 30)) % 200}" opacity=".7"/>`;
  s += `<text x="0" y="-440" text-anchor="middle" font-size="30" fill="#bff6ff" font-family="Figtree" font-weight="700" letter-spacing="6">LA FONDA · ${14 - verdes} ESPERANDO</text></g></g>`;
  return s;
}
function taller(t, o = {}) {
  let w = `<rect x="-900" y="-900" width="2880" height="3800" fill="#08090c"/>`;
  const ventana = `${marNoche(t, -200, 150, 1480, 1100)}${Array.from({ length: 7 }, (_, i) => `<rect x="${-200 + i * 246}" y="150" width="12" height="1100" fill="#0b0d12"/>`).join("")}<rect x="-200" y="640" width="1480" height="10" fill="#0b0d12"/>`;
  w += ventana + `<rect x="-900" y="0" width="2880" height="150" fill="#0c0e13"/>`;
  for (let i = 0; i < 4; i++) w += `<rect x="${-100 + i * 340}" y="70" width="240" height="8" rx="4" fill="#f4f1e6" filter="url(#brillo)" opacity=".85"/>`;
  w += `<rect x="-900" y="1250" width="2880" height="1700" fill="url(#piso)"/><g mask="url(#reflejo)"><g transform="translate(0 2500) scale(1 -1)">${ventana}</g></g>`;
  w += `<rect x="-900" y="1244" width="2880" height="10" fill="#2a2f39"/>`;
  // bancos de trabajo con herramientas
  w += `<g transform="translate(-60 1180)"><rect x="-200" y="0" width="420" height="30" fill="#2a2e36"/><rect x="-180" y="30" width="20" height="140" fill="#1b1e24"/><rect x="180" y="30" width="20" height="140" fill="#1b1e24"/>
    <rect x="-150" y="-60" width="90" height="60" rx="6" fill="#3a3f49"/><rect x="-140" y="-52" width="70" height="36" fill="#50dcff" opacity=".35"/><path d="M20 0 L 60 -80 M80 0 L 100 -60" stroke="#9aa3ad" stroke-width="10"/></g>
    <g transform="translate(1140 1180)"><rect x="-220" y="0" width="420" height="30" fill="#2a2e36"/><circle cx="-100" cy="-40" r="40" fill="none" stroke="#e8a33a" stroke-width="10"/><rect x="0" y="-90" width="120" height="90" rx="8" fill="#3a3f49"/></g>`;
  w += o.atras || "";
  // partículas de polvo en la luz de la luna
  for (let i = 0; i < 40; i++) { const ph = (t * 0.03 + azar(i)) % 1; w += `<circle cx="${100 + azar(i + 5) * 900 + Math.sin(t + i) * 20}" cy="${300 + ph * 1000}" r="${1.5 + azar(i) * 2}" fill="#fff6dc" opacity="${0.35 * Math.sin(ph * Math.PI)}"/>`; }
  w += o.frente || "";
  return w;
}
// ---------- Vuelo nocturno ----------
function vuelo(t) {
  let w = `<rect x="-900" y="-900" width="2880" height="3800" fill="url(#noche)"/>`;
  for (let i = 0; i < 120; i++) w += `<circle cx="${-300 + azar(i) * 1700}" cy="${-300 + azar(i + 40) * 1200}" r="${0.8 + azar(i + 9) * 1.8}" fill="#fff" opacity="${0.3 + 0.5 * azar(i + 3)}"/>`;
  w += `<circle cx="860" cy="380" r="300" fill="url(#luna)"/><circle cx="860" cy="380" r="42" fill="#fff8e0"/>`;
  // ciudad en perspectiva abajo
  w += `<path d="M-900 1250 L 1980 1250 L 1980 2900 L -900 2900Z" fill="#04060c"/>`;
  for (let r = 0; r < 26; r++) { const y = 1260 + Math.pow(r / 26, 1.8) * 1300, sep = 18 + r * 9, off = ((t * 260 * (1 + r * 0.08)) % sep);
    for (let x = -900 + off - sep; x < 1980; x += sep) if (azar(Math.floor(x / sep) * 31 + r) > 0.45) w += `<circle cx="${x}" cy="${y}" r="${0.8 + r * 0.16}" fill="${azar(x + r) > 0.8 ? "#9fe6ff" : "#ffcf7a"}" opacity="${0.4 + r * 0.02}"/>`; }
  for (let i = 0; i < 7; i++) { const x = ((i * 400 - t * 520) % 2400 + 2400) % 2400 - 700; w += `<ellipse cx="${x}" cy="${500 + azar(i) * 800}" rx="${300 + azar(i) * 300}" ry="${70 + azar(i + 2) * 60}" fill="url(#nube)"/>`; }
  return w;
}
// ---------- Restaurante ----------
function salon(t, o = {}) {
  let w = restaurante(t, o.luz ?? 1);
  w += `<rect x="760" y="560" width="300" height="200" rx="10" fill="#f3d7a2" opacity=".8"/><rect x="760" y="540" width="300" height="34" fill="#2a1d14"/><text x="910" y="566" text-anchor="middle" font-size="26" font-weight="800" fill="#f1c76a" font-family="Figtree">COCINA</text>`;
  const M = [[200, 1330], [860, 1300], [330, 1700], [790, 1720]];
  M.forEach(([x, y], i) => { w += g(x, y - 40, 1, persona({ piel: PIELES[i], pelo: ["corto", "largo", "calvo", "moño"][i], camisa: ["#3d6fb6", "#8a3b5c", "#5a7a3a", "#2a9d8f"][i], brazo: o.manos ? (Math.sin(t * 5 + i * 2) > -0.2 ? 1 : 0) : 0, boca: o.asombro ? 0.95 : 0.4, cejas: o.manos ? "enojo" : o.asombro ? "arriba" : "", mira: o.mira ?? 0 })) + mesa(x, y); });
  return { w, M };
}
function hudRestaurante(t, M, verdes) {
  return M.map(([x, y], i) => { const ok = i < verdes, c = ok ? "#4dff9a" : "#ff4a5a", r = 150, k = ok ? 1 : 1 + 0.06 * Math.sin(t * 10);
    return `<g transform="translate(${x} ${y - 120}) scale(${k})" filter="url(#brillo)"><path d="M${-r} ${-r + 40} V ${-r} H ${-r + 40} M${r - 40} ${-r} H ${r} V ${-r + 40} M${r} ${r - 40} V ${r} H ${r - 40} M${-r + 40} ${r} H ${-r} V ${r - 40}" fill="none" stroke="${c}" stroke-width="6"/>
      <text x="${-r}" y="${-r - 16}" font-size="30" font-weight="800" fill="${c}" font-family="Figtree" letter-spacing="2">MESA ${i + 1} · ${ok ? "PEDIDO ENVIADO ✓" : "ESPERANDO"}</text></g>`; }).join("");
}
// ---------- Cámara ----------
const CAM = { gancho: [[540, 1300, 1.25], [540, 1280, 1.35]], titulo: [[540, 960, 1], [540, 960, 1]], taller: [[540, 900, 1.0], [560, 1050, 1.2]], traje: [[540, 1150, 1.25], [540, 1120, 1.5]],
  vuelo: [[540, 960, 1], [560, 980, 1.08]], mesas: [[540, 1450, 1.0], [540, 1450, 1.06]], aterriza: [[540, 1350, 1.0], [660, 1280, 1.15]], sello: [[540, 960, 1], [540, 960, 1]] };
function camara(t) {
  const k = escenaDe(t), [a, b] = E[k], p = (t - a) / (b - a), [c0, c1] = CAM[k];
  let c = c0.map((v, i) => lerp(v, c1[i], ease(p)));
  if (k === "taller") { const l = lin("orbi", "taller", 1); if (l) { const q = ease((t - l.ini + 0.3) / 0.5); c = c.map((v, i) => lerp(v, [540, 1080, 1.55][i], q)); } }
  if (k === "aterriza") { const o = lin("orbi", "aterriza"); if (o) { const q = ease((t - o.ini + 0.6) / 0.6); c = c.map((v, i) => lerp(v, [600, 1120, 1.5][i], q)); } }
  return c;
}
let ultimo = "";
async function render(t, f) {
  const k = escenaDe(t), [a, b] = E[k], tt = t - a;
  let w = "", hud = "", shake = 0;
  if (k === "gancho" || k === "mesas") {
    const verdes = k === "mesas" ? Math.min(4, Math.floor(cl((t - E.mesas[0] - 0.4) / 4.4) * 5)) : 0;
    const { w: s, M } = salon(t, { luz: k === "gancho" ? 0.5 : 1, manos: verdes < 4, mira: 6 });
    w = s + hudRestaurante(t, M, verdes);
    if (k === "mesas") w += M.map(([x, y], i) => i < verdes ? `<line x1="540" y1="-200" x2="${x}" y2="${y - 120}" stroke="#50dcff" stroke-width="4" opacity="${0.5 + 0.5 * Math.sin(t * 12 + i)}" filter="url(#brillo)"/>` : "").join("");
  }
  if (k === "taller" || k === "traje") {
    const l3 = lin("orbi", "taller", 1), verdes = 0;
    let atras = holograma(t, 540, 1420, 1, verdes), frente = "", ox = 540, oy = 1120 + Math.sin(t * 2) * 8;
    let a1 = -20 + 6 * Math.sin(t * 0.8), a2 = 40, b1 = 20 - 6 * Math.sin(t * 0.9), b2 = -40, armor = { torso: 0, hombros: 0, casco: 0, visor: 0, reactor: 0 }, cara = "normal", piezaI = "", piezaD = "";
    if (k === "taller") { cara = habla("sofia", t) ? "sarcastico" : "orgulloso"; if (l3 && t > l3.fin) cara = "guino"; }
    if (k === "traje") {
      // secuencia: torso (1.2 s), hombros (2.4 s), casco (3.6 s), reactor (4.6 s), visor (6.6 s)
      const tl = (x) => cl((tt - x) / 0.6);
      armor = { torso: tl(1.0), hombros: tl(2.2), casco: tl(3.4), reactor: cl((tt - 4.5) / 0.3), visor: cl((tt - 6.4) / 0.35), t };
      a1 = -30 + 25 * Math.sin(tt * 2.2); b1 = 30 - 25 * Math.sin(tt * 2.0); a2 = 50 + 20 * Math.sin(tt * 3); b2 = -50 - 20 * Math.sin(tt * 3);
      cara = habla("orbi", t) ? "feliz" : "orgulloso";
      if (tt > 1.0 && tt < 1.6 || tt > 2.2 && tt < 2.8 || tt > 3.4 && tt < 4.0) frente += Array.from({ length: 16 }, (_, i) => { const ph = ((tt * 3 + azar(i)) % 1); return `<line x1="${540 + (azar(i + 1) - 0.5) * 260}" y1="${1120 + (azar(i + 4) - 0.5) * 260}" x2="${540 + (azar(i + 1) - 0.5) * 260 + (azar(i + 7) - 0.5) * 120 * ph}" y2="${1120 + (azar(i + 4) - 0.5) * 260 + 80 * ph}" stroke="#ffd27a" stroke-width="4" opacity="${1 - ph}"/>`; }).join("");
      shake = [1.6, 2.8, 4.0, 6.75].some((x) => tt > x && tt < x + 0.12) ? 8 : 0;
      atras = holograma(t, 540, 1420, 1 - cl((tt - 0.5) / 0.6) * 0.7, 0);
    }
    const svgO = orbiCara(t, cara, habla("orbi", t));
    frente = brazo(170, 1330, a1, a2, piezaI) + brazo(910, 1330, b1, b2, piezaD) + `<g transform="translate(${ox} ${oy}) scale(.9)">${armadura(svgO, { ...armor, t })}</g>` + frente;
    w = taller(t, { atras, frente });
    if (k === "traje" && tt > 6.75) hud = hudCasco(t, tt - 6.75, "MARK I · EN LÍNEA");
  }
  if (k === "vuelo") {
    const q = out3(tt / 0.8), x = lerp(-300, 470, q) + Math.sin(t * 1.3) * 30, y = lerp(1500, 980, q) + Math.sin(t * 2.1) * 20;
    w = vuelo(t) + `<path d="M${x - 40} ${y + 260} Q ${x - 400} ${y + 600} ${x - 900} ${y + 1100}" stroke="#bff6ff" stroke-width="30" fill="none" opacity=".25" filter="url(#brillo)"/>`
      + `<g transform="translate(${x} ${y}) rotate(${-18 + 4 * Math.sin(t * 2)}) scale(.72)">${armadura(orbiCara(t, "orgulloso", false), { visor: 1, fuego: 1, t })}</g>`;
    for (let i = 0; i < 30; i++) { const ph = (t * 2 + azar(i)) % 1; w += `<line x1="${azar(i) * 1080}" y1="${-100 + ph * 2200}" x2="${azar(i) * 1080 - 10}" y2="${-100 + ph * 2200 - 140}" stroke="#fff" stroke-width="2" opacity=".18"/>`; }
    const s = lin("sofia", "vuelo"), n = s ? Math.floor(cl((t - s.ini) / (s.fin - s.ini + 0.3)) * 14) : 0;
    hud = hudCasco(t, 1, `QR CONECTADOS ${n}/14`, { alt: Math.round(320 + 40 * Math.sin(t)), vel: Math.round(182 + 10 * Math.sin(t * 1.7)) });
    shake = 2;
  }
  if (k === "mesas") hud = hudCasco(t, 1, "MODO MESERO · ACTIVO", {});
  if (k === "aterriza") {
    const caida = out3((tt - 0.15) / 0.45), golpe = tt > 0.6 && tt < 0.95, { w: s } = salon(t, { asombro: true, mira: 4 });
    const jl = lin("julian", "aterriza"), ol = lin("orbi", "aterriza"), visor = ol ? 1 - cl((t - ol.ini + 0.7) / 0.4) : 1;
    w = s;
    if (tt > 0.6) w += `<ellipse cx="540" cy="1390" rx="${200 + 500 * cl((tt - 0.6) / 0.8)}" ry="${40 + 90 * cl((tt - 0.6) / 0.8)}" fill="url(#polvo)" opacity="${1 - cl((tt - 0.6) / 1.4)}"/>
      <path d="M540 1390 l -160 40 m 160 -40 l 120 70 m -120 -70 l -40 110 m 40 -110 l 210 -10" stroke="#2a1d14" stroke-width="6" fill="none"/>`;
    w += g(lerp(1150, 920, out3((tt - 1.0) / 0.6)), 1260, 0.95, julian({ bandeja: true, platos: 3, ojos: "grandes", boca: habla("julian", t) ? 0.4 + 0.5 * Math.abs(Math.sin(t * 15)) : "o", sudor: true, inclina: -12 }));
    const cara = visor < 0.5 ? (ol && t > ol.fin ? "guino" : "orgulloso") : "normal";
    w += `<g transform="translate(540 ${lerp(-500, 1200, caida)}) scale(.86)">${armadura(orbiCara(t, cara, habla("orbi", t)), { visor, fuego: 1 - cl((tt - 0.5) / 0.4), t })}</g>`;
    shake = golpe ? 18 : 0;
  }
  if (k === "titulo" || k === "sello") w = taller(t, {}) + `<rect x="-900" y="-900" width="2880" height="3800" fill="rgba(0,0,0,.6)"/>`;
  const [cx, cy, cs] = camara(t), sx = shake * Math.sin(f * 7.1), sy = shake * Math.cos(f * 5.3);
  $("#escena").innerHTML = `<svg viewBox="0 0 1080 1920" width="1080" height="1920">${DEFS}<g transform="translate(${540 + sx} ${960 + sy}) scale(${cs}) translate(${-cx} ${-cy})">${w}</g></svg>`;
  // alerta roja del gancho
  if (k === "gancho") hud = `<rect width="1080" height="1920" fill="rgba(200,0,20,${0.18 + 0.12 * Math.sin(t * 14)})"/>
    <g transform="translate(540 700)"><rect x="-470" y="-120" width="940" height="240" rx="18" fill="rgba(30,0,6,.82)" stroke="#ff3b4a" stroke-width="6"/>
      <text y="-30" text-anchor="middle" font-size="64" font-weight="800" fill="#ff5a66" font-family="Figtree" letter-spacing="6">⚠ ALERTA</text>
      <text y="56" text-anchor="middle" font-size="58" font-weight="800" fill="#fff" font-family="Figtree">14 MESAS ESPERANDO</text></g>
    <text x="540" y="900" text-anchor="middle" font-size="44" fill="#ffb3b9" font-family="Figtree" font-weight="700">TIEMPO DE ESPERA ${String(19 + Math.floor(t / 1.2)).padStart(2, "0")}:${String(Math.floor((t * 37) % 60)).padStart(2, "0")}</text>`;
  $("#hud").innerHTML = hud;
  let negro = 0; Object.keys(E).forEach((e) => { const x = E[e][0]; if (x > 0) negro = Math.max(negro, 1 - cl(Math.abs(t - x) / 0.18)); });
  $("#negro").style.opacity = negro;
  // título
  $("#titulo").style.opacity = k === "titulo" ? out3(tt / 0.5) * cl((b - t) / 0.4) : 0;
  $("#titulo b").style.backgroundPosition = `${120 - 140 * cl((tt - 0.3) / 1.8)}% 0`;
  $("#titulo small").style.opacity = out3((tt - 1.0) / 0.5);
  // subtítulos
  const l = L.find((x) => t >= x.ini - 0.05 && t < x.fin + 0.3), sub = $("#sub");
  if (l && k !== "sello") { if (ultimo !== l.txt) { ultimo = l.txt; sub.innerHTML = `<small>${{ orbi: "ORBI", sofia: "SOFÍA · IA DEL TALLER", julian: "JULIÁN · MESERO" }[l.quien]}</small>${l.txt}`; sub.className = l.quien; }
    sub.style.opacity = out3((t - l.ini + 0.05) / 0.12) * cl((l.fin + 0.3 - t) / 0.15); } else sub.style.opacity = 0;
  if (k === "sello") { $("#sello").style.opacity = out3(tt / 0.5);
    $("#o-final").innerHTML = `<svg viewBox="-240 -200 480 520" width="460" height="498">${ARMA_DEFS}${armadura(orbiCara(t, tt > 1 ? "guino" : "orgulloso", false), { visor: 1 - cl((tt - 0.4) / 0.4), t })}</svg>`;
    $("#frase").style.opacity = out3((tt - 0.8) / 0.4); $("#logo").style.opacity = out3((tt - 1.3) / 0.5); } else $("#sello").style.opacity = 0;
  grano(f);
}
// HUD del casco: arcos, lecturas y un aviso central
function hudCasco(t, k, aviso, d = {}) {
  const op = cl(k * 3);
  return `<g opacity="${op}" fill="none" stroke="#7fe8ff" stroke-width="3" font-family="Figtree">
    <circle cx="540" cy="960" r="300" stroke-dasharray="40 18" stroke-dashoffset="${t * 60}" opacity=".6"/><circle cx="540" cy="960" r="250" stroke-dasharray="4 10" opacity=".5"/>
    <path d="M540 640 v 40 M540 1240 v 40 M220 960 h 40 M820 960 h 40" stroke-width="4"/>
    <path d="M90 520 Q 40 960 90 1400" stroke-width="5" opacity=".7"/><path d="M990 520 Q 1040 960 990 1400" stroke-width="5" opacity=".7"/>
    ${d.alt ? `<text x="120" y="900" fill="#bff6ff" stroke="none" font-size="30" font-weight="700">ALT</text><text x="120" y="944" fill="#fff" stroke="none" font-size="40" font-weight="800">${d.alt} m</text>
    <text x="960" y="900" text-anchor="end" fill="#bff6ff" stroke="none" font-size="30" font-weight="700">VEL</text><text x="960" y="944" text-anchor="end" fill="#fff" stroke="none" font-size="40" font-weight="800">${d.vel} km/h</text>` : ""}
    <rect x="290" y="1340" width="500" height="70" rx="10" fill="rgba(5,30,45,.75)" stroke="#7fe8ff"/><text x="540" y="1388" text-anchor="middle" fill="#e8fbff" stroke="none" font-size="34" font-weight="800" letter-spacing="3">${aviso}</text></g>`;
}
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
