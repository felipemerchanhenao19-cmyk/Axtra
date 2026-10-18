// «Expediente 27» (cine negro). render(t, f)
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
const boca = (t) => 0.25 + 0.6 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 4.7));
const g = (x, y, s, c, op = 1, rot = 0) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})" opacity="${op}">${c}</g>`;
const azar = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
// Relámpagos: [tiempo, fuerza]
const RAYOS = [[0.35, 1], [0.55, 0.6], [1.9, 0.8], [E.callejon[0] + 0.15, 0.7], [E.revela[0], 1], [E.revela[0] + 0.18, 0.8]];
const rayo = (t) => RAYOS.reduce((s, [a, f]) => s + (t >= a ? f * Math.exp(-(t - a) * 9) * (0.7 + 0.3 * Math.sin((t - a) * 90)) : 0), 0);
function orbiCara(t, nombre, h) {
  const base = { ...EXPRESIONES[nombre] };
  if (h) { const a = 0.25 + 0.55 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 5.3)); base.boca = nombre === "feliz" ? [0.9, 1.2, Math.max(0.2, a)] : [0.15, 0.7, a]; }
  if ((t % 3.3) < 0.12 && base.oi > 0) { base.oi = 0.08; if (base.od > 0) base.od = 0.08; }
  return orbi(nombre, { e: base, anillo: -10 + 4 * Math.sin(t * 1.3), brillo: 0.6 }).replace("<svg ", '<svg width="380" height="380" ');
}
const DEFS = `<defs>
  <linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050a16"/><stop offset=".7" stop-color="#14223d"/><stop offset="1" stop-color="#2a2340"/></linearGradient>
  <linearGradient id="alba" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4f7a"/><stop offset=".6" stop-color="#e59a5c"/><stop offset="1" stop-color="#ffd79a"/></linearGradient>
  <radialGradient id="cono" cx="50%" cy="0%" r="100%"><stop offset="0" stop-color="rgba(255,214,150,.55)"/><stop offset="1" stop-color="rgba(255,214,150,0)"/></radialGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="rgba(255,220,160,.8)"/><stop offset=".3" stop-color="rgba(255,200,130,.25)"/><stop offset="1" stop-color="rgba(255,200,130,0)"/></radialGradient>
  <radialGradient id="neblina"><stop offset="0" stop-color="rgba(150,170,210,.22)"/><stop offset="1" stop-color="rgba(150,170,210,0)"/></radialGradient>
  <radialGradient id="charco"><stop offset="0" stop-color="rgba(255,210,140,.5)"/><stop offset=".6" stop-color="rgba(120,140,190,.15)"/><stop offset="1" stop-color="rgba(0,0,0,0)"/></radialGradient>
  <linearGradient id="haz" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="rgba(255,246,200,.55)"/><stop offset="1" stop-color="rgba(255,246,200,0)"/></linearGradient>
  <linearGradient id="muro" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1c1416"/><stop offset="1" stop-color="#3a2528"/></linearGradient>
  <linearGradient id="muroD" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#16141c"/><stop offset="1" stop-color="#2c2533"/></linearGradient>
  <linearGradient id="asfalto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#151821"/><stop offset="1" stop-color="#07080c"/></linearGradient>
  <filter id="sil" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 .02  0 0 0 0 .01  0 0 0 0 .035  0 0 0 1 0" result="s"/>
    <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#ff3fb5" flood-opacity=".75"/></filter>
  <clipPath id="ventana"><rect x="110" y="360" width="520" height="660"/></clipPath>
</defs>`;
// ---------- Ciudad bajo la lluvia (título y ventana) ----------
function ciudad(t, x0, y0, w, h, alba = 0) {
  let s = `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="url(#cielo)"/>`;
  if (alba > 0) s += `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="url(#alba)" opacity="${alba}"/>`;
  for (let i = 0; i < 16; i++) { const bw = 60 + azar(i) * 90, bx = x0 + (i / 16) * w * 1.1 - 30, bh = h * (0.3 + azar(i + 9) * 0.5), by = y0 + h - bh;
    s += `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" fill="${i % 2 ? "#0a0f1c" : "#0d1424"}"/>`;
    for (let j = 0; j < 10; j++) if (azar(i * 13 + j) > 0.55) s += `<rect x="${bx + 10 + (j % 3) * (bw / 3.4)}" y="${by + 18 + Math.floor(j / 3) * 42}" width="10" height="16" fill="#f1c76a" opacity="${(0.35 + 0.5 * azar(j + i)) * (1 - alba)}"/>`; }
  const on = alba > 0 ? 0 : (Math.sin(t * 23) > -0.6 || (t % 2.7) > 0.3 ? 1 : 0.15);
  s += `<g transform="translate(${x0 + w * 0.72} ${y0 + h * 0.3})" opacity="${on}"><rect x="-34" y="-10" width="68" height="250" rx="8" fill="#1a0a10" stroke="#ff3b5c" stroke-width="5"/>
    ${"HOTEL".split("").map((c, i) => `<text x="0" y="${36 + i * 46}" text-anchor="middle" font-size="40" font-weight="800" fill="#ff8095" font-family="Figtree" style="filter:drop-shadow(0 0 10px #ff3b5c)">${c}</text>`).join("")}</g>`;
  return s;
}
// ---------- Oficina del detective ----------
function oficina(t, o = {}) {
  const alba = o.alba || 0, rl = rayo(t);
  let w = `<rect x="-700" y="-700" width="2480" height="3400" fill="${alba ? "#2a2522" : "#121722"}"/>`;
  for (let i = 0; i < 30; i++) w += `<rect x="${-700 + i * 86}" y="-700" width="3" height="3400" fill="rgba(0,0,0,.25)"/>`;
  // ventana con ciudad, lluvia y persianas
  w += `<g clip-path="url(#ventana)">${ciudad(t, 110, 360, 520, 660, alba)}${alba ? "" : Array.from({ length: 50 }, (_, i) => { const x = 110 + azar(i) * 520, y = 360 + ((azar(i + 50) * 700 + t * 900) % 700);
    return `<line x1="${x}" y1="${y}" x2="${x - 6}" y2="${y + 40}" stroke="rgba(190,210,240,.45)" stroke-width="2"/>`; }).join("")}
    <rect x="110" y="360" width="520" height="660" fill="#fff" opacity="${rl * 0.8}"/>
    ${Array.from({ length: 9 }, (_, i) => `<rect x="110" y="${360 + i * 30}" width="520" height="22" fill="#2b2620" opacity=".95"/>`).join("")}</g>
    <rect x="110" y="360" width="520" height="660" fill="none" stroke="#2a1d14" stroke-width="22"/><line x1="370" y1="630" x2="370" y2="1020" stroke="#2a1d14" stroke-width="12"/>
    <line x1="140" y1="360" x2="140" y2="640" stroke="#555" stroke-width="2"/>`;
  // luz de la ventana proyectada en rayas sobre la pared y el piso
  const tono = alba ? `rgba(255,190,120,${0.13})` : `rgba(150,180,255,${0.05 + rl * 0.25})`;
  w += Array.from({ length: 8 }, (_, i) => `<path d="M${640 + i * 10} ${640 + i * 34} L ${1500} ${900 + i * 70} L ${1500} ${920 + i * 70} L ${640 + i * 10} ${654 + i * 34}Z" fill="${tono}"/>`).join("");
  // ventilador de techo
  const ang = (t * 210) % 360;
  w += `<g transform="translate(720 150)"><line x1="0" y1="-200" x2="0" y2="0" stroke="#111" stroke-width="10"/><g transform="scale(1 .22)">${[0, 90, 180, 270].map((a) => `<ellipse cx="${150 * Math.cos((ang + a) * Math.PI / 180)}" cy="${150 * Math.sin((ang + a) * Math.PI / 180)}" rx="120" ry="40" transform="rotate(${ang + a} ${150 * Math.cos((ang + a) * Math.PI / 180)} ${150 * Math.sin((ang + a) * Math.PI / 180)})" fill="#1e1a17"/>`).join("")}</g><ellipse rx="34" ry="18" fill="#2a2420"/></g>`;
  // puerta con vidrio esmerilado (se abre en «cliente»)
  const ab = o.puerta || 0;
  w += `<rect x="790" y="540" width="280" height="760" fill="#e8c27a" opacity="${ab}"/>${ab > 0 ? `<g opacity="${ab}"><path d="M790 1300 L 1070 1300 L 1400 1500 L 600 1500Z" fill="rgba(232,194,122,.25)"/></g>` : ""}
    <g transform="translate(790 540) scale(${1 - 0.8 * ab} 1)"><rect width="280" height="760" fill="#3a2414" stroke="#22150b" stroke-width="10"/><rect x="30" y="40" width="220" height="330" fill="#9fb1bf" opacity=".55"/>
      <g transform="translate(140 180) scale(-1 1)"><text text-anchor="middle" font-size="30" fill="#1a1410" font-family="Special Elite">ORBI</text><text y="40" text-anchor="middle" font-size="18" fill="#1a1410" font-family="Special Elite">INVESTIGACIONES</text></g>
      <circle cx="40" cy="420" r="12" fill="#c9a65a"/></g>`;
  if (o.sombraVidrio) w += `<g opacity="${o.sombraVidrio}"><ellipse cx="930" cy="660" rx="45" ry="55" fill="#1a1410"/><path d="M860 760 Q 930 700 1000 760 L 1010 900 L 850 900Z" fill="#1a1410"/></g>`;
  w += o.antes || "";
  // escritorio y utilería
  w += `<path d="M-300 1370 L 1380 1370 L 1500 1500 L -420 1500Z" fill="#3b2617"/><rect x="-420" y="1500" width="1920" height="900" fill="#24160c"/>
    <line x1="-420" y1="1500" x2="1500" y2="1500" stroke="#5a3a22" stroke-width="6"/>
    <ellipse cx="230" cy="1420" rx="210" ry="40" fill="rgba(255,210,140,.18)"/>`;
  // lámpara de banquero
  w += `<g transform="translate(230 1330)"><path d="M-90 -130 L 90 -130 L 0 140" fill="url(#cono)" opacity=".7"/><ellipse cx="0" cy="40" rx="60" ry="14" fill="#2a2016"/>
    <rect x="-6" y="-120" width="12" height="160" fill="#c9a65a"/><path d="M-90 -130 Q -88 -186 0 -190 Q 88 -186 90 -130Z" fill="#1f6b46"/><path d="M-90 -130 L 90 -130" stroke="#c9a65a" stroke-width="6"/>
    <ellipse cx="0" cy="-128" rx="60" ry="8" fill="#fff3c8"/></g>`;
  // taza con vapor
  w += `<g transform="translate(420 1390)"><rect x="-32" y="-50" width="64" height="62" rx="10" fill="#e9e2d0"/><path d="M32 -36 q 26 6 0 30" stroke="#e9e2d0" stroke-width="8" fill="none"/>
    ${[0, 1, 2].map((i) => `<path d="M${-14 + i * 14} -60 q ${10 * Math.sin(t * 3 + i)} -26 0 -52 q ${-10 * Math.sin(t * 3 + i)} -26 0 -52" stroke="rgba(230,230,240,${0.3 - 0.08 * i})" stroke-width="6" fill="none" transform="translate(0 ${-((t * 30 + i * 20) % 40)})"/>`).join("")}</g>`;
  // máquina de escribir
  w += `<g transform="translate(600 1395)"><rect x="-90" y="-210" width="180" height="120" fill="#efe6d2" transform="rotate(-2)"/>${[-180, -160, -140].map((y) => `<line x1="-70" y1="${y}" x2="60" y2="${y}" stroke="#8a8170" stroke-width="5"/>`).join("")}
    <rect x="-150" y="-100" width="300" height="40" rx="14" fill="#1c1c20"/><path d="M-130 -60 L 130 -60 L 150 20 L -150 20Z" fill="#26262c"/>
    ${Array.from({ length: 24 }, (_, i) => `<circle cx="${-112 + (i % 8) * 32 + Math.floor(i / 8) * 8}" cy="${-40 + Math.floor(i / 8) * 20}" r="8" fill="#d8d0bc"/>`).join("")}</g>`;
  // teléfono de disco
  w += `<g transform="translate(40 1400)"><path d="M-80 20 L -60 -50 L 60 -50 L 80 20Z" fill="#111"/><circle cy="-10" r="34" fill="#222" stroke="#c9a65a" stroke-width="3"/>
    ${Array.from({ length: 8 }, (_, i) => `<circle cx="${22 * Math.cos(i * 0.7)}" cy="${-10 + 22 * Math.sin(i * 0.7)}" r="5" fill="#ddd"/>`).join("")}<path d="M-90 -64 Q 0 -100 90 -64 L 80 -48 Q 0 -78 -80 -48Z" fill="#000"/></g>`;
  // carpeta del expediente
  const sello = o.sello || 0;
  w += `<g transform="translate(${o.carpetaX || 760} 1450) rotate(-4)"><rect x="-140" y="-60" width="280" height="110" rx="6" fill="#c9a66b"/><rect x="-140" y="-74" width="110" height="24" rx="6" fill="#c9a66b"/>
    <text x="-120" y="-10" font-size="28" fill="#3a2a1a" font-family="Special Elite">EXPEDIENTE 27</text><text x="-120" y="26" font-size="18" fill="#3a2a1a" font-family="Special Elite">Asadero El Fogón</text>
    ${sello > 0 ? `<g transform="translate(60 0) rotate(-14) scale(${lerp(2.2, 1, out3(sello))})" opacity="${cl(sello * 3)}"><rect x="-120" y="-34" width="240" height="68" rx="8" fill="none" stroke="#c01b2c" stroke-width="7"/>
      <text y="18" text-anchor="middle" font-size="46" fill="#c01b2c" font-family="Special Elite">CERRADO</text></g>` : ""}</g>`;
  w += `<g transform="translate(270 1560)"><rect x="-150" y="-36" width="300" height="72" rx="6" fill="#1a120a" stroke="#c9a65a" stroke-width="4"/><text y="10" text-anchor="middle" font-size="28" fill="#e8c27a" font-family="Special Elite">ORBI · DETECTIVE</text></g>`;
  w += o.despues || "";
  return w;
}
// ---------- Pizarra de pistas ----------
const RECIBOS = [[250, 640, -6, 4, "48.000"], [800, 610, 5, 11, "62.000"], [220, 1260, 4, 17, "35.000"], [840, 1290, -5, 22, "71.000"], [540, 1500, 2, 29, "55.000"], [520, 470, -2, 30, "40.000"]];
function tablero(t, p) {
  const nar = lin("narra", "pistas");
  let s = `<rect x="-300" y="-300" width="1680" height="2520" fill="#0d0b0a"/><rect x="40" y="330" width="1000" height="1380" rx="10" fill="#5a3a22"/><rect x="66" y="356" width="948" height="1328" fill="#a17f53"/>`;
  for (let i = 0; i < 260; i++) s += `<circle cx="${70 + azar(i) * 940}" cy="${360 + azar(i + 400) * 1320}" r="${2 + azar(i + 800) * 3}" fill="rgba(60,40,20,.35)"/>`;
  // foto del local, mapa y notas
  s += `<g transform="translate(830 960) rotate(4)"><rect x="-110" y="-90" width="220" height="190" fill="#f4f1ea"/><rect x="-96" y="-76" width="192" height="130" fill="#2c3440"/>
      <rect x="-80" y="-30" width="160" height="80" fill="#6e1f1f"/><text y="-40" text-anchor="middle" font-size="20" fill="#f1c76a" font-family="Figtree" font-weight="800">EL FOGÓN</text>
      <text y="84" text-anchor="middle" font-size="20" fill="#2a2420" font-family="Special Elite">el cliente</text></g>${chincheta(830, 875)}
    <g transform="translate(240 950) rotate(-3)"><rect x="-120" y="-80" width="240" height="160" fill="#f2e3a0"/><text x="-100" y="-30" font-size="28" fill="#2a2420" font-family="Special Elite">27 % × 30</text>
      <text x="-100" y="14" font-size="28" fill="#2a2420" font-family="Special Elite">pedidos =</text><text x="-100" y="58" font-size="34" fill="#c01b2c" font-family="Special Elite">¿quién?</text></g>${chincheta(240, 880, "#2fbbe8")}`;
  // foto central: la sombra con corona
  s += `<g transform="translate(540 980) rotate(-2)"><rect x="-130" y="-150" width="260" height="300" fill="#f4f1ea"/><rect x="-110" y="-130" width="220" height="210" fill="#1a1a22"/>
      <g transform="translate(0 -10) scale(.32)" filter="url(#sil)">${comi({ cara: "diva" })}</g><text y="-30" text-anchor="middle" font-size="120" fill="rgba(255,255,255,.85)" font-family="Special Elite">?</text>
      <text y="124" text-anchor="middle" font-size="26" fill="#2a2420" font-family="Special Elite">sospechosa</text></g>`;
  // hilos rojos que se van tendiendo
  RECIBOS.forEach(([x, y], i) => { const k = cl(p * 1.6 - i * 0.12); if (k > 0) s += `<line x1="${x}" y1="${y - 120}" x2="${lerp(x, 540, k)}" y2="${lerp(y - 120, 850, k)}" stroke="#c01b2c" stroke-width="5"/>`; });
  RECIBOS.forEach(([x, y, r, n, v], i) => { const marca = nar ? cl((t - nar.ini - 3.0 - i * 0.12) / 0.5) : 0; s += `<g transform="translate(${x} ${y}) rotate(${r})">${recibo(n, v, marca)}</g>${chincheta(x, y - 120)}`; });
  s += chincheta(540, 850);
  return s;
}
// ---------- Callejón bajo la lluvia ----------
function callejon(t, o = {}) {
  const rl = rayo(t), VP = [560, 860];
  let w = `<rect x="-800" y="-800" width="2680" height="3600" fill="#07080d"/>`;
  w += ciudad(t, 360, 160, 400, 700);
  w += `<path d="M-800 -800 L 380 520 L 380 1130 L -800 2600Z" fill="url(#muro)"/><path d="M1880 -800 L 740 520 L 740 1130 L 1880 2600Z" fill="url(#muroD)"/>`;
  for (let i = -6; i <= 14; i++) { const a = i / 14; w += `<line x1="-800" y1="${-800 + a * 3400}" x2="380" y2="${520 + a * 610}" stroke="rgba(0,0,0,.35)" stroke-width="3"/><line x1="1880" y1="${-800 + a * 3400}" x2="740" y2="${520 + a * 610}" stroke="rgba(0,0,0,.35)" stroke-width="3"/>`; }
  for (let i = 0; i < 12; i++) { const x = lerp(-300, 360, i / 12); w += `<line x1="${x}" y1="${lerp(-300, 560, i / 12) - 400}" x2="${x}" y2="${lerp(2300, 1110, i / 12)}" stroke="rgba(0,0,0,.18)" stroke-width="2"/>`; }
  w += `<path d="M380 1130 L 740 1130 L 1880 2600 L -800 2600Z" fill="url(#asfalto)"/>`;
  // escalera de incendios
  w += `<g stroke="#0c0b10" stroke-width="10" fill="none"><path d="M1020 420 L 860 600 M1020 640 L 860 760 M1020 860 L 860 920"/><path d="M1060 560 L 900 700 L 900 640 M1060 800 L 900 860"/></g>`;
  // aviso de neón titilante
  const neon = (Math.sin(t * 17) > -0.7 || (t % 1.9) > 0.2) ? 1 : 0.15;
  w += `<g transform="translate(160 700) skewY(18)" opacity="${neon}"><rect x="-120" y="-60" width="240" height="110" rx="14" fill="#14060f" stroke="#ff3fb5" stroke-width="6"/>
    <text y="12" text-anchor="middle" font-size="44" font-weight="800" fill="#ffc2e8" font-family="Figtree" style="filter:drop-shadow(0 0 12px #ff3fb5)">24 HORAS</text></g>`;
  // farol al fondo, cono de luz volumétrico y charcos
  w += `<path d="M640 560 L 660 560 L 660 1150 L 640 1150Z" fill="#0b0b10"/><path d="M650 560 Q 650 520 610 520 L 590 520" stroke="#0b0b10" stroke-width="12" fill="none"/>
    <path d="M560 528 L 620 528 L 600 548 L 580 548Z" fill="#222"/><circle cx="590" cy="548" r="120" fill="url(#halo)"/>
    <path d="M574 548 L 606 548 L 760 1180 L 420 1180Z" fill="url(#cono)" opacity=".75"/><ellipse cx="590" cy="1170" rx="190" ry="30" fill="rgba(255,214,150,.22)"/>
    <ellipse cx="560" cy="1420" rx="260" ry="46" fill="url(#charco)"/><ellipse cx="300" cy="1700" rx="300" ry="60" fill="url(#charco)" opacity=".6"/>
    <ellipse cx="160" cy="1480" rx="140" ry="26" fill="rgba(255,63,181,.18)"/>`;
  // salpicaduras de lluvia en el piso
  for (let i = 0; i < 26; i++) { const ph = (t * 1.7 + azar(i)) % 1, x = 420 + (azar(i + 3) - 0.5) * 1100, y = 1160 + azar(i + 7) * 700;
    w += `<ellipse cx="${x}" cy="${y}" rx="${4 + ph * 26}" ry="${1 + ph * 6}" fill="none" stroke="rgba(190,210,240,${0.4 * (1 - ph)})" stroke-width="2"/>`; }
  // canecas, alcantarilla con vapor, gato
  w += `<g transform="translate(180 1360)"><rect x="-80" y="-140" width="160" height="180" rx="10" fill="#1f2a2a"/><rect x="-90" y="-158" width="180" height="26" rx="8" fill="#2a3838"/>${[-40, 0, 40].map((x) => `<line x1="${x}" y1="-120" x2="${x}" y2="30" stroke="#152020" stroke-width="6"/>`).join("")}</g>
    <g transform="translate(320 1300) scale(.7)"><rect x="-80" y="-140" width="160" height="180" rx="10" fill="#1a2230"/><rect x="-90" y="-158" width="180" height="26" rx="8" fill="#243044" transform="rotate(-12)"/></g>
    <ellipse cx="620" cy="1560" rx="120" ry="24" fill="#0f1116" stroke="#2a2d36" stroke-width="5"/>
    ${[0, 1, 2, 3].map((i) => { const ph = (t * 0.35 + i * 0.25) % 1; return `<ellipse cx="${620 + Math.sin(t + i) * 40}" cy="${1540 - ph * 520}" rx="${90 + ph * 220}" ry="${60 + ph * 140}" fill="url(#neblina)" opacity="${1 - ph}"/>`; }).join("")}
    ${(t % 4) > 0.2 ? `<g transform="translate(930 1240)"><ellipse cx="-14" rx="9" ry="${(t % 4) < 0.35 ? 1 : 6}" fill="#d8ff6a"/><ellipse cx="14" rx="9" ry="${(t % 4) < 0.35 ? 1 : 6}" fill="#d8ff6a"/></g>` : ""}`;
  // huellas de la mochila (magenta) que se encienden con la linterna
  const hu = o.huellas ?? 0;
  for (let i = 0; i < 9; i++) { const a = i / 8, x = lerp(440, 620, a) + (i % 2 ? 26 : -26) * (1 - a * 0.6), y = lerp(1500, 1180, a), s = lerp(1.1, 0.45, a), on = cl((hu - a) * 4);
    w += `<g transform="translate(${x} ${y}) scale(${s} ${s * 0.4})" opacity="${on}"><rect x="-22" y="-30" width="44" height="60" rx="16" fill="#ff3fb5" style="filter:drop-shadow(0 0 10px #ff3fb5)"/></g>`; }
  // niebla que cruza (detrás de los personajes)
  for (let i = 0; i < 4; i++) w += `<ellipse cx="${(i * 400 + t * 40) % 1800 - 300}" cy="${1100 + i * 120}" rx="420" ry="90" fill="url(#neblina)"/>`;
  w += o.medio || "";
  w += `<rect x="-800" y="-800" width="2680" height="3600" fill="#cfe0ff" opacity="${rl * 0.35}"/>`;
  return w;
}
// ---------- Cámara ----------
const CAM = { titulo: [[540, 960, 1], [540, 960, 1.04]], oficina: [[370, 640, 1.7], [540, 1120, 1.12]], cliente: [[660, 1120, 1.12], [640, 1110, 1.2]],
  pistas: [[540, 980, 0.98], [540, 980, 1.1]], callejon: [[420, 1300, 1.15], [560, 1150, 1.3]], revela: [[560, 1170, 1.22], [570, 1170, 1.3]],
  cierre: [[560, 1180, 1.12], [700, 1330, 1.45]], sello: [[540, 960, 1], [540, 960, 1]] };
function camara(t) {
  const k = escenaDe(t), [a, b] = E[k], p = (t - a) / (b - a), [c0, c1] = CAM[k];
  let c = c0.map((v, i) => lerp(v, c1[i], ease(p)));
  if (k === "cliente") { const o = lin("orbi", "cliente"); if (o) { const q = ease((t - o.ini + 0.4) / 0.6); c = c.map((v, i) => lerp(v, [540, 1060, 1.42][i], q)); } }
  if (k === "pistas") { const n = lin("narra", "pistas"); if (n) { const q = ease((t - n.ini - 2.8) / 0.9); c = c.map((v, i) => lerp(v, [250, 720, 2.35][i], q)); } }
  if (k === "callejon") { const s = lin("comi", "callejon"); if (s) { const q = ease((t - s.ini + 0.6) / 1.6); c = c.map((v, i) => lerp(v, [610, 1030, 2.1][i], q)); } }
  if (k === "revela") { const n = lin("comi", "revela"); if (n) { const q = ease((t - n.ini + 0.1) / 0.3); c = c.map((v, i) => lerp(v, [690, 1150, 1.7][i], q)); } }
  return c;
}
let ultimo = "";
async function render(t, f) {
  const k = escenaDe(t), [a, b] = E[k], tt = t - a;
  let w = "";
  if (k === "titulo" || k === "sello") w = ciudad(t, -300, -300, 1680, 2600) + `<rect x="-300" y="1500" width="1680" height="800" fill="#05060a"/>`;
  if (k === "oficina" || k === "cliente") {
    let det = orbiCara(t, "normal", habla("orbi", t)), antes = "", sombra = 0, puerta = 0;
    const ac = lin("aure", "cliente");
    if (k === "oficina") det = orbiCara(t, tt > 3 ? "sarcastico" : "normal", false);
    if (k === "cliente") {
      sombra = cl(tt / 0.3) * cl((0.9 - tt) / 0.2); puerta = ease((tt - 0.6) / 0.5);
      const entra = out3((tt - 0.9) / 0.8), ax = lerp(930, 860, entra), ay = lerp(1240, 1290, entra);
      antes += g(ax, ay, 1.35 * lerp(0.85, 1, entra), aurelio({ boca: habla("aure", t) ? boca(t) : 0.3, mojado: true, mira: -6 }), cl((tt - 0.75) / 0.3));
      det = orbiCara(t, habla("aure", t) ? "triste" : "normal", habla("orbi", t));
    }
    const oy = 1050 + Math.sin(t * 2) * 10;
    antes = `<g transform="translate(470 ${oy}) scale(.82)">${detective(det)}</g>` + antes;
    w = oficina(t, { antes, puerta, sombraVidrio: sombra });
  }
  if (k === "pistas") {
    const nar = lin("narra", "pistas"), p = nar ? cl((t - nar.ini) / (nar.fin - nar.ini)) : 0;
    const base = tablero(t, p);
    w = base + `<path d="M-300 -300 L 1380 -300 L 1380 2220 L -300 2220Z" fill="rgba(0,0,0,.0)"/><circle cx="540" cy="700" r="900" fill="url(#halo)" opacity=".18"/>`;
    // lupa que recorre los recibos y amplía lo que hay debajo
    const ruta = [[520, 1500], [220, 1260], [840, 1290], [800, 610], [250, 720]], seg = cl(p * 1.25) * (ruta.length - 1), i0 = Math.min(ruta.length - 2, Math.floor(seg)), q = ease(seg - i0);
    const lx = lerp(ruta[i0][0], ruta[i0 + 1][0], q) + Math.sin(t * 2) * 8, ly = lerp(ruta[i0][1], ruta[i0 + 1][1], q) + Math.cos(t * 1.7) * 8, R = 95;
    w += `<defs><clipPath id="lente"><circle cx="${lx}" cy="${ly}" r="${R}"/></clipPath></defs><g clip-path="url(#lente)"><g transform="translate(${lx} ${ly}) scale(1.7) translate(${-lx} ${-ly})">${base}</g></g>`
      + `<g transform="translate(${lx} ${ly})">${lupa(R)}</g>`;
  }
  if (k === "callejon" || k === "revela") {
    const nar = lin("narra", "callejon"), hu = nar ? cl((t - nar.ini) / 2.0) : 1;
    const sc = lin("comi", "callejon"), nooo = lin("comi", "revela"), orbiR = lin("orbi", "revela");
    let medio = "";
    // Comi: silueta bajo el farol; con el rayo de «revela» sale a la luz
    if (k === "callejon" && sc && t > sc.ini - 1.0) {
      const ap = cl((t - sc.ini + 1.0) / 0.8);
      medio += `<ellipse cx="610" cy="1150" rx="${90 * ap}" ry="14" fill="rgba(0,0,0,.6)"/><path d="M590 1150 L ${640} 1150 L ${520} ${1150 + 380 * ap} L ${380} ${1150 + 380 * ap}Z" fill="rgba(0,0,0,${0.45 * ap})"/>`
        + `<g opacity="${ap}">${g(612, 1048, 0.42, comiNoir({ cara: "diva", boca: habla("comi", t) ? boca(t) : 0 }), 1, Math.sin(t * 1.4) * 2).replace("<g transform", '<g filter="url(#sil)" transform')}</g>`
        + `<g opacity="${ap * (0.6 + 0.4 * Math.sin(t * 5))}"><path d="M582 1036 L 594 1036 M632 1036 L 644 1036" stroke="#fff" stroke-width="3"/></g>`;
    }
    if (k === "revela") {
      const derrite = nooo ? ease((t - nooo.ini) / 1.0) : 0, cx = lerp(612, 720, out3(tt / 0.4)), cy = lerp(1048, 1180, out3(tt / 0.4)), cs = lerp(0.42, 0.66, out3(tt / 0.4));
      const temb = derrite > 0 ? Math.sin(t * 60) * 6 * (1 - derrite) : 0;
      medio += `<ellipse cx="${cx}" cy="${cy + 170 * cs / 0.66}" rx="${130 * (1 - derrite * 0.3)}" ry="18" fill="rgba(0,0,0,.6)"/>`;
      medio += `<g transform="translate(${cx + temb} ${cy + 160 * derrite}) scale(${cs * (1 + 0.25 * derrite)} ${cs * (1 - derrite)})" opacity="${1 - derrite * 0.6}">${comiNoir({ cara: derrite > 0 ? "shock" : orbiR && habla("orbi", t) ? "shock" : "enojo", boca: habla("comi", t) ? 1 : 0, abierto: derrite > 0.05, gafas: derrite < 0.2, brazoArriba: derrite > 0 })}</g>`;
      if (derrite > 0) { medio += `<ellipse cx="${cx}" cy="${cy + 170}" rx="${60 + 160 * derrite}" ry="${10 + 24 * derrite}" fill="#b5179e" opacity=".75"/>`;
        for (let i = 0; i < 8; i++) { const ph = cl(derrite * 1.4 - i * 0.05); medio += billete(cx + 150 + i * 30 - ph * 900 * (0.4 + azar(i)), cy + 60 - Math.sin(ph * Math.PI) * 420 - i * 10, ph * 600 + i * 40); } }
      // holograma del pedido directo
      if (orbiR && t > orbiR.ini + 1.0) { const q = rebote((t - orbiR.ini - 1.0) / 0.5), sale = nooo ? 1 - cl((t - nooo.ini) / 0.3) * 0 : 1;
        medio += `<g transform="translate(420 960) scale(${q})" opacity="${sale}"><path d="M-40 260 L -190 -20 L 190 -20 L 40 260Z" fill="rgba(47,187,232,.12)"/>
          <rect x="-200" y="-140" width="400" height="200" rx="26" fill="rgba(8,30,55,.88)" stroke="#2fbbe8" stroke-width="5"/>
          <text x="-170" y="-88" font-size="24" fill="#5fc9f1" font-family="Figtree" font-weight="800" letter-spacing="3">APEX DOMICILIOS</text>
          <text x="-170" y="-44" font-size="32" fill="#fff" font-family="Figtree" font-weight="800">Pedido #31 · El Fogón</text>
          <text x="-170" y="-2" font-size="26" fill="#9db0c5" font-family="Figtree">Directo al restaurante</text>
          <g transform="translate(110 30) rotate(-8)"><rect x="-96" y="-26" width="192" height="52" rx="10" fill="rgba(5,30,20,.95)" stroke="#2ee59d" stroke-width="5"/><text y="10" text-anchor="middle" font-size="28" font-weight="800" fill="#2ee59d" font-family="Figtree">0 % comisión</text></g></g>`; }
    }
    // Orbi detective con linterna
    const ox = k === "callejon" ? lerp(240, 330, ease(tt / 3)) : 330, oy = 1300 + Math.sin(t * 2) * 10;
    const cara = k === "callejon" ? (sc && t > sc.ini - 0.6 ? "sorprendido" : "normal") : (habla("comi", t) || (nooo && t > nooo.ini) ? "guino" : "orgulloso");
    const det = `<g transform="translate(${ox} ${oy}) scale(.62)">${detective(orbiCara(t, cara, habla("orbi", t)))}</g>`;
    const lx = ox + 150, ly = oy - 40; let ha = k === "callejon" ? lerp(-0.25, -0.12, hu) : -0.08;
    if (k === "callejon" && sc) ha = lerp(ha, Math.atan2(1010 - ly, 600 - lx), ease((t - sc.ini + 0.8) / 0.7));
    const haz = `<g transform="translate(${lx} ${ly}) rotate(${ha * 180 / Math.PI})"><path d="M60 -10 L 900 -110 L 900 110 L 60 10Z" fill="url(#haz)"/><g transform="scale(.8)">${linterna()}</g></g>`;
    w = callejon(t, { huellas: hu, medio: medio + haz + det });
  }
  if (k === "cierre") {
    const n = lin("narra", "cierre"), sello = n ? cl((t - n.ini - 0.1) / 0.35) : 0;
    const antes = `<g transform="translate(470 ${1050 + Math.sin(t * 2) * 10}) scale(.82)">${detective(orbiCara(t, tt > 2.4 ? "guino" : "orgulloso", false), { sombrero: tt > 2.4 ? 14 * ease((tt - 2.4) / 0.4) : 0 })}</g>`
      + g(860, 1290, 1.35, aurelio({ boca: 0.9, cejas: "arriba", puesto: true, mira: -4 }) + billetes(6, 180, 70));
    w = oficina(t, { alba: 1, antes, sello, carpetaX: 700 });
  }
  const [cx, cy, cs] = camara(t), nooo = lin("comi", "revela");
  let sac = 0; if (k === "cierre") { const n = lin("narra", "cierre"); if (n && t > n.ini + 0.25 && t < n.ini + 0.45) sac = 12; } if (nooo && t > nooo.ini && t < nooo.ini + 0.6) sac = 10;
  const sx = sac * Math.sin(f * 7.1), sy = sac * Math.cos(f * 5.3);
  $("#escena").innerHTML = `<svg viewBox="0 0 1080 1920" width="1080" height="1920">${DEFS}<g transform="translate(${540 + sx} ${960 + sy}) scale(${cs}) translate(${-cx} ${-cy})">${w}</g></svg>`;
  // lluvia en primer plano (afuera)
  const llueve = ["titulo", "callejon", "revela", "sello"].includes(k);
  $("#lluvia").innerHTML = llueve ? Array.from({ length: 170 }, (_, i) => { const v = 2200 + azar(i + 5) * 900, x = azar(i) * 1200 - 60 - ((t * v * 0.12) % 1200) * 0 + ((t * 120) % 60), y = ((azar(i + 99) * 2100 + t * v) % 2100) - 100, l = 50 + azar(i + 7) * 60;
    return `<line x1="${x}" y1="${y}" x2="${x - l * 0.18}" y2="${y + l}" stroke="rgba(200,215,240,${0.18 + azar(i + 3) * 0.3})" stroke-width="${1.5 + azar(i + 1) * 2}"/>`; }).join("") : "";
  $("#flash").style.opacity = Math.min(0.85, rayo(t) * 0.7);
  // fundidos a negro entre escenas (callejón → revela es corte directo con relámpago)
  let negro = 0; Object.keys(E).forEach((e) => { const x = E[e][0]; if (x > 0 && e !== "revela") negro = Math.max(negro, 1 - cl(Math.abs(t - x) / 0.22)); });
  if (k === "titulo") negro = Math.max(negro, 1 - cl(tt / 0.4));
  $("#negro").style.opacity = negro;
  // gradación: fría de noche, cálida al amanecer
  $("#tinte").style.background = k === "cierre" ? "linear-gradient(180deg, rgba(255,170,90,.18), rgba(120,60,20,.12))" : "linear-gradient(180deg, rgba(20,60,120,.28), rgba(10,20,50,.35))";
  // título
  const T = "EXPEDIENTE 27", n = k === "titulo" ? Math.floor(cl((tt - 0.5) / 1.1) * T.length) : 0;
  $("#titulo").style.opacity = k === "titulo" ? cl((b - t) / 0.35) : 0;
  $("#tecla").textContent = T.slice(0, n); $("#cursor").style.opacity = (Math.floor(t * 3) % 2 && n < T.length) ? 1 : (n < T.length ? 0 : 0);
  $("#titulo small").style.opacity = out3((tt - 1.6) / 0.5); $("#titulo em").style.opacity = out3((tt - 0.1) / 0.5);
  // subtítulos
  const l = L.find((x) => t >= x.ini - 0.05 && t < x.fin + 0.35), sub = $("#sub");
  if (l && k !== "sello") { if (ultimo !== l.txt) { ultimo = l.txt;
      const quien = { narra: "EL DETECTIVE · VOZ EN OFF", orbi: "ORBI", aure: "DON AURELIO · ASADERO EL FOGÓN", comi: l.esc === "callejon" ? "LA SOMBRA" : "COMI" }[l.quien];
      sub.innerHTML = `<small>${quien}</small>${l.txt}`; sub.className = l.quien; }
    sub.style.opacity = out3((t - l.ini + 0.05) / 0.15) * cl((l.fin + 0.35 - t) / 0.15); } else sub.style.opacity = 0;
  // cierre de marca
  if (k === "sello") {
    const q = out3(tt / 0.5); $("#sello").style.opacity = q;
    $("#o-final").innerHTML = `<svg viewBox="-260 -300 520 600" width="560" height="646">${detective(orbiCara(t, tt < 0.8 ? "normal" : "guino", false), { sombrero: 16 * ease((tt - 0.6) / 0.4) * (1 - ease((tt - 2.2) / 0.4)) })}</svg>`;
    const F = "CASO CERRADO."; $("#frase").textContent = F.slice(0, Math.floor(cl((tt - 0.3) / 0.6) * F.length));
    $("#logo").style.opacity = out3((tt - 1.0) / 0.5);
  } else $("#sello").style.opacity = 0;
  grano(f);
}
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
