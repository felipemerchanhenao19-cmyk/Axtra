// Vestuario y utilería de «Expediente 27»: Orbi detective, Don Aurelio, Comi en gabardina y los objetos de la oficina.
// Orbi detective: gabardina detrás, Orbi (svg de 380) en el centro, solapas y sombrero encima. sombrero = grados que levanta el ala (saludo).
function detective(svgOrbi, o = {}) {
  const lev = o.sombrero || 0;
  return `<g>
    <path d="M-150 250 Q -190 120 -96 78 L 96 78 Q 190 120 150 250 Q 0 285 -150 250Z" fill="#6f5a3d"/>
    <path d="M-150 250 Q -190 120 -96 78 L -40 78 L -60 260Z" fill="#5d4a31"/>
    <rect x="-150" y="196" width="300" height="22" rx="6" fill="#4a3a26"/><rect x="-18" y="192" width="36" height="30" rx="4" fill="none" stroke="#c9a65a" stroke-width="5"/>
    <circle cx="-30" cy="160" r="7" fill="#3a2d1d"/><circle cx="30" cy="160" r="7" fill="#3a2d1d"/>
    <g transform="translate(-190 -190)">${svgOrbi}</g>
    <path d="M-104 84 L -46 112 L -70 176 L -122 120Z" fill="#87704d" stroke="#5d4a31" stroke-width="4"/>
    <path d="M104 84 L 46 112 L 70 176 L 122 120Z" fill="#87704d" stroke="#5d4a31" stroke-width="4"/>
    <g transform="rotate(${-8 - lev} -150 -92) translate(0 ${-lev * 1.6})">
      <ellipse cx="0" cy="-60" rx="120" ry="20" fill="rgba(0,0,0,.35)"/>
      <ellipse cx="0" cy="-92" rx="168" ry="30" fill="#24232a"/>
      <path d="M-104 -96 Q -100 -172 -70 -186 Q -30 -168 0 -184 Q 30 -168 70 -186 Q 100 -172 104 -96Z" fill="#2f2e36"/>
      <path d="M-70 -186 Q -30 -168 0 -184 Q 30 -168 70 -186" fill="none" stroke="#17161b" stroke-width="5"/>
      <path d="M-104 -96 Q 0 -80 104 -96 L 103 -122 Q 0 -108 -103 -122Z" fill="#5a1a22"/>
      <path d="M-160 -96 Q -60 -112 0 -110" fill="none" stroke="rgba(255,255,255,.12)" stroke-width="4"/>
    </g>
  </g>`;
}
// Objetos que flotan junto a Orbi (no tiene manos): brillo cian de «telequinesis».
function lupa(r = 70) {
  return `<g><circle r="${r + 16}" fill="rgba(47,187,232,.12)"/><circle r="${r}" fill="rgba(190,230,255,.12)" stroke="#c9a65a" stroke-width="12"/>
    <path d="M${r * 0.71 + 6} ${r * 0.71 + 6} L ${r * 1.7} ${r * 1.7}" stroke="#3a2414" stroke-width="22" stroke-linecap="round"/>
    <path d="M${-r * 0.5} ${-r * 0.55} Q ${-r * 0.2} ${-r * 0.8} ${r * 0.15} ${-r * 0.75}" stroke="rgba(255,255,255,.5)" stroke-width="7" fill="none" stroke-linecap="round"/></g>`;
}
function linterna() {
  return `<g><rect x="-60" y="-18" width="110" height="36" rx="10" fill="#3a3d45"/><path d="M50 -26 L 80 -34 L 80 34 L 50 26Z" fill="#555a64"/>
    <ellipse cx="80" cy="0" rx="8" ry="32" fill="#fff6c8"/><rect x="-30" y="-24" width="16" height="10" rx="3" fill="#c9a65a"/></g>`;
}
// Don Aurelio: dueño del asadero El Fogón. Bigote, delantal, sombrero vueltiao en las manos (o puesto), mojado por la lluvia.
function aurelio(o = {}) {
  const p = persona({ piel: "#c68a5c", pelo: "calvo", colorPelo: "#2e231c", camisa: "#e9e2d0", boca: o.boca ?? 0.3, cejas: o.cejas ?? "triste", brazo: 0, mira: o.mira || 0 });
  const vueltiao = (x, y, s, rot = 0) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">
      <ellipse rx="110" ry="28" fill="#f1e6c8"/>${[96, 80, 64].map((r, i) => `<ellipse rx="${r}" ry="${r * 0.25}" fill="none" stroke="${i % 2 ? "#f1e6c8" : "#1d1a16"}" stroke-width="7"/>`).join("")}
      <path d="M-56 -4 Q -54 -66 0 -70 Q 54 -66 56 -4Z" fill="#f1e6c8"/>${[-46, -22, -2].map((y) => `<path d="M-54 ${y} Q 0 ${y - 10} 54 ${y}" stroke="#1d1a16" stroke-width="6" fill="none"/>`).join("")}</g>`;
  const gotas = o.mojado ? [[-60, -60], [52, -40], [-20, -10], [64, 20], [-48, 30]].map(([x, y]) => `<path d="M${x} ${y} q 6 10 0 16 q -6 -6 0 -16Z" fill="#a9d6ff" opacity=".8"/>`).join("") : "";
  return `<g>${p}
    <path d="M-44 -48 L 44 -48 L 54 62 L -54 62Z" fill="#6e1f1f"/><text x="0" y="22" text-anchor="middle" font-size="18" font-weight="800" fill="#f1c76a" font-family="Figtree">EL FOGÓN</text>
    <path d="M-30 -48 L -36 -74 M30 -48 L 36 -74" stroke="#6e1f1f" stroke-width="7"/>
    <path d="M-30 -120 Q -16 -132 0 -122 Q 16 -132 30 -120 Q 20 -110 0 -116 Q -20 -110 -30 -120Z" fill="#2e231c"/>
    ${o.puesto ? vueltiao(0, -196, 0.72, -4) : vueltiao(0, 10, 0.85, -6)}${gotas}</g>`;
}
// Comi de cine negro: gabardina con cuello alzado, gafas oscuras y maletín del 27 %.
function comiNoir(o = {}) {
  const base = comi({ cara: o.cara || "enojo", boca: o.boca || 0, brazoArriba: o.brazoArriba });
  const maletin = o.maletin === false ? "" : o.abierto
    ? `<g transform="translate(225 110)"><rect x="-80" y="-10" width="160" height="90" rx="10" fill="#4a2a14"/><path d="M-80 -10 L -70 -90 L 90 -80 L 80 -10Z" fill="#5c3418"/>${billetes(3, 180, 0)}</g>`
    : `<g transform="translate(225 110)"><rect x="-80" y="-50" width="160" height="110" rx="12" fill="#5c3418" stroke="#3a2010" stroke-width="5"/>
       <rect x="-24" y="-74" width="48" height="26" rx="8" fill="none" stroke="#3a2010" stroke-width="9"/><rect x="-80" y="-6" width="160" height="10" fill="#3a2010"/>
       <rect x="-46" y="14" width="92" height="34" rx="6" fill="#c9a65a"/><text x="0" y="40" text-anchor="middle" font-size="26" font-weight="800" fill="#3a2010" font-family="Figtree">27 %</text></g>`;
  const gafas = o.gafas === false ? "" : `<g><rect x="-108" y="-50" width="94" height="58" rx="22" fill="#0c0a10"/><rect x="14" y="-50" width="94" height="58" rx="22" fill="#0c0a10"/>
      <path d="M-14 -30 Q 0 -40 14 -30" stroke="#0c0a10" stroke-width="9" fill="none"/><path d="M-92 -38 L -60 -38" stroke="rgba(255,255,255,.55)" stroke-width="6" stroke-linecap="round"/><path d="M30 -38 L 62 -38" stroke="rgba(255,255,255,.55)" stroke-width="6" stroke-linecap="round"/></g>`;
  return `<g>${base}
    <path d="M-175 190 L -178 -110 Q -176 -160 -128 -168 L -96 -100 L -110 190Z" fill="#3b3346"/><path d="M175 190 L 178 -110 Q 176 -160 128 -168 L 96 -100 L 110 190Z" fill="#3b3346"/>
    <path d="M-128 -168 L -170 -236 L -88 -150Z M128 -168 L 170 -236 L 88 -150Z" fill="#4a4157"/>
    <rect x="-178" y="150" width="356" height="24" rx="6" fill="#2a2433"/><rect x="-20" y="146" width="40" height="32" rx="4" fill="none" stroke="#c9a65a" stroke-width="5"/>
    ${gafas}${maletin}</g>`;
}
function recibo(n, valor, marca = 1) {
  return `<g><rect x="-100" y="-130" width="200" height="260" fill="#efe6d2"/><path d="M-100 130 ${Array.from({ length: 10 }, (_, i) => `L ${-90 + i * 20} ${i % 2 ? 130 : 140}`).join(" ")} L 100 130Z" fill="#efe6d2"/>
    <text x="0" y="-92" text-anchor="middle" font-size="22" fill="#2a2420" font-family="Special Elite">PEDIDO #${n}</text>
    ${[-62, -38, -14].map((y, i) => `<line x1="-76" y1="${y}" x2="${[60, 30, 50][i]}" y2="${y}" stroke="#9a8f7a" stroke-width="5"/>`).join("")}
    <text x="-76" y="24" font-size="26" fill="#2a2420" font-family="Special Elite">$ ${valor}</text>
    <text x="0" y="86" text-anchor="middle" font-size="40" fill="#c01b2c" font-family="Special Elite">− 27 %</text>
    <ellipse cx="0" cy="74" rx="84" ry="34" fill="none" stroke="#c01b2c" stroke-width="5" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${1 - marca}" transform="rotate(-6)"/></g>`;
}
function chincheta(x, y, c = "#c01b2c") { return `<circle cx="${x + 3}" cy="${y + 4}" r="10" fill="rgba(0,0,0,.35)"/><circle cx="${x}" cy="${y}" r="10" fill="${c}"/><circle cx="${x - 3}" cy="${y - 3}" r="3" fill="rgba(255,255,255,.6)"/>`; }
