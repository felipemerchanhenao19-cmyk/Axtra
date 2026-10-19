// «Orbi en la cocina»: escena genérica que se arma con el guion (EP) y la línea de tiempo de las voces (LINEA). render(t, f)
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const rebote = (x) => { x = cl(x); return 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
const L = LINEA.lineas, SELLO = LINEA.sello, PISO = 1260, CENTRO = 1090;
const habla = (q, t) => L.some((l) => l.quien === q && t >= l.ini && t < l.fin);
const bocaT = (t) => 0.25 + 0.6 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 4.7));
const ev = (l) => EP.lineas[l.i][3] || {};
const yDe = (q) => EP.reparto[q].tipo === "orbi" ? (EP.reparto[q].y || 800) : CENTRO;
// Estado de cada personaje en el tiempo t: se aplican los eventos de las líneas que ya empezaron
function estado(t) {
  const S = {};
  for (const [q, r] of Object.entries(EP.reparto)) S[q] = { q, r, vivo: EP.inicio.includes(q), x0: r.x, x1: r.x, tm: -9, te: EP.inicio.includes(q) ? -9 : null, ts: null, cara: r.tipo === "orbi" ? "normal" : "normal", pose: "abajo", tp: -9, acc: r.acc || [] };
  for (const l of L) {
    const a = l.ini - 0.25; if (t < a) break; const e = ev(l);
    (e.entra || []).forEach((q) => { S[q].vivo = true; S[q].te = a; S[q].ts = null; });
    (e.sale || []).forEach((q) => { S[q].ts = a; });
    for (const [q, x] of Object.entries(e.mueve || {})) { const s = S[q], xa = posX(s, a); s.x0 = xa; s.x1 = x; s.tm = a; }
    for (const [q, c] of Object.entries(e.caras || {})) S[q].cara = c;
    for (const [q, p] of Object.entries(e.poses || {})) { S[q].pose = p; S[q].tp = a; }
    for (const [q, c] of Object.entries(e.acc || {})) S[q].acc = c;
  }
  return S;
}
function posX(s, t) { let x = lerp(s.x0, s.x1, ease((t - s.tm) / 0.8)); if (s.ts !== null) x = lerp(x, 1450, ease((t - s.ts - 0.6) / 0.9)); return x; }
// Cámara: se acerca a quien habla; en las líneas de drama hace el triple zoom de telenovela
const CAMS = [{ t: -1, c: [540, 1090, 1.12] }];
L.forEach((l, i) => {
  const r = EP.reparto[l.quien], e = ev(l), x = (e.mueve && e.mueve[l.quien]) ?? r.x, sx = cl(x, 150, 930), sy = yDe(l.quien);
  const base = [lerp(540, sx, 0.25), lerp(1090, sy, 0.3), i === 0 ? 1.12 : 1.22];
  CAMS.push({ t: l.ini - 0.3, c: base });
  if (e.drama) { [1.3, 1.55, 1.8].forEach((z, k) => CAMS.push({ t: l.ini + k * 0.32, c: [sx, sy - 20, z], dur: 0.12 })); CAMS.push({ t: l.fin + 0.15, c: base }); }
});
CAMS.push({ t: SELLO - 0.4, c: [540, 1090, 1.1] }); CAMS.sort((a, b) => a.t - b.t);
function camara(t) {
  let c = CAMS[0].c;
  for (let i = 1; i < CAMS.length && CAMS[i].t <= t; i++) { const k = CAMS[i], fin = Math.min(t, CAMS[i + 1] ? CAMS[i + 1].t : t); c = c.map((v, j) => lerp(v, k.c[j], ease((fin - k.t) / (k.dur || 0.5)))); }
  return c;
}
function orbiCara(t, nombre, h) {
  const base = { ...EXPRESIONES[nombre] || EXPRESIONES.normal };
  if (h) { const a = 0.25 + 0.55 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 5.3)); base.boca = nombre === "feliz" ? [0.9, 1.2, Math.max(0.2, a)] : [0.15, 0.7, a]; }
  if ((t % 3.3) < 0.12 && base.oi > 0) { base.oi = 0.08; if (base.od > 0) base.od = 0.08; }
  return orbi(nombre, { e: base, anillo: -10 + 4 * Math.sin(t * 1.3) }).replace("<svg ", '<svg width="380" height="380" ');
}
const g = (x, y, s, c, rot = 0, op = 1) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})" opacity="${op}">${c}</g>`;
function personaje(s, t) {
  const r = s.r, h = habla(s.q, t), fase = r.x * 0.013;
  if (!s.vivo || (s.ts !== null && t > s.ts + 1.6)) return "";
  let x = posX(s, t), y = yDe(s.q), esc = 1, rot = 0, extra = "";
  const caminando = (t - s.tm < 0.8 && t > s.tm) || (s.ts !== null && t > s.ts + 0.6);
  if (s.te !== null && t - s.te < 0.6 && r.tipo === "orbi") esc = rebote((t - s.te) / 0.6);
  else if (s.te !== null && t - s.te < 0.5 && !(r.x < -100 || r.x > 1180)) esc = rebote((t - s.te) / 0.5);
  if (r.tipo === "orbi") {
    const cara = { normal: "normal", feliz: "feliz", sarcastico: "sarcastico", sorprendido: "sorprendido", triste: "triste", enojo: "enojado", guino: "guino", orgulloso: "orgulloso" }[s.cara] || "normal";
    let w = `<g transform="translate(${x} ${y + Math.sin(t * 2.2) * 12}) scale(${0.72 * esc})"><g transform="translate(-190 -190)">${orbiCara(t, cara, h)}</g></g>`;
    if (s.te !== null && t - s.te < 1) { const q = t - s.te; w += Array.from({ length: 12 }, (_, i) => `<circle cx="${x + Math.cos(i * .52) * q * 320}" cy="${y + Math.sin(i * .52) * q * 320}" r="${8 * (1 - q)}" fill="#bff0ff"/>`).join(""); }
    return w;
  }
  if (r.tipo === "comi") {
    const cara = ["diva", "shock", "enojo", "llanto"].includes(s.cara) ? s.cara : "diva";
    return g(x, PISO - 240 * 0.68 + Math.sin(t * 2.6) * 6, 0.68, comi({ cara, boca: h ? bocaT(t) : 0, abanico: cara === "diva" ? Math.sin(t * 7) * 12 : null, brazoArriba: s.ts !== null }), caminando ? Math.sin(t * 14) * 4 : 0);
  }
  let pose = s.pose, brazo = ["abajo", "arriba", "cabeza", "jarra", "dos", "saluda"].includes(pose) ? pose : "abajo";
  let dy = Math.sin(t * 2 + fase) * 4, sq = 1 + (h ? 0.025 * Math.sin(t * 16) : 0);
  if (pose === "desmayo") { const q = ease((t - s.tp) / 0.5); rot = 78 * q; dy += 10 * q; brazo = "dos"; }
  if (pose === "brinco") dy -= Math.abs(Math.sin((t - s.tp) * 8)) * 70;
  if (caminando) { dy -= Math.abs(Math.sin(t * 12)) * 18; rot = Math.sin(t * 12) * 4; }
  const cuerpo = comida(r.tipo, { cara: s.cara, boca: h ? bocaT(t) : 0, acc: s.acc, brazo, t, fase, banda: r.banda, mira: (540 - x) / 300 });
  return `<g transform="translate(${x} ${y + dy}) scale(${0.95 * esc}) rotate(${rot} 0 170) scale(${1 / sq} ${sq})"><g transform="translate(0 ${170 * (1 - sq)})">${cuerpo}</g></g>`;
}
// ---------- Fondos
function cocina(t, oscuro = false) {
  const pared = oscuro ? "#1b2036" : "#f2e2c4", azul = oscuro ? "#232b47" : "#d4ebe5", linea = oscuro ? "#2e3756" : "#b9d6cf";
  let w = `<rect x="-600" y="-400" width="2300" height="1700" fill="${pared}"/>`;
  w += `<rect x="-600" y="560" width="2300" height="700" fill="${azul}"/>` + Array.from({ length: 16 }, (_, i) => `<line x1="-600" y1="${560 + i * 45}" x2="1700" y2="${560 + i * 45}" stroke="${linea}" stroke-width="3"/>`).join("")
    + Array.from({ length: 40 }, (_, i) => Array.from({ length: 16 }, (_, j) => `<line x1="${-600 + i * 90 + (j % 2) * 45}" y1="${560 + j * 45}" x2="${-600 + i * 90 + (j % 2) * 45}" y2="${605 + j * 45}" stroke="${linea}" stroke-width="3"/>`).join("")).join("");
  // ventana
  w += `<rect x="90" y="160" width="300" height="300" rx="14" fill="${oscuro ? "#0b1030" : "#9fd6f2"}" stroke="${oscuro ? "#39314a" : "#8a5a34"}" stroke-width="16"/><line x1="240" y1="160" x2="240" y2="460" stroke="${oscuro ? "#39314a" : "#8a5a34"}" stroke-width="12"/><line x1="90" y1="310" x2="390" y2="310" stroke="${oscuro ? "#39314a" : "#8a5a34"}" stroke-width="12"/>`;
  if (oscuro) w += `<circle cx="160" cy="230" r="44" fill="#f4f1d0"/><circle cx="178" cy="220" r="40" fill="#0b1030"/>`;
  else w += `<ellipse cx="160" cy="240" rx="60" ry="22" fill="#fff" opacity=".8"/><ellipse cx="320" cy="390" rx="50" ry="18" fill="#fff" opacity=".7"/>`;
  // repisa con frascos
  w += `<rect x="560" y="430" width="560" height="20" rx="6" fill="#8a5a34"/>` + [600, 690, 780, 880, 980].map((x, i) => `<rect x="${x}" y="${330 + (i % 2) * 20}" width="70" height="${100 - (i % 2) * 20}" rx="12" fill="${["#e8a33d", "#c0392b", "#7cc142", "#f4c430", "#8e5a2b"][i]}" opacity="${oscuro ? .45 : .85}"/><rect x="${x - 4}" y="${322 + (i % 2) * 20}" width="78" height="16" rx="6" fill="#5b3a20"/>`).join("");
  // ollas colgadas
  w += [620, 800, 960].map((x, i) => `<line x1="${x}" y1="-400" x2="${x}" y2="${150 + i * 20}" stroke="#555" stroke-width="5"/><circle cx="${x}" cy="${210 + i * 20}" r="${50 - i * 6}" fill="${oscuro ? "#3a3f50" : "#9aa3ad"}" stroke="#5c636d" stroke-width="6"/>`).join("");
  w += `<text x="760" y="${oscuro ? 545 : 540}" text-anchor="middle" font-family="Italiana, serif" font-size="56" fill="${oscuro ? "#5a4a6a" : "#8a5a34"}">La Fonda</text>`;
  w += mesa(oscuro);
  return w;
}
function mesa(oscuro = false, color = "#8a5a34") {
  return `<rect x="-600" y="${PISO}" width="2300" height="40" fill="${oscuro ? "#4a4a5a" : "#ece6dc"}"/><rect x="-600" y="${PISO + 40}" width="2300" height="900" fill="${oscuro ? "#2a1e1a" : color}"/>`
    + Array.from({ length: 14 }, (_, i) => `<rect x="${-560 + i * 180}" y="${PISO + 80}" width="150" height="320" rx="10" fill="rgba(0,0,0,.14)"/>`).join("");
}
function vitrinaFrente(t) {
  return `<rect x="-600" y="880" width="2300" height="${PISO - 880}" fill="rgba(210,235,255,.13)"/>` + [80, 520, 900].map((x) => `<path d="M${x} 900 L ${x + 90} 900 L ${x - 30} ${PISO} L ${x - 120} ${PISO} Z" fill="rgba(255,255,255,.12)"/>`).join("")
    + `<rect x="-600" y="868" width="2300" height="22" fill="#c4ccd4"/><rect x="-600" y="${PISO - 10}" width="2300" height="14" fill="#c4ccd4"/>
    <g transform="translate(540 930)"><rect x="-120" y="-26" width="240" height="44" rx="10" fill="#c0392b"/><text y="8" text-anchor="middle" font-size="26" font-weight="800" fill="#fff" font-family="Figtree">VITRINA</text></g>`;
}
function consultorio(t) {
  return `<rect x="-600" y="-400" width="2300" height="1700" fill="#e1d8f0"/><rect x="-600" y="900" width="2300" height="400" fill="#cbbfe0"/><rect x="-600" y="894" width="2300" height="12" fill="#a898c8"/>
    <g transform="translate(250 420)"><rect x="-150" y="-110" width="300" height="220" fill="#fffbea" stroke="#b08a3a" stroke-width="16"/><text y="-30" text-anchor="middle" font-family="Italiana, serif" font-size="42" fill="#5a4a2a">Dr. Orbi</text>
      <text y="16" text-anchor="middle" font-family="Figtree" font-size="22" fill="#7a6a4a">Psicología de cocina</text><circle cy="62" r="22" fill="#c0392b"/></g>
    <g transform="translate(940 820)"><rect x="-40" y="0" width="80" height="120" rx="14" fill="#c0703a"/>${[-50, -10, 30, 60].map((a) => `<ellipse cx="0" cy="-40" rx="26" ry="80" fill="#4e8a22" transform="rotate(${a} 0 20)"/>`).join("")}</g>
    <rect x="-600" y="${PISO + 40}" width="2300" height="900" fill="#7a5a8a"/><ellipse cx="540" cy="${PISO + 120}" rx="520" ry="60" fill="#9a7aaa"/>
    <g><rect x="90" y="${PISO - 130}" width="560" height="170" rx="40" fill="#2a9d8f"/><rect x="60" y="${PISO - 260}" width="120" height="300" rx="50" fill="#21867a"/><rect x="90" y="${PISO - 10}" width="560" height="50" rx="20" fill="#1d7a6f"/>
      <rect x="110" y="${PISO + 40}" width="30" height="60" fill="#5b3a20"/><rect x="600" y="${PISO + 40}" width="30" height="60" fill="#5b3a20"/></g>`;
}
function estudio(t) {
  let w = `<rect x="-600" y="-400" width="2300" height="1700" fill="#0b1430"/>`;
  w += `<rect x="40" y="200" width="1000" height="420" rx="24" fill="#132a5a" stroke="#2fbbe8" stroke-width="6"/><text x="540" y="380" text-anchor="middle" font-family="Figtree" font-weight="900" font-size="96" fill="#fff">${EP.pantalla || "EL GRAN DEBATE"}</text>
    <text x="540" y="470" text-anchor="middle" font-family="Figtree" font-weight="700" font-size="40" fill="#5fc9f1" letter-spacing="8">EN VIVO</text><circle cx="330" cy="455" r="14" fill="#e01e3c" opacity="${0.5 + 0.5 * Math.sin(t * 5)}"/>`;
  w += [180, 540, 900].map((x, i) => `<path d="M${x} -100 L ${x - 220 + 60 * Math.sin(t * .8 + i)} ${PISO} L ${x + 220 + 60 * Math.sin(t * .8 + i)} ${PISO} Z" fill="rgba(160,210,255,.07)"/>`).join("");
  w += `<rect x="-600" y="${PISO}" width="2300" height="900" fill="#081024"/><rect x="-600" y="${PISO}" width="2300" height="8" fill="#2fbbe8" opacity=".6"/>`;
  return w;
}
function atriles() {
  return (EP.atriles || []).map((x) => `<g transform="translate(${x} 1195)"><path d="M-150 0 L 150 0 L 120 420 L -120 420 Z" fill="#14244a" stroke="#2fbbe8" stroke-width="6"/><rect x="-150" y="-16" width="300" height="24" rx="8" fill="#2fbbe8"/>
    <rect x="-90" y="90" width="180" height="60" rx="10" fill="#0b1430"/><text y="132" text-anchor="middle" font-family="Figtree" font-weight="800" font-size="34" fill="#fff">${x < 540 ? "MAÍZ" : "TRIGO"}</text></g>`).join("");
}
function pasarela(t) {
  let w = `<rect x="-600" y="-400" width="2300" height="1700" fill="#2a0b3a"/>`;
  w += Array.from({ length: 30 }, (_, i) => `<circle cx="${(i * 137) % 1300 - 100}" cy="${(i * 211) % 700 + 80}" r="${4 + (i % 3) * 3}" fill="#ffd166" opacity="${0.3 + 0.7 * Math.abs(Math.sin(t * 3 + i))}"/>`).join("");
  w += `<g transform="translate(540 520)"><rect x="-430" y="-80" width="860" height="160" rx="30" fill="#b5179e" stroke="#ffd166" stroke-width="6"/><text y="22" text-anchor="middle" font-family="Italiana, serif" font-size="82" fill="#fff">Señorita Cocina</text></g>`;
  w += [-1, 1].map((s) => `<path d="M${540 + s * 700} -400 Q ${540 + s * 520} 500 ${540 + s * 560} ${PISO} L ${540 + s * 900} ${PISO} L ${540 + s * 900} -400 Z" fill="#8a0f3a"/>`).join("");
  w += `<path d="M-600 ${PISO} L 1700 ${PISO} L 1700 2200 L -600 2200 Z" fill="#3a1050"/><path d="M200 ${PISO} L 880 ${PISO} L 1100 2200 L -20 2200 Z" fill="#f2e6f7" opacity=".9"/>`
    + Array.from({ length: 8 }, (_, i) => `<circle cx="${210 - i * 30}" cy="${PISO + 40 + i * 110}" r="10" fill="#ffd166"/><circle cx="${870 + i * 30}" cy="${PISO + 40 + i * 110}" r="10" fill="#ffd166"/>`).join("");
  return w;
}
function terrorFrente(t) {
  const parpadeo = Math.sin(t * 23) > 0.93 || Math.sin(t * 7.3 + 1) > 0.97 ? 0.35 : 0;
  return `<path d="M-120 -40 L 260 -40 L -120 300 Z M-120 -40 Q 80 60 160 -40 M-120 120 Q 30 60 60 -40" stroke="rgba(230,230,240,.5)" stroke-width="3" fill="none"/>
    ${[20, 1060].map((x) => `<g transform="translate(${x} ${PISO - 60})"><ellipse rx="70" ry="58" fill="#e8762b"/><path d="M0 -58 q 6 -24 18 -30" stroke="#4e8a22" stroke-width="10" fill="none"/>
      <path d="M-34 -10 l 14 -18 l 14 18 Z M6 -10 l 14 -18 l 14 18 Z M-34 20 Q 0 44 34 20 L 20 26 L 10 18 L 0 28 L -10 18 L -20 26 Z" fill="#ffd166"/></g>`).join("")}
    <rect x="-600" y="-400" width="2300" height="2700" fill="rgba(0,0,10,${0.1 + parpadeo})"/>`;
}
function fondo(t) { return { cocina: cocina(t), vitrina: cocina(t), consultorio: consultorio(t), estudio: estudio(t), terror: cocina(t, true), pasarela: pasarela(t) }[EP.fondo] || cocina(t); }
function frente(t) { return { vitrina: vitrinaFrente(t), estudio: atriles(), terror: terrorFrente(t) }[EP.fondo] || ""; }
// ---------- Cuadro
const PROD = { dom: ["Apex Domicilios", "Sus domicilios, sin comisiones"], play: ["Apex Play", "Pida desde la mesa con un QR"] }[EP.producto];
$("#serie").textContent = EP.serie; $("#gancho").innerHTML = EP.gancho; $("#logo b").innerHTML = `<i></i>${PROD[0]}`; $("#logo span").textContent = PROD[1];
$("#frase").textContent = EP.continuara ? "Continuará…" : (EP.frase || "");
const COLOR = { orbi: "#2fbbe8", comi: "#e83fb5", arepa: "#f0b84a", chorizo: "#e0603f", aguacate: "#7cc142", empanada: "#f0a94e", tinto: "#c9a27a", hamburguesa: "#f4c430", pan: "#d8955a", papa: "#c9a06a" };
let ultimo = "", ultPed = "";
async function render(t, f) {
  const S = estado(t);
  const orden = Object.values(S).sort((a, b) => (a.r.tipo === "orbi") - (b.r.tipo === "orbi"));
  let w = fondo(t) + orden.filter((s) => s.r.tipo !== "orbi").map((s) => personaje(s, t)).join("") + frente(t) + orden.filter((s) => s.r.tipo === "orbi").map((s) => personaje(s, t)).join("");
  let [cx, cy, cs] = camara(t);
  const tem = L.find((l) => ev(l).temblor && t > l.ini && t < l.ini + 0.5), lsal = L.find((l) => (ev(l).sale || []).length && t > l.ini + 0.4 && t < l.ini + 0.6);
  const k = tem || lsal ? 12 : 0, sx = k * Math.sin(f * 7.1), sy = k * Math.cos(f * 5.3);
  $("#escena").innerHTML = `<svg viewBox="0 0 1080 1920" width="1080" height="1920"><g transform="translate(${540 + sx} ${960 + sy}) scale(${cs}) translate(${-cx} ${-cy})">${w}</g></svg>`;
  // Tinte y rayas de telenovela en las líneas de drama
  const dr = L.find((l) => ev(l).drama && t >= l.ini - 0.05 && t < l.fin + 0.4);
  $("#tinte").style.opacity = dr ? 0.55 * cl((t - dr.ini + 0.05) / 0.1) * cl((dr.fin + 0.4 - t) / 0.3) : 0;
  $("#rayas").style.opacity = dr && [0, 0.32, 0.64].some((d) => t > dr.ini + d && t < dr.ini + d + 0.22) ? 0.7 : 0;
  // Gancho (primeros 3 s) y serie
  $("#gancho").style.opacity = cl((3.2 - t) / 0.3); $("#gancho").style.transform = `translateX(-50%) scale(${1.06 - 0.06 * out3(t / 0.4)})`;
  $("#serie").style.opacity = t < SELLO ? 1 : 0;
  // Chip y tarjeta de pedido
  const lc = [...L].reverse().find((l) => ev(l).chip && t >= l.ini + 0.2 && t < Math.max(l.fin + 1.4, l.ini + 2.8)), chip = $("#chip");
  if (lc) { chip.textContent = ev(lc).chip; chip.className = ev(lc).chipok ? "ok" : ""; const q = rebote((t - lc.ini - 0.2) / 0.35); chip.style.opacity = 1; chip.style.transform = `translateX(-50%) rotate(-4deg) scale(${q})`; } else chip.style.opacity = 0;
  const lp = [...L].reverse().find((l) => ev(l).pedido && t >= l.ini && t < Math.max(l.fin + 1.6, l.ini + 3.2)), ped = $("#pedido");
  if (lp) { const [a, b] = ev(lp).pedido.split("|"); if (ultPed !== a) { ultPed = a; ped.innerHTML = `<i></i><b>${a}</b><span>${b || ""}</span>`; }
    ped.style.opacity = out3((t - lp.ini) / 0.25); ped.style.transform = `translateX(-50%) translateY(${60 * (1 - out3((t - lp.ini) / 0.35))}px)`; } else ped.style.opacity = 0;
  // Subtítulos
  const l = L.find((x) => t >= x.ini - 0.05 && t < x.fin + 0.3), sub = $("#sub");
  if (l && t < SELLO) { if (ultimo !== l.txt + l.i) { ultimo = l.txt + l.i; sub.innerHTML = `<small style="color:${COLOR[EP.reparto[l.quien].tipo]}">${EP.reparto[l.quien].nombre}</small>${l.txt}`; sub.style.borderColor = COLOR[EP.reparto[l.quien].tipo]; }
    sub.style.opacity = out3((t - l.ini + 0.05) / 0.15) * cl((l.fin + 0.3 - t) / 0.15); } else sub.style.opacity = 0;
  // Sello final
  if (t >= SELLO) { const tt = t - SELLO; $("#sello").style.opacity = out3(tt / 0.5); $("#o-final").innerHTML = orbiCara(t, tt < 0.5 ? "normal" : "guino", false);
    $("#frase").style.opacity = out3((tt - 0.3) / 0.4); $("#logo").style.opacity = out3((tt - 0.8) / 0.5); } else $("#sello").style.opacity = 0;
  grano(f);
}
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
