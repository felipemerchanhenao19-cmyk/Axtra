// Guarda la app (no las conversaciones) para que abra rápido y se vea aunque no haya señal.
const CACHE = "axtra-v2";
const APP = ["/", "/index.html", "/manifest.webmanifest", "/icono-192.png", "/icono-512.png",
  "/fonts/sora-latin-300-normal.woff2", "/fonts/sora-latin-400-normal.woff2", "/fonts/sora-latin-600-normal.woff2",
  "/fonts/inter-latin-400-normal.woff2", "/fonts/inter-latin-500-normal.woff2", "/fonts/inter-latin-600-normal.woff2",
  "/fonts/inter-cyrillic-400-normal.woff2", "/fonts/inter-cyrillic-600-normal.woff2"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(CACHE).then((c) => c.addAll(APP)).catch(() => {})); self.skipWaiting(); });
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin || url.pathname.startsWith("/api/")) return;
  // Primero la red (para recibir las actualizaciones); si no hay señal, lo guardado
  e.respondWith(fetch(e.request).then((r) => {
    if (r.ok) { const copia = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, copia)); }
    return r;
  }).catch(() => caches.match(e.request).then((r) => r || caches.match("/"))));
});

// Notificaciones (recordatorios y avisos de Axtra)
self.addEventListener("push", (e) => {
  let d = {}; try { d = e.data.json(); } catch { d = { titulo: "Axtra", cuerpo: e.data ? e.data.text() : "" }; }
  e.waitUntil(self.registration.showNotification(d.titulo || "Axtra", {
    body: d.cuerpo || "", icon: "/icono-192.png", badge: "/icono-192.png", vibrate: [120, 60, 120], data: { url: d.url || "/" } }));
});
self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: "window" }).then((cs) => {
    const c = cs.find((x) => x.url.startsWith(self.location.origin));
    return c ? c.focus() : self.clients.openWindow(e.notification.data.url || "/");
  }));
});
