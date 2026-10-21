// «Películas Apex»: escenarios de cine en 2.5D (luces, siluetas, profundidad) y el asistente de IA como una esfera de luz.
// Cada escenario devuelve {lejos, cerca} en coordenadas de un cuadro de 1080 x 1920; la cámara los mueve con paralaje.
const rnd = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const MUNDO_DEFS = `<defs>
  <radialGradient id="calida"><stop offset="0" stop-color="rgba(255,196,120,.85)"/><stop offset=".35" stop-color="rgba(255,160,80,.28)"/><stop offset="1" stop-color="rgba(255,140,60,0)"/></radialGradient>
  <radialGradient id="fria"><stop offset="0" stop-color="rgba(140,220,255,.85)"/><stop offset=".35" stop-color="rgba(80,190,255,.25)"/><stop offset="1" stop-color="rgba(40,160,255,0)"/></radialGradient>
  <radialGradient id="roja"><stop offset="0" stop-color="rgba(255,90,60,.8)"/><stop offset=".4" stop-color="rgba(255,60,40,.25)"/><stop offset="1" stop-color="rgba(255,40,20,0)"/></radialGradient>
  <radialGradient id="bokehC"><stop offset="0" stop-color="rgba(255,210,150,.55)"/><stop offset=".75" stop-color="rgba(255,190,120,.35)"/><stop offset="1" stop-color="rgba(255,190,120,0)"/></radialGradient>
  <radialGradient id="bokehF"><stop offset="0" stop-color="rgba(150,220,255,.5)"/><stop offset=".75" stop-color="rgba(120,200,255,.3)"/><stop offset="1" stop-color="rgba(120,200,255,0)"/></radialGradient>
  <linearGradient id="cono" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="rgba(255,214,150,.42)"/><stop offset="1" stop-color="rgba(255,214,150,0)"/></linearGradient>
  <linearGradient id="conoF" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="rgba(150,225,255,.42)"/><stop offset="1" stop-color="rgba(150,225,255,0)"/></linearGradient>
  <linearGradient id="conoR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="rgba(255,120,70,.45)"/><stop offset="1" stop-color="rgba(255,90,50,0)"/></linearGradient>
  <linearGradient id="paredMadera" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d0705"/><stop offset=".6" stop-color="#22140c"/><stop offset="1" stop-color="#140b06"/></linearGradient>
  <linearGradient id="piso" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a0f09"/><stop offset="1" stop-color="#050302"/></linearGradient>
  <linearGradient id="mantel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e8d8bf"/><stop offset="1" stop-color="#8a7558"/></linearGradient>
  <linearGradient id="maderaMesa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2212"/><stop offset=".5" stop-color="#5a3519"/><stop offset="1" stop-color="#1a0d06"/></linearGradient>
  <linearGradient id="acero" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a2e34"/><stop offset=".5" stop-color="#8a929c"/><stop offset="1" stop-color="#2a2e34"/></linearGradient>
  <linearGradient id="asfalto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05070c"/><stop offset="1" stop-color="#11151e"/></linearGradient>
  <radialGradient id="esfera" cx="36%" cy="30%" r="75%"><stop offset="0" stop-color="#f4fdff"/><stop offset=".14" stop-color="#9ff0ff"/><stop offset=".42" stop-color="#2fbbe8"/><stop offset=".8" stop-color="#0b4f9e"/><stop offset="1" stop-color="#061a3d"/></radialGradient>
  <radialGradient id="cuerpoOrbe" cx="50%" cy="50%" r="50%" fx="32.5%" fy="30%"><stop offset="0" stop-color="#f2fcff"/><stop offset=".25" stop-color="#7fe2ff"/><stop offset=".55" stop-color="#2a9fe0"/><stop offset=".85" stop-color="#0b3d91"/><stop offset="1" stop-color="#061a3d"/></radialGradient>
  <radialGradient id="haloOrbe"><stop offset=".378" stop-color="rgb(63,208,255)" stop-opacity=".75"/><stop offset=".69" stop-color="rgb(63,208,255)" stop-opacity=".22"/><stop offset="1" stop-color="rgb(63,208,255)" stop-opacity="0"/></radialGradient>
  <radialGradient id="brilloOrbe"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <radialGradient id="bordeOrbe"><stop offset=".8" stop-color="rgb(139,233,255)" stop-opacity="0"/><stop offset="1" stop-color="rgb(139,233,255)" stop-opacity=".75"/></radialGradient>
  <radialGradient id="aura"><stop offset="0" stop-color="rgba(120,230,255,.75)"/><stop offset=".3" stop-color="rgba(60,190,255,.3)"/><stop offset="1" stop-color="rgba(40,160,255,0)"/></radialGradient>
  <filter id="desenfoque" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="suave" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>`;
const bokeh = (n, sem, x0, x1, y0, y1, r0, r1, grad = "bokehC", t = 0) => Array.from({ length: n }, (_, i) => {
  const x = x0 + rnd(sem + i) * (x1 - x0), y = y0 + rnd(sem + i * 3) * (y1 - y0), r = r0 + rnd(sem + i * 7) * (r1 - r0);
  return `<circle cx="${x + Math.sin(t * 0.3 + i) * 6}" cy="${y}" r="${r}" fill="url(#${grad})" opacity="${0.5 + 0.5 * Math.sin(t * 0.8 + i * 1.7) ** 2}"/>`; }).join("");
// ---------- Siluetas con luz de borde (nada de caricatura)
function silueta(x, y, s, o = {}) {
  const tipo = o.tipo || "sentado", c = o.borde || "rgba(255,190,120,.7)", t = o.t || 0, d = o.lado ?? 1;
  const cab = `<ellipse cx="0" cy="-205" rx="34" ry="42" fill="#06070a"/><path d="M${-34 * d} -215 Q ${-30 * d} -250 0 -248" stroke="${c}" stroke-width="5" fill="none"/>`;
  let cuerpo = `<path d="M-18 -168 L 18 -168 L 22 -150 Q 78 -140 88 -80 L 92 40 L -92 40 L -88 -80 Q -78 -140 -22 -150 Z" fill="#06070a"/><path d="M${-88 * d} -80 Q ${-78 * d} -140 ${-22 * d} -150" stroke="${c}" stroke-width="5" fill="none"/>`;
  if (o.mano) cuerpo += `<path d="M${70 * d} -110 Q ${100 * d} -190 ${92 * d} -${280 + 8 * Math.sin(t * 6)}" stroke="#06070a" stroke-width="30" stroke-linecap="round" fill="none"/><circle cx="${92 * d}" cy="-${290 + 8 * Math.sin(t * 6)}" r="20" fill="#06070a" stroke="${c}" stroke-width="3"/>`;
  if (tipo === "pie" || tipo === "mesero") {
    const p = o.paso ?? 0, a = Math.sin(p) * 22;
    cuerpo = `<path d="M-18 -168 L 18 -168 L 22 -150 Q 74 -140 80 -80 L 70 120 L -70 120 L -80 -80 Q -74 -140 -22 -150 Z" fill="#06070a"/>
      <path d="M-30 110 L ${-34 - a} 380 M30 110 L ${34 + a} 380" stroke="#06070a" stroke-width="44" stroke-linecap="round"/>
      <path d="M${-80 * d} -80 Q ${-74 * d} -140 ${-22 * d} -150" stroke="${c}" stroke-width="5" fill="none"/>`;
    if (tipo === "mesero") cuerpo += `<path d="M70 -100 Q 130 -110 150 -150" stroke="#06070a" stroke-width="28" stroke-linecap="round" fill="none"/><ellipse cx="170" cy="-160" rx="95" ry="14" fill="#0a0b0e" stroke="${c}" stroke-width="3"/>
      ${[-40, 0, 40].map((dx) => `<path d="M${170 + dx - 22} -164 Q ${170 + dx} -196 ${170 + dx + 22} -164 Z" fill="#0a0b0e" stroke="${c}" stroke-width="2"/>`).join("")}`;
  }
  return `<g transform="translate(${x} ${y}) scale(${s})" opacity="${o.op ?? 1}">${cuerpo}${cab}</g>`;
}
// ---------- El asistente: el orbe nuevo de Apex (el mismo de la app): esfera con cara —ojos, cejas y boca—,
// anillo inclinado por debajo de la cara con una luz que lo recorre, halo y brillo que gira.
// Estados: reposo (sonrisa), habla (la boca se abre con la voz, nunca una «O»), escucha (cejas arriba, boquita «o»), piensa (mira arriba y una ceja alzada).
let ORBE_N = 0;
function orbe(x, y, r0, t, o = {}) {
  const nace = o.nace ?? 1, estado = o.estado || (o.habla > 0.02 ? "habla" : "reposo");
  const extra = estado === "habla" || estado === "escucha" ? (o.habla ?? 0.5) : 0;
  const piensa = estado === "piensa", oye = estado === "escucha", habla = estado === "habla";
  const k = (1 + 0.035 * Math.sin(t * 1.8) + extra * 0.12) * Math.max(0.001, 0.2 + 0.8 * nace), r = r0 * k, n = ++ORBE_N;
  const giro = piensa ? 2.6 : 0.9;
  let s = `<circle cx="${x}" cy="${y}" r="${r * 3.2}" fill="url(#aura)" opacity="${0.55 * nace}"/>
    <circle cx="${x}" cy="${y}" r="${r * 1.85}" fill="url(#haloOrbe)" opacity="${Math.min(1, (0.3 + extra * 0.45) / 0.75) * nace}"/>`;
  if (nace < 1) s += Array.from({ length: 40 }, (_, i) => { const a = rnd(i) * Math.PI * 2, d = r0 * (1 + 9 * (1 - nace) * (0.4 + rnd(i + 3)));
    return `<circle cx="${x + Math.cos(a + t) * d}" cy="${y + Math.sin(a + t) * d}" r="${2 + 3 * rnd(i + 5)}" fill="#bff6ff" opacity="${0.4 + 0.6 * nace}"/>`; }).join("");
  // anillo: mitad de atrás (arriba) y mitad de adelante (abajo), con la luz pasando por delante o por detrás
  const ra = r * 1.32, rb = r * 0.26, la = (t * giro) % (Math.PI * 2);
  const anillo = (frente) => `<g transform="translate(${x} ${y + r * 0.38}) rotate(${(-0.22 + 0.06 * Math.sin(t * 1.3)) * 57.3})">
    <path d="M${ra} 0 A ${ra} ${rb} 0 0 ${frente ? 1 : 0} ${-ra} 0" fill="none" stroke="rgba(139,233,255,${frente ? 0.7 + extra * 0.3 : 0.3})" stroke-width="${r0 * (frente ? 0.044 : 0.03)}"/>
    ${(la < Math.PI) === frente ? `<circle cx="${Math.cos(la) * ra}" cy="${Math.sin(la) * rb}" r="${r0 * 0.052}" fill="#e8fbff"/>` : ""}</g>`;
  s += anillo(false);
  // cuerpo, brillo que gira y borde luminoso
  const bx = x + Math.cos(t * giro) * r * 0.55, by = y + Math.sin(t * giro) * r * 0.18 - r * 0.1;
  s += `<clipPath id="oc${n}"><circle cx="${x}" cy="${y}" r="${r}"/></clipPath>
    <circle cx="${x}" cy="${y}" r="${r}" fill="url(#cuerpoOrbe)"/>
    <circle cx="${bx}" cy="${by}" r="${r * 0.5}" fill="url(#brilloOrbe)" clip-path="url(#oc${n})"/>
    <circle cx="${x}" cy="${y}" r="${r}" fill="url(#bordeOrbe)" opacity="${Math.min(1, (0.35 + extra * 0.4) / 0.75)}"/>`;
  // cara: ojos que parpadean y miran alrededor, cejas y boca
  const ap = (t % 3.7) < 0.13 && !piensa ? 0.1 : oye ? 1.15 : 1;
  const mx = piensa ? r * 0.06 : Math.sin(t * 0.55) * r * 0.05, my = piensa ? -r * 0.07 : Math.sin(t * 0.37) * r * 0.02;
  const ey = y - r * 0.1, sep = r * 0.33;
  [-1, 1].forEach((d) => {
    const ex = x + d * sep;
    s += `<ellipse cx="${ex}" cy="${ey}" rx="${r * 0.14}" ry="${r * 0.2 * ap}" fill="#f4fbff"/>`;
    if (ap > 0.3) s += `<ellipse cx="${ex + mx}" cy="${ey + my + r * 0.02}" rx="${r * 0.075}" ry="${r * 0.1 * Math.min(1, ap)}" fill="#071a33"/>
      <circle cx="${ex + mx + r * 0.03}" cy="${ey + my - r * 0.03}" r="${r * 0.028}" fill="#fff"/>`;
    const alza = oye ? r * 0.07 : piensa && d > 0 ? r * 0.09 : 0, inc = piensa ? d * 0.18 : oye ? -d * 0.08 : 0;
    s += `<path transform="translate(${ex} ${ey - r * 0.3 - alza}) rotate(${inc * 57.3})" d="M${-r * 0.13} ${r * 0.02} Q 0 ${-r * 0.04} ${r * 0.13} ${r * 0.02}" fill="none" stroke="#06244f" stroke-width="${r * 0.06}" stroke-linecap="round"/>`;
  });
  const my2 = y + r * 0.3;
  if (habla && extra > 0.04) {
    const alto = r * (0.06 + 0.1 * Math.min(1, extra * 1.6));
    const boca = `M${x - r * 0.21} ${my2 - r * 0.03} Q ${x} ${my2 + r * 0.01} ${x + r * 0.21} ${my2 - r * 0.03} Q ${x} ${my2 + alto * 2.1} ${x - r * 0.21} ${my2 - r * 0.03} Z`;
    s += `<clipPath id="ob${n}"><path d="${boca}"/></clipPath><path d="${boca}" fill="#071a33"/>
      <ellipse cx="${x}" cy="${my2 + alto * 1.2}" rx="${r * 0.09}" ry="${alto * 0.5}" fill="#ff7b8a" clip-path="url(#ob${n})"/>`;
  } else if (piensa) s += `<path d="M${x - r * 0.1} ${my2 + r * 0.02} L ${x + r * 0.12} ${my2 - r * 0.02}" stroke="#071a33" stroke-width="${r * 0.055}" stroke-linecap="round"/>`;
  else if (oye) s += `<ellipse cx="${x}" cy="${my2}" rx="${r * 0.07}" ry="${r * 0.08}" fill="#071a33"/>`;
  else s += `<path d="M${x - r * 0.2} ${my2 - r * 0.02} Q ${x} ${my2 + r * 0.16} ${x + r * 0.2} ${my2 - r * 0.02}" fill="none" stroke="#071a33" stroke-width="${r * 0.055}" stroke-linecap="round"/>`;
  s += anillo(true);
  return `<g opacity="${Math.min(1, nace * 1.4)}">${s}</g>`;
}
// Nivel de voz simulado por sílabas (para que la boca se abra y cierre con ritmo de habla)
function nivelVoz(t) { const v = Math.abs(Math.sin(t * 10.5) * Math.sin(t * 6.1 + 1)) * (0.6 + 0.4 * Math.sin(t * 2.3) ** 2); return 0.15 + 0.85 * v; }
// ---------- Platos reales: fotos de la carta recortadas (fotos/), con sombra de contacto y la luz cálida de la vela encima
const PLATOS = { bandeja: { w: 620, alto: 446 / 738 * 0.74, base: 0.5 }, torta: { w: 440, alto: 466 / 534, base: 0.78 } };
function platoReal(x, y, tipo, t) {
  const p = PLATOS[tipo], w = p.w, h = w * p.alto, top = y - h * p.base;
  return `<ellipse cx="${x}" cy="${y + h * (1 - p.base) - 18}" rx="${w * 0.5}" ry="${w * 0.1}" fill="rgba(0,0,0,.55)" filter="url(#desenfoque)"/>
    <image href="fotos/${tipo}.png" x="${x - w / 2}" y="${top}" width="${w}" height="${h}" preserveAspectRatio="none"/>
    <ellipse cx="${x - w * 0.15}" cy="${top + h * 0.35}" rx="${w * 0.45}" ry="${h * 0.4}" fill="url(#calida)" opacity="${0.35 + 0.05 * Math.sin(t * 9)}" style="mix-blend-mode:soft-light"/>`;
}
// ---------- Escenarios
function lampara(x, y, s, t, on = 1, cono = "cono") {
  const fl = 0.95 + 0.05 * Math.sin(t * 13 + x);
  return `<g transform="translate(${x} ${y}) scale(${s})"><line x1="0" y1="-900" x2="0" y2="0" stroke="#0a0604" stroke-width="4"/>
    <path d="M-60 0 L 60 0 L 34 -46 L -34 -46 Z" fill="#1a110a"/><ellipse cx="0" cy="2" rx="60" ry="9" fill="rgba(255,220,160,${0.9 * on})"/>
    <path d="M-60 4 L -420 900 L 420 900 L 60 4 Z" fill="url(#${cono})" opacity="${on * fl}"/><circle cy="10" r="${150 * on}" fill="url(#calida)" opacity="${on}"/></g>`;
}
function mesaSalon(x, y, s, t, o = {}) {
  const c = `<g transform="translate(${x} ${y}) scale(${s})">
    <ellipse cx="0" cy="40" rx="250" ry="34" fill="rgba(0,0,0,.6)"/>
    <path d="M-230 0 Q -230 90 -200 110 L 200 110 Q 230 90 230 0 Z" fill="#6a5a46"/><ellipse rx="230" ry="46" fill="url(#mantel)"/>
    <circle cx="0" cy="-30" r="${120 + 10 * Math.sin(t * 9 + x)}" fill="url(#calida)" opacity=".9"/>
    <rect x="-8" y="-58" width="16" height="44" fill="#efe6d0"/><ellipse cx="0" cy="${-66 + Math.sin(t * 11 + x)}" rx="6" ry="13" fill="#ffd27a"/>
    ${[-120, 110].map((dx) => `<path d="M${dx - 14} -6 L ${dx - 18} -60 Q ${dx} -76 ${dx + 18} -60 L ${dx + 14} -6 Z" fill="rgba(255,240,220,.18)" stroke="rgba(255,230,200,.5)" stroke-width="2"/>`).join("")}
    ${o.qr ? `<g transform="translate(150 -40)"><rect x="-26" y="-60" width="52" height="64" rx="4" fill="rgba(220,240,255,.25)" stroke="rgba(255,255,255,.5)" stroke-width="2"/><rect x="-16" y="-50" width="32" height="32" fill="#0b1626"/></g>` : ""}</g>`;
  return c;
}
function salon(t, o = {}) {
  const luz = o.luces ?? 1, rojo = o.alerta || 0;
  let lejos = `<rect x="-900" y="-900" width="2900" height="3900" fill="url(#paredMadera)"/>`;
  lejos += Array.from({ length: 22 }, (_, i) => `<rect x="${-700 + i * 130}" y="200" width="6" height="900" fill="rgba(0,0,0,.35)"/>`).join("");
  lejos += `<rect x="150" y="250" width="780" height="620" fill="#04060c"/>` + bokeh(38, 11, 160, 920, 270, 850, 8, 26, "bokehF", t) + bokeh(20, 51, 160, 920, 270, 850, 10, 30, "bokehC", t);
  if (o.lluvia) lejos += Array.from({ length: 40 }, (_, i) => { const x = 160 + rnd(i) * 760, y = 260 + ((rnd(i + 2) * 600 + t * 500) % 600); return `<line x1="${x}" y1="${y}" x2="${x - 4}" y2="${y + 30}" stroke="rgba(180,210,255,.25)" stroke-width="2"/>`; }).join("");
  lejos += `<rect x="140" y="240" width="800" height="640" fill="none" stroke="#120a06" stroke-width="26"/><line x1="540" y1="240" x2="540" y2="880" stroke="#120a06" stroke-width="16"/>`;
  lejos += [[-120, 560], [1200, 560]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="200" fill="url(#calida)" opacity="${0.6 * luz}"/><rect x="${x - 20}" y="${y - 30}" width="40" height="60" rx="8" fill="#2a1a10"/>`).join("");
  lejos += `<rect x="-900" y="1000" width="2900" height="2000" fill="url(#piso)"/>`;
  lejos += [180, 540, 900].map((x, i) => `<rect x="${x - 30}" y="1010" width="60" height="420" fill="rgba(255,190,110,${0.12 * luz})" filter="url(#suave)"/>`).join("");
  const lamps = [[180, 420, 0.7], [540, 380, 0.8], [900, 420, 0.7]].map(([x, y, s], i) => lampara(x, y, s, t, luz * cl((o.encender ?? 1) * 3 - i), rojo > 0.5 ? "conoR" : "cono")).join("");
  // mesas en tres filas de profundidad, con comensales en silueta
  const filas = [[[220, 1080, 0.42], [540, 1070, 0.42], [860, 1080, 0.42]], [[150, 1250, 0.66], [930, 1250, 0.66]], [[540, 1520, 1.0]]];
  let medio = "";
  filas.forEach((fila, fi) => fila.forEach(([x, y, s], k) => {
    const id = fi * 3 + k, mano = (o.manos || []).includes(id);
    medio += silueta(x - 150 * s, y - 20 * s, s * 0.95, { mano, lado: -1, t: t + id, borde: rojo > 0.5 ? "rgba(255,110,80,.7)" : "rgba(255,190,120,.6)" });
    medio += silueta(x + 150 * s, y - 20 * s, s * 0.95, { lado: 1, t, borde: "rgba(255,190,120,.6)" });
    medio += mesaSalon(x, y, s, t, { qr: o.qr });
    if (o.orbes && (o._tt ?? t) > (o.orbes[id] ?? 99)) { const q = cl(((o._tt ?? t) - o.orbes[id]) / 0.8); medio += orbe(x, y - 170 * s, 34 * s, t + id, { nace: q, estado: Math.sin(t * 2 + id) > 0.2 ? "habla" : "reposo", habla: 0.6 * nivelVoz(t + id) }); }
  }));
  if (o.trazos) filas.flat().forEach(([x, y, s], i) => { const a = o.trazos + i * 0.25, tt = o._tt ?? t; if (tt < a) return; const q = cl((tt - a) / 1.2);
    medio += `<path d="M${x} ${y - 170 * s} Q ${(x + 1150) / 2} ${y - 500} 1150 760" fill="none" stroke="rgba(127,216,240,.8)" stroke-width="${6 * s + 2}" stroke-dasharray="${1400 * q} 3000" stroke-linecap="round"/>
      <path d="M${x} ${y - 170 * s} Q ${(x + 1150) / 2} ${y - 500} 1150 760" fill="none" stroke="rgba(127,216,240,.25)" stroke-width="${22 * s + 6}" stroke-dasharray="${1400 * q} 3000" stroke-linecap="round"/>`; });
  if (o.mesero != null) { const x = lerp(-200, 1300, ((t * 0.09 + o.mesero) % 1)); medio += silueta(x, 1360, 0.9, { tipo: "mesero", paso: t * 7, borde: "rgba(255,200,130,.75)" }); }
  const cerca = bokeh(7, 91, -100, 1180, 1650, 2000, 70, 150, "bokehC", t) + `<rect x="-900" y="-900" width="2900" height="3900" fill="rgba(255,60,40,${0.18 * rojo})"/>`;
  return { lejos: lejos + lamps, medio, cerca };
}
function mesa(t, o = {}) {
  let lejos = `<rect x="-900" y="-900" width="2900" height="3900" fill="#080504"/>` + bokeh(26, 7, -200, 1280, 200, 1100, 40, 120, "bokehC", t) + bokeh(8, 77, -200, 1280, 200, 1000, 50, 110, "bokehF", t);
  if (o.mano) lejos += `<g filter="url(#desenfoque)" opacity=".85">${silueta(780, 1030, 1.3, { mano: true, lado: 1, t })}</g>`;
  let medio = `<path d="M-900 1080 L 1980 1080 L 2400 2900 L -1300 2900 Z" fill="url(#maderaMesa)"/>` + Array.from({ length: 9 }, (_, i) => `<path d="M${-300 + i * 200} 1080 Q ${-260 + i * 210} 1500 ${-500 + i * 260} 2900" stroke="rgba(0,0,0,.22)" stroke-width="5" fill="none"/>`).join("");
  medio += `<ellipse cx="540" cy="1080" rx="900" ry="40" fill="rgba(255,190,110,.15)"/>`;
  // vela, copa, plato y el código QR en su base de acrílico
  medio += `<circle cx="${o.velaX ?? 240}" cy="1120" r="${300 + 20 * Math.sin(t * 9)}" fill="url(#calida)"/><rect x="${(o.velaX ?? 240) - 26}" y="1020" width="52" height="140" rx="6" fill="#efe6d0"/><ellipse cx="${o.velaX ?? 240}" cy="${1004 + Math.sin(t * 11) * 3}" rx="14" ry="30" fill="#ffd27a"/>`;
  medio += `<g transform="translate(860 1200)"><path d="M-46 0 L -56 -150 Q 0 -190 56 -150 L 46 0 Z" fill="rgba(255,240,220,.12)" stroke="rgba(255,235,210,.6)" stroke-width="3"/><path d="M-50 -80 Q 0 -70 50 -80 L 46 0 L -46 0 Z" fill="rgba(150,20,40,.55)"/><rect x="-4" y="0" width="8" height="90" fill="rgba(255,240,220,.4)"/><ellipse cy="92" rx="50" ry="10" fill="rgba(255,240,220,.3)"/></g>`;
  if (o.plato !== false) medio += platoReal(o.platoX ?? 470, 1460, o.plato || "bandeja", t);
  if (o.qr) { const brillo = o.qrLuz ?? 0, cx = o.qrX ?? 540, cy = o.qrY ?? 1180;
    medio += `<g transform="translate(${cx} ${cy})"><circle cy="-120" r="${260 * brillo}" fill="url(#fria)" opacity="${brillo}"/><rect x="-90" y="-240" width="180" height="230" rx="10" fill="rgba(220,240,255,.18)" stroke="rgba(255,255,255,.6)" stroke-width="3"/>
      <rect x="-70" y="-220" width="140" height="140" fill="#f4f8fb"/>${Array.from({ length: 49 }, (_, i) => rnd(i + 11) > 0.5 ? `<rect x="${-66 + (i % 7) * 19}" y="${-216 + Math.floor(i / 7) * 19}" width="17" height="17" fill="#0b1626"/>` : "").join("")}
      <text y="-46" text-anchor="middle" font-family="Figtree" font-weight="800" font-size="22" fill="#e8fbff">MESA 4</text><rect x="-100" y="-10" width="200" height="16" rx="4" fill="rgba(220,240,255,.3)"/></g>`; }
  if (o.flash) medio += `<rect x="-900" y="-900" width="2900" height="3900" fill="rgba(255,255,255,${o.flash})"/>`;
  const cerca = bokeh(5, 33, -100, 1180, 1700, 2050, 90, 170, "bokehC", t);
  return { lejos, medio, cerca };
}
function cocina(t, o = {}) {
  let lejos = `<rect x="-900" y="-900" width="2900" height="3900" fill="#0b0c0e"/>` + Array.from({ length: 30 }, (_, i) => Array.from({ length: 10 }, (_, j) => `<rect x="${-600 + i * 80}" y="${200 + j * 80}" width="76" height="76" fill="rgba(200,210,220,${0.03 + 0.03 * rnd(i * 10 + j)})"/>`).join("")).join("");
  lejos += [200, 540, 880].map((x) => `<g transform="translate(${x} 420)"><rect x="-70" y="-30" width="140" height="30" fill="#2a2e34"/><path d="M-70 0 L -260 760 L 260 760 L 70 0 Z" fill="url(#conoR)" opacity="${0.8 + 0.2 * Math.sin(t * 5 + x)}"/><circle r="180" fill="url(#roja)"/></g>`).join("");
  lejos += `<g transform="translate(540 760)">${silueta(0, 220, 1.3, { tipo: "pie", borde: "rgba(255,120,70,.8)", paso: t * 3 })}<rect x="-40" y="-90" width="80" height="60" rx="20" fill="#e8e4da" transform="translate(0 -40)"/></g>`;
  let medio = `<rect x="-900" y="1150" width="2900" height="70" fill="url(#acero)"/><rect x="-900" y="1220" width="2900" height="1700" fill="#121417"/>`;
  medio += `<line x1="-200" y1="900" x2="1280" y2="900" stroke="#8a929c" stroke-width="10"/>` + Array.from({ length: o.tickets ?? 7 }, (_, i) => { const x = -100 + i * 180, sw = Math.sin(t * 3 + i) * 4;
    return `<g transform="translate(${x} 904) rotate(${sw})"><rect x="-60" y="0" width="120" height="${180 + (i % 3) * 30}" fill="#f4efe2"/>${[30, 60, 90, 120].map((y) => `<line x1="-44" y1="${y}" x2="${30 - (i * 7 + y) % 40}" y2="${y}" stroke="#555" stroke-width="5"/>`).join("")}${o.tachados && i % 2 ? `<path d="M-50 20 L 50 150 M50 20 L -50 150" stroke="#d0261c" stroke-width="7"/>` : ""}</g>`; }).join("");
  medio += Array.from({ length: 6 }, (_, i) => `<ellipse cx="${200 + i * 140 + Math.sin(t + i) * 30}" cy="${1100 - ((t * 60 + i * 80) % 400)}" rx="${60 + i * 6}" ry="30" fill="rgba(230,230,240,${0.06 + 0.02 * i})"/>`).join("");
  if (o.fuego) medio += `<g transform="translate(300 1150)"><ellipse rx="${140 + 30 * Math.sin(t * 17)}" ry="${90 + 30 * Math.sin(t * 13)}" cy="-60" fill="url(#roja)"/><path d="M-60 0 Q -40 ${-120 - 40 * Math.sin(t * 15)} 0 -160 Q 40 ${-110 - 40 * Math.sin(t * 12)} 60 0 Z" fill="rgba(255,170,60,.85)"/></g>`;
  return { lejos, medio, cerca: bokeh(5, 61, -100, 1180, 1700, 2050, 80, 150, "bokehC", t) };
}
function ciudad(t, o = {}) {
  const hz = 760, fx = 540;   // horizonte y punto de fuga
  let lejos = `<rect x="-900" y="-900" width="2900" height="3900" fill="#04060d"/><rect x="-900" y="${hz - 300}" width="2900" height="320" fill="#0b1226"/>` + bokeh(30, 5, 300, 780, hz - 260, hz, 4, 12, "bokehC", t);
  // fachadas a ambos lados que se pierden en el punto de fuga
  [-1, 1].forEach((d) => { for (let i = 0; i < 7; i++) {
    const n0 = i / 7, n1 = (i + 1) / 7, x0 = fx + d * lerp(1500, 60, n0 ** 0.6), x1 = fx + d * lerp(1500, 60, n1 ** 0.6), alto0 = lerp(1900, 120, n0 ** 0.6), alto1 = lerp(1900, 120, n1 ** 0.6);
    lejos += `<path d="M${x0} ${hz - alto0} L ${x1} ${hz - alto1} L ${x1} ${hz + alto1 * 0.18} L ${x0} ${hz + alto0 * 0.18} Z" fill="${i % 2 ? "#0b0f1a" : "#0e1322"}"/>`;
    for (let r = 0; r < 6; r++) for (let c = 0; c < 3; c++) if (rnd(i * 31 + r * 7 + c + (d > 0 ? 300 : 0)) > 0.45) {
      const u = (c + 0.3) / 3, v = (r + 0.3) / 7, X = lerp(x0, x1, u), H = lerp(alto0, alto1, u), Y = hz - H + v * H * 1.0;
      lejos += `<rect x="${X - 6 * (1 - u * 0.6)}" y="${Y}" width="${22 * (1 - u * 0.7)}" height="${30 * (1 - u * 0.7)}" fill="rgba(255,${190 + 40 * rnd(i + r)},${120 + 60 * rnd(c + r)},${0.35 + 0.45 * rnd(i * r + c)})"/>`; } } });
  const neon = [["ABIERTO", "#ff2f8a", 170, 640, -1], ["COMIDA", "#00e0ff", 900, 560, 1], ["DOMICILIOS", "#ffcf3a", 120, 900, -1], ["RESTAURANTE", "#7cff6a", 960, 860, 1]];
  lejos += neon.map(([w, c, x, y, d], i) => { const on = Math.sin(t * (6 + i) + i * 3) > -0.92 ? 1 : 0.25;
    return `<g opacity="${on}" transform="translate(${x} ${y}) skewY(${d * 14})"><circle r="220" fill="${c}" opacity=".12"/><text text-anchor="middle" font-family="Figtree" font-weight="900" font-size="64" fill="none" stroke="${c}" stroke-width="4" style="filter:drop-shadow(0 0 16px ${c})">${w}</text><text text-anchor="middle" font-family="Figtree" font-weight="900" font-size="64" fill="${c}" opacity=".4">${w}</text></g>`; }).join("");
  // faroles
  lejos += [[-1, 0.15], [1, 0.3], [-1, 0.5], [1, 0.62]].map(([d, n]) => { const x = fx + d * lerp(1300, 120, n ** 0.6), h = lerp(1300, 160, n ** 0.6);
    return `<line x1="${x}" y1="${hz + h * 0.18}" x2="${x}" y2="${hz - h * 0.6}" stroke="#05070c" stroke-width="${10 * (1 - n)}"/><circle cx="${x - d * 30 * (1 - n)}" cy="${hz - h * 0.6}" r="${180 * (1 - n * 0.7)}" fill="url(#calida)"/>
      <path d="M${x - d * 30 * (1 - n)} ${hz - h * 0.6} L ${x - d * 30 - 220 * (1 - n)} ${hz + h * 0.18} L ${x - d * 30 + 220 * (1 - n)} ${hz + h * 0.18} Z" fill="url(#cono)" opacity=".6"/>`; }).join("");
  // calle mojada con reflejos
  let medio = `<path d="M${fx - 60} ${hz} L ${fx + 60} ${hz} L 2400 3200 L -1300 3200 Z" fill="url(#asfalto)"/>`;
  medio += neon.map(([, c, x], i) => `<rect x="${lerp(fx, x, 0.85) - 25}" y="${hz + 40}" width="50" height="1300" fill="${c}" opacity=".16" filter="url(#suave)" transform="skewX(${(x - fx) / 30})"/>`).join("");
  medio += Array.from({ length: 8 }, (_, i) => { const n = i / 8, y = hz + 30 + n * n * 1300, w = 8 + n * 40; return `<rect x="${fx - w / 2}" y="${y}" width="${w}" height="${20 + n * 90}" fill="rgba(255,240,200,.45)"/>`; }).join("");
  const motos = o.motos ?? 5; for (let i = 0; i < motos; i++) { const q = ((t * 0.28 + i / motos) % 1), e = q * q, carril = (i % 2 ? 1 : -1) * (0.25 + 0.15 * (i % 3)), x = fx + carril * e * 1100, y = hz + 20 + e * 1500, propia = o.propia && i === 0;
    const luz = propia ? "127,216,240" : i % 3 === 0 ? "255,70,60" : "255,240,210", r = 4 + 30 * e;
    medio += `<line x1="${x}" y1="${y}" x2="${fx + carril * Math.max(0, e - 0.12) * 1100}" y2="${hz + 20 + Math.max(0, e - 0.12) * 1500}" stroke="rgba(${luz},.55)" stroke-width="${r * 0.9}" stroke-linecap="round"/>
      <circle cx="${x}" cy="${y}" r="${r * 3}" fill="${propia ? "url(#fria)" : i % 3 === 0 ? "url(#roja)" : "url(#calida)"}"/><circle cx="${x}" cy="${y}" r="${r * 0.6}" fill="rgb(${luz})"/>
      <rect x="${x - r * 0.4}" y="${y + r}" width="${r * 0.8}" height="${r * 6}" fill="rgba(${luz},.25)" filter="url(#suave)"/>`; }
  if (o.lluvia !== false) medio += Array.from({ length: 90 }, (_, i) => { const x = rnd(i) * 1300 - 100, y = ((rnd(i + 4) * 2200 + t * 1700) % 2200) - 150; return `<line x1="${x}" y1="${y}" x2="${x - 8}" y2="${y + 64}" stroke="rgba(200,220,255,${0.18 + 0.2 * rnd(i + 1)})" stroke-width="2"/>`; }).join("");
  return { lejos, medio, cerca: bokeh(5, 71, -100, 1180, 1700, 2050, 70, 140, "bokehF", t) };
}
function mostrador(t, o = {}) {
  let lejos = `<rect x="-900" y="-900" width="2900" height="3900" fill="#050404"/><rect x="620" y="300" width="380" height="520" fill="#06080e"/>` + Array.from({ length: 30 }, (_, i) => { const x = 630 + rnd(i) * 360, y = 310 + ((rnd(i + 2) * 500 + t * 400) % 500); return `<line x1="${x}" y1="${y}" x2="${x - 3}" y2="${y + 24}" stroke="rgba(170,200,255,.3)" stroke-width="2"/>`; }).join("") + bokeh(10, 21, 640, 980, 320, 800, 10, 26, "bokehF", t);
  lejos += `<rect x="610" y="290" width="400" height="540" fill="none" stroke="#0e0907" stroke-width="22"/>`;
  lejos += lampara(420, 520, 1.0, t, 1);
  let medio = silueta(420, 1240, 1.6, { tipo: "pie", borde: "rgba(255,190,120,.8)", lado: 1 });
  medio += `<rect x="-900" y="1230" width="2900" height="40" fill="#3a2414"/><rect x="-900" y="1270" width="2900" height="1700" fill="#1a0f08"/>`;
  medio += `<g transform="translate(700 1180)"><rect x="-110" y="-90" width="220" height="100" rx="10" fill="#1b1d22"/><rect x="-90" y="-76" width="140" height="40" fill="#0b2a2a"/><text x="-20" y="-48" text-anchor="middle" font-family="DejaVu Sans Mono" font-size="26" fill="#3aff9a">${o.caja || ""}</text></g>`;
  medio += Array.from({ length: o.billetes ?? 8 }, (_, i) => `<g transform="translate(${200 + (i % 4) * 8} ${1222 - i * 7}) rotate(${(i * 37) % 9 - 4})"><rect x="-70" y="-14" width="140" height="28" rx="3" fill="#5fa86b" stroke="#2f6b3a" stroke-width="3"/></g>`).join("");
  if (o.drenar) for (let i = 0; i < 26; i++) { const q = ((t * 0.5 + rnd(i)) % 1), x = lerp(220, 800, q) + Math.sin(i + t * 3) * 30, y = lerp(1180, 520, q) - Math.sin(q * Math.PI) * 120;
    medio += `<circle cx="${x}" cy="${y}" r="${6 + 6 * rnd(i)}" fill="rgba(255,80,70,${0.9 * (1 - q) * o.drenar})"/><circle cx="${x}" cy="${y}" r="${24}" fill="url(#roja)" opacity="${0.6 * (1 - q) * o.drenar}"/>`; }
  return { lejos, medio, cerca: bokeh(4, 41, -100, 1180, 1750, 2050, 90, 160, "bokehC", t) };
}
function vacio(t, o = {}) {
  let lejos = `<rect x="-900" y="-900" width="2900" height="3900" fill="#020308"/>` + [0, 1, 2, 3].map((i) => `<ellipse cx="${540 + Math.sin(t * 0.2 + i) * 200}" cy="${700 + i * 300}" rx="${900}" ry="${120 + i * 20}" fill="rgba(60,120,200,${0.05 + 0.02 * i})"/>`).join("");
  lejos += `<path d="M440 -400 L 0 2000 L 1080 2000 L 640 -400 Z" fill="url(#conoF)" opacity=".35"/>`;
  const medio = Array.from({ length: 70 }, (_, i) => `<circle cx="${(rnd(i) * 1300 - 100 + t * 8 * (rnd(i + 1) - .5)) % 1300}" cy="${(rnd(i + 5) * 2000 - t * 14 * rnd(i + 2) + 4000) % 2000}" r="${1 + rnd(i + 3) * 3}" fill="rgba(180,230,255,${0.2 + 0.5 * rnd(i + 7)})"/>`).join("");
  return { lejos, medio, cerca: "" };
}
function plano(t, o = {}) {
  const k = o.dibujo ?? 1; let lejos = `<rect x="-900" y="-900" width="2900" height="3900" fill="#06142e"/>` + Array.from({ length: 60 }, (_, i) => `<line x1="${-600 + i * 60}" y1="-900" x2="${-600 + i * 60}" y2="3000" stroke="rgba(127,216,240,${i % 5 ? 0.06 : 0.14})" stroke-width="2"/><line x1="-900" y1="${-600 + i * 60}" x2="2000" y2="${-600 + i * 60}" stroke="rgba(127,216,240,${i % 5 ? 0.06 : 0.14})" stroke-width="2"/>`).join("");
  const traz = (d, len, de) => `<path d="${d}" fill="none" stroke="#bfefff" stroke-width="5" stroke-dasharray="${len}" stroke-dashoffset="${len * (1 - cl((k - de) / 0.35))}"/>`;
  let medio = traz("M140 420 L 940 420 L 940 1560 L 140 1560 Z", 3900, 0) + traz("M140 560 L 520 560 L 520 420", 900, 0.15) + `<text x="200" y="510" font-family="DejaVu Sans Mono" font-size="30" fill="#7fd8f0" opacity="${cl((k - 0.3) / 0.3)}">COCINA</text>`;
  [[300, 800], [520, 800], [740, 800], [300, 1080], [520, 1080], [740, 1080], [300, 1360], [520, 1360], [740, 1360]].forEach(([x, y], i) => {
    medio += traz(`M${x - 70} ${y} A 70 70 0 1 0 ${x + 70} ${y} A 70 70 0 1 0 ${x - 70} ${y}`, 450, 0.3 + i * 0.05);
    if (o.qrs && k > 0.85 + i * 0.012) medio += `<rect x="${x - 18}" y="${y - 18}" width="36" height="36" fill="#7fd8f0"/><circle cx="${x}" cy="${y}" r="70" fill="url(#fria)" opacity=".6"/>`; });
  medio += `<line x1="-200" y1="${300 + ((t * 300) % 1500)}" x2="1300" y2="${300 + ((t * 300) % 1500)}" stroke="rgba(127,216,240,.35)" stroke-width="4"/>`;
  return { lejos, medio, cerca: "" };
}
function estudio(t, o = {}) {
  const lejos = `<rect x="-900" y="-900" width="2900" height="3900" fill="#04060b"/><path d="M440 -400 L -100 1700 L 1180 1700 L 640 -400 Z" fill="url(#${o.frio === false ? "cono" : "conoF"})" opacity=".55"/>
    <ellipse cx="540" cy="1700" rx="600" ry="90" fill="rgba(127,216,240,.12)"/><rect x="-900" y="1700" width="2900" height="1300" fill="#020306"/>`;
  return { lejos, medio: bokeh(14, 81, -100, 1180, 200, 1500, 20, 60, "bokehF", t), cerca: "" };
}
const ESCENARIOS = { salon, mesa, cocina, ciudad, mostrador, vacio, plano, estudio };
