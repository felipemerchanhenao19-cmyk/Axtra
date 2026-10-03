/* Apex Play · el orbe de voz (motor económico de Axtra).
 *
 * El teléfono escucha y, cuando el cliente termina de hablar, manda ese pedacito de audio a la puerta.
 * Axtra lo entiende (Groq Whisper), piensa (Groq) y responde con voz (Google). Las frases fijas
 * (saludo, «Muy buena elección», despedida…) ya están grabadas: suenan al instante y no cuestan.
 * Nada de lo que dice el orbe se muestra escrito: solo se escucha.
 *
 * Uso en el menú de cualquier restaurante:
 *   <script src="https://api.axtra.chat/web/apex-voz.js"></script>
 *   const orbe = new ApexVoz({ api: "https://api.axtra.chat", restaurante: "demo", mesa: "1" });
 *   orbe.onestado = (e) => ...;   // "conectando" | "escuchando" | "oyendo" | "pensando" | "hablando" | "dormido" | "apagado"
 *   orbe.onnivel = (n) => ...;    // 0..1 para animar el orbe (voz del cliente o del orbe)
 *   orbe.onpedido = (p) => ...;   // {platos, total, total_numero} cuando cambia el pedido
 *   orbe.onsinvoz = () => ...;    // falló la voz o se acabó el saldo del mes: mostrar «Llamar al mesero»
 *   orbe.onerror = (msg) => ...;
 *   botonComenzar.onclick = () => orbe.iniciar();     // debe ser un toque (permiso de audio y micrófono)
 *   botonPedir.onclick = () => orbe.pedirPlato("ajiaco");
 *   botonPedirTodo.onclick = () => orbe.pedirTodo();
 *   botonMesero.onclick = () => orbe.llamarMesero();
 */
(function () {
  "use strict";
  const CLAVE = (r, m) => `apex:${r}:${m}`;
  const TIPO = ["audio/webm;codecs=opus", "audio/ogg;codecs=opus", "audio/mp4", "audio/webm"]
    .find((t) => window.MediaRecorder && MediaRecorder.isTypeSupported(t)) || "";
  const espera = (ms) => new Promise((r) => setTimeout(r, ms));

  class ApexVoz {
    constructor({ api, restaurante, mesa }) {
      Object.assign(this, { api: api.replace(/\/$/, ""), restaurante, mesa });
      this.estado = "apagado"; this.frases = {}; this.ocupado = false; this.despedida = false;
      for (const k of ["onestado", "onnivel", "onerror", "onpedido", "onsinvoz"]) this[k] = () => {};
    }

    _estado(e) { if (e !== this.estado) { this.estado = e; this.onestado(e); } }

    async _post(ruta, cuerpo, extra = {}) {
      const r = await fetch(this.api + ruta, { method: "POST", ...extra,
        headers: { "Content-Type": "application/json", ...(extra.headers || {}) },
        body: extra.body !== undefined ? extra.body : JSON.stringify(cuerpo) });
      const datos = await r.json().catch(() => ({}));
      if (!r.ok) throw Object.assign(new Error(datos.error || `error ${r.status}`), { status: r.status });
      return datos;
    }
    _cred() { return { sesion: this.s.sesion, secreto: this.s.secreto }; }

    async _sesion() {
      let anterior = null;
      try { anterior = JSON.parse(sessionStorage.getItem(CLAVE(this.restaurante, this.mesa)) || "null"); } catch {}
      this.s = await this._post("/v1/sesion", { restaurante: this.restaurante, mesa: this.mesa, anterior });
      try { sessionStorage.setItem(CLAVE(this.restaurante, this.mesa), JSON.stringify(this._cred())); } catch {}
      if (this.s.sin_voz) this.onsinvoz();
    }

    /* 1. «Toque para comenzar»: sesión, micrófono, frases grabadas y saludo. */
    async iniciar() {
      if (this.mic) { if (this.estado === "dormido") this._escuchar(); return; }
      this._estado("conectando");
      try {
        // El audio se desbloquea dentro del toque (Android/iPhone lo exigen)
        this.ctx = new (window.AudioContext || window.webkitAudioContext)(); this.ctx.resume();
        this.altavoz = new Audio(); this.altavoz.playsInline = true;
        await this._sesion();
        this.mic = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 } });
        this.anMic = this.ctx.createAnalyser(); this.anMic.fftSize = 1024;
        this.ctx.createMediaStreamSource(this.mic).connect(this.anMic);
        this.anVoz = this.ctx.createAnalyser(); this.anVoz.fftSize = 512;
        const fuente = this.ctx.createMediaElementSource(this.altavoz);
        fuente.connect(this.anVoz); this.anVoz.connect(this.ctx.destination);
        this._precargar();
        this.vigia = setInterval(() => this._vigilar(), 60);
        await this._decir({ frase: this.s.frases.saludo });
        this._escuchar();
      } catch (e) {
        this.onerror(e.status === 403 ? "La mesa está cerrada. Pida al mesero que la abra."
                   : e.status === 409 ? "Ya hay una conversación activa en esta mesa."
                   : e.name === "NotAllowedError" ? "Permita el micrófono para hablar con el orbe." : "No pude iniciar el orbe: " + e.message);
        this.terminar("error al iniciar");
      }
    }

    /* Descarga una vez las frases fijas: después suenan sin esperar. */
    _precargar() {
      for (const url of Object.values(this.s.frases)) {
        if (this.frases[url]) continue;
        this.frases[url] = fetch(this.api + url).then((r) => r.ok ? r.blob() : null)
          .then((b) => b && URL.createObjectURL(b)).catch(() => null);
      }
    }

    /* Reproduce lo que manda la puerta: una frase grabada (URL) o un audio nuevo (base64). */
    async _decir(res) {
      let url = null, temporal = false;
      if (res.frase) url = await (this.frases[res.frase] || (this.frases[res.frase] = fetch(this.api + res.frase)
        .then((r) => r.ok ? r.blob() : null).then((b) => b && URL.createObjectURL(b)).catch(() => null)));
      else if (res.audio) { url = URL.createObjectURL(new Blob([Uint8Array.from(atob(res.audio), (c) => c.charCodeAt(0))], { type: "audio/mpeg" })); temporal = true; }
      if (!url) { if (res.sin_voz) this.onsinvoz(); return; }
      this._estado("hablando");
      await new Promise((listo) => {
        this.alTerminar = listo;
        this.altavoz.onended = this.altavoz.onerror = () => listo();
        this.altavoz.src = url; this.altavoz.play().catch(() => listo());
      });
      this.alTerminar = null;
      if (temporal) URL.revokeObjectURL(url);
      if (res.sin_voz) this.onsinvoz();
    }

    _callar() { if (this.altavoz) { this.altavoz.pause(); if (this.alTerminar) this.alTerminar(); } }

    _escuchar() {
      if (!this.mic) return;
      this.ultimaVoz = Date.now(); this.voz = 0; this._estado("escuchando");
    }

    _nivel(an) {
      const d = new Float32Array(an.fftSize); an.getFloatTimeDomainData(d);
      let s = 0; for (const v of d) s += v * v; return Math.sqrt(s / d.length);
    }

    /* Cada 60 ms: ¿el cliente empezó o terminó de hablar? ¿interrumpe al orbe? */
    _vigilar() {
      if (!this.mic) return;
      const rms = this._nivel(this.anMic), ahora = Date.now();
      if (this.base === undefined) { this.base = 0.008; this.medidas = 0; }
      if (this.estado === "escuchando" && rms < this.base * 2.5) {           // aprende el ruido del lugar
        this.base = this.base * 0.95 + Math.max(0.004, rms) * 0.05;
      }
      const umbral = Math.max(0.015, this.base * 3);
      this.onnivel(this.estado === "hablando" ? Math.min(1, this._nivel(this.anVoz) * 6) : Math.min(1, rms * 8));

      if (this.estado === "escuchando") {
        this.voz = rms > umbral ? this.voz + 60 : 0;
        if (this.voz >= 120) return this._grabar();
        const quieto = ahora - this.ultimaVoz;
        if (this.despedida && quieto > 10000) return this.terminar("pedido enviado");   // 4. se apaga solo
        if (!this.despedida && quieto > 45000) { this._estado("dormido"); }              // toque el orbe para seguir
      } else if (this.estado === "oyendo") {
        if (rms > umbral) this.ultimaVoz = ahora;
        if (ahora - this.ultimaVoz > 850 || ahora - this.inicioGrab > 15000) this._enviar();
      } else if (this.estado === "hablando") {                                          // interrumpir al orbe
        this.voz = rms > umbral * 2.5 ? this.voz + 60 : 0;
        if (this.voz >= 300) { this._callar(); this._grabar(); }
      }
    }

    _grabar() {
      if (!window.MediaRecorder) return;
      this.trozos = []; this.inicioGrab = this.ultimaVoz = Date.now(); this.despedida = false;
      this.rec = new MediaRecorder(this.mic, TIPO ? { mimeType: TIPO, audioBitsPerSecond: 32000 } : undefined);
      this.rec.ondataavailable = (e) => e.data.size && this.trozos.push(e.data);
      this.rec.start(200);
      this._estado("oyendo");
    }

    async _enviar() {
      const rec = this.rec; this.rec = null;
      this._estado("pensando");
      await new Promise((ok) => { rec.onstop = ok; rec.stop(); });
      const audio = new Blob(this.trozos, { type: rec.mimeType || TIPO });
      if (audio.size < 2500) return this._escuchar();                    // fue un ruido corto
      await this._turno(() => fetch(this.api + "/v1/turno", { method: "POST", body: audio,
        headers: { "Content-Type": audio.type || "application/octet-stream", "X-Apex-Sesion": this.s.sesion, "X-Apex-Secreto": this.s.secreto } })
        .then(async (r) => { const d = await r.json().catch(() => ({})); if (!r.ok) throw Object.assign(new Error(d.error || r.status), { status: r.status }); return d; }));
    }

    /* Una vuelta: pide la respuesta, la dice y vuelve a escuchar. Si la sesión venció, la renueva. */
    async _turno(pedir) {
      if (this.ocupado) return; this.ocupado = true;
      try {
        let res;
        try { res = await pedir(); }
        catch (e) { if (e.status !== 410 && e.status !== 401) throw e; await this._sesion(); res = await pedir(); }
        if (res.pedido) this.onpedido(res.pedido);
        await this._decir(res);
        if (res.despedida) this.despedida = true;
      } catch (e) {
        if (e.status === 409) this.onerror(e.message);
        else this.onsinvoz();                                           // sin red o sin servidor: plan de respaldo
      } finally {
        this.ocupado = false;
        if (this.mic && this.estado !== "apagado") this._escuchar();
      }
    }

    async _accion(tipo, extra = {}) {
      if (!this.mic) await this.iniciar();
      if (!this.s) return;
      this._callar();
      this._estado("pensando");
      await this._turno(() => this._post("/v1/accion", { ...this._cred(), tipo, ...extra }));
    }

    /* 2. Botón «Pedir» de un plato → «Muy buena elección». */
    pedirPlato(platoId, cantidad = 1) { return this._accion("pedir", { plato_id: platoId, cantidad }); }
    /* 3. «Pedir todo lo seleccionado» → repite el pedido y pide confirmación por voz. */
    pedirTodo() { return this._accion("pedir_todo"); }
    /* Respaldo: siempre se puede llamar a un humano, aunque la voz o el micrófono no funcionen. */
    async llamarMesero() {
      if (this.mic) return this._accion("mesero");
      if (!this.s) await this._sesion();
      await this._post("/v1/accion", { ...this._cred(), tipo: "mesero" });
      this.onerror("Listo: un mesero va en camino.");
    }

    /* 5. Se apaga y libera la mesa. */
    terminar(motivo = "terminó") {
      clearInterval(this.vigia); this._callar();
      if (this.rec && this.rec.state !== "inactive") this.rec.stop();
      if (this.mic) this.mic.getTracks().forEach((t) => t.stop());
      if (this.ctx) this.ctx.close().catch(() => {});
      if (this.s) {
        const cuerpo = JSON.stringify({ ...this._cred(), motivo });
        try { navigator.sendBeacon(this.api + "/v1/sesion/fin", new Blob([cuerpo], { type: "text/plain" })); } catch {}
        try { sessionStorage.removeItem(CLAVE(this.restaurante, this.mesa)); } catch {}
      }
      Object.assign(this, { s: null, mic: null, ctx: null, rec: null, despedida: false, ocupado: false, base: undefined });
      this.onnivel(0); this._estado("apagado");
    }
  }

  window.ApexVoz = ApexVoz;
})();
