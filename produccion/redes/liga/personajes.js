// «La Liga de la Cocina»: la comida de «Orbi en la cocina» con trajes de superhéroe (sin nombres ni logos de ninguna editorial).
// heroeFruta(tipo, o): capa, antifaz, emblema, tiara, anillo verde, partes de máquina, lazo de queso, estela de velocidad.
const EMB_Y = { arepa: 70, empanada: 34, tinto: 62, aguacate: 118, papa: 78, pan: 62, hamburguesa: 28, chorizo: 84 };
function emblema(e, y) {
  return `<g transform="translate(0 ${y})"><path d="M0 -40 L 40 -14 L 26 34 L -26 34 L -40 -14 Z" fill="${e.fondo || "#ffd166"}" stroke="#111" stroke-width="5"/>
    <text y="18" text-anchor="middle" font-size="44" font-weight="900" fill="${e.color || "#c01b2c"}" font-family="Figtree">${e.letra}</text></g>`;
}
function heroeFruta(tipo, o = {}) {
  const [bw, arriba, fy, abajo] = FORMA[tipo], t = o.t || 0; let atras = "", frente = "";
  if (o.rayos) atras += Array.from({ length: 7 }, (_, i) => `<path d="M${-bw - 40 - i * 50} ${-80 + i * 34} l -120 ${(i % 2 ? 1 : -1) * 18} l 50 0 l -110 ${(i % 2 ? -1 : 1) * 22}" stroke="#ffd166" stroke-width="${8 - i * 0.6}" fill="none" opacity="${0.9 - i * 0.1}" stroke-linejoin="round"/>`).join("");
  if (o.anillo) atras += `<circle r="${bw + 90}" cy="20" fill="url(#auraVerde)" opacity="${0.55 + 0.2 * Math.sin(t * 4)}"/>`;
  if (o.capa) atras += `<g transform="translate(0 ${fy + 30}) scale(${bw / 105} .62)">${capa(t, o.capa, o.viento ?? 0.6, 330)}</g>`;
  if (o.lazo) { const [lx, ly] = o.lazo, hx = bw + 50, hy = -100;
    atras += `<path d="M${hx} ${hy} Q ${(hx + lx) / 2} ${Math.min(hy, ly) - 160 + 20 * Math.sin(t * 6)} ${lx} ${ly}" stroke="rgba(255,220,90,.45)" stroke-width="26" fill="none"/>
      <path d="M${hx} ${hy} Q ${(hx + lx) / 2} ${Math.min(hy, ly) - 160 + 20 * Math.sin(t * 6)} ${lx} ${ly}" stroke="#ffd34a" stroke-width="10" fill="none" stroke-dasharray="18 6"/>
      <ellipse cx="${lx}" cy="${ly}" rx="120" ry="40" fill="none" stroke="#ffd34a" stroke-width="10"/>`; }
  const cuerpo = comida(tipo, { ...o, acc: o.acc || [], brazo: o.brazo || (o.lazo || o.anillo ? "arriba" : "abajo") });
  if (o.antifaz) { const y = fy;
    frente += `<path fill-rule="evenodd" d="M${-bw * 0.62} ${y - 20} Q 0 ${y - 46} ${bw * 0.62} ${y - 20} L ${bw * 0.6} ${y + 16} Q 0 ${y + 2} ${-bw * 0.6} ${y + 16} Z
      M-62 ${y} a 24 30 0 1 0 48 0 a 24 30 0 1 0 -48 0 Z M14 ${y} a 24 30 0 1 0 48 0 a 24 30 0 1 0 -48 0 Z" fill="${o.antifaz}" stroke="rgba(0,0,0,.5)" stroke-width="3"/>`; }
  if (o.ciber) frente += `<g transform="translate(0 ${fy})"><path d="M8 -${bw * 0.55} Q ${bw * 0.85} -${bw * 0.5} ${bw * 0.85} 20 Q ${bw * 0.8} 70 10 80 Z" fill="url(#metalGris)" stroke="#111" stroke-width="4" opacity=".95"/>
      <circle cx="38" cy="0" r="20" fill="#2a0000" stroke="#555" stroke-width="5"/><circle cx="38" cy="0" r="${10 + 2 * Math.sin(t * 8)}" fill="#ff2a2a"/><circle cx="38" cy="0" r="40" fill="url(#haloRojo)" opacity=".7"/>
      ${[-30, 0, 30, 60].map((yy) => `<line x1="${bw * 0.3}" y1="${yy}" x2="${bw * 0.8}" y2="${yy}" stroke="#2a2e36" stroke-width="3"/>`).join("")}</g>`;
  if (o.tiara) frente += `<g transform="translate(0 ${arriba + 18})"><path d="M-80 10 Q 0 -10 80 10 L 72 26 Q 0 8 -72 26 Z" fill="#f2c14a" stroke="#9a7410" stroke-width="4"/><polygon points="0,-30 8,-8 30,-8 12,6 18,28 0,14 -18,28 -12,6 -30,-8 -8,-8" fill="#c01b2c" stroke="#9a7410" stroke-width="3"/></g>`;
  if (o.emblema) frente += emblema(o.emblema, EMB_Y[tipo]);
  if (o.anillo) frente += `<circle cx="${bw + 50}" cy="-100" r="22" fill="#7cff6a"/><circle cx="${bw + 50}" cy="-100" r="60" fill="url(#auraVerde)"/>`;
  if (o.alas) frente += [-1, 1].map((s) => `<path d="M${s * (bw - 10)} ${arriba + 40} l ${s * 50} -40 l ${-s * 10} 30 l ${s * 40} -20 l ${-s * 20} 40 Z" fill="#f2c14a" stroke="#9a7410" stroke-width="3"/>`).join("");
  return `<g>${atras}${cuerpo}${frente}</g>`;
}
// El villano: Lord Comisión, un 27 % gigante con corona y capa
function lordComision(o = {}) {
  const t = o.t || 0;
  return `<g><circle r="380" cy="-40" fill="url(#auraMorada)" opacity="${0.7 + 0.2 * Math.sin(t * 3)}"/>
    <g transform="translate(0 -60) scale(1.7 1.1)">${capa(t, "#2a0a3a", 0.5, 330)}</g>
    ${porcentaje({ ...o, n: 27 })}
    <g transform="translate(0 -160)"><path d="M-90 0 L -90 -60 L -50 -24 L 0 -80 L 50 -24 L 90 -60 L 90 0 Z" fill="#3a3a3a" stroke="#111" stroke-width="5"/>${[-60, 0, 60].map((x) => `<circle cx="${x}" cy="-14" r="8" fill="#ff2a6a"/>`).join("")}</g>
    ${[-40, 40].map((x) => `<circle cx="${x}" cy="-52" r="16" fill="#ff2a2a" opacity="${0.8 + 0.2 * Math.sin(t * 9)}"/>`).join("")}</g>`;
}
const LIGA_DEFS = `<defs>
  <radialGradient id="auraVerde"><stop offset="0" stop-color="rgba(124,255,106,.6)"/><stop offset="1" stop-color="rgba(124,255,106,0)"/></radialGradient>
  <radialGradient id="auraMorada"><stop offset="0" stop-color="rgba(150,40,200,.55)"/><stop offset="1" stop-color="rgba(90,0,140,0)"/></radialGradient>
  <radialGradient id="planetaHorno" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#ffd27a"/><stop offset=".5" stop-color="#e0702a"/><stop offset="1" stop-color="#5a1a08"/></radialGradient>
</defs>`;
// Espacio con el planeta Horno (origen de la Súper Empanada)
function espacio(t, o = {}) {
  const k = o.explota ?? 0;
  let s = `<rect x="-900" y="-900" width="2900" height="3800" fill="#03040c"/>` + Array.from({ length: 120 }, (_, i) => `<circle cx="${rnd(i) * 2600 - 700}" cy="${rnd(i + 5) * 2600 - 400}" r="${0.8 + rnd(i + 2) * 2.4}" fill="#fff" opacity="${0.4 + 0.6 * Math.abs(Math.sin(t * 1.3 + i))}"/>`).join("");
  s += `<g transform="translate(540 760)"><circle r="${330 + 30 * k}" fill="url(#planetaHorno)"/>${Array.from({ length: 9 }, (_, i) => `<path d="M0 0 L ${Math.cos(i * 0.7) * 330} ${Math.sin(i * 0.7) * 330}" stroke="#ffef9a" stroke-width="${6 * k}" opacity="${k}"/>`).join("")}
    <circle r="${600 * k}" fill="rgba(255,240,180,${0.8 * k * (1 - k)})"/></g>`;
  return s;
}
// Cuartel de la Liga: mesa redonda con el emblema de Orbi
function cuartel(t, o = {}) {
  let s = taller(t, o);
  s += `<g transform="translate(540 1420)"><ellipse rx="420" ry="90" fill="#1a2232" stroke="#5fc9f1" stroke-width="6"/><ellipse rx="160" ry="34" fill="rgba(95,201,241,.25)"/>
    <text y="12" text-anchor="middle" font-family="Figtree" font-weight="900" font-size="40" fill="#bff6ff">LA LIGA</text></g>`;
  return s;
}
Object.assign(FONDOS, { espacio, cuartel });
function dibujaExtra(a, st, t, h, b) {
  if (a.tipo === "fruta") return heroeFruta(st.props.fruta, { ...st.props, cara: st.cara ?? st.props.cara, boca: b, t });
  if (a.tipo === "lord") return lordComision({ ...st.props, cara: st.cara, boca: b, t });
  return "";
}
