/* Video «Mire Apex en su restaurante»: vertical (9:16), dibujado en un canvas con la voz de Apex, música, efectos
   y las seis escenas: apertura, la mesa con el QR, el orbe que saluda, la carta, la cocina y el cierre.
   Mientras se reproduce la primera vez, se graba para que el cliente lo pueda descargar.
   Uso: const v = ApexVideo.crear(canvas); v.poster(datos, textos); await v.preparar(datos, textos, lineas); v.reproducir(); */
(() => {
  const W = 720, H = 1280, ORO = "#bf9b5f", ORO_CLARO = "#dcc08c", CREMA = "#f6f1e7", AZUL = "#111a2b";
  const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const o3 = (x) => 1 - Math.pow(1 - cl(x), 3);
  const io = (x) => { x = cl(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const atras = (x) => { x = cl(x); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
  const entre = (lt, a, b) => cl((lt - a) / (b - a));
  function semilla(s) { let h = 2166136261; for (const ch of String(s)) h = Math.imul(h ^ ch.charCodeAt(0), 16777619); return h >>> 0; }
  function azar(n) { let a = n; return () => { a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  const rgb = (hex) => { const n = parseInt(hex.replace("#", ""), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const rgba = (c, a) => { const [r, g, b] = Array.isArray(c) ? c : rgb(c); return `rgba(${r},${g},${b},${a})`; };
  const aclarar = (hex, k) => rgb(hex).map((v) => Math.round(v + (255 - v) * k));
  const fuente = (px, tipo = 600) => tipo === "t" ? `italic 400 ${px}px "Playfair Display", Georgia, serif` : `${tipo} ${px}px Figtree, system-ui, sans-serif`;
  const precio = (n) => "$" + Math.round(n).toLocaleString("es-CO");

  /* ---------- texto ---------- */
  function ajustar(g, txt, max, px, tipo) { let s = px; g.font = fuente(s, tipo); while (g.measureText(txt).width > max && s > 18) { s -= 2; g.font = fuente(s, tipo); } return s; }
  function partir(g, txt, max) { const out = []; let l = ""; for (const p of String(txt).split(" ")) { const prueba = l ? l + " " + p : p; if (g.measureText(prueba).width > max && l) { out.push(l); l = p; } else l = prueba; } if (l) out.push(l); return out; }
  function espaciado(g, txt, x, y, esp) {   // texto centrado con letras separadas
    const letras = [...txt], anchos = letras.map((c) => g.measureText(c).width), total = anchos.reduce((a, b) => a + b, 0) + esp * (letras.length - 1);
    let cx = x - total / 2; g.textAlign = "left"; letras.forEach((c, i) => { g.fillText(c, cx, y); cx += anchos[i] + esp; }); g.textAlign = "center";
  }
  function redondo(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }

  /* ---------- luces, grano y viñeta ---------- */
  function bokeh(n, sem, colores, zona = [0, 1, 0, 0.6]) {
    const r = azar(sem); return Array.from({ length: n }, () => ({ x: zona[0] + r() * (zona[1] - zona[0]), y: zona[2] + r() * (zona[3] - zona[2]), r: 30 + r() * 110,
      c: colores[Math.floor(r() * colores.length)], a: 0.2 + r() * 0.42, v: 0.2 + r() * 0.5, f: r() * 6.28, m: 10 + r() * 30 }));
  }
  function luces(g, lista, t, alfa) {
    if (alfa <= 0) return;
    g.save(); g.globalCompositeOperation = "lighter";
    for (const l of lista) {
      const x = l.x * W + Math.sin(t * l.v + l.f) * l.m, y = l.y * H + Math.cos(t * l.v * 0.8 + l.f) * l.m * 0.6, a = l.a * alfa * (0.75 + 0.25 * Math.sin(t * 1.3 + l.f));
      const gr = g.createRadialGradient(x, y, 0, x, y, l.r); gr.addColorStop(0, rgba(l.c, a)); gr.addColorStop(0.55, rgba(l.c, a * 0.35)); gr.addColorStop(1, rgba(l.c, 0));
      g.fillStyle = gr; g.fillRect(x - l.r, y - l.r, 2 * l.r, 2 * l.r);
    }
    g.restore();
  }
  const GRANO = (() => { const c = document.createElement("canvas"); c.width = c.height = 256; const x = c.getContext("2d"), d = x.createImageData(256, 256), r = azar(7);
    for (let i = 0; i < d.data.length; i += 4) { const v = r() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 26; } x.putImageData(d, 0, 0); return c; })();
  const VINETA = (() => { const c = document.createElement("canvas"); c.width = W; c.height = H; const x = c.getContext("2d");
    const gr = x.createRadialGradient(W / 2, H * 0.48, H * 0.25, W / 2, H * 0.5, H * 0.72); gr.addColorStop(0, "rgba(0,0,0,0)"); gr.addColorStop(1, "rgba(0,0,0,.48)");
    x.fillStyle = gr; x.fillRect(0, 0, W, H); return c; })();
  function acabado(g, f) {
    g.drawImage(VINETA, 0, 0);
    g.save(); g.globalCompositeOperation = "overlay"; const p = g.createPattern(GRANO, "repeat"), dx = (f * 37) % 256, dy = (f * 71) % 256;
    g.translate(-dx, -dy); g.fillStyle = p; g.fillRect(0, 0, W + 256, H + 256); g.restore();
  }
  function fondo(g, a, b) { const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, a); gr.addColorStop(1, b); g.fillStyle = gr; g.fillRect(0, 0, W, H); }
  function camara(g, escala, cx = W / 2, cy = H / 2, dx = 0, dy = 0) { g.translate(cx + dx, cy + dy); g.scale(escala, escala); g.translate(-cx, -cy); }

  /* ---------- objetos ---------- */
  function codigoQR(sem) { const r = azar(sem), n = 25, m = [];
    const esq = (x, y, a, b) => x >= a && x < a + 7 && y >= b && y < b + 7 && (x === a || x === a + 6 || y === b || y === b + 6 || (x > a + 1 && x < a + 5 && y > b + 1 && y < b + 5));
    for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) { const enE = (x < 8 && y < 8) || (x > n - 9 && y < 8) || (x < 8 && y > n - 9);
      m.push(enE ? esq(x, y, 0, 0) || esq(x, y, n - 7, 0) || esq(x, y, 0, n - 7) : r() < 0.48); } return { n, m }; }
  function dibujarQR(g, q, x, y, lado, color = AZUL) { const c = lado / q.n; g.fillStyle = color; q.m.forEach((v, i) => { if (v) g.fillRect(x + (i % q.n) * c, y + Math.floor(i / q.n) * c, c + 0.4, c + 0.4); }); }

  const PALETAS = [["#e8b94a", "#c8862a", "#5f8f3a"], ["#c8452f", "#8f2a1c", "#e9d9b0"], ["#7a4a2a", "#4e2c17", "#7cae4a"], ["#f1e4c4", "#d8b97a", "#c0392b"], ["#e07b39", "#a94f1f", "#f3e1a0"], ["#6b8f3a", "#3f6125", "#f2d16b"]];
  function tipoPlato(nombre) { const n = nombre.toLowerCase();
    if (/limonada|jugo|bebida|soda|gaseosa|cerveza|caf[eé]|t[eé]\b|batido|coctel|c[oó]ctel|lemonade|juice|drink|beer|coffee|suco|cerveja|refri|vino|wine|agua/.test(n)) return "vaso";
    if (/torta|postre|helado|pastel|brownie|flan|cake|dessert|ice cream|bolo|sobremesa|sorvete|pudim/.test(n)) return "postre"; return "plato"; }
  function dibujarComida(g, nombre, cx, cy, r, t) {
    const pal = PALETAS[semilla(nombre) % PALETAS.length], rr = azar(semilla(nombre + "x")), tipo = tipoPlato(nombre);
    g.save();
    if (tipo === "vaso") {
      g.fillStyle = "rgba(0,0,0,.25)"; g.beginPath(); g.ellipse(cx, cy + r * 0.82, r * 0.55, r * 0.12, 0, 0, Math.PI * 2); g.fill();
      const gr = g.createLinearGradient(cx - r * 0.45, 0, cx + r * 0.45, 0); gr.addColorStop(0, rgba(pal[2], 0.9)); gr.addColorStop(0.5, rgba(aclarar(pal[2], 0.5), 0.95)); gr.addColorStop(1, rgba(pal[2], 0.85));
      g.beginPath(); g.moveTo(cx - r * 0.5, cy - r * 0.7); g.lineTo(cx + r * 0.5, cy - r * 0.7); g.lineTo(cx + r * 0.4, cy + r * 0.8); g.lineTo(cx - r * 0.4, cy + r * 0.8); g.closePath(); g.fillStyle = gr; g.fill();
      g.strokeStyle = "rgba(255,255,255,.6)"; g.lineWidth = 3; g.stroke();
      g.fillStyle = "rgba(255,255,255,.35)"; g.fillRect(cx - r * 0.36, cy - r * 0.6, r * 0.1, r * 1.2);
      g.fillStyle = "#7cb342"; g.beginPath(); g.arc(cx + r * 0.42, cy - r * 0.7, r * 0.26, 0, Math.PI * 2); g.fill(); g.fillStyle = "#d4e157"; g.beginPath(); g.arc(cx + r * 0.42, cy - r * 0.7, r * 0.19, 0, Math.PI * 2); g.fill();
      g.strokeStyle = "#3fd0ff"; g.lineWidth = 5; g.beginPath(); g.moveTo(cx + r * 0.05, cy - r * 0.2); g.lineTo(cx + r * 0.2, cy - r * 1.05); g.stroke();
      g.restore(); return;
    }
    g.fillStyle = "rgba(0,0,0,.3)"; g.beginPath(); g.ellipse(cx, cy + r * 0.18, r * 1.02, r * 0.86, 0, 0, Math.PI * 2); g.fill();
    let gr = g.createRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.1, cx, cy, r); gr.addColorStop(0, "#ffffff"); gr.addColorStop(0.8, "#e9eef3"); gr.addColorStop(1, "#c9d2dc");
    g.fillStyle = gr; g.beginPath(); g.arc(cx, cy, r, 0, Math.PI * 2); g.fill();
    g.strokeStyle = "rgba(0,0,0,.08)"; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, r * 0.78, 0, Math.PI * 2); g.stroke();
    if (tipo === "postre") {
      g.fillStyle = pal[1]; g.beginPath(); g.moveTo(cx - r * 0.5, cy + r * 0.3); g.lineTo(cx + r * 0.45, cy + r * 0.05); g.lineTo(cx + r * 0.45, cy - r * 0.25); g.lineTo(cx - r * 0.5, cy - r * 0.02); g.closePath(); g.fill();
      g.fillStyle = pal[0]; g.beginPath(); g.moveTo(cx - r * 0.5, cy - r * 0.02); g.lineTo(cx + r * 0.45, cy - r * 0.25); g.lineTo(cx + r * 0.2, cy - r * 0.42); g.lineTo(cx - r * 0.62, cy - r * 0.16); g.closePath(); g.fill();
      g.fillStyle = "#d32f2f"; g.beginPath(); g.arc(cx - r * 0.05, cy - r * 0.35, r * 0.1, 0, Math.PI * 2); g.fill();
    } else {
      for (let i = 0; i < 6; i++) { const a = rr() * 6.28, d = rr() * r * 0.32, rad = r * (0.2 + rr() * 0.18);
        const gx = cx + Math.cos(a) * d, gy = cy + Math.sin(a) * d, c = pal[i % 2];
        const gg = g.createRadialGradient(gx - rad * 0.3, gy - rad * 0.3, rad * 0.1, gx, gy, rad); gg.addColorStop(0, rgba(aclarar(c, 0.35), 1)); gg.addColorStop(1, c);
        g.fillStyle = gg; g.beginPath(); g.ellipse(gx, gy, rad, rad * (0.75 + rr() * 0.3), rr() * 3, 0, Math.PI * 2); g.fill(); }
      g.fillStyle = pal[2]; for (let i = 0; i < 9; i++) { const a = rr() * 6.28, d = r * (0.2 + rr() * 0.42); g.beginPath(); g.arc(cx + Math.cos(a) * d, cy + Math.sin(a) * d, r * 0.05, 0, Math.PI * 2); g.fill(); }
    }
    g.globalCompositeOperation = "lighter";   // vapor
    for (let i = 0; i < 3; i++) { const fase = (t * 0.5 + i / 3) % 1, x0 = cx + (i - 1) * r * 0.28;
      g.strokeStyle = `rgba(255,255,255,${0.16 * Math.sin(fase * Math.PI)})`; g.lineWidth = 6; g.beginPath();
      for (let k = 0; k <= 10; k++) { const yy = cy - r * 0.4 - fase * r * 0.9 - k * r * 0.07; const xx = x0 + Math.sin(k * 0.9 + t * 2 + i) * r * 0.08; k ? g.lineTo(xx, yy) : g.moveTo(xx, yy); } g.stroke(); }
    g.restore();
  }

  /* ---------- las escenas ---------- */
  const ESCENAS = [
    { id: "apertura", min: 4.6, voz: 0.8, cola: 0.9 }, { id: "mesa", min: 5.8, voz: 0.5, cola: 0.9 }, { id: "saludo", min: 4.8, voz: 1.0, cola: 0.8 },
    { id: "carta", min: 6.4, voz: 0.5, cola: 1.4 }, { id: "cocina", min: 5.8, voz: 0.4, cola: 1.1 }, { id: "cierre", min: 5.4, voz: 0.5, cola: 2.6 },
  ];

  function apertura(g, lt, D, v) {
    const { d, x } = v;
    fondo(g, "#05070d", "#0d1120");
    g.save(); camara(g, 1 + 0.07 * (lt / D));
    luces(g, v.b1, v.t, o3(lt / 1.4));
    const s = entre(lt, 0.15, 1.35);           // destello dorado que cruza
    if (s > 0 && s < 1) { const px = -300 + s * (W + 600), gr = g.createLinearGradient(px - 300, 0, px + 300, 0);
      gr.addColorStop(0, "rgba(220,192,140,0)"); gr.addColorStop(0.5, "rgba(255,236,190,.95)"); gr.addColorStop(1, "rgba(220,192,140,0)"); g.fillStyle = gr; g.fillRect(0, H * 0.505 - 1.5, W, 3);
      const fl = g.createRadialGradient(px, H * 0.505, 0, px, H * 0.505, 160); fl.addColorStop(0, "rgba(255,230,180,.45)"); fl.addColorStop(1, "rgba(255,230,180,0)"); g.fillStyle = fl; g.fillRect(px - 160, H * 0.505 - 160, 320, 320); }
    g.textAlign = "center"; g.textBaseline = "alphabetic";
    if (v.logo) { const k = atras(entre(lt, 0.3, 1.0)); if (k > 0) { g.save(); g.translate(W / 2, H * 0.33); g.scale(k, k); g.beginPath(); g.arc(0, 0, 70, 0, Math.PI * 2); g.save(); g.clip();
      g.drawImage(v.logo, -70, -70, 140, 140); g.restore(); g.strokeStyle = ORO; g.lineWidth = 3; g.stroke(); g.restore(); } }
    g.globalAlpha = o3(entre(lt, 0.5, 1.2)); g.fillStyle = ORO_CLARO; g.font = fuente(26, 700); espaciado(g, x.una_noche, W / 2, H * 0.43 + (1 - g.globalAlpha) * 20, 9);
    g.globalAlpha = 1;
    const px = ajustar(g, d.n, 640, 112, "t"), rev = io(entre(lt, 0.9, 2.1));
    if (rev > 0) { g.save(); g.beginPath(); g.rect(0, H * 0.52 - px * 1.15, W * rev + 40, px * 1.7); g.clip();
      g.shadowColor = rgba(d.color, 0.9); g.shadowBlur = 50; g.fillStyle = CREMA; g.font = fuente(px, "t"); g.fillText(d.n, W / 2, H * 0.52); g.shadowBlur = 0; g.restore(); }
    const raya = io(entre(lt, 1.8, 2.6)); g.fillStyle = ORO; g.fillRect(W / 2 - 140 * raya, H * 0.552, 280 * raya, 2);
    const sub = [d.t, d.c].filter(Boolean).join("  ·  ");
    if (sub) { g.globalAlpha = o3(entre(lt, 2.2, 3.0)); g.fillStyle = "rgba(246,241,231,.75)"; g.font = fuente(30, 500); g.fillText(sub, W / 2, H * 0.6); g.globalAlpha = 1; }
    g.restore();
  }

  function mesa(g, lt, D, v) {
    const { d, x } = v, cx = W * 0.42, sy = H * 0.55, pcx = W * 0.68, pcy = H * 0.75;
    fondo(g, "#2a160c", "#0b0604");
    const m = entre(lt, D - 0.6, D), zoom = 1 + 0.12 * io(lt / D) + 3.2 * m * m;
    g.save(); camara(g, zoom, cx + (pcx - cx) * io(m), sy - 120 + (pcy - 150 - (sy - 120)) * io(m));
    luces(g, v.b2, v.t, 1);
    const top = H * 0.6; g.beginPath(); g.moveTo(-160, H + 40); g.lineTo(W + 160, H + 40); g.lineTo(W + 40, top); g.lineTo(-40, top); g.closePath();   // la mesa
    let gr = g.createLinearGradient(0, top, 0, H); gr.addColorStop(0, "#6a3a1f"); gr.addColorStop(1, "#2a160b"); g.fillStyle = gr; g.fill();
    g.save(); g.clip(); g.strokeStyle = "rgba(0,0,0,.18)"; g.lineWidth = 2;
    for (let i = 0; i < 14; i++) { const y0 = top + i * 46; g.beginPath(); g.moveTo(-100, y0); g.bezierCurveTo(W * 0.3, y0 + 18, W * 0.6, y0 - 14, W + 100, y0 + 10); g.stroke(); }
    const pool = g.createRadialGradient(cx, top + 110, 10, cx, top + 110, 440); pool.addColorStop(0, "rgba(255,196,120,.5)"); pool.addColorStop(1, "rgba(255,196,120,0)"); g.fillStyle = pool; g.fillRect(0, top, W, H - top); g.restore();
    const vx = W * 0.12, vy = top + 60, fl = 1 + 0.08 * Math.sin(v.t * 13) + 0.05 * Math.sin(v.t * 23);   // vela
    const halo = g.createRadialGradient(vx, vy - 70, 0, vx, vy - 70, 160 * fl); halo.addColorStop(0, "rgba(255,190,90,.6)"); halo.addColorStop(1, "rgba(255,190,90,0)"); g.fillStyle = halo; g.fillRect(vx - 170, vy - 240, 340, 340);
    g.fillStyle = "#efe6d6"; g.fillRect(vx - 18, vy - 50, 36, 60); g.fillStyle = "#d9cdb8"; g.beginPath(); g.ellipse(vx, vy - 50, 18, 6, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = "#fff3c4"; g.beginPath(); g.ellipse(vx, vy - 70, 7 * fl, 16 * fl, Math.sin(v.t * 3) * 0.08, 0, Math.PI * 2); g.fill();
    g.fillStyle = "rgba(0,0,0,.35)"; g.beginPath(); g.ellipse(W * 0.98, top + 90, 150, 50, 0, 0, Math.PI * 2); g.fill();   // plato al fondo
    g.fillStyle = "#eef1f4"; g.beginPath(); g.ellipse(W * 0.98, top + 78, 150, 48, 0, 0, Math.PI * 2); g.fill();
    const bw = 250, bh = 360, bx = cx - bw / 2, by = sy - bh + 40, q = 170, qx = cx - q / 2, qy = by + 78;   // soporte con el QR
    g.fillStyle = "rgba(0,0,0,.45)"; g.beginPath(); g.ellipse(cx, sy + 44, 170, 26, 0, 0, Math.PI * 2); g.fill();
    gr = g.createLinearGradient(bx, by, bx + bw, by + bh); gr.addColorStop(0, "#1d1712"); gr.addColorStop(1, "#0b0907"); redondo(g, bx, by, bw, bh, 18); g.fillStyle = gr; g.fill();
    g.save(); g.shadowColor = d.color; g.shadowBlur = 18; g.strokeStyle = d.color; g.lineWidth = 5; g.stroke(); g.restore();
    g.textAlign = "center"; g.fillStyle = CREMA; ajustar(g, d.n, bw - 36, 32, "t"); g.fillText(d.n, cx, by + 54);
    redondo(g, qx - 10, qy - 10, q + 20, q + 20, 10); g.fillStyle = "#fff"; g.fill(); dibujarQR(g, v.qr, qx, qy, q);
    g.fillStyle = ORO_CLARO; g.font = fuente(19, 800); espaciado(g, x.mesa, cx, by + bh - 50, 4); g.fillStyle = "rgba(246,241,231,.7)"; g.font = fuente(15, 700); espaciado(g, "APEX PLAY", cx, by + bh - 24, 5);
    const ok = entre(lt, 3.5, 4.4);
    if (ok > 0) { g.save(); g.globalCompositeOperation = "lighter"; const fl2 = g.createRadialGradient(cx, qy + q / 2, 0, cx, qy + q / 2, 230);
      fl2.addColorStop(0, rgba(aclarar(d.color, 0.5), 0.55 * (1 - ok))); fl2.addColorStop(1, rgba(d.color, 0)); g.fillStyle = fl2; g.fillRect(cx - 230, qy + q / 2 - 230, 460, 460); g.restore(); }
    const sube = io(entre(lt, 1.0, 2.1)), cw = 310, ch = 620;   // el celular del cliente: en su visor se ve el código
    if (sube > 0) {
      g.save(); g.translate(pcx + 40 * (1 - sube), pcy + 560 * (1 - sube)); g.rotate(-0.1 + 0.04 * (1 - sube));
      g.shadowColor = "rgba(0,0,0,.65)"; g.shadowBlur = 50; redondo(g, -cw / 2, -ch / 2, cw, ch, 46); g.fillStyle = "#0b0f18"; g.fill(); g.shadowBlur = 0;
      g.save(); redondo(g, -cw / 2 + 12, -ch / 2 + 12, cw - 24, ch - 24, 36); g.clip();
      let pg = g.createLinearGradient(0, -ch / 2, 0, ch / 2); pg.addColorStop(0, "#3a2416"); pg.addColorStop(1, "#140b06"); g.fillStyle = pg; g.fillRect(-cw / 2, -ch / 2, cw, ch);
      const vq = 150, vy = -ch / 2 + 190;
      redondo(g, -vq / 2 - 8, vy - vq / 2 - 8, vq + 16, vq + 16, 8); g.fillStyle = "#fff"; g.fill(); dibujarQR(g, v.qr, -vq / 2, vy - vq / 2, vq);
      const esc = entre(lt, 2.2, 3.5);
      if (esc > 0 && esc < 1) { const ly = vy - vq / 2 + vq * (0.5 - 0.5 * Math.cos(esc * Math.PI * 2)); g.save(); g.shadowColor = d.color; g.shadowBlur = 22;
        g.fillStyle = rgba(aclarar(d.color, 0.45), 0.95); g.fillRect(-vq / 2 - 20, ly - 2, vq + 40, 4); g.restore(); }
      if (ok > 0) { g.fillStyle = rgba(d.color, 0.35 * Math.sin(Math.min(1, ok * 1.5) * Math.PI)); g.fillRect(-cw / 2, -ch / 2, cw, ch); }
      g.restore();
      g.strokeStyle = ok > 0 ? "#2fbf71" : "rgba(255,255,255,.9)"; g.lineWidth = 5; const s0 = 98;
      [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([sx, sy2]) => { g.beginPath(); g.moveTo(sx * s0, vy + sy2 * s0 - sy2 * 30); g.lineTo(sx * s0, vy + sy2 * s0); g.lineTo(sx * s0 - sx * 30, vy + sy2 * s0); g.stroke(); });
      redondo(g, -120, vy + 118, 240, 52, 26); g.fillStyle = ok > 0 ? "#2fbf71" : "rgba(5,8,15,.75)"; g.fill();
      g.fillStyle = "#fff"; g.font = fuente(21, 700); g.textAlign = "center"; g.fillText(ok > 0 ? "✓ " + x.mesa : x.escaneando, 0, vy + 152);
      g.fillStyle = "#05080f"; redondo(g, -48, -ch / 2 + 22, 96, 26, 13); g.fill();
      g.restore();
    }
    g.restore();
    if (m > 0) { g.fillStyle = `rgba(255,255,255,${Math.pow(m, 2.2)})`; g.fillRect(0, 0, W, H); }   // entra al celular
  }

  function pantalla(g, v, titulo) {   // la pantalla del celular (escenas del orbe y la carta)
    fondo(g, "#0f2140", "#071020");
    const gl = g.createRadialGradient(W / 2, H * 0.32, 20, W / 2, H * 0.32, 640); gl.addColorStop(0, "rgba(40,110,200,.35)"); gl.addColorStop(1, "rgba(40,110,200,0)"); g.fillStyle = gl; g.fillRect(0, 0, W, H);
    luces(g, v.b3, v.t, 0.6);
    g.fillStyle = "rgba(139,233,255,.85)"; g.font = fuente(19, 700); g.textAlign = "left"; g.fillText(titulo, 52, 142);
    ajustar(g, v.d.n, 440, 40, "t"); g.fillStyle = CREMA; g.textAlign = "left"; g.fillText(v.d.n, 52, 192);
    g.textAlign = "center"; redondo(g, W - 196, 140, 146, 54, 27); g.strokeStyle = "rgba(139,233,255,.45)"; g.lineWidth = 2; g.stroke(); g.fillStyle = CREMA; g.font = fuente(20, 700); g.fillText(v.x.mesa, W - 123, 175);
  }

  function saludo(g, lt, D, v) {
    const { d, x } = v;
    pantalla(g, v, "APEX PLAY");
    const k = atras(entre(lt, 0.05, 0.9)), tam = 540 * k, oy = H * 0.38;
    if (k > 0) {
      const brillo = g.createRadialGradient(W / 2, oy, 0, W / 2, oy, 420); brillo.addColorStop(0, rgba(d.color, 0.28 + v.nivel * 0.3)); brillo.addColorStop(1, rgba(d.color, 0));
      g.fillStyle = brillo; g.fillRect(0, oy - 420, W, 840);
      if (window.OrbeSaturno) { OrbeSaturno.dibujar(v.orbe, performance.now() / 1000, v.nivel, { habla: v.nivel > 0.02 }); g.drawImage(v.orbe, W / 2 - tam / 2, oy - tam / 2, tam, tam); }
    }
    const destello = 1 - entre(lt, 0, 0.5); if (destello > 0) { g.fillStyle = `rgba(255,255,255,${destello})`; g.fillRect(0, 0, W, H); }
    g.textAlign = "center"; g.globalAlpha = o3(entre(lt, 0.8, 1.3)); g.fillStyle = ORO_CLARO; g.font = fuente(34, 500); g.fillText(x.bienvenido, W / 2, H * 0.6); g.globalAlpha = 1;
    const px = ajustar(g, d.n, 640, 84, "t"), letras = [...d.n], n = Math.round(letras.length * entre(lt, 1.1, 2.3));
    g.save(); g.shadowColor = rgba(d.color, 0.8); g.shadowBlur = 30; g.fillStyle = CREMA; g.font = fuente(px, "t"); g.fillText(letras.slice(0, n).join(""), W / 2, H * 0.6 + px * 1.05); g.restore();
    const chips = ["ES", "EN", "PT", "DE", "RU", "日本"], cw = 74;   // los idiomas del orbe
    chips.forEach((c, i) => { const a = o3(entre(lt, 2.0 + i * 0.08, 2.5 + i * 0.08)); if (!a) return; const cx = W / 2 + (i - 2.5) * (cw + 12);
      g.globalAlpha = a; redondo(g, cx - cw / 2, H * 0.705, cw, 44, 22); g.fillStyle = i === v.idx ? CREMA : "rgba(255,255,255,.06)"; g.fill();
      g.strokeStyle = "rgba(139,233,255,.3)"; g.lineWidth = 1.5; g.stroke(); g.fillStyle = i === v.idx ? AZUL : CREMA; g.font = fuente(19, 700); g.fillText(c, cx, H * 0.705 + 29); });
    g.globalAlpha = 1;
  }

  function carta(g, lt, D, v) {
    const { d, x } = v;
    pantalla(g, v, x.carta);
    const y0 = 240, alto = 212, sep = 18, cw = W - 80;
    d.platos.forEach((p, i) => {
      const k = atras(entre(lt, 0.15 + i * 0.18, 0.95 + i * 0.18)); if (k <= 0) return;
      const yy = y0 + i * (alto + sep), xx = 40 + (1 - k) * 520;
      g.save(); g.translate(xx + cw / 2, yy + alto / 2); g.rotate((1 - k) * 0.25); g.translate(-cw / 2, -alto / 2);
      const reco = i === 0 && lt > 0.9, sel = (i === 1 && lt > 3.4) || (i === 2 && lt > 4.0);
      g.shadowColor = "rgba(0,0,0,.45)"; g.shadowBlur = 30; redondo(g, 0, 0, cw, alto, 30); g.fillStyle = "#13233d"; g.fill(); g.shadowBlur = 0;
      if (reco) { g.save(); g.shadowColor = ORO; g.shadowBlur = 26 * (0.6 + 0.4 * Math.sin(v.t * 4)); g.strokeStyle = ORO; g.lineWidth = 4; redondo(g, 0, 0, cw, alto, 30); g.stroke(); g.restore(); }
      else { g.strokeStyle = "rgba(139,233,255,.14)"; g.lineWidth = 2; redondo(g, 0, 0, cw, alto, 30); g.stroke(); }
      redondo(g, 20, 20, 172, 172, 22); g.fillStyle = "#0b1628"; g.fill();
      g.save(); redondo(g, 20, 20, 172, 172, 22); g.clip(); const fg = g.createRadialGradient(106, 96, 10, 106, 106, 130); fg.addColorStop(0, "#3a2a1c"); fg.addColorStop(1, "#151008"); g.fillStyle = fg; g.fillRect(20, 20, 172, 172);
      dibujarComida(g, p.nombre, 106, 110, 66, v.t + i); g.restore();
      g.textAlign = "left"; g.fillStyle = CREMA; g.font = fuente(34, 700); const ls = partir(g, p.nombre, cw - 250).slice(0, 2);
      ls.forEach((l, j) => g.fillText(l, 216, 64 + j * 40));
      g.fillStyle = "#ffcf66"; g.font = fuente(34, 800); g.fillText(precio(p.precio), 216, alto - 30);
      const bw = 150, bx = cw - bw - 22, by = alto - 80;
      redondo(g, bx, by, bw, 60, 30); g.fillStyle = sel ? "#2fbf71" : "#3fd0ff"; g.fill(); g.fillStyle = sel ? "#fff" : AZUL; g.font = fuente(25, 800); g.textAlign = "center"; g.fillText(sel ? x.agregado : x.pedir, bx + bw / 2, by + 40);
      if (reco) { const ra = o3(entre(lt, 0.9, 1.4)); g.globalAlpha = ra; redondo(g, cw - 236, -20, 212, 46, 23); g.fillStyle = ORO; g.fill(); g.fillStyle = AZUL; g.font = fuente(19, 800); espaciado(g, x.recomendado, cw - 130, 10, 2); g.globalAlpha = 1; }
      g.restore();
      [[1, 3.25], [2, 3.85]].forEach(([j, tt]) => { if (i !== j) return; const a = entre(lt, tt, tt + 0.6); if (a <= 0 || a >= 1) return;   // el toque del dedo
        const tx = 40 + cw - 97, ty = yy + alto - 50; g.save(); g.globalCompositeOperation = "lighter";
        g.fillStyle = `rgba(255,255,255,${0.5 * (1 - a)})`; g.beginPath(); g.arc(tx, ty, 26 + a * 50, 0, Math.PI * 2); g.fill(); g.restore(); });
    });
    const bar = o3(entre(lt, 4.3, 4.9));   // barra del pedido
    if (bar > 0) { const by = 944 + 60 * (1 - bar), total = d.platos[1].precio + d.platos[2].precio, env = lt > 5.3;
      g.globalAlpha = bar; redondo(g, 40, by, W - 80, 92, 46); g.fillStyle = env ? "#2fbf71" : d.color; g.fill();
      g.fillStyle = "#fff"; g.textAlign = "left"; g.font = fuente(28, 800); g.fillText(env ? x.enviando : `${x.ver_pedido} · 2`, 84, by + 58);
      g.textAlign = "right"; g.fillText(precio(total), W - 84, by + 58); g.globalAlpha = 1; }
  }

  function cocina(g, lt, D, v) {
    const { d, x } = v;
    fondo(g, "#1a0f08", "#070403");
    g.save(); camara(g, 1.04 - 0.04 * io(lt / D));
    [0.2, 0.5, 0.8].forEach((px, i) => {   // lámparas de la cocina
      const lx = W * px, cono = g.createLinearGradient(0, 120, 0, H * 0.75); cono.addColorStop(0, "rgba(255,190,110,.32)"); cono.addColorStop(1, "rgba(255,190,110,0)");
      g.fillStyle = cono; g.beginPath(); g.moveTo(lx - 40, 150); g.lineTo(lx + 40, 150); g.lineTo(lx + 230, H * 0.75); g.lineTo(lx - 230, H * 0.75); g.closePath(); g.fill();
      g.fillStyle = "#2b2b2f"; g.beginPath(); g.moveTo(lx - 60, 150); g.lineTo(lx + 60, 150); g.lineTo(lx + 30, 100); g.lineTo(lx - 30, 100); g.closePath(); g.fill();
      g.fillStyle = "#ffe2a8"; g.beginPath(); g.ellipse(lx, 152, 50, 8, 0, 0, Math.PI * 2); g.fill(); g.fillStyle = "#3a3a40"; g.fillRect(lx - 2, 0, 4, 100); });
    luces(g, v.b5, v.t, 1);
    const mt = H * 0.74, acero = g.createLinearGradient(0, mt, 0, H); acero.addColorStop(0, "#9aa3ad"); acero.addColorStop(0.08, "#5d646d"); acero.addColorStop(0.5, "#3b4047"); acero.addColorStop(1, "#1f2226");
    g.fillStyle = acero; g.fillRect(0, mt, W, H - mt); g.fillStyle = "rgba(255,255,255,.35)"; g.fillRect(0, mt, W, 3);
    g.restore();
    // la comanda sale de la impresora
    const sale = io(entre(lt, 0.25, 1.5)), tw = 470, th = 610, tx = W / 2 - tw / 2, ty = -th + sale * (th + 150) + Math.sin(v.t * 1.6) * 4 * sale;
    g.fillStyle = "#16181c"; redondo(g, W / 2 - 290, 70, 580, 90, 22); g.fill(); g.fillStyle = "#0a0b0d"; g.fillRect(W / 2 - 250, 132, 500, 12);
    g.fillStyle = "#2fbf71"; g.beginPath(); g.arc(W / 2 + 240, 115, 9, 0, Math.PI * 2); g.fill();
    g.save(); g.beginPath(); g.rect(0, 138, W, H); g.clip();
    g.save(); g.translate(0, 0); g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 40;
    g.beginPath(); g.moveTo(tx, ty); g.lineTo(tx + tw, ty); g.lineTo(tx + tw, ty + th); for (let i = 0; i <= 18; i++) g.lineTo(tx + tw - (i * tw) / 18, ty + th + (i % 2 ? 16 : 0)); g.closePath();
    g.fillStyle = "#fbf8f1"; g.fill(); g.shadowBlur = 0; g.restore();
    g.textAlign = "center"; g.fillStyle = "#2a9d6a"; g.font = fuente(24, 800); espaciado(g, x.nuevo_pedido, W / 2, ty + 70, 4);
    g.fillStyle = "#1b2333"; g.font = fuente(46, "t"); g.fillText(x.mesa, W / 2, ty + 132);
    g.fillStyle = "#5d6678"; g.font = fuente(22, 600); const n = ajustar(g, d.n, tw - 60, 22, 600); g.fillText(d.n, W / 2, ty + 168);
    g.strokeStyle = "#c9c2b4"; g.setLineDash([8, 8]); g.lineWidth = 2; g.beginPath(); g.moveTo(tx + 30, ty + 196); g.lineTo(tx + tw - 30, ty + 196); g.stroke();
    g.textAlign = "left"; g.fillStyle = "#1b2333"; [1, 2].forEach((j, k) => { g.font = fuente(28, 700); const nom = partir(g, "1 × " + d.platos[j].nombre, tw - 60)[0]; g.fillText(nom, tx + 30, ty + 250 + k * 56); });
    g.beginPath(); g.moveTo(tx + 30, ty + 360); g.lineTo(tx + tw - 30, ty + 360); g.stroke(); g.setLineDash([]);
    g.font = fuente(30, 800); g.fillText(x.total, tx + 30, ty + 412); g.textAlign = "right"; g.fillText(precio(d.platos[1].precio + d.platos[2].precio), tx + tw - 30, ty + 412);
    g.textAlign = "center"; g.fillStyle = "#9c7a3f"; g.font = fuente(20, 700); g.fillText(x.via, W / 2, ty + 470);
    g.fillStyle = "#1b2333"; for (let i = 0; i < 26; i++) g.fillRect(tx + 60 + i * 13.5, ty + 500, i % 3 ? 4 : 7, 52);
    g.restore();
    const dg = entre(lt, 1.45, 2.4);   // campanazo
    if (dg > 0 && dg < 1) { g.save(); g.globalCompositeOperation = "lighter"; for (let k = 0; k < 3; k++) { const a = cl(dg * 1.4 - k * 0.2); if (a <= 0 || a >= 1) continue;
      g.strokeStyle = `rgba(255,214,140,${0.7 * (1 - a)})`; g.lineWidth = 4; g.beginPath(); g.arc(W / 2, 115, 60 + a * 340, 0, Math.PI * 2); g.stroke(); } g.restore(); }
    x.cifras.forEach((c, i) => {   // cero errores, cero comisiones, cero esperas
      const a = atras(entre(lt, 2.2 + i * 0.35, 2.75 + i * 0.35)); if (a <= 0) return; const cw = 200, cx = W / 2 + (i - 1) * (cw + 16), cy = H * 0.665;
      g.save(); g.translate(cx, cy); g.scale(a, a); redondo(g, -cw / 2, -62, cw, 124, 22); g.fillStyle = "rgba(10,12,16,.82)"; g.fill(); g.strokeStyle = rgba(ORO, 0.7); g.lineWidth = 2; g.stroke();
      g.fillStyle = ORO_CLARO; g.font = fuente(52, "t"); g.textAlign = "center"; g.fillText("0", 0, 4); g.fillStyle = CREMA; g.font = fuente(20, 700); g.fillText(c, 0, 40); g.restore(); });
  }

  function cierre(g, lt, D, v) {
    const { d, x } = v;
    fondo(g, "#0a1120", "#05080f");
    g.save(); g.globalCompositeOperation = "lighter";   // rayos de luz
    for (let i = 0; i < 5; i++) { const a = -0.5 + i * 0.25 + Math.sin(v.t * 0.2 + i) * 0.05; g.save(); g.translate(W / 2, -80); g.rotate(a);
      const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, "rgba(191,155,95,.16)"); gr.addColorStop(1, "rgba(191,155,95,0)"); g.fillStyle = gr; g.fillRect(-40, 0, 80, H * 1.2); g.restore(); }
    g.restore();
    v.chispas.forEach((c) => { const yy = ((c.y - v.t * c.v * 0.05) % 1 + 1) % 1; g.fillStyle = `rgba(220,192,140,${c.a * (0.5 + 0.5 * Math.sin(v.t * 3 + c.f))})`; g.beginPath(); g.arc(c.x * W, yy * H, c.r, 0, Math.PI * 2); g.fill(); });
    g.textAlign = "center";
    const k1 = atras(entre(lt, 0.1, 0.8)), k2 = atras(entre(lt, 0.4, 1.1)), cy = H * 0.3;
    if (v.logo) { g.save(); g.translate(W / 2 - 130, cy); g.scale(k1, k1); g.beginPath(); g.arc(0, 0, 78, 0, Math.PI * 2); g.save(); g.clip(); g.drawImage(v.logo, -78, -78, 156, 156); g.restore(); g.strokeStyle = ORO; g.lineWidth = 3; g.stroke(); g.restore(); }
    else { g.save(); g.translate(W / 2 - 130, cy); g.scale(k1, k1); g.beginPath(); g.arc(0, 0, 78, 0, Math.PI * 2); g.fillStyle = d.color; g.fill(); g.strokeStyle = ORO; g.lineWidth = 3; g.stroke();
      g.fillStyle = CREMA; g.font = fuente(70, "t"); g.fillText([...d.n.trim()][0] || "A", 0, 24); g.restore(); }
    g.globalAlpha = o3(entre(lt, 0.6, 1.0)); g.fillStyle = ORO_CLARO; g.font = fuente(40, 300); g.fillText("×", W / 2, cy + 14); g.globalAlpha = 1;
    if (v.apex) { g.save(); g.translate(W / 2 + 130, cy); g.scale(k2, k2); g.beginPath(); g.arc(0, 0, 78, 0, Math.PI * 2); g.save(); g.clip(); g.drawImage(v.apex, -78, -78, 156, 156); g.restore(); g.strokeStyle = ORO; g.lineWidth = 3; g.stroke(); g.restore(); }
    g.globalAlpha = o3(entre(lt, 1.0, 1.6)); g.fillStyle = ORO; g.font = fuente(24, 800); espaciado(g, "APEX CORPORATION", W / 2, cy + 150, 8);
    g.fillStyle = "rgba(246,241,231,.8)"; g.font = fuente(36, 500); g.fillText(x.asi, W / 2, H * 0.53);
    const px = ajustar(g, d.n, 640, 96, "t"); g.save(); g.shadowColor = rgba(d.color, 0.9); g.shadowBlur = 40; g.fillStyle = CREMA; g.font = fuente(px, "t"); g.fillText(d.n, W / 2, H * 0.53 + px * 1.15); g.restore();
    g.globalAlpha = 1;
    const raya = io(entre(lt, 1.4, 2.2)); g.fillStyle = d.color; g.fillRect(W / 2 - 160 * raya, H * 0.53 + px * 1.15 + 26, 320 * raya, 5);
    g.globalAlpha = o3(entre(lt, 1.9, 2.6)); g.fillStyle = CREMA; g.font = fuente(28, 600); g.fillText(x.instalacion, W / 2, H * 0.75);
    redondo(g, W / 2 - 250, H * 0.79, 500, 84, 42); g.fillStyle = "#25d366"; g.fill(); g.fillStyle = "#fff"; g.font = fuente(30, 800); g.fillText("WhatsApp 310 789 7960", W / 2, H * 0.79 + 54);
    g.fillStyle = "rgba(246,241,231,.7)"; g.font = fuente(24, 500); g.fillText("apexcorporation@axtra.chat", W / 2, H * 0.79 + 136); g.globalAlpha = 1;
    const negro = entre(lt, D - 0.35, D); if (negro > 0) { g.fillStyle = `rgba(0,0,0,${negro * 0.4})`; g.fillRect(0, 0, W, H); }
  }

  const DIBUJO = { apertura, mesa, saludo, carta, cocina, cierre };
  const SUAVE = { mesa: 0.5, carta: 0.4, cocina: 0.45, cierre: 0.6 };      // fundido de entrada de cada escena

  function subtitulo(g, txt, a, orbe) {
    if (!txt || a <= 0) return;
    g.save(); g.globalAlpha = a; g.font = fuente(31, 600); const ls = partir(g, txt, 600).slice(0, 3), alto = ls.length * 42 + 30, y = H - 104 - alto;
    const ancho = Math.min(640, Math.max(...ls.map((l) => g.measureText(l).width)) + 56);
    redondo(g, W / 2 - ancho / 2, y, ancho, alto, 22); g.fillStyle = "rgba(5,8,15,.72)"; g.fill();
    if (orbe) { g.strokeStyle = rgba(ORO, 0.8); g.lineWidth = 2; g.stroke(); }
    g.fillStyle = "#fff"; g.textAlign = "center"; ls.forEach((l, i) => g.fillText(l, W / 2, y + 47 + i * 42)); g.restore();
  }
  function marca(g, v) { g.save(); g.globalAlpha = 0.85; if (v.apex) { g.drawImage(v.apex, 36, 34, 40, 40); } g.fillStyle = ORO_CLARO; g.font = fuente(16, 800); g.textAlign = "left"; espaciado(g, "APEX", 128, 61, 5); g.restore(); }

  /* ---------- sonido: música sintetizada, efectos y voces ---------- */
  const nota = (m) => 440 * Math.pow(2, (m - 69) / 12);
  const ACORDES = [[57, 60, 64, 67, 71], [53, 57, 60, 64], [48, 55, 59, 64], [55, 59, 62, 64]], BAJOS = [45, 41, 48, 43];
  function crearSonido() {
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return null;
    const ctx = new AC();
    const mezcla = ctx.createGain(), salida = ctx.createGain(); mezcla.connect(salida); salida.connect(ctx.destination);
    let grabar = null; try { grabar = ctx.createMediaStreamDestination(); mezcla.connect(grabar); } catch (e) {}
    const ruido = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate), dr = ruido.getChannelData(0); for (let i = 0; i < dr.length; i++) dr[i] = Math.random() * 2 - 1;
    return { ctx, mezcla, salida, grabar, ruido, nodos: [] };
  }
  function programar(S, t0, linea, total, voces) {
    const { ctx } = S, nodos = S.nodos;
    const osc = (tipo, f, ini, fin, destino, det = 0) => { const o = ctx.createOscillator(); o.type = tipo; o.frequency.value = f; o.detune.value = det; o.connect(destino); o.start(ini); o.stop(fin); nodos.push(o); return o; };
    const gan = (v, destino) => { const x = ctx.createGain(); x.gain.value = v; x.connect(destino); return x; };
    const musica = gan(0, S.mezcla), M = musica.gain;
    M.setValueAtTime(0, t0); M.linearRampToValueAtTime(0.55, t0 + 1.6);
    voces.forEach((v) => { M.setTargetAtTime(0.28, t0 + v.ini - 0.15, 0.08); M.setTargetAtTime(0.55, t0 + v.fin + 0.15, 0.3); });
    M.setTargetAtTime(0, t0 + total - 1.2, 0.5);
    const filtro = ctx.createBiquadFilter(); filtro.type = "lowpass"; filtro.frequency.value = 1300; filtro.Q.value = 0.6; filtro.connect(musica);
    const beat = 60 / 84, compas = beat * 4, inicioRitmo = linea[1].ini, finRitmo = linea[5].ini + 0.5, inicioHat = linea[3].ini;
    for (let c = 0, t = 0; t < total + 0.5; c++, t += compas) {
      const ac = ACORDES[c % 4], a = t0 + t, b = Math.min(t0 + total + 1.5, a + compas + 0.6);
      ac.forEach((m) => { const e = gan(0, filtro); e.gain.setValueAtTime(0, a); e.gain.linearRampToValueAtTime(0.022, a + 0.7); e.gain.setValueAtTime(0.022, b - 0.7); e.gain.linearRampToValueAtTime(0, b);
        osc("sawtooth", nota(m), a, b, e, -7); osc("sawtooth", nota(m), a, b, e, 7); });
      const bj = gan(0, musica); bj.gain.setValueAtTime(0, a); bj.gain.linearRampToValueAtTime(0.16, a + 0.05); bj.gain.exponentialRampToValueAtTime(0.0008, a + compas * 0.9); osc("triangle", nota(BAJOS[c % 4]), a, a + compas, bj);
      for (let k = 0; k < 8; k++) { const tt = t + k * beat / 2; if (tt < inicioRitmo - 0.2 || tt > total - 1) continue;   // arpegio
        const m = ac[[0, 2, 1, 3, 2, 4, 1, 2][k] % ac.length] + 12, p = gan(0, musica), at = t0 + tt;
        p.gain.setValueAtTime(0, at); p.gain.linearRampToValueAtTime(0.045, at + 0.01); p.gain.exponentialRampToValueAtTime(0.0006, at + 0.32); osc("triangle", nota(m), at, at + 0.36, p); }
      for (let k = 0; k < 4; k++) { const tt = t + k * beat, at = t0 + tt; if (tt < inicioRitmo || tt > finRitmo) continue;
        if (k % 2 === 0) { const kg = gan(0, musica); kg.gain.setValueAtTime(0.5, at); kg.gain.exponentialRampToValueAtTime(0.001, at + 0.28);
          const o = osc("sine", 140, at, at + 0.3, kg); o.frequency.setValueAtTime(140, at); o.frequency.exponentialRampToValueAtTime(42, at + 0.14); }
        if (tt >= inicioHat) { const n = ctx.createBufferSource(); n.buffer = S.ruido; const hp = ctx.createBiquadFilter(); hp.type = "highpass"; hp.frequency.value = 7000;
          const hg = gan(0, musica); hg.gain.setValueAtTime(0.05, at + beat / 2); hg.gain.exponentialRampToValueAtTime(0.0005, at + beat / 2 + 0.06);
          n.connect(hp); hp.connect(hg); n.start(at + beat / 2, Math.random() * 0.5, 0.08); nodos.push(n); } }
    }
    const efectos = gan(0.9, S.mezcla);
    const silbido = (at) => { const n = ctx.createBufferSource(); n.buffer = S.ruido; const bp = ctx.createBiquadFilter(); bp.type = "bandpass"; bp.Q.value = 1.4;
      bp.frequency.setValueAtTime(300, at); bp.frequency.exponentialRampToValueAtTime(3500, at + 0.45); const e = gan(0, efectos);
      e.gain.setValueAtTime(0, at); e.gain.linearRampToValueAtTime(0.16, at + 0.25); e.gain.linearRampToValueAtTime(0, at + 0.55); n.connect(bp); bp.connect(e); n.start(at, 0, 0.6); nodos.push(n); };
    const tono = (f, at, dur, v, tipo = "sine") => { const e = gan(0, efectos); e.gain.setValueAtTime(0, at); e.gain.linearRampToValueAtTime(v, at + 0.008); e.gain.exponentialRampToValueAtTime(0.0005, at + dur); osc(tipo, f, at, at + dur + 0.05, e); };
    linea.slice(1).forEach((e) => silbido(t0 + e.ini - 0.4));
    tono(1320, t0 + linea[1].ini + 3.5, 0.12, 0.12); tono(1760, t0 + linea[1].ini + 3.62, 0.18, 0.12);      // el QR se lee
    [3.25, 3.85].forEach((s) => tono(880, t0 + linea[3].ini + s, 0.09, 0.1, "triangle"));                   // toques en la carta
    tono(1046, t0 + linea[3].ini + 5.3, 0.25, 0.08); tono(1568, t0 + linea[3].ini + 5.42, 0.3, 0.08);        // pedido enviado
    [1568, 2349, 3136].forEach((f, i) => tono(f, t0 + linea[4].ini + 1.45, 1.8 - i * 0.4, 0.14 / (i + 1)));   // campana de la cocina
    [2.2, 2.55, 2.9].forEach((s) => tono(660, t0 + linea[4].ini + s, 0.12, 0.07, "triangle"));
    [523, 659, 784, 1046].forEach((f, i) => tono(f, t0 + linea[5].ini + 0.1 + i * 0.09, 2.6, 0.05, "triangle"));   // acorde final
  }

  function envolvente(buf) {   // volumen de la voz 25 veces por segundo, para que el orbe lata con ella
    const d = buf.getChannelData(0), n = Math.floor(buf.sampleRate / 25), out = [];
    for (let i = 0; i + n <= d.length; i += n) { let s = 0; for (let k = i; k < i + n; k += 4) s += d[k] * d[k]; out.push(Math.sqrt(s / (n / 4))); }
    const tope = [...out].sort((a, b) => a - b)[Math.floor(out.length * 0.95)] || 1; return out.map((x) => Math.min(1, x / tope));
  }

  /* ---------- el reproductor ---------- */
  function crear(canvas) {
    const g = canvas.getContext("2d"); canvas.width = W; canvas.height = H;
    const apex = new Image(); apex.src = "/web/sitio/logo.png";
    const orbe = document.createElement("canvas"); orbe.width = orbe.height = 520;
    let S = null, v = null, linea = [], total = 0, voces = [], t0 = 0, estado = "listo", raf = 0, cuadro = 0, grabadora = null, partes = [], archivo = null;
    const yo = { onprogreso: null, onfin: null, onarchivo: null, get estado() { return estado; }, get total() { return total; }, get archivo() { return archivo; } };

    function vistas(datos, textos) {
      const r = rgb(datos.color);
      return { d: datos, x: textos, idx: textos.idx || 0, orbe, apex: apex.complete && apex.naturalWidth ? apex : null, logo: datos.logoImg || null, qr: codigoQR(semilla(datos.n)),
        b1: bokeh(28, 11, ["#ffcf8a", "#ffb35c", datos.color], [0, 1, 0.05, 0.95]), b2: bokeh(26, 23, ["#ffcf8a", "#ff9f4a", "#ffe2b0", datos.color], [0, 1, 0, 0.55]),
        b3: bokeh(14, 37, ["#3fd0ff", "#7fb2ff", datos.color], [0, 1, 0, 1]), b5: bokeh(18, 51, ["#ff8a3a", "#ffb35c", "#ff5a2a"], [0, 1, 0.55, 1]),
        chispas: Array.from({ length: 70 }, (_, i) => { const a = azar(900 + i); return { x: a(), y: a(), r: 1 + a() * 2.5, v: 0.4 + a(), a: 0.3 + a() * 0.6, f: a() * 6 }; }), t: 0, nivel: 0, rgb: r };
    }
    function pintar(t) {
      if (!v) return;
      v.t = t; let k = linea.findIndex((e) => t < e.ini + e.dur); if (k < 0) k = linea.length - 1;
      const e = linea[k], lt = t - e.ini, voz = voces[k];
      v.nivel = voz && voz.env && t >= voz.ini && t < voz.fin ? voz.env[Math.min(voz.env.length - 1, Math.floor((t - voz.ini) * 25))] * 0.9 : 0;
      g.save(); DIBUJO[e.id](g, lt, e.dur, v); g.restore();
      const fi = SUAVE[e.id]; if (fi && lt < fi && k > 0) { const p = linea[k - 1]; g.save(); g.globalAlpha = 1 - io(lt / fi); DIBUJO[p.id](g, t - p.ini, p.dur, v); g.restore(); }
      marca(g, v);
      const activa = voces.find((x) => t >= x.ini - 0.05 && t < x.fin + 0.35);
      if (activa && activa.escena !== "cierre") subtitulo(g, activa.txt, cl((t - activa.ini + 0.05) / 0.15) * cl((activa.fin + 0.35 - t) / 0.2), activa.escena === "saludo" || activa.escena === "carta");
      acabado(g, cuadro++);
    }
    function poster(datos, textos) {   // primer cuadro con el nombre del restaurante, antes de reproducir
      v = vistas(datos, textos); linea = ESCENAS.map((e, i) => ({ ...e, ini: i * 5, dur: e.min })); voces = []; total = 30; estado = "listo";
      pintar(3.2);
    }
    async function preparar(datos, textos, lineasVoz) {
      detener(); archivo = null; v = vistas(datos, textos);
      if (!S) S = crearSonido();
      if (S && S.ctx.state === "suspended") await S.ctx.resume().catch(() => {});
      try { if (navigator.audioSession) navigator.audioSession.type = "playback"; } catch (e) {}   // en iPhone suena aunque esté en silencio
      await Promise.all([document.fonts.load('italic 80px "Playfair Display"'), document.fonts.load("700 40px Figtree")].map((p) => p.catch(() => {})));
      const buffers = await Promise.all(lineasVoz.map(async (l) => {
        if (!S) return null;
        try { const r = await fetch(l.src); return await S.ctx.decodeAudioData(await r.arrayBuffer()); } catch (e) { return null; } }));
      let t = 0; linea = []; voces = [];
      ESCENAS.forEach((e, i) => { const b = buffers[i], dv = b ? b.duration : 0, dur = Math.max(e.min, e.voz + dv + e.cola);
        linea.push({ ...e, ini: t, dur }); if (lineasVoz[i]) voces.push({ escena: e.id, txt: lineasVoz[i].txt, ini: t + e.voz, fin: t + e.voz + (dv || 2.6), buf: b, env: b ? envolvente(b) : null }); t += dur; });
      total = t; v.apex = apex.complete && apex.naturalWidth ? apex : null; estado = "preparado"; pintar(0);
    }
    function grabarInicio() {   // se graba la primera vez que se ve completo (si ya hay archivo, no se vuelve a grabar)
      grabadora = null; if (archivo) return;
      if (!window.MediaRecorder || !canvas.captureStream) return;
      const tipos = ["video/mp4;codecs=avc1.42E01E,mp4a.40.2", "video/mp4;codecs=avc1", "video/webm;codecs=vp9,opus", "video/webm;codecs=vp8,opus", "video/webm", "video/mp4"];
      const tipo = tipos.find((x) => MediaRecorder.isTypeSupported(x)); if (!tipo) return;
      try {
        const pista = canvas.captureStream(30), audio = S && S.grabar ? S.grabar.stream.getAudioTracks() : [];
        grabadora = new MediaRecorder(new MediaStream([...pista.getVideoTracks(), ...audio]), { mimeType: tipo, videoBitsPerSecond: 5e6 });
        const mias = []; partes = mias; const esta = grabadora;
        grabadora.ondataavailable = (e) => e.data.size && mias.push(e.data);
        grabadora.onstop = () => { if (esta.descartada || estado !== "terminado" || !mias.length) return;
          archivo = { blob: new Blob(mias, { type: tipo.split(";")[0] }), ext: tipo.includes("mp4") ? "mp4" : "webm" }; yo.onarchivo && yo.onarchivo(archivo); };
        grabadora.start(500);
      } catch (e) { grabadora = null; }
    }
    function reproducir() {
      if (!v || !linea.length) return;
      if (estado === "pausado") { estado = "reproduciendo"; if (S) S.ctx.resume(); if (grabadora && grabadora.state === "paused") grabadora.resume(); bucle(); return; }
      detener(); estado = "reproduciendo";
      const ahora = S ? S.ctx.currentTime + 0.12 : performance.now() / 1000; t0 = ahora;
      if (S) { programar(S, t0, linea, total, voces);
        voces.forEach((x) => { if (!x.buf) return; const s = S.ctx.createBufferSource(); s.buffer = x.buf; const gv = S.ctx.createGain(); gv.gain.value = 1.15; s.connect(gv); gv.connect(S.mezcla); s.start(t0 + x.ini); S.nodos.push(s); }); }
      grabarInicio(); bucle();
    }
    const reloj = () => S ? S.ctx.currentTime - t0 : performance.now() / 1000 - t0;
    function bucle() {
      cancelAnimationFrame(raf);
      const paso = () => { if (estado !== "reproduciendo") return; const t = Math.max(0, reloj()); pintar(Math.min(t, total)); yo.onprogreso && yo.onprogreso(Math.min(t, total), total);
        if (t >= total) { estado = "terminado"; if (grabadora && grabadora.state !== "inactive") grabadora.stop(); yo.onfin && yo.onfin(); return; } raf = requestAnimationFrame(paso); };
      raf = requestAnimationFrame(paso);
    }
    function pausar() { if (estado !== "reproduciendo") return; estado = "pausado"; cancelAnimationFrame(raf); if (S) S.ctx.suspend(); if (grabadora && grabadora.state === "recording") grabadora.pause(); }
    function detener() {
      cancelAnimationFrame(raf);
      if (S) { S.nodos.forEach((n) => { try { n.stop(); } catch (e) {} }); S.nodos = []; if (S.ctx.state === "suspended") S.ctx.resume().catch(() => {}); }
      if (grabadora && grabadora.state !== "inactive") { const gr = grabadora; grabadora = null; gr.descartada = true; try { gr.stop(); } catch (e) {} }
      if (estado === "reproduciendo" || estado === "pausado") estado = "preparado";
    }
    function silencio(si) { if (S) S.salida.gain.value = si ? 0 : 1; }
    return Object.assign(yo, { poster, preparar, reproducir, pausar, detener, silencio, desbloquear() { if (!S) S = crearSonido(); if (S && S.ctx.state === "suspended") S.ctx.resume(); },
      cuadroEn(t) { pintar(t); } });
  }
  window.ApexVideo = { crear, ESCENAS };
})();
