// Personajes de «Cine Apex»: figuras humanas de cuerpo entero, con proporciones reales y sombreado de cine.
// humano(o) dibuja con los pies en (0,0); mide ~560 de alto. Orbi y Comi usan el mismo cuerpo con su cabeza propia.
const _tono = (hex, k) => { const n = parseInt(hex.slice(1), 16); let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  const f = (c) => Math.round(k < 0 ? c * (1 + k) : c + (255 - c) * k); return "#" + [f(r), f(g), f(b)].map((c) => Math.max(0, Math.min(255, c)).toString(16).padStart(2, "0")).join(""); };
// Degradado lateral (luz desde la derecha) por color; se define en línea y se reutiliza por id
function tela(hex) { const id = "t" + hex.slice(1);
  return [`url(#${id})`, `<linearGradient id="${id}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="${_tono(hex, -0.45)}"/><stop offset=".55" stop-color="${hex}"/><stop offset=".9" stop-color="${_tono(hex, 0.12)}"/><stop offset="1" stop-color="${_tono(hex, 0.3)}"/></linearGradient>`]; }
function pielG(hex) { const id = "p" + hex.slice(1);
  return [`url(#${id})`, `<radialGradient id="${id}" cx="60%" cy="35%" r="75%"><stop offset="0" stop-color="${_tono(hex, 0.12)}"/><stop offset=".6" stop-color="${hex}"/><stop offset="1" stop-color="${_tono(hex, -0.35)}"/></radialGradient>`]; }
const POSES = {
  reposo: [[6, 8], [6, 8]], zombi: [[80, 22], [86, 18]], senala: [[8, 10], [95, 0]], baile: [[55, 25], [150, 15]], leer: [[28, 115], [28, 115]],
  bolsillos: [[12, -28], [12, -28]], telefono: [[8, 10], [25, 150]], brazos_arriba: [[160, 10], [160, 10]], mano_pecho: [[8, 10], [25, 125]],
  ofrece: [[8, 10], [60, 40]], abraza: [[70, 70], [70, 70]], saluda: [[8, 10], [150, 25]], apunta: [[8, 10], [88, -5]], flor: [[8, 10], [45, 60]] };
function brazo(lado, [a1, a2], ancho, color, piel, mangaCorta) {
  const s = lado, L1 = 118, L2 = 112, x0 = s * 58, y0 = -418;
  const r1 = (a1 * Math.PI) / 180, r2 = ((a1 + a2) * Math.PI) / 180;
  const x1 = x0 + s * Math.sin(r1) * L1, y1 = y0 + Math.cos(r1) * L1, x2 = x1 + s * Math.sin(r2) * L2, y2 = y1 + Math.cos(r2) * L2;
  const manga = mangaCorta ? `M${x0} ${y0} L ${(x0 + x1) / 2} ${(y0 + y1) / 2}` : `M${x0} ${y0} L ${x1} ${y1} L ${x2 - s * Math.sin(r2) * 14} ${y2 - Math.cos(r2) * 14}`;
  const bajo = mangaCorta ? `<path d="M${(x0 + x1) / 2} ${(y0 + y1) / 2} L ${x1} ${y1} L ${x2} ${y2}" stroke="${piel}" stroke-width="${ancho - 8}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>` : "";
  return `<path d="${manga}" stroke="rgba(0,0,0,.55)" stroke-width="${ancho + 5}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>${bajo}
    <path d="${manga}" stroke="${color}" stroke-width="${ancho}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    <circle cx="${x2}" cy="${y2}" r="14" fill="${piel}" stroke="rgba(0,0,0,.35)" stroke-width="2"/>`;
}
function piernas(o, pant, zap, piel) {
  const vest = o.ropa === "vestido", gr = vest ? 19 : 39;
  return [-1, 1].map((l) => { const ph = o.paso != null ? Math.sin(o.paso + (l > 0 ? Math.PI : 0)) : 0, alza = Math.max(0, ph) * 20;
    const x0 = l * 26, y0 = -268, x1 = l * (31 + alza * 0.4), y1 = -134 - alza * 0.6, x2 = l * 36, y2 = -alza, col = vest ? piel : pant;
    return `<path d="M${x0} ${y0} L ${x1} ${y1} L ${x2} ${y2 - 12}" stroke="rgba(0,0,0,.55)" stroke-width="${gr + 5}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <path d="M${x0} ${y0} L ${x1} ${y1} L ${x2} ${y2 - 12}" stroke="${col}" stroke-width="${gr}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <path d="M${x2 - 20} ${y2 - 2} Q ${x2 - 18} ${y2 - 24} ${x2 + l * 6} ${y2 - 22} Q ${x2 + l * 26} ${y2 - 18} ${x2 + l * 30} ${y2 - 2} Z" fill="${zap}" stroke="#000" stroke-width="2"/>`; }).join("");
}
function torso(o, c1, c2, defs) {
  const r = o.ropa || "traje", [g1, d1] = tela(c1); defs.push(d1);
  const cuerpo = (abajo = -262, ancho = 64) => `<path d="M${-ancho} -420 Q -72 -340 ${-ancho + 6} ${abajo} L ${ancho - 6} ${abajo} Q 72 -340 ${ancho} -420 Q 0 -446 ${-ancho} -420 Z" fill="${g1}" stroke="rgba(0,0,0,.6)" stroke-width="3"/>`;
  switch (r) {
    case "traje": return cuerpo(-250) + `<path d="M-20 -432 L 0 -360 L 20 -432 Z" fill="#f3f1ec"/><path d="M-6 -420 L 6 -420 L 9 -330 L 0 -318 L -9 -330 Z" fill="${c2}"/>
      <path d="M-30 -436 L -6 -350 L -26 -300 M30 -436 L 6 -350 L 26 -300" stroke="rgba(0,0,0,.5)" stroke-width="4" fill="none"/>${[-305, -280].map((y) => `<circle cx="10" cy="${y}" r="4" fill="rgba(0,0,0,.6)"/>`).join("")}`;
    case "gabardina": return `<path d="M-70 -420 Q -84 -260 -92 -110 L 92 -110 Q 84 -260 70 -420 Q 0 -446 -70 -420 Z" fill="${g1}" stroke="rgba(0,0,0,.6)" stroke-width="3"/>
      <path d="M-46 -446 L -18 -330 L 0 -110 M46 -446 L 18 -330" stroke="rgba(0,0,0,.45)" stroke-width="4" fill="none"/><path d="M-62 -300 L 62 -300" stroke="${_tono(c1, -0.4)}" stroke-width="12"/>
      <path d="M-50 -452 L -30 -420 L -40 -380 Z M50 -452 L 30 -420 L 40 -380 Z" fill="${_tono(c1, -0.25)}"/><path d="M-14 -430 L 0 -390 L 14 -430Z" fill="${c2}"/>`;
    case "vestido": { const [g2, d2] = tela(c1); return `<path d="M-50 -420 Q -60 -340 -44 -290 Q -100 -200 -96 -150 L 96 -150 Q 100 -200 44 -290 Q 60 -340 50 -420 Q 0 -440 -50 -420 Z" fill="${g1}" stroke="rgba(0,0,0,.55)" stroke-width="3"/>
      <path d="M-44 -290 Q 0 -280 44 -290" stroke="${_tono(c1, -0.3)}" stroke-width="5" fill="none"/>${o.collar ? `<path d="M-26 -428 Q 0 -400 26 -428" stroke="#f4e3b0" stroke-width="5" fill="none"/>` : ""}`; }
    case "mesero": return cuerpo(-252, 60) .replace(g1, "#f3f1ec") + `<path d="M-54 -420 Q -60 -330 -52 -262 L 52 -262 Q 60 -330 54 -420 L 22 -432 L 0 -360 L -22 -432 Z" fill="url(#t111418)" stroke="#000" stroke-width="3"/>
      <linearGradient id="t111418" x1="0" x2="1"><stop offset="0" stop-color="#050608"/><stop offset=".6" stop-color="#1a1d24"/><stop offset="1" stop-color="#3a3f4a"/></linearGradient>
      <g transform="translate(0 -428)"><path d="M0 0 L -24 -11 L -24 11Z M0 0 L 24 -11 L 24 11Z" fill="${c2 || "#2f6fd6"}"/><circle r="5" fill="${_tono(c2 || "#2f6fd6", -0.3)}"/></g>${[-380, -340, -300].map((y) => `<circle cx="0" cy="${y}" r="4" fill="#666"/>`).join("")}`;
    case "camisa": return cuerpo(-258) + `<path d="M-20 -432 L 0 -400 L 20 -432" stroke="rgba(0,0,0,.5)" stroke-width="4" fill="none"/><line x1="0" y1="-400" x2="0" y2="-262" stroke="rgba(0,0,0,.35)" stroke-width="3"/>
      ${o.chaleco ? `<path d="M-64 -420 Q -70 -340 -58 -262 L -18 -262 L -14 -400 Z M64 -420 Q 70 -340 58 -262 L 18 -262 L 14 -400 Z" fill="${_tono(o.chaleco, 0)}" stroke="#000" stroke-width="2"/><polygon points="-44,-370 -38,-356 -24,-356 -35,-347 -31,-333 -44,-342 -57,-333 -53,-347 -64,-356 -50,-356" fill="#d9b25a"/>` : ""}`;
    case "chaqueta": return cuerpo(-252) + `<path d="M-22 -432 L -10 -262 L 10 -262 L 22 -432 Z" fill="${c2}"/><path d="M-36 -440 L -14 -380 L -30 -330 M36 -440 L 14 -380 L 30 -330" stroke="rgba(0,0,0,.55)" stroke-width="5" fill="none"/>`;
    case "delantal": return cuerpo(-256) + `<path d="M-46 -380 L 46 -380 L 54 -150 L -54 -150 Z" fill="#f2efe8" stroke="rgba(0,0,0,.3)" stroke-width="2"/><path d="M-46 -380 L -40 -430 M46 -380 L 40 -430" stroke="#f2efe8" stroke-width="6"/>`;
    case "harapos": return cuerpo(-252) + `<path d="M-58 -262 L -40 -240 L -22 -266 L -4 -236 L 14 -264 L 34 -238 L 58 -262" fill="${g1}" stroke="rgba(0,0,0,.5)" stroke-width="2"/>
      <path d="M-30 -380 l 18 30 l -10 20 M30 -330 l -14 24" stroke="#3a1a10" stroke-width="5" fill="none" opacity=".7"/><ellipse cx="-20" cy="-320" rx="16" ry="10" fill="#4a2a1a" opacity=".55"/>`;
    case "sastre": return `<path d="M-60 -420 Q -66 -340 -50 -268 Q -60 -200 -58 -150 L 58 -150 Q 60 -200 50 -268 Q 66 -340 60 -420 Q 0 -446 -60 -420 Z" fill="${g1}" stroke="rgba(0,0,0,.6)" stroke-width="3"/>
      <path d="M-24 -432 L 0 -340 L 24 -432 Z" fill="${c2}"/><path d="M-50 -268 L 50 -268" stroke="${_tono(c1, -0.35)}" stroke-width="4"/><path d="M-34 -436 L -4 -340 M34 -436 L 4 -340" stroke="#d9b25a" stroke-width="3" fill="none"/>`;
  }
  return cuerpo();
}
function cara(o, piel, defs) {
  const [gp, dp] = pielG(piel); defs.push(dp);
  const c = o.cara || "serio", h = o.boca || 0, mx = (o.mira || 0) * 5, edad = o.edad || 0, z = o.zombi;
  const ap = { sorpresa: 1.25, miedo: 1.3, triste: 0.75, enojo: 0.7, sonrisa: 0.8, cerrado: 0.06 }[c] ?? 1;
  const ojo = (x) => z ? `<ellipse cx="${x}" cy="-508" rx="11" ry="7" fill="#e8e4c8"/><circle cx="${x}" cy="-508" r="2.5" fill="#6a6a50"/>`
    : `<path d="M${x - 12} -508 Q ${x} ${-508 - 9 * ap} ${x + 12} -508 Q ${x} ${-508 + 7 * ap} ${x - 12} -508 Z" fill="#f6f2ea"/><circle cx="${x + mx}" cy="-508" r="${5.5 * Math.min(1, ap + 0.2)}" fill="#2b1d16"/><circle cx="${x + mx + 2}" cy="-510" r="1.6" fill="#fff"/>
       <path d="M${x - 13} -509 Q ${x} ${-519 * 1 - 2 * ap} ${x + 13} -509" stroke="#2a1a12" stroke-width="2.5" fill="none"/>`;
  const ceja = { enojo: [8, 14], triste: [-6, -14], sorpresa: [-8, 0], miedo: [-6, -12], sonrisa: [-2, 0] }[c] || [0, 0];
  const cejas = [-1, 1].map((s) => `<path d="M${s * 9} ${-526 + ceja[0] * 0.3} L ${s * 30} ${-528 - ceja[0] * 0.2}" stroke="${o.colorPelo || "#2a1a12"}" stroke-width="4.5" stroke-linecap="round" transform="rotate(${s * ceja[1] * 0.6} ${s * 20} -527)"/>`).join("");
  const labio = z ? "#4a3a30" : _tono(piel, -0.35);
  const bocaS = h > 0.05 ? `<ellipse cx="0" cy="-468" rx="${10 + 3 * h}" ry="${3 + 9 * h}" fill="#3a1414"/><path d="M-9 -471 L 9 -471" stroke="#eee" stroke-width="2.5" opacity="${h > 0.3 ? 1 : 0}"/>`
    : z ? `<path d="M-14 -466 Q 0 -458 14 -466 L 10 -462 L 4 -466 L -2 -461 L -8 -466Z" fill="#2a1a14"/>`
    : c === "sonrisa" ? `<path d="M-15 -472 Q 0 -460 15 -472" stroke="${labio}" stroke-width="4" fill="none" stroke-linecap="round"/>`
    : c === "triste" ? `<path d="M-13 -464 Q 0 -472 13 -464" stroke="${labio}" stroke-width="4" fill="none" stroke-linecap="round"/>`
    : c === "sorpresa" || c === "miedo" ? `<ellipse cx="0" cy="-467" rx="7" ry="9" fill="#3a1414"/>`
    : `<path d="M-13 -468 Q 0 -466 13 -468" stroke="${labio}" stroke-width="4" fill="none" stroke-linecap="round"/>`;
  const arrugas = edad ? `<path d="M-30 -496 q -6 4 -10 0 M30 -496 q 6 4 10 0 M-22 -478 q -4 10 2 16 M22 -478 q 4 10 -2 16 M-16 -540 q 16 -4 32 0" stroke="${_tono(piel, -0.3)}" stroke-width="1.8" fill="none" opacity=".8"/>` : "";
  const barba = o.barba ? `<path d="M-38 -490 Q -36 -446 0 -440 Q 36 -446 38 -490 Q 20 -462 0 -462 Q -20 -462 -38 -490 Z" fill="${o.colorPelo || "#2a1a12"}" opacity="${o.barba === "sombra" ? 0.35 : 0.9}"/>` : "";
  const ojeras = z ? `<ellipse cx="-20" cy="-504" rx="15" ry="11" fill="#3a3a2a" opacity=".5"/><ellipse cx="20" cy="-504" rx="15" ry="11" fill="#3a3a2a" opacity=".5"/>` : "";
  const lentes = o.lentes ? `<g fill="${o.lentes === "sol" ? "rgba(10,10,14,.9)" : "rgba(200,230,255,.12)"}" stroke="#151515" stroke-width="3"><rect x="-34" y="-520" width="27" height="20" rx="6"/><rect x="7" y="-520" width="27" height="20" rx="6"/></g><line x1="-7" y1="-512" x2="7" y2="-512" stroke="#151515" stroke-width="3"/>` : "";
  return `<path d="M-40 -515 Q -42 -566 0 -568 Q 42 -566 40 -515 Q 40 -470 22 -452 Q 10 -442 0 -442 Q -10 -442 -22 -452 Q -40 -470 -40 -515 Z" fill="${gp}" stroke="rgba(0,0,0,.45)" stroke-width="2.5"/>
    <ellipse cx="-41" cy="-505" rx="7" ry="13" fill="${_tono(piel, -0.15)}"/><ellipse cx="41" cy="-505" rx="7" ry="13" fill="${_tono(piel, -0.05)}"/>
    ${ojeras}${barba}${ojo(-20)}${ojo(20)}${cejas}<path d="M2 -506 Q 8 -488 0 -482" stroke="${_tono(piel, -0.32)}" stroke-width="3" fill="none"/>${bocaS}${arrugas}${lentes}`;
}
function pelo(o) {
  const col = o.colorPelo || "#2a1a12", t = o.pelo || "corto";
  return { corto: `<path d="M-42 -516 Q -46 -578 2 -580 Q 46 -576 42 -516 Q 36 -548 6 -552 Q -28 -556 -42 -516 Z" fill="${col}"/>`,
    peinado: `<path d="M-42 -512 Q -48 -584 6 -584 Q 50 -580 42 -512 Q 40 -556 14 -560 Q -20 -566 -42 -512 Z" fill="${col}"/><path d="M-18 -572 Q 10 -580 34 -560" stroke="${_tono(col, 0.3)}" stroke-width="3" fill="none"/>`,
    largo: `<path d="M-44 -510 Q -52 -586 2 -584 Q 54 -584 46 -510 L 52 -400 Q 30 -420 34 -470 Q 30 -540 0 -548 Q -30 -540 -34 -470 Q -30 -420 -52 -400 Z" fill="${col}"/>`,
    ondas: `<path d="M-46 -510 Q -54 -588 2 -586 Q 56 -586 48 -510 Q 64 -450 44 -410 Q 30 -430 34 -470 Q 28 -540 0 -548 Q -28 -540 -34 -470 Q -30 -430 -44 -410 Q -64 -450 -46 -510 Z" fill="${col}"/>`,
    recogido: `<circle cx="0" cy="-584" r="22" fill="${col}"/><path d="M-42 -512 Q -46 -578 0 -578 Q 46 -578 42 -512 Q 26 -550 0 -552 Q -26 -550 -42 -512 Z" fill="${col}"/>`,
    calvo: `<path d="M-42 -520 Q -44 -536 -38 -544 M42 -520 Q 44 -536 38 -544" stroke="${col}" stroke-width="7" fill="none"/>`,
    rizado: Array.from({ length: 11 }, (_, i) => `<circle cx="${-40 + i * 8}" cy="${-560 - Math.sin((i / 10) * Math.PI) * 22}" r="16" fill="${col}"/>`).join("") }[t] || "";
}
function sombrero(o) {
  const s = o.sombrero; if (!s) return "";
  if (s === "fedora") return `<g transform="translate(0 -562)"><ellipse rx="74" ry="14" fill="#1d1b19"/><path d="M-44 -2 Q -46 -48 0 -50 Q 46 -48 44 -2 Z" fill="#2a2724"/><rect x="-45" y="-14" width="90" height="10" fill="#0e0d0c"/></g>`;
  if (s === "vaquero") return `<g transform="translate(0 -560)"><path d="M-86 2 Q -60 -14 -44 -4 L 44 -4 Q 60 -14 86 2 Q 60 14 0 12 Q -60 14 -86 2 Z" fill="#6b4a2a"/><path d="M-42 -4 Q -40 -52 0 -52 Q 40 -52 42 -4 Z" fill="#7a5532"/></g>`;
  if (s === "boina") return `<ellipse cx="6" cy="-570" rx="50" ry="18" fill="#3a2a2a"/>`;
  return "";
}
function manoDe(lado, [a1, a2]) { const r1 = (a1 * Math.PI) / 180, r2 = ((a1 + a2) * Math.PI) / 180; return [lado * (58 + Math.sin(r1) * 118 + Math.sin(r2) * 112), -418 + Math.cos(r1) * 118 + Math.cos(r2) * 112, a1 + a2]; }
function enMano(o, [x, y, ang]) {
  const p = o.prop, g = (c, r = 0) => `<g transform="translate(${x} ${y}) rotate(${r})">${c}</g>`;
  if (p === "linterna") return g(`<rect x="-9" y="-6" width="18" height="50" rx="5" fill="#2a2a2a"/><path d="M-10 44 L -150 330 L 150 330 L 10 44 Z" fill="rgba(255,250,210,.13)"/>`, -ang);
  if (p === "escaner") return g(`<rect x="-12" y="-14" width="58" height="28" rx="8" fill="#1a1d24" stroke="#5fc9f1" stroke-width="3"/><rect x="40" y="-8" width="10" height="16" fill="#ff3b5c"/><path d="M50 0 L 220 -40 L 220 40 Z" fill="rgba(255,60,90,.18)"/>`, 90 - ang);
  if (p === "telefono") return g(`<rect x="-11" y="-20" width="22" height="40" rx="5" fill="#111" stroke="#444" stroke-width="2"/><rect x="-8" y="-16" width="16" height="30" fill="#2fbbe8" opacity=".7"/>`);
  if (p === "flor") return g(`<path d="M0 0 L 4 -70" stroke="#3a6a2a" stroke-width="4"/><g transform="translate(4 -76)">${[0, 72, 144, 216, 288].map((a) => `<ellipse rx="9" ry="16" fill="#c0392b" transform="rotate(${a}) translate(0 -10)"/>`).join("")}<circle r="7" fill="#f4c430"/></g>`);
  if (p === "bandeja") return g(`<ellipse rx="70" ry="12" fill="#c9ced6" stroke="#8b939e" stroke-width="3"/><path d="M-40 -6 Q -40 -40 0 -42 Q 40 -40 40 -6 Z" fill="#d9dde3" stroke="#8b939e" stroke-width="3"/><circle cy="-44" r="6" fill="#8b939e"/>`);
  return "";
}
function accesorio(o) {
  if (o.prop === "libro") return `<g transform="translate(0 -330)"><rect x="-46" y="-30" width="92" height="62" rx="4" fill="#5a2a1a" stroke="#2a120a" stroke-width="3"/><rect x="-40" y="-26" width="80" height="54" fill="#efe6d0"/><line x1="0" y1="-26" x2="0" y2="28" stroke="#9a8a6a" stroke-width="2"/></g>`;
  if (o.prop === "paraguas") return `<g transform="translate(150 -560)"><path d="M-130 0 Q 0 -110 130 0 Q 100 -14 65 0 Q 32 -14 0 0 Q -32 -14 -65 0 Q -100 -14 -130 0 Z" fill="#1a1a22" stroke="#000" stroke-width="2"/><line x1="0" y1="0" x2="0" y2="170" stroke="#222" stroke-width="5"/></g>`;
  return "";
}
function cabezaOrbi(o) { return `<g transform="translate(0 -510) scale(.55)"><g transform="translate(-190 -190)">${orbiCara(o.t || 0, o.caraOrbi || "normal", (o.boca || 0) > 0.05)}</g></g>`; }
function cabezaComi(o) {
  const h = o.boca || 0, c = o.cara || "diva";
  return `<g transform="translate(0 -505)"><rect x="-62" y="-62" width="124" height="118" rx="12" fill="url(#cajaMag)" stroke="#5a0a44" stroke-width="3"/><rect x="40" y="-62" width="22" height="118" fill="rgba(0,0,0,.15)"/>
    <linearGradient id="cajaMag" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff5fc8"/><stop offset=".6" stop-color="#c2189a"/><stop offset="1" stop-color="#7a0c60"/></linearGradient>
    ${[-24, 24].map((x) => `<path d="M${x - 14} -8 Q ${x} ${c === "enojo" ? -14 : -20} ${x + 14} -8 Q ${x} 2 ${x - 14} -8 Z" fill="#fff"/><circle cx="${x + 2}" cy="-8" r="5" fill="#3a0a2e"/>
      ${[-10, -4, 2, 8].map((d) => `<line x1="${x + d}" y1="-16" x2="${x + d * 1.4}" y2="-26" stroke="#1a0010" stroke-width="2.5"/>`).join("")}`).join("")}
    <path d="M-40 -34 Q -24 ${c === "enojo" ? -28 : -42} -10 -32 M40 -34 Q 24 ${c === "enojo" ? -28 : -42} 10 -32" stroke="#2a0020" stroke-width="4" fill="none"/>
    ${h > 0.05 ? `<ellipse cx="0" cy="26" rx="${12 + 3 * h}" ry="${4 + 10 * h}" fill="#5a0a2a" stroke="#ff2f8a" stroke-width="4"/>` : `<path d="M-16 24 Q 0 34 16 24 Q 0 28 -16 24 Z" fill="#ff2f8a" stroke="#c0105a" stroke-width="3"/>`}
    <path d="M-30 -62 L -18 -86 L -4 -66 L 8 -90 L 20 -66 L 32 -86 L 40 -62 Z" fill="#f2c14a" stroke="#a87a10" stroke-width="2"/></g>`;
}
// Personaje completo. o = {piel, ropa, c1, c2, pant, zap, pelo, colorPelo, pose, brazos, paso, cara, boca, mira, edad, barba, lentes, sombrero, prop, zombi, cabeza: humano|orbi|comi, t}
function humano(o = {}) {
  const t = o.t || 0, defs = [], piel = o.zombi ? "#8e9b7c" : (o.piel || "#c98e62"), c1 = o.c1 || "#2b3346", c2 = o.c2 || "#7a1f2a";
  const pant = o.pant || _tono(c1, -0.2), zap = o.zap || "#14110f", pose = POSES[o.pose || "reposo"] || POSES.reposo, br = o.brazos || pose;
  const manos = o.cabeza === "orbi" ? "#5fb8f0" : piel, ancho = o.ropa === "vestido" ? 22 : 34, colorBrazo = o.ropa === "vestido" ? piel : o.ropa === "mesero" ? "#f3f1ec" : tela(c1)[0];
  const zb = o.zombi ? Math.sin(t * 2.3) * 6 : 0, arms = br.map(([a, b], i) => [a + zb * (i ? 1 : -1), b]);
  const cab = o.cabeza === "orbi" ? cabezaOrbi(o) : o.cabeza === "comi" ? cabezaComi(o) : `<rect x="-14" y="-460" width="28" height="30" fill="${_tono(piel, -0.2)}"/>` + pelo(o) + cara(o, piel, defs) + sombrero(o);
  const pelofrente = o.cabeza ? "" : (o.pelo === "corto" || o.pelo === "peinado" || o.pelo === "rizado" || o.pelo === "recogido") ? pelo(o) : "";
  const inclina = o.zombi ? 10 + Math.sin(t * 1.7) * 4 : 0;
  return `<g>${`<defs>${defs.join("")}</defs>`}
    <ellipse cx="0" cy="4" rx="90" ry="14" fill="rgba(0,0,0,.35)"/>
    ${piernas(o, pant, zap, piel)}
    <g transform="rotate(${inclina * 0.4} 0 -260)">
      ${torso(o, c1, c2, defs)}
      ${brazo(-1, arms[0], ancho, colorBrazo, manos, o.ropa === "harapos")}${brazo(1, arms[1], ancho, colorBrazo, manos, o.ropa === "harapos")}
      ${accesorio(o)}${enMano(o, manoDe(1, arms[1]))}
      <g transform="rotate(${inclina} 0 -450)">${cab}${pelofrente}</g>
    </g><defs>${defs.join("")}</defs></g>`;
}
