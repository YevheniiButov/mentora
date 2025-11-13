// Service Worker for Mentora Learning Map PWA
const CACHE_NAME = 'mentora-learning-map-v2';
const STATIC_CACHE = 'mentora-static-v2';
const DYNAMIC_CACHE = 'mentora-dynamic-v2';

const urlsToCache = [
  '/nl/learning-map',
  '/static/css/pages/learning_map.css',
  '/static/css/main.min.css',
  '/static/js/learning-map.js',
  '/static/images/icon-192-new.png',
  '/static/images/icon-512-new.png',
  '/static/css/compact-diagnostic.css',
  '/static/css/flashcards_simple.css'
];

// Install event
self.addEventListener('install', function(event) {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then(function(cache) {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(urlsToCache).catch(function(error) {
          console.log('[Service Worker] Static cache addAll failed:', error);
        });
      }),
      caches.open(DYNAMIC_CACHE).then(function(cache) {
        console.log('[Service Worker] Dynamic cache ready');
        return Promise.resolve();
      })
    ])
  );
  self.skipWaiting(); // Activate immediately
});

// Activate event
self.addEventListener('activate', function(event) {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE && cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(function() {
      // Clean up old dynamic cache entries (keep last 50)
      return caches.open(DYNAMIC_CACHE).then(function(cache) {
        return cache.keys().then(function(keys) {
          if (keys.length > 50) {
            return cache.delete(keys[0]);
          }
        });
      });
    })
  );
  return self.clients.claim(); // Take control of all pages
});

// Fetch event - Network first, fallback to cache
self.addEventListener('fetch', function(event) {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  const url = new URL(event.request.url);
  
  // Static assets - Cache first strategy
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(event.request)
        .then(function(response) {
          if (response) {
            return response;
          }
          return fetch(event.request).then(function(response) {
            if (response && response.status === 200) {
              const responseToCache = response.clone();
              caches.open(STATIC_CACHE).then(function(cache) {
                cache.put(event.request, responseToCache);
              });
            }
            return response;
          });
        })
    );
    return;
  }

  // API and dynamic content - Network first strategy
  event.respondWith(
    fetch(event.request)
      .then(function(response) {
        // Check if valid response
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }

        // Clone the response
        const responseToCache = response.clone();

        // Cache dynamic content
        caches.open(DYNAMIC_CACHE)
          .then(function(cache) {
            cache.put(event.request, responseToCache);
          });

        return response;
      })
      .catch(function() {
        // Network failed, try cache
        return caches.match(event.request)
          .then(function(response) {
            if (response) {
              return response;
            }
            
            // For navigation requests, return cached learning map
            if (event.request.mode === 'navigate') {
              return caches.match('/nl/learning-map');
            }
            
            // If not in cache, return offline message
            return new Response(
              JSON.stringify({
                error: 'Offline',
                message: 'You are currently offline. Some features may not be available.'
              }),
              {
                status: 503,
                statusText: 'Service Unavailable',
                headers: new Headers({
                  'Content-Type': 'application/json'
                })
              }
            );
          });
      })
  );
});

// Handle push notifications
self.addEventListener('push', function(event) {
  console.log('[Service Worker] Push notification received');
  
  let notificationData = {
    title: 'Mentora',
    body: 'New update available',
    icon: '/static/images/icon-192-new.png',
    badge: '/static/images/icon-192-new.png',
    tag: 'mentora-notification',
    data: {
      url: '/nl/learning-map'
    }
  };
  
  if (event.data) {
    try {
      const data = event.data.json();
      notificationData = {
        title: data.title || 'Mentora',
        body: data.body || 'New update available',
        icon: data.icon || '/static/images/icon-192-new.png',
        badge: '/static/images/icon-192-new.png',
        tag: data.tag || 'mentora-notification',
        data: {
          url: data.url || '/nl/learning-map'
        },
        requireInteraction: data.requireInteraction || false,
        vibrate: data.vibrate || [200, 100, 200]
      };
    } catch (e) {
      notificationData.body = event.data.text();
    }
  }

  event.waitUntil(
    self.registration.showNotification(notificationData.title, notificationData)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', function(event) {
  console.log('[Service Worker] Notification clicked');
  event.notification.close();

  const urlToOpen = event.notification.data?.url || '/nl/learning-map';

  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    }).then(function(clientList) {
      // Check if there's already a window open
      for (let i = 0; i < clientList.length; i++) {
        const client = clientList[i];
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      // If no window is open, open a new one
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Schedule daily learning reminders
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'SCHEDULE_NOTIFICATION') {
    const { title, body, delay } = event.data;
    
    // Schedule notification using setTimeout (simplified version)
    // In production, you'd use more sophisticated scheduling
    setTimeout(function() {
      self.registration.showNotification(title || 'Mentora', {
        body: body || 'Time for your daily learning!',
        icon: '/static/images/icon-192-new.png',
        badge: '/static/images/icon-192-new.png',
        tag: 'daily-reminder',
        vibrate: [200, 100, 200],
        data: {
          url: '/nl/learning-map'
        }
      });
    }, delay || 0);
  }
});

