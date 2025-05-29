/**
 * Service Worker для Dental Academy PWA
 * Обеспечивает работу приложения в режиме офлайн и оптимизацию кэширования
 * Версия: 1.3.0
 */

// Имена кэшей
const STATIC_CACHE_NAME = 'dental-academy-static-v1.3';
const DYNAMIC_CACHE_NAME = 'dental-academy-dynamic-v1.3';
const PAGES_CACHE_NAME = 'dental-academy-pages-v1.3';
const API_CACHE_NAME = 'dental-academy-api-v1.3';
const IMG_CACHE_NAME = 'dental-academy-images-v1.3';

// Ресурсы для обязательного кэширования (статические)
const STATIC_ASSETS = [
  '/',
  '/offline',
  '/static/css/mobile-app.css',
  '/static/css/theme-fixes.css',
  '/static/js/mobile-app.js',
  '/static/manifest.json',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png',
  '/static/images/offline.svg',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css'
];

// Ограничение размера динамического кэша
const MAX_DYNAMIC_CACHE_ITEMS = 100;
const MAX_PAGES_CACHE_ITEMS = 30;

// Установка Service Worker
self.addEventListener('install', event => {
  console.log('🟢 Service Worker: Установка...');
  
  // Принудительная активация без ожидания закрытия старых вкладок
  self.skipWaiting();
  
  event.waitUntil(
    // Кэширование критических ресурсов
    caches.open(STATIC_CACHE_NAME)
      .then(cache => {
        console.log('🔄 Кэширование статических ресурсов');
        return cache.addAll(STATIC_ASSETS.map(url => new Request(url, {credentials: 'same-origin'})))
          .catch(error => {
            console.error('⚠️ Ошибка кэширования статических ресурсов:', error);
            // Продолжаем даже при ошибке
            return Promise.resolve();
          });
      })
  );
});

// Активация Service Worker
self.addEventListener('activate', event => {
  console.log('🟢 Service Worker: Активация...');
  
  // Используем страницу немедленно
  event.waitUntil(self.clients.claim());
  
  // Удаляем устаревшие кэши
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => {
          return (
            cacheName.startsWith('dental-academy-') && 
            !cacheName.endsWith('-v1.3')
          );
        }).map(cacheName => {
          console.log('🗑️ Удаление устаревшего кэша:', cacheName);
          return caches.delete(cacheName);
        })
      );
    })
  );
});

// Перехват запросов
self.addEventListener('fetch', event => {
  const requestUrl = new URL(event.request.url);
  
  // Пропускаем запросы, не относящиеся к нашему приложению или POST запросы
  if (
    event.request.method !== 'GET' || 
    requestUrl.pathname.startsWith('/admin') ||
    requestUrl.pathname.startsWith('/api/auth') ||
    requestUrl.pathname.includes('/sw.js')
  ) {
    return;
  }

  // Стратегия кэширования зависит от типа запроса
  if (requestUrl.pathname.startsWith('/static/')) {
    // Для статических ресурсов: сначала кэш, затем сеть
    event.respondWith(cacheFirstStrategy(event.request, STATIC_CACHE_NAME));
  } 
  else if (requestUrl.pathname.startsWith('/api/')) {
    // Для API: сначала сеть, затем кэш
    event.respondWith(networkFirstStrategy(event.request, API_CACHE_NAME));
  }
  else if (
    requestUrl.pathname.includes('/images/') || 
    requestUrl.pathname.includes('.jpg') || 
    requestUrl.pathname.includes('.png') || 
    requestUrl.pathname.includes('.svg') || 
    requestUrl.pathname.includes('.webp')
  ) {
    // Для изображений: сначала кэш, затем сеть
    event.respondWith(cacheFirstStrategy(event.request, IMG_CACHE_NAME));
  }
  else {
    // Для HTML страниц: сначала сеть, затем кэш
    event.respondWith(networkFirstPageStrategy(event.request, PAGES_CACHE_NAME));
  }
});

// Стратегия "Сначала кэш, затем сеть"
async function cacheFirstStrategy(request, cacheName) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    // Асинхронное обновление кэша (без ожидания)
    updateCache(request, cacheName);
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    // Если ответ валидный, сохраняем его в кэше
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('⚠️ Fetch failed; returning offline page instead.', error);
    
    // Если запрос был для HTML страницы, возвращаем оффлайн страницу
    if (request.headers.get('Accept').includes('text/html')) {
      return caches.match('/offline');
    }
    
    // Для других ресурсов возвращаем пустой ответ
    return new Response('', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Стратегия "Сначала сеть, затем кэш"
async function networkFirstStrategy(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    
    // Если ответ валидный, сохраняем его в кэше
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('⚠️ Network request failed, getting from cache.', error);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Если запрос был для API и нет кэша, возвращаем пустой JSON
    if (request.url.includes('/api/')) {
      return new Response(JSON.stringify({
        error: 'offline',
        message: 'You are currently offline'
      }), {
        status: 200,
        headers: {'Content-Type': 'application/json'}
      });
    }
    
    return new Response('', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Стратегия для HTML страниц
async function networkFirstPageStrategy(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    
    // Если ответ валидный, сохраняем его в кэше
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
      
      // Очистка старых страниц
      cleanupCache(cacheName, MAX_PAGES_CACHE_ITEMS);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('⚠️ Network request failed for page, getting from cache.', error);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Если нет кэша, возвращаем оффлайн страницу
    return caches.match('/offline');
  }
}

// Асинхронное обновление кэша без блокировки ответа
async function updateCache(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      await cache.put(request, networkResponse);
      
      // Очистка старых записей
      if (cacheName === DYNAMIC_CACHE_NAME) {
        cleanupCache(cacheName, MAX_DYNAMIC_CACHE_ITEMS);
      }
    }
  } catch (error) {
    console.log('⚠️ Background cache update failed:', error);
  }
}

// Ограничение размера кэша (удаление старых записей)
async function cleanupCache(cacheName, maxItems) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  
  if (keys.length > maxItems) {
    console.log(`🧹 Cleaning up cache ${cacheName}, current size: ${keys.length}`);
    
    // Удаляем старые записи
    const itemsToDelete = keys.length - maxItems;
    for (let i = 0; i < itemsToDelete; i++) {
      await cache.delete(keys[i]);
    }
    
    console.log(`✅ Removed ${itemsToDelete} old items from ${cacheName}`);
  }
}

// Синхронизация в фоновом режиме
self.addEventListener('sync', event => {
  console.log('🔄 Background sync event:', event.tag);
  
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

// Обработка уведомлений
self.addEventListener('push', event => {
  console.log('📢 Push event received:', event);
  
  const notificationData = event.data.json();
  
  const notificationOptions = {
    body: notificationData.body || 'Новое сообщение от Dental Academy',
    icon: '/static/images/icon-192.png',
    badge: '/static/images/notification-badge.png',
    vibrate: [100, 50, 100],
    data: {
      url: notificationData.url || '/'
    }
  };
  
  event.waitUntil(
    self.registration.showNotification(
      notificationData.title || 'Dental Academy',
      notificationOptions
    )
  );
});

// Обработка клика по уведомлению
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  event.waitUntil(
    clients.matchAll({type: 'window'}).then(clientList => {
      const url = event.notification.data.url;
      
      // Если уже открыто окно, переключаемся на него
      for (const client of clientList) {
        if (client.url === url && 'focus' in client) {
          return client.focus();
        }
      }
      
      // Иначе открываем новое окно
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});

// Функция для синхронизации данных в фоновом режиме
async function syncData() {
  // Здесь можно реализовать синхронизацию оффлайн-данных с сервером
  console.log('🔄 Синхронизация данных с сервером...');
  
  // Пример реализации - отправка кэшированных данных
  try {
    // В реальном приложении здесь будет логика синхронизации
    console.log('✅ Синхронизация завершена успешно');
    return Promise.resolve();
  } catch (error) {
    console.error('❌ Ошибка синхронизации:', error);
    return Promise.reject(error);
  }
}

// Сообщаем основному потоку, что Service Worker успешно загрузился
self.clients.matchAll().then(clients => {
  clients.forEach(client => {
    client.postMessage({
      type: 'SW_INITIALIZED',
      message: 'Service Worker успешно загружен и активирован!'
    });
  });
});

console.log('✅ Service Worker успешно загружен!'); 