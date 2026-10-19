// Personajes de comida de «Orbi en la cocina» (Arepanovelas y compañía). Todo en SVG para animarlo.
// comida(tipo, o) dibuja el personaje centrado en el cuerpo, con los pies en y = +170.
// o = {cara, boca (0-1 hablando), acc: [rulos, bigote, gafas, corbatin, aretes, corona, fantasma, banda], banda, brazo, t, mira}
const FORMA = {
  //            ancho, arriba, cara, abajo
  arepa:       [150, -125, -10, 120],
  chorizo:     [85, -170, -60, 150],
  empanada:    [150, -95, 5, 60],
  tinto:       [110, -130, 10, 130],
  hamburguesa: [160, -165, -100, 100],
  pan:         [150, -165, 0, 110],
  papa:        [125, -150, -20, 145],
  aguacate:    [115, -195, -55, 150],
};
function ojos(o) {
  const c = o.cara || "normal", s = o.mira || 0, t = o.t || 0;
  let ap = { normal: 1, feliz: -1, triste: 0.7, enojo: 0.65, shock: 1.35, llanto: 0.45, diva: 0.5, orgullo: 0.5, nervioso: 1.15, guino: 1 }[c] ?? 1;
  if (ap > 0 && (t + (o.fase || 0)) % 3.1 < 0.11) ap = 0.08; // parpadeo
  const uno = (cx, lado) => {
    if (ap < 0 || (c === "guino" && lado > 0)) return `<path d="M${cx - 20} ${4} Q ${cx} -16 ${cx + 20} 4" fill="none" stroke="#2a160c" stroke-width="8" stroke-linecap="round"/>`;
    const pest = c === "diva" || o.pestanas ? [-16, -6, 4, 14].map((x) => `<line x1="${cx + x}" y1="${-26 * ap}" x2="${cx + x * 1.3}" y2="${-26 * ap - 13}" stroke="#2a160c" stroke-width="4" stroke-linecap="round"/>`).join("") : "";
    return `<ellipse cx="${cx}" cy="0" rx="20" ry="${26 * ap}" fill="#fff" stroke="#2a160c" stroke-width="4"/>
      <ellipse cx="${cx + s * 4}" cy="${3 * Math.min(1, ap)}" rx="9" ry="${Math.max(1, 12 * Math.min(1, ap))}" fill="#2a160c"/><circle cx="${cx + s * 4 + 4}" cy="-4" r="3" fill="#fff" opacity="${ap > 0.3 ? 1 : 0}"/>${pest}`;
  };
  const cejas = {
    enojo: `<path d="M-60 -40 L -18 -26 M18 -26 L 60 -40" stroke="#2a160c" stroke-width="9" stroke-linecap="round"/>`,
    triste: `<path d="M-60 -30 L -20 -42 M20 -42 L 60 -30" stroke="#2a160c" stroke-width="8" stroke-linecap="round"/>`,
    llanto: `<path d="M-60 -26 L -20 -40 M20 -40 L 60 -26" stroke="#2a160c" stroke-width="8" stroke-linecap="round"/>`,
    shock: `<path d="M-58 -58 Q -38 -70 -18 -58 M18 -58 Q 38 -70 58 -58" stroke="#2a160c" stroke-width="7" fill="none" stroke-linecap="round"/>`,
    diva: `<path d="M-62 -40 Q -40 -60 -16 -40 M16 -40 Q 40 -60 62 -40" stroke="#2a160c" stroke-width="7" fill="none" stroke-linecap="round"/>`,
    orgullo: `<path d="M-60 -46 Q -40 -54 -18 -46 M18 -50 Q 40 -60 60 -52" stroke="#2a160c" stroke-width="7" fill="none" stroke-linecap="round"/>`,
    nervioso: `<path d="M-60 -40 Q -40 -48 -20 -42 M20 -42 Q 40 -48 60 -40" stroke="#2a160c" stroke-width="7" fill="none" stroke-linecap="round"/>`,
  }[c] || `<path d="M-58 -42 Q -38 -50 -18 -42 M18 -42 Q 38 -50 58 -42" stroke="#2a160c" stroke-width="7" fill="none" stroke-linecap="round"/>`;
  return uno(-38, -1) + uno(38, 1) + cejas;
}
function boca(o, y = 46) {
  const c = o.cara || "normal", h = o.boca || 0;
  if (h > 0.05) return `<ellipse cx="0" cy="${y}" rx="${18 + 6 * h}" ry="${6 + 20 * h}" fill="#5a1414" stroke="#2a160c" stroke-width="5"/><ellipse cx="0" cy="${y + 4 + 10 * h}" rx="${10 + 3 * h}" ry="${3 + 5 * h}" fill="#ff7b8a"/>`;
  if (c === "shock") return `<ellipse cx="0" cy="${y + 4}" rx="16" ry="20" fill="#5a1414" stroke="#2a160c" stroke-width="5"/>`;
  if (c === "triste" || c === "llanto" || c === "enojo") return `<path d="M-24 ${y + 12} Q 0 ${y - 8} 24 ${y + 12}" stroke="#2a160c" stroke-width="7" fill="none" stroke-linecap="round"/>`;
  if (c === "nervioso") return `<path d="M-26 ${y} q 6.5 -8 13 0 t 13 0 t 13 0 t 13 0" stroke="#2a160c" stroke-width="6" fill="none" stroke-linecap="round"/>`;
  if (c === "feliz" || c === "diva" || c === "guino") return `<path d="M-30 ${y - 4} Q 0 ${y + 34} 30 ${y - 4} Z" fill="#5a1414" stroke="#2a160c" stroke-width="5" stroke-linejoin="round"/>`;
  if (c === "orgullo") return `<path d="M-26 ${y + 2} Q 4 ${y + 18} 28 ${y - 6}" stroke="#2a160c" stroke-width="7" fill="none" stroke-linecap="round"/>`;
  return `<path d="M-22 ${y} Q 0 ${y + 16} 22 ${y}" stroke="#2a160c" stroke-width="7" fill="none" stroke-linecap="round"/>`;
}
function extrasCara(o) {
  const c = o.cara || "normal", t = o.t || 0; let s = "";
  if (["feliz", "diva", "guino"].includes(c)) s += `<ellipse cx="-66" cy="32" rx="18" ry="10" fill="#ff7b8a" opacity=".55"/><ellipse cx="66" cy="32" rx="18" ry="10" fill="#ff7b8a" opacity=".55"/>`;
  if (c === "llanto") { const k = (t * 1.6) % 1; s += `<path d="M-40 20 Q -46 70 -40 ${90 + 60 * k}" stroke="#7fd7ff" stroke-width="12" fill="none" opacity=".85" stroke-linecap="round"/><path d="M40 20 Q 46 70 40 ${90 + 60 * k}" stroke="#7fd7ff" stroke-width="12" fill="none" opacity=".85" stroke-linecap="round"/>`; }
  if (c === "nervioso" || c === "shock") s += `<path d="M72 -60 q 10 16 0 26 q -10 -10 0 -26Z" fill="#7fd7ff"/>`;
  return s;
}
function brazos(bw, pose, color, t) {
  const p = { abajo: [[-bw - 34, 80], [bw + 34, 80]], arriba: [[-bw - 34, 80], [bw + 50, -100]], cabeza: [[-bw + 6, -120], [bw - 6, -120]],
    jarra: [[-bw + 4, 66], [bw - 4, 66]], dos: [[-bw - 60, -90], [bw + 60, -90]], saluda: [[-bw - 34, 80], [bw + 60 + 14 * Math.sin(t * 12), -90]] }[pose || "abajo"] || [[-bw - 34, 80], [bw + 34, 80]];
  const codo = pose === "jarra" ? [[-bw - 60, 30], [bw + 60, 30]] : [[-bw - 30, 10], [bw + 30, 10]];
  return p.map(([x, y], i) => `<path d="M${i ? bw - 8 : -bw + 8} 10 Q ${codo[i][0]} ${codo[i][1]} ${x} ${y}" stroke="${color}" stroke-width="13" fill="none" stroke-linecap="round"/><circle cx="${x}" cy="${y}" r="17" fill="#fff" stroke="${color}" stroke-width="5"/>`).join("");
}
function piernas(abajo, color) {
  return [-1, 1].map((s) => `<path d="M${s * 42} ${abajo - 8} L ${s * 48} 158" stroke="${color}" stroke-width="13" stroke-linecap="round"/><ellipse cx="${s * 62}" cy="164" rx="32" ry="15" fill="#2a160c"/>`).join("");
}
function cuerpo(tipo, t) {
  switch (tipo) {
    case "arepa": return `<ellipse cx="0" cy="0" rx="150" ry="125" fill="#f0cf86" stroke="#b98a3e" stroke-width="7"/>
      ${[[-90, -60, 14], [70, -78, 10], [100, 30, 16], [-100, 50, 11], [10, 85, 13], [-30, -95, 8]].map(([x, y, r]) => `<circle cx="${x}" cy="${y}" r="${r}" fill="#c98f3f" opacity=".7"/>`).join("")}
      ${[-70, -20, 30, 80].map((x) => `<line x1="${x - 40}" y1="-100" x2="${x + 40}" y2="100" stroke="#a8742c" stroke-width="7" opacity=".35"/>`).join("")}`;
    case "chorizo": return `<rect x="-85" y="-170" width="170" height="320" rx="85" fill="#b8432c" stroke="#7f2a1a" stroke-width="7"/>
      <rect x="-60" y="-140" width="26" height="200" rx="13" fill="rgba(255,255,255,.18)"/>
      ${[[-40, -10], [35, 40], [-20, 90], [45, -100]].map(([x, y]) => `<ellipse cx="${x}" cy="${y}" rx="12" ry="8" fill="#f0d0b0" opacity=".55"/>`).join("")}
      <path d="M0 -168 q -10 -20 0 -34 q 10 -14 0 -26" stroke="#d9c49a" stroke-width="7" fill="none" stroke-linecap="round"/>`;
    case "empanada": return `<path d="M-160 60 A 160 155 0 0 1 160 60 Z" fill="#e7a94e" stroke="#b5762b" stroke-width="7" stroke-linejoin="round"/>
      ${Array.from({ length: 11 }, (_, i) => { const a = Math.PI + (i / 10) * Math.PI, x = Math.cos(a) * 150, y = 60 + Math.sin(a) * 145; return `<circle cx="${x}" cy="${y}" r="17" fill="#d99540" stroke="#b5762b" stroke-width="5"/>`; }).join("")}
      ${[[-80, 30], [60, 10], [10, -50]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="7" fill="#b5762b" opacity=".6"/>`).join("")}`;
    case "tinto": return `${[-40, 0, 40].map((x, i) => `<path d="M${x} -150 q 16 -22 0 -44 q -16 -22 0 -44" stroke="rgba(255,255,255,${0.35 + 0.15 * Math.sin(t * 3 + i)})" stroke-width="9" fill="none" stroke-linecap="round" transform="translate(${6 * Math.sin(t * 2 + i)} 0)"/>`).join("")}
      <path d="M108 -60 q 70 0 70 60 q 0 60 -70 60" stroke="#efe9df" stroke-width="26" fill="none"/>
      <path d="M-112 -128 L 112 -128 L 98 130 Q 0 150 -98 130 Z" fill="#f7f3ec" stroke="#c9bfae" stroke-width="7" stroke-linejoin="round"/>
      <ellipse cx="0" cy="-128" rx="112" ry="26" fill="#efe9df" stroke="#c9bfae" stroke-width="7"/><ellipse cx="0" cy="-126" rx="94" ry="18" fill="#4a2a17"/>
      <rect x="-80" y="80" width="160" height="16" rx="8" fill="#c0392b" opacity=".8"/>`;
    case "hamburguesa": return `<path d="M-160 70 Q -160 110 0 112 Q 160 110 160 70 L 160 52 L -160 52 Z" fill="#d9903c" stroke="#9e6224" stroke-width="7"/>
      <rect x="-165" y="0" width="330" height="58" rx="28" fill="#6b3a1f" stroke="#43230f" stroke-width="7"/>
      <path d="M-170 -4 L 170 -4 L 130 30 L 90 -4 L 40 34 L 0 -4 L -50 30 L -100 -4 L -140 26 Z" fill="#f4c430" stroke="#c99a10" stroke-width="5" stroke-linejoin="round"/>
      <path d="M-175 -20 q 22 26 44 0 t 44 0 t 44 0 t 44 0 t 44 0 t 44 0 t 44 0 t 44 0" fill="#7cc142" stroke="#4e8a22" stroke-width="7"/>
      <path d="M-165 -20 Q -165 -170 0 -172 Q 165 -170 165 -20 Z" fill="#e3a043" stroke="#9e6224" stroke-width="7"/>
      ${[[-90, -140], [-30, -158], [40, -150], [100, -128], [-120, -90], [130, -80]].map(([x, y]) => `<ellipse cx="${x}" cy="${y}" rx="10" ry="5" fill="#fff4d8" transform="rotate(${x % 40} ${x} ${y})"/>`).join("")}`;
    case "pan": return `<path d="M-130 110 L -130 -40 Q -175 -60 -165 -110 Q -150 -165 -70 -160 Q 0 -190 70 -160 Q 150 -165 165 -110 Q 175 -60 130 -40 L 130 110 Z" fill="#b8712f" stroke="#7a4517" stroke-width="7" stroke-linejoin="round"/>
      <path d="M-108 92 L -108 -52 Q -148 -66 -142 -104 Q -130 -140 -66 -136 Q 0 -164 66 -136 Q 130 -140 142 -104 Q 148 -66 108 -52 L 108 92 Z" fill="#f6e3b4"/>
      ${Array.from({ length: 14 }, (_, i) => `<circle cx="${-90 + (i * 47) % 180}" cy="${-110 + (i * 31) % 190}" r="3.5" fill="#d9bf86"/>`).join("")}`;
    case "papa": return `<path d="M-120 -40 Q -140 -150 -10 -150 Q 120 -155 128 -30 Q 140 90 60 140 Q -40 165 -110 110 Q -150 60 -120 -40 Z" fill="#c9a06a" stroke="#8a6436" stroke-width="7"/>
      ${[[-80, -100], [70, -110], [90, 80], [-80, 90], [100, -10]].map(([x, y]) => `<ellipse cx="${x}" cy="${y}" rx="9" ry="6" fill="#8a6436" opacity=".6"/>`).join("")}`;
    case "aguacate": return `<path d="M0 -195 Q 70 -195 85 -90 Q 150 10 120 90 Q 80 155 0 155 Q -80 155 -120 90 Q -150 10 -85 -90 Q -70 -195 0 -195 Z" fill="#3e6b22" stroke="#25440f" stroke-width="7"/>
      <path d="M0 -168 Q 52 -168 64 -84 Q 120 6 96 80 Q 66 130 0 130 Q -66 130 -96 80 Q -120 6 -64 -84 Q -52 -168 0 -168 Z" fill="#d8e59a"/>
      <circle cx="0" cy="62" r="46" fill="#8a5a2b" stroke="#5e3a17" stroke-width="5"/><ellipse cx="-14" cy="48" rx="12" ry="8" fill="rgba(255,255,255,.3)"/>`;
  }
  return "";
}
function accesorios(tipo, o) {
  const [bw, arriba, fy] = FORMA[tipo], acc = o.acc || [], t = o.t || 0; let s = "";
  if (acc.includes("rulos")) s += [-70, 0, 70].map((x, i) => `<g transform="translate(${x} ${arriba + 4 - (i === 1 ? 10 : 0)}) rotate(${(i - 1) * 18})"><rect x="-22" y="-26" width="44" height="50" rx="14" fill="#ff8fc7" stroke="#d14f96" stroke-width="5"/>${[-12, 0, 12].map((y) => `<line x1="-22" y1="${y}" x2="22" y2="${y}" stroke="#d14f96" stroke-width="3"/>`).join("")}</g>`).join("");
  if (acc.includes("bigote")) s += `<path d="M0 ${fy + 28} Q -30 ${fy + 12} -60 ${fy + 30} Q -70 ${fy + 44} -54 ${fy + 40} Q -30 ${fy + 34} 0 ${fy + 38} Q 30 ${fy + 34} 54 ${fy + 40} Q 70 ${fy + 44} 60 ${fy + 30} Q 30 ${fy + 12} 0 ${fy + 28}Z" fill="#2a160c"/>`;
  if (acc.includes("gafas")) s += `<g transform="translate(0 ${fy})"><circle cx="-38" cy="0" r="30" fill="rgba(200,230,255,.15)" stroke="#2a160c" stroke-width="6"/><circle cx="38" cy="0" r="30" fill="rgba(200,230,255,.15)" stroke="#2a160c" stroke-width="6"/><line x1="-8" y1="-2" x2="8" y2="-2" stroke="#2a160c" stroke-width="6"/></g>`;
  if (acc.includes("aretes")) s += `<circle cx="${-bw + 6}" cy="${fy + 30}" r="14" fill="none" stroke="#f4c430" stroke-width="7"/><circle cx="${bw - 6}" cy="${fy + 30}" r="14" fill="none" stroke="#f4c430" stroke-width="7"/>`;
  if (acc.includes("corbatin")) s += `<g transform="translate(0 ${fy + 92})"><path d="M0 0 L -34 -18 L -34 18 Z M0 0 L 34 -18 L 34 18 Z" fill="#c0392b" stroke="#7a1f16" stroke-width="4"/><circle r="8" fill="#7a1f16"/></g>`;
  if (acc.includes("banda")) s += `<g><path d="M${-bw + 10} ${fy - 50} L ${bw - 10} ${fy + 110} L ${bw - 40} ${fy + 140} L ${-bw - 10} ${fy - 20} Z" fill="#fff" stroke="#c9a227" stroke-width="5" opacity=".95"/>
    <text x="0" y="${fy + 55}" text-anchor="middle" font-size="24" font-weight="800" fill="#b5179e" font-family="Figtree" transform="rotate(${Math.atan2(160, 2 * bw - 20) * 57.3} 0 ${fy + 45})">${o.banda || "SEÑORITA"}</text></g>`;
  if (acc.includes("corona")) s += `<g transform="translate(0 ${arriba - 6})"><path d="M-54 0 L -54 -50 L -27 -24 L 0 -62 L 27 -24 L 54 -50 L 54 0 Z" fill="#f4c430" stroke="#c99a10" stroke-width="5"/><circle cx="0" cy="-20" r="8" fill="#e83f6f"/></g>`;
  if (acc.includes("sombrero")) s += `<g transform="translate(0 ${arriba + 6})"><ellipse rx="120" ry="24" fill="#f3ead2" stroke="#2a160c" stroke-width="5"/><path d="M-62 -6 Q -60 -78 0 -80 Q 60 -78 62 -6 Z" fill="#f3ead2" stroke="#2a160c" stroke-width="5"/>${[-40, -20, 0, 20, 40].map((x) => `<line x1="${x}" y1="-70" x2="${x * 1.2}" y2="-8" stroke="#2a160c" stroke-width="5"/>`).join("")}</g>`;
  return s;
}
function fantasma(tipo, o) {
  const [bw, arriba] = FORMA[tipo], t = o.t || 0, w = bw + 50, top = arriba - 60;
  const seg = 2 * w / 7, borde = Array.from({ length: 7 }, (_, i) => `Q ${w - (i + 0.5) * seg} ${205 + 18 * Math.sin(t * 6 + i)} ${w - (i + 1) * seg} 170`).join(" ");
  return `<path d="M${-w} 170 L ${-w} ${top + 120} Q ${-w} ${top} 0 ${top} Q ${w} ${top} ${w} ${top + 120} L ${w} 170 ${borde} Z" fill="#f6f7fb" stroke="#c9ccd8" stroke-width="6"/>
    <ellipse cx="-40" cy="${top + 110}" rx="20" ry="30" fill="#14141c"/><ellipse cx="40" cy="${top + 110}" rx="20" ry="30" fill="#14141c"/>
    <ellipse cx="0" cy="${top + 180}" rx="${22 + 10 * (o.boca || 0)}" ry="${14 + 22 * (o.boca || 0)}" fill="#14141c"/>
    <text x="0" y="${top + 270}" text-anchor="middle" font-size="64" font-weight="900" fill="#e01e3c" font-family="Figtree">27 %</text>`;
}
function comida(tipo, o = {}) {
  const [bw, arriba, fy, abajo] = FORMA[tipo], t = o.t || 0, acc = o.acc || [];
  const tinta = { arepa: "#8a5a1e", chorizo: "#5e1d10", empanada: "#8a5a1e", tinto: "#6b625a", hamburguesa: "#6b3a1f", pan: "#6b3c14", papa: "#6b4c26", aguacate: "#25440f" }[tipo];
  if (acc.includes("fantasma")) return `<g>${piernas(abajo, tinta)}${fantasma(tipo, o)}</g>`;
  const cara = `<g transform="translate(0 ${fy}) scale(${tipo === "hamburguesa" ? 0.85 : 1})">${ojos(o)}${boca(o)}${extrasCara(o)}</g>`;
  return `<g>${piernas(abajo, tinta)}${brazos(bw, o.brazo, tinta, t)}${cuerpo(tipo, t)}${cara}${accesorios(tipo, o)}</g>`;
}
