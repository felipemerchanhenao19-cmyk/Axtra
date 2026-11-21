/* Orbe de Apex: esfera de nieve de cristal con Saturno girando adentro.
   Cada cuadro se calcula Saturno en 3D píxel a píxel: el sistema da vueltas sobre la vertical (los anillos cambian de ángulo),
   el planeta rota sobre su eje con bandas y tormentas, los anillos tienen la división de Cassini y grumos que orbitan,
   y hay sombras entre planeta y anillos. Las luces pasan por azul, rojo, violeta y verde, y la nieve gira dentro del cristal.
   Uso: OrbeSaturno.dibujar(canvas, t, nivelVoz, { piensa, oye, habla }) */
(function () {
  const N = 256, S = 2.36, PX = (2 * S) / N;            // búfer de Saturno: N×N píxeles, de -S a S radios del planeta
  const TAU = 0.3, EL = 0.38;                             // inclinación del eje respecto a la vertical y elevación de la cámara
  const CEL = Math.cos(EL), SEL = Math.sin(EL), CT = Math.cos(TAU), ST = Math.sin(TAU);
  const L = (() => { const v = [-0.75, 0.45, 0.55], m = Math.hypot(...v); return v.map((x) => x / m); })();   // luz principal: arriba a la izquierda
  const R0 = 1.24, R1 = 2.27;                             // anillos C, B, Cassini, A (en radios de Saturno)
  const COLORES = [[60, 140, 255], [255, 52, 72], [170, 82, 255], [36, 226, 128]];   // azul, rojo, violeta, verde

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

  /* ---------- anillos filtrados: sumas acumuladas del perfil para promediarlo según lo que cubre cada píxel (sin parpadeos) ---------- */
  const RP0 = 1.0, RP1 = 2.6, M = 4096, HM = (RP1 - RP0) / M;
  const CO = new Float64Array(M + 1), CR = new Float64Array(M + 1), CG = new Float64Array(M + 1), CB = new Float64Array(M + 1);
  for (let i = 0; i < M; i++) {
    const an = anillo(RP0 + (i + 0.5) * HM), op = an ? an.op : 0, col = an ? an.col : [0, 0, 0];
    CO[i + 1] = CO[i] + op * HM; CR[i + 1] = CR[i] + op * col[0] * HM; CG[i + 1] = CG[i] + op * col[1] * HM; CB[i + 1] = CB[i] + op * col[2] * HM;
  }
  function acum(C, x) { let u = (x - RP0) / HM; if (u <= 0) return C[0]; if (u >= M) return C[M]; const i = u | 0; return C[i] + (C[i + 1] - C[i]) * (u - i); }
  const opFiltrada = (p, w) => (acum(CO, p + w / 2) - acum(CO, p - w / 2)) / w;

  /* ---------- píxeles del búfer que pueden tener algo ---------- */
  let G = null;
  function preparar() {
    const xs = [], ys = [], idx = [], lim = (R1 + 3 * PX) ** 2;
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const x = (i + 0.5) * PX - S, y = S - (j + 0.5) * PX;
      if (x * x + y * y < lim) { xs.push(x); ys.push(y); idx.push(j * N + i); }
    }
    const lienzo = document.createElement("canvas"); lienzo.width = lienzo.height = N;
    const ctx = lienzo.getContext("2d");
    G = { n: idx.length, X: Float32Array.from(xs), Y: Float32Array.from(ys), idx: Int32Array.from(idx), lienzo, ctx, img: ctx.createImageData(N, N) };
  }

  /* ---------- un cuadro de Saturno ---------- */
  // giro: vueltas del sistema sobre la vertical · rot: vueltas del planeta sobre su eje · luz y borde: colores [0..1]
  function pintarSaturno(giro, rot, luz, borde) {
    const { n, X, Y, idx, img, ctx } = G, d = img.data, DOSPI = Math.PI * 2;
    const th = giro * DOSPI, cth = Math.cos(th), sth = Math.sin(th);
    // eje del planeta y base del plano ecuatorial: inclinar TAU, girar sobre la vertical y elevar la cámara
    const tr = (x, y, z) => { const x1 = x * cth + z * sth, z1 = -x * sth + z * cth; return [x1, y * CEL - z1 * SEL, y * SEL + z1 * CEL]; };
    const [Ax, Ay, Az] = tr(0, CT, ST), [Ux, Uy, Uz] = tr(1, 0, 0), [Wx, Wy, Wz] = tr(0, -ST, CT);
    const [Lx, Ly, Lz] = L, LA = Lx * Ax + Ly * Ay + Lz * Az, caraLuz = LA * Az > 0;
    const KR = 0.8 + 0.32 * luz[0], KG = 0.8 + 0.32 * luz[1], KB = 0.8 + 0.32 * luz[2];      // luz principal: blanca, apenas teñida (el dorado no se apaga)
    const QR = 0.6 + 0.6 * luz[0], QG = 0.6 + 0.6 * luz[1], QB = 0.6 + 0.6 * luz[2];      // los anillos de hielo sí toman el color
    const BR = 255 * borde[0], BG = 255 * borde[1], BB = 255 * borde[2];                      // contraluz de color en el lado oscuro
    const AR = 0.07 * luz[0], AG = 0.07 * luz[1], AB = 0.07 * luz[2];
    const desp = rot - Math.floor(rot), lim1 = (1 + PX) ** 2, rq0 = (R0 - 0.35) ** 2, rq1 = (R1 + 0.35) ** 2;
    const dzx = -Ax / Az, dzy = -Ay / Az;
    for (let k = 0; k < n; k++) {
      const x = X[k], y = Y[k], q = x * x + y * y;
      let pr = 0, pg = 0, pb = 0, pa = 0, zp = -9;
      if (q < lim1) {                                         // el planeta
        const dd = Math.sqrt(q); pa = (1 - dd) / PX + 0.5; if (pa > 1) pa = 1;
        if (pa > 0) {
          let px = x, py = y; if (dd > 0.999) { px *= 0.999 / dd; py *= 0.999 / dd; }
          const pz = Math.sqrt(Math.max(0, 1 - px * px - py * py)); zp = pz;
          let dl = (px * Lx + py * Ly + pz * Lz + 0.05) / 1.05; if (dl < 0) dl = 0;
          let s = Math.pow(dl, 0.85) * (0.72 + 0.28 * pz);
          const pA = px * Ax + py * Ay + pz * Az;
          if (pA * LA < 0) { const kk = -pA / LA, rx = px + kk * Lx, ry = py + kk * Ly, rz = pz + kk * Lz, rho = Math.sqrt(rx * rx + ry * ry + rz * rz);
            if (rho > R0 - 0.05 && rho < R1 + 0.05) s *= 1 - 0.8 * opFiltrada(rho, 0.03); }
          const lat = Math.asin(pA > 1 ? 1 : pA < -1 ? -1 : pA), lon = Math.atan2(px * Wx + py * Wy + pz * Wz, px * Ux + py * Uy + pz * Uz) / DOSPI + 0.5;
          let u = (lon - desp) * TW; u -= Math.floor(u / TW) * TW;
          let fila = ((0.5 - lat / Math.PI) * TH) | 0; if (fila < 0) fila = 0; else if (fila >= TH) fila = TH - 1;
          const i0 = u | 0, f = u - i0, o0 = (fila * TW + i0) * 3, o1 = (fila * TW + ((i0 + 1) & (TW - 1))) * 3;
          const tr_ = TEX[o0] + (TEX[o1] - TEX[o0]) * f, tg = TEX[o0 + 1] + (TEX[o1 + 1] - TEX[o0 + 1]) * f, tb = TEX[o0 + 2] + (TEX[o1 + 2] - TEX[o0 + 2]) * f;
          let lado = 0.2 + 0.8 * (px * 0.85 - py * 0.3); if (lado < 0) lado = 0; const rim = (1 - pz) * (1 - pz) * (1 - s) * lado * 0.75;
          pr = tr_ * (s * KR + AR) + BR * rim; pg = tg * (s * KG + AG) + BG * rim; pb = tb * (s * KB + AB) + BB * rim;
        } else pa = 0;
      }
      let ar = 0, ag = 0, ab = 0, ao = 0, delante = true;   // los anillos
      const zr = -(x * Ax + y * Ay) / Az, rho2 = q + zr * zr;
      if (rho2 > rq0 && rho2 < rq1 && !(pa >= 1 && zr < zp)) {
        const rho = Math.sqrt(rho2), gx = (x + zr * dzx) / rho, gy = (y + zr * dzy) / rho;
        let w = PX * Math.sqrt(gx * gx + gy * gy); if (w < 2 * HM) w = 2 * HM;
        const lo = rho - w / 2, hi = rho + w / 2, sop = acum(CO, hi) - acum(CO, lo), o = sop / w;
        if (o > 0.002) {
          const bq = x * Lx + y * Ly + zr * Lz; let sh = 1;
          if (bq < 0) { const dist = Math.sqrt(Math.max(0, rho2 - bq * bq)); sh = 0.07 + 0.93 * suave(0.97, 1.04, dist); }
          let ang = Math.atan2(x * Wx + y * Wy + zr * Wz, x * Ux + y * Uy + zr * Uz) / DOSPI + 0.5 + rot * 0.8 / (rho * Math.sqrt(rho));
          ang = (ang - Math.floor(ang)) * RA;
          const j0 = ang | 0, fa = ang - j0, fr = Math.min(RR - 1, Math.max(0, ((rho - R0) / (R1 - R0) * RR) | 0)) * RA;
          const m = 0.84 + 0.32 * (RUIDO_ANILLO[fr + j0] * (1 - fa) + RUIDO_ANILLO[fr + ((j0 + 1) & (RA - 1))] * fa);
          const cara = caraLuz ? 1 : 0.3 + 0.55 * (1 - o), k2 = (0.98 + 0.16 * (-x / rho)) * sh * m * cara / sop;
          ar = (acum(CR, hi) - acum(CR, lo)) * k2 * QR + BR * 0.08 * (1 - sh * cara);
          ag = (acum(CG, hi) - acum(CG, lo)) * k2 * QG + BG * 0.08 * (1 - sh * cara);
          ab = (acum(CB, hi) - acum(CB, lo)) * k2 * QB + BB * 0.08 * (1 - sh * cara);
          ao = o > 1 ? 1 : o; delante = pa <= 0 || zr > zp;
        }
      }
      let r, g, b, a;                                         // composición: lo de atrás primero
      if (delante) { r = ar * ao + pr * pa * (1 - ao); g = ag * ao + pg * pa * (1 - ao); b = ab * ao + pb * pa * (1 - ao); a = ao + pa * (1 - ao); }
      else { r = pr * pa + ar * ao * (1 - pa); g = pg * pa + ag * ao * (1 - pa); b = pb * pa + ab * ao * (1 - pa); a = pa + ao * (1 - pa); }
      const o = idx[k] * 4;
      if (a > 0.002) { d[o] = r / a; d[o + 1] = g / a; d[o + 2] = b / a; d[o + 3] = a * 255; } else d[o + 3] = 0;
    }
    ctx.putImageData(img, 0, 0);
  }

  /* ---------- nieve que gira dentro del cristal ---------- */
  const COPOS = Array.from({ length: 90 }, (_, i) => ({ a: hash(i, 11) * Math.PI * 2, r: 0.08 + Math.sqrt(hash(i, 12)) * 0.78, y: hash(i, 13) * 1.7 - 0.85,
    s: 0.6 + hash(i, 14) * 1.3, f: hash(i, 15) * 6.28, v: 1 + hash(i, 16) * 3, brillo: hash(i, 17) < 0.28 }));
  function moverNieve(t, dt, agit) {
    COPOS.forEach((c, i) => {
      c.a += dt * (0.18 + 2.4 * agit) * (0.55 + 0.45 / (0.35 + c.r));
      c.y += dt * (-0.055 + agit * 0.34 * Math.sin(t * 0.9 + i * 1.7));
      c.r = Math.min(0.86, Math.max(0.05, c.r + dt * agit * 0.12 * Math.sin(t * 0.7 + i)));
      const lim = Math.sqrt(Math.max(0.0001, 0.86 * 0.86 - c.r * c.r));
      if (c.y < -lim) { c.y = lim; c.a = hash(i, Math.floor(t * 10)) * Math.PI * 2; } else if (c.y > lim) c.y = lim;
    });
  }
  function dibujarNieve(g, c, r, w, t, luz, atras) {
    for (const p of COPOS) {
      const X = p.r * Math.cos(p.a), Z = p.r * Math.sin(p.a), y2 = p.y * CEL - Z * SEL, z2 = p.y * SEL + Z * CEL;
      if ((z2 < 0) !== atras) continue;
      const esc = 1 + 0.35 * z2, tw = 0.5 + 0.5 * Math.sin(t * p.v + p.f), mz = p.brillo ? 0.75 : 0.22;
      const col = [0, 1, 2].map((i) => Math.round(255 + (luz[i] * 255 - 255) * mz * (0.6 + 0.4 * tw)));
      const al = (0.38 + 0.5 * tw) * (atras ? 0.65 : 1), rad = Math.max(0.6, p.s * esc * w / 520 * 1.6);
      const sx = c + X * r, sy = c - y2 * r;
      g.fillStyle = `rgba(${col[0]},${col[1]},${col[2]},${al})`; g.beginPath(); g.arc(sx, sy, rad, 0, Math.PI * 2); g.fill();
      if (p.brillo && tw > 0.82 && !atras) {                 // destello de escarcha
        const l = rad * 4.5 * (tw - 0.82) / 0.18; g.strokeStyle = `rgba(255,255,255,${al})`; g.lineWidth = Math.max(0.5, rad * 0.35);
        g.beginPath(); g.moveTo(sx - l, sy); g.lineTo(sx + l, sy); g.moveTo(sx, sy - l); g.lineTo(sx, sy + l); g.stroke();
      }
    }
  }

  /* ---------- tiempo: todo gira más rápido al hablar y mucho más al pensar ---------- */
  let saturnoEn = null, costo = 0, ultimoT = null, giro = 0.12, rot = 0.2, ciclo = 0, agit = 0.15, pintadoEn = null, luz = [0, 0, 0], borde = [0, 0, 0];
  function colorEn(u) {
    u = ((u % 4) + 4) % 4; const i = Math.floor(u), k = suave(0.55, 1, u - i), a = COLORES[i], b = COLORES[(i + 1) % 4];
    return [0, 1, 2].map((j) => (a[j] + (b[j] - a[j]) * k) / 255);
  }
  function avanzar(t, est, extra) {
    if (!G) preparar();
    if (t === pintadoEn) return;
    const dt = ultimoT === null ? 0 : Math.min(0.1, Math.max(0, t - ultimoT)); ultimoT = t;
    const vel = est.piensa ? 3.2 : est.habla ? 1.6 : 1;
    giro += dt * vel / 16; rot += dt * vel / 10; ciclo += dt * vel / 3;
    const meta = est.piensa ? 0.85 : est.habla ? 0.35 + extra * 0.9 : est.oye ? 0.3 : 0.12;
    agit += (meta - agit) * Math.min(1, dt * 2.5);
    moverNieve(t, dt, agit);
    luz = colorEn(ciclo); borde = colorEn(ciclo + 1.6);
    // Saturno se recalcula a 30 cuadros por segundo (20 si el teléfono va lento); la nieve y las luces van a todo cuadro
    if (saturnoEn === null || t - saturnoEn >= (costo > 12 ? 1 / 20 : 1 / 30) - 0.002 || dt === 0) {
      const t0 = performance.now(); pintarSaturno(giro, rot, luz, borde); costo = costo * 0.9 + (performance.now() - t0) * 0.1; saturnoEn = t;
    }
    pintadoEn = t;
  }
  const rgba = (c, a) => `rgba(${Math.round(c[0] * 255)},${Math.round(c[1] * 255)},${Math.round(c[2] * 255)},${a})`;
  const claro = (c, k) => c.map((x) => x + (1 - x) * k);

  function dibujar(cv, t, extra = 0, est = {}) {
    avanzar(t, est, extra);
    const g = cv.getContext("2d"), w = cv.width, c = w / 2;
    const k = 1 + 0.012 * Math.sin(t * 1.6) + extra * 0.05, r = w * 0.3 * k;
    g.clearRect(0, 0, w, w);
    // halo exterior del color de turno: late con la voz, palpita al escuchar
    const oye = est.oye ? 0.5 + 0.5 * Math.sin(t * 5.5) : 0, ha = 0.26 + extra * 0.5 + oye * 0.18;
    const halo = g.createRadialGradient(c, c, r * 0.9, c, c, r * 1.66);
    halo.addColorStop(0, rgba(luz, ha)); halo.addColorStop(0.45, rgba(luz, ha * 0.22)); halo.addColorStop(1, rgba(luz, 0));
    g.fillStyle = halo; g.fillRect(0, 0, w, w);
    const piso = g.createRadialGradient(c, c + r * 1.08, 0, c, c + r * 1.08, r * 0.7);
    piso.addColorStop(0, "rgba(0,0,0,.35)"); piso.addColorStop(1, "rgba(0,0,0,0)");
    g.save(); g.translate(c, c + r * 1.08); g.scale(1, 0.18); g.translate(-c, -(c + r * 1.08)); g.fillStyle = piso; g.fillRect(0, 0, w, w); g.restore();

    g.save(); g.beginPath(); g.arc(c, c, r, 0, Math.PI * 2); g.clip();
    // el interior: azul noche con una nube del color de turno
    const fondo = g.createRadialGradient(c - r * 0.25, c - r * 0.3, r * 0.05, c, c, r);
    fondo.addColorStop(0, "#173f6c"); fondo.addColorStop(0.5, "#0a2142"); fondo.addColorStop(1, "#020914");
    g.fillStyle = fondo; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    const neb = g.createRadialGradient(c + r * 0.3, c + r * 0.32, 0, c + r * 0.3, c + r * 0.32, r * 0.9);
    neb.addColorStop(0, rgba(luz, 0.3 + extra * 0.2)); neb.addColorStop(1, rgba(luz, 0));
    g.fillStyle = neb; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    const neb2 = g.createRadialGradient(c - r * 0.45, c - r * 0.2, 0, c - r * 0.45, c - r * 0.2, r * 0.7);
    neb2.addColorStop(0, rgba(borde, 0.16)); neb2.addColorStop(1, rgba(borde, 0));
    g.fillStyle = neb2; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    dibujarNieve(g, c, r, w, t, luz, true);
    const aura = g.createRadialGradient(c, c, r * 0.1, c, c, r * 0.95);
    aura.addColorStop(0, `rgba(245,194,107,${0.1 + extra * 0.3})`); aura.addColorStop(1, "rgba(245,194,107,0)");
    g.fillStyle = aura; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    // Saturno
    const escala = (r * 0.4) / (N / (2 * S));
    g.save(); g.translate(c, c + r * 0.02); g.rotate(-0.12 + 0.04 * Math.sin(t * 0.33)); g.scale(escala, escala);
    g.imageSmoothingEnabled = true; g.imageSmoothingQuality = "high"; g.drawImage(G.lienzo, -N / 2, -N / 2); g.restore();
    dibujarNieve(g, c, r, w, t, luz, false);
    // grosor del cristal, luz refractada abajo y borde de Fresnel del color de turno
    const vin = g.createRadialGradient(c, c, r * 0.6, c, c, r);
    vin.addColorStop(0, "rgba(2,8,20,0)"); vin.addColorStop(1, "rgba(2,8,20,.55)");
    g.fillStyle = vin; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    g.save(); g.translate(c + r * 0.08, c + r * 0.74); g.scale(1, 0.32);
    const caus = g.createRadialGradient(0, 0, 0, 0, 0, r * 0.56); caus.addColorStop(0, rgba(claro(luz, 0.3), 0.34 + extra * 0.25)); caus.addColorStop(1, rgba(luz, 0));
    g.fillStyle = caus; g.beginPath(); g.arc(0, 0, r * 0.56, 0, Math.PI * 2); g.fill(); g.restore();
    const fres = g.createRadialGradient(c, c, r * 0.83, c, c, r);
    fres.addColorStop(0, rgba(luz, 0)); fres.addColorStop(1, rgba(claro(luz, 0.35), 0.38 + extra * 0.3 + oye * 0.35));
    g.fillStyle = fres; g.fillRect(c - r, c - r, 2 * r, 2 * r);
    if (est.piensa) { const a = t * 3.2; g.strokeStyle = rgba(claro(luz, 0.6), 0.8); g.lineWidth = r * 0.05; g.lineCap = "round";
      g.shadowColor = rgba(luz, 0.9); g.shadowBlur = r * 0.12; g.beginPath(); g.arc(c, c, r * 0.95, a, a + 0.7); g.stroke(); g.shadowBlur = 0; }
    // reflejos del cristal: ventana grande arriba a la izquierda, media luna de luz y rebote de color abajo a la derecha
    g.save(); g.translate(c - r * 0.36, c - r * 0.44); g.rotate(-0.62); g.scale(1, 0.55);
    const esp = g.createRadialGradient(0, 0, 0, 0, 0, r * 0.46); esp.addColorStop(0, "rgba(255,255,255,.42)"); esp.addColorStop(0.55, "rgba(255,255,255,.1)"); esp.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = esp; g.beginPath(); g.arc(0, 0, r * 0.46, 0, Math.PI * 2); g.fill(); g.restore();
    const media = (dx, dy, color) => { g.beginPath(); g.arc(c, c, r * 0.97, 0, Math.PI * 2); g.arc(c + dx * r, c + dy * r, r * 0.97, 0, Math.PI * 2, true); g.fillStyle = color; g.fill(); };
    const ml = g.createLinearGradient(c - r, c - r, c, c); ml.addColorStop(0, "rgba(255,255,255,.34)"); ml.addColorStop(0.6, "rgba(255,255,255,0)");
    media(0.07, 0.09, ml);
    const mr = g.createLinearGradient(c + r, c + r, c, c); mr.addColorStop(0, rgba(claro(borde, 0.2), 0.3 + extra * 0.2)); mr.addColorStop(0.5, rgba(borde, 0));
    media(-0.05, -0.06, mr);
    g.restore();
    g.save(); g.translate(c - r * 0.46, c - r * 0.52); g.rotate(-0.7); g.fillStyle = "rgba(255,255,255,.85)";
    g.beginPath(); g.ellipse(0, 0, r * 0.11, r * 0.045, 0, 0, Math.PI * 2); g.fill(); g.restore();
    const filo = g.createLinearGradient(c - r, c - r, c + r, c + r);
    filo.addColorStop(0, "rgba(230,250,255,.75)"); filo.addColorStop(0.5, rgba(claro(luz, 0.5), 0.2)); filo.addColorStop(1, rgba(claro(borde, 0.4), 0.55));
    g.strokeStyle = filo; g.lineWidth = Math.max(1, w * 0.004); g.beginPath(); g.arc(c, c, r - g.lineWidth / 2, 0, Math.PI * 2); g.stroke();
  }

  window.OrbeSaturno = { dibujar, costo: () => costo };
})();
