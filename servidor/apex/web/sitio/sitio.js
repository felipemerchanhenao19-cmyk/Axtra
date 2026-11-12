/* Sitio de Apex Corporation: idiomas, recorrido guiado con voz, orbe de Saturno y «Mire Apex en su restaurante». */
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const WA = "573107897960";
  const guardar = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };
  const leer = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };

  /* ================= textos ================= */
  const DIC = {
    en: {
      nav1: "What we do", nav2: "Products", nav3: "Your restaurant", nav4: "How we work", nav5: "Join us", hablemos: "Let's talk",
      h_ceja: "Software and artificial intelligence · Food industry",
      h_titulo: "Artificial intelligence that <em>serves, sells</em> and works in your restaurant.",
      h_lead: "Virtual waiters and commission-free delivery for restaurants across Colombia and other countries. No need to look for anything: tap the orb and our assistant will show you everything, in your language.",
      h_boton: "▶&nbsp; Tap to start the tour", h_wa: "Message us on WhatsApp",
      d1: "<b>2</b>products powered by<br>artificial intelligence", d2: "<b>6</b>languages the<br>assistant speaks", d3: "<b>5 to 7</b>business days<br>to install",
      asistente: "Apex assistant", b_hola: "Hi! How are you? I'm the Apex Corporation assistant. Tap the orb and I'll show you what we do for restaurants.", b_iniciar: "▶ Start",
      q_ceja: "What we do", q_titulo: "Technology you can feel at the table, in the kitchen and at the register.",
      q_texto: "We design artificial intelligence tools for real restaurants: easy for guests, useful for the team and profitable for the owner.",
      p1_t: "AI-powered service", p1_x: "A virtual waiter that greets, recommends, takes the order by voice and sends it to the kitchen. In each guest's language.",
      p2_t: "Direct sales", p2_x: "Your own delivery channel, with no commissions to apps. The customers and the profits are yours.",
      p3_t: "Wherever you are", p3_x: "Remote installation anywhere in Colombia and in other countries, with support from Monday to Sunday.",
      pr_ceja: "Products", pr_titulo: "Two products. One assistant.", pr_texto: "The Apex orb serves at the table and on deliveries: it listens, understands and answers with a natural voice.",
      pl_t: "Your restaurant's virtual waiter.", pl_x: "The guest scans the QR code on the table and the orb takes care of them: it shows the menu, makes recommendations and takes the order.",
      pl_1: "<span><b>A QR code on every table</b>, no app to download.</span>", pl_2: "<span><b>Dishes in 3D and augmented reality</b>: guests see the dish before ordering.</span>",
      pl_3: "<span><b>Voice orders</b> that go straight to the kitchen.</span>", pl_4: "<span><b>Six languages</b> for tourists and visitors.</span>", pl_demo: "Try Apex Play →",
      pl_e1: "Table 4 · Order sent<small>2 dishes · on its way to the kitchen</small>", pl_e2: "Español · Português<small>the orb switches languages</small>",
      do_t: "Your own delivery channel, with no commissions.", do_x: "Your customers order from your link or your WhatsApp, and the assistant takes care of the rest.",
      do_1: "<span><b>Zero commissions</b> per order: the margin stays in your restaurant.</span>", do_2: "<span><b>Automatic payment verification</b> with Nequi.</span>",
      do_3: "<span><b>Live order tracking</b> for your customer.</span>", do_4: "<span><b>Your own customer base</b>, so you can sell to them again.</span>", do_demo: "Try Apex Domicilios →",
      do_e1: "Nequi payment verified ✓<small>in seconds</small>", do_e2: "Your order is on its way<small>live tracking</small>",
      s_ceja: "See Apex in your restaurant", s_titulo: "Type your restaurant's name and watch it in action.", s_texto: "In seconds we put together a video with your name, your dishes and your colors, narrated by our assistant. Watch it right here and download it.",
      f_titulo: "Your restaurant", f_sub: "It takes less than a minute.", f_nombre: "Restaurant name", f_ciudad: "City", f_tipo: "Type of food", f_platos: "Three of your dishes",
      f_color: "Your brand color", f_logo: "＋ Upload logo", f_boton: "▶&nbsp; See my restaurant with Apex", f_nota: "We only use the name, city and first dish to narrate your video. We don't store your details.",
      f_tipo_ph: "Grill", f_p1: "House platter", f_p2: "400 g steak", f_p3: "Coconut lemonade",
      v_mesa: "TABLE 4 · APEX PLAY", v_bienvenido: "Welcome to", v_cocina: "● NEW ORDER · KITCHEN", v_fin_ceja: "This is how Apex would look", v_fin_texto: "We install it remotely in 5 to 7 business days.",
      v_fin_wa: "I want it for my restaurant", v_fin_otra: "↺ Watch again", v_ver: "▶ Watch the video", v_preparando: "Preparing your video…", v_bajar: "⬇ Download video",
      t_ceja: "How we work", t_titulo: "From the first conversation to your restaurant up and running.",
      t1: "We talk", t1x: "An in-person or online meeting to get to know your restaurant and what it needs.", t2: "We set up", t2x: "We load your menu, photos, prices and your assistant's voice.",
      t3: "We install", t3x: "Remote installation in 5 to 7 business days, with QR codes ready for your tables.", t4: "We support you", t4x: "Support from Monday to Sunday, 6:00 a.m. to 11:00 p.m.",
      r_ceja: "Our journey", r_titulo: "A Colombian company, built for the world.", r_texto: "Apex Corporation brings artificial intelligence to restaurants across Colombia and other countries, with a simple idea: every restaurant deserves the technology of the big chains.",
      r1: "<small>The beginning</small><h3>Made in Colombia</h3><p>We started building artificial intelligence for restaurant service.</p>",
      r2: "<small>First product</small><h3>Apex Play</h3><p>The orb arrives at the tables: 3D menu, voice orders and six languages.</p>",
      r3: "<small>Second product</small><h3>Apex Domicilios</h3><p>Your own delivery channel, commission-free and with verified payments.</p>",
      r4: "<small>Today</small><h3>All of Colombia and other countries</h3><p>Remote installation and a sales team serving restaurants in and outside Colombia.</p>",
      u_ceja: "Join us", u_titulo: "We're looking for sales closers across Colombia.", u_texto: "Remote, commission-based work closing sales of software and artificial intelligence for the food industry.", u_boton: "Send your résumé",
      c_ceja: "Contact", c_titulo: "Shall we talk about your restaurant?", c_texto: "We serve restaurants across Colombia and in other countries. Book an in-person or online meeting and we'll show you Apex running with your own menu.",
      c_wa: "Message us on WhatsApp", c_reunion: "Book a meeting", c_correo: "Email",
      pie_servicio: "Service across Colombia and other countries", pie_priv: "Privacy policy", pie_term: "Terms and conditions", seguir: "▶ Resume",
    },
    pt: {
      nav1: "O que fazemos", nav2: "Produtos", nav3: "Seu restaurante", nav4: "Como trabalhamos", nav5: "Trabalhe conosco", hablemos: "Vamos conversar",
      h_ceja: "Software e inteligência artificial · Setor gastronômico",
      h_titulo: "Inteligência artificial que <em>atende, vende</em> e trabalha no seu restaurante.",
      h_lead: "Garçons virtuais e delivery sem comissões para restaurantes de toda a Colômbia e de outros países. Não precisa procurar nada: toque no orbe e o nosso assistente mostra tudo, no seu idioma.",
      h_boton: "▶&nbsp; Toque para começar o tour", h_wa: "Fale conosco no WhatsApp",
      d1: "<b>2</b>produtos com<br>inteligência artificial", d2: "<b>6</b>idiomas que o<br>assistente fala", d3: "<b>5 a 7</b>dias úteis<br>de instalação",
      asistente: "Assistente da Apex", b_hola: "Olá! Tudo bem? Sou o assistente da Apex Corporation. Toque no orbe e eu mostro o que fazemos pelos restaurantes.", b_iniciar: "▶ Começar",
      q_ceja: "O que fazemos", q_titulo: "Tecnologia que se nota na mesa, na cozinha e no caixa.",
      q_texto: "Criamos ferramentas de inteligência artificial pensadas para restaurantes reais: fáceis para o cliente, úteis para a equipe e rentáveis para o dono.",
      p1_t: "Atendimento com IA", p1_x: "Um garçom virtual que cumprimenta, recomenda, anota o pedido por voz e o envia para a cozinha. No idioma de cada cliente.",
      p2_t: "Vendas diretas", p2_x: "O seu próprio canal de delivery, sem pagar comissões a aplicativos. Os clientes e os lucros são seus.",
      p3_t: "Onde você estiver", p3_x: "Instalação remota em toda a Colômbia e em outros países, com acompanhamento de segunda a domingo.",
      pr_ceja: "Produtos", pr_titulo: "Dois produtos. Um só assistente.", pr_texto: "O orbe da Apex atende na mesa e no delivery: escuta, entende e responde com voz natural.",
      pl_t: "O garçom virtual do seu restaurante.", pl_x: "O cliente escaneia o QR code da mesa e o orbe o atende: mostra o cardápio, faz recomendações e anota o pedido.",
      pl_1: "<span><b>QR code em cada mesa</b>, sem baixar aplicativos.</span>", pl_2: "<span><b>Pratos em 3D e realidade aumentada</b>: o cliente vê o prato antes de pedir.</span>",
      pl_3: "<span><b>Pedidos por voz</b> que chegam direto na cozinha.</span>", pl_4: "<span><b>Seis idiomas</b> para turistas e visitantes.</span>", pl_demo: "Experimentar o Apex Play →",
      pl_e1: "Mesa 4 · Pedido enviado<small>2 pratos · indo para a cozinha</small>", pl_e2: "English · Español<small>o orbe muda de idioma</small>",
      do_t: "O seu próprio canal de delivery, sem comissões.", do_x: "Os seus clientes pedem pelo seu link ou pelo seu WhatsApp, e o assistente cuida do resto.",
      do_1: "<span><b>Zero comissões</b> por pedido: a margem fica no seu restaurante.</span>", do_2: "<span><b>Verificação automática de pagamentos</b> pelo Nequi.</span>",
      do_3: "<span><b>Acompanhamento ao vivo</b> do pedido para o cliente.</span>", do_4: "<span><b>A sua base de clientes</b>, para vender de novo.</span>", do_demo: "Experimentar o Apex Domicilios →",
      do_e1: "Pagamento Nequi verificado ✓<small>em segundos</small>", do_e2: "O seu pedido está a caminho<small>acompanhamento ao vivo</small>",
      s_ceja: "Veja a Apex no seu restaurante", s_titulo: "Escreva o nome do seu restaurante e veja funcionando.", s_texto: "Em segundos montamos um vídeo com o seu nome, os seus pratos e as suas cores, narrado pelo nosso assistente. Assista aqui mesmo e baixe.",
      f_titulo: "O seu restaurante", f_sub: "Leva menos de um minuto.", f_nombre: "Nome do restaurante", f_ciudad: "Cidade", f_tipo: "Tipo de comida", f_platos: "Três dos seus pratos",
      f_color: "Cor da sua marca", f_logo: "＋ Enviar logo", f_boton: "▶&nbsp; Ver meu restaurante com a Apex", f_nota: "Usamos o nome, a cidade e o primeiro prato só para narrar o seu vídeo. Não guardamos os seus dados.",
      f_tipo_ph: "Churrascaria", f_p1: "Tábua da casa", f_p2: "Picanha 400 g", f_p3: "Limonada de coco",
      v_mesa: "MESA 4 · APEX PLAY", v_bienvenido: "Bem-vindo ao", v_cocina: "● NOVO PEDIDO · COZINHA", v_fin_ceja: "Assim ficaria a Apex", v_fin_texto: "Instalamos de forma remota em 5 a 7 dias úteis.",
      v_fin_wa: "Quero para o meu restaurante", v_fin_otra: "↺ Ver de novo", v_ver: "▶ Ver o vídeo", v_preparando: "Preparando o seu vídeo…", v_bajar: "⬇ Baixar vídeo",
      t_ceja: "Como trabalhamos", t_titulo: "Da primeira conversa ao seu restaurante funcionando.",
      t1: "Conversamos", t1x: "Uma reunião presencial ou online para conhecer o seu restaurante e o que ele precisa.", t2: "Configuramos", t2x: "Carregamos o seu cardápio, as suas fotos, os seus preços e a voz do seu assistente.",
      t3: "Instalamos", t3x: "Instalação remota em 5 a 7 dias úteis, com os QR codes prontos para as suas mesas.", t4: "Acompanhamos", t4x: "Suporte de segunda a domingo, das 6h às 23h.",
      r_ceja: "A nossa trajetória", r_titulo: "Uma empresa colombiana, pensada para o mundo.", r_texto: "A Apex Corporation leva inteligência artificial a restaurantes de toda a Colômbia e de outros países, com uma ideia simples: que qualquer restaurante tenha a tecnologia das grandes redes.",
      r1: "<small>O começo</small><h3>Feito na Colômbia</h3><p>Começamos a construir inteligência artificial para o atendimento em restaurantes.</p>",
      r2: "<small>Primeiro produto</small><h3>Apex Play</h3><p>O orbe chega às mesas: cardápio em 3D, pedidos por voz e seis idiomas.</p>",
      r3: "<small>Segundo produto</small><h3>Apex Domicilios</h3><p>Um canal próprio de delivery, sem comissões e com pagamentos verificados.</p>",
      r4: "<small>Hoje</small><h3>Toda a Colômbia e outros países</h3><p>Instalação remota e uma equipe comercial que atende restaurantes dentro e fora da Colômbia.</p>",
      u_ceja: "Trabalhe conosco", u_titulo: "Procuramos closers de vendas em toda a Colômbia.", u_texto: "Trabalho remoto, por comissão, fechando vendas de software e inteligência artificial para o setor gastronômico.", u_boton: "Enviar currículo",
      c_ceja: "Contato", c_titulo: "Vamos falar sobre o seu restaurante?", c_texto: "Atendemos restaurantes em toda a Colômbia e em outros países. Agende uma reunião presencial ou online e mostramos a Apex funcionando com o seu próprio cardápio.",
      c_wa: "Falar no WhatsApp", c_reunion: "Agendar uma reunião", c_correo: "E-mail",
      pie_servicio: "Atendimento em toda a Colômbia e outros países", pie_priv: "Política de privacidade", pie_term: "Termos e condições", seguir: "▶ Continuar",
    },
  };
  const UI = {
    es: { caps: ["Bienvenida", "Qué hacemos", "Apex Play", "Apex Domicilios", "Su restaurante", "Cómo trabajamos", "Contacto"], pausar: "Pausar", seguir: "Seguir",
      fin: "¡Gracias por ver el recorrido! Si quiere, escríbanos por WhatsApp o pruebe Apex con el nombre de su restaurante.", lang: "es-CO",
      wa: { general: "Hola, Apex Corporation. Vi su página y quiero información para mi restaurante.", reunion: "Hola, Apex Corporation. Quiero agendar una reunión para conocer Apex.",
            sim: (d) => `Hola, Apex Corporation. Vi cómo se vería Apex en mi restaurante ${d.n}${d.c ? " (" + d.c + ")" : ""} y lo quiero.` },
      sim: { s1: (d) => `Esta es una mesa de ${d.n}${d.c ? ", en " + d.c : ""}.`, s2: (d) => `El cliente escanea el código QR y el asistente lo saluda: «Bienvenido a ${d.n}. ¿Qué le provoca hoy?»`,
             s3: (d) => `Le muestra la carta y le recomienda: «Le sugiero ${d.platos[0].nombre}, es la favorita de la casa».`, s4: () => "El cliente pide por voz, y el pedido llega directo a la cocina.",
             s5: (d) => `Así se vería Apex en ${d.n}.`, fin: (d) => `en ${d.n}`, mesa: "Mesa 4", total: "Total" } },
    en: { caps: ["Welcome", "What we do", "Apex Play", "Apex Domicilios", "Your restaurant", "How we work", "Contact"], pausar: "Pause", seguir: "Resume",
      fin: "Thanks for watching the tour! Message us on WhatsApp, or try Apex with your restaurant's name.", lang: "en-US",
      wa: { general: "Hi Apex Corporation, I saw your website and I'd like information for my restaurant.", reunion: "Hi Apex Corporation, I'd like to book a meeting to learn about Apex.",
            sim: (d) => `Hi Apex Corporation, I saw how Apex would look at my restaurant ${d.n}${d.c ? " (" + d.c + ")" : ""} and I want it.` },
      sim: { s1: (d) => `This is a table at ${d.n}${d.c ? ", in " + d.c : ""}.`, s2: (d) => `The guest scans the QR code and the assistant greets them: “Welcome to ${d.n}. What would you like today?”`,
             s3: (d) => `It shows the menu and makes a suggestion: “I recommend the ${d.platos[0].nombre}, it's the house favorite.”`, s4: () => "The guest orders by voice, and the order goes straight to the kitchen.",
             s5: (d) => `This is how Apex would look at ${d.n}.`, fin: (d) => `at ${d.n}`, mesa: "Table 4", total: "Total" } },
    pt: { caps: ["Boas-vindas", "O que fazemos", "Apex Play", "Apex Domicilios", "Seu restaurante", "Como trabalhamos", "Contato"], pausar: "Pausar", seguir: "Continuar",
      fin: "Obrigado por assistir ao tour! Fale conosco no WhatsApp ou experimente a Apex com o nome do seu restaurante.", lang: "pt-BR",
      wa: { general: "Olá, Apex Corporation. Vi o site de vocês e quero informações para o meu restaurante.", reunion: "Olá, Apex Corporation. Quero agendar uma reunião para conhecer a Apex.",
            sim: (d) => `Olá, Apex Corporation. Vi como a Apex ficaria no meu restaurante ${d.n}${d.c ? " (" + d.c + ")" : ""} e quero.` },
      sim: { s1: (d) => `Esta é uma mesa do ${d.n}${d.c ? ", em " + d.c : ""}.`, s2: (d) => `O cliente escaneia o QR code e o assistente o recebe: “Bem-vindo ao ${d.n}. O que vai querer hoje?”`,
             s3: (d) => `Mostra o cardápio e recomenda: “Sugiro ${d.platos[0].nombre}, é o favorito da casa.”`, s4: () => "O cliente pede por voz, e o pedido chega direto na cozinha.",
             s5: (d) => `Assim ficaria a Apex no ${d.n}.`, fin: (d) => `no ${d.n}`, mesa: "Mesa 4", total: "Total" } },
  };

  /* ================= idioma ================= */
  const ES = {}, ES_PH = {};
  $$("[data-i]").forEach((el) => { if (!(el.dataset.i in ES)) ES[el.dataset.i] = el.innerHTML; });
  $$("[data-ph]").forEach((el) => { ES_PH[el.dataset.ph] = el.placeholder; });
  const pedido = new URLSearchParams(location.search).get("idioma");
  const navegador = (navigator.language || "es").slice(0, 2);
  let idioma = [pedido, leer("apex_idioma"), navegador].find((l) => l && UI[l]) || "es";
  const T = () => UI[idioma];

  function aplicarIdioma(l) {
    idioma = UI[l] ? l : "es"; guardar("apex_idioma", idioma);
    document.documentElement.lang = idioma;
    $$("[data-i]").forEach((el) => { const v = idioma === "es" ? ES[el.dataset.i] : DIC[idioma][el.dataset.i]; if (v != null) el.innerHTML = v; });
    $$("[data-ph]").forEach((el) => { el.placeholder = idioma === "es" ? ES_PH[el.dataset.ph] : DIC[idioma][el.dataset.ph] || ES_PH[el.dataset.ph]; });
    $$(".idiomas button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === idioma)));
    pintarCapitulos(); enlacesWhatsApp(); pintarSim();
    if (R.activo) { mostrar(frases()[Math.min(R.frase, frases().length - 1)]?.txt || ""); if (!R.pausado) { cortar(); reproducirFrase(); } }
    else if (R.terminado) mostrar(T().fin);
  }
  $$(".idiomas button").forEach((b) => b.addEventListener("click", () => aplicarIdioma(b.dataset.lang)));

  function enlacesWhatsApp() {
    $$("[data-wa]").forEach((a) => { a.href = `https://wa.me/${WA}?text=${encodeURIComponent(T().wa[a.dataset.wa] || T().wa.general)}`; });
  }

  /* ================= recorrido guiado ================= */
  let guion = null;
  const cargado = fetch("/web/sitio/voz/guion.json").then((r) => r.json()).then((g) => { guion = g; pintarCapitulos(); }).catch(() => {});
  const audio = new Audio(); audio.preload = "auto";
  const R = { activo: false, pausado: false, terminado: false, cap: 0, frase: 0, silencio: false, cc: true, timer: 0, programado: 0, hablando: false };
  let nivel = 0;
  const frases = () => (guion ? guion[R.cap].frases[idioma] || guion[R.cap].frases.es : []);
  const SILENCIO = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA=";
  function desbloquearAudio() { if (!audio.src) { audio.src = SILENCIO; audio.play().catch(() => {}); } }   // iPhone: el audio solo arranca dentro del toque
  function nivelVoz() {
    if (!R.hablando || R.silencio) return R.hablando ? 0.25 : 0;
    const f = frases()[R.frase];
    if (f && f.env && !audio.paused) return (f.env[Math.min(f.env.length - 1, Math.floor(audio.currentTime * 25))] || 0) / 99;
    return 0.3 + 0.25 * Math.abs(Math.sin(performance.now() / 90));   // voz del navegador (respaldo)
  }

  function mostrar(txt) { $("#subtitulo-portada").textContent = txt; $("#subtitulo-dock").textContent = txt; }
  function cortar() { clearTimeout(R.timer); audio.onended = audio.onerror = null; audio.pause(); R.hablando = false; if ("speechSynthesis" in window) speechSynthesis.cancel(); }

  function pintarCapitulos() {
    const caja = $("#capitulos"); if (!caja) return;
    caja.innerHTML = T().caps.map((n, i) => `<button data-cap="${i}" class="${R.activo && i === R.cap ? "si" : ""} ${R.activo && i < R.cap ? "visto" : ""}">${n}</button>`).join("");
    $$("button", caja).forEach((b) => b.addEventListener("click", () => iniciar(+b.dataset.cap)));
  }
  function enfocar(sel) { $$(".enfoque").forEach((e) => e.classList.remove("enfoque")); const el = sel && $(sel); if (el) el.classList.add("enfoque"); }
  function irA(c, i) {
    R.programado = performance.now();
    if (i === 0) { window.scrollTo({ top: 0, behavior: reducido ? "auto" : "smooth" }); return; }
    const el = $(c.resalta) || $(c.seccion);
    el?.scrollIntoView({ behavior: reducido ? "auto" : "smooth", block: "center" });
  }

  function iniciar(cap = 0) {
    if (!guion) { desbloquearAudio(); mostrar("…"); cargado.then(() => { if (guion) iniciar(cap); else mostrar(T().fin); }); return; }
    if (video.estado === "reproduciendo") video.pausar();
    cortar(); Object.assign(R, { activo: true, pausado: false, terminado: false });
    document.body.classList.add("en-recorrido"); actualizarControles();
    reproducirCap(cap, true);   // la primera frase suena en el mismo toque (si no, el iPhone la bloquea)
  }
  function reproducirCap(i, ya = false) {
    R.cap = i; R.frase = 0; const c = guion[i];
    pintarCapitulos(); enfocar(c.resalta); irA(c, i); actualizarDock();
    if (ya) reproducirFrase(); else R.timer = setTimeout(reproducirFrase, reducido ? 150 : 950);
  }
  function reproducirFrase() {
    if (!R.activo || R.pausado) return;
    const f = frases()[R.frase]; if (!f) return avanzar();
    mostrar(f.txt); clearTimeout(R.timer);
    const respaldo = () => {   // si el audio falla: voz del navegador y, si no hay, solo subtítulos con el tiempo de la frase
      R.hablando = true;
      if ("speechSynthesis" in window && !R.silencio) {
        const u = new SpeechSynthesisUtterance(f.txt); u.lang = T().lang; u.rate = 1.03;
        u.onend = () => { R.hablando = false; R.timer = setTimeout(avanzar, 300); }; speechSynthesis.cancel(); speechSynthesis.speak(u);
        R.timer = setTimeout(() => { speechSynthesis.cancel(); avanzar(); }, f.dur * 1000 + 2500);
      } else R.timer = setTimeout(() => { R.hablando = false; avanzar(); }, f.dur * 1000 + 350);
    };
    audio.onended = () => { R.hablando = false; R.timer = setTimeout(avanzar, 320); };
    audio.onerror = () => { audio.onerror = null; respaldo(); };
    audio.src = f.src; audio.muted = R.silencio; R.hablando = true;
    const p = audio.play(); if (p && p.catch) p.catch(() => { if (R.activo && !R.pausado) respaldo(); });
  }
  function avanzar() {
    if (!R.activo || R.pausado) return;
    R.hablando = false; R.frase++;
    if (R.frase < frases().length) reproducirFrase();
    else if (R.cap + 1 < guion.length) R.timer = setTimeout(() => reproducirCap(R.cap + 1), 450);
    else terminar(true);
  }
  function pausar() {
    if (!R.activo || R.pausado) return;
    R.pausado = true; clearTimeout(R.timer); audio.pause(); R.hablando = false; if ("speechSynthesis" in window) speechSynthesis.cancel();
    actualizarControles(); actualizarDock();
  }
  function seguir() {
    if (!R.activo) return iniciar(0);
    R.pausado = false; actualizarControles(); actualizarDock();
    const c = guion[R.cap]; enfocar(c.resalta); irA(c, R.cap);
    if (audio.src && audio.currentTime > 0 && !audio.ended && audio.currentTime < (audio.duration || 0) - 0.05) {
      R.hablando = true; audio.play().catch(() => reproducirFrase());   // dentro del toque: sigue donde iba
    } else reproducirFrase();
  }
  function terminar(completo) {
    cortar(); Object.assign(R, { activo: false, pausado: false, terminado: !!completo });
    enfocar(null); document.body.classList.remove("en-recorrido");
    mostrar(completo ? T().fin : (idioma === "es" ? ES.b_hola : DIC[idioma].b_hola));
    actualizarControles(); actualizarDock(); pintarCapitulos();
  }
  function actualizarControles() {
    $$("[data-accion='pausa']").forEach((b) => { b.hidden = !R.activo; b.textContent = R.pausado ? "▶" : "❚❚"; b.setAttribute("aria-label", R.pausado ? T().seguir : T().pausar); });
    $$(".burbuja .iniciar").forEach((b) => { b.hidden = R.activo; });
    $$("[data-accion='silencio']").forEach((b) => { b.textContent = R.silencio ? "🔇" : "🔊"; b.setAttribute("aria-pressed", String(R.silencio)); });
    $$("[data-accion='cc']").forEach((b) => b.setAttribute("aria-pressed", String(R.cc)));
    $("#burbuja").classList.toggle("sin-cc", !R.cc); $("#dock").classList.toggle("sin-cc", !R.cc);
  }
  let portadaVisible = true;
  function actualizarDock() {
    const d = $("#dock"); d.classList.toggle("visible", R.activo && !portadaVisible); d.classList.toggle("pausado", R.pausado);
  }
  new IntersectionObserver(([e]) => { portadaVisible = e.isIntersecting; actualizarDock(); }, { threshold: 0.25 }).observe($(".asistente"));

  $$("[data-recorrido]").forEach((b) => b.addEventListener("click", () => { if (!R.activo) iniciar(0); else if (R.pausado) seguir(); else pausar(); }));
  $$("[data-accion]").forEach((b) => b.addEventListener("click", () => {
    const a = b.dataset.accion;
    if (a === "pausa") R.pausado ? seguir() : pausar();
    else if (a === "seguir") seguir();
    else if (a === "silencio") { R.silencio = !R.silencio; audio.muted = R.silencio; if (R.silencio && "speechSynthesis" in window) speechSynthesis.cancel(); actualizarControles(); }
    else if (a === "cc") { R.cc = !R.cc; actualizarControles(); }
    else if (a === "saltar" && R.activo) { cortar(); R.pausado = false; actualizarControles(); R.cap + 1 < guion.length ? reproducirCap(R.cap + 1) : terminar(true); }
    else if (a === "cerrar") terminar(false);
  }));
  // Si el visitante se mueve por su cuenta, el asistente hace una pausa y le deja el botón «Seguir»
  const interrumpir = () => { if (R.activo && !R.pausado && performance.now() - R.programado > 1400) pausar(); };
  addEventListener("wheel", interrumpir, { passive: true });
  addEventListener("touchmove", interrumpir, { passive: true });
  addEventListener("keydown", (e) => { if (["ArrowDown", "ArrowUp", "PageDown", "PageUp", "Home", "End"].includes(e.key)) interrumpir(); if (e.key === "Escape" && R.activo) terminar(false); });

  /* ================= orbes y onda de voz ================= */
  const onda = $("#onda"), forma = Array.from({ length: 34 }, (_, i) => 0.35 + 0.65 * Math.abs(Math.sin(i * 1.7) * Math.sin(i * 0.45 + 0.6)));
  onda.innerHTML = forma.map(() => "<i></i>").join("");
  const barras = $$("i", onda);
  const visibles = new Set();
  const vigia = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting ? visibles.add(e.target) : visibles.delete(e.target)));
  ["#orbe", "#orbe-dock"].forEach((s) => vigia.observe($(s)));
  function cuadro(now) {
    const t = reducido ? 0 : now / 1000;
    const v = nivelVoz(); nivel += (v - nivel) * 0.35;
    const est = { habla: R.hablando, piensa: R.activo && !R.hablando && !R.pausado && performance.now() - R.programado < 900 };
    if (visibles.has($("#orbe"))) {
      OrbeSaturno.dibujar($("#orbe"), t, nivel, est);
      barras.forEach((b, i) => { b.style.height = (4 + (R.hablando ? nivel * 18 * forma[i] * (0.6 + 0.4 * Math.sin(now / 70 + i)) : 0)) + "px"; });
    }
    if (visibles.has($("#orbe-dock")) && $("#dock").classList.contains("visible")) OrbeSaturno.dibujar($("#orbe-dock"), t, nivel, est);
    requestAnimationFrame(cuadro);
  }

  /* ================= «Mire Apex en su restaurante»: el video ================= */
  const VTX = {
    es: { una_noche: "UNA NOCHE EN", mesa: "MESA 4", escaneando: "Escaneando…", bienvenido: "Bienvenido a", carta: "LA CARTA", recomendado: "★ RECOMENDADO", pedir: "Pedir",
          agregado: "✓ Listo", ver_pedido: "Ver pedido", enviando: "✓ Enviado a cocina", nuevo_pedido: "NUEVO PEDIDO", total: "TOTAL", via: "vía Apex Play",
          cifras: ["errores", "comisiones", "esperas"], asi: "Así se vería Apex en", instalacion: "Instalación remota en 5 a 7 días hábiles", idx: 0 },
    en: { una_noche: "ONE NIGHT AT", mesa: "TABLE 4", escaneando: "Scanning…", bienvenido: "Welcome to", carta: "THE MENU", recomendado: "★ RECOMMENDED", pedir: "Order",
          agregado: "✓ Added", ver_pedido: "View order", enviando: "✓ Sent to kitchen", nuevo_pedido: "NEW ORDER", total: "TOTAL", via: "via Apex Play",
          cifras: ["mistakes", "commissions", "waiting"], asi: "This is how Apex would look at", instalacion: "Remote installation in 5 to 7 business days", idx: 1 },
    pt: { una_noche: "UMA NOITE EM", mesa: "MESA 4", escaneando: "Escaneando…", bienvenido: "Bem-vindo ao", carta: "O CARDÁPIO", recomendado: "★ RECOMENDADO", pedir: "Pedir",
          agregado: "✓ Pronto", ver_pedido: "Ver pedido", enviando: "✓ Enviado à cozinha", nuevo_pedido: "NOVO PEDIDO", total: "TOTAL", via: "via Apex Play",
          cifras: ["erros", "comissões", "espera"], asi: "Assim ficaria a Apex em", instalacion: "Instalação remota em 5 a 7 dias úteis", idx: 2 },
  };
  const form = $("#form-sim"), lienzo = $("#video"), video = ApexVideo.crear(lienzo);
  const precioNum = (s) => +String(s).replace(/\D/g, "") || 0;
  let logo = null, generado = false;
  function datosSim() {
    const v = (k) => (form.elements[k].value || "").trim(), ph = (k) => form.elements[k].placeholder;
    return { n: v("nombre") || ph("nombre"), c: v("ciudad"), t: v("tipo"), color: form.elements.color.value || "#b3412b", logoImg: logo,
      platos: [1, 2, 3].map((i) => ({ nombre: v("p" + i) || ph("p" + i), precio: precioNum(v("v" + i) || ph("v" + i)) })) };
  }
  let posterPendiente = false;
  function pintarSim() {   // mientras escribe, la portada del video se actualiza con su nombre y su color
    if (!form || posterPendiente) return; posterPendiente = true;
    requestAnimationFrame(() => { posterPendiente = false; if (!["reproduciendo", "pausado"].includes(video.estado)) video.poster(datosSim(), VTX[idioma]);
      $("#reproductor").style.setProperty("--marca", form.elements.color.value || "#b3412b");
      $("#v-wa").href = `https://wa.me/${WA}?text=${encodeURIComponent(T().wa.sim(datosSim()))}`; });
  }
  form.addEventListener("input", pintarSim);
  document.fonts?.ready?.then(pintarSim);
  $("#s-logo").addEventListener("change", (e) => {
    const f = e.target.files[0]; if (!f || !f.type.startsWith("image/") || f.size > 6e6) return;
    const lector = new FileReader(); lector.onload = () => { const im = new Image(); im.onload = () => { logo = im; pintarSim(); }; im.src = lector.result; }; lector.readAsDataURL(f);
  });
  const mmss = (t) => Math.floor(t / 60) + ":" + String(Math.floor(t % 60)).padStart(2, "0");
  video.onprogreso = (t, total) => { $("#v-pista").style.width = (t / total * 100) + "%"; $("#v-t").textContent = mmss(t); $("#v-total").textContent = mmss(total); };
  video.onfin = () => { $("#v-play").textContent = "↺"; $("#v-play").setAttribute("aria-label", "↺"); $("#v-otra").hidden = false; };
  video.onarchivo = (a) => { const b = $("#v-bajar"); b.hidden = false; b.onclick = () => {
    const url = URL.createObjectURL(a.blob), enlace = document.createElement("a"), slug = datosSim().n.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^\w]+/g, "-").replace(/^-|-$/g, "");
    enlace.href = url; enlace.download = `Apex-${slug || "video"}.${a.ext}`; document.body.append(enlace); enlace.click(); enlace.remove(); setTimeout(() => URL.revokeObjectURL(url), 4000); }; };
  async function generarVideo() {
    video.desbloquear();                        // el sonido se habilita en el mismo toque (iPhone)
    if (R.activo && !R.pausado) pausar();
    const d = datosSim(), cargando = $("#v-cargando");
    cargando.hidden = false; $("#v-capa").hidden = true; $("#v-acciones").hidden = true; $("#v-bajar").hidden = true; $("#v-otra").hidden = true;
    if (matchMedia("(max-width: 900px)").matches) $("#reproductor").scrollIntoView({ behavior: reducido ? "auto" : "smooth", block: "start" });
    let lineas = null;
    try {   // la voz de Apex dice el nombre de su restaurante; si no se puede, usa la voz grabada genérica
      const r = await fetch("/v1/sitio/video", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idioma, nombre: d.n, ciudad: d.c, plato: d.platos[0].nombre }) });
      if (r.ok) lineas = (await r.json()).lineas;
    } catch (e) {}
    if (!lineas) { try { lineas = (await (await fetch("/web/sitio/voz/video.json")).json())[idioma]; } catch (e) { lineas = []; } }
    await video.preparar(d, VTX[idioma], lineas);
    cargando.hidden = true; $("#v-acciones").hidden = false; generado = true;
    $("#v-play").textContent = "❚❚"; video.reproducir();
  }
  form.addEventListener("submit", (e) => { e.preventDefault(); generarVideo(); });
  new IntersectionObserver(([e]) => document.body.classList.toggle("en-video", e.isIntersecting && matchMedia("(max-width: 900px)").matches), { threshold: 0.2 }).observe($("#reproductor"));
  form.addEventListener("focusin", () => { if (R.activo && !R.pausado) pausar(); });
  $("#v-capa").addEventListener("click", () => { if (form.reportValidity()) generarVideo(); });
  $("#v-play").addEventListener("click", () => {
    if (!generado) { if (form.reportValidity()) generarVideo(); return; }
    if (video.estado === "reproduciendo") { video.pausar(); $("#v-play").textContent = "▶"; }
    else { video.desbloquear(); $("#v-otra").hidden = true; video.reproducir(); $("#v-play").textContent = "❚❚"; }
  });
  $("#v-otra").addEventListener("click", () => { video.desbloquear(); $("#v-otra").hidden = true; video.reproducir(); $("#v-play").textContent = "❚❚"; });
  $("#v-sonido").addEventListener("click", (e) => { const b = e.currentTarget, si = b.getAttribute("aria-pressed") !== "true"; b.setAttribute("aria-pressed", String(si)); b.textContent = si ? "🔇" : "🔊"; video.silencio(si); });

  /* ================= menú del celular, documentos legales y pie ================= */
  const cab = $("#cabecera"), ham = $("#hamburguesa");
  ham.addEventListener("click", () => { const a = !cab.classList.contains("abierto"); cab.classList.toggle("abierto", a); ham.setAttribute("aria-expanded", String(a)); });
  $$("#panel-movil a").forEach((a) => a.addEventListener("click", () => { cab.classList.remove("abierto"); ham.setAttribute("aria-expanded", "false"); }));
  const legal = $("#legal");
  const pestana = (p) => { $$("[data-pest]", legal).forEach((b) => b.setAttribute("aria-selected", String(b.dataset.pest === p))); $("#doc-privacidad").hidden = p !== "privacidad"; $("#doc-terminos").hidden = p !== "terminos"; };
  $$("[data-legal]").forEach((b) => b.addEventListener("click", () => { pestana(b.dataset.legal); legal.showModal(); }));
  $$("[data-pest]", legal).forEach((b) => b.addEventListener("click", () => pestana(b.dataset.pest)));
  $(".cerrar", legal).addEventListener("click", () => legal.close());
  legal.addEventListener("click", (e) => { if (e.target === legal) legal.close(); });
  $("#anio").textContent = new Date().getFullYear();

  aplicarIdioma(idioma); actualizarControles();
  requestAnimationFrame(cuadro);
  // Llega del escáner de prospectos con ?nombre=…&ciudad=…&tipo=…: el formulario del video queda listo para ese restaurante
  (() => {
    const q = new URLSearchParams(location.search), f = document.getElementById("form-sim");
    if (!f || !q.get("nombre")) return;
    for (const k of ["nombre", "ciudad", "tipo"]) if (q.get(k) && f.elements[k]) f.elements[k].value = q.get(k).slice(0, f.elements[k].maxLength || 40);
    setTimeout(() => document.getElementById("su-restaurante")?.scrollIntoView({ behavior: "smooth" }), 400);
  })();
  window.ApexSitio = { iniciar, pausar, seguir, terminar, aplicarIdioma, generarVideo, video, estado: () => ({ ...R, idioma, video: video.estado }) };
})();
