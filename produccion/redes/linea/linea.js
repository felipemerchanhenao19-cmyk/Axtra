// «Línea de luz»: gráfico animado vertical. Una línea de neón dibuja cada escena; palabras clave grandes en mayúsculas; contadores.
const W = 1080, H = 1920, C = document.getElementById("c"), x = C.getContext("2d");
const AZ = "#36c2f5", AZ2 = "#9fe3ff", BL = "#f4f8fb", GR = "#7d8b99", AMB = "#ffc35a", VER = "#4ce08a", ROJO = "#ff5a5a";
const cl = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v)), suave = (v) => { v = cl(v); return v * v * (3 - 2 * v); };
const sal = (v) => { v = cl(v); return 1 - Math.pow(1 - v, 3); }, lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => cl((t - a) / (b - a));   // avance 0..1 entre a y b
function semilla(s) { return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; }

// ---------- utilidades de dibujo
function brillo(col, blur, fn) { x.save(); x.shadowColor = col; x.shadowBlur = blur; fn(); x.restore(); }
function texto(s, X, Y, px, col = BL, peso = 800, al = "center", sp = 0, alpha = 1) {
  x.save(); x.globalAlpha *= alpha; x.font = `${peso} ${px}px Figtree`; x.fillStyle = col; x.textAlign = al; x.textBaseline = "middle"; x.letterSpacing = sp + "px"; x.fillText(s, X, Y); x.restore();
}
function textoBrillo(s, X, Y, px, col = AZ, alpha = 1, peso = 800, sp = 0) { x.save(); x.globalAlpha *= alpha; x.shadowColor = col; x.shadowBlur = 40; texto(s, X, Y, px, col, peso, "center", sp); x.shadowBlur = 12; texto(s, X, Y, px, "#ffffff", peso, "center", sp, 0.55); x.restore(); }
// palabra que entra con golpe: escala de 1.25 a 1 y aparece
function golpe(s, X, Y, px, k, col = BL, peso = 800, sp = -2) { if (k <= 0) return; const e = 1 + 0.25 * (1 - sal(k * 2.2)); x.save(); x.translate(X, Y); x.scale(e, e); x.globalAlpha = cl(k * 3);
  x.shadowColor = col === BL ? "rgba(54,194,245,.55)" : col; x.shadowBlur = 30; texto(s, 0, 0, px, col, peso, "center", sp); x.restore(); }
function rr(X, Y, w, h, r) { x.beginPath(); x.roundRect(X, Y, w, h, r); }
// línea de neón que avanza por una lista de puntos (k = 0..1 de su largo)
function linea(pts, k, col = AZ, ancho = 6, cabeza = true) {
  if (k <= 0) return; let L = 0; const d = []; for (let i = 1; i < pts.length; i++) { const l = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); d.push(l); L += l; }
  let rest = L * cl(k); x.save(); x.lineCap = "round"; x.lineJoin = "round";
  const camino = () => { x.beginPath(); x.moveTo(pts[0][0], pts[0][1]); let r = rest, px = pts[0][0], py = pts[0][1];
    for (let i = 1; i < pts.length && r > 0; i++) { const f = Math.min(1, r / d[i - 1]); px = lerp(pts[i - 1][0], pts[i][0], f); py = lerp(pts[i - 1][1], pts[i][1], f); x.lineTo(px, py); r -= d[i - 1]; } return [px, py]; };
  x.strokeStyle = col; x.shadowColor = col; x.shadowBlur = 34; x.lineWidth = ancho; const [hx, hy] = camino(); x.stroke();
  x.shadowBlur = 0; x.strokeStyle = "rgba(255,255,255,.85)"; x.lineWidth = ancho * 0.35; camino(); x.stroke();
  if (cabeza && k < 1) { const g = x.createRadialGradient(hx, hy, 0, hx, hy, 46); g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(0.25, col); g.addColorStop(1, "rgba(0,0,0,0)"); x.fillStyle = g; x.fillRect(hx - 46, hy - 46, 92, 92); }
  x.restore();
}
function marco(X, Y, w, h, k, col = AZ, r = 34) {   // tarjeta con borde de neón que se dibuja
  if (k <= 0) return; const p = [[X + r, Y], [X + w - r, Y], [X + w, Y + r], [X + w, Y + h - r], [X + w - r, Y + h], [X + r, Y + h], [X, Y + h - r], [X, Y + r], [X + r, Y]];
  x.save(); x.globalAlpha = cl(k * 2) * 0.9; rr(X, Y, w, h, r); x.fillStyle = "rgba(8,16,26,.82)"; x.fill(); x.restore(); linea(p, sal(k), col, 4, false);
}
function pin(X, Y, s, col = AZ) {   // ícono de ubicación de la marca
  x.save(); x.translate(X, Y); x.scale(s, s); x.shadowColor = col; x.shadowBlur = 30; x.fillStyle = col; rr(-40, -40, 80, 80, 20); x.fill();
  x.fillStyle = "#06121c"; x.beginPath(); x.arc(0, -6, 17, PI, 0); x.lineTo(0, 24); x.closePath(); x.fill(); x.fillStyle = col; x.beginPath(); x.arc(0, -6, 7, 0, 2 * PI); x.fill(); x.restore();
}
const PI = Math.PI;
function burbuja(s, X, Y, w, ia, k) { if (k <= 0) return 0; x.save(); x.globalAlpha = cl(k * 3); x.translate(0, (1 - sal(k * 2)) * 30); x.font = "600 40px Figtree";
  const pal = s.split(" "), lin = []; let l = ""; pal.forEach((p) => { const pr = l ? l + " " + p : p; if (x.measureText(pr).width > w - 70) { lin.push(l); l = p; } else l = pr; }); lin.push(l);
  const h = 44 + lin.length * 52; rr(X, Y, w, h, 30); x.fillStyle = ia ? "rgba(54,194,245,.16)" : "#151c25"; x.fill(); x.strokeStyle = ia ? AZ : "rgba(160,180,200,.35)"; x.lineWidth = 3;
  if (ia) { x.shadowColor = AZ; x.shadowBlur = 18; } x.stroke(); x.shadowBlur = 0; lin.forEach((s2, i) => texto(s2, X + 36, Y + 48 + i * 52, 40, BL, 600, "left")); x.restore(); return h; }
function moto(X, Y, s, col = AZ) {   // repartidor en moto, trazo simple
  x.save(); x.translate(X, Y); x.scale(s, s); x.strokeStyle = col; x.lineWidth = 8; x.lineCap = "round"; x.shadowColor = col; x.shadowBlur = 20;
  x.beginPath(); x.arc(-60, 40, 28, 0, 2 * PI); x.stroke(); x.beginPath(); x.arc(70, 40, 28, 0, 2 * PI); x.stroke();
  x.beginPath(); x.moveTo(-60, 40); x.lineTo(-10, 0); x.lineTo(50, 0); x.lineTo(70, 40); x.moveTo(30, 0); x.lineTo(45, -40); x.lineTo(70, -40); x.stroke();
  x.strokeRect(-55, -55, 50, 45); x.restore();
}
function copo(X, Y, r, a) { x.save(); x.translate(X, Y); x.rotate(a); x.strokeStyle = "rgba(220,240,255,.9)"; x.lineWidth = r * 0.14; x.lineCap = "round";
  for (let i = 0; i < 6; i++) { x.rotate(PI / 3); x.beginPath(); x.moveTo(0, 0); x.lineTo(0, -r); x.moveTo(0, -r * 0.55); x.lineTo(-r * 0.22, -r * 0.75); x.moveTo(0, -r * 0.55); x.lineTo(r * 0.22, -r * 0.75); x.stroke(); } x.restore(); }

// ---------- fondo: negro con viñeta, retícula tenue y polvo de luz
const NIEVE = (() => { const r = semilla(11); return Array.from({ length: 70 }, () => [r() * W, r() * H, 3 + r() * 9, 0.3 + r() * 0.7, r() * 6]); })();
function fondo(t, nieve = 0) {
  x.fillStyle = "#03060a"; x.fillRect(0, 0, W, H);
  const g = x.createRadialGradient(W / 2, H * 0.45, 100, W / 2, H * 0.45, 1250); g.addColorStop(0, "rgba(20,48,70,.55)"); g.addColorStop(1, "rgba(0,0,0,0)"); x.fillStyle = g; x.fillRect(0, 0, W, H);
  x.strokeStyle = "rgba(80,140,180,.06)"; x.lineWidth = 2; for (let X = 0; X <= W; X += 90) { x.beginPath(); x.moveTo(X, 0); x.lineTo(X, H); x.stroke(); } for (let Y = 0; Y <= H; Y += 90) { x.beginPath(); x.moveTo(0, Y); x.lineTo(W, Y); x.stroke(); }
  if (nieve > 0) NIEVE.forEach(([nx, ny, r, v, f]) => { const yy = (ny + t * 90 * v) % H, xx = nx + Math.sin(t * 0.8 + f) * 30; x.globalAlpha = nieve * 0.75 * v; copo(xx, yy, r * 1.4, t * 0.4 + f); x.globalAlpha = 1; });
}

// ---------- escenas (tiempos en segundos)
const T = { s1: 0, s2: 2.7, s3: 5.4, s4: 6.6, s5: 9.4, s6: 12.6, s7: 15.0, s8: 18.4, s9: 21.4, fin: 25.0 };
function escena1(t) {   // SE VIENE DICIEMBRE
  fondo(t, seg(t, 0.3, 1.2)); const k = seg(t, 0, 1.0);
  linea([[-40, 1020], [200, 1020], [300, 900], [780, 900], [880, 1020], [1120, 1020]], k * 1.1, AZ, 7);
  copo(540, 640, 120 * sal(seg(t, 0.2, 0.9)), t * 0.6);
  golpe("SE VIENE", 540, 820, 70, seg(t, 0.35, 0.9), AZ2, 800, 12);
  golpe("DICIEMBRE", 540, 960, 190, seg(t, 0.55, 1.1), BL, 800, -6);
  const a = seg(t, 1.2, 1.6); texto("y tu restaurante va a recibir", 540, 1160, 52, GR, 600, "center", 0, a);
  golpe("MUCHOS DOMICILIOS", 540, 1250, 92, seg(t, 1.5, 1.9), AMB, 800, -1);
}
function escena2(t) {   // la avalancha de mensajes
  const u = t - T.s2; fondo(t, 0.3);
  const X = 190, Y = 330, w = 700, h = 1000; marco(X, Y, w, h, seg(u, 0, 0.4), "rgba(160,180,200,.6)", 60);
  const msgs = ["¿Tienen domicilio?", "¿Cuánto vale la bandeja?", "¿Ya salió mi pedido?", "Hola??", "Ya les pagué, ¿les llegó?", "¿A qué hora llega?", "¿Siguen abiertos?", "Holaaa", "¿Me confirman?"];
  msgs.forEach((m, i) => { const k = seg(u, 0.25 + i * 0.16, 0.45 + i * 0.16); if (k <= 0) return; const yy = Y + 60 + i * 102 - Math.max(0, (u - 1.1)) * 120;
    if (yy < Y + 20 || yy > Y + h - 90) return; burbuja(m, X + 40 + (i % 2) * 90, yy, 520, false, k); });
  const n = Math.min(99, Math.floor(Math.pow(seg(u, 0.3, 2.0), 1.6) * 99)); if (n > 0) brillo(ROJO, 30, () => { x.fillStyle = ROJO; x.beginPath(); x.arc(X + w - 10, Y + 10, 70, 0, 2 * PI); x.fill(); texto(n >= 99 ? "99+" : String(n), X + w - 10, Y + 12, 56, "#fff", 800); });
  golpe("¿VAS A RESPONDER", 540, 1470, 78, seg(u, 1.1, 1.5), BL, 800, -1); golpe("UNO POR UNO?", 540, 1570, 104, seg(u, 1.4, 1.8), ROJO, 800, -2);
}
function escena3(t) {   // la línea barre todo y aparece la marca
  const u = t - T.s3; fondo(t, 0); const k = seg(u, 0, 0.55);
  linea([[-60, 1500], [540, 960], [1140, 420]], k, AZ, 10);
  const a = seg(u, 0.35, 0.9); x.save(); x.globalAlpha = a; pin(540, 820, 1.6 * (0.8 + 0.2 * sal(a))); x.restore();
  golpe("APEX", 540, 1010, 150, seg(u, 0.45, 0.9), BL, 800, 10); golpe("DOMICILIOS", 540, 1140, 92, seg(u, 0.6, 1.0), AZ, 800, 14);
}
function escena4(t) {   // tu propio link + la IA toma el pedido
  const u = t - T.s4; fondo(t, 0);
  golpe("TU PROPIO LINK", 540, 330, 100, seg(u, 0, 0.35), BL, 800, -2);
  const X = 160, Y = 460, w = 760; marco(X, Y, w, 110, seg(u, 0.15, 0.5), AZ, 55); texto("pedidos · tu restaurante", X + w / 2, Y + 57, 44, AZ2, 600, "center", 0, seg(u, 0.35, 0.6));
  linea([[540, 570], [540, 660]], seg(u, 0.5, 0.75), AZ, 6, false);
  marco(130, 680, 820, 640, seg(u, 0.6, 1.0), AZ, 50);
  let y = 730; y += burbuja("Quiero dos bandejas paisas", 170, y, 600, false, seg(u, 0.9, 1.2)) + 24;
  burbuja("¡Listo! Son $ 64.000. ¿Pagas con Wompi o envías el comprobante?", 330, y, 590, true, seg(u, 1.3, 1.7));
  golpe("LA IA TOMA EL PEDIDO", 540, 1460, 84, seg(u, 1.6, 2.0), AZ, 800, -1);
}
function escena5(t) {   // pago: Wompi automático o solo mirar el comprobante
  const u = t - T.s5; fondo(t, 0);
  golpe("EL PAGO", 540, 330, 120, seg(u, 0, 0.35), BL, 800, 4);
  linea([[540, 420], [540, 520], [270, 640], [270, 700]], seg(u, 0.2, 0.7), VER, 6, false); linea([[540, 520], [810, 640], [810, 700]], seg(u, 0.35, 0.8), AMB, 6, false);
  marco(70, 720, 400, 520, seg(u, 0.6, 1.0), VER, 40); marco(610, 720, 400, 520, seg(u, 0.75, 1.15), AMB, 40);
  textoBrillo("WOMPI", 270, 830, 74, VER, seg(u, 0.9, 1.2)); texto("se conecta y", 270, 940, 40, GR, 600, "center", 0, seg(u, 1.0, 1.3));
  golpe("AUTOMÁTICO", 270, 1010, 58, seg(u, 1.15, 1.45), BL); const c1 = seg(u, 1.4, 1.7); if (c1 > 0) brillo(VER, 30, () => texto("✓", 270, 1130, 120 * sal(c1), VER, 800));
  textoBrillo("COMPROBANTE", 810, 830, 54, AMB, seg(u, 1.1, 1.4)); texto("solo lo miras", 810, 940, 40, GR, 600, "center", 0, seg(u, 1.2, 1.5));
  golpe("Y LISTO", 810, 1010, 64, seg(u, 1.4, 1.7), BL); const c2 = seg(u, 1.65, 1.95); if (c2 > 0) brillo(AMB, 30, () => texto("✓", 810, 1130, 120 * sal(c2), AMB, 800));
  golpe("TÚ ELIGES", 540, 1430, 110, seg(u, 2.1, 2.5), BL, 800, -2);
}
function escena6(t) {   // el cliente se entera solo
  const u = t - T.s6; fondo(t, 0);
  marco(250, 300, 580, 1000, seg(u, 0, 0.45), "rgba(160,180,200,.7)", 70);
  const a = seg(u, 0.5, 0.85); if (a > 0) { x.save(); x.translate(0, (1 - sal(a)) * -80); x.globalAlpha = cl(a * 2); rr(290, 420, 500, 220, 36); x.fillStyle = "#121b26"; x.fill(); x.strokeStyle = AZ; x.lineWidth = 4; x.shadowColor = AZ; x.shadowBlur = 24; x.stroke(); x.shadowBlur = 0;
    texto("TU RESTAURANTE", 330, 480, 30, AZ2, 800, "left", 4); texto("¡Tu pedido ya salió!", 330, 545, 48, BL, 800, "left"); texto("Llega en unos 25 minutos", 330, 600, 34, GR, 600, "left"); x.restore(); }
  const m = seg(u, 0.7, 2.2); linea([[120, 1040], [960, 1040]], m, AZ, 4, false); moto(lerp(80, 900, sal(m)), 960, 1.1);
  golpe("YA NO AVISAS TÚ", 540, 1430, 92, seg(u, 1.0, 1.4), BL, 800, -2); golpe("EL CLIENTE SE ENTERA SOLO", 540, 1540, 64, seg(u, 1.3, 1.7), AZ, 800, 0);
}
function escena7(t) {   // incluye
  const u = t - T.s7; fondo(t, seg(u, 2.0, 2.6)); golpe("INCLUYE", 540, 330, 120, seg(u, 0, 0.35), BL, 800, 10);
  const items = [["24/7", "SOPORTE", "siempre que lo necesites", AZ], ["8", "PLATOS EN 3D", "de regalo para tu carta", AMB], ["❄", "TEMÁTICA NAVIDEÑA", "adaptada a tu restaurante", VER]];
  items.forEach(([n, a, b, col], i) => { const k = seg(u, 0.3 + i * 0.75, 0.75 + i * 0.75); const Y = 470 + i * 340; marco(110, Y, 860, 290, k, col, 40);
    if (i === 2) { if (k > 0.3) { x.save(); x.globalAlpha = cl((k - 0.3) * 3); copo(250, Y + 145, 70, t * 0.5); x.restore(); } } else textoBrillo(n, 250, Y + 150, 120, col, cl((k - 0.3) * 3));
    golpe(a, 640, Y + 120, 60, cl((k - 0.4) * 2), BL, 800, 0); texto(b, 640, Y + 195, 38, GR, 600, "center", 0, cl((k - 0.6) * 3)); });
}
function escena8(t) {   // 1 MES GRATIS para los primeros 5
  const u = t - T.s8; fondo(t, 0.4);
  const k = seg(u, 0, 0.5); [["1", 330], ["M", 470], ["E", 610], ["S", 750]].forEach(([c, X], i) => { const kk = seg(u, i * 0.1, 0.35 + i * 0.1); if (kk <= 0) return;
    x.save(); x.globalAlpha = cl(kk * 2); rr(X - 62, 520, 124, 170, 22); x.fillStyle = "rgba(10,20,30,.9)"; x.fill(); x.strokeStyle = i ? "rgba(160,180,200,.7)" : AMB; x.lineWidth = 5; x.shadowColor = i ? AZ : AMB; x.shadowBlur = 24; x.stroke(); x.restore();
    texto(c, X, 608, 120, i ? BL : AMB, 800, "center", 0, cl(kk * 2)); });
  golpe("GRATIS", 540, 830, 170, seg(u, 0.55, 0.95), AMB, 800, 0);
  texto("para los primeros", 540, 1000, 50, GR, 600, "center", 0, seg(u, 1.0, 1.3)); golpe("5 RESTAURANTES", 540, 1090, 96, seg(u, 1.2, 1.6), BL, 800, -1);
  for (let i = 0; i < 5; i++) { const kk = seg(u, 1.5 + i * 0.18, 1.7 + i * 0.18); const X = 240 + i * 150; x.save(); x.globalAlpha = 0.25 + 0.75 * kk; x.strokeStyle = kk > 0.5 ? AMB : "rgba(160,180,200,.5)"; x.lineWidth = 5;
    if (kk > 0.5) { x.shadowColor = AMB; x.shadowBlur = 26; } rr(X - 50, 1210, 100, 100, 24); x.stroke(); x.restore(); if (kk > 0.5) pin(X, 1260, 0.6, AMB); }
  texto("Totalmente gratis. Sin compromiso.", 540, 1430, 46, BL, 600, "center", 0, seg(u, 2.4, 2.8));
}
function escena9(t) {   // cierre
  const u = t - T.s9; fondo(t, 0.2);
  linea([[-40, 700], [1120, 700]], seg(u, 0, 0.6), AZ, 5, false);
  texto("Después", 540, 520, 46, GR, 600, "center", 0, seg(u, 0.1, 0.4)); golpe("$ 120.000 AL MES", 540, 600, 84, seg(u, 0.2, 0.55), BL, 800, -1);
  golpe("UN SOLO LINK.", 540, 860, 110, seg(u, 0.6, 0.95), BL, 800, -2); golpe("CERO MENSAJES.", 540, 990, 110, seg(u, 0.85, 1.2), AZ, 800, -2);
  const a = seg(u, 1.4, 1.9); x.save(); x.globalAlpha = a; pin(270, 1200, 0.9); x.restore(); texto("Apex Domicilios", 610, 1200, 64, BL, 800, "center", 0, a);
  const b = seg(u, 1.9, 2.3); if (b > 0) { x.save(); x.globalAlpha = b; rr(150, 1340, 780, 150, 75); x.fillStyle = AZ; x.shadowColor = AZ; x.shadowBlur = 40 + 20 * Math.sin(t * 4); x.fill(); x.restore();
    texto("RESPONDE ESTE MENSAJE", 540, 1400, 50, "#03121c", 800, "center", 2, b); texto("y lo dejamos listo para diciembre", 540, 1452, 32, "#06263a", 700, "center", 0, b); }
  texto("APEX CORPORATION", 540, 1640, 28, GR, 700, "center", 8, seg(u, 2.2, 2.6));
}
const ESCENAS = [[T.s1, escena1], [T.s2, escena2], [T.s3, escena3], [T.s4, escena4], [T.s5, escena5], [T.s6, escena6], [T.s7, escena7], [T.s8, escena8], [T.s9, escena9]];
// grano
const G = document.getElementById("g"), gx = G.getContext("2d"), GD = gx.createImageData(360, 640);
function render(t) {
  let f = ESCENAS[0][1]; ESCENAS.forEach(([a, fn]) => { if (t >= a) f = fn; }); f(t);
  // destello de corte al cambiar de escena
  ESCENAS.forEach(([a]) => { const d = t - a; if (a > 0 && d >= 0 && d < 0.18) { x.fillStyle = `rgba(160,225,255,${0.35 * (1 - d / 0.18)})`; x.fillRect(0, 0, W, H); } });
  const r = semilla(Math.floor(t * 30) + 7); for (let i = 0; i < GD.data.length; i += 4) { const v = r() * 255; GD.data[i] = GD.data[i + 1] = GD.data[i + 2] = v; GD.data[i + 3] = 255; } gx.putImageData(GD, 0, 0);
}
window.render = render; window.DURACION = T.fin;
