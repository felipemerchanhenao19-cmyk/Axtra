// Vestuario y utilería de «Mesero nocturno»: Orbi con chaqueta militar verde oliva, el taxi amarillo y los soportes QR de Apex Play.
function chaqueta(svgOrbi, o = {}) {
  return `<g>
    <path d="M-160 260 Q -196 120 -100 78 L 100 78 Q 196 120 160 260 Q 0 292 -160 260Z" fill="#4d5233"/>
    <path d="M-160 260 Q -196 120 -100 78 L -44 78 L -66 270Z" fill="#41452a"/>
    <path d="M0 110 L 0 270" stroke="#2f3220" stroke-width="6"/>${[140, 180, 220].map((y) => `<circle cx="-14" cy="${y}" r="6" fill="#2f3220"/>`).join("")}
    <rect x="-140" y="170" width="70" height="56" rx="6" fill="#454a2e" stroke="#2f3220" stroke-width="4"/><rect x="70" y="170" width="70" height="56" rx="6" fill="#454a2e" stroke="#2f3220" stroke-width="4"/>
    <g transform="translate(-105 140) rotate(-6)"><rect x="-40" y="-16" width="80" height="32" rx="4" fill="#1b1d12" stroke="#c9a65a" stroke-width="3"/><text y="7" text-anchor="middle" font-size="18" font-weight="800" fill="#e8c27a" font-family="Figtree">APEX</text></g>
    <g transform="translate(-190 -190)">${svgOrbi}</g>
    <path d="M-110 84 L -40 106 L -64 150 L -128 112Z" fill="#5d6340" stroke="#363a24" stroke-width="4"/>
    <path d="M110 84 L 40 106 L 64 150 L 128 112Z" fill="#5d6340" stroke="#363a24" stroke-width="4"/>
  </g>`;
}
// Taxi amarillo visto de lado. ruedas = ángulo de giro; ventana = contenido (Orbi al volante).
function taxi(t, o = {}) {
  const giro = (t * 720) % 360;
  const rueda = (x) => `<g transform="translate(${x} 150)"><circle r="78" fill="#0d0d10"/><circle r="44" fill="#7b7f88"/><g transform="rotate(${giro})">${[0, 60, 120].map((a) => `<rect x="-40" y="-5" width="80" height="10" fill="#4a4e57" transform="rotate(${a})"/>`).join("")}</g><circle r="12" fill="#c9ced6"/></g>`;
  return `<g>
    <ellipse cx="0" cy="232" rx="460" ry="26" fill="rgba(0,0,0,.6)"/>
    <path d="M-440 140 L -440 40 Q -430 -10 -360 -20 L -230 -30 L -150 -140 Q -130 -160 -90 -160 L 170 -160 Q 210 -160 240 -130 L 320 -30 L 410 -10 Q 450 0 452 40 L 452 140Z" fill="#f2b705"/>
    <path d="M-440 60 L 452 60" stroke="#c48f00" stroke-width="4"/>
    <g>${Array.from({ length: 22 }, (_, i) => `<rect x="${-420 + i * 40}" y="70" width="20" height="20" fill="${i % 2 ? "#111" : "#f2b705"}"/><rect x="${-400 + i * 40}" y="90" width="20" height="20" fill="${i % 2 ? "#f2b705" : "#111"}"/>`).join("").replace(/x="(\d+)"/g, (m, x) => +x > 430 ? 'x="-999"' : m)}</g>
    <path d="M-206 -32 L -140 -134 L 40 -134 L 40 -32Z" fill="#14181f"/><path d="M60 -32 L 60 -134 L 170 -134 Q 200 -134 222 -110 L 290 -32Z" fill="#14181f"/>
    <clipPath id="taxiVent"><path d="M60 -32 L 60 -134 L 170 -134 Q 200 -134 222 -110 L 290 -32Z"/></clipPath>
    <g clip-path="url(#taxiVent)">${o.ventana || ""}</g>
    <path d="M60 -134 L 170 -134 Q 200 -134 222 -110 L 250 -76" fill="none" stroke="rgba(255,255,255,.25)" stroke-width="6"/>
    <rect x="-70" y="-206" width="140" height="46" rx="10" fill="#fff4c4" style="filter:drop-shadow(0 0 18px #ffd84a)"/><text y="-173" text-anchor="middle" font-size="30" font-weight="800" fill="#2a2108" font-family="Figtree">TAXI</text>
    <rect x="410" y="0" width="40" height="30" rx="8" fill="#fff6c8" style="filter:drop-shadow(0 0 30px #fff2a0)"/><rect x="-446" y="4" width="22" height="30" rx="6" fill="#ff2a2a" style="filter:drop-shadow(0 0 20px #ff2a2a)"/>
    ${rueda(-280)}${rueda(290)}
  </g>`;
}
// Soporte de mesa con el QR de Apex Play y Orbi chiquito encima.
function soporteQR(brillo = 1) {
  const q = Array.from({ length: 49 }, (_, i) => ((i * 37 + (i >> 2) * 11) % 5 < 2 || [0, 1, 7, 8, 5, 6, 12, 13, 35, 36, 42, 43].includes(i)) ? `<rect x="${-35 + (i % 7) * 10}" y="${-35 + Math.floor(i / 7) * 10}" width="10" height="10" fill="#0b1626"/>` : "").join("");
  return `<g><circle cx="0" cy="-30" r="${90 * brillo}" fill="rgba(47,187,232,${0.18 * brillo})"/><path d="M-56 40 L -46 -90 L 46 -90 L 56 40Z" fill="#0b1626" stroke="#2fbbe8" stroke-width="5"/>
    <rect x="-40" y="-70" width="80" height="80" rx="6" fill="#fff"/><g transform="translate(0 -30)">${q}</g><text y="32" text-anchor="middle" font-size="16" font-weight="800" fill="#5fc9f1" font-family="Figtree">APEX PLAY</text></g>`;
}
function celular(brillo = 1) {
  return `<g><rect x="-34" y="-62" width="68" height="124" rx="12" fill="#14181f"/><rect x="-28" y="-52" width="56" height="100" rx="6" fill="#2fbbe8" opacity="${0.4 + 0.6 * brillo}"/>
    <circle cy="-8" r="16" fill="#e6f9ff" opacity="${brillo}"/><rect x="-18" y="22" width="36" height="8" rx="4" fill="#e6f9ff" opacity="${brillo}"/></g>`;
}
