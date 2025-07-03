const CACHE_NAME = "hamrogahana-pwa-v1";
const urlsToCache = [
  "/",
  "/static/css/style.css",
  "/static/js/script.js",
  "/static/icons/tm.png",
  "/static/icons/gem_white.png",
];

// Install event
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

// Fetch event
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
