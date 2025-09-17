/**
 * Service Worker for Mentora PWA
 * Provides offline functionality, caching, and push notifications
 */

const CACHE_NAME = 'dental-academy-v1.2.0';
const OFFLINE_URL = '/offline'; // ✅ ИСПРАВЛЕНО: убрал .html

// Files to cache for offline functionality
const STATIC_CACHE_URLS = [
  '/',
  '/offline', // ✅ ИСПРАВЛЕНО: убрал .html
  '/static/css/mobile-app.css',
  '/static/css/modern-theme.css',
  '/static/css/theme-fixes.css',
  '/static/js/mobile-app.js',
  '/static/js/theme-system.js', // Если есть
  '/static/images/logo.png', // Если есть
  '/static/images/favicon.png',
  '/static/favicon.png', // Если есть
  '/manifest.json', // ✅ ДОБАВЛЕНО
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css'
];

// API endpoints to cache
const API_CACHE_URLS = [
  '/api/user-stats',
  '/api/learning-paths',
  '/api/user-progress'
];

// Dynamic cache patterns
const CACHE_PATTERNS = {
  images: /\.(png|jpg|jpeg|svg|gif|webp)$/i,
  fonts: /\.(woff|woff2|ttf|eot)$/i,
  api: /^\/api\//,
  lessons: /^\/\w+\/lesson\//,
  modules: /^\/\w+\/module\//
};

// Cache strategies
const CACHE_STRATEGIES = {
  CACHE_FIRST: 'cache-first',
  NETWORK_FIRST: 'network-first',
  NETWORK_ONLY: 'network-only',
  CACHE_ONLY: 'cache-only',
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate'
};

// ===== INSTALL EVENT =====
self.addEventListener('install', event => {

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {

        // ✅ ИСПРАВЛЕНО: Кэшируем только существующие файлы
        return Promise.allSettled(
          STATIC_CACHE_URLS.map(url => 
            cache.add(url).catch(error => {
              console.warn(`⚠️ Failed to cache ${url}:`, error.message);
              return null; // Продолжаем даже если один файл не загрузился
            })
          )
        );
      })
      .then(() => {

        return self.skipWaiting();
      })
      .catch(error => {
        console.error('❌ Failed to cache static assets:', error);
      })
  );
});

// ===== ACTIVATE EVENT =====
self.addEventListener('activate', event => {

  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME) {

              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Take control of all clients
      self.clients.claim()
    ]).then(() => {

    })
  );
});

// ===== FETCH EVENT =====
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome extensions and other protocols
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  // ✅ ДОБАВЛЕНО: Skip admin routes для безопасности
  if (url.pathname.startsWith('/admin') || url.pathname.startsWith('/auth/logout')) {
    return;
  }
  
  // Determine cache strategy based on request
  const strategy = getCacheStrategy(request);
  
  event.respondWith(
    executeStrategy(request, strategy)
      .catch(error => {
        console.error('🔥 Fetch failed:', error);
        return handleFetchError(request, error);
      })
  );
});

// ===== CACHE STRATEGY FUNCTIONS =====

function getCacheStrategy(request) {
  const url = new URL(request.url);
  const pathname = url.pathname;
  
  // API requests - network first with fallback
  if (CACHE_PATTERNS.api.test(pathname)) {
    return CACHE_STRATEGIES.NETWORK_FIRST;
  }
  
  // Images - cache first
  if (CACHE_PATTERNS.images.test(pathname)) {
    return CACHE_STRATEGIES.CACHE_FIRST;
  }
  
  // Fonts - cache first
  if (CACHE_PATTERNS.fonts.test(pathname)) {
    return CACHE_STRATEGIES.CACHE_FIRST;
  }
  
  // Lessons and modules - stale while revalidate
  if (CACHE_PATTERNS.lessons.test(pathname) || CACHE_PATTERNS.modules.test(pathname)) {
    return CACHE_STRATEGIES.STALE_WHILE_REVALIDATE;
  }
  
  // External resources - cache first
  if (url.origin !== self.location.origin) {
    return CACHE_STRATEGIES.CACHE_FIRST;
  }
  
  // Default strategy for HTML pages
  return CACHE_STRATEGIES.NETWORK_FIRST;
}

async function executeStrategy(request, strategy) {
  switch (strategy) {
    case CACHE_STRATEGIES.CACHE_FIRST:
      return cacheFirst(request);
    
    case CACHE_STRATEGIES.NETWORK_FIRST:
      return networkFirst(request);
    
    case CACHE_STRATEGIES.STALE_WHILE_REVALIDATE:
      return staleWhileRevalidate(request);
    
    case CACHE_STRATEGIES.CACHE_ONLY:
      return cacheOnly(request);
    
    case CACHE_STRATEGIES.NETWORK_ONLY:
      return networkOnly(request);
    
    default:
      return networkFirst(request);
  }
}

// Cache First Strategy
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    throw error;
  }
}

// Network First Strategy
async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// Stale While Revalidate Strategy
async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  // Fetch from network in background
  const networkResponsePromise = fetch(request).then(response => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch(() => {
    // Ignore network errors in background
  });
  
  // Return cached response immediately if available
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // If no cached response, wait for network
  return networkResponsePromise;
}

// Cache Only Strategy
async function cacheOnly(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  throw new Error('No cached response available');
}

// Network Only Strategy
async function networkOnly(request) {
  return fetch(request);
}

// ===== ERROR HANDLING =====

async function handleFetchError(request, error) {
  const url = new URL(request.url);
  
  // For navigation requests, show offline page
  if (request.mode === 'navigate') {
    const cache = await caches.open(CACHE_NAME);
    const offlineResponse = await cache.match(OFFLINE_URL);
    
    if (offlineResponse) {
      return offlineResponse;
    }
    
    // ✅ УЛУЧШЕНО: Более красивая offline страница
    return new Response(`
      <!DOCTYPE html>
      <html lang="ru">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Offline - Mentora</title>
        <style>
          * { box-sizing: border-box; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            color: #374151;
            text-align: center;
            padding: 20px;
          }
          .offline-container {
            background: white;
            padding: 3rem 2rem;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 100%;
          }
          .offline-icon {
            font-size: 64px;
            margin-bottom: 20px;
            opacity: 0.8;
          }
          .offline-title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 12px;
            color: #111827;
          }
          .offline-message {
            font-size: 16px;
            line-height: 1.6;
            opacity: 0.8;
            margin-bottom: 24px;
          }
          .retry-btn {
            padding: 12px 24px;
            background: linear-gradient(135deg, #3ECDC1, #2BB6AC);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
          }
          .retry-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(62, 205, 193, 0.3);
          }
          .status { 
            margin-top: 20px; 
            padding: 12px;
            background: #f3f4f6;
            border-radius: 8px;
            font-size: 14px;
          }
          .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #ef4444;
            margin-right: 8px;
          }
          .status-dot.online { background: #10b981; }
          @media (max-width: 480px) {
            .offline-container { padding: 2rem 1.5rem; }
            .offline-title { font-size: 20px; }
          }
        </style>
      </head>
      <body>
        <div class="offline-container">
          <div class="offline-icon">📱</div>
          <h1 class="offline-title">Вы офлайн</h1>
          <p class="offline-message">
            Проверьте подключение к интернету. Некоторые материалы доступны без интернета.
          </p>
          <button class="retry-btn" onclick="window.location.reload()">
            🔄 Попробовать снова
          </button>
          <div class="status">
            <span class="status-dot" id="status-dot"></span>
            <span id="status-text">Проверка соединения...</span>
          </div>
        </div>
        
        <script>
          function updateStatus() {
            const dot = document.getElementById('status-dot');
            const text = document.getElementById('status-text');
            if (navigator.onLine) {
              dot.classList.add('online');
              text.textContent = 'Соединение восстановлено! Нажмите "Попробовать снова".';
            } else {
              dot.classList.remove('online');
              text.textContent = 'Нет подключения к интернету.';
            }
          }
          
          window.addEventListener('online', updateStatus);
          window.addEventListener('offline', updateStatus);
          updateStatus();
          
          // Auto-reload when online
          window.addEventListener('online', () => {
            setTimeout(() => window.location.reload(), 1000);
          });
        </script>
      </body>
      </html>
    `, {
      status: 200,
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  }
  
  // For API requests, return error response
  if (CACHE_PATTERNS.api.test(url.pathname)) {
    return new Response(JSON.stringify({
      error: 'Network unavailable',
      offline: true,
      message: 'This feature requires an internet connection'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // For other requests, throw the error
  throw error;
}

// ===== MESSAGE HANDLING ===== ✅ ДОБАВЛЕНО
self.addEventListener('message', event => {

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({
      type: 'VERSION',
      version: CACHE_NAME
    });
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    caches.delete(CACHE_NAME).then(() => {
      event.ports[0].postMessage({ type: 'CACHE_CLEARED' });
    });
  }
});

// ===== PUSH NOTIFICATIONS =====

self.addEventListener('push', event => {

  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (error) {
              data = { title: 'Mentora', body: event.data.text() };
    }
  }
  
  const options = {
    title: data.title || 'Mentora',
    body: data.body || 'У вас есть новые материалы для изучения!',
    icon: '/static/images/favicon.png',
    badge: '/static/images/favicon.png',
    image: data.image,
    data: data.url ? { url: data.url } : undefined,
    actions: [
      {
        action: 'open',
        title: 'Открыть',
        icon: '/static/images/favicon.png'
      },
      {
        action: 'close',
        title: 'Закрыть'
      }
    ],
    requireInteraction: false,
    silent: false,
    vibrate: [100, 50, 100] // ✅ ДОБАВЛЕНО
  };
  
  event.waitUntil(
    self.registration.showNotification(options.title, options)
  );
});

self.addEventListener('notificationclick', event => {

  event.notification.close();
  
  if (event.action === 'close') {
    return;
  }
  
  const url = event.notification.data?.url || '/';
  
  event.waitUntil(
    self.clients.matchAll({ type: 'window' }).then(clients => {
      // Check if there's already a window/tab open with the target URL
      for (const client of clients) {
        if (client.url === url && 'focus' in client) {
          return client.focus();
        }
      }
      
      // If not, open a new window/tab
      if (self.clients.openWindow) {
        return self.clients.openWindow(url);
      }
    })
  );
});

// ===== BACKGROUND SYNC =====

self.addEventListener('sync', event => {

  if (event.tag === 'lesson-progress-sync') {
    event.waitUntil(syncLessonProgress());
  }
  
  if (event.tag === 'offline-actions-sync') {
    event.waitUntil(syncOfflineActions());
  }
});

async function syncLessonProgress() {
  try {
    // Get offline progress data from IndexedDB or localStorage
    const offlineProgress = JSON.parse(localStorage.getItem('offline-lesson-progress') || '[]');
    
    if (offlineProgress.length === 0) {
      return;
    }
    
    // Send progress to server
    for (const progress of offlineProgress) {
      try {
        await fetch('/api/lesson-progress', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(progress)
        });
      } catch (error) {
        console.error('Failed to sync progress item:', error);
      }
    }
    
    // Clear synced data
    localStorage.removeItem('offline-lesson-progress');

  } catch (error) {
    console.error('❌ Failed to sync lesson progress:', error);
  }
}

async function syncOfflineActions() {
  try {
    const offlineActions = JSON.parse(localStorage.getItem('offline-actions') || '[]');
    
    if (offlineActions.length === 0) {
      return;
    }
    
    for (const action of offlineActions) {
      try {
        await fetch(action.url, {
          method: action.method,
          headers: action.headers,
          body: action.body
        });
      } catch (error) {
        console.error('Failed to sync action:', error);
      }
    }
    
    localStorage.removeItem('offline-actions');

  } catch (error) {
    console.error('❌ Failed to sync offline actions:', error);
  }
}

// ===== PERIODIC BACKGROUND SYNC =====

self.addEventListener('periodicsync', event => {

  if (event.tag === 'content-sync') {
    event.waitUntil(syncContent());
  }
});

async function syncContent() {
  try {
    // Sync latest lessons and modules
    const response = await fetch('/api/content-updates');
    const updates = await response.json();
    
    if (updates.hasUpdates) {
      const cache = await caches.open(CACHE_NAME);
      
      // Cache new content
      for (const url of updates.newContent) {
        try {
          const contentResponse = await fetch(url);
          if (contentResponse.ok) {
            await cache.put(url, contentResponse);
          }
        } catch (error) {
          console.error('Failed to cache content:', url, error);
        }
      }

    }
    
  } catch (error) {
    console.error('❌ Failed to sync content:', error);
  }
}

// ===== UTILITY FUNCTIONS =====

// Clean up old cache entries
async function cleanupCache() {
  const cache = await caches.open(CACHE_NAME);
  const requests = await cache.keys();
  const now = Date.now();
  const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days
  
  for (const request of requests) {
    const response = await cache.match(request);
    const dateHeader = response.headers.get('date');
    
    if (dateHeader) {
      const responseDate = new Date(dateHeader).getTime();
      if (now - responseDate > maxAge) {
        await cache.delete(request);
      }
    }
  }
}

// Log cache statistics
async function logCacheStats() {
  try {
    const cache = await caches.open(CACHE_NAME);
    const requests = await cache.keys();

    // Group by type
    const stats = {
      html: 0,
      css: 0,
      js: 0,
      images: 0,
      api: 0,
      other: 0
    };
    
    requests.forEach(request => {
      const url = request.url;
      if (url.includes('.html') || url.endsWith('/')) stats.html++;
      else if (url.includes('.css')) stats.css++;
      else if (url.includes('.js')) stats.js++;
      else if (CACHE_PATTERNS.images.test(url)) stats.images++;
      else if (CACHE_PATTERNS.api.test(url)) stats.api++;
      else stats.other++;
    });

  } catch (error) {
    console.error('❌ Failed to get cache stats:', error);
  }
}

// Periodic cleanup (every hour)
setInterval(() => {
  cleanupCache();
  logCacheStats();
}, 60 * 60 * 1000);

