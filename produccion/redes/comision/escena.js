// «La Comisión — Capítulo 1: El reencuentro». render(t, f)
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const rebote = (x) => { x = cl(x); return 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
const E = LINEA.escenas, L = LINEA.lineas;
const escenaDe = (t) => Object.keys(E).find((k) => t >= E[k][0] && t < E[k][1]) || "sello";
const habla = (q, t) => L.some((l) => l.quien === q && t >= l.ini && t < l.fin);
const lin = (q, esc, n = 0) => L.filter((l) => l.quien === q && (!esc || l.esc === esc))[n];
const boca = (t) => 0.25 + 0.6 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 4.7));
const g = (x, y, s, c, op = 1, rot = 0) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})" opacity="${op}">${c}</g>`;
const CAM = { titulo: [[540, 1250, 1], [540, 1250, 1]], entrada: [[580, 1250, 1.3], [600, 1250, 1.36]], cobro: [[600, 1240, 1.38], [620, 1240, 1.45]],
  orbi: [[580, 1170, 1.25], [580, 1160, 1.3]], drama: [[760, 1230, 1.3], [700, 1200, 1.35]], llanto: [[760, 1250, 1.5], [760, 1250, 1.6]],
  salida: [[660, 1250, 1.25], [660, 1250, 1.25]], final: [[450, 1180, 1.4], [450, 1170, 1.48]], sello: [[540, 1250, 1], [540, 1250, 1]] };
function camara(t) {
  const k = escenaDe(t), [a, b] = E[k], p = (t - a) / (b - a), [c0, c1] = CAM[k], orden = Object.keys(E), prev = orden[orden.indexOf(k) - 1];
  let c = c0.map((v, i) => lerp(v, c1[i], ease(p)));
  if (prev && k !== "sello" && prev !== "titulo") { const pc = CAM[prev][1], q = ease((t - a) / 0.6); c = c.map((v, i) => lerp(pc[i], v, q)); }
  if (k === "drama") { const l = lin("comi", "drama"); if (l) { let z = 0; [0, 0.35, 0.7].forEach((d, i) => { if (t >= l.ini + d) z = i + 1; });
      const fuera = ease((t - l.fin - 0.15) / 0.4); c = [lerp(780, c[0], fuera), lerp(1230, c[1], fuera), lerp([1.3, 1.75, 2.15, 2.55][z], c[2], fuera)];
      const o = lin("orbi", "drama"); if (o) { const q = ease((t - o.ini + 0.3) / 0.5); c = c.map((v, i) => lerp(v, [560, 1120, 1.4][i], q)); } } }
  if (k === "llanto") { const r = lin("rosa", "llanto"); if (r) { const q = ease((t - r.ini + 0.3) / 0.4); c = c.map((v, i) => lerp(v, [340, 1260, 1.6][i], q)); } }
  return c;
}
function orbiCara(t, nombre, h) {
  const base = { ...EXPRESIONES[nombre] };
  if (h) { const a = 0.25 + 0.55 * Math.abs(Math.sin(t * 16)) * (0.6 + 0.4 * Math.sin(t * 5.3)); base.boca = nombre === "feliz" ? [0.9, 1.2, Math.max(0.2, a)] : [0.15, 0.7, a]; }
  if ((t % 3.3) < 0.12 && base.oi > 0) { base.oi = 0.08; if (base.od > 0) base.od = 0.08; }
  return orbi(nombre, { e: base, anillo: -10 + 4 * Math.sin(t * 1.3) }).replace("<svg ", '<svg width="380" height="380" ');
}
let ultimo = "";
async function render(t, f) {
  const k = escenaDe(t), [a, b] = E[k], tt = t - a;
  let w = restaurante(t, 1);
  // puerta a la derecha
  w += `<rect x="930" y="760" width="220" height="380" rx="8" fill="#3a2414" stroke="#2a1a0e" stroke-width="10"/><circle cx="955" cy="960" r="10" fill="#d9b25a"/>`;
  // Doña Rosa detrás del mostrador
  const hr = habla("rosa", t);
  let rCejas = "", rBoca = hr ? boca(t) : 0.4, rBrazo = 0;
  if (k === "cobro" || k === "drama") { rCejas = "enojo"; rBoca = hr ? boca(t) * 1.2 : 0.15; }
  if (k === "llanto") rBoca = hr ? boca(t) : 0.35;
  if (k === "final") { rCejas = "arriba"; rBoca = hr ? 0.95 : 0.8; }
  if (k === "entrada") rBrazo = Math.sin(t * 6) > 0 ? 1 : 0;
  w += g(330, 1385 + Math.sin(t * 2) * 3, 1.3, rosa({ boca: rBoca, cejas: rCejas, brazo: rBrazo, mira: k === "final" ? 4 : 6 }));
  // mostrador y plata
  const lc = lin("comi", "cobro"), quitados = lc ? Math.floor(cl((t - lc.ini) / (lc.fin - lc.ini + 0.3)) * 6) : 0;
  const pila = ["titulo", "entrada"].includes(k) ? 12 : 12 - (k === "cobro" ? quitados : 6);
  w += g(540, 1450, 1, mostrador() + billetes(pila));
  if (k === "cobro" && lc) for (let i = 0; i < 6; i++) { const ti = (t - lc.ini - i * 0.35) / 0.9; if (ti < 0 || ti > 1) continue;
    const x = lerp(370, 790, ti), y = lerp(1420, 1260, ti) - Math.sin(ti * Math.PI) * 260; w += billete(x, y, ti * 540); }
  // Comi
  if (!["titulo", "sello"].includes(k)) {
    let cx = 790, cy = 1335, cs = 0.85, cara = "diva", rot = 0, abanico = null, brazoArriba = false;
    const hc = habla("comi", t);
    if (k === "entrada") { const q = out3((tt - 0.2) / 1.1); cx = lerp(1250, 790, q); rot = Math.sin(t * 3) * 3; abanico = Math.sin(t * 7) * 12; }
    if (k === "cobro") { cara = hc ? "diva" : "diva"; abanico = Math.sin(t * 7) * 12; const d = lin("comi", "cobro", 1); if (d && t > d.ini) brazoArriba = true; }
    if (k === "orbi") { cara = habla("orbi", t) ? "shock" : "enojo"; }
    if (k === "drama") { cara = "shock"; const o = lin("orbi", "drama"); if (o && t > o.ini) cara = "enojo"; rot = Math.sin(t * 20) * (t < (o ? o.ini : 99) ? 2 : 0); }
    if (k === "llanto") { cara = "llanto"; rot = Math.sin(t * 9) * 3; }
    if (k === "salida") { cara = "enojo"; const q = ease((tt - 1.6) / 0.9); cx = lerp(790, 1350, q); brazoArriba = tt < 1.6; }
    if (k === "final") { cx = 1400; }
    w += g(cx, cy + Math.sin(t * 2.6) * 6, cs, comi({ cara, boca: hc ? boca(t) : 0, abanico, brazoArriba }), 1, rot);
    if (k === "entrada" && tt < 2.6) w += `<path d="M${cx - 60} 300 L ${cx - 260} 1560 L ${cx + 260} 1560 L ${cx + 60} 300Z" fill="rgba(255,190,240,${0.16 * (1 - tt / 2.6)})"/>`;
  }
  // Orbi
  if (["orbi", "drama", "llanto", "salida", "final"].includes(k)) {
    let ox = 560, oy = 1040, os = 0.8, cara = "orgulloso";
    if (k === "orbi") { os = 0.8 * rebote(tt / 0.6); cara = habla("comi", t) ? "sarcastico" : "orgulloso"; }
    if (k === "drama") cara = habla("comi", t) ? "sarcastico" : "feliz";
    if (k === "llanto") cara = "sarcastico";
    if (k === "salida") cara = "guino";
    if (k === "final") { ox = lerp(560, 520, out3(tt / 0.8)); cara = tt > 1.6 ? "guino" : "feliz"; }
    w += `<g transform="translate(${ox} ${oy + Math.sin(t * 2.2) * 12}) scale(${os})"><g transform="translate(-190 -190)">${orbiCara(t, cara, habla("orbi", t))}</g></g>`;
    if (k === "orbi" && tt < 1.0) w += Array.from({ length: 10 }, (_, i) => { const r = tt * 300; return `<circle cx="${560 + Math.cos(i * .63) * r}" cy="${1040 + Math.sin(i * .63) * r}" r="${7 * (1 - tt)}" fill="#bff0ff"/>`; }).join("");
    if (k === "drama") { const o = lin("orbi", "drama"); if (o && t > o.ini - 0.2) { const q = rebote((t - o.ini + 0.2) / 0.5);
      w += `<g transform="translate(560 1290) scale(${q})"><rect x="-230" y="-80" width="460" height="160" rx="26" fill="#0b1626" stroke="#2fbbe8" stroke-width="5"/>
        <text x="-200" y="-24" font-size="34" font-weight="800" fill="#fff" font-family="Figtree">Pedido #24 · Domicilio</text>
        <text x="-200" y="26" font-size="28" fill="#9db0c5" font-family="Figtree">Contra entrega · $ 55.000</text></g>`;
      const qs = rebote((t - o.ini - 0.6) / 0.35); if (t > o.ini + 0.6) w += `<g transform="translate(600 1430) rotate(-8) scale(${2 - qs})"><rect x="-210" y="-50" width="420" height="100" rx="18" fill="rgba(5,30,20,.9)" stroke="#2ee59d" stroke-width="8"/>
        <text x="0" y="18" text-anchor="middle" font-size="52" font-weight="800" fill="#2ee59d" font-family="Figtree">0 % COMISIÓN</text></g>`; } }
  }
  const [cx, cy, cs] = camara(t), salida = lin("comi", "salida"), golpe = salida && t > E.salida[1] - 0.9 && t < E.salida[1] - 0.6 ? 14 : 0;
  const sx = golpe * Math.sin(f * 7.1), sy = golpe * Math.cos(f * 5.3);
  $("#escena").innerHTML = `<svg viewBox="0 0 1080 1920" width="1080" height="1920"><g transform="translate(${540 + sx} ${960 + sy}) scale(${cs}) translate(${-cx} ${-cy})">${w}</g></svg>`;
  // Tintes de telenovela
  const lcd = lin("comi", "drama"); let rojo = 0;
  if (k === "drama" && lcd) rojo = cl((t - lcd.ini) / 0.1) * cl((lcd.fin + 0.3 - t) / 0.3);
  if (k === "llanto") rojo = 0.5;
  if (k === "titulo") rojo = 1.8 * cl((b - t) / 0.5);
  $("#tinte").style.opacity = Math.min(1, rojo * 0.55); $("#tinte").style.background = k === "titulo" ? "radial-gradient(80% 55% at 50% 45%, #96143c 0%, #3c061e 50%, #080208 100%)" : k === "llanto" ? "radial-gradient(70% 60% at 50% 50%, rgba(120,40,160,.2), rgba(60,0,80,.85))" : "radial-gradient(70% 60% at 50% 50%, rgba(200,0,60,.1), rgba(120,0,30,.9))";
  $("#rayas").style.opacity = k === "drama" && lcd && [0, 0.35, 0.7].some((d) => t > lcd.ini + d && t < lcd.ini + d + 0.25) ? 0.7 : 0;
  // Título de telenovela
  $("#titulo").style.opacity = k === "titulo" ? out3(tt / 0.6) * cl((b - t) / 0.4) : 0;
  $("#titulo").style.transform = `translate(-50%,-50%) scale(${1.1 - 0.1 * out3(tt / 1.2)})`;
  $("#brillo").style.backgroundPosition = `${130 - 160 * cl((tt - 0.4) / 1.6)}% 0`;
  // Chip de comisión
  const chip = $("#chip"); chip.style.opacity = (k === "cobro" && lc && t > lc.ini + 0.8) ? 1 : 0;
  // Subtítulos
  const l = L.find((x) => t >= x.ini - 0.05 && t < x.fin + 0.35), sub = $("#sub");
  if (l && k !== "sello") { if (ultimo !== l.txt) { ultimo = l.txt; sub.innerHTML = `<small>${{ orbi: "ORBI", comi: "COMI · LA APP DE SIEMPRE", rosa: "DOÑA ROSA" }[l.quien]}</small>${l.txt}`; sub.className = l.quien; }
    sub.style.opacity = out3((t - l.ini + 0.05) / 0.15) * cl((l.fin + 0.35 - t) / 0.15); } else sub.style.opacity = 0;
  // Sello
  if (k === "sello") { const q = out3(tt / 0.6); $("#sello").style.opacity = q; $("#o-final").innerHTML = orbiCara(t, tt < 0.5 ? "normal" : "guino", false);
    $("#frase").style.opacity = out3((tt - 0.5) / 0.4); $("#logo").style.opacity = out3((tt - 1.1) / 0.5); } else $("#sello").style.opacity = 0;
  grano(f);
}
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
