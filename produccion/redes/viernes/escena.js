// «Viernes, 8 p. m.» — render(t, f). Mundo 1080x1920; la cámara recorta y se mueve.
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const rebote = (x) => { x = cl(x); const c = 2.70158; return 1 + c * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
const E = LINEA.escenas, L = LINEA.lineas;
const escenaDe = (t) => Object.keys(E).find((k) => t >= E[k][0] && t < E[k][1]) || "sello";
const habla = (quien, t) => L.some((l) => l.quien === quien && t >= l.ini && t < l.fin);
const linea = (t) => L.find((l) => t >= l.ini - 0.05 && t < l.fin + 0.35);
const boca = (t) => 0.25 + 0.6 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 4.7));
const lin = (q, n = 0) => L.filter((l) => l.quien === q)[n];
const g = (x, y, s, cont, op = 1, rot = 0) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})" opacity="${op}">${cont}</g>`;
// Cámara: punto del mundo al centro y zoom
const CAM = { calma: [[540, 1150, 1.0], [540, 1300, 1.08]], avalancha: [[540, 1380, 0.96], [540, 1400, 1.02]], papel: [[430, 1560, 1.32], [430, 1520, 1.38]],
  derrota: [[560, 1640, 1.25], [560, 1660, 1.38]], aparece: [[540, 1300, 1.12], [540, 1260, 1.2]], atiende: [[540, 1380, 0.98], [540, 1390, 1.03]],
  protesta: [[400, 1560, 1.3], [380, 1540, 1.36]], final: [[520, 1480, 1.1], [520, 1460, 1.16]], sello: [[540, 960, 1], [540, 960, 1]] };
function camara(t) {
  const k = escenaDe(t), [a, b] = E[k], p = (t - a) / (b - a), [c0, c1] = CAM[k];
  let c = [lerp(c0[0], c1[0], ease(p)), lerp(c0[1], c1[1], ease(p)), lerp(c0[2], c1[2], ease(p))];
  const orden = Object.keys(E), prev = orden[orden.indexOf(k) - 1];
  if (prev && k !== "sello") { const pc = CAM[prev][1], q = ease((t - a) / 0.7); c = c.map((v, i) => lerp(pc[i], v, q)); }
  // en «papel» la cámara busca al cliente que reclama
  if (k === "papel") { const r = lin("c3", 1); if (r) { const q = ease((t - r.ini + 0.4) / 0.5) * (1 - ease((t - r.fin - 0.2) / 0.5)); c = c.map((v, i) => lerp(v, [300, 1460, 1.25][i], q)); } }
  return c;
}
// Clientes: [quién, mesa x, y, opciones de persona, aparece en]
const CLIENTES = [["c2", 250, 1240, { piel: "#f2c9a0", pelo: "largo", colorPelo: "#5a3a1a", camisa: "#c0392b" }],
  ["c1", 830, 1220, { piel: "#a8714a", pelo: "corto", camisa: "#2e8b57" }],
  ["c4", 830, 1580, { piel: "#f6d5b5", pelo: "moño", colorPelo: "#2b1d14", camisa: "#8e44ad" }],
  ["c3", 250, 1600, { piel: "#7a4b2e", pelo: "calvo", colorPelo: "#2b1d14", camisa: "#3d6fb6" }]];
function cliente([q, x, y, o], t, k) {
  const l0 = lin(q, 0), ap = l0 ? l0.ini - 0.45 : 99, aparecido = t >= ap || ["papel", "derrota", "aparece", "atiende", "protesta", "final"].includes(k);
  if (!aparecido) return g(x, y + 48, 1.0, mesa(0, 0));
  const kpop = k === "avalancha" ? rebote((t - ap) / 0.45) : 1;
  const enojo = ["avalancha", "papel", "derrota"].includes(k), contento = ["atiende", "final", "protesta"].includes(k);
  const brazo = (k === "avalancha" || (k === "papel" && q === "c3")) ? 1 : 0;
  const h = habla(q, t);
  const p = persona({ ...o, brazo, boca: h ? boca(t) * 1.3 : contento ? 0.75 : enojo ? 0.15 : 0.35, cejas: enojo ? "enojo" : contento ? "arriba" : "",
    mira: Math.sin(t * 1.3 + x) * 4 });
  const bob = Math.sin(t * (enojo ? 7 : 2) + x) * (enojo ? 6 : 2);
  let extra = "";
  if (q === "c3" && (k === "papel" || k === "derrota")) { const r = lin("c3", 1); if (r && t > r.ini - 0.6) extra = g(30, -18, 0.9,
      `<ellipse cx="0" cy="0" rx="60" ry="14" fill="#fff"/><path d="M-40 -14 Q 0 -44 34 -14 Q 0 12 -40 -14Z M34 -14 L 56 -32 L 56 4Z" fill="#6fa8dc"/><circle cx="-22" cy="-18" r="4" fill="#222"/>`); }
  if (k === "atiende" || k === "final" || k === "protesta") { const tt = { c2: 0.12, c1: 0.32, c4: 0.72, c3: 0.5 }[q]; const a = E.atiende[0] + (E.atiende[1] - E.atiende[0]) * tt;
    const kk = out3((t - a) / 0.35); if (t > a) extra += `<g transform="translate(-10 -330) scale(${0.6 + 0.4 * kk})" opacity="${kk}"><rect x="-110" y="-34" width="220" height="62" rx="31" fill="#0b1626" stroke="#2ee59d" stroke-width="4"/>
      <text x="0" y="10" text-anchor="middle" font-size="30" font-weight="800" fill="#2ee59d" font-family="Figtree">✓ En cocina</text></g>`; }
  return g(x, y + bob * 0.3, 1.0 * kpop, p, 1) + g(x, y + 48, 1.0, mesa(0, 0) + extra);
}
function hojas(t, a, b) { // hojas de papel volando
  if (t < a || t > b) return "";
  return Array.from({ length: 7 }, (_, i) => { const tt = ((t - a) * 0.9 + i * 0.37) % 2.2, x = 470 + Math.sin(i * 2.3) * 90 + tt * 80 * (i % 2 ? 1 : -1), y = 1560 - tt * 420;
    return g(x, y, 1, `<rect x="-34" y="-44" width="68" height="88" fill="#fbf6e6" stroke="#c9bd98" stroke-width="3"/><line x1="-24" y1="-20" x2="24" y2="-20" stroke="#a9c7e8" stroke-width="3"/><line x1="-24" y1="0" x2="24" y2="0" stroke="#a9c7e8" stroke-width="3"/>`, cl(1 - tt / 2.2), tt * 260 * (i % 2 ? 1 : -1)); }).join("");
}
function orbiCara(t, nombre, h) {
  const base = { ...EXPRESIONES[nombre] };
  if (h) { const a = 0.25 + 0.55 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 5.3)); base.boca = nombre === "feliz" ? [0.9, 1.2, Math.max(0.2, a)] : [0.15, 0.7, a]; }
  if ((t % 3.3) < 0.12 && base.oi > 0) { base.oi = 0.08; if (base.od > 0) base.od = 0.08; }
  return orbi(nombre, { e: base, anillo: -10 + 4 * Math.sin(t * 1.3) });
}
let ultimo = "";
async function render(t, f) {
  const k = escenaDe(t), [a, b] = E[k], tt = t - a;
  const luz = k === "derrota" ? lerp(1, 0.25, out3(tt / 0.8)) : k === "aparece" ? lerp(0.25, 1, out3((tt - 1.0) / 1.6)) : 1;
  let mundo = restaurante(t, luz);
  // Mesa siete (central), con su hablador: de aquí sale Orbi
  const brilloQR = k === "aparece" ? cl((tt - 0.3) / 0.6) * (0.6 + 0.4 * Math.sin(t * 8)) : 0;
  mundo += g(540, 1440, 0.95, mesa(0, 0) + `<circle cx="70" cy="-44" r="${60 + 30 * brilloQR}" fill="rgba(47,187,232,${0.45 * brilloQR})"/>`);
  if (k === "aparece" && brilloQR) mundo += `<path d="M${540 + 66 - 40} ${1395} L ${540 + 66 - 160} 900 L ${540 + 66 + 160} 900 L ${540 + 66 + 40} 1395Z" fill="rgba(140,220,255,${0.18 * brilloQR})"/>`;
  CLIENTES.forEach((c) => mundo += cliente(c, t, k));
  // Julián
  let jx = 560, jy = 1780, js = 1.15, jo = {};
  const hj = habla("julian", t);
  if (k === "calma") jo = { bandeja: true, platos: 0, boca: Math.sin(t * 3) > 0 ? "o" : undefined, mira: Math.sin(t * 0.8) * 4 };
  if (k === "avalancha") jo = { sudor: tt > 1.5, ojos: "grandes", bandeja: true, platos: 3, inclina: Math.sin(t * 5) * 14, mira: Math.sin(t * 6) * 6, boca: hj ? boca(t) : "o" };
  if (k === "papel") jo = { sudor: true, ojos: "grandes", boca: "o", mira: -4 };
  if (k === "derrota") { jy = lerp(1780, 1880, out3(tt / 0.8)); jo = { ojos: "cerrados", boca: hj ? boca(t) : "triste", sudor: true }; }
  if (k === "aparece") { jy = lerp(1880, 1780, out3((tt - 2.0) / 0.8)); jo = { ojos: "grandes", boca: "o", mira: -3 }; }
  if (k === "atiende" || k === "protesta") jo = { bandeja: true, platos: 3, mira: Math.sin(t * 1.5) * 4 };
  if (k === "final") jo = { bandeja: true, platos: 3, boca: hj ? boca(t) : undefined, mira: -5 };
  mundo += g(jx, jy + (k === "avalancha" ? Math.abs(Math.sin(t * 6)) * -10 : 0), js, julian(jo), 1, k === "avalancha" ? Math.sin(t * 6) * 3 : 0);
  // Don Papel
  if (["papel", "derrota", "aparece", "atiende", "protesta", "final"].includes(k)) {
    let px = 330, py = 1570, ps = 0.95;
    if (k === "papel") { const kk = rebote(tt / 0.6); py = lerp(1760, 1570, kk); }
    if (["aparece", "atiende", "final"].includes(k)) { px = 175; py = 1730; ps = 0.7; }
    if (k === "protesta") { px = lerp(175, 300, out3(tt / 0.5)); py = lerp(1730, 1600, out3(tt / 0.5)); ps = lerp(0.7, 0.95, out3(tt / 0.5)); }
    const s = lin("orbi", L.filter((l) => l.quien === "orbi").length - 2), cerrado = (k === "protesta" && s && t > s.ini + 0.3) || k === "final";
    const hp = habla("papel", t);
    mundo += g(px, py + Math.sin(t * 3) * 6, ps, donPapel({ boca: hp ? boca(t) : 0.15, cara: k === "aparece" || k === "protesta" ? "enojo" : "", cerrado }), 1, cerrado ? 0 : Math.sin(t * 2) * 4);
  }
  mundo += hojas(t, E.papel[0] + 1.0, E.derrota[0] + 0.5);
  // Orbi
  let orbiHtml = "";
  if (["aparece", "atiende", "protesta", "final"].includes(k)) {
    let ox = 606, oy = 1180, os = 1, cara = "normal";
    if (k === "aparece") { const kk = out3((tt - 0.8) / 1.0); oy = lerp(1400, 1150, kk); os = 0.2 + 0.8 * rebote((tt - 0.8) / 0.9); cara = tt > 3.2 ? "orgulloso" : "normal"; }
    if (k === "atiende") { const r = (t - a) / (b - a); const ruta = [[606, 1150], [250, 980], [830, 960], [830, 1320], [606, 1150]];
      const seg = Math.min(3.999, r * 4), i = Math.floor(seg), q = ease(seg - i); ox = lerp(ruta[i][0], ruta[i + 1][0], q); oy = lerp(ruta[i][1], ruta[i + 1][1], q); os = 0.8; cara = "feliz"; }
    if (k === "protesta") { ox = lerp(606, 560, out3(tt / 0.6)); oy = lerp(1150, 1360, out3(tt / 0.6)); os = 0.9; cara = habla("papel", t) ? "sarcastico" : "guino"; }
    if (k === "final") { ox = 330; oy = lerp(1380, 1330, out3(tt / 1)); os = 0.9; cara = tt > 1.6 ? "guino" : "orgulloso"; }
    orbiHtml = `<g transform="translate(${ox} ${oy + Math.sin(t * 2.2) * 12}) scale(${os * 1.0})"><g transform="translate(-190 -190)">${orbiCara(t, cara, habla("orbi", t)).replace("<svg ", '<svg width="380" height="380" ')}</g></g>`;
    if (k === "aparece" && tt > 0.8 && tt < 2.2) orbiHtml += Array.from({ length: 10 }, (_, i) => { const r = (tt - 0.8) * 260, an = i * 0.63; return `<circle cx="${606 + Math.cos(an) * r}" cy="${1250 + Math.sin(an) * r}" r="${6 * (1 - (tt - 0.8) / 1.4)}" fill="#bff0ff"/>`; }).join("");
  }
  mundo += orbiHtml;
  // Cámara
  const [cx, cy, cs] = camara(t), sacude = k === "avalancha" ? 6 : 0;
  const sx = sacude * Math.sin(f * 7.1), sy = sacude * Math.cos(f * 5.3);
  $("#escena").innerHTML = `<svg viewBox="0 0 1080 1920" width="1080" height="1920"><g transform="translate(${540 + sx} ${960 + sy}) scale(${cs}) translate(${-cx} ${-cy})">${mundo}</g></svg>`;
  // Velo de derrota / luz azul de Orbi
  $("#velo").style.opacity = k === "derrota" ? 0.65 * out3(tt / 0.8) : k === "aparece" ? 0.65 * (1 - out3((tt - 1.0) / 1.6)) : 0;
  // Título y barras de cine
  $("#titulo").style.opacity = k === "calma" ? out3(tt / 0.6) * cl((b - tt - a + a) / 0.5) * cl((E.calma[1] - t) / 0.4) : 0;
  $("#barras").style.opacity = k === "calma" ? cl((E.calma[1] - t) / 0.4) : 0;
  // Contadores
  let chip = "", ok = false;
  if (k === "avalancha") chip = `MESAS OCUPADAS: ${Math.min(12, Math.floor(cl(tt / 3) * 12))}`;
  if (k === "papel" || k === "derrota") chip = `PEDIDOS PERDIDOS: ${Math.min(3, Math.floor(cl((t - E.papel[0] - 1) / 4) * 3) + (t > E.papel[0] + 1 ? 1 : 0))}`;
  if (k === "atiende" || k === "protesta") { chip = "PEDIDOS PERDIDOS: 0"; ok = true; }
  $("#chip").textContent = chip; $("#chip").className = ok ? "ok" : ""; $("#chip").style.opacity = chip ? 1 : 0;
  // Subtítulos
  const l = linea(t), sub = $("#sub");
  if (l && k !== "sello") { if (ultimo !== l.txt) { ultimo = l.txt; sub.innerHTML = `<small>${NOMBRES[l.quien]}</small>${l.txt}`; sub.className = l.quien === "orbi" ? "orbi" : l.quien === "papel" ? "papel" : ""; }
    sub.style.opacity = out3((t - l.ini + 0.05) / 0.15) * cl((l.fin + 0.35 - t) / 0.15); sub.style.transform = `translateX(-50%) scale(${0.92 + 0.08 * out3((t - l.ini) / 0.15)})`; }
  else sub.style.opacity = 0;
  // Sello final
  if (k === "sello") { const kk = out3(tt / 0.6); $("#sello").style.opacity = kk; $("#o-final").innerHTML = orbiCara(t, tt < 0.5 ? "normal" : "guino", false);
    $("#o-final").style.transform = `scale(${0.7 + 0.3 * rebote(tt / 0.5)})`; $("#frase").style.opacity = out3((tt - 0.5) / 0.4); $("#logo").style.opacity = out3((tt - 1.1) / 0.5); }
  else $("#sello").style.opacity = 0;
  grano(f);
}
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
const NOMBRES = { orbi: "ORBI", julian: "JULIÁN, EL MESERO", papel: "DON PAPEL", c1: "CLIENTE", c2: "CLIENTA", c3: "CLIENTE", c4: "CLIENTA" };
