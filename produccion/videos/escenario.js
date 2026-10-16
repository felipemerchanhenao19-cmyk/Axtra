// Motor de imagen: render(t) dibuja el cuadro del segundo t. Todo es determinista (sin animaciones CSS).
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const lerp = (a, b, k) => a + (b - a) * k;
const lerpP = (A, B, k) => A.map((v, i) => lerp(v, B[i], k));
let escenaActual = null;

function pose(el, p, extra = "") {   // p = [x, y, escala, rotX, rotY, rotZ]
  el.style.transform = `translate(-50%,-50%) translate3d(${p[0]}px,${p[1]}px,0) scale(${p[2]}) rotateX(${p[3]}deg) rotateY(${p[4]}deg) rotateZ(${p[5]}deg) ${extra}`;
}
function palabras(el, html) { // separa en palabras para revelarlas una a una
  el.innerHTML = html.split(/(<br>)/).map((trozo) => trozo === "<br>" ? "<br>" : trozo.split(" ").filter(Boolean).map((w) => `<span class="w">${w}</span>`).join(" ")).join("");
}
function revelar(el, tt, inicio, paso = 0.11, salida = Infinity) {
  el.querySelectorAll(".w").forEach((w, i) => {
    const k = out3((tt - inicio - i * paso) / 0.7), s = cl((salida - tt) / 0.45);
    w.style.opacity = k * s; w.style.filter = `blur(${(1 - k) * 14 + (1 - s) * 10}px)`;
    w.style.transform = `translateY(${(1 - k) * 28}px)`;
  });
}
function luz(color, x, y, intensidad, tam = 70) {
  const c = { fria: "47,150,232", calida: "232,140,60", oro: "232,190,110", blanca: "200,230,255" }[color] || color;
  $("#halo").style.background = `radial-gradient(${tam}% ${tam * 1.2}% at ${x}% ${y}%, rgba(${c},${0.55 * intensidad}) 0%, rgba(${c},${0.16 * intensidad}) 35%, rgba(0,0,0,0) 70%)`;
}
function rayos(op, t) {
  $("#rayos").style.opacity = op;
  $("#rayos").style.transform = `translateX(${Math.sin(t * 0.13) * 60}px) rotate(${-18 + Math.sin(t * 0.07) * 3}deg)`;
}
function grano(f) {
  const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height);
  let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; const v = (s / 233280) * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
  x.putImageData(d, 0, 0);
}
async function pantalla(img, carpeta, n, seg) {
  const i = Math.max(1, Math.min(n, Math.floor(seg * 24) + 1));
  const src = `${carpeta}/${String(i).padStart(5, "0")}.jpg`;
  if (img.dataset.src !== src) { img.dataset.src = src; img.src = src; await img.decode().catch(() => {}); }
}
function reflejo(el, rotY, k = 1) { // brillo del vidrio según el ángulo
  el.querySelector(".brillo").style.background = `linear-gradient(${105 + rotY * 1.5}deg, rgba(255,255,255,0) ${30 + rotY}%, rgba(255,255,255,${0.10 * k}) ${45 + rotY}%, rgba(255,255,255,0) ${60 + rotY}%)`;
  el.style.boxShadow = `${-rotY * 0.8}px 40px 120px rgba(0,0,0,.65), ${rotY * -0.15}px 0 0 1.5px rgba(160,190,220,${0.25 + Math.abs(rotY) / 90}), 0 0 140px rgba(47,187,232,${0.12 * k})`;
}
const ocultar = () => document.querySelectorAll(".capa").forEach((e) => e.style.opacity = 0);

async function render(t, f) {
  const s = TL.find((e) => t >= e.ini && t < e.fin) || TL[TL.length - 1];
  const i = TL.indexOf(s), prev = TL[i - 1], next = TL[i + 1];
  const tt = t - s.ini, D = s.fin - s.ini, tv = s.voz - s.ini, dv = s.dur_voz;
  const entra = out3(tt / 0.6), sale = cl((D - tt) / 0.5), vis = Math.min(entra, sale);
  const nueva = escenaActual !== s.id; escenaActual = s.id;
  ocultar(); grano(f);
  // cámara: deriva lenta permanente
  $("#mundo").style.transform = `scale(${1.02 + 0.015 * Math.sin(t * 0.11)}) translate(${Math.sin(t * 0.09) * 8}px, ${Math.cos(t * 0.07) * 6}px)`;
  $("#flash").style.opacity = 0; rayos(0, t);
  const E = s.e;

  if (E.tipo === "texto") {
    const k = s.id === "apertura" ? out3(tt / 2.4) : 1;
    luz(E.luz, 50, 55, (0.25 + 0.75 * k) * (s.id === "apertura" ? 1 : 0.7), 30 + 40 * k);
    rayos(0.35 * k * sale, t);
    const tiempos = E.lineas.map(([fr]) => tv + fr * dv);
    let j = 0; tiempos.forEach((x, n) => { if (tt >= x) j = n; });
    const [, a, b] = E.lineas[j];
    const llave = s.id + j;
    if ($("#grande").dataset.k !== llave) { $("#grande").dataset.k = llave; palabras($("#grande"), a); palabras($("#grande2"), b || ""); }
    const fin = j < E.lineas.length - 1 ? tiempos[j + 1] - 0.05 : D - 0.1;
    $("#bloque-grande").style.opacity = 1;
    revelar($("#grande"), tt, tiempos[j], 0.12, fin); revelar($("#grande2"), tt, tiempos[j] + 0.6, 0.08, fin);
    $("#bloque-grande").style.transform = `scale(${1 + 0.04 * (tt - tiempos[j]) / 3})`;
  }

  if (E.tipo === "numero") {
    luz("calida", 50, 50, 0.55 * vis, 60); rayos(0.25 * vis, t);
    const k = ease((tt - tv) / (dv * 0.7));
    $("#numero").textContent = Math.round(lerp(E.desde, E.hasta, k)) + E.sufijo;
    $("#bloque-num").style.opacity = vis;
    $("#numero").style.transform = `scale(${0.92 + 0.08 * out3(tt / 1.2) + 0.03 * (tt / D)})`;
    $("#numero").style.filter = `blur(${(1 - out3(tt / 0.9)) * 18}px)`;
    if (nueva) palabras($("#num-pie"), E.pie);
    revelar($("#num-pie"), tt, tv + dv * 0.45, 0.09, D - 0.1);
  }

  if (E.tipo === "revelacion") {
    const hit = tv + dv * 0.62;
    if (nueva) { palabras($("#grande"), E.antes); palabras($("#grande2"), ""); $("#marca-txt").textContent = E.marca; }
    $("#bloque-grande").style.opacity = 1; $("#grande").dataset.k = "";
    revelar($("#grande"), tt, tv, 0.12, hit - 0.35);
    const kh = cl((tt - hit) / 2.2);
    luz("fria", 50, 50, tt < hit ? 0.3 : 0.4 + 0.6 * (1 - kh * 0.4), tt < hit ? 30 : 75);
    rayos((tt < hit ? 0.1 : 0.55) * sale, t);
    $("#flash").style.opacity = tt >= hit ? Math.max(0, 0.85 - (tt - hit) * 1.6) : 0;
    const ko = out3((tt - hit) / 1.4);
    $("#orbe").style.opacity = ko * 0.9 * sale; pose($("#orbe"), [0, -150, 1.15 + 0.2 * ko + 0.03 * (tt - hit), 0, 0, 0]);
    $("#orbe").querySelector(".anillo").style.transform = `rotate(${-14 + 4 * Math.sin(t * 0.6)}deg)`;
    const kl = out3((tt - hit - 0.15) / 1.0);
    $("#marca").style.opacity = kl * sale; $("#marca").style.filter = `blur(${(1 - kl) * 22}px)`;
    $("#marca").style.transform = `translate(-50%,-50%) translateY(150px) scale(${1.12 - 0.12 * kl + 0.02 * cl(tt - hit - 1)})`;
    $("#marca-txt").style.backgroundPosition = `${120 - 140 * cl((tt - hit - 0.5) / 1.6)}% 0`;
  }

  if (E.tipo === "cel" || E.tipo === "tab") {
    const esCel = E.tipo === "cel", dev = esCel ? $("#cel") : $("#tab");
    const A = esCel ? E.pose[0] : [360, 30, 0.9, 10, -30, 1], B = esCel ? E.pose[1] : [390, 20, 0.97, 4, -16, 0];
    let p = lerpP(A, B, ease(tt / D));
    const prevDev = prev && prev.e.tipo === E.tipo;
    if (prevDev) { const PB = prev.e.pose ? prev.e.pose[1] : B; p = lerpP(PB, p, ease(tt / 1.1)); }
    else { const k = out3(tt / 1.3); p = lerpP([A[0], A[1] + 700, A[2] * 0.85, A[3] + 45, A[4], A[5]], p, k); }
    const nextDev = next && next.e.tipo === E.tipo;
    dev.style.opacity = nextDev ? (prevDev ? 1 : out3(tt / 0.5)) : Math.min(prevDev ? 1 : out3(tt / 0.5), sale);
    pose(dev, p); reflejo(dev, p[4], 1);
    await pantalla(dev.querySelector("img"), E.fuente === "c" ? DIR_C : DIR_K, E.fuente === "c" ? N_C : N_K, E.desde + tt);
    $("#sombra").style.opacity = dev.style.opacity * 0.8;
    $("#sombra").style.transform = `translate(-50%,-50%) translate(${p[0]}px, ${esCel ? 470 : 380}px) scale(${p[2] * (esCel ? 1 : 1.8)}, ${p[2] * 0.6})`;
    const lx = 50 + p[0] / 19.2;
    luz(s.id === "oferta" ? "oro" : "fria", lx, 45, 0.85, 55); rayos(0.3, t);
    if (!esCel) { const pulso = Math.max(0, 1 - Math.abs(tt - 2.2) / 0.9); dev.style.boxShadow += `, 0 0 ${80 + 120 * pulso}px rgba(47,187,232,${0.15 + 0.45 * pulso})`; }
    // texto al lado
    if (E.texto !== "idiomas") {
      const T = $("#texto"); T.className = "capa lado-" + E.texto; T.style.opacity = 1;
      if (nueva) { $("#kicker").textContent = E.kicker; palabras($("#titulo"), E.titulo); palabras($("#sub"), E.sub || ""); }
      const k0 = Math.max(0.35, tv - 0.1);
      $("#kicker").style.opacity = out3((tt - k0 + 0.3) / 0.6) * sale; $("#kicker").style.letterSpacing = `${0.5 - 0.2 * out3((tt - k0) / 1.5)}em`;
      revelar($("#titulo"), tt, k0 + 0.15, 0.1, D - 0.15); revelar($("#sub"), tt, k0 + dv * 0.45, 0.06, D - 0.15);
    }
    if (E.chips) E.chips.forEach((c, n) => { const el = $("#chip" + n); el.textContent = c; const k = out3((tt - tv - dv * (0.25 + n * 0.2)) / 0.6);
      el.style.opacity = k * sale; el.style.transform = `translate(-50%,-50%) translate(${[-660, -405, -110][n]}px, ${190 + (1 - k) * 30}px) scale(${0.85 + 0.15 * k})`; });
    if (E.texto === "idiomas") {
      const lista = E.saludos, paso = (D - 0.4) / lista.length, j = Math.min(lista.length - 1, Math.floor(tt / paso)), u = (tt - j * paso) / paso;
      $("#saludo").textContent = lista[j]; $("#saludo").style.opacity = Math.min(out3(u / 0.25), cl((1 - u) / 0.25)) * 0.9;
      $("#saludo").style.transform = `translate(-50%,-50%) translateX(-330px) scale(${0.95 + 0.1 * u})`;
    }
  }

  if (E.tipo === "futuro") {
    luz("fria", 50, 50, 0.75 * vis, 70); rayos(0.4 * vis, t);
    if (nueva) { E.tarjetas.forEach((c, n) => $("#fut" + n).querySelector("b").textContent = c); palabras($("#fut-titulo"), E.titulo); }
    $("#fut-titulo").style.opacity = 1;
    $("#fut-kicker").style.opacity = out3((tt - 0.3) / 0.6) * sale;
    const junta = ease((tt - (tv + dv * 0.78)) / 1.1);
    E.tarjetas.forEach((c, n) => {
      const el = $("#fut" + n), k = out3((tt - tv - dv * (0.3 + n * 0.13)) / 0.7);
      const x = lerp([-520, 0, 520][n], [-140, 0, 140][n], junta), y = lerp(0, -20, junta);
      el.style.opacity = k * Math.pow(1 - junta, 2) * sale;
      el.style.transform = `translate(-50%,-50%) translate3d(${x}px, ${y + (1 - k) * 60}px, 0) rotateY(${[22, 0, -22][n] * (1 - junta)}deg) scale(${1 - 0.3 * junta})`;
    });
    $("#orbe").style.opacity = junta * sale; pose($("#orbe"), [0, -40, 0.6 + 0.5 * junta, 0, 0, 0]);
    $("#orbe").querySelector(".anillo").style.transform = `rotate(${-14 + 4 * Math.sin(t * 0.6)}deg)`;
    revelar($("#fut-titulo"), tt, tv + dv * 0.82, 0.12, D - 0.1);
  }

  if (E.tipo === "logo") {
    const hit = tv - 0.15, kh = out3((tt - hit) / 1.2);
    luz("fria", 50, 48, (0.2 + 0.7 * kh) * sale, 60); rayos(0.5 * kh * sale, t);
    $("#flash").style.opacity = tt >= hit ? Math.max(0, 0.6 - (tt - hit) * 1.4) : 0;
    if (nueva) { $("#marca-txt").textContent = E.marca; palabras($("#lema"), E.lema); }
    $("#orbe").style.opacity = kh * 0.55 * sale; pose($("#orbe"), [0, -190, 0.95 + 0.04 * tt, 0, 0, 0]);
    $("#orbe").querySelector(".anillo").style.transform = `rotate(${-14 + 4 * Math.sin(t * 0.6)}deg)`;
    $("#marca").style.opacity = kh * sale; $("#marca").style.filter = `blur(${(1 - kh) * 20}px)`;
    $("#marca").style.transform = `translate(-50%,-50%) translateY(90px) scale(${1.1 - 0.1 * kh})`;
    $("#marca-txt").style.backgroundPosition = `${120 - 140 * cl((tt - hit - 0.3) / 1.6)}% 0`;
    $("#bloque-lema").style.opacity = 1; revelar($("#lema"), tt, tv + dv * 0.3, 0.1, D - 0.1);
  }

  if (E.tipo === "contacto") {
    luz("fria", 30, 50, 0.6 * vis, 60); rayos(0.25 * vis, t);
    const fin = cl((D - tt) / 1.4);
    $("#contacto").style.opacity = out3(tt / 0.9) * fin;
    $("#c-qr").style.transform = `perspective(1400px) rotateY(${14 - 10 * ease(tt / D)}deg) translateY(${(1 - out3(tt / 1.0)) * 40}px)`;
    $("#c-der").style.transform = `translateX(${(1 - out3((tt - 0.3) / 1.0)) * 40}px)`;
  }
}
