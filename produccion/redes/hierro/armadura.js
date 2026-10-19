// Armadura de Orbi (rojo y oro, reactor en el pecho). Coordenadas: Orbi centrado en (0,0), radio ~116.
// o = { torso, hombros, casco, visor (0 abierto → 1 cerrado), reactor (0-1), fuego (0-1), t }
const ARMA_DEFS = `<defs>
  <linearGradient id="rojoMetal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e8333a"/><stop offset=".45" stop-color="#a4141b"/><stop offset=".7" stop-color="#6d0a10"/><stop offset="1" stop-color="#c22128"/></linearGradient>
  <radialGradient id="cascoMetal" cx="34%" cy="28%" r="80%"><stop offset="0" stop-color="#ff8a8a"/><stop offset=".18" stop-color="#e3262e"/><stop offset=".6" stop-color="#8e0d14"/><stop offset="1" stop-color="#3e0408"/></radialGradient>
  <linearGradient id="oroMetal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff1b8"/><stop offset=".3" stop-color="#e6b54a"/><stop offset=".65" stop-color="#a8761c"/><stop offset="1" stop-color="#f3cf6a"/></linearGradient>
  <radialGradient id="reactor"><stop offset="0" stop-color="#ffffff"/><stop offset=".35" stop-color="#bff6ff"/><stop offset=".7" stop-color="#36c9ff"/><stop offset="1" stop-color="rgba(54,201,255,0)"/></radialGradient>
  <linearGradient id="fuego" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".25" stop-color="#bff6ff"/><stop offset=".6" stop-color="#36a9ff"/><stop offset="1" stop-color="rgba(40,120,255,0)"/></linearGradient>
  <filter id="brillo" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="halo" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="22"/></filter>
</defs>`;
const CARA = "M-80 -72 Q 0 -100 80 -72 L 74 48 Q 0 96 -74 48 Z";
function armadura(svgOrbi, o = {}) {
  const t = o.t || 0, cl = (x) => Math.min(1, Math.max(0, x));
  const pz = (k, dx, dy) => { const p = cl(o[k] ?? 1), q = 1 - Math.pow(1 - p, 3); return { tr: `translate(${dx * (1 - q)} ${dy * (1 - q)})`, op: p > 0 ? 1 : 0 }; };
  const T = pz("torso", 0, 700), H = pz("hombros", 0, 0), C = pz("casco", 0, -700), v = cl(o.visor ?? 1), R = cl(o.reactor ?? 1), F = cl(o.fuego || 0);
  const hIzq = `translate(${-520 * (1 - Math.pow(1 - cl(o.hombros ?? 1), 3))} 0)`, hDer = `translate(${520 * (1 - Math.pow(1 - cl(o.hombros ?? 1), 3))} 0)`;
  let s = "";
  // propulsor
  if (F > 0) s += `<g opacity="${F}"><ellipse cx="0" cy="${330 + 120 * F}" rx="${70 + 10 * Math.sin(t * 40)}" ry="${180 * F}" fill="url(#fuego)" filter="url(#brillo)"/><ellipse cx="0" cy="300" rx="90" ry="40" fill="#bff6ff" filter="url(#halo)"/></g>`;
  // torso
  s += `<g transform="${T.tr}" opacity="${T.op}">
    <path d="M-150 270 Q -176 140 -104 82 L 104 82 Q 176 140 150 270 Q 0 306 -150 270Z" fill="url(#rojoMetal)"/>
    <path d="M-96 230 L -40 214 L -40 276 Q -80 278 -110 270Z M96 230 L 40 214 L 40 276 Q 80 278 110 270Z" fill="url(#oroMetal)"/>
    <path d="M-30 210 L 30 210 L 26 284 L -26 284Z" fill="url(#oroMetal)"/><path d="M-30 236 L 30 236 M -28 260 L 28 260" stroke="#7a5212" stroke-width="3"/>
    <path d="M-104 82 Q -60 130 0 132 Q 60 130 104 82" fill="none" stroke="#3e0408" stroke-width="5"/>
    <circle cx="0" cy="164" r="34" fill="#2b2f36" stroke="#9aa3ad" stroke-width="5"/>
    <circle cx="0" cy="164" r="${26 + 2 * Math.sin(t * 6)}" fill="url(#reactor)" opacity="${R}" filter="url(#brillo)"/>
    <circle cx="0" cy="164" r="70" fill="#36c9ff" opacity="${0.35 * R}" filter="url(#halo)"/>
    ${[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => `<line x1="0" y1="140" x2="0" y2="146" stroke="#e8fbff" stroke-width="3" opacity="${R}" transform="rotate(${i * 36} 0 164)"/>`).join("")}
  </g>`;
  // hombros
  s += `<g opacity="${H.op}"><g transform="${hIzq}"><path d="M-104 84 Q -190 70 -196 160 Q -160 150 -122 170 Q -120 120 -104 84Z" fill="url(#oroMetal)"/></g>
    <g transform="${hDer}"><path d="M104 84 Q 190 70 196 160 Q 160 150 122 170 Q 120 120 104 84Z" fill="url(#oroMetal)"/></g></g>`;
  // Orbi
  s += `<g transform="translate(-190 -190)">${svgOrbi}</g>`;
  // casco con hueco para la cara
  s += `<g transform="${C.tr}" opacity="${C.op}"><path d="M0 -126 A 126 126 0 1 1 -0.1 -126Z ${CARA}" fill="url(#cascoMetal)" fill-rule="evenodd"/>
    <path d="M-80 -72 Q 0 -100 80 -72" fill="none" stroke="url(#oroMetal)" stroke-width="7"/><path d="M-110 -40 Q -118 20 -96 70 M110 -40 Q 118 20 96 70" fill="none" stroke="#3e0408" stroke-width="5"/>
    <ellipse cx="-44" cy="-92" rx="40" ry="14" fill="rgba(255,255,255,.28)" transform="rotate(-22 -44 -92)"/></g>`;
  // visor dorado (baja y se cierra)
  if (v > 0.02) s += `<g transform="translate(0 ${-150 * (1 - v)})" opacity="${Math.min(1, v * 3)}"><path d="${CARA}" fill="url(#oroMetal)" stroke="#7a5212" stroke-width="4"/>
    <path d="M-62 -26 L -16 -20 L -20 -6 L -58 -12Z M62 -26 L 16 -20 L 20 -6 L 58 -12Z" fill="#e8fbff" opacity="${v > 0.95 ? 1 : 0.2}" filter="url(#brillo)"/>
    <path d="M-34 52 L 34 52" stroke="#7a5212" stroke-width="5"/><path d="M-50 70 Q 0 86 50 70" stroke="#7a5212" stroke-width="4" fill="none"/>
    <path d="M-60 -64 Q 0 -84 60 -64" stroke="rgba(255,255,255,.5)" stroke-width="5" fill="none"/></g>`;
  return s;
}
