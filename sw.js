/* ═══════════════════════════════════════════════
   Service Worker — Perla Ben-Harrosh Cookbook v11
   Network-first for HTML/JS (always fresh code)
   Cache-first for images (fast loading)
   v11: ignore non-GET, require basic response type,
        reject status 0/206, centralised _shouldCache()
═══════════════════════════════════════════════ */
const CACHE_NAME = 'perla-cookbook-v11';
const SHELL = [
  './',
  './index.html',
  './data.js',
  './pre_en.js',
  './manifest.json',
  './images/book_images/wedding.jpg',
  './book_data.js'
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

/**
 * Central cache-eligibility check.
 * @param {Request} request
 * @param {Response} response
 * @returns {boolean} true if safe to cache
 */
function _shouldCache(request, response) {
  // Only cache GET requests (never cache POST e.g. Web3Forms)
  if (request.method !== 'GET') return false;
  // Only cache same-origin (basic) responses — never opaque (type 'opaque')
  if (response.type !== 'basic') return false;
  // Reject error/partial responses
  if (response.status === 0 || response.status === 206) return false;
  // Must be a successful response
  if (response.status !== 200) return false;
  return true;
}

/* Fetch strategy:
   - Non-GET requests: passthrough (never cache POSTs)
   - Images: cache-first (fast, images rarely change)
   - Everything else: network-first (always get fresh HTML/JS/CSS) */
self.addEventListener('fetch', function(e) {
  // Ignore non-GET requests entirely (e.g. POST to Web3Forms)
  if (e.request.method !== 'GET') return;

  var url = new URL(e.request.url);

  // Images: cache-first, network fallback
  if (url.pathname.match(/\.(jpg|jpeg|png|webp|gif)$/i) || url.pathname.includes('/images/')) {
    e.respondWith(
      caches.match(e.request).then(function(cached) {
        if (cached) return cached;
        return fetch(e.request).then(function(resp) {
          if (_shouldCache(e.request, resp)) {
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
      if (_shouldCache(e.request, resp)) {
        var clone = resp.clone();
        caches.open(CACHE_NAME).then(function(c) { c.put(e.request, clone); });
      }
      return resp;
    }).catch(function() {
      return caches.match(e.request);
    })
  );
});
