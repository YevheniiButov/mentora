
// Service Worker for Mentora
const CACHE_NAME = 'dental-academy-v1';
const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/css/unified-theme.css',
    '/static/js/main.js',
    '/static/js/universal-scripts.js',
    '/static/images/logo.png'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});
