import { defaultCache } from '@serwist/next/worker';
import { NetworkOnly, Serwist } from 'serwist';
import type { PrecacheEntry, RuntimeCaching, SerwistGlobalConfig } from 'serwist';

declare global {
    interface WorkerGlobalScope extends SerwistGlobalConfig {
        __SW_MANIFEST: (PrecacheEntry | string)[] | undefined;
    }
}
declare const self: ServiceWorkerGlobalScope;

const CACHE_NAME = 'fireaway-cache-v1';

const apiBypass: RuntimeCaching[] = [
    {
        matcher: ({ url, sameOrigin }) => url.pathname.startsWith("/api/") || !sameOrigin,
        handler: new NetworkOnly(),
    },
];

const mapboxCaching: RuntimeCaching[] = [
    {
        matcher: ({ url, request }) =>
            url.hostname.includes('mapbox.com') ||
            request.destination === 'style' ||
            request.destination === 'script' ||
            request.destination === 'image',
        handler: async ({ request }) => {
            const cache = await caches.open(CACHE_NAME);
            const cachedResponse = await cache.match(request);
            try {
                const networkResponse = await fetch(request);
                if (networkResponse.ok) {
                    cache.put(request, networkResponse.clone());
                }
                return networkResponse;
            } catch {
                return cachedResponse || Response.error();
            }
        },
    },
];

const serwist = new Serwist({
    precacheEntries: self.__SW_MANIFEST,
    skipWaiting: true,
    clientsClaim: true,
    navigationPreload: true,
    runtimeCaching: [...apiBypass, ...mapboxCaching, ...defaultCache],
    fallbacks: {
        entries: [
            {
                url: '/',
                matcher: ({ request }) => request.mode === 'navigate',
            },
        ],
    },
});

serwist.addEventListeners();

// handle incoming web push messages
self.addEventListener('ppush', (event: PushEvent) => {
    if (!event.data) return;

    let payload: {
        title?: string;
        body?: string;
        notificationId?: string;
        fireReportId?: string;
        type?: string;
        severity?: string;
    };
    try {
        payload = event.data.json();
    } catch {
        return;
    }

    const title = payload.title || 'Fire Away';
    event.waitUntil(
        self.registration.showNotification(title, {
            body: payload.body,
            icon: '/icons/icon-192.png',
            badge: '/icons/icon-192',
            data: { fireReportId: payload.fireReportId, notificationId: payload.notificationId },
        }),
    );
});

// clicking OS-level notification focuses on open tab if there is one, else opens a new one at app's root
self.addEventListener('notificationclick', (event: NotificationEvent) => {
    event.notification.close();
    event.waitUntil(
        self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientsArr) => {
            const existing = clientsArr.find((c) => 'focus' in c) as WindowClient | undefined;
            if (existing) {
                return existing.focus();
            }
            return self.clients.openWindow('/');
        }),
    );
});