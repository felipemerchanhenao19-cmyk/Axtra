// «Apex · Páginas web». render(t, f). Escenas en capas HTML; cada una entra y sale con fundido y movimiento de cámara.
const $ = (s) => document.querySelector(s);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const out3 = (x) => 1 - Math.pow(1 - cl(x), 3);
const ease = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const E = LINEA.escenas, L = LINEA.lineas;
const escenaDe = (t) => Object.keys(E).find((k) => t >= E[k][0] && t < E[k][1]) || "cierre";
// Opacidad de una escena con fundido de entrada/salida
const vis = (k, t, fi = 0.35, fo = 0.35) => { const [a, b] = E[k]; return cl((t - a + 0.05) / fi) * cl((b - t + 0.05) / fo); };
let ultimo = "";
function render(t, f) {
  const k = escenaDe(t);
  for (const id of Object.keys(E)) $("#" + id).style.opacity = vis(id, t, id === "gancho" ? 0.01 : 0.35);
  // Gancho: navegador vacío que se acerca
  { const tt = t - E.gancho[0]; $("#gancho .nav").style.transform = `perspective(1400px) rotateX(${8 - 8 * out3(tt / 2)}deg) scale(${0.92 + 0.1 * ease(tt / 2.2)})`;
    $("#gancho .cursor").style.opacity = Math.floor(t * 2.5) % 2 ? 1 : 0; }
  // Marca: logo con barrido de luz
  { const tt = t - E.marca[0]; $("#marca .logo").style.transform = `scale(${0.8 + 0.2 * out3(tt / 0.9)})`;
    $("#marca .barrido").style.backgroundPosition = `${140 - 180 * cl(tt / 1.6)}% 0`; }
  // Software: celular con el orbe flotando
  { const tt = t - E.software[0]; $("#software .cel").style.transform = `translateY(${60 - 60 * out3(tt / 1)}px) rotate(${-4 + 2 * Math.sin(t * 0.8)}deg)`;
    $("#software .orbe").style.transform = `translateY(${Math.sin(t * 2) * 10}px)`;
    $("#software .orbe").innerHTML = orbi(Math.floor(tt / 1.6) % 2 ? "feliz" : "normal", { anillo: -10 + 4 * Math.sin(t * 1.3) }); }
  // Webs: carrusel 3D de tres sitios de ejemplo
  { const tt = t - E.webs[0]; const giro = -30 + 60 * ease(tt / (E.webs[1] - E.webs[0]));
    document.querySelectorAll("#webs .sitio").forEach((s, i) => { const a = giro + (i - 1) * 38, rad = a * Math.PI / 180;
      s.style.transform = `translate(-50%,-50%) translateX(${Math.sin(rad) * 430}px) translateZ(${Math.cos(rad) * 260 - 260}px) rotateY(${-a * 0.9}deg)`;
      s.style.zIndex = Math.round(100 + Math.cos(rad) * 50); s.style.filter = `brightness(${0.55 + 0.45 * Math.cos(rad)})`; }); }
  // Funciones: celular con sitio y chips que aparecen
  { const tt = t - E.funciones[0]; $("#funciones .cel").style.transform = `scale(${0.95 + 0.05 * out3(tt / 1)})`;
    document.querySelectorAll("#funciones .chip").forEach((c, i) => { const q = out3((tt - 0.9 - i * 0.9) / 0.5); c.style.opacity = q; c.style.transform = `translateX(${(1 - q) * 80}px)`; }); }
  // Precio
  { const tt = t - E.precio[0]; $("#precio .grande").style.transform = `scale(${0.9 + 0.1 * out3((tt - 3.2) / 0.8)})`; $("#precio .grande").style.opacity = out3((tt - 3.2) / 0.6);
    $("#precio .desde").style.opacity = out3((tt - 4.8) / 0.6); $("#precio .joven").style.opacity = out3(tt / 0.6);
    $("#precio .brillo").style.backgroundPosition = `${140 - 180 * cl((tt - 4.8) / 1.8)}% 0`; }
  // Cierre
  { const tt = t - E.cierre[0]; $("#cierre .logo").style.transform = `scale(${0.85 + 0.15 * out3(tt / 1)})`; document.querySelectorAll("#cierre .dato").forEach((d, i) => { d.style.opacity = out3((tt - 1.2 - i * 0.35) / 0.5); }); }
  // Luces de fondo
  $("#luz1").style.transform = `translate(${Math.sin(t * 0.3) * 120}px, ${Math.cos(t * 0.25) * 160}px)`; $("#luz2").style.transform = `translate(${Math.cos(t * 0.27) * 140}px, ${Math.sin(t * 0.31) * 120}px)`;
  // Subtítulos
  const l = L.find((x) => t >= x.ini - 0.05 && t < x.fin + 0.3), sub = $("#sub");
  if (l && !["cierre", "gancho"].includes(k)) { if (ultimo !== l.txt) { ultimo = l.txt; sub.textContent = l.txt; } sub.style.opacity = out3((t - l.ini + 0.05) / 0.12) * cl((l.fin + 0.3 - t) / 0.15); } else sub.style.opacity = 0;
  grano(f);
}
function grano(f) { const c = $("#grano"), x = c.getContext("2d"), d = x.createImageData(c.width, c.height); let s = (f * 9301 + 49297) % 233280;
  for (let i = 0; i < d.data.length; i += 4) { s = (s * 9301 + 49297) % 233280; d.data[i] = d.data[i + 1] = d.data[i + 2] = (s / 233280) * 255; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); }
