// «Despacho»: oficina de noche en estilo low-poly (ventanal con ciudad azul desenfocada, escritorio, portátil, lámpara, taza)
// con el Personaje 01 sentado. El portátil muestra Apex Domicilios funcionando; e.panel (0..4) y e.avance (0..1) lo controlan.
// Estado: e.p01 = { mira, miraY, ladea, bd, bi, taza } (vía e.pose*), voz del personaje con la línea "p01".
function despacho(escena) {
  const D = new THREE.Group(); D.position.set(0, 0, 120); escena.add(D); const U = {}, r = semilla(4242);
  U.fondo = 0x0a1438; U.niebla = [0x0a1438, 0.03];
  const F = (col, rg = 0.75, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: col, roughness: rg, flatShading: true }, o));
  const add = (geo, m, x, y, z, padre = D) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; padre.add(o); return o; };
  // sala: piso, paredes oscuras y ventanal con ciudad de noche
  add(new THREE.PlaneGeometry(14, 14), F(0x1a1f33, 0.7), 0, 0, 0).rotation.x = -PI / 2;
  const pared = F(0x121831, 0.9); add(new THREE.BoxGeometry(10, 4, 0.1), pared, 0, 2, -3.2);
  const vid = add(new THREE.PlaneGeometry(6.2, 3.0), new THREE.MeshBasicMaterial({ color: 0x0a1a4a }), 0, 1.75, -3.12); vid.castShadow = false;
  for (let i = 0; i < 5; i++) add(new THREE.BoxGeometry(0.06, 3.1, 0.08), F(0x0b0e18, 0.5), -3 + i * 1.5, 1.75, -3.08);
  add(new THREE.BoxGeometry(6.3, 0.07, 0.1), F(0x0b0e18, 0.5), 0, 0.22, -3.08);
  const bok = (() => { const c = document.createElement("canvas"); c.width = c.height = 64; const g = c.getContext("2d"), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, "rgba(255,255,255,.95)"); gr.addColorStop(0.6, "rgba(255,255,255,.5)"); gr.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
  U.luces = []; for (let i = 0; i < 260; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: bok, color: r() < 0.68 ? 0x6f9bff : 0xffc37a, transparent: true, opacity: 0.3 + r() * 0.55, depthWrite: false, fog: false }));
    s.position.set((r() - 0.5) * 7, 0.4 + r() * 3.0, -3.6 - r() * 4); s.scale.setScalar(0.06 + r() * 0.28); D.add(s); U.luces.push([s, r() * 10]); }
  // escritorio, silla, lámpara, taza y libros
  const madera = F(0x2a2433, 0.6); add(new THREE.BoxGeometry(1.7, 0.05, 0.85), madera, 0, 0.75, 0); [[-0.8, -0.38], [0.8, -0.38], [-0.8, 0.38], [0.8, 0.38]].forEach(([x, z]) => add(new THREE.BoxGeometry(0.05, 0.73, 0.05), F(0x16141c, 0.6), x, 0.365, z));
  add(new THREE.BoxGeometry(0.55, 0.06, 0.5), F(0x101218, 0.7), 0, 0.46, -0.7); add(new THREE.BoxGeometry(0.55, 0.65, 0.06), F(0x101218, 0.7), 0, 0.8, -0.96);
  const lampG = new THREE.Group(); lampG.position.set(0.6, 0.775, -0.15); D.add(lampG); add(new THREE.CylinderGeometry(0.07, 0.08, 0.02, 8), F(0x2b2b30, 0.4), 0, 0, 0, lampG);
  add(new THREE.CylinderGeometry(0.008, 0.008, 0.42, 6), F(0xb07a3a, 0.35, { metalness: 0.6 }), 0, 0.21, 0, lampG).rotation.z = 0.2;
  const pant = add(new THREE.ConeGeometry(0.09, 0.13, 7, 1, true), F(0x3a2e24, 0.5, { side: THREE.DoubleSide }), -0.06, 0.44, 0.04, lampG); pant.rotation.z = 0.9;
  const bomb = add(new THREE.SphereGeometry(0.022, 8, 6), new THREE.MeshBasicMaterial({ color: 0xffe2b0 }), -0.1, 0.4, 0.05, lampG);
  U.luzLampara = new THREE.SpotLight(0xffc98f, 6, 3.2, 0.9, 0.7, 1.4); U.luzLampara.position.set(0.5, 1.2, -0.05); U.luzLampara.target.position.set(0, 0.95, -0.6); U.luzLampara.castShadow = true; U.luzLampara.shadow.mapSize.set(2048, 2048); U.luzLampara.shadow.bias = -0.0003; U.luzLampara.shadow.radius = 3; D.add(U.luzLampara); D.add(U.luzLampara.target);
  const mug = add(new THREE.CylinderGeometry(0.045, 0.04, 0.1, 9), F(0x8a7e72, 0.5), 0.32, 0.825, 0.12); const tapa = add(new THREE.CircleGeometry(0.04, 9), new THREE.MeshBasicMaterial({ color: 0xffe6b8 }), 0.32, 0.876, 0.12); tapa.rotation.x = -PI / 2;
  [0x6a2a2a, 0x2a4a6a, 0xc9a24a].forEach((c, i) => add(new THREE.BoxGeometry(0.22, 0.04, 0.16), F(c, 0.8), -0.68, 0.795 + i * 0.04, -0.22));
  // portátil girado hacia el personaje, con la pantalla de Apex Domicilios
  const lap = new THREE.Group(); lap.position.set(-0.28, 0.775, -0.05); lap.rotation.y = PI + 0.42; D.add(lap);
  add(new THREE.BoxGeometry(0.46, 0.018, 0.32), F(0xa9adb8, 0.35, { metalness: 0.5 }), 0, 0.009, 0, lap);
  const bis = new THREE.Group(); bis.position.set(0, 0.018, -0.16); bis.rotation.x = -0.32; lap.add(bis); add(new THREE.BoxGeometry(0.46, 0.3, 0.012), F(0xa9adb8, 0.35, { metalness: 0.5 }), 0, 0.15, 0, bis);
  const cv = document.createElement("canvas"); cv.width = 2048; cv.height = 1280; const gx = cv.getContext("2d"); gx.scale(2, 2), tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const pantalla = add(new THREE.PlaneGeometry(0.43, 0.27), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }), 0, 0.15, 0.0065, bis); pantalla.castShadow = false;
  U.luzPantalla = new THREE.PointLight(0x8fb8ff, 1.2, 1.6, 2); U.luzPantalla.position.set(0, 0.15, 0.25); bis.add(U.luzPantalla);
  U.pantallaMundo = () => { const v = new THREE.Vector3(); pantalla.getWorldPosition(v); return v; };
  // personaje 01 sentado detrás del escritorio
  U.p01 = personaLowPoly(Object.assign({ semilla: 31, fuerte: true, peinado: "definitivo", barbaNivel: 0.95, detalle: true, piel: "#c98e6b", pelo: "#16100c", barba: "#1a120e", camisa: "#17181c", iris: "#3a281a" }));
  U.p01.raiz.position.set(0, 0, -0.68); D.add(U.p01.raiz);
  // compañeras de trabajo (aparecen con e.equipo > 0.5): Valeria (caja) a la izquierda y Sofía (cocina) a la derecha, de pie frente al escritorio
  U.val = personaLowPoly({ semilla: 57, mujer: true, detalle: true, peinado: "melena", piel: "#d9a383", pelo: "#2a1810", labios: "#b8615a", camisa: "#7a2e3a", pantalon: "#1f2230", iris: "#4a2e1a" });
  U.sof = personaLowPoly({ semilla: 73, mujer: true, detalle: true, peinado: "coleta", piel: "#a8714f", pelo: "#140d0a", labios: "#9a4a44", camisa: "#f2efe9", pantalon: "#2a2a30", iris: "#2e1e14", delantal: true });
  U.val.raiz.position.set(-0.6, 0, 0.66); U.val.raiz.rotation.y = 0.75; U.sof.raiz.position.set(0.6, 0, 0.64); U.sof.raiz.rotation.y = -0.75;
  [U.val, U.sof].forEach((q) => { q.raiz.visible = false; D.add(q.raiz); });
  // luces generales: azul de la ciudad y relleno cálido suave
  D.add(new THREE.HemisphereLight(0x5a78d8, 0x2a2440, 0.85));
  const contra = new THREE.DirectionalLight(0x6f8fff, 2.1); contra.position.set(1.6, 2.6, -3); contra.castShadow = true; contra.shadow.mapSize.set(2048, 2048); Object.assign(contra.shadow.camera, { left: -2, right: 2, top: 2.5, bottom: -1, near: 0.5, far: 10 }); D.add(contra);
  const rim = new THREE.SpotLight(0x9fb8ff, 5, 4, 0.5, 0.8, 1.5); rim.position.set(-1.2, 1.8, -2.0); rim.target.position.set(0, 1.25, -0.68); D.add(rim); D.add(rim.target);
  const relleno = new THREE.DirectionalLight(0xffe2c8, 0.55); relleno.position.set(0.5, 1.8, 3); D.add(relleno);
  // ---------- Navidad (e.navidad > 0.5): guirnalda de bombillos en el ventanal y arbolito low-poly con esferas
  const NAV = new THREE.Group(); NAV.visible = false; D.add(NAV); U.bombillos = [];
  const colN = [0xff3b3b, 0x3bff7a, 0xffd23b, 0x3bb8ff, 0xff7ad9];
  for (let i = 0; i <= 44; i++) { const x = -3 + i * (6 / 44), y = 2.05 - 0.2 * Math.abs(Math.sin((x + 3) / 1.5 * PI));
    const m = new THREE.MeshBasicMaterial({ color: colN[i % 5], fog: false }); const b = new THREE.Mesh(new THREE.SphereGeometry(0.035, 8, 6), m); b.position.set(x, y, -3.0); NAV.add(b);
    const h = new THREE.Sprite(new THREE.SpriteMaterial({ map: bok, color: colN[i % 5], transparent: true, opacity: 0.55, depthWrite: false, fog: false })); h.position.copy(b.position); h.scale.setScalar(0.32); NAV.add(h); U.bombillos.push([m, h, i]); }
  const arbol = new THREE.Group(); arbol.position.set(-0.85, 0, -1.75); arbol.scale.setScalar(1.25); NAV.add(arbol);
  add(new THREE.CylinderGeometry(0.05, 0.06, 0.18, 6), F(0x4a2c18, 0.8), 0, 0.09, 0, arbol);
  [[0.46, 0.5, 0.42], [0.36, 0.42, 0.74], [0.25, 0.34, 1.02]].forEach(([rad, h, y]) => add(new THREE.ConeGeometry(rad, h, 7), F(0x1e5a34, 0.8), 0, y, 0, arbol));
  add(new THREE.OctahedronGeometry(0.06), new THREE.MeshBasicMaterial({ color: 0xffd23b }), 0, 1.24, 0, arbol);
  for (let i = 0; i < 16; i++) { const a = i * 2.4, y = 0.32 + (i / 16) * 0.8, rad = 0.4 * (1 - (y - 0.25) / 1.0) + 0.03;
    add(new THREE.SphereGeometry(0.03, 7, 5), F(colN[i % 5], 0.3, { metalness: 0.4, emissive: colN[i % 5], emissiveIntensity: 0.35 }), Math.cos(a) * rad, y, Math.sin(a) * rad, arbol); }
  const calido = new THREE.PointLight(0xffb070, 0.9, 2.2, 2); calido.position.set(-0.75, 1.0, -1.4); NAV.add(calido);
  // ---------- interfaz de Apex Domicilios en el portátil
  const rr = (X, Y, w, h, rad) => { gx.beginPath(); gx.roundRect(X, Y, w, h, rad); };
  const txt = (s, X, Y, f, c, al = "left") => { gx.font = f; gx.fillStyle = c; gx.textAlign = al; gx.fillText(s, X, Y); };
  function ui(panel, k, t, e = {}) {
    gx.fillStyle = "#070b14"; gx.fillRect(0, 0, 1024, 640); gx.fillStyle = "#0e1626"; gx.fillRect(0, 0, 1024, 70);
    gx.fillStyle = "#36c2f5"; rr(30, 18, 34, 34, 9); gx.fill(); txt("Apex Domicilios", 78, 46, "800 28px Figtree", "#eef4fa"); txt("Panel del restaurante", 994, 46, "600 20px Figtree", "#7d8b99", "right");
    txt("PEDIDOS DE HOY", 40, 120, "700 18px Figtree", "#7d8b99"); txt(String(Math.round(e.pedidos ?? 38 + 4 * Math.min(1, k * 2))), 40, 182, "800 64px Figtree", "#36c2f5");
    if (e.navidad > 0.5) { rr(560, 22, 190, 28, 14); gx.fillStyle = "rgba(255,59,59,.22)"; gx.fill(); txt("✦ Tema navideño", 655, 42, "700 16px Figtree", "#ff8a8a", "center"); }
    txt("COMISIÓN", 300, 120, "700 18px Figtree", "#7d8b99"); txt("$ 0", 300, 182, "800 64px Figtree", panel >= 4 ? "#ffc35a" : "#eef4fa");
    const peds = [["#1042", "2 × Bandeja paisa", "$ 64.000"], ["#1043", "Ajiaco de la casa", "$ 24.000"], ["#1044", "Hamburguesa artesanal", "$ 28.000"]];
    peds.forEach(([id, pl, pr], i) => { const a = Math.min(1, Math.max(0, k * 3 - i * 0.6)); if (a <= 0) return; const Y = 220 + i * 88; gx.globalAlpha = a; rr(40, Y, 560, 74, 14); gx.fillStyle = "#121b2b"; gx.fill();
      txt(id, 62, Y + 30, "700 18px Figtree", "#7d8b99"); txt(pl, 62, Y + 58, "600 24px Figtree", "#eef4fa"); txt(pr, 580, Y + 30, "700 22px Figtree", "#eef4fa", "right");
      const est = i === 0 ? (panel >= 3 ? "EN CAMINO · CLIENTE AVISADO ✓" : panel >= 2 ? "PAGADO ✓" : "NUEVO") : i === 1 ? "EN COCINA" : "RECIBIDO";
      txt(est, 580, Y + 58, "700 16px Figtree", i === 0 && panel >= 2 ? "#4ce08a" : "#36c2f5", "right"); gx.globalAlpha = 1; });
    // tarjeta derecha según el paso: chat del asistente, pago Wompi, aviso al cliente
    rr(630, 100, 360, 500, 18); gx.fillStyle = "#0e1626"; gx.fill();
    if (panel <= 1) { txt("ASISTENTE · CHAT DEL CLIENTE", 652, 136, "700 15px Figtree", "#7d8b99");
      const b = (s, Y, ia) => { rr(ia ? 700 : 652, Y, 270, 64, 16); gx.fillStyle = ia ? "rgba(54,194,245,.18)" : "#18233a"; gx.fill(); txt(s, ia ? 716 : 668, Y + 40, "600 19px Figtree", "#eef4fa"); };
      if (k > 0.1) b("Dos bandejas paisas, porfa", 160, false); if (k > 0.3) b("¡Listo! Son $ 64.000", 240, true); if (k > 0.5) b("Pago con Wompi", 320, false); }
    if (panel === 2) { txt("PAGO", 652, 136, "700 15px Figtree", "#7d8b99"); txt("Wompi", 652, 200, "800 46px Figtree", "#4ce08a"); txt("$ 64.000", 652, 252, "700 30px Figtree", "#eef4fa");
      rr(652, 290, 316, 70, 35); gx.fillStyle = "#4ce08a"; gx.fill(); txt("APROBADO ✓", 810, 335, "800 26px Figtree", "#04140a", "center");
      txt("o si prefiere: solo mira el comprobante", 652, 410, "500 18px Figtree", "#7d8b99"); }
    if (panel >= 3) { txt("AVISO AL CLIENTE", 652, 136, "700 15px Figtree", "#7d8b99"); rr(652, 160, 316, 150, 20); gx.fillStyle = "#18233a"; gx.fill();
      txt("Su restaurante", 676, 200, "700 18px Figtree", "#ffc35a"); txt("¡Su pedido ya salió!", 676, 244, "800 28px Figtree", "#eef4fa"); txt("Llega en unos 25 minutos", 676, 282, "500 18px Figtree", "#7d8b99");
      txt("Enviado automáticamente", 652, 350, "600 18px Figtree", "#4ce08a"); }
    if (panel === 6 || panel === 7) { rr(630, 100, 360, 500, 18); gx.fillStyle = "#0e1626"; gx.fill(); const A = (x) => Math.min(1, Math.max(0, (k - x) * 4));
      if (panel === 6) { txt("CON APLICACIONES", 652, 136, "700 15px Figtree", "#7d8b99");
        gx.globalAlpha = A(0); txt("Ventas al mes", 652, 182, "600 20px Figtree", "#9fb0c2"); txt("$ 10.000.000", 968, 182, "800 24px Figtree", "#eef4fa", "right");
        gx.globalAlpha = A(0.2); txt("Comisión 25 %", 652, 232, "600 20px Figtree", "#9fb0c2"); txt("− $ 2.500.000", 968, 232, "800 24px Figtree", "#ff6b6b", "right");
        gx.globalAlpha = A(0.45); gx.fillStyle = "#2a1418"; rr(652, 270, 316, 130, 16); gx.fill(); txt("AL AÑO SE VAN", 672, 306, "700 16px Figtree", "#ff9a9a"); txt("$ 30.000.000", 672, 370, "900 46px Figtree", "#ff5a5a"); gx.globalAlpha = 1; }
      if (panel === 7) { txt("CON SU PROPIO LINK", 652, 136, "700 15px Figtree", "#7d8b99");
        gx.globalAlpha = A(0); txt("Plan mensual", 652, 182, "600 20px Figtree", "#9fb0c2"); txt("$ 120.000", 968, 182, "800 24px Figtree", "#eef4fa", "right");
        gx.globalAlpha = A(0.15); txt("Comisión por pedido", 652, 232, "600 20px Figtree", "#9fb0c2"); txt("$ 0", 968, 232, "800 24px Figtree", "#4ce08a", "right");
        gx.globalAlpha = A(0.4); gx.fillStyle = "#0f2a1c"; rr(652, 270, 316, 130, 16); gx.fill(); txt("AHORRO AL AÑO", 672, 306, "700 16px Figtree", "#9dffbf"); txt("$ 28.560.000", 672, 370, "900 44px Figtree", "#4ce08a"); gx.globalAlpha = 1; } }
    if (panel === 5 || panel >= 8) { rr(630, 100, 360, 500, 18); gx.fillStyle = "#0e1626"; gx.fill(); txt("REGALO DE DICIEMBRE", 652, 136, "700 15px Figtree", "#7d8b99");
      txt("Tema navideño", 652, 196, "800 34px Figtree", "#ff8a8a"); txt("para su restaurante", 652, 230, "500 20px Figtree", "#9fb0c2");
      txt("8 platos en 3D", 652, 300, "800 34px Figtree", "#ffd23b"); txt("de obsequio", 652, 334, "500 20px Figtree", "#9fb0c2");
      txt("Soporte 24/7", 652, 404, "800 34px Figtree", "#4ce08a"); txt("para la temporada alta", 652, 438, "500 20px Figtree", "#9fb0c2"); }
    tex.needsUpdate = true;
  }
  // ---------- interfaz de Apex Play (e.app = 1): el asistente de cada mesa, en vivo. panel: 0 salón, 1 mesa 7, 2 mesa 12 (inglés), 3 mesa 3 (cuenta), 4 mesa 7 (cliente frecuente)
  function uiPlay(panel, k, t) {
    gx.fillStyle = "#070b14"; gx.fillRect(0, 0, 1024, 640); gx.fillStyle = "#0e1626"; gx.fillRect(0, 0, 1024, 70);
    gx.fillStyle = "#f5a636"; rr(30, 18, 34, 34, 17); gx.fill(); txt("Apex Play", 78, 46, "800 28px Figtree", "#eef4fa"); txt("Salón en vivo", 994, 46, "600 20px Figtree", "#7d8b99", "right");
    txt("MESAS ATENDIDAS", 40, 112, "700 16px Figtree", "#7d8b99"); txt("12 / 12", 40, 160, "800 46px Figtree", "#f5a636");
    txt("ESPERA PROMEDIO", 300, 112, "700 16px Figtree", "#7d8b99"); txt("0 min", 300, 160, "800 46px Figtree", "#eef4fa");
    const foco = [0, 7, 12, 3, 7][Math.min(4, panel)];
    for (let i = 0; i < 12; i++) { const n = i + 1, X = 40 + (i % 4) * 142, Y = 196 + Math.floor(i / 4) * 128, f = n === foco;
      rr(X, Y, 128, 112, 16); gx.fillStyle = f ? "rgba(245,166,54,.22)" : "#121b2b"; gx.fill(); if (f) { gx.strokeStyle = "#f5a636"; gx.lineWidth = 3; gx.stroke(); }
      txt("Mesa " + n, X + 16, Y + 34, "700 20px Figtree", "#eef4fa");
      const pul = 0.55 + 0.45 * Math.sin(t * 3 + i); gx.globalAlpha = pul; gx.fillStyle = "#4ce08a"; gx.beginPath(); gx.arc(X + 24, Y + 72, 8, 0, 7); gx.fill(); gx.globalAlpha = 1;
      txt(n === 7 ? "Pidiendo" : n === 12 ? "English" : n === 3 ? "Cuenta" : "Asistente ✓", X + 40, Y + 79, "600 16px Figtree", "#9fb0c2"); }
    rr(630, 100, 360, 500, 18); gx.fillStyle = "#0e1626"; gx.fill();
    const b = (s, Y, ia, a) => { if (a <= 0) return; gx.globalAlpha = Math.min(1, a); rr(ia ? 690 : 652, Y, 280, 64, 16); gx.fillStyle = ia ? "rgba(245,166,54,.2)" : "#18233a"; gx.fill(); txt(s, ia ? 706 : 668, Y + 40, "600 19px Figtree", "#eef4fa"); gx.globalAlpha = 1; };
    const ok = (s, Y, a) => { if (a <= 0) return; gx.globalAlpha = Math.min(1, a); rr(652, Y, 316, 60, 30); gx.fillStyle = "#4ce08a"; gx.fill(); txt(s, 810, Y + 39, "800 21px Figtree", "#04140a", "center"); gx.globalAlpha = 1; };
    const A = (x) => (k - x) * 4;
    if (panel === 0) { txt("ASISTENTE EN CADA MESA", 652, 136, "700 15px Figtree", "#7d8b99"); txt("Toma pedidos", 652, 200, "800 34px Figtree", "#eef4fa"); txt("Recomienda platos", 652, 248, "800 34px Figtree", "#eef4fa"); txt("Habla idiomas", 652, 296, "800 34px Figtree", "#eef4fa"); txt("Llama al mesero", 652, 344, "800 34px Figtree", "#eef4fa"); }
    if (panel === 1) { txt("MESA 7", 652, 136, "700 15px Figtree", "#7d8b99"); b("Otra ronda de limonadas", 160, false, A(0.05)); b("¡Claro! 4 limonadas", 240, true, A(0.3)); ok("ENVIADO A COCINA ✓", 330, A(0.55)); }
    if (panel === 2) { txt("MESA 12 · ENGLISH", 652, 136, "700 15px Figtree", "#7d8b99"); b("What do you recommend?", 160, false, A(0.05)); b("Try our bandeja paisa!", 240, true, A(0.3)); ok("PEDIDO TOMADO ✓", 330, A(0.55)); }
    if (panel === 3) { txt("MESA 3", 652, 136, "700 15px Figtree", "#7d8b99"); b("La cuenta, por favor", 160, false, A(0.05)); ok("MESERO AVISADO ✓", 250, A(0.35)); }
    if (panel >= 4) { txt("MESA 7 · CLIENTE FRECUENTE", 652, 136, "700 15px Figtree", "#7d8b99"); txt("Doña Marta", 652, 200, "800 40px Figtree", "#f5a636"); txt("Viene cada domingo", 652, 244, "500 20px Figtree", "#9fb0c2"); txt("Pide: limonada de coco", 652, 278, "500 20px Figtree", "#9fb0c2"); }
    tex.needsUpdate = true;
  }
  D.userData = U;
  U.paso = (tt, e = {}) => {
    U.luces.forEach(([s, f]) => { s.material.opacity = Math.max(0.15, s.material.opacity * 0.98 + 0.02 * (0.5 + 0.4 * Math.sin(tt * 0.7 + f))); });
    U.p01.pose({ sentado: true, mira: e.mira ?? 0.35, miraY: e.miraY ?? 0.08, ladea: e.ladea ?? 0, voz: e.voz01 || 0, taza: e.taza > 0.5,
      bi: e.manos === 0 ? [0.15, -0.12, -0.35] : [-0.95, -0.12, -0.75], bd: e.taza > 0.5 ? [-0.55, 0.42, -1.85] : e.manos === 0 ? [0.15, 0.12, -0.35] : [-0.95, 0.12, -0.75], cejas: e.cejas || 0 });
    const eq = e.equipo > 0.5, vz = e.vozDe || (() => 0);
    [[U.val, "val", e.miraVal ?? 0, e.brazoVal ?? 0], [U.sof, "sof", e.miraSof ?? 0, e.brazoSof ?? 0]].forEach(([q, id, m, br], j) => { q.raiz.visible = eq; if (!eq) return;
      const v = vz(id), resp = Math.sin(tt * 1.6 + j * 2) * 0.012;
      q.pose({ mira: m, miraY: -0.08 + resp, ladea: (j ? -1 : 1) * 0.05, voz: v, taza: e.tazas > 0.5, cejas: e.cejasEq || 0,
        bi: br > 0.5 ? [-0.9, -0.25, -1.2] : [0.05, -0.1, -0.2 - v * 0.3], bd: e.tazas > 0.5 ? [-0.55, 0.42, -1.85] : br > 0.5 ? [-0.9, 0.25, -1.2] : [0.05, 0.1, -0.2 - v * 0.3] }); });
    NAV.visible = e.navidad > 0.5;
    if (NAV.visible) U.bombillos.forEach(([m, h, i]) => { const on = 0.35 + 0.65 * (0.5 + 0.5 * Math.sin(tt * 2.2 + i * 1.7)); m.color.setHex(colN[i % 5]).multiplyScalar(0.4 + 0.6 * on); h.material.opacity = 0.2 + 0.45 * on; });
    (e.app > 0.5 ? uiPlay : ui)(Math.round(e.panel ?? 0), e.avance ?? 1, tt, e);
  };
  return D;
}
