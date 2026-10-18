// «Mesero nocturno» (homenaje a Taxi Driver). render(t, f)
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const rebote = (x) => { x = cl(x); return 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
const E = LINEA.escenas, L = LINEA.lineas;
const escenaDe = (t) => Object.keys(E).find((k) => t >= E[k][0] && t < E[k][1]) || "sello";
const habla = (q, t) => L.some((l) => (Array.isArray(q) ? q.includes(l.quien) : l.quien === q) && t >= l.ini && t < l.fin);
const lin = (q, esc, n = 0) => L.filter((l) => l.quien === q && (!esc || l.esc === esc))[n];
const boca = (t) => 0.25 + 0.6 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 4.7));
const g = (x, y, s, c, op = 1, rot = 0) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})" opacity="${op}">${c}</g>`;
const azar = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
function orbiCara(t, nombre, h, extra = {}) {
  const base = { ...EXPRESIONES[nombre], ...extra };
  if (h) { const a = 0.25 + 0.55 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 5.3)); base.boca = nombre === "feliz" ? [0.9, 1.2, Math.max(0.2, a)] : [0.12, 0.7, a * 0.8]; }
  if ((t % 3.7) < 0.12 && base.oi > 0) { base.oi = 0.08; if (base.od > 0) base.od = 0.08; }
  return orbi(nombre, { e: base, anillo: -10 + 4 * Math.sin(t * 1.3), brillo: 0.5 }).replace("<svg ", '<svg width="380" height="380" ');
}
const TRAVIS = { oi: 0.42, od: 0.42, ci: [6, 10], cd: [6, -10], boca: [-0.05, 0.7, 0], mira: [0, 0] };   // mirada fija, cejas bajas
const DEFS = `<defs>
  <radialGradient id="neblina"><stop offset="0" stop-color="rgba(230,230,240,.55)"/><stop offset="1" stop-color="rgba(230,230,240,0)"/></radialGradient>
  <radialGradient id="bokeh"><stop offset="0" stop-color="rgba(255,255,255,.9)"/><stop offset=".6" stop-color="rgba(255,255,255,.35)"/><stop offset="1" stop-color="rgba(255,255,255,0)"/></radialGradient>
  <linearGradient id="asfalto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1418"/><stop offset="1" stop-color="#050406"/></linearGradient>
  <radialGradient id="rojo"><stop offset="0" stop-color="rgba(255,40,60,.55)"/><stop offset="1" stop-color="rgba(255,40,60,0)"/></radialGradient>
  <radialGradient id="verde"><stop offset="0" stop-color="rgba(60,255,170,.35)"/><stop offset="1" stop-color="rgba(60,255,170,0)"/></radialGradient>
</defs>`;
// ---------- Calle de noche con avisos de neón (se desplaza con «avance») ----------
const AVISOS = [["RESTAURANTE", "#ff3b5c"], ["BAR", "#2fe0ff"], ["ABIERTO", "#ff3fb5"], ["PIZZA", "#ffb347"], ["COMIDA", "#4dff9a"], ["CAFÉ", "#ff3b5c"], ["HOTEL", "#2fe0ff"], ["ASADERO", "#ffb347"]];
function calle(t, avance) {
  let w = `<rect x="-900" y="-900" width="2880" height="3800" fill="#07060a"/>`;
  for (let i = 0; i < 18; i++) { const x = ((i * 260 - avance * 0.25) % 4680 + 4680) % 4680 - 1400, h = 500 + azar(i) * 700;
    w += `<rect x="${x}" y="${1240 - h - 300}" width="240" height="${h + 300}" fill="#0c0b12"/>`;
    for (let j = 0; j < 14; j++) if (azar(i * 17 + j) > 0.6) w += `<rect x="${x + 20 + (j % 4) * 55}" y="${1240 - h - 260 + Math.floor(j / 4) * 80}" width="22" height="34" fill="#e8b45f" opacity=".45"/>`; }
  for (let i = 0; i < 8; i++) { const x = ((i * 520 - avance) % 4160 + 4160) % 4160 - 1300, [txt, c] = AVISOS[i], on = (Math.sin(t * (9 + i) + i) > -0.85) ? 1 : 0.2;
    w += `<rect x="${x}" y="500" width="500" height="760" fill="${i % 2 ? "#14101a" : "#18121a"}"/><rect x="${x + 40}" y="900" width="420" height="320" fill="#2a1d14" opacity=".9"/><rect x="${x + 40}" y="900" width="420" height="320" fill="${c}" opacity=".08"/>
      <g opacity="${on}"><rect x="${x + 50}" y="760" width="400" height="100" rx="14" fill="none" stroke="${c}" stroke-width="7" style="filter:drop-shadow(0 0 16px ${c})"/>
      <text x="${x + 250}" y="830" text-anchor="middle" font-size="${txt.length > 8 ? 46 : 60}" font-weight="800" fill="#fff" font-family="Figtree" style="filter:drop-shadow(0 0 12px ${c})">${txt}</text></g>
      <rect x="${x + 220}" y="1330" width="60" height="560" fill="${c}" opacity="${0.12 * on}"/>`; }
  w += `<rect x="-900" y="1240" width="2880" height="1700" fill="url(#asfalto)" opacity=".92"/><rect x="-900" y="1240" width="2880" height="16" fill="#2a2228"/>`;
  for (let i = 0; i < 8; i++) { const x = ((i * 520 - avance) % 4160 + 4160) % 4160 - 1300, c = AVISOS[i][1]; w += `<rect x="${x + 120}" y="1300" width="260" height="500" fill="${c}" opacity=".07"/>`; }
  for (let i = 0; i < 10; i++) { const x = ((i * 300 - avance * 1.4) % 3000 + 3000) % 3000 - 900; w += `<rect x="${x}" y="1640" width="150" height="14" fill="#d8c070" opacity=".5"/>`; }
  return w;
}
function vapor(t, x, y, k = 1) {
  return Array.from({ length: 6 }, (_, i) => { const ph = (t * 0.25 + i / 6) % 1; return `<ellipse cx="${x + Math.sin(t * 0.7 + i) * 60}" cy="${y - ph * 900}" rx="${(200 + ph * 400) * k}" ry="${(120 + ph * 260) * k}" fill="url(#neblina)" opacity="${(1 - ph) * k}"/>`; }).join("");
}
// ---------- Baño con espejo (gancho y escena del espejo) ----------
function bano(t, contenido) {
  let w = `<rect x="-900" y="-900" width="2880" height="3800" fill="#1d2a26"/>`;
  for (let y = -900; y < 2900; y += 90) for (let x = -900; x < 1980; x += 90) w += `<rect x="${x + 3}" y="${y + 3}" width="84" height="84" fill="${(x / 90 + y / 90) % 2 ? "#243530" : "#22322d"}"/>`;
  w += `<rect x="150" y="260" width="780" height="1080" rx="16" fill="#3a3f3c"/><rect x="180" y="290" width="720" height="1020" fill="#0b0d10"/>
    <clipPath id="espejo"><rect x="180" y="290" width="720" height="1020"/></clipPath>
    <g clip-path="url(#espejo)"><rect x="180" y="290" width="720" height="1020" fill="#141018"/>
      <rect x="560" y="290" width="360" height="1020" fill="#3a0f18" opacity=".7"/><circle cx="880" cy="500" r="${520 + 30 * Math.sin(t * 13)}" fill="url(#rojo)"/><circle cx="200" cy="900" r="420" fill="url(#verde)"/>
      ${contenido}
      <path d="M180 290 L 900 1310" stroke="rgba(255,255,255,.05)" stroke-width="160"/><path d="M640 290 L 900 700 L 860 290Z" fill="rgba(255,255,255,.04)"/>
      ${Array.from({ length: 14 }, (_, i) => `<circle cx="${200 + azar(i) * 680}" cy="${300 + azar(i + 30) * 1000}" r="${3 + azar(i + 9) * 9}" fill="rgba(200,190,160,.18)"/>`).join("")}</g>
    <rect x="120" y="1360" width="840" height="70" rx="20" fill="#d9dcd6"/><path d="M220 1430 Q 540 1600 860 1430Z" fill="#c4c8c1"/><rect x="520" y="1330" width="40" height="50" rx="8" fill="#9aa0a6"/>
    <rect x="-900" y="1600" width="2880" height="1400" fill="#141c19"/>`;
  return w;
}
// ---------- Restaurante (mesas que esperan / Apex Play en acción) ----------
function salon(t, modo) {
  const k = modo === "accion";
  let w = restaurante(t, k ? 1 : 0.55);
  // ventana de cocina
  w += `<rect x="760" y="560" width="300" height="200" rx="10" fill="#f3d7a2" opacity="${k ? 0.9 : 0.4}"/><rect x="760" y="540" width="300" height="34" fill="#2a1d14"/><text x="910" y="566" text-anchor="middle" font-size="26" font-weight="800" fill="#f1c76a" font-family="Figtree">COCINA</text>`;
  // reloj de pared: corre rápido mientras esperan
  const ang = k ? t * 30 : t * 720;
  w += `<g transform="translate(150 640)"><circle r="70" fill="#f4f1ea" stroke="#2a1d14" stroke-width="10"/><line x2="0" y2="-50" stroke="#111" stroke-width="6" transform="rotate(${ang})"/><line x2="0" y2="-34" stroke="#111" stroke-width="8" transform="rotate(${ang / 12})"/></g>`;
  const M = [[230, 1330], [800, 1300], [520, 1640]];
  const mesasL = lin("narra", "mesas"), se = mesasL ? cl((t - mesasL.ini - 4.0) / 1.2) : 0;
  M.forEach(([x, y], i) => {
    if (!k && i === 2 && se > 0) { const sx = x + se * 700; w += g(sx, y - 40, 1, persona({ piel: PIELES[i + 1], pelo: "largo", camisa: "#8a3b5c", boca: 0.2, cejas: "enojo", mira: 8 }), 1 - se * 0.3, se * 6); }
    else w += g(x, y - 40, 1, persona({ piel: PIELES[i], pelo: ["corto", "largo", "calvo"][i], camisa: ["#3d6fb6", "#8a3b5c", "#5a7a3a"][i], brazo: k ? 0 : (Math.sin(t * 5 + i * 2) > -0.2 ? 1 : 0), boca: k ? 0.85 : 0.2, cejas: k ? "arriba" : "enojo", mira: k ? 0 : 6 }));
    w += mesa(x, y);
    if (k) { const sc = lin("narra", "accion"), qr = sc ? cl((t - sc.ini) / 0.6) : 1; w += g(x - 70, y - 70, 0.7 * rebote(qr), soporteQR(0.7 + 0.3 * Math.sin(t * 4 + i)));
      w += g(x + 70, y - 120 + Math.sin(t * 3 + i) * 6, 0.8, celular(0.5 + 0.5 * Math.abs(Math.sin(t * 3 + i)))); }
    else w += `<g transform="translate(${x + 40} ${y - 260})" opacity="${0.6 + 0.4 * Math.sin(t * 6 + i)}"><circle r="34" fill="#fff"/><text y="14" text-anchor="middle" font-size="44" font-weight="800" fill="#c01b2c" font-family="Figtree">?</text></g>`;
  });
  // Julián: corriendo y sudando, o tranquilo con los platos
  if (k) { const x = lerp(1150, 640, out3((t - E.accion[0] - 2.5) / 1.6)); w += g(x, 1260, 0.95, julian({ bandeja: true, platos: 3, boca: "", mira: -4 })); }
  else { const x = 540 + Math.sin(t * 2.4) * 420; w += g(x, 1260, 0.95, julian({ bandeja: true, platos: 2, inclina: Math.sin(t * 9) * 10, sudor: true, ojos: "grandes", boca: "o" }), 1, Math.sin(t * 12) * 3); }
  // pedidos que vuelan a la cocina
  if (k) { const ac = lin("narra", "accion"); if (ac) ["Mesa 1 · Bandeja paisa", "Mesa 2 · 2 limonadas", "Mesa 3 · Ajiaco"].forEach((txt, i) => {
    const q = cl((t - ac.ini - 3.1 - i * 0.45) / 1.0); if (q <= 0) return; const [x0, y0] = M[i], x = lerp(x0, 910, ease(q)), y = lerp(y0 - 200, 660, ease(q)) - Math.sin(q * Math.PI) * 160, s = q < 1 ? 1 : 0;
    w += `<g transform="translate(${x} ${y}) scale(${lerp(1, 0.6, q)})" opacity="${1 - cl((q - 0.9) * 10) * 0}"><rect x="-170" y="-34" width="340" height="68" rx="34" fill="#0b1626" stroke="#2fbbe8" stroke-width="4"/>
      <text y="10" text-anchor="middle" font-size="28" font-weight="800" fill="#fff" font-family="Figtree">${txt}</text></g>`; }); }
  return w;
}
// ---------- Cámara ----------
const CAM = { gancho: [[540, 760, 2.0], [540, 780, 2.35]], titulo: [[540, 960, 1], [540, 960, 1]], taxi: [[720, 1150, 1.5], [560, 1080, 1.1]], mesas: [[520, 1150, 1.3], [540, 1130, 1.4]],
  espejo: [[540, 820, 1.25], [540, 800, 1.45]], accion: [[540, 1150, 1.25], [560, 1120, 1.3]], final: [[540, 800, 1.0], [540, 800, 1.08]], sello: [[540, 960, 1], [540, 960, 1]] };
function camara(t) {
  const k = escenaDe(t), [a, b] = E[k], p = (t - a) / (b - a), [c0, c1] = CAM[k];
  let c = c0.map((v, i) => lerp(v, c1[i], ease(p)));
  if (k === "mesas") { const l = lin("narra", "mesas"); if (l) { const q1 = ease((t - l.ini - 1.6) / 0.5), q2 = ease((t - l.ini - 3.8) / 0.6);
    c = c.map((v, i) => lerp(lerp(v, [560, 1150, 1.6][i], q1), [700, 1250, 1.45][i], q2)); } }
  if (k === "espejo") { const l = lin("orbi", "espejo"); if (l) { const q = ease((t - l.ini + 0.4) / 0.4); c = c.map((v, i) => lerp(v, [560, 900, 1.15][i], q)); } }
  if (k === "accion") { const l = lin("narra", "accion"); if (l) { const q = ease((t - l.ini - 3.0) / 0.5), q2 = ease((t - l.ini - 4.6) / 0.6);
    c = c.map((v, i) => lerp(lerp(v, [300, 1120, 1.6][i], q), [700, 1000, 1.25][i], q2)); } }
  return c;
}
let ultimo = "";
async function render(t, f) {
  const k = escenaDe(t), [a, b] = E[k], tt = t - a;
  let w = "";
  if (k === "gancho" || k === "espejo") {
    let cara = "enojado", extra = TRAVIS, ladeo = 0, carta = "";
    if (k === "espejo") {
      const l1 = lin("lento", "espejo", 0), l2 = lin("lento", "espejo", 1), o3 = lin("orbi", "espejo");
      ladeo = l2 && t > l2.ini ? -10 * ease((t - l2.ini) / 0.3) : (l1 && t > l1.ini ? 8 * ease((t - l1.ini) / 0.3) : 0);
      if (l1 && t < l1.fin + 0.3) { cara = "sarcastico"; extra = { oi: 0.4, od: 0.6 }; }
      if (o3 && t > o3.ini - 0.6) {   // la tarjeta QR sale disparada de la manga, como el riel del arma en la película
        const q = out3((t - o3.ini + 0.6) / 0.25), gira = (1 - q) * 540;
        carta = `<g transform="translate(${lerp(900, 780, q)} ${lerp(1250, 1080, q)}) rotate(${gira - 8 * q}) scale(${lerp(0.3, 0.85, q)})"><rect x="-100" y="-130" width="200" height="260" rx="20" fill="#0b1626" stroke="#2fbbe8" stroke-width="6"/>
          <g transform="translate(0 -20) scale(1.6)">${soporteQR(0).replace(/<path[^>]*\/>/, "").replace(/<circle[^>]*\/>/, "")}</g><text y="110" text-anchor="middle" font-size="26" font-weight="800" fill="#fff" font-family="Figtree">MESA 4</text></g>`;
        cara = "guino"; extra = {};
        if (t > o3.fin - 0.2) { const r = rebote((t - o3.fin + 0.2) / 0.4);
          carta += `<g transform="translate(440 1180) scale(${r})"><rect x="-200" y="-40" width="400" height="80" rx="40" fill="rgba(5,30,20,.95)" stroke="#2ee59d" stroke-width="5"/><text y="12" text-anchor="middle" font-size="32" font-weight="800" fill="#2ee59d" font-family="Figtree">✓ Enviado a cocina</text></g>`; }
      }
    }
    const den = `<g transform="translate(540 ${820 + Math.sin(t * 1.5) * 6}) rotate(${ladeo}) scale(1.15)">${chaqueta(orbiCara(t, cara, habla(["orbi", "lento"], t), extra))}</g>`;
    w = bano(t, den + carta);
  }
  if (k === "titulo" || k === "sello") w = calle(t, t * 120) + `<rect x="-900" y="-900" width="2880" height="3800" fill="rgba(0,0,0,.55)"/>`;
  if (k === "taxi") {
    const x = lerp(1500, 540, out3((tt - 0.2) / 3.0)), bob = Math.sin(t * 9) * 3;
    const ventana = `<rect x="40" y="-150" width="280" height="140" fill="#1a1620"/><g transform="translate(150 -60) scale(.36)">${chaqueta(orbiCara(t, "normal", false, TRAVIS))}</g>`;
    w = calle(t, t * 520) + vapor(t, 560, 1360, 1 - cl((tt - 2) / 3) * 0.6) + g(x, 1150 + bob, 1, taxi(t, { ventana })) + vapor(t + 3, 300, 1500, 0.8 - cl((tt - 2) / 3) * 0.6);
  }
  if (k === "mesas") {
    w = salon(t, "mesas");
    // marco de la ventanilla del taxi, con gotas
    w += `<path d="M-900 -900 H 1980 V 2900 H -900Z M60 300 Q 60 220 140 220 H 940 Q 1020 220 1020 300 V 1560 Q 1020 1640 940 1640 H 140 Q 60 1640 60 1560Z" fill="#0b0a0d" fill-rule="evenodd"/>
      <path d="M60 300 Q 60 220 140 220 H 940 Q 1020 220 1020 300 V 1560 Q 1020 1640 940 1640 H 140 Q 60 1640 60 1560Z" fill="none" stroke="#f2b705" stroke-width="14"/>
      ${Array.from({ length: 40 }, (_, i) => { const y = 240 + ((azar(i) * 1400 + t * (40 + azar(i + 4) * 120)) % 1400); return `<ellipse cx="${80 + azar(i + 9) * 920}" cy="${y}" rx="${5 + azar(i + 2) * 8}" ry="${8 + azar(i + 2) * 12}" fill="rgba(220,235,255,.22)" stroke="rgba(255,255,255,.3)" stroke-width="2"/>`; }).join("")}`;
  }
  if (k === "accion") w = salon(t, "accion");
  if (k === "final") {
    // retrovisor: los ojos de Orbi, luces de la ciudad pasando
    const cara = habla("orbi", t) ? "sarcastico" : (t > (lin("orbi", "final")?.fin || 99) ? "guino" : "normal");
    w = `<rect x="-900" y="-900" width="2880" height="3800" fill="#050407"/>`;
    for (let i = 0; i < 16; i++) { const ph = (t * 0.9 + azar(i)) % 1, c = AVISOS[i % 8][1]; w += `<ellipse cx="${lerp(1500, -400, ph)}" cy="${200 + azar(i + 3) * 500}" rx="${90 + azar(i) * 140}" ry="${60 + azar(i) * 80}" fill="${c}" opacity=".22"/>`; }
    w += `<rect x="-900" y="560" width="2880" height="3000" fill="#0a090c"/><path d="M-900 560 H 1980" stroke="#1d1a22" stroke-width="30"/>
      <rect x="520" y="560" width="40" height="150" fill="#16141a"/>
      <rect x="110" y="680" width="860" height="300" rx="70" fill="#16141a"/><clipPath id="retro"><rect x="135" y="705" width="810" height="250" rx="56"/></clipPath>
      <g clip-path="url(#retro)"><rect x="135" y="705" width="810" height="250" fill="#120f18"/>
        ${Array.from({ length: 6 }, (_, i) => { const ph = (t * 0.7 + i / 6) % 1; return `<rect x="${lerp(1000, 0, ph)}" y="705" width="120" height="250" fill="${AVISOS[i][1]}" opacity=".18"/>`; }).join("")}
        <g transform="translate(560 880) scale(2.6)"><g transform="translate(-190 -190)">${orbiCara(t, cara, habla("orbi", t), cara === "normal" ? TRAVIS : {})}</g></g></g>
      <rect x="135" y="705" width="810" height="40" rx="20" fill="rgba(255,255,255,.06)"/>
      <path d="M-900 1500 Q 540 1380 1980 1500 V 2900 H -900Z" fill="#141217"/><circle cx="540" cy="1800" r="330" fill="none" stroke="#1d1b22" stroke-width="60"/>
      <g transform="translate(870 1350)"><rect x="-90" y="-50" width="180" height="100" rx="10" fill="#0b0b0e" stroke="#f2b705" stroke-width="4"/><text y="14" text-anchor="middle" font-size="40" font-weight="800" fill="#ff4a3a" font-family="Figtree" style="filter:drop-shadow(0 0 8px #ff2a2a)">$ 0.00</text></g>`;
  }
  const [cx, cy, cs] = camara(t);
  const temblor = k === "taxi" ? 2 : 0, sx = temblor * Math.sin(f * 3.1), sy = temblor * Math.cos(f * 2.3);
  $("#escena").innerHTML = `<svg viewBox="0 0 1080 1920" width="1080" height="1920">${DEFS}<g transform="translate(${540 + sx} ${960 + sy}) scale(${cs}) translate(${-cx} ${-cy})">${w}</g></svg>`;
  // lluvia en primer plano en la calle
  $("#lluvia").innerHTML = ["titulo", "taxi"].includes(k) ? Array.from({ length: 120 }, (_, i) => { const v = 2000 + azar(i + 5) * 900, x = azar(i) * 1160 - 40, y = ((azar(i + 99) * 2100 + t * v) % 2100) - 100, l = 40 + azar(i + 7) * 50;
    return `<line x1="${x}" y1="${y}" x2="${x - l * 0.12}" y2="${y + l}" stroke="rgba(230,220,200,${0.14 + azar(i + 3) * 0.22})" stroke-width="2"/>`; }).join("") : "";
  // corte seco del gancho al título; fundidos cortos en lo demás
  let negro = 0; Object.keys(E).forEach((e) => { const x = E[e][0]; if (x > 0 && e !== "titulo") negro = Math.max(negro, 1 - cl(Math.abs(t - x) / 0.16)); });
  $("#negro").style.opacity = negro;
  $("#tinte").style.background = k === "accion" ? "linear-gradient(180deg, rgba(255,190,110,.12), rgba(47,187,232,.12))" : "linear-gradient(180deg, rgba(255,40,40,.16), rgba(20,90,70,.22))";
  // título
  $("#titulo").style.opacity = k === "titulo" ? cl(tt / 0.08) * cl((b - t) / 0.3) : 0;
  $("#titulo b").style.transform = `scaleX(.82) scale(${1.06 - 0.06 * out3(tt / 2)})`;
  $("#titulo b").style.opacity = (tt < 0.12 || (tt > 0.3 && tt < 0.36)) ? 0.3 : 1;
  $("#titulo small").style.opacity = out3((tt - 0.6) / 0.5);
  // subtítulos
  const l = L.find((x) => t >= x.ini - 0.05 && t < x.fin + 0.3), sub = $("#sub");
  if (l && k !== "sello" && k !== "titulo") { if (ultimo !== l.txt) { ultimo = l.txt; sub.innerHTML = `${l.quien === "narra" ? "<small>DIARIO DE ORBI</small>" : ""}${l.txt}`; sub.className = l.quien; }
    sub.style.opacity = out3((t - l.ini + 0.05) / 0.1) * cl((l.fin + 0.3 - t) / 0.15); } else sub.style.opacity = 0;
  // cierre de marca
  if (k === "sello") { $("#sello").style.opacity = out3(tt / 0.4);
    $("#o-final").innerHTML = `<svg viewBox="-230 -230 460 520" width="500" height="565">${chaqueta(orbiCara(t, tt < 0.9 ? "normal" : "guino", false, tt < 0.9 ? TRAVIS : {}))}</svg>`;
    $("#frase").style.opacity = out3((tt - 0.5) / 0.4); $("#logo").style.opacity = out3((tt - 1.0) / 0.5); } else $("#sello").style.opacity = 0;
  grano(f);
}
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
