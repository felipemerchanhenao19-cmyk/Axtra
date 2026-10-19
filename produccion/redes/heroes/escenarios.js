// Escenarios de «Orbi: universo de héroes». Coordenadas del mundo: cuadro de 1080 x 1920 (la cámara se mueve encima).
const rnd = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const ESC_DEFS = `<defs>
  <linearGradient id="cieloNoche" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#03050d"/><stop offset=".5" stop-color="#0b1730"/><stop offset="1" stop-color="#1f2c52"/></linearGradient>
  <linearGradient id="cieloTormenta" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05060a"/><stop offset=".6" stop-color="#151b2b"/><stop offset="1" stop-color="#2b3248"/></linearGradient>
  <radialGradient id="lunaH"><stop offset="0" stop-color="#fffbe8"/><stop offset=".1" stop-color="#fff3cc"/><stop offset=".3" stop-color="rgba(255,240,200,.18)"/><stop offset="1" stop-color="rgba(255,240,200,0)"/></radialGradient>
  <radialGradient id="nubeH"><stop offset="0" stop-color="rgba(110,125,170,.4)"/><stop offset="1" stop-color="rgba(110,125,170,0)"/></radialGradient>
  <radialGradient id="farol"><stop offset="0" stop-color="rgba(255,200,120,.6)"/><stop offset="1" stop-color="rgba(255,200,120,0)"/></radialGradient>
  <radialGradient id="neonRosa"><stop offset="0" stop-color="rgba(255,60,160,.55)"/><stop offset="1" stop-color="rgba(255,60,160,0)"/></radialGradient>
  <linearGradient id="haz" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="rgba(255,240,190,.55)"/><stop offset="1" stop-color="rgba(255,240,190,.05)"/></linearGradient>
  <linearGradient id="ladrillo" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a1612"/><stop offset=".5" stop-color="#4a2a20"/><stop offset="1" stop-color="#2a1612"/></linearGradient>
  <linearGradient id="charco" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="rgba(255,80,170,.35)"/><stop offset="1" stop-color="rgba(255,80,170,0)"/></linearGradient>
</defs>`;
const _edif = {};
function edificios(t, capa, base, alto, color, luces, semilla) {
  const clave = [base, alto, color, luces, semilla].join(); if (_edif[clave]) return _edif[clave];
  let s = "", x = -700;
  for (let i = 0; x < 1800; i++) {
    const w = 90 + rnd(semilla + i) * 150, h = alto * (0.45 + rnd(semilla + i * 3) * 0.55), y = base - h;
    s += `<rect x="${x}" y="${y}" width="${w}" height="${h + 900}" fill="${color}"/>`;
    if (rnd(semilla + i * 7) > 0.6) s += `<rect x="${x + w / 2 - 3}" y="${y - 60}" width="6" height="60" fill="${color}"/><circle cx="${x + w / 2}" cy="${y - 62}" r="5" fill="#ff4040" opacity=".8"/>`;
    for (let r = 0; r < h / 34 - 1; r++) for (let c = 0; c < w / 26 - 1; c++) if (rnd(semilla * 13 + i * 97 + r * 7 + c) < luces)
      s += `<rect x="${x + 12 + c * 26}" y="${y + 16 + r * 34}" width="12" height="16" fill="${rnd(i + r + c) > 0.3 ? "#f6cf7a" : "#9ad7ff"}" opacity="${0.55 + 0.4 * rnd(i * r + c)}"/>`;
    x += w + 6;
  }
  return (_edif[clave] = s);
}
function ciudad(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="url(${o.tormenta ? "#cieloTormenta" : "#cieloNoche"})"/>`;
  if (!o.tormenta) s += `<circle cx="${o.lunaX ?? 800}" cy="${o.lunaY ?? 300}" r="420" fill="url(#lunaH)"/><circle cx="${o.lunaX ?? 800}" cy="${o.lunaY ?? 300}" r="70" fill="#fff6dc"/>`;
  s += Array.from({ length: 9 }, (_, i) => `<ellipse cx="${((rnd(i) * 2400 + t * (12 + i * 3)) % 2600) - 800}" cy="${120 + rnd(i + 9) * 600}" rx="${300 + rnd(i + 2) * 300}" ry="${50 + rnd(i + 4) * 60}" fill="url(#nubeH)"/>`).join("");
  if (o.senal) s += senal(t, o.senal);
  s += edificios(t, 0, 1250, 700, "#0c1426", 0.18, 3) + edificios(t, 1, 1450, 650, "#0a0f1c", 0.24, 11) + edificios(t, 2, 1700, 600, "#05080f", 0.3, 23);
  s += `<rect x="-900" y="1700" width="2900" height="1200" fill="#040609"/>`;
  return s;
}
// Señal en el cielo: un haz de luz desde un reflector hasta las nubes con el símbolo de Orbi (un QR con la O)
function senal(t, o = {}) {
  const k = o.k ?? 1, x0 = o.x0 ?? 300, y0 = o.y0 ?? 1500, x1 = o.x ?? 640, y1 = o.y ?? 380;
  const qr = Array.from({ length: 49 }, (_, i) => rnd(i + 3) > 0.5 && ![0, 1, 7, 8, 5, 6, 12, 13, 35, 36, 42, 43].includes(i) ? `<rect x="${-70 + (i % 7) * 20}" y="${-70 + Math.floor(i / 7) * 20}" width="18" height="18"/>` : "").join("");
  return `<g opacity="${k}"><path d="M${x0 - 30} ${y0} L ${x1 - 230} ${y1} L ${x1 + 230} ${y1} L ${x0 + 30} ${y0} Z" fill="url(#haz)"/>
    <ellipse cx="${x1}" cy="${y1}" rx="250" ry="120" fill="rgba(255,240,190,.55)"/>
    <g transform="translate(${x1} ${y1}) scale(1 .5)" fill="#0a0f1c" opacity=".85"><circle r="98" fill="none" stroke="#0a0f1c" stroke-width="20"/>${qr}
      ${[[-70, -70], [50, -70], [-70, 50]].map(([x, y]) => `<rect x="${x}" y="${y}" width="40" height="40" fill="none" stroke="#0a0f1c" stroke-width="8"/>`).join("")}</g></g>`;
}
function azotea(t, o = {}) {
  let s = `<g transform="translate(540 700) scale(.8) translate(-540 -700)">${ciudad(t, o)}</g>`;
  s += `<rect x="-900" y="1380" width="2900" height="1500" fill="#11141c"/><rect x="-900" y="1360" width="2900" height="40" fill="#272c38"/>
    ${Array.from({ length: 30 }, (_, i) => `<rect x="${-900 + i * 100}" y="1362" width="4" height="36" fill="#11141c"/>`).join("")}
    <g transform="translate(${o.tanque ?? 120} 1360)"><rect x="-90" y="-300" width="180" height="230" rx="20" fill="#1a1f2a"/><path d="M-100 -300 L 0 -360 L 100 -300 Z" fill="#141822"/>${[-70, 70].map((x) => `<rect x="${x - 6}" y="-80" width="12" height="80" fill="#141822"/>`).join("")}</g>
    <g transform="translate(${o.gargola ?? 760} 1360)"><path d="M-80 0 L -60 -90 Q -30 -150 30 -140 L 60 -180 L 70 -120 Q 100 -90 80 0 Z" fill="#232836"/><circle cx="20" cy="-120" r="6" fill="#ff5050" opacity=".7"/></g>`;
  if (o.reflector) s += `<g transform="translate(${o.reflector[0]} ${o.reflector[1]})"><rect x="-26" y="0" width="52" height="80" fill="#2b2f38"/><ellipse cx="0" cy="-10" rx="60" ry="44" fill="#3a3f4a" transform="rotate(-30)"/><ellipse cx="18" cy="-26" rx="44" ry="30" fill="#fff6d0" opacity="${o.reflectorK ?? 1}" transform="rotate(-30 18 -26)"/></g>`;
  return s;
}
function restauranteH(t, o = {}) {
  const luz = o.luz ?? 1;
  let s = restaurante(t, luz);
  if (o.ventanaRota) s += `<rect x="620" y="300" width="360" height="230" fill="#000" opacity=".6"/>` + Array.from({ length: 8 }, (_, i) => `<path d="M${620 + rnd(i) * 360} 300 L ${640 + rnd(i + 3) * 320} ${330 + rnd(i + 5) * 180} L ${620 + rnd(i + 7) * 360} 530" stroke="rgba(200,230,255,.7)" stroke-width="3" fill="none"/>`).join("");
  (o.mesas || []).forEach(([x, y, gente], i) => {
    if (gente) s += `<g transform="translate(${x - 120} ${y - 30}) scale(.8)">${persona({ piel: PIELES[i % 5], camisa: ["#3d6fb6", "#c0392b", "#2a9d8f", "#8e44ad", "#e67e22"][i % 5], pelo: ["corto", "largo", "moño", "calvo"][i % 4], brazo: o.manos ? 1 : -1, boca: 0.4 })}</g>`
      + `<g transform="translate(${x + 120} ${y - 30}) scale(.8)">${persona({ piel: PIELES[(i + 2) % 5], camisa: ["#e67e22", "#2a9d8f", "#3d6fb6", "#c0392b"][i % 4], pelo: ["largo", "corto", "calvo", "moño"][i % 4], boca: 0.4 })}</g>`;
    s += mesa(x, y, 0.9);
  });
  return s;
}
function callejon(t, o = {}) {
  const neon = Math.sin(t * 17) > 0.92 ? 0.3 : 1;
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="#07080d"/>`;
  s += `<path d="M-900 -900 L 300 300 L 300 1500 L -900 2600 Z" fill="url(#ladrillo)"/><path d="M1980 -900 L 780 300 L 780 1500 L 1980 2600 Z" fill="url(#ladrillo)"/>`;
  for (let r = 0; r < 40; r++) s += `<path d="M-900 ${-900 + r * 90} L 300 ${300 + r * 30}" stroke="rgba(0,0,0,.35)" stroke-width="4"/><path d="M1980 ${-900 + r * 90} L 780 ${300 + r * 30}" stroke="rgba(0,0,0,.35)" stroke-width="4"/>`;
  s += `<rect x="300" y="300" width="480" height="1200" fill="#0d1018"/><circle cx="540" cy="700" r="260" fill="url(#farol)" opacity=".5"/>`;
  s += `<path d="M-900 2600 L 300 1500 L 780 1500 L 1980 2600 Z" fill="#0b0d12"/><ellipse cx="560" cy="1760" rx="300" ry="40" fill="url(#charco)" opacity="${neon}"/><ellipse cx="380" cy="1900" rx="200" ry="26" fill="url(#charco)" opacity="${neon * 0.7}"/>`;
  s += `<g transform="translate(870 620) rotate(8)" opacity="${neon}"><circle r="320" fill="url(#neonRosa)"/><rect x="-170" y="-50" width="340" height="100" rx="20" fill="none" stroke="#ff4fb0" stroke-width="8"/><text y="18" text-anchor="middle" font-size="52" font-weight="900" fill="#ffb3e0" font-family="Figtree">DOMICILIOS</text></g>`;
  s += `<g transform="translate(140 1560)"><rect x="-150" y="-160" width="300" height="160" rx="10" fill="#1f3a2a"/><rect x="-160" y="-180" width="320" height="30" rx="6" fill="#16291e"/></g>`;
  s += Array.from({ length: 4 }, (_, i) => `<ellipse cx="${200 + i * 60 + 20 * Math.sin(t + i)}" cy="${1300 - ((t * 60 + i * 120) % 500)}" rx="${60 + i * 10}" ry="${30 + i * 6}" fill="rgba(200,200,220,${0.05 + 0.02 * i})"/>`).join("");
  return s;
}
function taller(t, o = {}) {
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="#04070d"/><rect x="-900" y="1350" width="2900" height="1500" fill="#0a0e16"/>`;
  s += Array.from({ length: 14 }, (_, i) => `<line x1="${-600 + i * 180}" y1="1350" x2="${540 + (i - 7) * 600}" y2="2600" stroke="rgba(80,200,255,.12)" stroke-width="3"/>`).join("");
  s += `<ellipse cx="540" cy="1360" rx="300" ry="50" fill="none" stroke="rgba(80,220,255,.7)" stroke-width="6"/><ellipse cx="540" cy="1360" rx="250" ry="38" fill="rgba(80,220,255,.12)"/>`;
  s += [[150, 500], [930, 560], [200, 900], [900, 980]].map(([x, y], i) => `<g transform="translate(${x} ${y})" opacity="${0.6 + 0.3 * Math.sin(t * 2 + i)}"><rect x="-120" y="-80" width="240" height="160" rx="10" fill="rgba(60,200,255,.08)" stroke="rgba(120,230,255,.6)" stroke-width="3"/>
    ${Array.from({ length: 5 }, (_, k) => `<rect x="-100" y="${-60 + k * 26}" width="${60 + rnd(i * 5 + k) * 140}" height="10" fill="rgba(160,240,255,.5)"/>`).join("")}</g>`).join("");
  return s;
}
function negro(t, o = {}) { return `<rect x="-900" y="-900" width="2900" height="3800" fill="${o.color || "#000"}"/>`; }
const FONDOS = { ciudad, azotea, restaurante: restauranteH, callejon, taller, negro };
