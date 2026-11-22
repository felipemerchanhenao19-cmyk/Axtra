// Marcador fijo arriba (EP.hud = {linea, etiqueta}; valor por plano: pl.hud = 12 o [[0, 12], ["f0", 9]]) y mapa de viajes desde arriba
// (pl.diagrama = {modo: 5 | 1, avance: [[0, 0], [3, 1]]}): tablero con cocina, caja y 12 mesas; las líneas de colores son los viajes del mesero.
const HUD = (() => {
  const cv = document.getElementById("diagrama"), g = cv && cv.getContext("2d");
  const TIPOS = [["CARTA", "#f5a636"], ["PEDIDO", "#36c2f5"], ["PLATO", "#4ce08a"], ["CUENTA", "#ff6b8a"], ["VUELTO", "#c38bff"]];
  const X0 = 250, Y0 = 470, W = 470, H = 1080, mesas = []; for (let i = 0; i < 12; i++) mesas.push([X0 + (i % 2 ? W - 110 : 110), Y0 + 210 + Math.floor(i / 2) * 135]);
  const COC = [X0 + W / 2, Y0 + 70], CAJA = [X0 + W / 2, Y0 + H - 60];
  function dibujar(modo, k, t) {
    g.clearRect(0, 0, 1080, 1920); g.fillStyle = "#07080b"; g.fillRect(0, 0, 1080, 1920);
    // tablero ajedrezado con marco de madera
    g.fillStyle = "#6b4a2e"; g.fillRect(X0 - 26, Y0 - 26, W + 52, H + 52); const c = 39;
    for (let y = 0; y < H; y += c) for (let x = 0; x < W; x += c) { g.fillStyle = ((x + y) / c) % 2 ? "#e9e4da" : "#1c1c1f"; g.fillRect(X0 + x, Y0 + y, Math.min(c, W - x), Math.min(c, H - y)); }
    const caja = (p, txt) => { g.fillStyle = "#3b2a1c"; g.fillRect(p[0] - 90, p[1] - 30, 180, 60); g.font = "800 26px Figtree"; g.fillStyle = "#ffd9a0"; g.textAlign = "center"; g.fillText(txt, p[0], p[1] + 9); };
    caja(COC, "COCINA"); caja(CAJA, "CAJA");
    mesas.forEach(([x, y], i) => { g.fillStyle = "#f4efe6"; g.beginPath(); g.arc(x, y, 34, 0, 7); g.fill(); g.fillStyle = "#b8442e"; g.fillRect(x - 46, y - 12, 10, 24); g.fillRect(x + 36, y - 12, 10, 24);
      g.font = "800 20px Figtree"; g.fillStyle = "#1c1c1f"; g.textAlign = "center"; g.fillText(i + 1, x, y + 7); });
    // viajes: cada tipo es una línea de la mesa a la cocina o a la caja; aparecen en orden según k
    const tipos = modo === 1 ? [2] : [0, 1, 2, 3, 4], total = mesas.length * tipos.length;
    let n = 0; mesas.forEach(([x, y], i) => tipos.forEach((tp, j) => {
      const a = Math.min(1, Math.max(0, k * total - n)); n++; if (a <= 0) return;
      const dst = tp >= 3 ? CAJA : COC, off = (j - 2) * 7, [cx, cy] = [x + (dst[0] - x) * 0.5 + off * 3, y + (dst[1] - y) * 0.5];
      g.strokeStyle = TIPOS[tp][1]; g.globalAlpha = 0.85; g.lineWidth = modo === 1 ? 7 : 4; g.setLineDash(modo === 1 ? [] : [10, 8]); g.lineDashOffset = -t * 40;
      g.beginPath(); g.moveTo(x + off, y); const fx = x + off + (dst[0] + off - x - off) * a, fy = y + (dst[1] - y) * a; g.quadraticCurveTo(cx, cy, fx, fy); g.stroke(); g.globalAlpha = 1; g.setLineDash([]); }));
    // leyenda
    TIPOS.forEach(([s, col], i) => { const y = Y0 + 380 + i * 64, on = modo !== 1 || i === 2; g.globalAlpha = on ? 1 : 0.3;
      g.fillStyle = "#1a1408"; g.strokeStyle = col; g.lineWidth = 3; g.beginPath(); g.roundRect(X0 + W + 50, y - 26, 190, 48, 24); g.fill(); g.stroke();
      g.fillStyle = col; g.beginPath(); g.arc(X0 + W + 78, y - 2, 10, 0, 7); g.fill(); g.font = "800 22px Figtree"; g.fillStyle = "#fff"; g.textAlign = "left"; g.fillText(s, X0 + W + 100, y + 6); g.globalAlpha = 1; });
  }
  return {
    paso(t, pl, tt, L) {
      const h = document.getElementById("hud");
      if (h && EP.hud) { if (!h.dataset.ok) { h.dataset.ok = 1; h.innerHTML = `<div class="l">${EP.hud.linea}</div><div class="c"><span>✋</span><small>${EP.hud.etiqueta}</small><b>0</b></div>`; }
        const v = pl.hud !== undefined ? Math.round(continuo(pl.hud, tt, L)[0]) : null; h.style.opacity = v === null ? 0 : 1; if (v !== null) h.querySelector("b").textContent = v; }
      if (!cv) return; const d = pl.diagrama; cv.style.opacity = d ? 1 : 0; if (d) dibujar(d.modo || 5, d.avance !== undefined ? continuo(d.avance, tt, L)[0] : 1, t);
    },
  };
})();
