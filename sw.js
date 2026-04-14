/* ═══════════════════════════════════════════════
   Service Worker — Perla Ben-Harrosh Cookbook v10
   Network-first for HTML/JS (always fresh code)
   Cache-first for images (fast loading)
═══════════════════════════════════════════════ */
const CACHE_NAME = 'perla-cookbook-v10';
const SHELL = [
  './',
  './index.html',
  './data.js',
  './pre_en.js',
  './manifest.json',
  './images/wedding.jpg'
];

/* Install — cache shell individually (resilient to 404s) */
self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return Promise.all(
        SHELL.map(function(url) {
          return cache.add(url).catch(function() {
            /* Skip files that fail to fetch (e.g. wedding.jpg not yet uploaded) */
          });
        })
      );
    }).then(function() { self.skipWaiting(); })
  );
});

/* Activate — clean ALL old caches, claim clients immediately */
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

/* Fetch strategy:
   - Images: cache-first (fast, images rarely change)
   - Everything else: network-first (always get fresh HTML/JS/CSS) */
self.addEventListener('fetch', function(e) {
  var url = new URL(e.request.url);

  // Images: cache-first, network fallback
  if (url.pathname.match(/\.(jpg|jpeg|png|webp|gif)$/i) || url.pathname.includes('/images/')) {
    e.respondWith(
      caches.match(e.request).then(function(cached) {
        if (cached) return cached;
        return fetch(e.request).then(function(resp) {
          if (resp && resp.status === 200) {
            var clone = resp.clone();
            caches.open(CACHE_NAME).then(function(c) { c.put(e.request, clone); });
          }
          return resp;
        });
      })
    );
    return;
  }

  // HTML, JS, CSS, fonts: network-first, cache fallback
  e.respondWith(
    fetch(e.request).then(function(resp) {
      if (resp && resp.status === 200 && url.origin === self.location.origin) {
        var clone = resp.clone();
        caches.open(CACHE_NAME).then(function(c) { c.put(e.request, clone); });
      }
      return resp;
    }).catch(function() {
      return caches.match(e.request);
    })
  );
});
