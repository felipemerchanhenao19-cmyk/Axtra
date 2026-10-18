// Comi: mochila de domicilios ficticia, diva de telenovela. Doña Rosa: dueña del restaurante.
function comi(o = {}) {
  const cara = o.cara || "diva", hab = o.boca ?? 0, ojoAp = cara === "shock" ? 1.25 : cara === "diva" ? 0.55 : cara === "llanto" ? 0.35 : 0.9;
  const ojo = (cx, s) => `<g transform="translate(${cx} -20)"><ellipse rx="26" ry="${30 * ojoAp}" fill="#fff"/><circle cx="${s * 3}" cy="${4 * ojoAp}" r="${12 * Math.min(1, ojoAp + 0.3)}" fill="#2b0a2e"/>
    <path d="M-30 ${-30 * ojoAp + 4} Q 0 ${-44 * ojoAp} 30 ${-30 * ojoAp + 4}" fill="#7b2cbf" opacity=".7"/>
    ${[-24, -12, 0, 12, 24].map((x) => `<line x1="${x}" y1="${-29 * ojoAp}" x2="${x * 1.3}" y2="${-29 * ojoAp - 16}" stroke="#1a0a1c" stroke-width="4" stroke-linecap="round"/>`).join("")}</g>`;
  const ceja = cara === "enojo" ? `<path d="M-90 -78 L -36 -62 M36 -62 L 90 -78" stroke="#1a0a1c" stroke-width="9" stroke-linecap="round"/>`
    : cara === "llanto" ? `<path d="M-90 -64 L -36 -80 M36 -80 L 90 -64" stroke="#1a0a1c" stroke-width="9" stroke-linecap="round"/>`
    : `<path d="M-92 -78 Q -62 -96 -34 -80 M34 -80 Q 62 -96 92 -78" stroke="#1a0a1c" stroke-width="8" fill="none" stroke-linecap="round"/>`;
  const boca = hab > 0.05 || cara === "shock" ? `<ellipse cx="0" cy="60" rx="${22 + 6 * hab}" ry="${8 + 26 * Math.max(hab, cara === "shock" ? 0.8 : 0)}" fill="#7a0f2e" stroke="#e01e5a" stroke-width="8"/>`
    : cara === "llanto" ? `<path d="M-34 70 Q 0 44 34 70" stroke="#e01e5a" stroke-width="12" fill="none" stroke-linecap="round"/>`
    : `<path d="M-34 52 Q 0 82 34 52 Q 0 66 -34 52Z" fill="#e01e5a"/>`;
  const lagrimas = cara === "llanto" ? `<path d="M-62 -6 Q -70 60 -64 140" stroke="#7fd7ff" stroke-width="14" fill="none" opacity=".85"/><path d="M62 -6 Q 70 60 64 140" stroke="#7fd7ff" stroke-width="14" fill="none" opacity=".85"/>` : "";
  const abanico = o.abanico ? `<g transform="translate(-200 30) rotate(${o.abanico})"><path d="M0 0 L -90 -80 A 120 120 0 0 1 40 -118 Z" fill="#ff7bbf" stroke="#b5179e" stroke-width="4"/>
    ${[0, 1, 2, 3].map((i) => `<line x1="0" y1="0" x2="${-90 + i * 40}" y2="${-80 - i * 12}" stroke="#b5179e" stroke-width="3"/>`).join("")}</g>` : "";
  return `<g>
    <rect x="-70" y="160" width="26" height="80" rx="10" fill="#3a0d3f"/><rect x="44" y="160" width="26" height="80" rx="10" fill="#3a0d3f"/>
    <path d="M-80 240 l 40 0 l -6 -14 Z M40 240 l 40 0 l -6 -14 Z" fill="#e01e5a"/>
    <path d="M-150 -40 Q -230 20 -200 40" stroke="#b5179e" stroke-width="26" stroke-linecap="round" fill="none"/>
    <path d="M150 -40 Q 230 ${o.brazoArriba ? -120 : 20} 200 ${o.brazoArriba ? -170 : 40}" stroke="#b5179e" stroke-width="26" stroke-linecap="round" fill="none"/>
    <rect x="-160" y="-170" width="320" height="340" rx="40" fill="#b5179e"/>
    <rect x="-160" y="-170" width="320" height="70" rx="34" fill="#d63aaf"/>
    <rect x="-60" y="-200" width="120" height="40" rx="18" fill="none" stroke="#7b1468" stroke-width="12"/>
    <circle cx="-120" cy="-70" r="10" fill="#ffd166"/><circle cx="120" cy="-70" r="10" fill="#ffd166"/>
    ${ojo(-60, 1)}${ojo(60, -1)}${ceja}${boca}${lagrimas}
    <g transform="translate(0 128)"><rect x="-70" y="-24" width="140" height="44" rx="12" fill="#fff"/><text x="0" y="10" text-anchor="middle" font-size="30" font-weight="800" fill="#b5179e" font-family="Figtree">COMI</text></g>
    <path d="M-60 -230 L -30 -270 L 0 -238 L 30 -270 L 60 -230 Z" fill="#ffd166" stroke="#e0a800" stroke-width="4"/>
    ${abanico}
  </g>`;
}
function rosa(o = {}) {
  const p = persona({ piel: "#e3b48c", pelo: "moño", colorPelo: "#9aa0a6", camisa: "#2a9d8f", brazo: o.brazo || 0, boca: o.boca ?? 0.4, cejas: o.cejas || "", mira: o.mira || 0 });
  return `<g>${p}<rect x="-52" y="-30" width="104" height="90" rx="12" fill="#f4f1ea"/><path d="M-30 -30 L -40 -62 M30 -30 L 40 -62" stroke="#f4f1ea" stroke-width="8"/>
    <circle cx="-18" cy="-140" r="15" fill="none" stroke="#333" stroke-width="4"/><circle cx="18" cy="-140" r="15" fill="none" stroke="#333" stroke-width="4"/><line x1="-3" y1="-140" x2="3" y2="-140" stroke="#333" stroke-width="4"/></g>`;
}
function mostrador() {
  return `<g><rect x="-460" y="0" width="920" height="40" rx="10" fill="#c58a54"/><rect x="-440" y="40" width="880" height="320" fill="#7a4b2e"/>
    ${[-330, -110, 110, 330].map((x) => `<rect x="${x - 90}" y="70" width="180" height="250" rx="12" fill="rgba(0,0,0,.15)"/>`).join("")}
    <g transform="translate(300 -40)"><rect x="-70" y="-50" width="140" height="90" rx="12" fill="#2b2d33"/><rect x="-50" y="-36" width="100" height="34" rx="6" fill="#2fbbe8" opacity=".8"/>
      <rect x="-80" y="40" width="160" height="20" rx="6" fill="#3a3d45"/></g></g>`;
}
function billetes(n, dx = 0, dy = 0) {
  return Array.from({ length: n }, (_, i) => `<g transform="translate(${-180 + dx + (i % 4) * 8} ${-14 - i * 7 + dy}) rotate(${(i * 37) % 9 - 4})"><rect x="-60" y="-14" width="120" height="28" rx="4" fill="#5fa86b" stroke="#2f6b3a" stroke-width="3"/><circle r="8" fill="#2f6b3a"/></g>`).join("");
}
function billete(x, y, r) { return `<g transform="translate(${x} ${y}) rotate(${r})"><rect x="-60" y="-14" width="120" height="28" rx="4" fill="#5fa86b" stroke="#2f6b3a" stroke-width="3"/><circle r="8" fill="#2f6b3a"/></g>`; }
