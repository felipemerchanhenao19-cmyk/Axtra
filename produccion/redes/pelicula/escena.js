// «Películas Apex»: cámara (travelling, grúa, ángulo 3D, enfoque), luz y color por plano, celular/pantalla en 3D con el sistema real,
// textos de cine y cifras proyectadas. EP = guion, LINEA = tiempos (motor de «heroes»). render(t, f) es asíncrona.
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const lerp = (a, b, k) => a + (b - a) * k;
const P = LINEA.planos, TODAS = P.flatMap((p) => p.lineas);
const pesos = (n) => "$ " + Math.round(n).toLocaleString("es-CO");
function resolver(v, p) {
  if (v && typeof v === "object" && !Array.isArray(v)) { if (v.anim) { const [a, b, p0 = 0, p1 = 1] = v.anim; return lerp(a, b, ease((p - p0) / Math.max(0.001, p1 - p0))); }
    const r = {}; for (const k in v) r[k] = resolver(v[k], p); return r; }
  return v;
}
function claves(c, p, def) {   // [[x,...],[x,...]] o [[p, x, ...], ...]
  if (!c) return def; if (c.length === 2 && c[0].length === def.length) return c[0].map((v, j) => lerp(v, c[1][j], ease(p)));
  let i = 0; while (i < c.length - 2 && p >= c[i + 1][0]) i++; const [p0, ...a] = c[i], [p1, ...b] = c[Math.min(i + 1, c.length - 1)];
  return a.map((v, j) => lerp(v, b[j], ease((p - p0) / Math.max(0.001, p1 - p0))));
}
const GRADOS = { ambar: "contrast(1.15) saturate(1.1) sepia(.18)", noche: "contrast(1.2) saturate(.9) brightness(.92)", frio: "contrast(1.15) saturate(.85) hue-rotate(6deg)",
  rojo: "contrast(1.25) saturate(1.2)", limpio: "contrast(1.1) saturate(1.05)", sueño: "contrast(1.05) saturate(1.2) brightness(1.04)" };
// Dispositivos con la grabación real
const VID = {};
function vid(i, ruta) { if (!VID[i]) { const v = document.createElement("video"); v.src = "file://" + GRAB + ruta; v.muted = true; v.preload = "auto"; VID[i] = v; } return VID[i]; }
async function buscar(v, t) {
  if (v.readyState < 2) await new Promise((r) => { v.addEventListener("loadeddata", r, { once: true }); setTimeout(r, 5000); });
  t = Math.max(0, Math.min(t, (isFinite(v.duration) ? v.duration : 999) - 0.05)); if (Math.abs(v.currentTime - t) < 0.001) return;
  await new Promise((r) => { v.addEventListener("seeked", r, { once: true }); v.currentTime = t; setTimeout(r, 3000); });
}
// El cuadro del video se copia a un lienzo después de cada búsqueda: así nunca sale la pantalla en negro por un cuadro aún sin pintar
function lienzo(v) { if (!v._lz) v._lz = document.createElement("canvas"); return v._lz; }
function pintar(v) { const c = lienzo(v); if (!v.videoWidth) return; if (c.width !== v.videoWidth) { c.width = v.videoWidth; c.height = v.videoHeight; } c.getContext("2d").drawImage(v, 0, 0); }
EP.planos.forEach((pl, i) => { if (pl.dispositivo) vid(i, pl.dispositivo.video); });
let ultSub = "", ultTexto = -1;
async function render(t, f) {
  let i = 0; P.forEach((p, k) => { if (t >= p.ini) i = k; });
  const pl = EP.planos[i], L = P[i], tt = t - L.ini, dur = L.fin - L.ini, p = cl(tt / dur), fin = L.fin - t;
  const op = { ...resolver(pl.op || {}, p), _tt: tt };
  // Cámara: posición, zoom, giro, ángulo 3D y un leve pulso de cámara en mano
  const [cx, cy, z, rot] = claves(pl.cam, p, [540, 960, 1, 0]), [rx, ry] = claves(pl.angulo, p, [0, 0]);
  const mano = pl.mano ?? 3, hx = mano * Math.sin(t * 1.1) + mano * 0.5 * Math.sin(t * 2.7), hy = mano * Math.cos(t * 0.9);
  const esc = ESCENARIOS[pl.escenario](t, op), k = pl.paralaje ?? 0.6;
  const g = (fz, extra = "") => `<svg viewBox="0 0 1080 1920" width="1080" height="1920" style="overflow:visible">${extra}<g transform="translate(${540 + hx * fz} ${960 + hy * fz}) rotate(${rot * fz}) scale(${1 + (z - 1) * fz}) translate(${-(540 + (cx - 540) * fz)} ${-(960 + (cy - 960) * fz)})">`;
  let orbeSvg = "";
  if (pl.orbe) { const o = resolver(pl.orbe, p), q = pl.orbe.nace ? cl((tt - pl.orbe.nace[0]) / (pl.orbe.nace[1] - pl.orbe.nace[0])) : 1;
    const dice = TODAS.some((l) => l.quien === "orbe" && t >= l.ini && t < l.fin);
    const estado = dice ? "habla" : (pl.orbe.estado || "reposo"), habla = dice ? nivelVoz(t) : 0.4;
    orbeSvg = q > 0 ? orbe(o.x, o.y + Math.sin(t * 1.6) * 10, o.r, t, { nace: q, estado, habla }) : ""; }
  $("#lejos").innerHTML = g(k, MUNDO_DEFS) + esc.lejos + "</g></svg>";
  $("#medio").innerHTML = g(1) + esc.medio + orbeSvg + "</g></svg>";
  $("#cerca").innerHTML = g(1.35) + (esc.cerca || "") + "</g></svg>";
  // las fotos de los platos tienen que estar pintadas antes de tomar el cuadro
  await Promise.all([...document.querySelectorAll("#medio image")].map((im) => Promise.race([
    im.decode ? im.decode().catch(() => {}) : new Promise((r) => im.addEventListener("load", r, { once: true })), new Promise((r) => setTimeout(r, 3000))])));
  const dof = resolver(pl.foco || {}, p);
  $("#lejos").style.filter = `blur(${dof.lejos ?? 3}px)`; $("#medio").style.filter = `blur(${dof.medio ?? 0}px)`; $("#cerca").style.filter = `blur(${dof.cerca ?? 10}px)`;
  $("#mundo").style.transform = `perspective(1800px) rotateX(${rx}deg) rotateY(${ry}deg) scale(${1 + Math.abs(rx) / 120 + Math.abs(ry) / 120})`;
  $("#mundo").style.filter = GRADOS[pl.grado] || "none";
  $("#tinte").style.background = pl.tinte || "transparent"; $("#tinte").style.opacity = pl.tinte ? (pl.tinteK ?? 0.35) : 0;
  // Haces de luz y destello de lente en pantalla
  const fl = pl.destello ? resolver(pl.destello, p) : null;
  $("#destello").style.opacity = fl ? (fl.k ?? 1) * (0.75 + 0.25 * Math.sin(t * 3)) : 0;
  if (fl) $("#destello").style.background = `radial-gradient(circle at ${fl.x}px ${fl.y}px, rgba(255,255,255,.9) 0, rgba(${fl.color || "160,225,255"},.45) 60px, rgba(${fl.color || "160,225,255"},0) 340px),
    linear-gradient(0deg, transparent ${fl.y - 4}px, rgba(${fl.color || "160,225,255"},.55) ${fl.y}px, transparent ${fl.y + 4}px)`;
  $("#polvo").innerHTML = pl.polvo === false ? "" : `<svg viewBox="0 0 1080 1920" width="1080" height="1920">${Array.from({ length: 50 }, (_, j) => `<circle cx="${(rnd(j) * 1080 + t * 10 * (rnd(j + 2) - 0.5) * 3 + 1080) % 1080}" cy="${(rnd(j + 5) * 1920 - t * 16 + 1920 * 4) % 1920}" r="${1 + rnd(j + 1) * 2.5}" fill="rgba(255,236,210,${0.12 + 0.25 * rnd(j + 3)})"/>`).join("")}</svg>`;
  // Celular o pantalla en 3D con la grabación real
  const dv = $("#dispositivo");
  if (pl.dispositivo) { const d = pl.dispositivo, v = VID[i], [x, y, s, a, b, c] = claves(d.pose, p, [0, 0, 1, 0, 0, 0]);
    if (dv.dataset.i !== String(i)) { dv.dataset.i = i; dv.className = d.tipo; dv.innerHTML = d.tipo === "cel" ? `<div class="pantalla"></div><div class="brillo"></div><div class="isla"></div>` : `<div class="pantalla"></div><div class="brillo"></div><div class="base"></div>`; dv.querySelector(".pantalla").appendChild(lienzo(v)); }
    dv.style.opacity = out3(tt / 0.5) * cl(fin / 0.3);
    dv.style.transform = `translate(-50%,-50%) translate(${x}px, ${y}px) perspective(2000px) rotateX(${a}deg) rotateY(${b}deg) rotateZ(${c}deg) scale(${s})`;
    dv.querySelector(".brillo").style.background = `linear-gradient(${110 + b * 2}deg, rgba(255,255,255,0) ${30 + b}%, rgba(255,255,255,.16) ${42 + b}%, rgba(255,255,255,0) ${55 + b}%)`;
    if (d.cam) { const [vx, vy, vz] = claves(d.cam, p, [0, 0, 1]); v._lz.style.transformOrigin = "0 0"; v._lz.style.transform = `scale(${vz}) translate(${-vx * 100}%, ${-vy * 100}%)`; }
    await buscar(v, Math.min(d.desde + tt * (d.vel ?? 1), d.hasta ?? 999));
    pintar(v);
  } else { dv.style.opacity = 0; dv.dataset.i = ""; }
  // Textos de cine
  const tx = $("#texto");
  if (pl.texto) { const x = pl.texto; if (ultTexto !== i) { ultTexto = i; tx.className = x.estilo || "centro";
      tx.innerHTML = `<small>${x.kicker || ""}</small><b>${(x.titulo || "").split(" ").map((w) => `<span>${w}</span>`).join(" ")}</b>${x.sub ? `<em>${x.sub}</em>` : ""}`; }
    const de = x.desde ?? 0.3, hasta = x.hasta ?? dur;
    tx.style.opacity = cl((tt - de) / 0.4) * cl((Math.min(hasta, dur) - tt) / 0.35);
    tx.querySelectorAll("b span").forEach((s, j) => { const q = out3((tt - de - 0.1 - j * 0.12) / 0.5); s.style.opacity = q; s.style.filter = `blur(${(1 - q) * 10}px)`; s.style.display = "inline-block"; s.style.transform = `translateY(${(1 - q) * 30}px)`; });
    tx.querySelector("small").style.letterSpacing = `${0.3 + 0.25 * (1 - out3((tt - de) / 1.2))}em`;
  } else { tx.style.opacity = 0; ultTexto = -1; }
  // Cifra proyectada (holograma)
  const ci = $("#cifra");
  if (pl.cifra) { const c = pl.cifra, q = out3((tt - (c.desde ?? 0.6)) / (c.dura ?? 1.6)), flick = tt - (c.desde ?? 0.6) < 0.25 ? (Math.sin(t * 90) > 0 ? 1 : 0.3) : 1;
    ci.className = c.color || "cian"; ci.innerHTML = `<small>${c.etiqueta || ""}</small><b>${pesos(c.valor * q)}${c.sufijo ? `<i>${c.sufijo}</i>` : ""}</b>${c.nota ? `<em>${c.nota}</em>` : ""}`;
    ci.style.opacity = cl((tt - (c.desde ?? 0.6) + 0.2) / 0.3) * cl(fin / 0.3) * flick; ci.style.top = `${c.y ?? 760}px`; } else ci.style.opacity = 0;
  // Palabras flotando (idiomas)
  $("#palabras").innerHTML = (pl.palabras || []).map((w, j) => { const a = j * (6.283 / pl.palabras.length) + t * 0.25, q = out3((tt - 0.5 - j * 0.35) / 0.6);
    return `<span style="left:${540 + Math.cos(a) * 360}px;top:${(pl.palabrasY ?? 900) + Math.sin(a) * 240}px;opacity:${q * (0.55 + 0.45 * Math.sin(a + 1.2))}">${w}</span>`; }).join("");
  // Cierre
  const fi = $("#final");
  if (pl.final) { const c = pl.final; if (!fi.dataset.listo) { fi.dataset.listo = 1; fi.innerHTML = `<div class="logo"><span class="pin"></span>${c.producto}</div><div class="frase">${c.frase}</div>${c.detalle ? `<div class="detalle">${c.detalle}</div>` : ""}<div class="wa"><i></i><div><small>Escríbanos por WhatsApp</small><b>310 789 7960</b></div></div><div class="pie">Apex Corporation · Tuluá</div>`; }
    fi.style.opacity = out3((tt - 0.3) / 0.8); [".logo", ".frase", ".detalle", ".wa", ".pie"].forEach((s, j) => { const e = fi.querySelector(s); if (!e) return; const q = out3((tt - 0.4 - j * 0.35) / 0.6); e.style.opacity = q; e.style.transform = `translateY(${(1 - q) * 30}px)`; });
    fi.querySelector(".logo").style.backgroundPosition = `${120 - 160 * cl(tt / 2.5)}% 0`;
  } else fi.style.opacity = 0;
  // Subtítulos de la narración
  const l = TODAS.find((x) => t >= x.ini - 0.05 && t < x.fin + 0.2), sub = $("#sub");
  if (l) { if (ultSub !== l.txt + l.ini) { ultSub = l.txt + l.ini; sub.textContent = l.txt; } sub.style.opacity = out3((t - l.ini + 0.05) / 0.15) * cl((l.fin + 0.2 - t) / 0.15); } else sub.style.opacity = 0;
  $("#nota").textContent = pl.nota || ""; $("#nota").style.opacity = pl.nota ? cl(tt / 0.6) * 0.9 : 0;
  // Transiciones: fundido, destello blanco y fuga de luz cálida
  const sig = EP.planos[i + 1]; let negro = 0;
  if (pl.trans === "negro") negro = 1 - cl(tt / 0.5); if (sig && sig.trans === "negro") negro = Math.max(negro, 1 - cl(fin / 0.4));
  if (t < 0.6) negro = Math.max(negro, 1 - t / 0.6); if (t > LINEA.dur - 0.6) negro = Math.max(negro, cl((t - LINEA.dur + 0.6) / 0.6));
  $("#negro").style.opacity = negro;
  $("#blanco").style.opacity = pl.trans === "flash" ? 1 - cl(tt / 0.3) : 0;
  const fuga = pl.trans === "fuga" ? Math.sin(cl(tt / 0.9) * Math.PI) : 0;
  $("#fuga").style.opacity = fuga; $("#fuga").style.backgroundPosition = `${-40 + 140 * cl(tt / 0.9)}% 0`;
  $("#mundo").style.filter += pl.trans === "barrido" && tt < 0.3 ? ` blur(${(1 - tt / 0.3) * 18}px)` : "";
  grano(f);
}
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
