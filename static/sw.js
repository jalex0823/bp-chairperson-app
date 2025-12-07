const CACHE_NAME = 'bp-chairperson-v1';
const urlsToCache = [
  '/',
  '/dashboard',
  '/calendar',
  '/profile',
  '/static/css/custom.css',
  '/static/manifest.json',
  // Add offline fallback page
  '/offline.html'
];

// Install service worker
self.addEventListener('install', function(event) {
  console.log('[ServiceWorker] Install');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('[ServiceWorker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate service worker
self.addEventListener('activate', function(event) {
  console.log('[ServiceWorker] Activate');
  event.waitUntil(
    caches.keys().then(function(keyList) {
      return Promise.all(keyList.map(function(key) {
        if (key !== CACHE_NAME) {
          console.log('[ServiceWorker] Removing old cache', key);
          return caches.delete(key);
        }
      }));
    })
  );
  return self.clients.claim();
});

// Fetch events - serve from cache with network fallback
self.addEventListener('fetch', function(event) {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip external requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Return cached version or fetch from network
        if (response) {
          console.log('[ServiceWorker] Serving from cache:', event.request.url);
          return response;
        }

        return fetch(event.request).then(function(response) {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response for caching
          const responseToCache = response.clone();

          // Cache certain resources
          if (shouldCache(event.request.url)) {
            caches.open(CACHE_NAME)
              .then(function(cache) {
                cache.put(event.request, responseToCache);
              });
          }

          return response;
        }).catch(function() {
          // Return offline page for navigation requests
          if (event.request.destination === 'document') {
            return caches.match('/offline.html');
          }
        });
      }
    )
  );
});

// Determine if a URL should be cached
function shouldCache(url) {
  // Cache static assets and key pages
  return url.includes('/static/') || 
         url.includes('/dashboard') || 
         url.includes('/calendar') || 
         url.includes('/profile');
}

// Handle push notifications
self.addEventListener('push', function(event) {
  console.log('[ServiceWorker] Push received');
  
  const options = {
    body: event.data ? event.data.text() : 'You have a meeting reminder!',
    icon: '/static/img/icon-192x192.png',
    badge: '/static/img/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'view',
        title: 'View Meeting',
        icon: '/static/img/calendar-icon.png'
      },
      {
        action: 'close',
        title: 'Dismiss',
        icon: '/static/img/close-icon.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Back Porch Reminder', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', function(event) {
  console.log('[ServiceWorker] Notification click received');

  event.notification.close();

  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  }
});

// Background sync for offline actions
self.addEventListener('sync', function(event) {
  if (event.tag === 'background-sync') {
    console.log('[ServiceWorker] Background sync');
    event.waitUntil(
      // Sync any pending actions when back online
      syncPendingActions()
    );
  }
});

function syncPendingActions() {
  // Implementation for syncing offline actions
  return Promise.resolve();
}