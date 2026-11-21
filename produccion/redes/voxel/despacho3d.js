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
  U.luzLampara = new THREE.SpotLight(0xffc98f, 6, 3.2, 0.9, 0.7, 1.4); U.luzLampara.position.set(0.5, 1.2, -0.05); U.luzLampara.target.position.set(0, 0.95, -0.6); U.luzLampara.castShadow = true; D.add(U.luzLampara); D.add(U.luzLampara.target);
  const mug = add(new THREE.CylinderGeometry(0.045, 0.04, 0.1, 9), F(0x8a7e72, 0.5), 0.32, 0.825, 0.12); const tapa = add(new THREE.CircleGeometry(0.04, 9), new THREE.MeshBasicMaterial({ color: 0xffe6b8 }), 0.32, 0.876, 0.12); tapa.rotation.x = -PI / 2;
  [0x6a2a2a, 0x2a4a6a, 0xc9a24a].forEach((c, i) => add(new THREE.BoxGeometry(0.22, 0.04, 0.16), F(c, 0.8), -0.68, 0.795 + i * 0.04, -0.22));
  // portátil girado hacia el personaje, con la pantalla de Apex Domicilios
  const lap = new THREE.Group(); lap.position.set(-0.28, 0.775, -0.05); lap.rotation.y = PI + 0.42; D.add(lap);
  add(new THREE.BoxGeometry(0.46, 0.018, 0.32), F(0xa9adb8, 0.35, { metalness: 0.5 }), 0, 0.009, 0, lap);
  const bis = new THREE.Group(); bis.position.set(0, 0.018, -0.16); bis.rotation.x = -0.32; lap.add(bis); add(new THREE.BoxGeometry(0.46, 0.3, 0.012), F(0xa9adb8, 0.35, { metalness: 0.5 }), 0, 0.15, 0, bis);
  const cv = document.createElement("canvas"); cv.width = 1024; cv.height = 640; const gx = cv.getContext("2d"), tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const pantalla = add(new THREE.PlaneGeometry(0.43, 0.27), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }), 0, 0.15, 0.0065, bis); pantalla.castShadow = false;
  U.luzPantalla = new THREE.PointLight(0x8fb8ff, 1.2, 1.6, 2); U.luzPantalla.position.set(0, 0.15, 0.25); bis.add(U.luzPantalla);
  U.pantallaMundo = () => { const v = new THREE.Vector3(); pantalla.getWorldPosition(v); return v; };
  // personaje 01 sentado detrás del escritorio
  U.p01 = personaLowPoly(Object.assign({ semilla: 31, fuerte: true, peinado: "definitivo", barbaNivel: 0.95, piel: "#c98e6b", pelo: "#16100c", barba: "#1a120e", camisa: "#17181c", iris: "#3a281a" }));
  U.p01.raiz.position.set(0, 0, -0.68); D.add(U.p01.raiz);
  // luces generales: azul de la ciudad y relleno cálido suave
  D.add(new THREE.HemisphereLight(0x5a78d8, 0x2a2440, 0.85));
  const contra = new THREE.DirectionalLight(0x6f8fff, 1.5); contra.position.set(1.6, 2.6, -3); D.add(contra);
  const relleno = new THREE.DirectionalLight(0xffe2c8, 0.55); relleno.position.set(0.5, 1.8, 3); D.add(relleno);
  // ---------- interfaz de Apex Domicilios en el portátil
  const rr = (X, Y, w, h, rad) => { gx.beginPath(); gx.roundRect(X, Y, w, h, rad); };
  const txt = (s, X, Y, f, c, al = "left") => { gx.font = f; gx.fillStyle = c; gx.textAlign = al; gx.fillText(s, X, Y); };
  function ui(panel, k, t) {
    gx.fillStyle = "#070b14"; gx.fillRect(0, 0, 1024, 640); gx.fillStyle = "#0e1626"; gx.fillRect(0, 0, 1024, 70);
    gx.fillStyle = "#36c2f5"; rr(30, 18, 34, 34, 9); gx.fill(); txt("Apex Domicilios", 78, 46, "800 28px Figtree", "#eef4fa"); txt("Panel del restaurante", 994, 46, "600 20px Figtree", "#7d8b99", "right");
    txt("PEDIDOS DE HOY", 40, 120, "700 18px Figtree", "#7d8b99"); txt(String(Math.round(38 + 4 * Math.min(1, k * 2))), 40, 182, "800 64px Figtree", "#36c2f5");
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
    tex.needsUpdate = true;
  }
  D.userData = U;
  U.paso = (tt, e = {}) => {
    U.luces.forEach(([s, f]) => { s.material.opacity = Math.max(0.15, s.material.opacity * 0.98 + 0.02 * (0.5 + 0.4 * Math.sin(tt * 0.7 + f))); });
    U.p01.pose({ sentado: true, mira: e.mira ?? 0.35, miraY: e.miraY ?? 0.08, ladea: e.ladea ?? 0, voz: e.voz01 || 0, taza: e.taza > 0.5,
      bi: e.manos === 0 ? [0.15, -0.12, -0.35] : [-0.95, -0.12, -0.75], bd: e.taza > 0.5 ? [-0.55, 0.42, -1.85] : e.manos === 0 ? [0.15, 0.12, -0.35] : [-0.95, 0.12, -0.75], cejas: e.cejas || 0 });
    ui(Math.round(e.panel ?? 0), e.avance ?? 1, tt);
  };
  return D;
}
