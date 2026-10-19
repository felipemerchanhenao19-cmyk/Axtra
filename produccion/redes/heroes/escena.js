// Motor por planos de «Orbi: universo de héroes». EP = guion (planos, actores, efectos); LINEA = tiempos de cada plano y cada voz.
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const rebote = (x) => { x = cl(x); return 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
const CURVAS = { ease, out: out3, lineal: cl, rebote, in: (x) => Math.pow(cl(x), 3) };
const P = LINEA.planos, SELLO = LINEA.sello, TODAS = P.flatMap((p) => p.lineas);
const bocaT = (t) => 0.25 + 0.6 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 4.7));
const habla = (q, t) => TODAS.some((l) => l.quien === q && t >= l.ini && t < l.fin);
const planoEn = (t) => { let k = 0; for (let i = 0; i < P.length; i++) if (t >= P[i].ini) k = i; return k; };
// Valores animados: {anim: [v0, v1, p0, p1, curva]} se resuelven con el avance del plano (0-1)
function resolver(v, p) {
  if (v && typeof v === "object" && !Array.isArray(v)) {
    if (v.anim) { const [a, b, p0 = 0, p1 = 1, c = "ease"] = v.anim; return lerp(a, b, CURVAS[c]((p - p0) / Math.max(0.001, p1 - p0))); }
    const r = {}; for (const k in v) r[k] = resolver(v[k], p); return r;
  }
  return v;
}
const tFx = (pl, L, fx, cual = "") => {
  const lin = fx["linea" + cual], pp = fx["p" + cual];
  if (lin != null) return L.lineas[lin].ini + (fx["dt" + cual] || 0);
  if (pp != null) return L.ini + pp * (L.fin - L.ini);
  return cual ? L.fin : L.ini;
};
// ---------- Actores
function dibujaActor(a, st, t) {
  const h = habla(a.voz || a.id, t), b = h ? bocaT(t) : 0, cara = st.cara ?? a.cara, pr = st.props;
  switch (a.tipo) {
    case "orbi": return orbiHeroe(t, pr.traje || "normal", cara || "normal", h, pr);
    case "cuaderno": return cuaderno({ ...pr, cara, boca: b, t });
    case "horaPico": return horaPico({ ...pr, cara, boca: b, t });
    case "porcentaje": return porcentaje({ ...pr, cara, boca: b, t });
    case "factura": return factura({ ...pr, cara, boca: b, t });
    case "sofia": return sofia({ ...pr, boca: b, t });
    case "comi": return comi({ cara: cara || "diva", boca: b, abanico: (cara || "diva") === "diva" ? Math.sin(t * 7) * 12 : null, brazoArriba: pr.brazoArriba });
    case "rosa": { const ro = `<g transform="translate(-210 -65) scale(1.3)">${rosa({ boca: h ? bocaT(t) : (pr.boca ?? 0.4), cejas: pr.cejas || "", brazo: pr.brazo || 0, mira: pr.mira ?? 0 })}</g>`;
      return pr.mostrador ? ro + mostrador() + billetes(pr.billetes ?? 0) : ro; }
    case "julian": return julian({ ...pr, boca: h ? bocaT(t) : pr.boca });
    case "persona": return persona({ ...pr, boca: h ? bocaT(t) : (pr.boca ?? 0.4) });
  }
  return typeof dibujaExtra === "function" ? dibujaExtra(a, { ...st, cara }, t, h, b) : "";
}
function actores(pl, L, t, p, golpes) {
  const est = {};
  pl.actores.forEach((a) => (est[a.id] = { cara: a.cara, props: resolver(a.props || {}, p) }));
  pl.lineas.forEach((ln, k) => { const e = ln[3] || {}; if (t < L.lineas[k].ini - 0.1) return;
    for (const [id, c] of Object.entries(e.caras || {})) if (est[id]) est[id].cara = c;
    for (const [id, pr] of Object.entries(e.props || {})) if (est[id]) est[id].props = { ...est[id].props, ...pr }; });
  return pl.actores.map((a) => {
    const fin = a.a || {}, q = CURVAS[a.curva || "ease"]((p - (a.de ?? 0)) / Math.max(0.001, (a.hasta ?? 1) - (a.de ?? 0)));
    let x = lerp(a.x, fin.x ?? a.x, q), y = lerp(a.y, fin.y ?? a.y, q), s = lerp(a.s ?? 1, fin.s ?? (a.s ?? 1), q), r = lerp(a.r ?? 0, fin.r ?? (a.r ?? 0), q);
    let op = 1; if (a.aparece != null) op = out3((p - a.aparece) / 0.06); if (a.desaparece != null) op *= 1 - cl((p - a.desaparece) / 0.06);
    if (op <= 0.01) return "";
    if (a.flota) y += Math.sin(t * 2.2 + a.x) * a.flota;
    const gp = golpes[a.id]; if (gp) { x += gp.dir * 70 * gp.k; r += gp.dir * 12 * gp.k; }
    const sombra = a.sombra ? `<ellipse cx="${x}" cy="${a.sombra}" rx="${120 * s}" ry="${20 * s}" fill="rgba(0,0,0,.45)"/>` : "";
    return `${sombra}<g transform="translate(${x} ${y}) rotate(${r}) scale(${s * (a.voltea ? -1 : 1)} ${s})" opacity="${op}">${dibujaActor(a, est[a.id], t)}</g>`;
  }).join("");
}
// ---------- Efectos
const IMPACTO = [];
function efectos(pl, L, t) {
  let mundo = "", pantalla = "", sacude = 0, flash = 0; const golpes = {};
  for (const fx of pl.fx || []) {
    const T0 = tFx(pl, L, fx), T1 = tFx(pl, L, fx, "1"), d = t - T0;
    switch (fx.tipo) {
      case "lluvia": pantalla += Array.from({ length: 150 }, (_, i) => { const v = 2200 + rnd(i) * 900, x = (rnd(i + 7) * 1400 - 160 + t * 260) % 1400 - 160, y = ((rnd(i + 3) * 2300 + t * v) % 2300) - 180;
        return `<line x1="${x}" y1="${y}" x2="${x - 14}" y2="${y + 70}" stroke="rgba(190,210,255,${(0.18 + 0.25 * rnd(i + 1)) * (fx.k ?? 1)})" stroke-width="${1.5 + rnd(i + 2) * 2}"/>`; }).join(""); break;
      case "polvo": pantalla += Array.from({ length: 40 }, (_, i) => `<circle cx="${(rnd(i) * 1080 + t * 12 * (rnd(i + 2) - 0.5) * 4 + 1080) % 1080}" cy="${(rnd(i + 5) * 1920 - t * 20 + 1920 * 4) % 1920}" r="${1 + rnd(i + 1) * 3}" fill="rgba(255,240,210,${0.15 + 0.2 * rnd(i + 3)})"/>`).join(""); break;
      case "rayo": if (d > 0 && d < 0.5) { flash = Math.max(flash, d < 0.08 ? 0.9 : d > 0.16 && d < 0.24 ? 0.6 : 0); sacude = Math.max(sacude, 6 * (1 - d / 0.5));
          if (d < 0.3) { let px = fx.x ?? 700, py = -200, path = `M${px} ${py}`; for (let k = 1; k < 12; k++) { px += (rnd(k + T0) - 0.5) * 140; py += (fx.y ?? 1200) / 11; path += ` L ${px} ${py}`; }
            mundo += `<path d="${path}" stroke="rgba(200,220,255,.5)" stroke-width="22" fill="none"/><path d="${path}" stroke="#fff" stroke-width="6" fill="none"/>`; } } break;
      case "paginas": { const n = fx.n || 10; for (let i = 0; i < n; i++) { const a = T0 + (T1 - T0) * 0.7 * (i / n), k = (t - a) / ((T1 - T0) * 0.45); if (k < 0 || k > 1.05) continue;
          const [x0, y0] = fx.de, [x1, y1] = fx.a.map((v, j) => v + (rnd(i + j) - 0.5) * (fx.disp ?? 200)), x = lerp(x0, x1, k), y = lerp(y0, y1, k) - Math.sin(k * Math.PI) * (fx.arco ?? 200);
          mundo += `<g transform="translate(${x} ${y}) rotate(${k * 720 * (rnd(i) > .5 ? 1 : -1)}) scale(${0.8 + 0.4 * Math.sin(k * 9)} 1)"><rect x="-40" y="-52" width="80" height="104" rx="4" fill="#fbf8ef" stroke="#bdb6a2" stroke-width="2"/>
            ${[0, 1, 2, 3].map((j) => `<path d="M-28 ${-30 + j * 18} q 8 -6 16 0 t 16 0 t 16 0" stroke="#1e3a8a" stroke-width="3" fill="none"/>`).join("")}</g>`; } break; }
      case "vidrios": if (d > 0 && d < 1.6) { for (let i = 0; i < 30; i++) { const ang = rnd(i) * Math.PI * 2, v = 300 + rnd(i + 1) * 900, x = fx.x + Math.cos(ang) * v * d, y = fx.y + Math.sin(ang) * v * d * 0.6 + 900 * d * d;
          mundo += `<path d="M0 -${10 + rnd(i) * 20} L ${8 + rnd(i + 2) * 14} ${6 + rnd(i) * 10} L -${6 + rnd(i + 3) * 12} 8 Z" transform="translate(${x} ${y}) rotate(${d * 600 * (rnd(i) - .5)})" fill="rgba(200,235,255,.75)" stroke="#fff" stroke-width="2"/>`; }
          flash = Math.max(flash, d < 0.06 ? 0.8 : 0); sacude = Math.max(sacude, 16 * (1 - d / 0.4)); } break;
      case "pum": if (d > 0 && d < 0.75) { const k = rebote(d / 0.18) * (1 - cl((d - 0.55) / 0.2)), pts = Array.from({ length: 24 }, (_, i) => { const r = i % 2 ? 120 : 210 + rnd(i) * 40, a = (i / 24) * Math.PI * 2; return `${Math.cos(a) * r},${Math.sin(a) * r * 0.8}`; }).join(" ");
          mundo += `<g transform="translate(${fx.x} ${fx.y}) rotate(${fx.rot ?? -8}) scale(${k * (fx.s ?? 1)})"><polygon points="${pts}" fill="${fx.color || "#ffd166"}" stroke="#111" stroke-width="10"/>
            <text y="30" text-anchor="middle" font-size="96" font-weight="900" fill="#c01b2c" stroke="#111" stroke-width="5" paint-order="stroke" font-family="Figtree" font-style="italic">${fx.texto}</text></g>`;
          sacude = Math.max(sacude, 22 * (1 - d / 0.35)); flash = Math.max(flash, d < 0.05 ? 0.5 : 0);
          if (fx.a) golpes[fx.a] = { dir: fx.dir ?? 1, k: Math.sin(cl(d / 0.5) * Math.PI) }; } break;
      case "radar": if (t > T0 && t < T1) for (let i = 0; i < 4; i++) { const k = ((t - T0) / 1.4 + i / 4) % 1;
          mundo += `<circle cx="${fx.x}" cy="${fx.y}" r="${60 + k * (fx.r ?? 900)}" fill="none" stroke="rgba(255,60,60,${0.7 * (1 - k)})" stroke-width="${8 * (1 - k) + 2}"/>`; } break;
      case "onda": if (t > T0 && t < T1) for (let i = 0; i < 3; i++) { const k = ((t - T0) / 0.9 + i / 3) % 1;
          mundo += `<path d="M${fx.x - 40 - k * 120} ${fx.y - 40 - k * 80} A ${60 + k * 150} ${60 + k * 150} 0 0 1 ${fx.x + 40 + k * 120} ${fx.y - 40 - k * 80}" fill="none" stroke="rgba(255,90,90,${0.9 * (1 - k)})" stroke-width="6"/>`; } break;
      case "qr": { const n = fx.mesas.length; fx.mesas.forEach(([mx, my], i) => { const a = T0 + (T1 - T0) * (i / n), k = (t - a) / 0.35; if (k < 0) return;
          if (k < 1.3) mundo += `<line x1="${fx.de[0]}" y1="${fx.de[1]}" x2="${lerp(fx.de[0], mx, cl(k))}" y2="${lerp(fx.de[1], my - 160, cl(k))}" stroke="#7fe0ff" stroke-width="${10 * (1.3 - k)}" opacity=".9"/>`;
          if (k > 0.9) { const q = rebote((k - 0.9) / 0.6); mundo += `<g transform="translate(${mx} ${my - 170}) scale(${q})"><rect x="-46" y="-46" width="92" height="92" rx="14" fill="#fff" stroke="#2fbbe8" stroke-width="6"/>
              ${Array.from({ length: 16 }, (_, j) => rnd(j + i * 3) > 0.45 ? `<rect x="${-30 + (j % 4) * 15}" y="${-30 + Math.floor(j / 4) * 15}" width="13" height="13" fill="#0b1626"/>` : "").join("")}
              <circle cx="40" cy="-40" r="20" fill="#2ee59d" stroke="#fff" stroke-width="4"/><path d="M30 -40 l 7 7 l 13 -14" stroke="#fff" stroke-width="5" fill="none"/></g>`;
            if (fx.cocina) { const c = (k - 1.2) / 1.2; if (c > 0 && c < 1) mundo += `<g transform="translate(${lerp(mx, fx.cocina[0], ease(c))} ${lerp(my - 170, fx.cocina[1], ease(c)) - Math.sin(c * Math.PI) * 120}) scale(${1 - 0.4 * c})"><rect x="-60" y="-30" width="120" height="60" rx="10" fill="#0b1626" stroke="#2fbbe8" stroke-width="4"/><text y="10" text-anchor="middle" font-size="22" font-weight="800" fill="#bff6ff" font-family="Figtree">PEDIDO</text></g>`; } } }); break; }
      case "disparo": if (d > 0 && d < 1.4) { const k = cl(d / 0.32), x = lerp(fx.de[0], fx.a[0], k), y = lerp(fx.de[1], fx.a[1], k);
          if (k < 1) mundo += `<line x1="${lerp(fx.de[0], fx.a[0], Math.max(0, k - 0.35))}" y1="${lerp(fx.de[1], fx.a[1], Math.max(0, k - 0.35))}" x2="${x}" y2="${y}" stroke="${fx.color || "#7fe0ff"}" stroke-width="26" stroke-linecap="round" opacity=".55"/><circle cx="${x}" cy="${y}" r="38" fill="#fff"/><circle cx="${x}" cy="${y}" r="70" fill="url(#halo)"/>
            <text x="${x}" y="${y + 12}" text-anchor="middle" font-size="34" font-weight="900" fill="#0b1626" font-family="Figtree">${fx.texto || "0 %"}</text>`;
          else { const e = (d - 0.32) / 1.0; mundo += `<circle cx="${fx.a[0]}" cy="${fx.a[1]}" r="${40 + e * 420}" fill="none" stroke="rgba(255,255,255,${1 - e})" stroke-width="${30 * (1 - e)}"/><circle cx="${fx.a[0]}" cy="${fx.a[1]}" r="${200 * (1 - e)}" fill="url(#halo)"/>`;
            for (let i = 0; i < 14; i++) { const ang = rnd(i + T0) * Math.PI * 2, v = 300 + rnd(i) * 500; mundo += `<g transform="translate(${fx.a[0] + Math.cos(ang) * v * e} ${fx.a[1] + Math.sin(ang) * v * e + 700 * e * e}) scale(${Math.abs(Math.cos(e * 20 + i))} 1)"><circle r="20" fill="#f4c430" stroke="#9a7410" stroke-width="4"/><text y="8" text-anchor="middle" font-size="20" font-weight="900" fill="#9a7410" font-family="Figtree">$</text></g>`; } }
          if (d > 0.3 && d < 0.4) { flash = Math.max(flash, 0.6); } if (d > 0.32) sacude = Math.max(sacude, 20 * (1 - (d - 0.32) / 0.4));
          if (fx.golpea) golpes[fx.golpea] = { dir: fx.dir ?? 1, k: d > 0.32 ? Math.sin(cl((d - 0.32) / 0.5) * Math.PI) : 0 }; } break;
      case "monedas": { const n = fx.n || 12; for (let i = 0; i < n; i++) { const a = T0 + (T1 - T0) * 0.6 * (i / n), k = (t - a) / ((T1 - T0) * 0.4); if (k < 0 || k > 1) continue;
          mundo += `<g transform="translate(${lerp(fx.de[0], fx.a[0], ease(k))} ${lerp(fx.de[1], fx.a[1], ease(k)) - Math.sin(k * Math.PI) * 300}) scale(${Math.abs(Math.cos(k * 12 + i))} 1)"><circle r="24" fill="#f4c430" stroke="#9a7410" stroke-width="4"/><text y="9" text-anchor="middle" font-size="24" font-weight="900" fill="#9a7410" font-family="Figtree">$</text></g>`; } break; }
      case "velocidad": if (t > T0 && t < T1) pantalla += Array.from({ length: 40 }, (_, i) => { const a = rnd(i) * Math.PI * 2, r0 = 380 + ((t * 2400 + rnd(i + 1) * 900) % 900), r1 = r0 + 160;
          return `<line x1="${540 + Math.cos(a) * r0}" y1="${960 + Math.sin(a) * r0}" x2="${540 + Math.cos(a) * r1}" y2="${960 + Math.sin(a) * r1}" stroke="rgba(255,255,255,.5)" stroke-width="5"/>`; }).join(""); break;
      case "confeti": if (d > 0) pantalla += Array.from({ length: 70 }, (_, i) => `<rect x="${rnd(i) * 1080 + Math.sin(t * 3 + i) * 30}" y="${-60 + d * (500 + rnd(i + 1) * 600) - rnd(i + 2) * 600}" width="16" height="9" fill="${["#ffd166", "#2fbbe8", "#2ee59d", "#ff5c8a"][i % 4]}" transform="rotate(${t * 300 * (rnd(i) - .5)} ${rnd(i) * 1080} ${-60 + d * 800})"/>`).join(""); break;
      case "destello": if (d > 0 && d < 0.9) { const k = Math.sin(cl(d / 0.9) * Math.PI); mundo += `<g opacity="${k}"><circle cx="${fx.x}" cy="${fx.y}" r="${160 + 100 * k}" fill="url(#halo)"/><path d="M${fx.x - 500 * k} ${fx.y} L ${fx.x + 500 * k} ${fx.y} M${fx.x} ${fx.y - 300 * k} L ${fx.x} ${fx.y + 300 * k}" stroke="#fff" stroke-width="4"/></g>`; } break;
    }
  }
  return { mundo, pantalla, sacude, flash, golpes };
}
// ---------- Cámara
function camara(pl, p) {
  const c = pl.cam || [[540, 960, 1, 0], [540, 960, 1, 0]];
  if (c[0].length === 5) { let i = 0; while (i < c.length - 2 && p >= c[i + 1][0]) i++; const [p0, ...a] = c[i], [p1, ...b] = c[Math.min(i + 1, c.length - 1)], k = ease((p - p0) / Math.max(0.001, p1 - p0)); return a.map((v, j) => lerp(v, b[j], k)); }
  const k = CURVAS[pl.curva || "ease"](p); return c[0].map((v, j) => lerp(v, c[1][j], k));
}
const GRADOS = { noche: "contrast(1.12) saturate(.85) brightness(.95)", calido: "contrast(1.06) saturate(1.12) sepia(.12)", sepia: "sepia(.85) contrast(1.15) brightness(.88)",
  radar: "grayscale(1) contrast(1.9) brightness(.8) sepia(1) hue-rotate(-42deg) saturate(8)", frio: "contrast(1.1) saturate(.75) hue-rotate(8deg)", epico: "contrast(1.18) saturate(1.15)",
  ...(typeof GRADOS_EXTRA === "object" ? GRADOS_EXTRA : {}) };
let ultSub = "", ultPed = "";
async function render(t, f) {
  const i = planoEn(t), pl = EP.planos[i], L = P[i], p = cl((t - L.ini) / (L.fin - L.ini)), tt = t - L.ini;
  const fx = efectos(pl, L, t), fo = resolver(pl.fondoOp || {}, p);
  let [cx, cy, z, r] = camara(pl, p);
  const mano = pl.mano ?? 4, sh = fx.sacude;
  const sx = mano * Math.sin(t * 1.3) + sh * Math.sin(f * 7.1), sy = mano * Math.cos(t * 1.1) + sh * Math.cos(f * 5.3);
  const k = pl.paralaje ?? 0.55, zf = 1 + (z - 1) * k;
  $("#fondo").innerHTML = `<svg viewBox="0 0 1080 1920" width="1080" height="1920">${ESC_DEFS}${HDEFS}<g transform="translate(${540 + sx * k} ${960 + sy * k}) rotate(${r}) scale(${zf}) translate(${-(540 + (cx - 540) * k)} ${-(960 + (cy - 960) * k)})">${FONDOS[pl.fondo](t, fo)}</g></svg>`;
  $("#fondo").style.filter = pl.dof ? `blur(${pl.dof}px)` : "none";
  $("#mundo").innerHTML = `<svg viewBox="0 0 1080 1920" width="1080" height="1920">${ARMA_DEFS}${HDEFS}<g transform="translate(${540 + sx} ${960 + sy}) rotate(${r}) scale(${z}) translate(${-cx} ${-cy})">${actores(pl, L, t, p, fx.golpes)}${fx.mundo}</g></svg>`;
  $("#cine").style.filter = GRADOS[pl.grado] || "none";
  $("#pantalla").innerHTML = `<svg viewBox="0 0 1080 1920" width="1080" height="1920">${fx.pantalla}</svg>`;
  // Transiciones
  const sig = EP.planos[i + 1], fin = L.fin - t;
  let negro = 0; if (pl.trans === "negro") negro = 1 - cl(tt / 0.35); if (sig && sig.trans === "negro") negro = Math.max(negro, 1 - cl(fin / 0.3)); if (t >= SELLO - 0.4) negro = Math.max(negro, cl((t - SELLO + 0.4) / 0.4));
  $("#negro").style.opacity = negro;
  $("#flash").style.opacity = Math.max(fx.flash, pl.trans === "flash" ? 1 - cl(tt / 0.25) : 0);
  $("#cine").style.transform = pl.trans === "barrido" && tt < 0.25 ? `translateX(${(1 - out3(tt / 0.25)) * -260}px)` : "none";
  if (pl.trans === "barrido" && tt < 0.25) $("#cine").style.filter += ` blur(${(1 - tt / 0.25) * 14}px)`;
  // Gancho, título, letrero
  $("#gancho").style.opacity = cl((3.0 - t) / 0.3);
  const ti = $("#titulo");
  if (pl.titulo) { ti.style.opacity = out3((tt - 0.2) / 0.5) * cl((fin - 0.1) / 0.4); $("#titulo b").style.backgroundPosition = `${120 - 140 * cl(tt / (L.fin - L.ini))}% 0`;
    ti.style.transform = `translate(-50%,-50%) scale(${1.12 - 0.12 * out3(tt / 2)})`; } else ti.style.opacity = 0;
  const le = $("#letrero");
  if (pl.letrero) { const n = Math.floor(cl((tt - 0.3) / 1.2) * pl.letrero.length); le.textContent = pl.letrero.slice(0, n) + (n < pl.letrero.length && f % 12 < 6 ? "▌" : ""); le.style.opacity = cl((fin - 0.1) / 0.3) * (tt > 0.25 ? 1 : 0); } else le.style.opacity = 0;
  // Subtítulos
  const l = TODAS.find((x) => t >= x.ini - 0.05 && t < x.fin + 0.25), sub = $("#sub");
  if (l && t < SELLO) { if (ultSub !== l.txt + l.ini) { ultSub = l.txt + l.ini; const rp = EP.reparto[l.quien];
      sub.innerHTML = `<small style="color:${rp.color}">${rp.nombre}</small>${l.txt}`; sub.className = l.quien === "narrador" ? "narr" : ""; }
    sub.style.opacity = out3((t - l.ini + 0.05) / 0.12) * cl((l.fin + 0.25 - t) / 0.12); } else sub.style.opacity = 0;
  // Tarjeta de pedido (la publicidad escondida)
  let ped = null; for (let j = 0; j <= i; j++) EP.planos[j].lineas.forEach((ln, kk) => { const e = ln[3] || {}; if (e.pedido && t >= P[j].lineas[kk].ini && t < P[j].lineas[kk].ini + (e.dur || 3.4)) ped = [e.pedido, P[j].lineas[kk].ini]; });
  const pe = $("#pedido"); if (ped) { const [a, b] = ped[0].split("|"); if (ultPed !== a) { ultPed = a; pe.innerHTML = `<i></i><b>${a}</b><span>${b || ""}</span>`; }
    pe.style.opacity = out3((t - ped[1]) / 0.25); pe.style.transform = `translateX(-50%) translateY(${50 * (1 - out3((t - ped[1]) / 0.35))}px)`; } else pe.style.opacity = 0;
  // Sello final
  if (t >= SELLO) { const s = t - SELLO; $("#sello").style.opacity = out3(s / 0.5);
    $("#o-final").innerHTML = `<svg viewBox="-260 -260 520 620" width="640" height="760">${ARMA_DEFS}${HDEFS}${orbiHeroe(t, EP.selloTraje || "normal", s < 0.6 ? "normal" : "guino", false, { viento: 0.4 })}</svg>`;
    $("#frase").style.opacity = out3((s - 0.3) / 0.4); $("#logo").style.opacity = out3((s - 0.8) / 0.5); } else $("#sello").style.opacity = 0;
  grano(f);
}
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
const PROD = { dom: ["Apex Domicilios", "Sus domicilios, sin comisiones"], play: ["Apex Play", "Pida desde la mesa con un QR"] }[EP.producto];
$("#gancho").innerHTML = EP.gancho; $("#logo b").innerHTML = `<i></i>${PROD[0]}`; $("#logo span").textContent = PROD[1]; $("#frase").textContent = EP.frase || "";
{ const tp = EP.planos.find((p) => p.titulo); if (tp) { $("#titulo b").textContent = tp.titulo[0]; $("#titulo small").textContent = tp.titulo[1] || ""; } }
