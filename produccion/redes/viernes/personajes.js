// Personajes y escenario de «Viernes, 8 p. m.» en SVG plano (estilo ilustración).
const PIELES = ["#f2c9a0", "#d9a273", "#a8714a", "#7a4b2e", "#f6d5b5"];
// Persona sentada o de pie. o = {piel, pelo, colorPelo, camisa, boca, cejas, brazo (-1 abajo, 0 mesa, 1 arriba), mira}
function persona(o = {}) {
  const piel = o.piel || PIELES[0], pelo = o.colorPelo || "#2b1d14", cam = o.camisa || "#3d6fb6";
  const brazoArriba = o.brazo === 1, boca = o.boca ?? 0.4, mx = o.mira || 0;
  const cabello = { corto: `<path d="M-46 -150 Q -48 -205 0 -208 Q 48 -205 46 -150 Q 30 -178 0 -176 Q -30 -178 -46 -150Z" fill="${pelo}"/>`,
    largo: `<path d="M-52 -140 Q -60 -212 0 -212 Q 60 -212 52 -140 L 58 -80 Q 40 -100 40 -150 Q 0 -190 -40 -150 Q -40 -100 -58 -80Z" fill="${pelo}"/>`,
    calvo: `<path d="M-44 -158 Q -46 -170 -38 -176" stroke="${pelo}" stroke-width="8" fill="none"/>`,
    moño: `<circle cx="0" cy="-212" r="22" fill="${pelo}"/><path d="M-48 -146 Q -50 -206 0 -206 Q 50 -206 48 -146 Q 20 -172 -48 -146Z" fill="${pelo}"/>` }[o.pelo || "corto"];
  const brazo = brazoArriba
    ? `<path d="M50 -40 Q 92 -110 84 -190" stroke="${cam}" stroke-width="34" stroke-linecap="round" fill="none"/><circle cx="84" cy="-200" r="20" fill="${piel}"/>`
    : `<path d="M50 -40 Q 76 10 50 52" stroke="${cam}" stroke-width="34" stroke-linecap="round" fill="none"/>`;
  const cejas = o.cejas === "arriba" ? -8 : o.cejas === "enojo" ? 4 : 0, ang = o.cejas === "enojo" ? 14 : o.cejas === "triste" ? -14 : 0;
  return `<g>
    <path d="M-70 60 Q -72 -50 0 -62 Q 72 -50 70 60 Z" fill="${cam}"/>
    <rect x="-14" y="-92" width="28" height="34" rx="10" fill="${piel}"/>
    ${brazo}<path d="M-50 -40 Q -76 10 -50 52" stroke="${cam}" stroke-width="34" stroke-linecap="round" fill="none"/>
    <ellipse cx="0" cy="-140" rx="50" ry="58" fill="${piel}"/>
    ${cabello}
    <circle cx="${-18 + mx}" cy="-140" r="6" fill="#1b1b1b"/><circle cx="${18 + mx}" cy="-140" r="6" fill="#1b1b1b"/>
    <path d="M-28 ${-158 + cejas} L -8 ${-160 + cejas}" transform="rotate(${ang} -18 -159)" stroke="${pelo}" stroke-width="6" stroke-linecap="round"/>
    <path d="M8 ${-160 + cejas} L 28 ${-158 + cejas}" transform="rotate(${-ang} 18 -159)" stroke="${pelo}" stroke-width="6" stroke-linecap="round"/>
    ${boca > 0.75 ? `<ellipse cx="0" cy="-110" rx="13" ry="${10 * boca}" fill="#5a1a1a"/>` : `<path d="M-16 -112 Q 0 ${-112 + 22 * (boca - 0.4)} 16 -112" stroke="#5a1a1a" stroke-width="5" fill="none" stroke-linecap="round"/>`}
  </g>`;
}
// Julián, el mesero: chaleco negro, camisa blanca, corbatín (como Orbi), bandeja.
function julian(o = {}) {
  const sudor = o.sudor ? `<path d="M52 -170 q 8 14 0 22 q -8 -8 0 -22Z" fill="#7fd7ff"/><path d="M-60 -150 q 7 12 0 19 q -7 -7 0 -19Z" fill="#7fd7ff"/>` : "";
  const ojos = o.ojos === "grandes" ? `<circle cx="-18" cy="-140" r="11" fill="#fff"/><circle cx="18" cy="-140" r="11" fill="#fff"/><circle cx="-18" cy="-140" r="5" fill="#111"/><circle cx="18" cy="-140" r="5" fill="#111"/>`
    : o.ojos === "cerrados" ? `<path d="M-26 -140 q 8 6 16 0 M10 -140 q 8 6 16 0" stroke="#111" stroke-width="5" fill="none"/>`
    : `<circle cx="-18" cy="-140" r="6" fill="#111"/><circle cx="18" cy="-140" r="6" fill="#111"/>`;
  const bocaJ = o.boca === "o" ? `<ellipse cx="0" cy="-108" rx="10" ry="14" fill="#5a1a1a"/>` : o.boca === "triste" ? `<path d="M-16 -104 Q 0 -118 16 -104" stroke="#5a1a1a" stroke-width="5" fill="none"/>`
    : `<path d="M-18 -114 Q 0 -96 18 -114" stroke="#5a1a1a" stroke-width="5" fill="none"/>`;
  const bandeja = o.bandeja ? `<g transform="translate(96 -150) rotate(${o.inclina || 0})"><ellipse cx="0" cy="0" rx="80" ry="14" fill="#c9ced6" stroke="#8b939e" stroke-width="3"/>
      ${(o.platos || 3) > 0 ? Array.from({ length: o.platos || 3 }, (_, i) => `<ellipse cx="${-46 + i * 46}" cy="-10" rx="22" ry="8" fill="#fff"/><circle cx="${-46 + i * 46}" cy="-18" r="12" fill="${["#c9572e", "#e8b33a", "#6aa84f"][i % 3]}"/>`).join("") : ""}</g>` : "";
  return `<g>
    <rect x="-46" y="40" width="34" height="150" rx="14" fill="#1d2430"/><rect x="12" y="40" width="34" height="150" rx="14" fill="#1d2430"/>
    <path d="M-72 70 Q -76 -50 0 -64 Q 76 -50 72 70 Z" fill="#f4f6f8"/>
    <path d="M-72 70 Q -76 -50 -20 -60 L -8 70 Z M72 70 Q 76 -50 20 -60 L 8 70 Z" fill="#1d2430"/>
    <rect x="-60" y="30" width="120" height="110" rx="10" fill="#efe9dd"/>
    <path d="M-52 -40 Q -86 0 -64 60" stroke="#f4f6f8" stroke-width="32" stroke-linecap="round" fill="none"/>
    <path d="M52 -40 Q 92 -90 92 -140" stroke="#f4f6f8" stroke-width="32" stroke-linecap="round" fill="none"/><circle cx="92" cy="-146" r="18" fill="#d9a273"/>
    <rect x="-14" y="-92" width="28" height="34" rx="10" fill="#d9a273"/>
    <g transform="translate(0 -62)"><path d="M0 0 L-24 -11 L-24 11Z M0 0 L24 -11 L24 11Z" fill="#1d2430"/><circle r="6" fill="#2fbbe8"/></g>
    <ellipse cx="0" cy="-140" rx="50" ry="58" fill="#d9a273"/>
    <path d="M-50 -150 Q -52 -210 0 -212 Q 52 -210 50 -150 Q 40 -186 6 -180 Q -30 -190 -50 -150Z" fill="#1a1410"/>
    ${ojos}${bocaJ}${sudor}${bandeja}
  </g>`;
}
// Don Papel, la libreta de toda la vida: espiral, bigote, ceño, lápiz en la oreja.
function donPapel(o = {}) {
  const enojo = o.cara === "enojo", hab = o.boca ?? 0.2;
  return `<g>
    <rect x="-90" y="-130" width="180" height="240" rx="14" fill="#fbf6e6" stroke="#c9bd98" stroke-width="5"/>
    ${[-60, -36, -12, 12, 36, 60].map((x) => `<circle cx="${x}" cy="-130" r="10" fill="none" stroke="#7d7d7d" stroke-width="6"/>`).join("")}
    ${[-70, -45, -20, 40, 65, 90].map((y) => `<line x1="-70" y1="${y}" x2="70" y2="${y}" stroke="#a9c7e8" stroke-width="3"/>`).join("")}
    <path d="M-52 -78 L -14 ${enojo ? -66 : -82}" stroke="#4a3b2a" stroke-width="9" stroke-linecap="round"/><path d="M14 ${enojo ? -66 : -82} L 52 -78" stroke="#4a3b2a" stroke-width="9" stroke-linecap="round"/>
    <circle cx="-32" cy="-50" r="9" fill="#222"/><circle cx="32" cy="-50" r="9" fill="#222"/>
    <circle cx="32" cy="-50" r="22" fill="none" stroke="#b08d3c" stroke-width="4"/><path d="M54 -48 Q 70 -20 64 10" stroke="#b08d3c" stroke-width="3" fill="none"/>
    <path d="M-50 -12 Q -26 -30 0 -16 Q 26 -30 50 -12 Q 30 -2 0 -10 Q -30 -2 -50 -12Z" fill="#4a3b2a"/>
    <ellipse cx="0" cy="8" rx="${16}" ry="${4 + 14 * hab}" fill="#5a1a1a"/>
    <g transform="translate(96 -120) rotate(30)"><rect x="-8" y="-60" width="16" height="110" fill="#f2c230"/><path d="M-8 50 L 0 70 L 8 50Z" fill="#e9c9a0"/><rect x="-8" y="-72" width="16" height="14" fill="#e88"/></g>
  </g>`;
}
function mesa(x, y, esc = 1) {
  return `<g transform="translate(${x} ${y}) scale(${esc})"><ellipse cx="0" cy="34" rx="150" ry="22" fill="rgba(0,0,0,.35)"/>
    <rect x="-140" y="-14" width="280" height="36" rx="18" fill="#8a5a36"/><ellipse cx="0" cy="-14" rx="140" ry="22" fill="#a8703f"/>
    <rect x="-12" y="20" width="24" height="70" fill="#5c3a22"/><g transform="translate(70 -26)"><rect x="-16" y="-34" width="32" height="40" rx="5" fill="#e9eef4"/><rect x="-10" y="-28" width="20" height="20" fill="#0b1626"/></g></g>`;
}
function restaurante(t, luz = 1) {
  const lamparas = [200, 540, 880].map((x, i) => `<line x1="${x}" y1="0" x2="${x}" y2="${210 + i % 2 * 30}" stroke="#2a1d14" stroke-width="4"/>
     <path d="M${x - 60} ${210 + i % 2 * 30} L ${x + 60} ${210 + i % 2 * 30} L ${x + 34} ${170 + i % 2 * 30} L ${x - 34} ${170 + i % 2 * 30}Z" fill="#c98a3a"/>
     <circle cx="${x}" cy="${238 + i % 2 * 30}" r="${150 * luz}" fill="url(#calido)" opacity="${0.9 * luz}"/>`).join("");
  return `<defs><radialGradient id="calido"><stop offset="0" stop-color="rgba(255,205,130,.55)"/><stop offset="1" stop-color="rgba(255,205,130,0)"/></radialGradient>
     <linearGradient id="pared" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b2418"/><stop offset="1" stop-color="#5a3622"/></linearGradient></defs>
    <rect x="0" y="0" width="1080" height="1100" fill="url(#pared)"/>
    ${Array.from({ length: 12 }, (_, i) => `<rect x="${i * 92}" y="560" width="86" height="540" fill="rgba(0,0,0,.12)"/>`).join("")}
    <rect x="620" y="300" width="360" height="230" rx="10" fill="#0d1a2e" stroke="#2a1d14" stroke-width="12"/>
    ${Array.from({ length: 14 }, (_, i) => `<rect x="${640 + (i * 53) % 320}" y="${380 + (i * 37) % 120}" width="10" height="${40 + (i * 13) % 60}" fill="#f1c76a" opacity=".6"/>`).join("")}
    <text x="300" y="420" fill="#f1c76a" font-size="64" font-family="Italiana, serif" opacity=".9">La Fonda</text>
    <rect x="0" y="1100" width="1080" height="820" fill="#6b4226"/>${Array.from({ length: 9 }, (_, i) => `<line x1="0" y1="${1150 + i * 90}" x2="1080" y2="${1150 + i * 90}" stroke="rgba(0,0,0,.18)" stroke-width="4"/>`).join("")}
    ${lamparas}`;
}
