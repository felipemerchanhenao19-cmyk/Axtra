// Videos corporativos de Apex para dueños de restaurante: gráficos animados, cifras reales y el sistema grabado en pantalla.
// EP = guion (planos con tipo y datos), LINEA = tiempos de cada plano y cada voz (del motor de «heroes»). render(t, f) es asíncrona.
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const lerp = (a, b, k) => a + (b - a) * k;
const P = LINEA.planos, SELLO = LINEA.sello, TODAS = P.flatMap((p) => p.lineas);
const pesos = (n) => "$ " + Math.round(n).toLocaleString("es-CO");
const VIDEOS = {};
function video(ruta, clave) { if (!VIDEOS[clave]) { const v = document.createElement("video"); v.src = "file://" + GRAB + ruta; v.muted = true; v.preload = "auto"; VIDEOS[clave] = v; } return VIDEOS[clave]; }
async function buscar(v, t) {
  if (v.readyState < 2) await new Promise((r) => { v.addEventListener("loadeddata", r, { once: true }); setTimeout(r, 4000); });
  t = Math.max(0, Math.min(t, (v.duration || 999) - 0.05)); if (Math.abs(v.currentTime - t) < 0.001) return;
  await new Promise((r) => { v.addEventListener("seeked", r, { once: true }); v.currentTime = t; setTimeout(r, 3000); });
}
// Construye el HTML de cada plano una sola vez
const ESC = EP.planos.map((pl, i) => {
  const d = document.createElement("div"); d.className = "plano"; let h = "";
  switch (pl.tipo) {
    case "portada": h = `<div class="portada"><div class="sup">${pl.sup || ""}</div><div class="tit">${pl.titulo}</div><div class="sub">${pl.sub || ""}</div></div>`; break;
    case "cifra": h = `<div class="cifra"><div class="eti">${pl.etiqueta}</div><div class="val ${pl.color || ""}">$ 0</div><div class="nota">${pl.nota || ""}</div></div>`; break;
    case "comparacion": h = `<div class="compa"><div class="sup">${pl.sup || ""}</div><div class="tit">${pl.titulo}</div>${pl.items.map((it) => `<div class="fila ${it.tono || ""}"><div class="nom">${it.nombre}<small>${it.nota || ""}</small></div><div class="barra" style="width:0"><b>${it.texto || ""}</b></div></div>`).join("")}</div>`; break;
    case "lista": h = `<div class="lista"><div class="sup">${pl.sup || ""}</div><div class="tit">${pl.titulo}</div>${pl.items.map((x) => `<div class="item"><i></i><span>${x}</span></div>`).join("")}</div>`; break;
    case "demo": h = `<div class="demo"><div class="sup">${pl.sup || ""}</div><div class="paso">${pl.titulo}</div></div><div class="cel"></div>`; break;
    case "caja": h = `<div class="demo"><div class="sup">${pl.sup || ""}</div><div class="paso">${pl.titulo}</div></div><div class="lap"><div class="pan"></div><div class="base"></div></div>`; break;
    case "pasos": h = `<div class="pasos"><div class="sup">${pl.sup || ""}</div><div class="tit">${pl.titulo}</div>${pl.pasos.map(([a, b], k) => `<div class="pa"><div class="n">${k + 1}</div><div><b>${a}</b><span>${b}</span></div></div>`).join("")}</div>`; break;
    case "precios": h = `<div class="precios"><div class="sup">${pl.sup || ""}</div><div class="tit">${pl.titulo}</div>${pl.tarjetas.map((c) => `<div class="tarjeta"><h3><span class="pin"></span>${c.nombre}</h3>${c.lineas.map(([a, b, antes]) => `<div class="linea"><span>${a}</span><span>${antes ? `<s>${antes}</s>` : ""}<b>${b}</b></span></div>`).join("")}</div>`).join("")}</div>`; break;
    case "pregunta": h = `<div class="pregunta"><div class="sup">${pl.sup || "Pregunta frecuente"}</div><div class="tit">${pl.pregunta}</div><div class="resp">${pl.respuesta}</div></div>`; break;
    case "cierre": h = `<div class="cierre"><div class="logo"><span class="pin"></span>${pl.producto}</div><div class="frase">${pl.frase}</div><div class="wa"><i></i><div><small>Escríbanos por WhatsApp</small><b>310 789 7960</b></div></div><div class="pie">Apex Corporation · Software e inteligencia artificial para empresas</div></div>`; break;
  }
  d.innerHTML = h; $("#planos").appendChild(d);
  if (pl.tipo === "demo") d.querySelector(".cel").appendChild(video(pl.video, i));
  if (pl.tipo === "caja") d.querySelector(".pan").appendChild(video(pl.video, i));
  return d;
});
$("#marca").innerHTML = `Apex Corporation<span>${EP.marca || ""}</span>`;
const aparece = (el, k, dy = 40) => { el.style.opacity = out3(k); el.style.transform = `translateY(${dy * (1 - out3(k))}px)`; };
let ultSub = "";
async function render(t, f) {
  let i = 0; P.forEach((p, k) => { if (t >= p.ini) i = k; });
  const pl = EP.planos[i], L = P[i], tt = t - L.ini, dur = L.fin - L.ini, p = cl(tt / dur), fin = L.fin - t;
  ESC.forEach((d, k) => (d.style.opacity = k === i ? 1 : 0));
  const d = ESC[i]; d.style.opacity = cl(tt / 0.35) * (i < P.length - 1 ? cl(fin / 0.3) : 1);
  // Fondo con movimiento lento
  $("#rejilla").style.transform = `translate(${(t * 14) % 120}px, ${(t * 9) % 120}px)`;
  document.querySelectorAll(".luz").forEach((l, k) => { l.style.left = `${300 + 380 * Math.sin(t * 0.17 + k * 2)}px`; l.style.top = `${600 + 520 * Math.cos(t * 0.13 + k * 3)}px`; l.style.transform = "translate(-50%,-50%)"; });
  const sup = d.querySelector(".sup"); if (sup) aparece(sup, tt / 0.5, 20);
  const tit = d.querySelector(".tit, .paso"); if (tit) aparece(tit, (tt - 0.15) / 0.6);
  switch (pl.tipo) {
    case "portada": aparece(d.querySelector(".sub"), (tt - 0.6) / 0.6); break;
    case "cifra": { const v = d.querySelector(".val"), k = out3((tt - 0.3) / 1.4); v.innerHTML = pesos(pl.valor * k) + (pl.sufijo ? `<small style="font-size:.4em;letter-spacing:0;opacity:${k > 0.98 ? 1 : 0}">${pl.sufijo}</small>` : "");
      aparece(d.querySelector(".eti"), tt / 0.5); aparece(d.querySelector(".nota"), (tt - 1.4) / 0.5); v.style.transform = `scale(${1 + 0.04 * Math.sin(cl((tt - 1.6) / 0.4) * Math.PI)})`; break; }
    case "comparacion": { const mx = Math.max(...pl.items.map((x) => x.valor));
      d.querySelectorAll(".fila").forEach((fila, k) => { const a = 0.6 + k * (pl.paso ?? 0.9), q = out3((tt - a) / 1.0); aparece(fila, (tt - a + 0.2) / 0.4, 20);
        const b = fila.querySelector(".barra"); b.style.width = `${Math.max(1.5, (pl.items[k].valor / mx) * (pl.ancho ?? 62)) * q}%`; b.querySelector("b").textContent = pl.items[k].texto || pesos(pl.items[k].valor * q); }); break; }
    case "lista": { const its = d.querySelectorAll(".item"), n = its.length; its.forEach((el, k) => aparece(el, (tt - 0.7 - k * Math.max(0.5, (dur - 1.8) / n)) / 0.45, 30)); break; }
    case "pasos": { const its = d.querySelectorAll(".pa"), n = its.length; its.forEach((el, k) => aparece(el, (tt - 0.7 - k * Math.max(0.6, (dur - 1.8) / n)) / 0.45, 30)); break; }
    case "precios": d.querySelectorAll(".tarjeta").forEach((el, k) => aparece(el, (tt - 0.6 - k * 1.2) / 0.5, 40)); break;
    case "pregunta": aparece(d.querySelector(".resp"), (tt - (L.lineas[1] ? L.lineas[1].ini - L.ini - 0.1 : 1.6)) / 0.5, 30); break;
    case "cierre": aparece(d.querySelector(".logo"), tt / 0.6); aparece(d.querySelector(".frase"), (tt - 0.5) / 0.6); aparece(d.querySelector(".wa"), (tt - 1.1) / 0.6); aparece(d.querySelector(".pie"), (tt - 1.6) / 0.6, 10); break;
    case "demo": { const c = d.querySelector(".cel"), z = lerp(pl.zoom?.[0] ?? 0.92, pl.zoom?.[1] ?? 0.96, ease(p)); c.style.transform = `scale(${z}) translateY(${30 * (1 - out3(tt / 0.6))}px)`;
      await buscar(VIDEOS[i], Math.min(pl.desde + tt * (pl.vel ?? 1), pl.hasta)); break; }
    case "caja": { const v = VIDEOS[i], [x0, y0, z0] = pl.cam?.[0] ?? [0, 0, 1], [x1, y1, z1] = pl.cam?.[1] ?? [0, 0, 1], k = ease(p), z = lerp(z0, z1, k);
      v.style.transform = `scale(${z}) translate(${-lerp(x0, x1, k) * 964}px, ${-lerp(y0, y1, k) * 670}px)`; aparece(d.querySelector(".lap"), tt / 0.6, 40);
      await buscar(v, Math.min(pl.desde + tt * (pl.vel ?? 1), pl.hasta)); break; }
  }
  // Subtítulos de la narración
  const l = TODAS.find((x) => t >= x.ini - 0.05 && t < x.fin + 0.2), sub = $("#sub");
  if (l) { if (ultSub !== l.txt + l.ini) { ultSub = l.txt + l.ini; sub.textContent = l.txt; } sub.style.opacity = out3((t - l.ini + 0.05) / 0.12) * cl((l.fin + 0.2 - t) / 0.12); } else sub.style.opacity = 0;
  $("#nota").textContent = pl.nota || ""; $("#nota").style.opacity = pl.nota ? cl(tt / 0.6) : 0;
  $("#negro").style.opacity = Math.max(1 - cl(t / 0.4), cl((t - (LINEA.dur - 0.5)) / 0.5));
  grano(f);
}
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
