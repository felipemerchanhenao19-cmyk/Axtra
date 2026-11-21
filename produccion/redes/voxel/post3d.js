// Posproducción en la tarjeta gráfica: desenfoque de lente (DOF) a media resolución + brillo (bloom), mezclados en una sola pasada final.
// Antes: DOF de 30 muestras en cada píxel a resolución completa y bloom copiando el lienzo al procesador (≈3,5 s por cuadro).
// Ahora: el desenfoque se calcula en ¼ de los píxeles, el borde nítido/borroso se decide con la profundidad a resolución completa
// y el bloom se hace en la GPU a 270×480 (el mismo tamaño que tenía el lienzo de bloom). Mismo aspecto, mucho más rápido.
function crearPost(REN, EP) {
  const sz = REN.getDrawingBufferSize(new THREE.Vector2()), W = sz.x, H = sz.y, CAL = EP.calidad || 1;
  // a calidad ≥ 1,3 la escena ya se dibuja más grande y se reduce: no hace falta MSAA; por debajo se usan 4 muestras
  const rt = (w, h, prof, tipo = THREE.HalfFloatType) => { const r = new THREE.WebGLRenderTarget(w, h, { type: tipo, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, depthBuffer: !!prof, samples: prof && CAL < 1.3 ? 4 : 0 });
    if (prof) r.depthTexture = new THREE.DepthTexture(w, h); return r; };
  const ESCENA = rt(W, H, true), MEDIA = rt(Math.ceil(W / 2), Math.ceil(H / 2)), B1 = rt(270, 480, false, THREE.UnsignedByteType), B2 = rt(270, 480, false, THREE.UnsignedByteType);
  const VS = "varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }";
  const PROF = `#include <packing>
    uniform sampler2D tProf; uniform float near, far, foco, fuerza;
    float prof(vec2 uv){ return -perspectiveDepthToViewZ(texture2D(tProf, uv).x, near, far); }
    float coc(float z){ return clamp(abs(z - foco) / max(z, 0.001) * fuerza * 34.0, 0.0, 26.0); }`;
  const comunes = () => ({ tProf: { value: ESCENA.depthTexture }, near: { value: 0.05 }, far: { value: 90 }, foco: { value: 2 }, fuerza: { value: 1 } });
  const mat = (u, fs) => new THREE.ShaderMaterial({ uniforms: u, vertexShader: VS, fragmentShader: fs, depthTest: false, depthWrite: false });
  // 1) Desenfoque (bokeh de disco, mismas 30 muestras y mismo peso anti-sangrado que antes) a media resolución
  const uD = Object.assign(comunes(), { tCol: { value: ESCENA.texture }, px: { value: new THREE.Vector2(CAL / W, CAL / H) } });
  const mDof = mat(uD, `${PROF} uniform sampler2D tCol; uniform vec2 px; varying vec2 vUv;
    void main(){ float c0 = coc(prof(vUv)); vec3 acc = texture2D(tCol, vUv).rgb; float w = 1.0;
      for (int i = 1; i < 30; i++) { float fi = float(i); float r = sqrt(fi / 29.0) * c0; float a = fi * 2.39996;
        vec2 o = vec2(cos(a), sin(a)) * r * px; float cs = coc(prof(vUv + o)); float wi = clamp(cs / max(c0, 0.001), 0.15, 1.0);
        acc += texture2D(tCol, vUv + o).rgb * wi; w += wi; }
      gl_FragColor = vec4(acc / w, 1.0); }`);
  // 2) Brillo: imagen ya con tono de cine (ACES + sRGB), brightness(0.75) contrast(2.2) como el filtro anterior
  const uB = { tCol: { value: MEDIA.texture }, expo: { value: 1.35 }, paso: { value: new THREE.Vector2(0.5 / 270, 0.5 / 480) } };
  const mBri = mat(uB, `uniform sampler2D tCol; uniform float expo; uniform vec2 paso; varying vec2 vUv;
    vec3 RRT(vec3 v){ vec3 a = v * (v + 0.0245786) - 0.000090537; vec3 b = v * (0.983729 * v + 0.4329510) + 0.238081; return a / b; }
    vec3 aces(vec3 c){ const mat3 I = mat3(vec3(0.59719, 0.07600, 0.02840), vec3(0.35458, 0.90834, 0.13383), vec3(0.04823, 0.01566, 0.83777));
      const mat3 O = mat3(vec3(1.60475, -0.10208, -0.00327), vec3(-0.53108, 1.10813, -0.07276), vec3(-0.07367, -0.00605, 1.07602));
      c *= expo / 0.6; return clamp(O * RRT(I * c), 0.0, 1.0); }
    vec3 srgb(vec3 c){ return mix(c * 12.92, pow(c, vec3(0.41666)) * 1.055 - 0.055, step(0.0031308, c)); }
    void main(){ vec3 c = vec3(0.0);
      c += texture2D(tCol, vUv + paso * vec2(-1.0, -1.0)).rgb; c += texture2D(tCol, vUv + paso * vec2(1.0, -1.0)).rgb;
      c += texture2D(tCol, vUv + paso * vec2(-1.0, 1.0)).rgb; c += texture2D(tCol, vUv + paso * vec2(1.0, 1.0)).rgb;
      vec3 d = srgb(aces(c * 0.25)) * 0.75; gl_FragColor = vec4(clamp((d - 0.5) * 2.2 + 0.5, 0.0, 1.0), 1.0); }`);
  // 3) Desenfoque gaussiano separable (σ = 7 px en 270×480, igual que blur(7px))
  const uG = { tCol: { value: B1.texture }, dir: { value: new THREE.Vector2() } };
  const mGau = mat(uG, `uniform sampler2D tCol; uniform vec2 dir; varying vec2 vUv;
    void main(){ vec3 acc = texture2D(tCol, vUv).rgb; float w = 1.0;
      for (int i = 1; i <= 21; i++) { float fi = float(i); float g = exp(-fi * fi / 98.0); acc += (texture2D(tCol, vUv + dir * fi).rgb + texture2D(tCol, vUv - dir * fi).rgb) * g; w += 2.0 * g; }
      gl_FragColor = vec4(acc / w, 1.0); }`);
  // 4) Mezcla final: nítido o borroso según la profundidad a resolución completa, tono de cine y bloom en modo «screen»
  const uF = Object.assign(comunes(), { tCol: { value: ESCENA.texture }, tBor: { value: MEDIA.texture }, tBlo: { value: B1.texture }, conDof: { value: 1 }, bloom: { value: 0 } });
  const mFin = mat(uF, `${PROF} uniform sampler2D tCol, tBor, tBlo; uniform float conDof, bloom; varying vec2 vUv;
    void main(){ vec3 c = texture2D(tCol, vUv).rgb;
      if (conDof > 0.5) { float k = smoothstep(0.35, 2.2, coc(prof(vUv))); c = mix(c, texture2D(tBor, vUv).rgb, k); }
      gl_FragColor = vec4(c, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
      vec3 b = texture2D(tBlo, vUv).rgb * bloom; gl_FragColor.rgb = 1.0 - (1.0 - gl_FragColor.rgb) * (1.0 - b); }`);
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2)); quad.frustumCulled = false;
  const QS = new THREE.Scene(); QS.add(quad); const QC = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const pasada = (m, destino) => { quad.material = m; REN.setRenderTarget(destino); REN.render(QS, QC); };
  return {
    // dof: fuerza del desenfoque (0 = sin desenfoque), bloom: opacidad del brillo (0..1)
    render(ESC, CAM, foco, dof, bloom) {
      REN.setRenderTarget(ESCENA); REN.render(ESC, CAM);
      for (const u of [uD, uF]) { u.near.value = CAM.near; u.far.value = CAM.far; u.foco.value = foco; u.fuerza.value = dof; }
      uF.conDof.value = dof > 0 ? 1 : 0; uF.bloom.value = bloom; uB.expo.value = REN.toneMappingExposure;
      if (dof > 0) pasada(mDof, MEDIA);
      if (bloom > 0) {
        uB.tCol.value = dof > 0 ? MEDIA.texture : ESCENA.texture; pasada(mBri, B1);
        uG.tCol.value = B1.texture; uG.dir.value.set(1 / 270, 0); pasada(mGau, B2);
        uG.tCol.value = B2.texture; uG.dir.value.set(0, 1 / 480); pasada(mGau, B1);
      }
      pasada(mFin, null);
    },
  };
}
