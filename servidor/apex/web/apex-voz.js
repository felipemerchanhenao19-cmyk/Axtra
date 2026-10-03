/* Apex Play · voz del orbe con OpenAI Realtime (WebRTC, voz a voz).
 *
 * Uso en el menú de cualquier restaurante:
 *   <script src="https://api.axtra.chat/web/apex-voz.js"></script>
 *   const orbe = new ApexVoz({ api: "https://api.axtra.chat", restaurante: "demo", mesa: "1" });
 *   orbe.onestado = (e) => ...;          // "conectando" | "escuchando" | "pensando" | "hablando" | "apagado"
 *   orbe.onnivel = (n) => ...;           // 0..1, volumen de la voz del orbe (para animar)
 *   orbe.onerror = (msg) => ...;
 *   botonComenzar.onclick = () => orbe.iniciar();        // debe ser un toque (permiso de audio y micrófono)
 *   botonPedir.onclick = () => orbe.pedirPlato("ajiaco");
 *   botonPedirTodo.onclick = () => orbe.pedirTodo();
 *
 * Nada de lo que dice el orbe se muestra escrito: solo se escucha.
 * La API key de OpenAI nunca llega al navegador: el servidor entrega un token efímero de 60 s.
 */
(function () {
  "use strict";
  const CLAVE = (r, m) => `apex:${r}:${m}`;

  class ApexVoz {
    constructor({ api, restaurante, mesa }) {
      Object.assign(this, { api: api.replace(/\/$/, ""), restaurante, mesa });
      this.estado = "apagado"; this.uso = {}; this.cola = []; this.respondiendo = false;
      this.pendientes = []; this.despedida = false; this.timerSilencio = null;
      this.onestado = () => {}; this.onnivel = () => {}; this.onerror = () => {}; this.onpedido = () => {};
    }

    _estado(e) { if (e !== this.estado) { this.estado = e; this.onestado(e); } }

    async _post(ruta, cuerpo) {
      const r = await fetch(this.api + ruta, { method: "POST", headers: { "Content-Type": "application/json" },
                                               body: JSON.stringify(cuerpo) });
      const datos = await r.json().catch(() => ({}));
      if (!r.ok) throw Object.assign(new Error(datos.error || `error ${r.status}`), { status: r.status });
      return datos;
    }
    _cred() { return { sesion: this.s.sesion, secreto: this.s.secreto }; }

    /* 1. Toque para comenzar: pide sesión, abre el micrófono y conecta con OpenAI por WebRTC. */
    async iniciar() {
      if (this.pc) return;
      this._estado("conectando");
      try {
        let anterior = null;
        try { anterior = JSON.parse(sessionStorage.getItem(CLAVE(this.restaurante, this.mesa)) || "null"); } catch {}
        this.s = await this._post("/v1/sesion", { restaurante: this.restaurante, mesa: this.mesa, anterior });
        try { sessionStorage.setItem(CLAVE(this.restaurante, this.mesa), JSON.stringify(this._cred())); } catch {}
        this.mic = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } });

        const pc = this.pc = new RTCPeerConnection();
        this.audio = new Audio(); this.audio.autoplay = true; this.audio.playsInline = true;
        pc.ontrack = (e) => { this.audio.srcObject = e.streams[0]; this._medir(e.streams[0]); };
        pc.addTrack(this.mic.getTracks()[0], this.mic);
        pc.onconnectionstatechange = () => { if (["failed", "closed"].includes(pc.connectionState)) this.terminar("conexión perdida"); };
        this.dc = pc.createDataChannel("oai-events");
        this.dc.onmessage = (m) => { try { this._evento(JSON.parse(m.data)); } catch (e) { console.warn(e); } };
        const abierto = new Promise((ok) => (this.dc.onopen = ok));

        const oferta = await pc.createOffer(); await pc.setLocalDescription(oferta);
        const r = await fetch("https://api.openai.com/v1/realtime/calls", {
          method: "POST", body: oferta.sdp, headers: { Authorization: `Bearer ${this.s.token}`, "Content-Type": "application/sdp" } });
        if (!r.ok) throw new Error(`OpenAI no aceptó la conexión (${r.status})`);
        const callId = (r.headers.get("Location") || "").split("/").pop();
        await pc.setRemoteDescription({ type: "answer", sdp: await r.text() });
        if (callId) this._post("/v1/sesion/llamada", { ...this._cred(), call_id: callId }).catch(() => {});
        await abierto;
        this.inicio = Date.now();
        this.limite = setTimeout(() => this.terminar("tope de tiempo"), this.s.max_segundos * 1000);
        this._estado("escuchando");
        this.decir(this.s.frases.saludo);
      } catch (e) {
        this.onerror(e.status === 403 ? "La mesa está cerrada. Pida al mesero que la abra."
                   : e.status === 409 ? "Ya hay una conversación activa en esta mesa."
                   : e.status === 429 ? "El orbe no está disponible ahora; un mesero lo atenderá."
                   : (e.name === "NotAllowedError" ? "Permita el micrófono para hablar con el orbe." : e.message));
        this.terminar("error al iniciar");
      }
    }

    /* Volumen de la voz del orbe (para animarlo). */
    _medir(stream) {
      try {
        const ctx = this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        const an = ctx.createAnalyser(); an.fftSize = 512; ctx.createMediaStreamSource(stream).connect(an);
        const d = new Uint8Array(an.fftSize);
        const paso = () => { if (!this.pc) return; an.getByteTimeDomainData(d); let s = 0;
          for (const v of d) s += (v - 128) ** 2; this.onnivel(Math.min(1, Math.sqrt(s / d.length) / 40)); requestAnimationFrame(paso); };
        paso();
      } catch {}
    }

    _enviar(ev) { if (this.dc && this.dc.readyState === "open") this.dc.send(JSON.stringify(ev)); }

    /* Pide una respuesta; si el orbe está hablando, espera su turno. */
    _responder(response) {
      if (this.respondiendo) { this.cola.push(response); return; }
      this.respondiendo = true; this.ultima = response; this._enviar({ type: "response.create", response });
    }

    /* Frase fija del guion (saludo, «Muy buena elección», etc.). */
    decir(frase) {
      this._responder({ tool_choice: "none",
        instructions: `Di exactamente esta frase, sin agregar nada más: «${frase}»` });
    }

    _nota(texto) {     // acción hecha en la pantalla, para que el orbe la tenga en cuenta
      this._enviar({ type: "conversation.item.create",
        item: { type: "message", role: "system", content: [{ type: "input_text", text: texto }] } });
    }

    _herramienta(nombre, argumentos = {}) {
      return this._post("/v1/herramienta", { ...this._cred(), nombre, argumentos });
    }

    /* 2. Botón «Pedir» de un plato. */
    async pedirPlato(platoId, cantidad = 1) {
      if (!this.pc) await this.iniciar();
      const r = await this._herramienta("agregar_plato", { plato_id: platoId, cantidad });
      this.onpedido(r);
      if (!r.ok) { this.decir("Lo siento, ese plato no está disponible ahora."); return r; }
      this._nota(`El cliente tocó «Pedir» en: ${r.agregado}. Pedido actual: ${JSON.stringify(r.platos)}; total ${r.total}.`);
      this.decir(this.s.frases.eleccion);
      return r;
    }

    /* 3. Botón «Pedir todo lo seleccionado»: repite el pedido y pide confirmación por voz. */
    async pedirTodo() {
      if (!this.pc) await this.iniciar();
      const r = await this._herramienta("ver_pedido");
      if (!r.platos || !r.platos.length) { this.decir("Aún no ha seleccionado ningún plato. ¿Qué le provoca?"); return; }
      this._nota(`El cliente tocó «Pedir todo lo seleccionado». Pedido: ${JSON.stringify(r.platos)}; total ${r.total}.`);
      this._responder({ instructions: "Repite el pedido de forma breve (platos, cantidades y total) y pregunta si lo confirma. " +
        "Si el cliente dice que sí, usa confirmar_pedido." });
    }

    /* Eventos de OpenAI Realtime. */
    _evento(ev) {
      switch (ev.type) {
        case "input_audio_buffer.speech_started":
          clearTimeout(this.timerSilencio); this._estado("escuchando"); break;
        case "input_audio_buffer.speech_stopped": this._estado("pensando"); break;
        case "output_audio_buffer.started": this._estado("hablando"); break;
        case "output_audio_buffer.stopped":
          this._estado("escuchando");
          if (this.despedida) {      // 4. tras despedirse, escucha 10 s y si nadie habla, se apaga
            clearTimeout(this.timerSilencio);
            this.timerSilencio = setTimeout(() => this.terminar("pedido enviado"), 10000);
          }
          break;
        case "response.function_call_arguments.done":
          this.pendientes.push(this._ejecutar(ev.call_id, ev.name, ev.arguments)); break;
        case "response.done": this._finRespuesta(ev.response || {}); break;
        case "response.created": this.respondiendo = true; break;      // también las que el orbe inicia solo
        case "error":
          console.warn("Realtime:", ev.error);
          if (/active response/i.test(ev.error?.message || "") && this.ultima) { this.cola.unshift(this.ultima); this.respondiendo = true; }
          break;
      }
    }

    async _ejecutar(callId, nombre, args) {
      let salida;
      try { salida = await this._herramienta(nombre, args); }
      catch (e) { salida = { ok: false, error: e.message }; }
      if (nombre === "confirmar_pedido" && salida.ok) { this.despedida = true; this.onpedido({ ...salida, confirmado: true }); }
      else if (salida.platos) this.onpedido(salida);
      this._enviar({ type: "conversation.item.create",
        item: { type: "function_call_output", call_id: callId, output: JSON.stringify(salida) } });
    }

    async _finRespuesta(resp) {
      const u = resp.usage;
      if (u) {
        const i = u.input_token_details || {}, o = u.output_token_details || {}, c = i.cached_tokens_details || {};
        const suma = (k, v) => (this.uso[k] = (this.uso[k] || 0) + (v || 0));
        suma("audio_in", (i.audio_tokens || 0) - (c.audio_tokens || 0)); suma("audio_in_cache", c.audio_tokens);
        suma("texto_in", (i.text_tokens || 0) - (c.text_tokens || 0)); suma("texto_in_cache", c.text_tokens);
        suma("audio_out", o.audio_tokens); suma("texto_out", o.text_tokens);
      }
      this.respondiendo = false;
      if (this.pendientes.length) {       // hubo herramientas: el orbe debe responder con su resultado
        const p = this.pendientes; this.pendientes = []; await Promise.all(p);
        return this._responder({});
      }
      if (this.cola.length) this._responder(this.cola.shift());
    }

    /* 5. Se apaga: cuelga y reporta el uso (para controlar el gasto por restaurante). */
    async terminar(motivo = "terminó") {
      clearTimeout(this.timerSilencio); clearTimeout(this.limite);
      const pc = this.pc; this.pc = null;
      if (pc) { try { pc.close(); } catch {} }
      if (this.mic) this.mic.getTracks().forEach((t) => t.stop());
      if (this.ctx) this.ctx.close().catch(() => {});
      if (this.s) {
        const cuerpo = JSON.stringify({ ...this._cred(), uso: this.uso });
        try { navigator.sendBeacon ? navigator.sendBeacon(this.api + "/v1/sesion/fin", new Blob([cuerpo], { type: "text/plain" }))
                                   : await fetch(this.api + "/v1/sesion/fin", { method: "POST", body: cuerpo, keepalive: true }); } catch {}
        try { sessionStorage.removeItem(CLAVE(this.restaurante, this.mesa)); } catch {}
        this.s = null;
      }
      Object.assign(this, { dc: null, respondiendo: false, cola: [], pendientes: [], despedida: false, uso: {} });
      this.onnivel(0); this._estado("apagado");
    }
  }

  window.ApexVoz = ApexVoz;
})();
