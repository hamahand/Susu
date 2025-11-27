const CACHE_NAME = 'sususave-v1';
const API_CACHE_NAME = 'sususave-api-v1';

// Assets to cache on install
const STATIC_ASSETS = [
  '/app/',
  '/app/index.html',
  '/app/login',
  '/app/register',
  '/app/dashboard',
  '/assets/logo.svg',
  '/assets/logo-icon.svg',
  '/assets/favicon.svg',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - network first for API, cache first for assets
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API requests - network first with cache fallback
  if (url.pathname.startsWith('/auth/') || 
      url.pathname.startsWith('/groups/') || 
      url.pathname.startsWith('/payments/') || 
      url.pathname.startsWith('/payouts/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Clone the response before caching
          const responseClone = response.clone();
          caches.open(API_CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });
          return response;
        })
        .catch(() => {
          // Fallback to cache if network fails
          return caches.match(request);
        })
    );
    return;
  }

  // Static assets - cache first with network fallback
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(request).then((response) => {
        // Don't cache non-successful responses
        if (!response || response.status !== 200 || response.type === 'error') {
          return response;
        }

        // Clone the response
        const responseClone = response.clone();

        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, responseClone);
        });

        return response;
      });
    })
  );
});

// Background sync for failed requests (future feature)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-payments') {
    console.log('[SW] Background sync triggered');
    // Implement background sync logic here
  }
});

// Push notifications (future feature)
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'SusuSave';
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/assets/logo-icon.svg',
    badge: '/assets/favicon.svg',
    vibrate: [200, 100, 200],
    data: data.url || '/app/dashboard',
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked');
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data || '/app/dashboard')
  );
});

