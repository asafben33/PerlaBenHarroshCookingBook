/* ═══════════════════════════════════════════════
   Service Worker — Perla Ben-Harrosh Cookbook
   Offline-first: caches shell + data for instant load
═══════════════════════════════════════════════ */
const CACHE_NAME = 'perla-cookbook-v5';
const SHELL = [
  './',
  './index.html',
  './data.js',
  './wedding.jpg',
  'https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@300;400;500;700;900&display=swap'
];

/* Install — cache shell */
self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(SHELL);
    }).then(function() { self.skipWaiting(); })
  );
});

/* Activate — clean old caches */
self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== CACHE_NAME; })
            .map(function(k) { return caches.delete(k); })
      );
    }).then(function() { return self.clients.claim(); })
  );
});

/* Fetch — cache-first for shell, network-first for images */
self.addEventListener('fetch', function(e) {
  var url = new URL(e.request.url);

  // Images: network-first, cache fallback
  if (url.pathname.match(/\.(jpg|jpeg|png|webp|gif)$/i) || url.pathname.includes('/images/')) {
    e.respondWith(
      fetch(e.request).then(function(resp) {
        if (resp && resp.status === 200) {
          var clone = resp.clone();
          caches.open(CACHE_NAME).then(function(c) { c.put(e.request, clone); });
        }
        return resp;
      }).catch(function() {
        return caches.match(e.request);
      })
    );
    return;
  }

  // Shell & data: cache-first, network fallback
  e.respondWith(
    caches.match(e.request).then(function(cached) {
      if (cached) return cached;
      return fetch(e.request).then(function(resp) {
        if (resp && resp.status === 200 && url.origin === self.location.origin) {
          var clone = resp.clone();
          caches.open(CACHE_NAME).then(function(c) { c.put(e.request, clone); });
        }
        return resp;
      });
    })
  );
});
