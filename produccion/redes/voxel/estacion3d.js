// «Estación»: puesto de trabajo de alta gama (metal oscuro, vidrio, pantallas OLED) con Apex Play y Apex Domicilios funcionando.
// Estado (e): enc (pantallas encendidas 0..1), play, dom, ana, holo, menu (avance de cada interfaz 0..1), luz (intensidad general).
function estacion(escena) {
  const E = new THREE.Group(); escena.add(E); E.position.set(0, 0, 90); const U = {}, r = semilla(2024);
  U.fondo = 0x030407; U.niebla = [0x04060a, 0.075];
  const AMBAR = "#E8A04A", AMBAR2 = "#F2B866", ACERO = "#6F8FA8", ACERO2 = "#9DBAD6", BLANCO = "#E9EEF3", GRIS = "#6B7A88", PANEL = "#0D1118";

  // ---------- reflejos: un estudio pequeño con paneles de luz ámbar y azul acero
  const pm = new THREE.PMREMGenerator(REN), env = new THREE.Scene();
  env.add(new THREE.Mesh(new THREE.BoxGeometry(20, 10, 20), new THREE.MeshBasicMaterial({ color: 0x030405, side: THREE.BackSide })));
  [[-6, 4, 3, 4, 2, 0xffa24a, 2.2], [6, 3, -6, 6, 3, 0x6f9ac8, 1.6], [0, 4.9, 0, 6, 1, 0xdfe6ee, 0.6], [0, 1.5, 9.5, 8, 1.2, 0x8fb0d0, 0.5]].forEach(([x, y, z, w, h, c, k]) => {
    const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(c).multiplyScalar(k), side: THREE.DoubleSide }));
    p.position.set(x, y, z); p.lookAt(0, 1, 0); env.add(p); });
  const ENV = pm.fromScene(env, 0.035).texture;
  const metal = (c, m, rg, k = 1) => new THREE.MeshStandardMaterial({ color: c, metalness: m, roughness: rg, envMap: ENV, envMapIntensity: k });

  // ---------- sala: piso pulido, pared con lamas de luz
  const piso = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), metal(0x07080a, 0.7, 0.32, 0.7)); piso.rotation.x = -PI / 2; piso.receiveShadow = true; E.add(piso);
  const pared = new THREE.Mesh(new THREE.PlaneGeometry(14, 7), metal(0x07090c, 0.3, 0.8, 0.4)); pared.position.set(0, 3.5, -3.2); pared.receiveShadow = true; E.add(pared);
  U.lamas = [];
  for (let i = 0; i < 11; i++) { const x = -3.75 + i * 0.75, m = new THREE.MeshBasicMaterial({ color: 0x6f9ac8 });
    const l = new THREE.Mesh(new THREE.BoxGeometry(0.018, 3.4, 0.02), m); l.position.set(x, 2.3, -3.15); E.add(l); U.lamas.push(l); }
  U.ranura = new THREE.Mesh(new THREE.BoxGeometry(7.6, 0.012, 0.02), new THREE.MeshBasicMaterial({ color: 0xe8a04a })); U.ranura.position.set(0, 0.42, -3.12); E.add(U.ranura);

  // ---------- escritorio: losa de metal oscuro con filo de luz ámbar
  const mesaM = metal(0x101216, 0.85, 0.22, 1.6);
  const tapa = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.05, 1.0), mesaM); tapa.position.set(0, 0.75, 0); tapa.castShadow = tapa.receiveShadow = true; E.add(tapa);
  [-1.1, 1.1].forEach((x) => { const p = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.73, 0.9), mesaM); p.position.set(x, 0.365, 0); p.castShadow = true; E.add(p); });
  U.filo = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.006, 0.006), new THREE.MeshBasicMaterial({ color: 0xffa24a })); U.filo.position.set(0, 0.728, 0.503); E.add(U.filo);
  const vidrio = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.004, 0.36), new THREE.MeshStandardMaterial({ color: 0x0a1016, metalness: 0.2, roughness: 0.05, envMap: ENV, envMapIntensity: 1.6, transparent: true, opacity: 0.75 }));
  vidrio.position.set(0, 0.777, 0.27); E.add(vidrio);

  // ---------- teclado con luz por debajo
  const tec = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.014, 0.15), metal(0x111317, 0.8, 0.3)); tec.position.set(0, 0.786, 0.26); tec.castShadow = true; E.add(tec);
  const teclas = new THREE.InstancedMesh(new THREE.BoxGeometry(0.024, 0.008, 0.022), metal(0x16191e, 0.5, 0.45, 0.6), 75), mt = new THREE.Matrix4();
  for (let f = 0; f < 5; f++) for (let c = 0; c < 15; c++) { mt.makeTranslation(-0.196 + c * 0.028, 0.797, 0.205 + f * 0.027); teclas.setMatrixAt(f * 15 + c, mt); } E.add(teclas);
  U.bajoTec = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.19), new THREE.MeshBasicMaterial({ map: texturaRadial("rgba(255,170,90,0.9)", "rgba(255,170,90,0)"), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
  U.bajoTec.rotation.x = -PI / 2; U.bajoTec.position.set(0, 0.7765, 0.26); E.add(U.bajoTec);

  // ---------- interfaces: lienzos que se redibujan cada cuadro
  const lienzo = (w, h) => { const c = document.createElement("canvas"); c.width = w; c.height = h; const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return { c, x: c.getContext("2d"), t }; };
  const rr = (x, X, Y, w, h, r) => { x.beginPath(); x.roundRect(X, Y, w, h, r); };
  const txt = (x, s, X, Y, font, color, al = "left") => { x.font = font; x.fillStyle = color; x.textAlign = al; x.fillText(s, X, Y); };
  const esp = (x, s, X, Y, px, color, sp = 0.28, al = "left") => { x.font = `700 ${px}px Figtree`; x.fillStyle = color; x.textAlign = al; x.letterSpacing = `${px * sp}px`; x.fillText(s.toUpperCase(), X, Y); x.letterSpacing = "0px"; };
  const tipeo = (s, k) => s.slice(0, Math.floor(s.length * cl(k)));

  function monitor(x, z, rot) {
    const g = new THREE.Group(); g.position.set(x, 1.24, z); g.rotation.y = rot; E.add(g);
    const marco = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.78, 0.016), metal(0x0a0b0d, 0.9, 0.22)); marco.castShadow = true; g.add(marco);
    const L = lienzo(576, 1000), pant = new THREE.Mesh(new THREE.PlaneGeometry(0.43, 0.7465), new THREE.MeshBasicMaterial({ map: L.t, toneMapped: false })); pant.position.z = 0.0085; g.add(pant);
    const vid = new THREE.Mesh(new THREE.PlaneGeometry(0.43, 0.7465), new THREE.MeshStandardMaterial({ color: 0x000000, metalness: 0, roughness: 0.04, envMap: ENV, envMapIntensity: 0.35, transparent: true, opacity: 0.22 })); vid.position.z = 0.0095; g.add(vid);
    const tallo = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.45, 0.02), metal(0x14161a, 0.9, 0.25)); tallo.position.set(0, -0.48, -0.05); g.add(tallo);
    const base = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.008, 0.12), metal(0x14161a, 0.9, 0.25)); base.position.set(0, -0.486, -0.06); g.add(base);
    const luz = new THREE.PointLight(0x9cbad8, 0.6, 2.2, 2); luz.position.set(0, 0, 0.25); g.add(luz);
    return { g, L, pant, luz };
  }
  U.mon = { ana: monitor(-0.52, -0.14, 0.5), play: monitor(0, -0.3, 0), dom: monitor(0.52, -0.14, -0.5) };

  // tableta de cocina sobre el escritorio
  const tabG = new THREE.Group(); tabG.position.set(0.72, 0.79, 0.24); tabG.rotation.set(-PI / 2 + 0.32, 0, -0.35); E.add(tabG);
  const tabM = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.18, 0.008), metal(0x0b0c0e, 0.9, 0.25)); tabM.castShadow = true; tabG.add(tabM);
  U.tab = lienzo(624, 432); const tabP = new THREE.Mesh(new THREE.PlaneGeometry(0.245, 0.168), new THREE.MeshBasicMaterial({ map: U.tab.t, toneMapped: false })); tabP.position.z = 0.0045; tabG.add(tabP);

  // hologramas de vidrio: flujo de la IA y carta digital
  function holo(w, h, cw, ch, pos, rot) {
    const g = new THREE.Group(); g.position.set(...pos); g.rotation.set(...rot); E.add(g);
    const L = lienzo(cw, ch), m = new THREE.MeshBasicMaterial({ map: L.t, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, toneMapped: false });
    g.add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), m));
    const tinte = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: 0x5f86ad, transparent: true, opacity: 0.05, depthWrite: false, side: THREE.DoubleSide }));
    tinte.position.z = -0.002; g.add(tinte);
    const borde = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(w, h)), new THREE.LineBasicMaterial({ color: 0x9dbad6, transparent: true, opacity: 0.6 })); g.add(borde);
    return { g, L, m, tinte, borde, y0: pos[1] };
  }
  U.flujo = holo(0.92, 0.36, 1024, 400, [0, 1.84, -0.12], [0, 0, 0]);
  U.carta = holo(0.34, 0.5, 544, 800, [-0.86, 1.12, 0.34], [0, 0.62, 0]);

  // ---------- luces: llave ámbar dura desde arriba, contraluz azul acero
  escena.add(new THREE.HemisphereLight(0x22303e, 0x050403, 0.0));
  U.llave = new THREE.SpotLight(0xffa24a, 55, 9, 0.42, 0.75, 2); U.llave.position.set(-1.3, 3.3, 1.0); U.llave.target.position.set(0.1, 0.75, -0.05);
  U.llave.castShadow = true; U.llave.shadow.mapSize.set(1024, 1024); U.llave.shadow.bias = -0.0004; E.add(U.llave); E.add(U.llave.target);
  U.contra = new THREE.SpotLight(0x6f9ac8, 45, 9, 0.55, 0.8, 2); U.contra.position.set(1.6, 2.6, -2.4); U.contra.target.position.set(0, 1.0, 0); E.add(U.contra); E.add(U.contra.target);
  U.relleno = new THREE.PointLight(0x5a7c9e, 5, 8, 2); U.relleno.position.set(1.8, 2.0, 2.4); E.add(U.relleno);

  // rayo volumétrico de la luz llave
  const rayoM = new THREE.ShaderMaterial({ uniforms: { color: { value: new THREE.Color(1.0, 0.62, 0.3) }, k: { value: 0.35 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    vertexShader: "varying vec3 vN; varying vec3 vV; varying float vY; void main(){ vec4 mv = modelViewMatrix * vec4(position,1.0); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz); vY = uv.y; gl_Position = projectionMatrix * mv; }",
    fragmentShader: "uniform vec3 color; uniform float k; varying vec3 vN; varying vec3 vV; varying float vY; void main(){ float borde = pow(abs(dot(vN, vV)), 2.2); float a = borde * mix(0.05, 1.0, pow(vY, 1.4)) * k; gl_FragColor = vec4(color * a, 1.0); }" });
  const de = U.llave.position.clone(), a = U.llave.target.position.clone(), largo = de.distanceTo(a);
  U.rayo = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 1.25, largo, 48, 1, true), rayoM); U.rayo.position.copy(de).add(a).multiplyScalar(0.5);
  U.rayo.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), de.clone().sub(a).normalize()); E.add(U.rayo);

  // polvo dentro del rayo y bokeh (fuera de foco) cerca de la cámara
  const n = 700, pp = new Float32Array(n * 3); U.polvoB = [];
  for (let i = 0; i < n; i++) { const k = r(), c = a.clone().lerp(de, k * 0.9), rad = (0.06 + 1.2 * (1 - k)) * Math.sqrt(r()), an = r() * PI * 2;
    U.polvoB.push([c.x + Math.cos(an) * rad, c.y, c.z + Math.sin(an) * rad, r() * 10]); }
  const pg = new THREE.BufferGeometry(); pg.setAttribute("position", new THREE.BufferAttribute(pp, 3));
  U.polvo = new THREE.Points(pg, new THREE.PointsMaterial({ color: 0xffc890, size: 0.006, transparent: true, opacity: 0.8, depthWrite: false, blending: THREE.AdditiveBlending })); E.add(U.polvo);
  const disco = (() => { const c = document.createElement("canvas"); c.width = c.height = 128; const x = c.getContext("2d"), g = x.createRadialGradient(64, 64, 0, 64, 64, 62);
    g.addColorStop(0, "rgba(255,255,255,0.55)"); g.addColorStop(0.78, "rgba(255,255,255,0.7)"); g.addColorStop(0.9, "rgba(255,255,255,0.95)"); g.addColorStop(1, "rgba(255,255,255,0)");
    x.fillStyle = g; x.beginPath(); x.arc(64, 64, 62, 0, PI * 2); x.fill(); return new THREE.CanvasTexture(c); })();
  U.bokeh = [];
  for (let i = 0; i < 26; i++) { const ambar = r() < 0.55, s = new THREE.Sprite(new THREE.SpriteMaterial({ map: disco, color: ambar ? 0xffa860 : 0x7fa6cc, transparent: true, opacity: 0.0, blending: THREE.AdditiveBlending, depthWrite: false }));
    const b = [(r() - 0.5) * 3.2, 0.6 + r() * 1.8, -0.6 + r() * 2.6]; s.position.set(...b); const t0 = 0.03 + r() * 0.09; s.scale.setScalar(t0); E.add(s); U.bokeh.push({ s, b, f: r() * 10, o: 0.12 + r() * 0.2 }); }

  // destellos anamórficos (rayas horizontales azul acero)
  const raya = (() => { const c = document.createElement("canvas"); c.width = 1024; c.height = 32; const x = c.getContext("2d");
    for (let X = 0; X < 1024; X++) { const h = Math.pow(1 - Math.abs(X - 512) / 512, 2.2); const g = x.createLinearGradient(0, 0, 0, 32);
      g.addColorStop(0, "rgba(255,255,255,0)"); g.addColorStop(0.5, `rgba(255,255,255,${h})`); g.addColorStop(1, "rgba(255,255,255,0)"); x.fillStyle = g; x.fillRect(X, 0, 1, 32); }
    return new THREE.CanvasTexture(c); })();
  const destello = (pos, ancho, color, op) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: raya, color, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false }));
    s.position.set(...pos); s.scale.set(ancho, ancho * 0.012, 1); E.add(s); return { s, op }; };
  const nucleo = (pos, t, color) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: texturaRadial("rgba(255,255,255,1)", "rgba(255,255,255,0)"), color, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    s.position.set(...pos); s.scale.setScalar(t); E.add(s); return s; };
  U.flares = [destello([-1.3, 3.3, 1.0], 6, 0x8fb4dc, 0.7), destello([0, 1.62, -0.28], 3.2, 0x8fb4dc, 0.35), destello([0, 0.73, 0.51], 4, 0xffb070, 0.25)];
  U.foco = nucleo([-1.3, 3.3, 1.0], 0.5, 0xffc080);

  // ---------- dibujo de las interfaces
  function cabecera(x, W, marca, titulo, t) {
    x.fillStyle = "#06080b"; x.fillRect(0, 0, W, 1000);
    const g = x.createLinearGradient(0, 0, 0, 1000); g.addColorStop(0, "rgba(111,143,168,0.10)"); g.addColorStop(1, "rgba(0,0,0,0)"); x.fillStyle = g; x.fillRect(0, 0, W, 1000);
    esp(x, marca, 36, 64, 20, AMBAR); txt(x, titulo, 36, 112, "700 38px Figtree", BLANCO);
    x.fillStyle = ACERO2; x.globalAlpha = 0.5 + 0.5 * Math.sin(t * 3); x.beginPath(); x.arc(W - 48, 56, 7, 0, PI * 2); x.fill(); x.globalAlpha = 1;
    esp(x, "En línea", W - 64, 63, 15, GRIS, 0.2, "right");
    x.fillStyle = "rgba(111,143,168,0.25)"; x.fillRect(36, 140, W - 72, 2);
  }
  function burbuja(x, s, X, Y, w, ia, k) {
    if (k <= 0) return 0; x.globalAlpha = cl(k * 3); x.font = "500 24px Figtree"; const pal = s.split(" "), lin = []; let l = "";
    pal.forEach((p) => { const pr = l ? l + " " + p : p; if (x.measureText(pr).width > w - 44) { lin.push(l); l = p; } else l = pr; }); lin.push(l);
    const h = 26 + lin.length * 32; rr(x, X, Y, w, h, 18); x.fillStyle = ia ? "rgba(232,160,74,0.14)" : "#121821"; x.fill();
    x.strokeStyle = ia ? "rgba(232,160,74,0.55)" : "rgba(111,143,168,0.35)"; x.lineWidth = 2; x.stroke();
    lin.forEach((s2, i) => txt(x, s2, X + 22, Y + 40 + i * 32, "500 24px Figtree", ia ? "#F6E3C8" : BLANCO)); x.globalAlpha = 1; return h;
  }
  function pPlay(k, t, enc) {
    const { x } = U.mon.play.L, W = 576; cabecera(x, W, "Apex Play", "Asistente de mesa", t);
    esp(x, "Mesas atendidas a la vez", 36, 186, 16, GRIS, 0.2);
    for (let i = 0; i < 20; i++) { const c = i % 5, f = Math.floor(i / 5), X = 36 + c * 102, Y = 206 + f * 62, on = cl(k * 26 - i * 0.6);
      rr(x, X, Y, 90, 50, 10); x.fillStyle = on > 0 ? `rgba(232,160,74,${0.08 + 0.14 * on})` : "#0e131a"; x.fill();
      x.strokeStyle = on > 0 ? `rgba(242,184,102,${0.35 + 0.6 * on})` : "rgba(111,143,168,0.22)"; x.lineWidth = 2; x.stroke();
      txt(x, String(i + 1), X + 45, Y + 33, "700 22px Figtree", on > 0.5 ? AMBAR2 : GRIS, "center"); }
    x.fillStyle = "rgba(111,143,168,0.25)"; x.fillRect(36, 470, W - 72, 2);
    esp(x, "Mesa 7 · conversación", 36, 512, 16, ACERO2, 0.2);
    let y = 534; const cK = (a, b) => cl((k - a) / (b - a));
    y += burbuja(x, "¿Qué nos recomienda para dos personas?", 36, y, 400, false, cK(0.12, 0.2)) + 14;
    y += burbuja(x, tipeo("Les recomiendo el ajiaco de la casa y dos limonadas de coco.", cK(0.25, 0.42)), 140, y, 400, true, cK(0.24, 0.3)) + 14;
    y += burbuja(x, "Perfecto. Uno sin alcaparras, por favor.", 36, y, 400, false, cK(0.48, 0.55)) + 14;
    // onda de voz mientras habla el cliente
    const habla = (k > 0.1 && k < 0.22) || (k > 0.46 && k < 0.57);
    for (let i = 0; i < 46; i++) { const h = habla ? 6 + 30 * Math.abs(Math.sin(t * 11 + i * 0.7) * Math.sin(t * 3.3 + i * 0.31)) : 3;
      x.fillStyle = habla ? AMBAR : "rgba(111,143,168,0.4)"; x.fillRect(40 + i * 11, 952 - h / 2, 5, h); }
    // pedido listo para cocina
    const pk = cK(0.62, 0.72);
    if (pk > 0) { x.globalAlpha = pk; const Y = Math.max(y, 770); rr(x, 36, Y, W - 72, 150, 16); x.fillStyle = "#0f141b"; x.fill(); x.strokeStyle = "rgba(242,184,102,0.7)"; x.lineWidth = 2; x.stroke();
      esp(x, "Pedido · mesa 7", 60, Y + 38, 15, AMBAR, 0.24); txt(x, "2 × Ajiaco de la casa", 60, Y + 76, "600 24px Figtree", BLANCO);
      txt(x, "Uno sin alcaparras", 84, Y + 106, "500 20px Figtree", GRIS); txt(x, "2 × Limonada de coco", 60, Y + 136, "600 24px Figtree", BLANCO);
      if (k > 0.8) { rr(x, W - 236, Y + 20, 180, 40, 20); x.fillStyle = AMBAR; x.fill(); esp(x, "En cocina ✓", W - 146, Y + 47, 15, "#1a1006", 0.14, "center"); }
      x.globalAlpha = 1; }
    U.mon.play.L.t.needsUpdate = true;
  }
  function pDom(k, t) {
    const { x } = U.mon.dom.L, W = 576; cabecera(x, W, "Apex Domicilios", "Pedidos directos", t);
    esp(x, "Comisión por pedido", 36, 196, 16, GRIS, 0.2); txt(x, "$ 0", 36, 300, "800 110px Figtree", AMBAR2);
    txt(x, "Su propio enlace de pedidos", 36, 344, "500 24px Figtree", ACERO2);
    x.fillStyle = "rgba(111,143,168,0.25)"; x.fillRect(36, 384, W - 72, 2);
    const ped = [["#1042", "Bandeja paisa", "$ 32.000", "En camino"], ["#1043", "Ajiaco de la casa", "$ 24.000", "En cocina"], ["#1044", "Hamburguesa artesanal", "$ 28.000", "Recibido"], ["#1045", "Arroz con pollo", "$ 22.000", "Recibido"]];
    ped.forEach(([id, plato, precio, est], i) => { const a = cl((k - 0.08 - i * 0.12) / 0.1); if (a <= 0) return; const Y = 410 + i * 104;
      x.globalAlpha = a; x.save(); x.translate((1 - suave(a)) * 40, 0); rr(x, 36, Y, W - 72, 88, 14); x.fillStyle = "#0e131a"; x.fill(); x.strokeStyle = "rgba(111,143,168,0.3)"; x.lineWidth = 2; x.stroke();
      txt(x, id, 58, Y + 36, "700 18px Figtree", GRIS); txt(x, plato, 58, Y + 68, "600 25px Figtree", BLANCO); txt(x, precio, W - 60, Y + 36, "700 22px Figtree", BLANCO, "right");
      const c = est === "En camino" ? AMBAR : est === "En cocina" ? ACERO2 : GRIS; esp(x, est, W - 60, Y + 70, 14, c, 0.18, "right"); x.restore(); x.globalAlpha = 1; });
    const nk = cl((k - 0.62) / 0.1);
    if (nk > 0) { x.globalAlpha = nk; const Y = 840; rr(x, 36, Y, W - 72, 110, 16); x.fillStyle = "rgba(232,160,74,0.12)"; x.fill(); x.strokeStyle = "rgba(242,184,102,0.7)"; x.lineWidth = 2; x.stroke();
      esp(x, "Comprobante de pago", 60, Y + 42, 15, AMBAR, 0.22); txt(x, "Nequi · $ 32.000 · Verificado ✓", 60, Y + 82, "600 25px Figtree", BLANCO); x.globalAlpha = 1; }
    U.mon.dom.L.t.needsUpdate = true;
  }
  function pAna(k, t) {
    const { x } = U.mon.ana.L, W = 576; cabecera(x, W, "Operación", "En tiempo real", t);
    const kp = [["Pedidos hoy", String(Math.round(148 * suave(cl(k * 1.3))))], ["Mesas activas", `${Math.round(18 * suave(cl(k * 1.5)))} / 20`]];
    kp.forEach(([a, b], i) => { const X = 36 + i * 258; rr(x, X, 170, 246, 130, 14); x.fillStyle = "#0e131a"; x.fill(); x.strokeStyle = "rgba(111,143,168,0.3)"; x.lineWidth = 2; x.stroke();
      esp(x, a, X + 22, 210, 14, GRIS, 0.2); txt(x, b, X + 22, 274, "800 52px Figtree", i ? BLANCO : AMBAR2); });
    esp(x, "Pedidos por hora", 36, 350, 15, GRIS, 0.2);
    const ys = [0.18, 0.22, 0.3, 0.52, 0.78, 0.62, 0.4, 0.46, 0.7, 0.92, 0.84, 0.6], X0 = 36, X1 = W - 36, Y0 = 640, Y1 = 380, np = ys.length, lim = cl(k * 1.2) * (np - 1);
    for (let i = 0; i < 5; i++) { x.fillStyle = "rgba(111,143,168,0.12)"; x.fillRect(X0, Y1 + i * 65, X1 - X0, 1); }
    const P = (i) => [X0 + (X1 - X0) * i / (np - 1), Y0 - (Y0 - Y1) * (ys[Math.floor(i)] + (ys[Math.min(np - 1, Math.floor(i) + 1)] - ys[Math.floor(i)]) * (i % 1))];
    x.beginPath(); x.moveTo(X0, Y0); for (let i = 0; i <= lim; i += 0.1) x.lineTo(...P(i)); x.lineTo(P(lim)[0], Y0); x.closePath();
    const g = x.createLinearGradient(0, Y1, 0, Y0); g.addColorStop(0, "rgba(111,143,168,0.45)"); g.addColorStop(1, "rgba(111,143,168,0)"); x.fillStyle = g; x.fill();
    x.beginPath(); for (let i = 0; i <= lim; i += 0.1) x[i ? "lineTo" : "moveTo"](...P(i)); x.strokeStyle = AMBAR; x.lineWidth = 4; x.stroke();
    const [px, py] = P(lim); x.fillStyle = AMBAR2; x.beginPath(); x.arc(px, py, 8, 0, PI * 2); x.fill();
    esp(x, "Origen de los pedidos", 36, 712, 15, GRIS, 0.2);
    [["En mesa · Apex Play", 0.64, AMBAR], ["Domicilio directo · Apex Domicilios", 0.36, ACERO2]].forEach(([s, v, c], i) => { const Y = 740 + i * 96;
      txt(x, s, 36, Y + 22, "600 22px Figtree", BLANCO); rr(x, 36, Y + 38, W - 72, 18, 9); x.fillStyle = "#121821"; x.fill();
      rr(x, 36, Y + 38, Math.max(18, (W - 72) * v * suave(cl((k - 0.3) / 0.4))), 18, 9); x.fillStyle = c; x.fill(); });
    esp(x, "Sin comisiones de terceros", 36, 960, 15, AMBAR, 0.2);
    U.mon.ana.L.t.needsUpdate = true;
  }
  function pTab(k, t) {
    const { x, c } = U.tab; x.fillStyle = "#06080b"; x.fillRect(0, 0, c.width, c.height);
    esp(x, "Cocina", 28, 52, 18, AMBAR, 0.3); txt(x, "Nuevo pedido", 28, 96, "700 34px Figtree", BLANCO);
    if (k > 0.8) { const a = cl((k - 0.8) / 0.06); x.globalAlpha = a; rr(x, 28, 130, 568, 260, 16); x.fillStyle = "#0f141b"; x.fill(); x.strokeStyle = `rgba(242,184,102,${0.4 + 0.5 * Math.abs(Math.sin(t * 4))})`; x.lineWidth = 3; x.stroke();
      esp(x, "Mesa 7", 56, 180, 18, AMBAR2, 0.24); txt(x, "2 × Ajiaco de la casa", 56, 238, "600 32px Figtree", BLANCO); txt(x, "Uno sin alcaparras", 84, 280, "500 26px Figtree", GRIS);
      txt(x, "2 × Limonada de coco", 56, 338, "600 32px Figtree", BLANCO); x.globalAlpha = 1; }
    else txt(x, "Esperando pedidos…", 28, 200, "500 28px Figtree", GRIS);
    U.tab.t.needsUpdate = true;
  }
  function pFlujo(k, t) {
    const { x, c } = U.flujo.L; x.clearRect(0, 0, c.width, c.height); x.fillStyle = "#000"; x.fillRect(0, 0, c.width, c.height);
    const nodos = [["Voz del cliente", 120], ["IA Apex", 400], ["Pedido", 650], ["Cocina", 900]], Y = 200;
    x.strokeStyle = "rgba(157,186,214,0.55)"; x.lineWidth = 3; x.beginPath(); x.moveTo(120, Y); x.lineTo(900, Y); x.stroke();
    nodos.forEach(([s, X], i) => { const on = cl(k * 4 - i * 0.8); const R = i === 1 ? 62 : 44;
      const g = x.createRadialGradient(X, Y, 0, X, Y, R * 2.2); g.addColorStop(0, `rgba(232,160,74,${0.5 * on})`); g.addColorStop(1, "rgba(0,0,0,0)"); x.fillStyle = g; x.fillRect(X - R * 2.2, Y - R * 2.2, R * 4.4, R * 4.4);
      x.beginPath(); x.arc(X, Y, R, 0, PI * 2); x.fillStyle = "#000"; x.fill(); x.strokeStyle = on > 0.5 ? AMBAR2 : ACERO2; x.lineWidth = 4; x.stroke();
      if (i === 1) { for (let j = 0; j < 3; j++) { x.beginPath(); x.arc(X, Y, R - 14 - j * 12, t * (1.2 + j * 0.5), t * (1.2 + j * 0.5) + 2.2); x.strokeStyle = `rgba(242,184,102,${0.8 - j * 0.2})`; x.lineWidth = 3; x.stroke(); } }
      esp(x, s, X, Y + R + 50, 22, on > 0.5 ? BLANCO : GRIS, 0.2, "center"); });
    for (let j = 0; j < 14; j++) { const u = ((t * 0.35 + j / 14) % 1), X = 120 + 780 * u; if (X > 120 + 780 * cl(k * 1.3)) continue;
      const g = x.createRadialGradient(X, Y, 0, X, Y, 16); g.addColorStop(0, "rgba(255,214,160,1)"); g.addColorStop(1, "rgba(255,160,80,0)"); x.fillStyle = g; x.fillRect(X - 16, Y - 16, 32, 32); }
    esp(x, "Flujo de pedidos con inteligencia artificial", 512, 66, 20, ACERO2, 0.22, "center");
    U.flujo.L.t.needsUpdate = true;
  }
  function pCarta(k, t) {
    const { x, c } = U.carta.L; x.fillStyle = "#000"; x.fillRect(0, 0, c.width, c.height);
    esp(x, "Carta digital", 40, 70, 22, AMBAR, 0.3); txt(x, "Mesa 7", 40, 118, "700 38px Figtree", BLANCO);
    const platos = [["Ajiaco de la casa", "$ 24.000", true], ["Bandeja paisa", "$ 32.000"], ["Limonada de coco", "$ 9.000", true], ["Postre de natas", "$ 11.000"]];
    const sel = Math.floor(cl(k) * 3.99);
    platos.forEach(([n, p, rec], i) => { const Y = 160 + i * 150, on = i === sel;
      rr(x, 30, Y, 484, 128, 16); x.strokeStyle = on ? AMBAR2 : "rgba(157,186,214,0.5)"; x.lineWidth = on ? 4 : 2; x.stroke();
      if (on) { x.fillStyle = "rgba(232,160,74,0.14)"; x.fill(); }
      txt(x, n, 54, Y + 54, "600 30px Figtree", BLANCO); txt(x, p, 54, Y + 96, "500 26px Figtree", ACERO2);
      if (rec) esp(x, "Recomendado", 490, Y + 54, 14, AMBAR, 0.2, "right"); });
    U.carta.L.t.needsUpdate = true;
  }

  E.userData = U;
  U.paso = (tt, e = {}) => {
    const enc = e.enc ?? 1, I = e.luz && !Array.isArray(e.luz) ? e.luz : 1;
    U.llave.intensity = 130 * I; U.contra.intensity = 90 * I; U.relleno.intensity = 5 * I; U.rayo.material.uniforms.k.value = 0.32 * I; U.foco.material.opacity = 0.9 * I;
    const fil = e.filo ?? enc; U.filo.material.color.setRGB(1.0 * fil, 0.62 * fil, 0.28 * fil); U.bajoTec.material.opacity = 0.6 * fil;
    U.lamas.forEach((l, i) => { const k = cl(enc * 1.6 - Math.abs(i - 5) * 0.12); l.material.color.setRGB(0.17 * k, 0.26 * k, 0.37 * k); });
    U.ranura.material.color.setRGB(0.9 * enc, 0.55 * enc, 0.25 * enc);
    // encendido de pantallas con un parpadeo breve
    Object.values(U.mon).forEach((M, i) => { const k = cl(enc * 1.4 - i * 0.15), fl = k > 0 && k < 1 ? (0.6 + 0.4 * Math.sin(tt * 90 + i)) : 1; M.pant.material.color.setScalar(k * fl); M.luz.intensity = 0.6 * k; });
    pPlay(e.play ?? 0, tt, enc); pDom(e.dom ?? 0, tt); pAna(e.ana ?? 0, tt); pTab(e.play ?? 0, tt); pFlujo(e.flujo ?? 0, tt); pCarta(e.menu ?? 0, tt);
    [[U.flujo, e.holo ?? 0], [U.carta, e.holoC ?? e.holo ?? 0]].forEach(([H, k]) => { const s = suave(k); H.g.position.y = H.y0 - (1 - s) * 0.12; H.m.opacity = s * (0.92 + 0.08 * Math.sin(tt * 7));
      H.tinte.material.opacity = 0.05 * s; H.borde.material.opacity = 0.6 * s; H.g.visible = k > 0.01; });
    const pos = U.polvo.geometry.attributes.position; U.polvoB.forEach(([x, y, z, f], i) => pos.setXYZ(i, x + Math.sin(tt * 0.3 + f) * 0.04, y + Math.sin(tt * 0.21 + f * 1.7) * 0.05, z + Math.cos(tt * 0.25 + f) * 0.04)); pos.needsUpdate = true;
    U.polvo.material.opacity = 0.8 * I;
    U.bokeh.forEach(({ s, b, f, o }) => { s.position.set(b[0] + Math.sin(tt * 0.2 + f) * 0.08, b[1] + Math.sin(tt * 0.15 + f) * 0.06, b[2]); s.material.opacity = o * (0.7 + 0.3 * Math.sin(tt * 0.8 + f)) * (e.bokeh ?? 1); });
    U.flares.forEach(({ s, op }, i) => { s.material.opacity = op * (i === 0 ? I : i === 2 ? fil : enc) * (0.85 + 0.15 * Math.sin(tt * 1.3 + i)); });
  };
  return E;
}
