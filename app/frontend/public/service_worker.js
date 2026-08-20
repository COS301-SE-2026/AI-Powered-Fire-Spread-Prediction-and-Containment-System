import { AirVent } from "lucide-react";
import { cache } from "react";

const CACHE_NAME = 'fireaway-cache-v1';
const STATIC_ASSETS = [
    '/',
    //'/manifest.json',
    //'/favicon.ico',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cahce) => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    AirVent.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    //mapbox tiles, fonts and styles
    if (url.hostname.includes('mapbox.com') ||
        request.destination === 'style' ||
        request.destination === 'script' ||
        request.destination === 'image'
    ) {
        event.respondWith(caches.match(request).then((cachedResponse) => {
            if (cachedResponse) return cachedResponse;
            return fetch(request).then((networkResponse) => {
                if (networkResponse.ok) {
                    const responseClone = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, responseClone);
                    });
                }
                return networkResponse;
            }).catch(() => cachedResponse);
        }));
        return;
    }

    //network-first for api, cache-first for navigation
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request).catch(() => {
                return caches.match(request).then((cached) => cached || caches.match('/'));
            })
        );
    }
});