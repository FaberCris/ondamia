/* ═══════════════════════════════════════════
   OndaMia — Service Worker
   Strategia: Cache First per risorse statiche
   Network First per contenuti dinamici
   ═══════════════════════════════════════════ */

const CACHE_NAME = 'ondamia-v1.0.0';
const OFFLINE_URL = '/offline.html';

// Risorse da cachare all'installazione
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/offline.html',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  // Google Fonts (se disponibili)
  'https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap'
];

// ── INSTALL ──
self.addEventListener('install', event => {
  console.log('[SW] Installing OndaMia v1.0.0');
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      // Cache risorse principali, ignora errori su risorse esterne
      return Promise.allSettled(
        STATIC_ASSETS.map(url =>
          cache.add(url).catch(err => console.warn('[SW] Failed to cache:', url, err))
        )
      );
    }).then(() => self.skipWaiting())
  );
});

// ── ACTIVATE ──
self.addEventListener('activate', event => {
  console.log('[SW] Activating OndaMia');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// ── FETCH ──
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignora richieste non-GET e chrome-extension
  if (request.method !== 'GET') return;
  if (url.protocol === 'chrome-extension:') return;

  // Strategia per Google Fonts: Cache First
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Strategia per navigazione: Network First con fallback offline
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match(request).then(cached => cached || caches.match(OFFLINE_URL)))
    );
    return;
  }

  // Strategia per risorse statiche: Cache First
  event.respondWith(cacheFirst(request));
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Risorsa non disponibile offline', {
      status: 503,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    });
  }
}

// ── BACKGROUND SYNC (futuro) ──
self.addEventListener('sync', event => {
  if (event.tag === 'sync-diary') {
    console.log('[SW] Background sync: diary data');
    // Qui andrà la logica di sync col backend (Step 2)
  }
});

// ── PUSH NOTIFICATIONS (futuro) ──
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  self.registration.showNotification(data.title || 'OndaMia', {
    body: data.body || 'Come stai oggi?',
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-96.png',
    tag: 'ondamia-reminder',
    data: { url: data.url || '/' }
  });
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data.url));
});
