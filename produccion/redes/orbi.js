// Orbi, el mesero virtual de Apex. orbi(expresion, opciones) → SVG. Todo vectorial para poder animarlo.
const EXPRESIONES = {
  //            ojoIzq/ojoDer: apertura 0-1.2 · cejas: [altura, ángulo] · boca: [curva, ancho, abierta] · mirada: [x, y]
  normal:     { oi: 1,   od: 1,   ci: [0, 0],    cd: [0, 0],    boca: [0.35, 1, 0],   mira: [0, 0] },
  feliz:      { oi: -1,  od: -1,  ci: [-4, 0],   cd: [-4, 0],   boca: [0.9, 1.25, 0.5], mira: [0, 0] },
  sarcastico: { oi: 0.45, od: 1,  ci: [2, -8],   cd: [-10, 14], boca: [0.25, 0.9, 0], mira: [6, 0], ladeo: 1 },
  sorprendido:{ oi: 1.25, od: 1.25, ci: [-14, 0], cd: [-14, 0], boca: [0, 0.45, 1],   mira: [0, 0] },
  triste:     { oi: 0.75, od: 0.75, ci: [-4, -18], cd: [-4, 18], boca: [-0.55, 0.8, 0], mira: [0, 6] },
  enojado:    { oi: 0.6, od: 0.6, ci: [6, 22],  cd: [6, -22],   boca: [-0.3, 0.8, 0],  mira: [0, 0] },
  guino:      { oi: 1,   od: -1,  ci: [-3, 0],   cd: [2, 0],    boca: [0.7, 1.1, 0],   mira: [-4, 0] },
  orgulloso:  { oi: 0.5, od: 0.5, ci: [-6, -6],  cd: [-6, 6],   boca: [0.6, 1.1, 0],   mira: [0, -4], ladeo: -1 },
};
function orbi(nombre = "normal", o = {}) {
  const e = { ...EXPRESIONES[nombre] || EXPRESIONES.normal, ...(o.e || {}) };
  const id = "o" + Math.random().toString(36).slice(2, 7), anillo = o.anillo ?? -10, brillo = o.brillo ?? 1;
  const ojo = (cx, ap, mx, my) => ap < 0
    ? `<path d="M${cx - 17} 186 Q ${cx} ${166} ${cx + 17} 186" fill="none" stroke="#f4fbff" stroke-width="9" stroke-linecap="round"/>`
    : `<ellipse cx="${cx}" cy="182" rx="17" ry="${26 * ap}" fill="#f4fbff"/>
       <ellipse cx="${cx + mx}" cy="${184 + my}" rx="9" ry="${Math.min(13, 15 * ap)}" fill="#071a33"/>
       <circle cx="${cx + mx + 4}" cy="${178 + my}" r="3.5" fill="#fff"/>`;
  const ceja = (cx, [h, a], lado) => `<path d="M${cx - 18} ${148 + h} Q ${cx} ${144 + h} ${cx + 18} ${148 + h}" transform="rotate(${a} ${cx} ${146 + h})" fill="none" stroke="#e6f7ff" stroke-width="8" stroke-linecap="round"/>`;
  const [cu, an, ab] = e.boca, w = 34 * an, y = 238, l = (e.ladeo || 0) * 6;
  const boca = ab > 0 && cu > 0.5
    ? `<path d="M${200 - w} ${y - 6} Q 200 ${y + 64 * cu} ${200 + w} ${y - 6} Z" fill="#071a33" stroke="#071a33" stroke-width="6" stroke-linejoin="round"/><ellipse cx="200" cy="${y + 22 * cu}" rx="${w * 0.4}" ry="${8 * cu}" fill="#ff7b8a"/>`
    : ab > 0
    ? `<ellipse cx="200" cy="${y + 4}" rx="${w * 0.6}" ry="${14 * ab + 4}" fill="#071a33"/><ellipse cx="200" cy="${y + 10 + 6 * ab}" rx="${w * 0.35}" ry="${5 * ab}" fill="#ff7b8a"/>`
    : `<path d="M${200 - w} ${y + l} Q 200 ${y + 26 * cu} ${200 + w} ${y - l}" fill="none" stroke="#071a33" stroke-width="8" stroke-linecap="round"/>`;
  return `<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="${id}e" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#effbff"/><stop offset=".12" stop-color="#7fe0ff"/><stop offset=".38" stop-color="#2fbbe8"/><stop offset=".75" stop-color="#0c4a9b"/><stop offset="1" stop-color="#061a3d"/></radialGradient>
    <radialGradient id="${id}h" cx="50%" cy="50%" r="50%"><stop offset=".55" stop-color="rgba(47,187,232,.45)"/><stop offset="1" stop-color="rgba(47,187,232,0)"/></radialGradient>
  </defs>
  <circle cx="200" cy="200" r="190" fill="url(#${id}h)" opacity="${brillo}"/>
  <g transform="rotate(${anillo} 200 272)"><path d="M46 272 A 154 30 0 0 1 354 272" fill="none" stroke="rgba(170,232,255,.75)" stroke-width="6"/></g>
  <circle cx="200" cy="200" r="122" fill="url(#${id}e)"/>
  <ellipse cx="132" cy="122" rx="26" ry="14" fill="rgba(255,255,255,.22)" transform="rotate(-35 132 122)"/>
  ${ojo(160, e.oi, ...e.mira)}${ojo(240, e.od, ...e.mira)}
  ${ceja(160, e.ci)}${ceja(240, e.cd)}
  ${boca}
  <g transform="rotate(${anillo} 200 272)"><path d="M46 272 A 154 30 0 0 0 354 272" fill="none" stroke="rgba(190,240,255,.95)" stroke-width="6"/></g>
  <g transform="translate(200 334)"><path d="M0 0 L-40 -18 L-40 18 Z M0 0 L40 -18 L40 18 Z" fill="#0b1626" stroke="#2fbbe8" stroke-width="3" stroke-linejoin="round"/><circle r="9" fill="#2fbbe8"/></g>
</svg>`;
}
if (typeof module !== "undefined") module.exports = { orbi, EXPRESIONES };
