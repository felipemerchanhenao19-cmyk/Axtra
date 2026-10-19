// Personajes de «Orbi: universo de héroes». Parodias sin nombres ni logos de ninguna editorial.
// Orbi va centrado en (0,0) con radio ~116 (igual que la armadura de «Mark I»).
const HDEFS = `<defs>
  <linearGradient id="capaNoche" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a3550"/><stop offset=".5" stop-color="#121a2e"/><stop offset="1" stop-color="#05080f"/></linearGradient>
  <linearGradient id="capaRoja" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff4a52"/><stop offset=".55" stop-color="#a3121b"/><stop offset="1" stop-color="#4a050a"/></linearGradient>
  <linearGradient id="chaleco" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b2f36"/><stop offset="1" stop-color="#0c0e12"/></linearGradient>
  <linearGradient id="papel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e9e4d6"/><stop offset=".5" stop-color="#fbf8ef"/><stop offset="1" stop-color="#ddd6c4"/></linearGradient>
  <linearGradient id="tapa" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3f7a4a"/><stop offset=".6" stop-color="#1e4a2a"/><stop offset="1" stop-color="#0e2615"/></linearGradient>
  <radialGradient id="relojRojo" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#ff8a7a"/><stop offset=".3" stop-color="#e0302a"/><stop offset=".8" stop-color="#7a0d0d"/><stop offset="1" stop-color="#3a0505"/></radialGradient>
  <radialGradient id="metalGris" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#9aa3b0"/><stop offset=".5" stop-color="#4a5260"/><stop offset="1" stop-color="#1a1e26"/></radialGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="rgba(255,255,255,.9)"/><stop offset=".3" stop-color="rgba(160,230,255,.5)"/><stop offset="1" stop-color="rgba(160,230,255,0)"/></radialGradient>
  <radialGradient id="haloRojo"><stop offset="0" stop-color="rgba(255,120,120,.8)"/><stop offset="1" stop-color="rgba(255,40,40,0)"/></radialGradient>
  <radialGradient id="sombra"><stop offset="0" stop-color="rgba(0,0,0,.55)"/><stop offset="1" stop-color="rgba(0,0,0,0)"/></radialGradient>
</defs>`;
const sombraPiso = (w = 140) => `<ellipse cx="0" cy="0" rx="${w}" ry="${w * 0.18}" fill="url(#sombra)"/>`;
function orbiCara(t, nombre, h, extra = {}) {
  const base = { ...EXPRESIONES[nombre] || EXPRESIONES.normal, ...extra };
  if (h) { const a = 0.25 + 0.55 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 5.3)); base.boca = nombre === "feliz" ? [0.9, 1.2, Math.max(0.2, a)] : [0.3, 0.8, a * 0.8]; }
  if ((t % 3.4) < 0.12 && base.oi > 0) { base.oi = 0.08; if (base.od > 0) base.od = 0.08; }
  return orbi(nombre, { e: base, anillo: -10 + 4 * Math.sin(t * 1.3), brillo: 0.5 }).replace("<svg ", '<svg width="380" height="380" ');
}
// Capa que ondea con el viento (v = fuerza 0-1)
function capa(t, relleno, v = 0.5, largo = 330) {
  const o = (k) => Math.sin(t * (5 + v * 6) + k) * (16 + 40 * v);
  return `<path d="M-96 -40 Q -170 ${largo * 0.4} ${-180 - 40 * v + o(0)} ${largo + o(1) * 0.3} Q ${-90 + o(2)} ${largo - 30 + o(3) * 0.5} ${-20 + o(4) * 0.5} ${largo + 10 + o(2) * 0.4} Q ${60 + o(1)} ${largo - 20 + o(0) * 0.5} ${150 + 30 * v + o(3)} ${largo + o(4) * 0.3} Q 170 ${largo * 0.4} 96 -40 Z" fill="${relleno}" stroke="rgba(0,0,0,.4)" stroke-width="4"/>
    <path d="M-60 0 Q ${-90 + o(1) * 0.3} ${largo * 0.6} ${-110 + o(2) * 0.4} ${largo - 10}" stroke="rgba(255,255,255,.07)" stroke-width="18" fill="none"/>`;
}
// traje: capa | sinmiedo | castigador | armadura | normal
function orbiHeroe(t, traje, cara, h, o = {}) {
  const svg = orbiCara(t, cara, h, o.extra || {});
  if (traje === "armadura") return armadura(svg, { visor: 1, t, ...o.armor });
  let atras = "", frente = "";
  if (traje === "capa") {
    atras = capa(t, "url(#capaNoche)", o.viento ?? 0.5);
    // capucha con orejitas y antifaz
    frente = `<path d="M-100 -64 L -86 -150 L -54 -100 Q 0 -122 54 -100 L 86 -150 L 100 -64 Q 60 -96 0 -96 Q -60 -96 -100 -64Z" fill="#141c2e" stroke="#05080f" stroke-width="4"/>
      <path d="M-112 -30 Q -60 -60 0 -46 Q 60 -60 112 -30 L 108 12 Q 60 -4 30 6 Q 0 -6 -30 6 Q -60 -4 -108 12 Z" fill="#141c2e"/>
      <path d="M-62 -22 L -22 -16 L -26 -2 L -58 -8 Z M62 -22 L 22 -16 L 26 -2 L 58 -8 Z" fill="#f4fbff" opacity=".95"/>
      <g transform="translate(0 104)"><ellipse rx="34" ry="20" fill="#f4c430" stroke="#9a7410" stroke-width="4"/><text y="9" text-anchor="middle" font-size="26" font-weight="900" fill="#141c2e" font-family="Figtree">O</text></g>`;
  }
  if (traje === "sinmiedo") {
    atras = `<circle r="150" fill="url(#haloRojo)" opacity="${0.35 + 0.15 * Math.sin(t * 3)}"/>`;
    frente = `<path d="M-120 -34 Q 0 -70 120 -34 L 118 6 Q 0 -26 -118 6 Z" fill="#b5121b" stroke="#5a0509" stroke-width="4"/>
      <path d="M-120 -14 Q -150 0 -168 30 Q -140 6 -116 2 Z" fill="#b5121b"/><path d="M-118 -4 Q -156 26 -160 62 Q -138 26 -112 10 Z" fill="#8a0d14"/>
      <path d="M-48 -112 Q -40 -150 -20 -160 Q -30 -130 -26 -106 Z M48 -112 Q 40 -150 20 -160 Q 30 -130 26 -106 Z" fill="#b5121b" stroke="#5a0509" stroke-width="3"/>`;
  }
  if (traje === "castigador") {
    atras = `<path d="M-118 20 Q -126 150 0 160 Q 126 150 118 20 Q 60 70 0 70 Q -60 70 -118 20Z" fill="url(#chaleco)" transform="translate(0 2)"/>`;
    frente = `<path d="M-116 34 Q -60 92 0 92 Q 60 92 116 34 Q 104 106 0 120 Q -104 106 -116 34Z" fill="url(#chaleco)" stroke="#000" stroke-width="3"/>
      <g transform="translate(0 92)"><text y="14" text-anchor="middle" font-size="44" font-weight="900" fill="#f4f4f4" font-family="Figtree" letter-spacing="-2">0 %</text></g>
      <path d="M-70 52 L -54 70 M -64 48 L -48 66" stroke="#2a2e36" stroke-width="5"/>
      <path d="M-120 -8 L 120 -8 L 116 8 L -116 8 Z" fill="#111" opacity=".85"/><path d="M38 -6 L 46 14" stroke="#c9c9c9" stroke-width="3"/>`;
  }
  return `${atras}<g transform="translate(-190 -190)">${svg}</g>${frente}`;
}
// Villano: el Cuaderno de pedidos (letra que nadie entiende)
function cuaderno(o = {}) {
  const t = o.t || 0, h = o.boca || 0, c = o.cara || "malvado", risa = c === "risa" ? Math.sin(t * 22) * 6 : 0;
  const ojos = c === "derrotado" ? `<path d="M-70 -40 l 30 20 m 0 -20 l -30 20 M40 -40 l 30 20 m 0 -20 l -30 20" stroke="#111" stroke-width="8" stroke-linecap="round"/>`
    : `<ellipse cx="-56" cy="-30" rx="26" ry="${c === "shock" ? 30 : 20}" fill="#fff8d6" stroke="#111" stroke-width="5"/><ellipse cx="56" cy="-30" rx="26" ry="${c === "shock" ? 30 : 20}" fill="#fff8d6" stroke="#111" stroke-width="5"/>
       <circle cx="-50" cy="-26" r="10" fill="#c01b2c"/><circle cx="50" cy="-26" r="10" fill="#c01b2c"/>
       <path d="M-92 ${c === "shock" ? -76 : -66} L -26 ${c === "shock" ? -66 : -46} M92 ${c === "shock" ? -76 : -66} L 26 ${c === "shock" ? -66 : -46}" stroke="#111" stroke-width="12" stroke-linecap="round"/>`;
  const boca = h > 0.05 || c === "risa" ? `<path d="M-56 30 Q 0 ${50 + 50 * Math.max(h, c === "risa" ? 0.7 : 0)} 56 30 Z" fill="#3a0a0a" stroke="#111" stroke-width="5"/><path d="M-40 32 L -30 46 L -20 33 M20 33 L 30 46 L 40 32" fill="#fff"/>`
    : c === "derrotado" ? `<path d="M-40 50 Q 0 26 40 50" stroke="#111" stroke-width="8" fill="none"/>` : `<path d="M-56 30 Q 0 66 56 30" stroke="#111" stroke-width="8" fill="none"/>`;
  const hoja = (i) => `<rect x="${-150 + i * 3}" y="${-190 + i * 3}" width="300" height="400" rx="12" fill="url(#papel)" stroke="#bdb6a2" stroke-width="2"/>`;
  return `<g transform="rotate(${risa})">
    ${sombraPiso(170).replace("<ellipse", '<ellipse transform="translate(0 270)"')}
    ${[-60, 60].map((x) => `<path d="M${x} 200 L ${x + (x < 0 ? -10 : 10)} 262" stroke="#1a1a1a" stroke-width="16" stroke-linecap="round"/><ellipse cx="${x + (x < 0 ? -22 : 22)}" cy="268" rx="34" ry="14" fill="#111"/>`).join("")}
    ${[3, 2, 1].map(hoja).join("")}
    <rect x="-160" y="-200" width="300" height="410" rx="14" fill="url(#tapa)" stroke="#0a1a0e" stroke-width="5"/>
    <rect x="-130" y="-120" width="240" height="70" rx="8" fill="#efe6c8" opacity=".9"/><text x="-10" y="-74" text-anchor="middle" font-size="34" font-weight="900" fill="#1e4a2a" font-family="Figtree">PEDIDOS</text>
    ${Array.from({ length: 9 }, (_, i) => `<ellipse cx="${-140 + i * 32}" cy="-204" rx="10" ry="22" fill="none" stroke="#b9c0c8" stroke-width="7"/>`).join("")}
    <g transform="translate(-10 40)">${ojos}${boca}</g>
    <g transform="translate(${-200} ${20}) rotate(${o.brazo === "arriba" ? -60 : -10})"><path d="M60 0 L -30 -10" stroke="#1a1a1a" stroke-width="16" stroke-linecap="round"/><g transform="translate(-40 -12) rotate(-70)"><rect x="-10" y="-90" width="20" height="150" fill="#f4c430" stroke="#9a7410" stroke-width="3"/><path d="M-10 60 L 0 92 L 10 60 Z" fill="#e8c39e"/><path d="M-4 82 L 0 92 L 4 82Z" fill="#222"/><rect x="-10" y="-104" width="20" height="16" fill="#e38" /></g></g>
    <path d="M150 20 Q 210 ${o.brazo === "lanza" ? -40 : 60} 230 ${o.brazo === "lanza" ? -90 : 100}" stroke="#1a1a1a" stroke-width="16" stroke-linecap="round" fill="none"/>
    ${o.garabatos ? Array.from({ length: 4 }, (_, i) => `<path d="M${-110} ${140 + i * 16} q 20 -14 40 0 t 40 0 t 40 0 t 40 0 t 30 0" stroke="#1e3a8a" stroke-width="3" fill="none" opacity=".7"/>`).join("") : ""}
  </g>`;
}
// Villano: la Hora Pico (despertador gigante)
function horaPico(o = {}) {
  const t = o.t || 0, h = o.boca || 0, c = o.cara || "furia", giro = o.giro ?? t * 90, temblor = c === "furia" ? Math.sin(t * 40) * 3 : 0;
  const ojos = c === "dormido" ? `<path d="M-70 -30 q 25 14 50 0 M20 -30 q 25 14 50 0" stroke="#111" stroke-width="8" fill="none"/>`
    : `<path d="M-80 -54 L -20 -36 L -26 -14 Q -60 -10 -76 -30Z M80 -54 L 20 -36 L 26 -14 Q 60 -10 76 -30Z" fill="#fff36b" stroke="#111" stroke-width="5"/><circle cx="-44" cy="-30" r="7" fill="#111"/><circle cx="44" cy="-30" r="7" fill="#111"/>`;
  const boca = h > 0.05 ? `<ellipse cx="0" cy="64" rx="${40 + 10 * h}" ry="${10 + 34 * h}" fill="#3a0a0a" stroke="#111" stroke-width="5"/>` : c === "dormido" ? `<path d="M-20 64 Q 0 76 20 64" stroke="#111" stroke-width="6" fill="none"/>` : `<path d="M-50 70 L -30 58 L -10 72 L 10 58 L 30 72 L 50 58" stroke="#111" stroke-width="7" fill="none" stroke-linejoin="round"/>`;
  return `<g transform="translate(${temblor} 0)">
    ${sombraPiso(190).replace("<ellipse", '<ellipse transform="translate(0 290)"')}
    ${[-1, 1].map((s) => `<path d="M${s * 110} 180 L ${s * 150} 280" stroke="#2a2a2a" stroke-width="22" stroke-linecap="round"/><ellipse cx="${s * 160}" cy="284" rx="40" ry="14" fill="#111"/>`).join("")}
    ${[-1, 1].map((s) => `<g transform="translate(${s * 140} -170) rotate(${s * 30 + (c === "furia" ? Math.sin(t * 50) * 8 : 0)})"><path d="M-70 30 A 70 70 0 0 1 70 30 Z" fill="url(#metalGris)" stroke="#111" stroke-width="5"/><circle cy="-46" r="12" fill="#666"/></g>`).join("")}
    <path d="M-60 -200 L 60 -200 L 0 -150 Z" fill="#555" opacity="${c === "furia" ? 1 : 0}"/>
    <circle r="230" fill="url(#relojRojo)" stroke="#2a0303" stroke-width="8"/>
    <circle r="180" fill="#fff8e8" stroke="#c9b48a" stroke-width="8"/>
    ${Array.from({ length: 12 }, (_, i) => `<line x1="0" y1="-160" x2="0" y2="${i % 3 ? -146 : -134}" stroke="#333" stroke-width="${i % 3 ? 4 : 8}" transform="rotate(${i * 30})"/>`).join("")}
    <text y="-100" text-anchor="middle" font-size="34" font-weight="900" fill="#c01b2c" font-family="Figtree">8:00 P. M.</text>
    ${ojos}${boca}
    <g transform="rotate(${giro})"><path d="M-8 0 L 0 -150 L 8 0 Z" fill="#111" opacity=".85"/></g><g transform="rotate(${giro / 12})"><path d="M-12 0 L 0 -100 L 12 0 Z" fill="#111" opacity=".85"/></g><circle r="14" fill="#c01b2c"/>
    ${c === "furia" ? [-1, 1].map((s) => `<path d="M${s * 200} -230 q ${s * 20} -40 0 -80 q ${-s * 20} -30 0 -60" stroke="rgba(255,255,255,${0.4 + 0.3 * Math.sin(t * 8)})" stroke-width="14" fill="none" stroke-linecap="round"/>`).join("") : ""}
  </g>`;
}
// Matones: los Porcentajes (El 15, El 27, El 30)
function porcentaje(o = {}) {
  const t = o.t || 0, n = o.n || 27, h = o.boca || 0, c = o.cara || "matón", col = { 15: "#6b7280", 27: "#7c2d12", 30: "#3f3f46" }[n] || "#444";
  const boca = h > 0.05 ? `<ellipse cx="0" cy="40" rx="${18 + 6 * h}" ry="${6 + 18 * h}" fill="#200" stroke="#000" stroke-width="4"/>` : c === "shock" ? `<ellipse cx="0" cy="44" rx="16" ry="20" fill="#200" stroke="#000" stroke-width="4"/>` : `<path d="M-26 40 Q 0 30 26 46" stroke="#000" stroke-width="7" fill="none" stroke-linecap="round"/>`;
  return `<g>
    ${sombraPiso(110).replace("<ellipse", '<ellipse transform="translate(0 200)"')}
    ${[-1, 1].map((s) => `<path d="M${s * 40} 120 L ${s * 50} 190" stroke="#111" stroke-width="18" stroke-linecap="round"/><ellipse cx="${s * 62}" cy="196" rx="30" ry="12" fill="#000"/>`).join("")}
    ${[-1, 1].map((s) => `<path d="M${s * 100} 0 Q ${s * 150} 60 ${s * 120} 110" stroke="${col}" stroke-width="26" stroke-linecap="round" fill="none"/><circle cx="${s * 120}" cy="116" r="20" fill="${col}" stroke="#000" stroke-width="4"/>`).join("")}
    <rect x="-110" y="-150" width="220" height="280" rx="70" fill="${col}" stroke="#000" stroke-width="6"/>
    <rect x="-90" y="-136" width="40" height="200" rx="20" fill="rgba(255,255,255,.08)"/>
    <text x="0" y="110" text-anchor="middle" font-size="76" font-weight="900" fill="#fff" font-family="Figtree" letter-spacing="-3">${n}%</text>
    <path d="M-92 -70 L 92 -70 L 84 -36 Q 50 -24 10 -40 L -10 -40 Q -50 -24 -84 -36 Z" fill="#050505"/><path d="M-70 -64 L -40 -64" stroke="rgba(255,255,255,.5)" stroke-width="5"/>
    <path d="M-80 -92 L -20 -78 M80 -92 L 20 -78" stroke="#000" stroke-width="10" stroke-linecap="round"/>
    ${boca}
    ${c === "golpe" ? `<path d="M-60 -120 l 20 20 m 0 -20 l -20 20 M40 -120 l 20 20 m 0 -20 l -20 20" stroke="#fff" stroke-width="6"/>` : ""}
  </g>`;
}
// Villana: Lady Factura (un recibo que crece sin fin)
function factura(o = {}) {
  const t = o.t || 0, h = o.boca || 0, c = o.cara || "diva", largo = o.largo ?? 600, limpio = o.limpia;
  const items = limpio ? [["Bandeja paisa", "$ 32.000"], ["Limonada", "$ 8.000"], ["Domicilio propio", "$ 5.000"], ["Comisión", "$ 0"]]
    : [["Bandeja paisa", "$ 32.000"], ["Comisión 27 %", "$ 8.640"], ["Tarifa de servicio", "$ 3.900"], ["Tarifa dinámica", "$ 2.500"], ["Cargo por lluvia", "$ 1.800"], ["Cargo por existir", "$ 990"], ["Comisión extra", "$ 4.000"], ["Otra tarifa", "$ 2.200"]];
  const tach = o.tachados || 0, w = 380, zig = Array.from({ length: 11 }, (_, i) => `L ${w / 2 - (i + 0.5) * (w / 11)} ${largo + 18} L ${w / 2 - (i + 1) * (w / 11)} ${largo}`).join(" ");
  const cara = `<g transform="translate(0 30)">
      ${c === "derrotada" ? `<path d="M-74 -20 q 26 16 52 0 M22 -20 q 26 16 52 0" stroke="#111" stroke-width="7" fill="none"/>`
      : `<ellipse cx="-48" cy="-16" rx="24" ry="${c === "shock" ? 28 : 18}" fill="#fff" stroke="#111" stroke-width="5"/><ellipse cx="48" cy="-16" rx="24" ry="${c === "shock" ? 28 : 18}" fill="#fff" stroke="#111" stroke-width="5"/>
        <circle cx="-44" cy="-12" r="9" fill="#5b21b6"/><circle cx="44" cy="-12" r="9" fill="#5b21b6"/>
        ${[-60, -48, -36].map((x) => `<line x1="${x}" y1="-34" x2="${x - 6}" y2="-50" stroke="#111" stroke-width="4"/><line x1="${-x}" y1="-34" x2="${-x + 6}" y2="-50" stroke="#111" stroke-width="4"/>`).join("")}
        <path d="M-84 -52 Q -50 ${c === "enojo" ? -40 : -70} -20 -50 M84 -52 Q 50 ${c === "enojo" ? -40 : -70} 20 -50" stroke="#111" stroke-width="7" fill="none" stroke-linecap="round"/>`}
      ${h > 0.05 ? `<ellipse cx="0" cy="46" rx="${18 + 6 * h}" ry="${6 + 18 * h}" fill="#7a0f2e" stroke="#e01e5a" stroke-width="7"/>` : `<path d="M-30 40 Q 0 62 30 40 Q 0 50 -30 40Z" fill="#e01e5a" stroke="#a0103e" stroke-width="4"/>`}
    </g>`;
  const filas = items.map(([a, b], i) => { const y = 170 + i * 46; if (y > largo - 60) return ""; const x = i < tach && !limpio && i > 0;
    return `<text x="-168" y="${y}" font-size="22" font-family="DejaVu Sans Mono, monospace" fill="#333">${a}</text><text x="168" y="${y}" text-anchor="end" font-size="22" font-family="DejaVu Sans Mono, monospace" fill="#333">${b}</text>
      ${x ? `<line x1="-175" y1="${y - 8}" x2="175" y2="${y - 8}" stroke="#e01e3c" stroke-width="6"/>` : ""}`; }).join("");
  const total = limpio ? `<text x="0" y="${170 + 4 * 46 + 30}" text-anchor="middle" font-size="34" font-weight="900" fill="#0e7a4a" font-family="Figtree">TOTAL $ 45.000 ✓</text>` : "";
  const brazo = (s) => `<path d="M${s * 150} 140 Q ${s * (230 + 30 * Math.sin(t * 6 + s))} ${100 + 40 * Math.cos(t * 5)} ${s * (300 + 40 * Math.sin(t * 4))} ${40 + 60 * Math.sin(t * 3 + s)}" stroke="#fbf8ef" stroke-width="30" fill="none" stroke-linecap="round" opacity=".95"/>`;
  return `<g>
    ${o.latigos ? brazo(-1) + brazo(1) : ""}
    <path d="M${-w / 2} -60 Q ${-w / 2} -110 0 -112 Q ${w / 2} -110 ${w / 2} -60 L ${w / 2} ${largo} ${zig} Z" fill="url(#papel)" stroke="#bdb6a2" stroke-width="4"/>
    <path d="M${-w / 2 + 20} -60 Q -60 -120 -20 -150 Q 10 -170 40 -150 Q 90 -130 ${w / 2 - 20} -60" fill="#5b21b6" opacity="${limpio ? 0 : 1}"/>
    <circle cx="70" cy="-150" r="16" fill="#e01e5a" opacity="${limpio ? 0 : 1}"/>
    ${cara}<line x1="-170" y1="128" x2="170" y2="128" stroke="#999" stroke-width="3" stroke-dasharray="8 6"/>${filas}${total}
  </g>`;
}
// Sofía, la IA del taller: holograma con onda de voz
function sofia(o = {}) {
  const t = o.t || 0, h = o.boca || 0;
  return `<g><ellipse cx="0" cy="140" rx="120" ry="26" fill="none" stroke="rgba(120,230,255,.6)" stroke-width="4"/><path d="M-110 140 L -50 -80 L 50 -80 L 110 140 Z" fill="rgba(80,220,255,.08)"/>
    ${[0, 1, 2].map((i) => `<circle r="${50 + i * 22 + 6 * Math.sin(t * 3 + i)}" fill="none" stroke="rgba(120,230,255,${0.6 - i * 0.15})" stroke-width="3"/>`).join("")}
    <path d="M-60 0 ${Array.from({ length: 24 }, (_, i) => `L ${-60 + i * 5.2} ${Math.sin(t * 30 + i) * (4 + 40 * h) * Math.sin((i / 23) * Math.PI)}`).join(" ")}" stroke="#bff6ff" stroke-width="4" fill="none"/></g>`;
}
