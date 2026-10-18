// Fotos de perfil de Apex: Saturno + A. Cada función devuelve un SVG 1000x1000 (zona segura: círculo de radio 470).
const fondo = (id, a = "#123a63", b = "#050a14") => `<defs><radialGradient id="${id}f" cx="50%" cy="42%" r="70%"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></radialGradient></defs>
  <rect width="1000" height="1000" fill="url(#${id}f)"/>${Array.from({ length: 70 }, (_, i) => { const r = Math.sin(i * 91.7) * 43758.5; const x = (r - Math.floor(r)) * 1000, y = ((r * 7) - Math.floor(r * 7)) * 1000;
  return `<circle cx="${x}" cy="${y}" r="${1 + (i % 3)}" fill="#fff" opacity="${0.15 + (i % 5) * 0.08}"/>`; }).join("")}`;
const esfera = (id, c = ["#effbff", "#7fe0ff", "#2fbbe8", "#0c4a9b", "#061a3d"]) => `<radialGradient id="${id}" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="${c[0]}"/><stop offset=".15" stop-color="${c[1]}"/><stop offset=".42" stop-color="${c[2]}"/><stop offset=".8" stop-color="${c[3]}"/><stop offset="1" stop-color="${c[4]}"/></radialGradient>`;
// 1 · Tejido: el anillo de Saturno es la barra de la A y se entrelaza con sus patas
function tejido() {
  const A = `<path d="M500 130 L 150 870 M500 130 L 850 870" stroke="url(#t-a)" stroke-width="120" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`;
  const anillo = (lado) => `<g transform="rotate(-14 500 560)"><path d="M150 560 A 350 80 0 0 ${lado} 850 560" fill="none" stroke="url(#t-r)" stroke-width="30" stroke-linecap="round"/></g>`;
  return `<svg viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg">${fondo("t")}
  <defs>${esfera("t-s")}<linearGradient id="t-a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#9fe6ff"/></linearGradient>
  <linearGradient id="t-r" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffd27a"/><stop offset=".5" stop-color="#fff2c9"/><stop offset="1" stop-color="#ffb347"/></linearGradient>
  <clipPath id="t-izq"><rect x="0" y="0" width="500" height="1000"/></clipPath><clipPath id="t-der"><rect x="500" y="0" width="500" height="1000"/></clipPath></defs>
  <g transform="translate(60 40) scale(.88)">${anillo(1)}
  <circle cx="500" cy="545" r="150" fill="rgba(47,187,232,.15)"/><circle cx="500" cy="545" r="98" fill="url(#t-s)"/>
  <g clip-path="url(#t-der)">${anillo(0)}</g>
  ${A}
  <g clip-path="url(#t-izq)">${anillo(0)}</g></g>
  </svg>`;
}
// 2 · Tallado: un planeta con la A recortada; el anillo le pone la barra
function tallado() {
  return `<svg viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg">${fondo("c", "#0e2f52")}
  <defs>${esfera("c-s")}<mask id="c-m"><rect width="1000" height="1000" fill="#fff"/>
    <path d="M500 300 L 330 700 L 400 700 L 500 455 L 600 700 L 670 700 Z" fill="#000"/></mask>
    <linearGradient id="c-r" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="rgba(170,232,255,.2)"/><stop offset=".5" stop-color="#e6f9ff"/><stop offset="1" stop-color="rgba(170,232,255,.2)"/></linearGradient></defs>
  <circle cx="500" cy="500" r="340" fill="rgba(47,187,232,.12)"/>
  <g transform="rotate(-16 500 520)"><path d="M90 520 A 410 92 0 0 1 910 520" fill="none" stroke="url(#c-r)" stroke-width="22"/></g>
  <circle cx="500" cy="500" r="270" fill="url(#c-s)" mask="url(#c-m)"/>
  <g transform="rotate(-16 500 520)"><path d="M90 520 A 410 92 0 0 0 910 520" fill="none" stroke="url(#c-r)" stroke-width="22"/></g>
  </svg>`;
}
// 3 · Monolínea: una A fina y, en lugar de la barra, un Saturno pequeño
function monolinea() {
  return `<svg viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg">${fondo("m", "#0b1626", "#03060c")}
  <defs>${esfera("m-s")}</defs>
  <path d="M500 150 L 210 840 M500 150 L 790 840" stroke="#f4fbff" stroke-width="64" stroke-linecap="round" fill="none"/>
  <circle cx="500" cy="590" r="150" fill="rgba(47,187,232,.18)"/>
  <g transform="rotate(-12 500 600)"><path d="M300 600 A 200 44 0 0 1 700 600" fill="none" stroke="#9fe6ff" stroke-width="18"/></g>
  <circle cx="500" cy="590" r="92" fill="url(#m-s)"/>
  <g transform="rotate(-12 500 600)"><path d="M300 600 A 200 44 0 0 0 700 600" fill="none" stroke="#e6f9ff" stroke-width="18"/></g>
  </svg>`;
}
// 4 · Cometa: Saturno es la punta de la A y sus estelas dibujan las patas
function cometa() {
  return `<svg viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg">${fondo("k", "#1a1240", "#05040f")}
  <defs>${esfera("k-s", ["#fff8e6", "#ffd27a", "#ff9a3c", "#b0364f", "#2a0d2e"])}
    <linearGradient id="k-l" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd27a"/><stop offset="1" stop-color="rgba(255,120,80,0)"/></linearGradient>
    <linearGradient id="k-d" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fe6ff"/><stop offset="1" stop-color="rgba(47,187,232,0)"/></linearGradient></defs>
  <path d="M470 330 L 200 880 L 300 880 L 500 400Z" fill="url(#k-l)"/><path d="M530 330 L 800 880 L 700 880 L 500 400Z" fill="url(#k-d)"/>
  <path d="M330 660 Q 500 610 670 660" fill="none" stroke="#fff2c9" stroke-width="16" stroke-linecap="round" stroke-dasharray="2 34"/>
  <circle cx="500" cy="300" r="190" fill="rgba(255,190,110,.12)"/>
  <g transform="rotate(-18 500 300)"><path d="M290 300 A 210 46 0 0 1 710 300" fill="none" stroke="#ffe3a8" stroke-width="16"/></g>
  <circle cx="500" cy="300" r="120" fill="url(#k-s)"/>
  <g transform="rotate(-18 500 300)"><path d="M290 300 A 210 46 0 0 0 710 300" fill="none" stroke="#fff4d6" stroke-width="16"/></g>
  </svg>`;
}
