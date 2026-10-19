// Escenarios de «Cine Apex». Mismo sistema de coordenadas que «heroes» (cuadro de 1080 x 1920, la cámara se mueve encima).
const cielo = (id, stops) => `<linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1">${stops.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join("")}</linearGradient>`;
const CINE_DEFS = `<defs>
  ${cielo("cAtardecerZ", [[0, "#1a0c08"], [0.45, "#7a2a0e"], [0.75, "#e0702a"], [1, "#ffb15a"]])}
  ${cielo("cAlba", [[0, "#2a3440"], [0.6, "#8a8f86"], [1, "#d8c9a0"]])}
  ${cielo("cDorado", [[0, "#3a5a7a"], [0.5, "#e8a860"], [1, "#ffd9a0"]])}
  ${cielo("cLaLa", [[0, "#0d1440"], [0.35, "#3a2a7a"], [0.65, "#a04a9a"], [0.85, "#f08a6a"], [1, "#ffc48a"]])}
  ${cielo("cNeon", [[0, "#02040a"], [0.5, "#0a1424"], [1, "#1a1030"]])}
  ${cielo("cOficina", [[0, "#cfe3f0"], [1, "#f4f8fb"]])}
  <radialGradient id="llamaZ"><stop offset="0" stop-color="rgba(255,200,90,.9)"/><stop offset=".4" stop-color="rgba(255,110,30,.5)"/><stop offset="1" stop-color="rgba(255,60,0,0)"/></radialGradient>
  <radialGradient id="humo"><stop offset="0" stop-color="rgba(30,25,25,.7)"/><stop offset="1" stop-color="rgba(30,25,25,0)"/></radialGradient>
  <radialGradient id="niebla"><stop offset="0" stop-color="rgba(220,220,210,.35)"/><stop offset="1" stop-color="rgba(220,220,210,0)"/></radialGradient>
  <radialGradient id="vela"><stop offset="0" stop-color="rgba(255,190,110,.65)"/><stop offset="1" stop-color="rgba(255,150,60,0)"/></radialGradient>
  <radialGradient id="foco"><stop offset="0" stop-color="rgba(255,240,210,.55)"/><stop offset="1" stop-color="rgba(255,240,210,0)"/></radialGradient>
  <radialGradient id="neonC"><stop offset="0" stop-color="rgba(0,240,255,.5)"/><stop offset="1" stop-color="rgba(0,240,255,0)"/></radialGradient>
  <radialGradient id="neonM"><stop offset="0" stop-color="rgba(255,40,170,.5)"/><stop offset="1" stop-color="rgba(255,40,170,0)"/></radialGradient>
  <linearGradient id="agua" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6a8aa0"/><stop offset="1" stop-color="#1e3446"/></linearGradient>
</defs>`;
const silueta = (t, base, alto, color, sem, rota = 0) => { let s = "", x = -800;
  for (let i = 0; x < 1900; i++) { const w = 80 + rnd(sem + i) * 160, h = alto * (0.4 + rnd(sem + i * 3) * 0.6), y = base - h;
    s += rota && rnd(sem + i * 5) > 0.5 ? `<path d="M${x} ${base} L ${x} ${y + 30} L ${x + w * 0.3} ${y} L ${x + w * 0.5} ${y + 40} L ${x + w * 0.7} ${y + 10} L ${x + w} ${y + 60} L ${x + w} ${base} Z" fill="${color}"/>` : `<rect x="${x}" y="${y}" width="${w}" height="${h + 600}" fill="${color}"/>`;
    x += w + 4; } return s; };
function ruinas(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="url(#cAtardecerZ)"/><circle cx="760" cy="900" r="160" fill="#ffd28a" opacity=".85"/>`;
  s += [0, 1, 2, 3].map((i) => `<ellipse cx="${100 + i * 300 + Math.sin(t * 0.3 + i) * 30}" cy="${700 - i * 60 - t * 6}" rx="${220 + i * 40}" ry="${380 + i * 30}" fill="url(#humo)"/>`).join("");
  s += silueta(t, 1350, 700, "#2a1208", 5, 1) + `<rect x="-900" y="1350" width="2900" height="1600" fill="#140804"/>`;
  s += [180, 620, 940].map((x, i) => `<ellipse cx="${x}" cy="1340" rx="${140 + 30 * Math.sin(t * 7 + i)}" ry="${90 + 20 * Math.sin(t * 9 + i)}" fill="url(#llamaZ)"/>`).join("");
  if (o.helicoptero !== false) s += `<g transform="translate(${(t * 70) % 1600 - 300} ${360 + Math.sin(t) * 10})"><path d="M-60 0 Q -40 -26 20 -22 L 60 -10 L 120 -14 L 120 -4 L 60 4 Q 20 22 -50 14 Z" fill="#1a0a06"/><line x1="-90" y1="-30" x2="${70 * Math.cos(t * 40)}" y2="-30" stroke="#1a0a06" stroke-width="4"/></g>`;
  return s + `<rect x="-900" y="-900" width="2900" height="3800" fill="rgba(80,30,10,.15)"/>`;
}
function muro(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="url(#cAtardecerZ)"/>`;
  s += `<rect x="-900" y="560" width="2900" height="900" fill="#5a4a3a"/>` + Array.from({ length: 24 }, (_, i) => `<line x1="-900" y1="${600 + i * 36}" x2="2000" y2="${600 + i * 36}" stroke="#3e3226" stroke-width="3"/>`).join("");
  // la pirámide de hambrientos que trepa el muro
  const h = o.altura ?? 0.8; let p = "";
  for (let i = 0; i < 260; i++) { const fila = Math.floor(Math.sqrt(i * 2)), x = 540 + (rnd(i) - 0.5) * (900 - fila * 30) * (1 - fila / 30), y = 1460 - fila * 34 * h - rnd(i + 3) * 30;
    if (y < 560) continue; const b = Math.sin(t * 5 + i) * 6;
    p += `<g transform="translate(${x} ${y})"><circle cy="-40" r="11" fill="#1a1410"/><path d="M-12 -30 L 12 -30 L 10 0 L -10 0 Z" fill="#221a14"/><path d="M-10 -26 L ${-26 + b} -60 M10 -26 L ${26 - b} -62" stroke="#1a1410" stroke-width="6"/></g>`; }
  s += p + `<rect x="-900" y="1460" width="2900" height="1500" fill="#1a0f08"/>`;
  s += [200, 880].map((x, i) => `<path d="M${x} 560 L ${x - 260 + 120 * Math.sin(t + i)} 1460 L ${x + 260 + 120 * Math.sin(t + i)} 1460 Z" fill="rgba(255,240,200,.08)"/>`).join("");
  return s;
}
function carretera(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="url(#cAlba)"/>`;
  s += Array.from({ length: 14 }, (_, i) => { const x = -700 + i * 200 + rnd(i) * 80, h = 400 + rnd(i + 2) * 300;
    return `<path d="M${x} 1250 L ${x + 6} ${1250 - h} M${x + 4} ${1250 - h * 0.6} L ${x + 60} ${1250 - h * 0.8} M${x + 4} ${1250 - h * 0.75} L ${x - 50} ${1250 - h * 0.95}" stroke="#3a3832" stroke-width="${8 + rnd(i) * 6}" fill="none"/>`; }).join("");
  s += `<rect x="-900" y="1250" width="2900" height="1700" fill="#5a5a48"/><path d="M380 1250 L 700 1250 L 1400 2600 L -320 2600 Z" fill="#3a3a38"/>` + Array.from({ length: 6 }, (_, i) => `<rect x="${532 - i * 6}" y="${1290 + i * i * 22}" width="${16 + i * 6}" height="${30 + i * 14}" fill="#c9b85a" opacity=".7"/>`).join("");
  s += `<g transform="translate(820 1380)"><path d="M-200 0 L -180 -70 L -90 -110 L 90 -110 L 160 -60 L 210 -50 L 210 0 Z" fill="#6a2a20"/><path d="M-80 -100 L 80 -100 L 130 -62 L -170 -62 Z" fill="#2a3a44" opacity=".8"/><circle cx="-120" cy="0" r="34" fill="#151515"/><circle cx="130" cy="0" r="34" fill="#151515"/></g>`;
  s += Array.from({ length: 5 }, (_, i) => `<g transform="translate(${((t * 20 + i * 140) % 700) - 100} ${300 + rnd(i) * 200})"><path d="M-12 0 Q -6 -8 0 0 Q 6 -8 12 0" stroke="#1a1a1a" stroke-width="3" fill="none"/></g>`).join("");
  return s + `<ellipse cx="540" cy="1200" rx="900" ry="200" fill="url(#niebla)"/>`;
}
function refugio(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="#1a120c"/><rect x="-900" y="1200" width="2900" height="1700" fill="#2a1a10"/>`;
  s += `<rect x="260" y="300" width="560" height="600" fill="#0a0c10"/>` + [0, 1, 2, 3, 4].map((i) => `<rect x="220" y="${330 + i * 120}" width="640" height="60" fill="#5a3a22" stroke="#2a1a0e" stroke-width="4" transform="rotate(${(i % 2 ? 1 : -1) * 6} 540 ${360 + i * 120})"/>`).join("");
  if (o.manos) s += Array.from({ length: 6 }, (_, i) => `<g transform="translate(${320 + i * 90} ${420 + (i % 2) * 120 + Math.sin(t * 4 + i) * 10})"><path d="M0 0 l -8 -30 M6 0 l 0 -34 M12 0 l 8 -30" stroke="#8e9b7c" stroke-width="7" stroke-linecap="round"/><circle r="12" fill="#8e9b7c"/></g>`).join("");
  s += [150, 930].map((x, i) => `<circle cx="${x}" cy="1080" r="${300 + 20 * Math.sin(t * 8 + i)}" fill="url(#vela)"/><rect x="${x - 10}" y="1080" width="20" height="60" fill="#efe6d0"/><ellipse cx="${x}" cy="${1072 + Math.sin(t * 11 + i) * 2}" rx="7" ry="14" fill="#ffd27a"/>`).join("");
  s += `<rect x="-900" y="1140" width="2900" height="30" fill="#4a2e1a"/>` + restaurante_mesa(540, 1500);
  return s;
}
function restaurante_mesa(x, y) { return `<g transform="translate(${x} ${y})"><ellipse rx="230" ry="40" fill="#6a4426"/><rect x="-14" y="10" width="28" height="200" fill="#3a2414"/></g>`; }
function lago(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="url(#cDorado)"/><circle cx="720" cy="820" r="90" fill="#fff0c8" opacity=".9"/>`;
  s += Array.from({ length: 16 }, (_, i) => `<ellipse cx="${-600 + i * 170}" cy="${980 - rnd(i) * 60}" rx="${120 + rnd(i + 1) * 60}" ry="${160 + rnd(i + 2) * 80}" fill="${["#c8642a", "#a8481e", "#d88a36", "#7a5a2a"][i % 4]}"/>`).join("");
  s += `<rect x="-900" y="1080" width="2900" height="1800" fill="url(#agua)"/>` + Array.from({ length: 30 }, (_, i) => `<line x1="${-600 + rnd(i) * 2200}" y1="${1110 + rnd(i + 4) * 600}" x2="${-540 + rnd(i) * 2200}" y2="${1110 + rnd(i + 4) * 600}" stroke="rgba(255,230,190,${0.15 + 0.15 * Math.sin(t * 2 + i)})" stroke-width="3"/>`).join("");
  if (o.bote !== false) s += `<g transform="translate(${o.boteX ?? 540} ${1500 + Math.sin(t * 1.4) * 6})"><path d="M-260 -30 L 260 -30 Q 220 50 0 60 Q -220 50 -260 -30 Z" fill="#5a3a22" stroke="#2a1a0e" stroke-width="4"/><path d="M-240 -30 L 240 -30" stroke="#8a5a36" stroke-width="8"/></g>`;
  s += [[200, 1300], [880, 1350]].map(([x, y], i) => `<g transform="translate(${x + Math.sin(t * 0.5 + i) * 20} ${y})"><ellipse rx="34" ry="16" fill="#f4f4f0"/><path d="M20 -6 Q 34 -50 18 -60" stroke="#f4f4f0" stroke-width="9" fill="none"/><path d="M18 -60 l 14 4" stroke="#e08a2a" stroke-width="5"/></g>`).join("");
  return s;
}
function residencia(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="#d8c8a8"/><rect x="-900" y="1150" width="2900" height="1700" fill="#7a5a3a"/>`;
  s += `<rect x="560" y="260" width="420" height="620" fill="#fff4d8" stroke="#8a6a4a" stroke-width="16"/><path d="M560 260 L 980 880 M770 260 L 770 880 M560 570 L 980 570" stroke="#8a6a4a" stroke-width="8"/>`;
  s += `<path d="M560 880 L 980 880 L 1300 1900 L 100 1900 Z" fill="rgba(255,240,200,.18)"/>`;
  s += `<g transform="translate(160 720)"><rect x="-30" y="0" width="60" height="140" fill="#5a3a22"/><path d="M-70 0 L 70 0 L 40 -90 L -40 -90 Z" fill="#e8d8b0"/><circle cy="-40" r="120" fill="url(#vela)" opacity=".6"/></g>`;
  return s + [0, 1].map((i) => `<rect x="${-200 + i * 1180}" y="400" width="140" height="180" fill="#6a5a4a" stroke="#4a3a2a" stroke-width="8"/>`).join("");
}
function colina(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="url(#cLaLa)"/>`;
  s += Array.from({ length: 50 }, (_, i) => `<circle cx="${rnd(i) * 2400 - 600}" cy="${rnd(i + 9) * 700 - 200}" r="${1 + rnd(i + 3) * 2}" fill="#fff" opacity="${0.3 + 0.6 * Math.abs(Math.sin(t + i))}"/>`).join("");
  s += `<path d="M-900 1200 Q 0 1080 600 1150 Q 1300 1220 2000 1120 L 2000 1500 L -900 1500 Z" fill="#2a1a40"/>`;
  s += Array.from({ length: 260 }, (_, i) => `<circle cx="${rnd(i + 50) * 2600 - 800}" cy="${1180 + rnd(i + 70) * 260}" r="${1.5 + rnd(i) * 2.5}" fill="${rnd(i + 2) > 0.5 ? "#ffd27a" : "#ffeccc"}" opacity="${0.5 + 0.5 * Math.abs(Math.sin(t * 0.7 + i))}"/>`).join("");
  s += `<path d="M-900 1500 Q 200 1360 900 1440 Q 1400 1500 2000 1460 L 2000 2900 L -900 2900 Z" fill="#1a1428"/><path d="M-200 1700 Q 500 1480 1300 1560" stroke="#3a2a48" stroke-width="80" fill="none"/>`;
  s += `<g transform="translate(${o.farolX ?? 860} 1520)"><rect x="-6" y="-560" width="12" height="560" fill="#14101c"/><path d="M-40 -560 L 40 -560 L 26 -610 L -26 -610 Z" fill="#14101c"/><circle cy="-575" r="200" fill="url(#foco)"/><circle cy="-578" r="16" fill="#fff4d0"/></g>`;
  s += `<g transform="translate(200 1600)"><rect x="-120" y="-60" width="240" height="18" fill="#14101c"/><rect x="-120" y="-110" width="240" height="14" fill="#14101c"/><rect x="-110" y="-60" width="10" height="60" fill="#14101c"/><rect x="100" y="-60" width="10" height="60" fill="#14101c"/></g>`;
  return s;
}
function club(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="#120608"/>`;
  s += Array.from({ length: 18 }, (_, i) => `<path d="M${-700 + i * 160} -400 Q ${-640 + i * 160} 600 ${-700 + i * 160} 1400 L ${-560 + i * 160} 1400 Q ${-620 + i * 160} 600 ${-560 + i * 160} -400 Z" fill="${i % 2 ? "#5a0a14" : "#6e0e1a"}"/>`).join("");
  s += `<rect x="-900" y="1400" width="2900" height="1600" fill="#1a0e0a"/><path d="M-900 1400 L 2000 1400" stroke="#d9b25a" stroke-width="6"/>`;
  s += `<path d="M540 -400 L 200 1400 L 880 1400 Z" fill="rgba(255,230,180,.13)"/><ellipse cx="540" cy="1400" rx="340" ry="40" fill="rgba(255,230,180,.25)"/>`;
  if (o.piano !== false) s += `<g transform="translate(${o.pianoX ?? 820} 1400)"><path d="M-200 -200 L 160 -200 Q 240 -200 240 -120 L 240 -80 L -200 -80 Z" fill="#0a0a0c"/><rect x="-200" y="-80" width="440" height="30" fill="#0a0a0c"/>${Array.from({ length: 22 }, (_, i) => `<rect x="${-196 + i * 20}" y="-80" width="18" height="18" fill="#f4f0e6"/>`).join("")}<rect x="-180" y="-50" width="14" height="50" fill="#0a0a0c"/><rect x="210" y="-50" width="14" height="50" fill="#0a0a0c"/></g>`;
  s += `<text x="540" y="300" text-anchor="middle" font-family="Playfair Display, serif" font-style="italic" font-size="96" fill="#ffcf7a" opacity="${0.85 + 0.15 * Math.sin(t * 9)}">El Club</text>`;
  return s;
}
function neon(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="url(#cNeon)"/>`;
  s += silueta(t, 1500, 1500, "#070a12", 41) + silueta(t, 1700, 1100, "#04060c", 57);
  const letreros = [["TINTO", "#00f0ff", 80, 520], ["ARROZ 24H", "#ff2fa8", 760, 420], ["SIN COMISIÓN", "#ffcf3a", 120, 980], ["EMPANADAS", "#7cff6a", 820, 860], ["DOMICILIOS", "#00f0ff", 420, 1260]];
  s += letreros.map(([txt, c, x, y], i) => { const on = Math.sin(t * (7 + i) + i) > -0.92 ? 1 : 0.25;
    return `<g opacity="${on}"><circle cx="${x + 90}" cy="${y - 20}" r="200" fill="${c === "#ff2fa8" ? "url(#neonM)" : "url(#neonC)"}" opacity=".5"/><text x="${x}" y="${y}" font-family="Figtree" font-weight="900" font-size="54" fill="none" stroke="${c}" stroke-width="3">${txt}</text><text x="${x}" y="${y}" font-family="Figtree" font-weight="900" font-size="54" fill="${c}" opacity=".35">${txt}</text></g>`; }).join("");
  if (o.holograma !== false) s += `<g transform="translate(${o.holoX ?? 540} ${o.holoY ?? 700})" opacity="${0.55 + 0.15 * Math.sin(t * 13)}"><rect x="-220" y="-300" width="440" height="560" fill="rgba(0,200,255,.08)" stroke="rgba(0,220,255,.4)" stroke-width="3"/>
    <g transform="translate(0 -60) scale(.9)"><g transform="translate(-190 -190)">${orbiCara(t, "guino", false)}</g></g><text y="200" text-anchor="middle" font-family="Figtree" font-weight="900" font-size="46" fill="#bff6ff">APEX</text></g>`;
  s += `<g transform="translate(${((t * 140) % 1900) - 400} ${300 + Math.sin(t) * 20})"><path d="M-80 0 Q -60 -30 30 -30 Q 90 -20 100 0 Q 60 16 -70 14 Z" fill="#1a1e28"/><circle cx="90" cy="0" r="8" fill="#ffd27a"/><circle cx="-76" cy="4" r="6" fill="#ff3040"/></g>`;
  return s + `<rect x="-900" y="1700" width="2900" height="1300" fill="#05070c"/><rect x="-900" y="1700" width="2900" height="6" fill="#00f0ff" opacity=".3"/>`;
}
function interrogatorio(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="#0c0a08"/>`;
  s += `<g opacity=".9">${Array.from({ length: 8 }, (_, i) => { const a = t * 1.6 + (i * Math.PI) / 4; return `<path d="M540 -200 L ${540 + Math.cos(a) * 1600} ${1800} L ${540 + Math.cos(a + 0.12) * 1600} 1800 Z" fill="rgba(255,200,120,.06)"/>`; }).join("")}</g>`;
  s += `<rect x="-900" y="1300" width="2900" height="1700" fill="#1a140e"/><rect x="-900" y="1290" width="2900" height="20" fill="#3a2a1a"/>`;
  s += `<g transform="translate(540 1260)"><rect x="-120" y="-130" width="240" height="140" rx="10" fill="#2a2620"/><rect x="-90" y="-110" width="180" height="90" rx="6" fill="#0a1a18"/>
    <g transform="translate(0 -66)"><ellipse rx="56" ry="30" fill="#f2efe6"/><circle r="22" fill="#4a6a5a"/><circle r="10" fill="#050505"/><circle cx="6" cy="-6" r="4" fill="#fff"/><path d="M-60 0 Q 0 ${-40 * Math.abs(Math.sin(t * 0.8))} 60 0" stroke="#0a1a18" stroke-width="10" fill="none"/></g>
    ${Array.from({ length: 10 }, (_, i) => `<rect x="${-100 + i * 20}" y="-8" width="12" height="${4 + Math.abs(Math.sin(t * 6 + i)) * 10}" fill="#3aff9a" opacity=".7"/>`).join("")}</g>`;
  return s + Array.from({ length: 4 }, (_, i) => `<ellipse cx="${300 + i * 160 + Math.sin(t * 0.4 + i) * 60}" cy="${500 - ((t * 25 + i * 90) % 400)}" rx="${120 + i * 20}" ry="40" fill="rgba(220,210,200,.06)"/>`).join("");
}
function oficina(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="#f2ede4"/><rect x="-900" y="1300" width="2900" height="1700" fill="#c9b8a0"/>`;
  s += `<rect x="-200" y="200" width="760" height="760" fill="url(#cOficina)" stroke="#9a8a7a" stroke-width="14"/>` + silueta(t, 960, 520, "#9ab0c4", 71).replace(/<rect/g, '<rect opacity=".55"').slice(0, 4000);
  s += `<rect x="-200" y="200" width="760" height="760" fill="none" stroke="#9a8a7a" stroke-width="14"/><line x1="180" y1="200" x2="180" y2="960" stroke="#9a8a7a" stroke-width="10"/>`;
  const dias = o.dias ?? 0;
  s += `<g transform="translate(820 520)"><rect x="-190" y="-230" width="380" height="440" fill="#fff" stroke="#c0392b" stroke-width="6"/><rect x="-190" y="-230" width="380" height="70" fill="#c0392b"/>
    <text y="-182" text-anchor="middle" font-family="Playfair Display, serif" font-size="40" fill="#fff">10 DÍAS</text>
    ${Array.from({ length: 10 }, (_, i) => `<g transform="translate(${-130 + (i % 4) * 88} ${-110 + Math.floor(i / 4) * 110})"><text text-anchor="middle" y="12" font-family="Figtree" font-weight="800" font-size="40" fill="#333">${i + 1}</text>
      ${i < dias ? `<path d="M-30 -30 L 30 30 M30 -30 L -30 30" stroke="#c0392b" stroke-width="7"/>` : ""}</g>`).join("")}</g>`;
  s += `<rect x="-900" y="1280" width="2900" height="40" fill="#8a6a4a"/><g transform="translate(540 1280)"><rect x="-360" y="0" width="720" height="40" fill="#5a3a22"/></g>`;
  return s;
}
Object.assign(FONDOS, { ruinas, muro, carretera, refugio, lago, residencia, colina, club, neon, interrogatorio, oficina });
const GRADOS_EXTRA = {
  apocalipsis: "contrast(1.25) saturate(.7) sepia(.25) brightness(.92)",
  caminantes: "contrast(1.2) saturate(.45) brightness(.88)",
  nostalgia: "sepia(.35) contrast(1.05) saturate(1.1) brightness(1.02)",
  lalaland: "contrast(1.08) saturate(1.3)",
  neon: "contrast(1.25) saturate(1.35) brightness(.92)",
  romcom: "contrast(1.02) saturate(1.15) brightness(1.06)",
  audaz: "contrast(1.18) saturate(.82) brightness(.93)",
};
// Actores nuevos para el motor de «heroes»
function dibujaExtra(a, st, t, h, b) {
  if (a.tipo !== "humano") return "";
  return humano({ ...st.props, cara: st.cara ?? st.props.cara, caraOrbi: st.cara, boca: b, t, paso: st.props.camina ? t * 7 : st.props.paso });
}
