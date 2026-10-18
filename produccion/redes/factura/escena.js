// «La factura» — telenovela. render(t) dibuja el cuadro t (s). Vertical 1080x1920.
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const rebote = (x) => { x = cl(x); const c = 1.70158 + 1; return 1 + c * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2); };
const entre = (t, a, b) => t >= a && t < b;
// Diálogos: [inicio, fin, quién, texto]  (quién: "orbi" o "dueno")
const DIALOGOS = [
  [5.15, 6.45, "dueno", "¿Por qué me haces esto?", "d1"],
  [10.1, 11.5, "orbi", "Ya, ya…", "o1"],
  [11.5, 13.9, "orbi", "Nadie debería pagar por cocinar.", "o2"],
  [15.9, 18.9, "orbi", "Su propio canal. Sin comisiones.", "o3"],
];
// La boca se mueve mientras suena su voz (si hay voces grabadas), si no, durante todo el subtítulo
const HABLA = DIALOGOS.filter((d) => d[2] === "orbi").map((d) => [d[0] + 0.05, VOZ[d[4]] ? d[0] + 0.05 + VOZ[d[4]] : d[1]]);
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
function fondo(t) {
  const drama = t < 9.4 || entre(t, 19.0, 22.6);
  const k = t < 9.4 ? 1 : t < 10.4 ? 1 - (t - 9.4) : entre(t, 19.0, 22.6) ? cl((t - 19.0) / 0.4) * cl((22.6 - t) / 0.3) : 0;
  $("#fondo").style.background = `radial-gradient(80% 55% at 50% 45%, rgba(150,20,60,${0.85 * k}) 0%, rgba(60,6,30,${0.9 * k}) 45%, rgba(8,2,8,${k}) 100%),
    radial-gradient(85% 55% at 50% 45%, #17406f 0%, #0b1626 60%, #050a14 100%)`;
}
async function pantalla(t0, seg) {
  const i = Math.max(1, Math.min(N_K, Math.floor((t0 + seg) * 24) + 1)), src = `${DIR_K}/${String(i).padStart(5, "0")}.jpg`, img = $("#caja img");
  if (img.dataset.src !== src) { img.dataset.src = src; img.src = src; await img.decode().catch(() => {}); }
}
function pañuelo(t) { // pañuelo blanco ondeando
  const w = (k) => 18 * Math.sin(t * 9 + k);
  return `<svg viewBox="0 0 220 200"><path d="M10 20 Q 60 ${10 + w(0)} 110 20 Q 160 ${30 + w(1)} 210 20 L 200 120 Q 150 ${130 + w(2)} 100 ${150 + w(3) * .6} Q 50 ${170 + w(4)} 20 160 Z"
    fill="#fdfdfd" stroke="#d9dee6" stroke-width="3"/><path d="M30 40 L 190 40 M 28 60 L 186 64" stroke="#ff8fb3" stroke-width="5" opacity=".6"/></svg>`;
}
function orbiCara(t, nombre, hablando) {
  const base = { ...EXPRESIONES[nombre] };
  if (hablando) { const a = 0.25 + 0.55 * Math.abs(Math.sin(t * 17)) * (0.6 + 0.4 * Math.sin(t * 5.3));
    base.boca = nombre === "feliz" ? [0.9, 1.2, Math.max(0.2, a)] : [0.05, 0.6, a]; }
  const parpadeo = (t % 3.1) < 0.12; if (parpadeo && base.oi > 0) { base.oi = 0.08; base.od = base.od > 0 ? 0.08 : base.od; }
  return orbi(nombre, { e: base, anillo: -10 + 4 * Math.sin(t * 1.3) });
}
const ocultar = () => document.querySelectorAll(".capa").forEach((e) => e.style.opacity = 0);
let ultimoSub = "";
async function render(t, f) {
  ocultar(); fondo(t); grano(f); $("#flash").style.opacity = 0; $("#rayas").style.opacity = 0;
  let zoom = 1, sacudir = 0;
  // 0 · Título de telenovela
  if (t < 2.4) { const k = out3(t / 0.9), s = cl((2.4 - t) / 0.4);
    $("#titulo").style.opacity = k * s; $("#titulo").style.transform = `translate(-50%,-50%) scale(${1.15 - 0.15 * k + 0.03 * t})`; $("#titulo").style.filter = `blur(${(1 - k) * 12}px)`;
    $("#brillo").style.opacity = k * s; $("#brillo").style.backgroundPosition = `${130 - 160 * cl((t - 0.6) / 1.4)}% 0`; }
  // 1 · La liquidación de la app, con tres zoom dramáticos
  if (entre(t, 2.2, 6.6)) { const k = out3((t - 2.2) / 0.6), s = cl((6.6 - t) / 0.3);
    $("#cel").style.opacity = k * s;
    const golpes = [3.6, 4.35, 5.1]; let z = 1; golpes.forEach((g, i) => { if (t >= g) z = 1 + 0.32 * (i + 1) * out3((t - g) / 0.12); });
    zoom = z; if (golpes.some((g) => entre(t, g, g + 0.25))) sacudir = 14;
    $("#cel").style.transform = `translate(-50%,-50%) translateY(${(1 - k) * 200}px) scale(${z})`;
    $("#cel").style.transformOrigin = "50% 66%";
    $("#linea-com").style.background = t > 3.6 ? `rgba(255,40,80,${0.18 + 0.12 * Math.sin(t * 20)})` : "transparent";
    $("#rayas").style.opacity = golpes.some((g) => entre(t, g, g + 0.3)) ? 0.8 : 0; }
  // 2 · 27 % gigante que llora
  if (entre(t, 6.4, 9.6)) { const k = rebote((t - 6.45) / 0.5), s = cl((9.6 - t) / 0.35);
    $("#veinti").style.opacity = cl((t - 6.4) / 0.15) * s; sacudir = t < 7.2 ? 18 * (1 - (t - 6.4) / 0.8) : 3;
    $("#veinti").style.transform = `translate(-50%,-50%) scale(${0.4 + 0.6 * k})`;
    $("#lagrimas").style.opacity = s; $("#lagrimas").innerHTML = [0, 1, 2, 3, 4, 5].map((i) => { const ti = (t - 6.9 - i * 0.35); if (ti < 0) return "";
      const y = (ti % 1.1) * 900, x = [-260, 180, -90, 300, 40, -320][i]; return `<i style="left:${540 + x}px;top:${980 + y}px;opacity:${1 - (ti % 1.1) / 1.1}"></i>`; }).join("");
    $("#veinti-pie").style.opacity = out3((t - 7.3) / 0.5) * s; }
  // 3 · Llega Orbi con el pañuelo
  const enOrbi = entre(t, 9.0, 22.9);
  if (enOrbi) {
    let x = 0, y = -120, esc = 1.0, cara = "triste";
    const llega = out3((t - 9.0) / 0.9); x = 700 * (1 - llega);
    if (t > 10.1) cara = "normal";
    if (t > 11.5) cara = "orgulloso";
    if (t > 14.0) { const k = ease((t - 14.0) / 0.8); x = lerp(0, 230, k); y = lerp(-120, -640, k); esc = lerp(1, 0.55, k); cara = "feliz"; }
    if (t > 19.0) { const k = ease((t - 19.0) / 0.6); x = lerp(230, 250, k); y = lerp(-640, 520, k); esc = lerp(0.55, 0.6, k); cara = "sarcastico"; }
    if (t > 21.3) cara = "sarcastico";
    const habla = HABLA.some(([a, b]) => entre(t, a, b));
    $("#orbi").style.opacity = cl((22.9 - t) / 0.3);
    $("#orbi").style.transform = `translate(-50%,-50%) translate(${x}px, ${y + 14 * Math.sin(t * 2.2)}px) scale(${esc}) rotate(${3 * Math.sin(t * 1.7)}deg)`;
    $("#orbi").innerHTML = orbiCara(t, cara, habla);
    const kp = entre(t, 9.0, 14.2) ? cl((14.2 - t) / 0.3) : 0;
    $("#pañuelo").style.opacity = kp; $("#pañuelo").innerHTML = pañuelo(t);
    $("#pañuelo").style.transform = `translate(-50%,-50%) translate(${x - 230}px, ${y + 120 + 10 * Math.sin(t * 3)}px) rotate(${-18 + 8 * Math.sin(t * 4)}deg)`;
    if (entre(t, 9.0, 9.3)) $("#flash").style.opacity = 0.35 * (1 - (t - 9.0) / 0.3);
  }
  // 4 · La caja de Apex Domicilios recibe el pedido · sello 0 %
  if (entre(t, 14.1, 19.2)) { const k = out3((t - 14.1) / 0.7), s = cl((19.2 - t) / 0.3);
    $("#caja").style.opacity = k * s; $("#caja").style.transform = `translate(-50%,-50%) translateY(${200 + (1 - k) * 300}px) perspective(1600px) rotateX(${12 - 8 * k}deg) scale(${0.96 + 0.04 * (t - 14.1) / 5})`;
    await pantalla(CAJA0, t - 14.1);
    const ks = rebote((t - 15.4) / 0.35); $("#sello").style.opacity = cl((t - 15.4) / 0.08) * s;
    $("#sello").style.transform = `translate(-50%,-50%) translate(0px, 640px) rotate(-8deg) scale(${2.2 - 1.2 * ks})`;
    if (entre(t, 15.4, 15.65)) sacudir = 10; }
  // 5 · Le termina a la app por chat
  if (entre(t, 19.0, 22.7)) { const s = cl((22.7 - t) / 0.3);
    $("#chat").style.opacity = out3((t - 19.0) / 0.4) * s;
    [[19.25, "b1"], [20.75, "b2"], [21.35, "b3"]].forEach(([a, id]) => { const k = rebote((t - a) / 0.3); const el = $("#" + id);
      el.style.opacity = cl((t - a) / 0.08); el.style.transform = `scale(${t < a ? 0 : 0.6 + 0.4 * k})`; });
    if (entre(t, 20.75, 21.0)) sacudir = 8; }
  // 6 · Sello Apex
  if (t >= 22.6) { const k = out3((t - 22.6) / 0.6);
    $("#sello-final").style.opacity = k; $("#o-final").innerHTML = orbiCara(t, t < 23.1 ? "normal" : "guino", entre(t, 23.35, 23.35 + (VOZ.o4 || 1.25)));
    $("#o-final").style.transform = `scale(${0.7 + 0.3 * rebote((t - 22.6) / 0.5)})`;
    $("#frase").style.opacity = out3((t - 23.2) / 0.4); $("#logo").style.opacity = out3((t - 24.0) / 0.5); }
  // Subtítulos
  const d = DIALOGOS.find(([a, b]) => entre(t, a, b));
  const sub = $("#sub");
  if (d) { if (ultimoSub !== d[3]) { ultimoSub = d[3]; sub.innerHTML = `<small>${d[2] === "orbi" ? "ORBI" : "EL DUEÑO"}</small>${d[3]}`; sub.className = "capa " + d[2]; }
    const k = out3((t - d[0]) / 0.18); sub.style.opacity = k * cl((d[1] - t) / 0.12); sub.style.transform = `translateX(-50%) scale(${0.9 + 0.1 * k})`;
    if (d[2] === "dueno") sub.style.top = "1460px"; else sub.style.top = t > 14 ? "520px" : "1330px"; }
  // Cámara: zoom y sacudida
  const sx = sacudir ? (Math.sin(f * 7.3) * sacudir) : 0, sy = sacudir ? (Math.cos(f * 5.1) * sacudir) : 0;
  $("#mundo").style.transform = `translate(${sx}px, ${sy}px) scale(${1.01 + 0.01 * Math.sin(t * 0.7)})`;
  $("#barras").style.opacity = t < 2.4 ? 1 : (t >= 22.6 ? 0 : 0);
}
const lerp = (a, b, k) => a + (b - a) * k;
