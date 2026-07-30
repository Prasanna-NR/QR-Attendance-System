// Service Worker for QR Attendance System
const CACHE_NAME = 'qr-attendance-v2';
const urlsToCache = [
    // HTML Pages
    '/',
    '/offline',
    
    // CSS
    '/static/css/style.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    
    // JS
    'https://code.jquery.com/jquery-3.6.0.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js',
    
    // Icons
    '/static/icons/icon-72x72.png',
    '/static/icons/icon-96x96.png',
    '/static/icons/icon-128x128.png',
    '/static/icons/icon-144x144.png',
    '/static/icons/icon-152x152.png',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-384x384.png',
    '/static/icons/icon-512x512.png',
    
    // Manifest
    '/manifest.json'
];


self.addEventListener('install', event => {
    console.log('[Service Worker] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[Service Worker] Caching app shell');
                return cache.addAll(urlsToCache);
            })
            .then(() => {
                console.log('[Service Worker] Installation complete');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('[Service Worker] Installation failed:', error);
            })
    );
});

//  clean old caches
self.addEventListener('activate', event => {
    console.log('[Service Worker] Activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[Service Worker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('[Service Worker] Activated successfully');
            return self.clients.claim();
        })
    );
});


self.addEventListener('fetch', event => {
    console.log('[Service Worker] Fetching:', event.request.url);
    
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache hit - return response
                if (response) {
                    console.log('[Service Worker] Serving from cache:', event.request.url);
                    return response;
                }
                
                // Not in cache - fetch from network
                console.log('[Service Worker] Fetching from network:', event.request.url);
                return fetch(event.request)
                    .then(response => {
                        // Check if we received a valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone the response
                        const responseToCache = response.clone();
                        
                        // Cache the fetched response
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(() => {
                        // If network fails and request is for HTML, show offline page
                        if (event.request.headers.get('accept').includes('text/html')) {
                            console.log('[Service Worker] Offline - serving offline page');
                            return caches.match('/offline');
                        }
                    });
            })
    );
});

// Push notification support
self.addEventListener('push', event => {
    console.log('[Service Worker] Push received:', event);
    
    let data = {
        title: 'QR Attendance System',
        body: 'You have a new notification',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png'
    };
    
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }
    
    const options = {
        body: data.body,
        icon: data.icon,
        badge: data.badge,
        vibrate: [200, 100, 200],
        data: {
            url: data.url || '/'
        },
        actions: [
            {
                action: 'open',
                title: 'Open App'
            },
            {
                action: 'close',
                title: 'Dismiss'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});


self.addEventListener('notificationclick', event => {
    console.log('[Service Worker] Notification clicked:', event);
    
    event.notification.close();

    if (event.action === 'open' || !event.action) {
        const url = event.notification.data.url || '/';
        event.waitUntil(
            clients.matchAll({ type: 'window' }).then(windowClients => {
                // Check if there is already a window/tab open with the target URL
                for (let client of windowClients) {
                    if (client.url === url && 'focus' in client) {
                        return client.focus();
                    }
                }
                // If not, open a new window/tab
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
        );
    }
});


self.addEventListener('sync', event => {
    console.log('[Service Worker] Sync event:', event);
    if (event.tag === 'sync-attendance') {
        event.waitUntil(syncAttendance());
    }
});


function syncAttendance() {
    console.log('[Service Worker] Syncing attendance data...');
    // This would sync any offline attendance data
    return clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage({
                type: 'sync-complete',
                message: 'Data synced successfully!'
            });
        });
    });
}


self.addEventListener('message', event => {
    console.log('[Service Worker] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});