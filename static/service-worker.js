// Service Worker for QR Attendance System
// Version: v4 - Complete Working Version
const CACHE_NAME = 'qr-attendance-v4';

// Files to cache for offline use
const urlsToCache = [
    '/',
    '/static/icons/icon-72x72.png',
    '/static/icons/icon-96x96.png',
    '/static/icons/icon-128x128.png',
    '/static/icons/icon-144x144.png',
    '/static/icons/icon-152x152.png',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-384x384.png',
    '/static/icons/icon-512x512.png'
];

// Install event - Cache files
self.addEventListener('install', function(event) {
    console.log('[Service Worker] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('[Service Worker] Caching files...');
                return cache.addAll(urlsToCache);
            })
            .then(function() {
                console.log('[Service Worker] Cache complete!');
                return self.skipWaiting();
            })
            .catch(function(error) {
                console.error('[Service Worker] Cache failed:', error);
            })
    );
});

// Activate event - Clean old caches
self.addEventListener('activate', function(event) {
    console.log('[Service Worker] Activating...');
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[Service Worker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(function() {
            console.log('[Service Worker] Activated!');
            return self.clients.claim();
        })
    );
});

// Fetch event - Serve from cache, fallback to network
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Found in cache - return it
                if (response) {
                    console.log('[Service Worker] From cache:', event.request.url);
                    return response;
                }
                
                // Not in cache - fetch from network
                console.log('[Service Worker] From network:', event.request.url);
                return fetch(event.request)
                    .then(function(networkResponse) {
                        // Cache the response for next time
                        if (networkResponse && networkResponse.status === 200) {
                            const responseClone = networkResponse.clone();
                            caches.open(CACHE_NAME)
                                .then(function(cache) {
                                    cache.put(event.request, responseClone);
                                });
                        }
                        return networkResponse;
                    })
                    .catch(function() {
                        // If offline and requesting HTML, show offline page
                        if (event.request.headers.get('accept') && 
                            event.request.headers.get('accept').includes('text/html')) {
                            console.log('[Service Worker] Offline - serving offline page');
                            return caches.match('/offline');
                        }
                    });
            })
    );
});