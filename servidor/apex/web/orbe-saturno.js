/* Orbe de Apex: esfera de cristal con Saturno girando adentro.
   Saturno se calcula píxel a píxel (planeta con bandas y tormentas que rotan, anillos con la división de Cassini,
   sombra de los anillos sobre el planeta y sombra del planeta sobre los anillos) una sola vez por cuadro,
   y luego cada canvas lo dibuja dentro del cristal con su halo, reflejos y borde.
   Uso: OrbeSaturno.dibujar(canvas, t, nivelVoz, { piensa, oye, habla }) */
(function () {
  const N = 256, S = 2.36, PX = (2 * S) / N;            // búfer de Saturno: N×N píxeles, de -S a S radios del planeta
  const SUB = 3;                                          // submuestras por lado (antialias de bordes y sombras)
  const E = 0.36, CE = Math.cos(E), SE = Math.sin(E);     // inclinación de los anillos hacia la cámara
  const A = [0, CE, SE], V = [0, SE, -CE];                // eje del planeta y segundo eje del plano de los anillos (el primero es x)
  const L = (() => { const v = [-0.8, 0.35, 0.5], m = Math.hypot(...v); return v.map((x) => x / m); })();   // luz desde arriba a la izquierda
  const LA = L[1] * A[1] + L[2] * A[2];
  const R0 = 1.24, R1 = 2.27;                             // anillos C, B, Cassini, A (en radios de Saturno)

  /* ---------- ruido periódico ---------- */
  function hash(i, j) { let h = (i * 374761393 + j * 668265263) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; }
  function ruido(x, y, p) {
    const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi, sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
    const m = (n) => ((n % p) + p) % p, a = hash(m(xi), yi), b = hash(m(xi + 1), yi), c = hash(m(xi), yi + 1), d = hash(m(xi + 1), yi + 1);
    return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
  }
  function fbm(x, y, p, oct = 4) { let s = 0, a = 0.5, f = 1; for (let o = 0; o < oct; o++) { s += a * ruido(x * f, y * f, p * f); a *= 0.5; f *= 2; } return s / (1 - Math.pow(0.5, oct)); }
  const mezcla = (a, b, k) => a + (b - a) * k, sat = (x) => Math.min(1, Math.max(0, x)), suave = (a, b, x) => { const k = sat((x - a) / (b - a)); return k * k * (3 - 2 * k); };

  /* ---------- textura del planeta (equirectangular) ---------- */
  const TW = 512, TH = 256, TEX = new Float32Array(TW * TH * 3);
  (function texturaPlaneta() {
    const crema = [244, 226, 186], ocre = [196, 150, 88], tostado = [158, 112, 64], polo = [150, 158, 160], ecuador = [250, 240, 214];
    const tormentas = [[0.31, 0.58, 0.045, 0.028], [0.74, -0.44, 0.03, 0.02], [0.52, 0.18, 0.022, 0.014]];
    for (let v = 0; v < TH; v++) {
      const lat = (0.5 - (v + 0.5) / TH) * Math.PI;
      for (let u = 0; u < TW; u++) {
        const lon = u / TW;
        const giro = (fbm(lon * 12, lat * 5, 12) - 0.5) * 0.09 + (fbm(lon * 40, lat * 18, 40, 3) - 0.5) * 0.025;
        const lw = lat + giro * (0.6 + 0.4 * Math.cos(lat * 3));
        let b = 0.5 + 0.24 * Math.sin(lw * 13) + 0.14 * Math.sin(lw * 29 + 1.3) + 0.07 * Math.sin(lw * 61 + 0.4);
        b += (fbm(lon * 90, lat * 60, 90, 2) - 0.5) * 0.12;
        b = sat(b);
        let col = b < 0.5 ? [mezcla(tostado[0], ocre[0], b * 2), mezcla(tostado[1], ocre[1], b * 2), mezcla(tostado[2], ocre[2], b * 2)]
                          : [mezcla(ocre[0], crema[0], b * 2 - 1), mezcla(ocre[1], crema[1], b * 2 - 1), mezcla(ocre[2], crema[2], b * 2 - 1)];
        const eq = 1 - suave(0.05, 0.16, Math.abs(lw)), pl = suave(1.0, 1.35, Math.abs(lat));
        col = col.map((x, i) => mezcla(mezcla(x, ecuador[i], eq * 0.7), polo[i] * (0.75 + 0.25 * b), pl));
        for (const [tl, tf, ax, ay] of tormentas) {
          let dl = lon - tl; dl -= Math.round(dl);
          const q = Math.exp(-((dl * Math.cos(tf)) ** 2 / (ax * ax) + (lat - tf) ** 2 / (ay * ay)));
          if (q > 0.002) col = col.map((x, i) => mezcla(x, [255, 250, 236][i], q * 0.85));
        }
        const o = (v * TW + u) * 3; TEX[o] = col[0]; TEX[o + 1] = col[1]; TEX[o + 2] = col[2];
      }
    }
  })();

  /* ---------- perfil de los anillos ---------- */
  function anillo(p) {
    if (p < R0 || p > R1) return null;
    let op, col;
    if (p < 1.53) { op = 0.14 + 0.18 * (p - R0) / 0.29; col = [164, 146, 120]; }                       // anillo C, tenue
    else if (p < 1.95) { const k = (p - 1.53) / 0.42; op = 0.84 + 0.14 * Math.sin(k * Math.PI); col = [250, 234, 200]; }   // anillo B, el más brillante
    else if (p < 2.03) { op = 0.05; col = [120, 110, 95]; }                                              // división de Cassini
    else { op = p > 2.205 && p < 2.222 ? 0.12 : 0.72; col = [228, 210, 174]; }                           // anillo A con la división de Encke
    op *= 0.82 + 0.18 * Math.sin(p * 173) * Math.sin(p * 61 + 0.7);                                      // anillitos finos
    op *= suave(R0, R0 + 0.02, p) * (1 - suave(R1 - 0.02, R1, p));
    return { op: sat(op), col };
  }
  const RA = 256, RR = 48, RUIDO_ANILLO = new Float32Array(RA * RR);   // grumos que giran con los anillos
  for (let j = 0; j < RR; j++) for (let i = 0; i < RA; i++) RUIDO_ANILLO[j * RA + i] = fbm(i / RA * 24, j * 0.9, 24, 3);

  /* ---------- geometría precalculada por píxel ---------- */
  let G = null;
  function preparar() {
    const idx = [], pC = [], pU = [], pV = [], pS = [], pRim = [], rF = [], rB = [], rCr = [], rCg = [], rCb = [], rAng = [], rOm = [], rRow = [];
    const n2 = SUB * SUB;
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const xc = (i + 0.5) * PX - S, yc = S - (j + 0.5) * PX;
      const zc = -(yc * A[1]) / A[2], pc = Math.sqrt(xc * xc + yc * yc + zc * zc);
      if (xc * xc + yc * yc > (1 + 2 * PX) ** 2 && (pc < R0 - 0.3 || pc > R1 + 0.3)) continue;
      let np = 0, sx = 0, sy = 0, ss = 0, sf = 0, sb = 0, wr = 0, cr = 0, cg = 0, cb = 0, sAng = 0, cAng = 0, sP = 0;
      for (let b = 0; b < SUB; b++) for (let a = 0; a < SUB; a++) {
        const x = xc + ((a + 0.5) / SUB - 0.5) * PX, y = yc + ((b + 0.5) / SUB - 0.5) * PX;
        const q = x * x + y * y, hp = q < 1, zp = hp ? Math.sqrt(1 - q) : 0;
        if (hp) {   // luz sobre el planeta: Lambert suave, oscurecimiento del borde y sombra de los anillos
          const d = x * L[0] + y * L[1] + zp * L[2];
          let s = Math.pow(Math.max(0, (d + 0.05) / 1.05), 0.85) * (0.72 + 0.28 * zp);
          const pa = y * A[1] + zp * A[2];
          if (LA > 0 && pa < 0) { const k = -pa / LA, rx = x + k * L[0], ry = y + k * L[1], rz = zp + k * L[2], an = anillo(Math.hypot(rx, ry, rz)); if (an) s *= 1 - 0.8 * an.op; }
          np++; sx += x; sy += y; ss += s;
        }
        const zr = -(y * A[1]) / A[2], p = Math.sqrt(x * x + y * y + zr * zr), an = anillo(p);
        if (an && !(hp && zr < zp)) {
          // sombra del planeta sobre los anillos (con penumbra)
          const bq = x * L[0] + y * L[1] + zr * L[2]; let sh = 1;
          if (bq < 0) sh = 0.07 + 0.93 * suave(0.97, 1.04, Math.sqrt(Math.max(0, p * p - bq * bq)));
          const luz = (0.98 + 0.16 * (-x / p)) * sh;
          if (!hp && zr < 0) sb += an.op; else sf += an.op;
          cr += an.col[0] * luz * an.op; cg += an.col[1] * luz * an.op; cb += an.col[2] * luz * an.op; wr += an.op;
          const ang = Math.atan2(y * SE - zr * CE, x); sAng += Math.sin(ang) * an.op; cAng += Math.cos(ang) * an.op; sP += p * an.op;
        }
      }
      if (!np && !wr) continue;
      idx.push(j * N + i); pC.push(np / n2); rF.push(sf / n2); rB.push(sb / n2);
      if (np) {
        let x = sx / np, y = sy / np; const m = Math.hypot(x, y); if (m > 0.999) { x *= 0.999 / m; y *= 0.999 / m; }
        const z = Math.sqrt(1 - x * x - y * y), lat = Math.asin(y * A[1] + z * A[2]), lon = Math.atan2(y * V[1] + z * V[2], x) / (Math.PI * 2) + 0.5;
        const s = ss / np, rim = Math.pow(1 - z, 3) * (1 - s) * 0.55;
        pU.push(lon); pV.push(Math.min(TH - 1, Math.max(0, Math.floor((0.5 - lat / Math.PI) * TH)))); pS.push(s); pRim.push(rim);
      } else { pU.push(0); pV.push(0); pS.push(0); pRim.push(0); }
      if (wr) {
        const p = sP / wr; rCr.push(cr / wr); rCg.push(cg / wr); rCb.push(cb / wr);
        rAng.push(Math.atan2(sAng, cAng) / (Math.PI * 2) + 0.5); rOm.push(0.55 / Math.pow(p, 1.5)); rRow.push(Math.min(RR - 1, Math.floor((p - R0) / (R1 - R0) * RR)));
      } else { rCr.push(0); rCg.push(0); rCb.push(0); rAng.push(0); rOm.push(0); rRow.push(0); }
    }
    const F = (a) => Float32Array.from(a);
    const lienzo = document.createElement("canvas"); lienzo.width = lienzo.height = N;
    const ctx = lienzo.getContext("2d");
    G = { n: idx.length, idx: Int32Array.from(idx), pC: F(pC), pU: F(pU), pV: Int32Array.from(pV), pS: F(pS), pRim: F(pRim), rF: F(rF), rB: F(rB),
          rCr: F(rCr), rCg: F(rCg), rCb: F(rCb), rAng: F(rAng), rOm: F(rOm), rRow: Int32Array.from(rRow), lienzo, ctx, img: ctx.createImageData(N, N) };
  }

  /* ---------- un cuadro de Saturno (fase = vueltas del planeta) ---------- */
  function pintarSaturno(fase) {
    const { n, idx, pC, pU, pV, pS, pRim, rF, rB, rCr, rCg, rCb, rAng, rOm, rRow, img, ctx } = G, d = img.data;
    const desp = (fase - Math.floor(fase)) * TW;
    for (let k = 0; k < n; k++) {
      let r = 0, g = 0, b = 0, a = 0, ar = 0, ag = 0, ab = 0;
      const fr = rF[k], br = rB[k], pc = pC[k];
      if (fr > 0 || br > 0) {
        let ang = rAng[k] + rOm[k] * fase; ang = (ang - Math.floor(ang)) * RA;
        const i0 = ang | 0, f = ang - i0, fila = rRow[k] * RA;
        const m = 0.84 + 0.32 * (RUIDO_ANILLO[fila + i0] * (1 - f) + RUIDO_ANILLO[fila + ((i0 + 1) & (RA - 1))] * f);
        ar = rCr[k] * m; ag = rCg[k] * m; ab = rCb[k] * m;
      }
      if (br > 0) { r = ar * br; g = ag * br; b = ab * br; a = br; }
      if (pc > 0) {
        let u = pU[k] * TW - desp; if (u < 0) u += TW;
        const i0 = u | 0, f = u - i0, fila = pV[k] * TW, o0 = (fila + i0) * 3, o1 = (fila + ((i0 + 1) & (TW - 1))) * 3, s = pS[k], rim = pRim[k];
        const pr = (TEX[o0] * (1 - f) + TEX[o1] * f) * s + 70 * rim, pg = (TEX[o0 + 1] * (1 - f) + TEX[o1 + 1] * f) * s + 175 * rim, pb = (TEX[o0 + 2] * (1 - f) + TEX[o1 + 2] * f) * s + 235 * rim;
        r = pr * pc + r * (1 - pc); g = pg * pc + g * (1 - pc); b = pb * pc + b * (1 - pc); a = pc + a * (1 - pc);
      }
      if (fr > 0) { r = ar * fr + r * (1 - fr); g = ag * fr + g * (1 - fr); b = ab * fr + b * (1 - fr); a = fr + a * (1 - fr); }
      const o = idx[k] * 4;
      if (a > 0.002) { d[o] = r / a; d[o + 1] = g / a; d[o + 2] = b / a; d[o + 3] = a * 255; } else d[o + 3] = 0;
    }
    ctx.putImageData(img, 0, 0);
  }

  /* ---------- estrellas dentro del cristal ---------- */
  const ESTRELLAS = Array.from({ length: 46 }, (_, i) => ({ a: hash(i, 1) * Math.PI * 2, d: Math.sqrt(hash(i, 2)) * 0.93, s: 0.4 + hash(i, 3) * 1.1, f: hash(i, 4) * 6.28, v: 0.6 + hash(i, 5) * 1.8 }));

  /* ---------- tiempo: la fase avanza más rápido cuando piensa ---------- */
  let ultimoT = null, fase = 0.18, pintadoEn = null;
  function avanzar(t, est) {
    if (!G) preparar();
    if (t === pintadoEn) return;
    const dt = ultimoT === null ? 0 : Math.min(0.1, Math.max(0, t - ultimoT));
    ultimoT = t; fase += dt / (est.piensa ? 9 : est.habla ? 26 : 38);
    pintarSaturno(fase); pintadoEn = t;
  }

  function dibujar(cv, t, extra = 0, est = {}) {
    avanzar(t, est);
    const g = cv.getContext("2d"), w = cv.width, c = w / 2;
    const k = 1 + 0.012 * Math.sin(t * 1.6) + extra * 0.05, r = w * 0.3 * k;
    g.clearRect(0, 0, w, w);
    // halo exterior: late con la voz, palpita al escuchar
    const oye = est.oye ? 0.5 + 0.5 * Math.sin(t * 5.5) : 0;
    const ha = 0.2 + extra * 0.5 + oye * 0.18;
    const halo = g.createRadialGradient(c, c, r * 0.9, c, c, r * 1.66);
    halo.addColorStop(0, `rgba(63,208,255,${ha})`); halo.addColorStop(0.45, `rgba(63,208,255,${ha * 0.22})`); halo.addColorStop(1, "rgba(63,208,255,0)");
    g.fillStyle = halo; g.fillRect(0, 0, w, w);
    // sombra de contacto bajo la esfera
    const piso = g.createRadialGradient(c, c + r * 1.08, 0, c, c + r * 1.08, r * 0.7);
    piso.addColorStop(0, "rgba(0,0,0,.35)"); piso.addColorStop(1, "rgba(0,0,0,0)");
    g.save(); g.translate(c, c + r * 1.08); g.scale(1, 0.18); g.translate(-c, -(c + r * 1.08)); g.fillStyle = piso; g.fillRect(0, 0, w, w); g.restore();

    g.save(); g.beginPath(); g.arc(c, c, r, 0, Math.PI * 2); g.clip();
    // el espacio adentro
    const fondo = g.createRadialGradient(c - r * 0.25, c - r * 0.3, r * 0.05, c, c, r);
    fondo.addColorStop(0, "#1a4677"); fondo.addColorStop(0.5, "#0a2244"); fondo.addColorStop(1, "#020914");
    g.fillStyle = fondo; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    const neb = g.createRadialGradient(c + r * 0.35, c + r * 0.3, 0, c + r * 0.35, c + r * 0.3, r * 0.8);
    neb.addColorStop(0, "rgba(63,208,255,.16)"); neb.addColorStop(1, "rgba(63,208,255,0)");
    g.fillStyle = neb; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    for (const e of ESTRELLAS) {
      const a = e.a + fase * 0.25, al = (0.35 + 0.65 * (0.5 + 0.5 * Math.sin(t * e.v + e.f))) * 0.8;
      g.fillStyle = `rgba(230,246,255,${al})`; g.beginPath(); g.arc(c + Math.cos(a) * e.d * r, c + Math.sin(a) * e.d * r, Math.max(0.6, e.s * w / 520), 0, Math.PI * 2); g.fill();
    }
    // resplandor cálido de Saturno: crece con la voz
    const calido = g.createRadialGradient(c, c, r * 0.1, c, c, r * 0.95);
    calido.addColorStop(0, `rgba(245,194,107,${0.1 + extra * 0.32})`); calido.addColorStop(1, "rgba(245,194,107,0)");
    g.fillStyle = calido; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    // Saturno
    const escala = (r * 0.4) / (N / (2 * S));
    g.save(); g.translate(c, c + r * 0.02); g.rotate(-0.3 + 0.045 * Math.sin(t * 0.33)); g.scale(escala, escala);
    g.imageSmoothingEnabled = true; g.imageSmoothingQuality = "high"; g.drawImage(G.lienzo, -N / 2, -N / 2); g.restore();
    // grosor del cristal: bordes más oscuros y luz que se refracta abajo
    const vin = g.createRadialGradient(c, c, r * 0.6, c, c, r);
    vin.addColorStop(0, "rgba(2,8,20,0)"); vin.addColorStop(1, "rgba(2,8,20,.6)");
    g.fillStyle = vin; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    g.save(); g.translate(c + r * 0.08, c + r * 0.74); g.scale(1, 0.32);
    const caus = g.createRadialGradient(0, 0, 0, 0, 0, r * 0.56); caus.addColorStop(0, `rgba(139,233,255,${0.3 + extra * 0.25})`); caus.addColorStop(1, "rgba(139,233,255,0)");
    g.fillStyle = caus; g.beginPath(); g.arc(0, 0, r * 0.56, 0, Math.PI * 2); g.fill(); g.restore();
    // borde de Fresnel
    const fres = g.createRadialGradient(c, c, r * 0.84, c, c, r);
    fres.addColorStop(0, "rgba(139,233,255,0)"); fres.addColorStop(1, `rgba(150,236,255,${0.32 + extra * 0.3 + oye * 0.35})`);
    g.fillStyle = fres; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    // destello que recorre el borde mientras piensa
    if (est.piensa) { const a = t * 3.2; g.strokeStyle = "rgba(220,250,255,.75)"; g.lineWidth = r * 0.05; g.lineCap = "round";
      g.shadowColor = "rgba(139,233,255,.9)"; g.shadowBlur = r * 0.12; g.beginPath(); g.arc(c, c, r * 0.95, a, a + 0.7); g.stroke(); g.shadowBlur = 0; }
    // reflejo grande y suave arriba a la izquierda (la ventana)
    g.save(); g.translate(c - r * 0.36, c - r * 0.44); g.rotate(-0.62); g.scale(1, 0.55);
    const esp = g.createRadialGradient(0, 0, 0, 0, 0, r * 0.46); esp.addColorStop(0, "rgba(255,255,255,.42)"); esp.addColorStop(0.55, "rgba(255,255,255,.1)"); esp.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = esp; g.beginPath(); g.arc(0, 0, r * 0.46, 0, Math.PI * 2); g.fill(); g.restore();
    // media luna de luz en el borde superior izquierdo y rebote tenue abajo a la derecha
    const media = (dx, dy, color) => { g.beginPath(); g.arc(c, c, r * 0.97, 0, Math.PI * 2); g.arc(c + dx * r, c + dy * r, r * 0.97, 0, Math.PI * 2, true); g.fillStyle = color; g.fill(); };
    const ml = g.createLinearGradient(c - r, c - r, c, c); ml.addColorStop(0, "rgba(255,255,255,.34)"); ml.addColorStop(0.6, "rgba(255,255,255,0)");
    media(0.07, 0.09, ml);
    const mr = g.createLinearGradient(c + r, c + r, c, c); mr.addColorStop(0, `rgba(139,233,255,${0.22 + extra * 0.2})`); mr.addColorStop(0.5, "rgba(139,233,255,0)");
    media(-0.05, -0.06, mr);
    g.restore();
    // brillo nítido y filo del cristal
    g.save(); g.translate(c - r * 0.46, c - r * 0.52); g.rotate(-0.7); g.fillStyle = "rgba(255,255,255,.85)";
    g.beginPath(); g.ellipse(0, 0, r * 0.11, r * 0.045, 0, 0, Math.PI * 2); g.fill(); g.restore();
    const filo = g.createLinearGradient(c - r, c - r, c + r, c + r);
    filo.addColorStop(0, "rgba(220,250,255,.75)"); filo.addColorStop(0.5, "rgba(139,233,255,.18)"); filo.addColorStop(1, "rgba(139,233,255,.5)");
    g.strokeStyle = filo; g.lineWidth = Math.max(1, w * 0.004); g.beginPath(); g.arc(c, c, r - g.lineWidth / 2, 0, Math.PI * 2); g.stroke();
  }

  window.OrbeSaturno = { dibujar };
})();
