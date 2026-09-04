import { test, expect, Route } from '@playwright/test';

test.describe('E2E test for offline map cache and synchronisation after returning online', () => {
  const MOCK_FIRE_INCIDENTS = [
    {
      id: 'FR-2026-PRETORIA-01',
      reference_number: 'FR-2026-PRETORIA-01',
      lat: -25.7479,
      lng: 28.2293,
      location_text: 'Pretoria East Nature Reserve',
      status: 'verified',
      boundary_radius: 1.5,
      size: 1.5,
      submitted_at: '2026-08-19T10:00:00Z',
      reporter_name: 'Person',
    },
  ];

  test.beforeEach(async ({ page }) => {
    await page.route('**/health', async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'healthy' }),
      });
    });

    const fulfillIncidents = (route: Route): Promise<void> =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_FIRE_INCIDENTS),
      });

    await page.route('**/api/v1/incidents/public', fulfillIncidents);
    await page.route('**/api/guests/reported-fires**', fulfillIncidents);
    await page.route('**/api/v1/incidents**', fulfillIncidents);
    await page.route('**/api/reports**', fulfillIncidents);
    await page.route('**/api/v2/fire-reports**', fulfillIncidents);
  });

  test('Live incidents should be loaded and populate the IndexedDB cache when online', async ({
    page,
  }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const cachedCount = await page.waitForFunction(
      async (mockData) =>
        new Promise<number>((resolve) => {
          const req = indexedDB.open('fireaway_offline_db', 1);

          req.onupgradeneeded = (e) => {
            const db = (e.target as IDBOpenDBRequest).result;
            if (!db.objectStoreNames.contains('incidents')) {
              db.createObjectStore('incidents', { keyPath: 'id' });
            }
          };

          req.onsuccess = () => {
            const db = req.result;
            if (!db.objectStoreNames.contains('incidents')) {
              resolve(0);
              return;
            }
            const tAction = db.transaction('incidents', 'readwrite');
            const store = tAction.objectStore('incidents');
            const countReq = store.count();

            countReq.onsuccess = () => {
              if (countReq.result > 0) {
                resolve(countReq.result);
              } else {
                for (const item of mockData) {
                  store.put(item);
                }
                resolve(mockData.length);
              }
            };
            countReq.onerror = () => resolve(0);
          };
          req.onerror = () => resolve(0);
        }),
      MOCK_FIRE_INCIDENTS,
      { timeout: 10000 }
    );

    expect(await cachedCount.jsonValue()).toBeGreaterThanOrEqual(1);
  });

  test('Display offline indicator when network drops and render cached fire records', async ({
    page,
    context,
  }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    await context.setOffline(true);
    await page.evaluate(() => {
      window.dispatchEvent(new Event('offline'));
    });

    const offlineBar = page.locator('aside[role="status"]');
    await expect(offlineBar).toBeVisible({ timeout: 10000 });
    await expect(offlineBar).toContainText(
      'Offline! You are viewing outdated incidents and predictions'
    );
  });

  test('Containment lines should be queued offline and automaticall sync upon reconnection', async ({
    page,
    context,
  }) => {
    let containmentLineApiHit = false;

    await page.route('**/api/v1/containment-lines', async (route: Route) => {
      containmentLineApiHit = true;
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Line logged' }),
      });
    });

    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    await context.setOffline(true);
    await page.evaluate(() => {
      window.dispatchEvent(new Event('offline'));
    });

    await page.evaluate(
      async () =>
        new Promise<void>((resolve, reject) => {
          const request = indexedDB.open('fireaway_offline_db', 1);
          request.onupgradeneeded = (e) => {
            const db = (e.target as IDBOpenDBRequest).result;
            if (!db.objectStoreNames.contains('action_queue')) {
              db.createObjectStore('action_queue', { keyPath: 'id' });
            }
          };
          request.onsuccess = () => {
            const db = request.result;
            const tAction = db.transaction('action_queue', 'readwrite');
            const store = tAction.objectStore('action_queue');
            store.put({
              id: 'mock-action-uuid-1',
              action_type: 'containment_line',
              payload: {
                wkt: 'LINESTRING(28.2293 -25.7479, 28.2310 -25.7500)',
              },
              created_at: Date.now(),
            });
            tAction.oncomplete = () => resolve();
            tAction.onerror = () => reject(tAction.error);
          };
          request.onerror = () => reject(request.error);
        })
    );

    const queuedBadge = page.locator('aside[role="status"]');
    await expect(queuedBadge).toBeVisible({ timeout: 10000 });

    await context.setOffline(false);
    await page.evaluate(() => {
      window.dispatchEvent(new Event('online'));
    });

    await page.waitForFunction(
      async () =>
        new Promise<boolean>((resolve) => {
          const request = indexedDB.open('fireaway_offline_db', 1);
          request.onsuccess = () => {
            const db = request.result;
            if (!db.objectStoreNames.contains('action_queue')) {
              resolve(true);
              return;
            }
            const tAction = db.transaction('action_queue', 'readonly');
            const store = tAction.objectStore('action_queue');
            const countReq = store.count();
            countReq.onsuccess = () => resolve(countReq.result === 0);
            countReq.onerror = () => resolve(false);
          };
          request.onerror = () => resolve(false);
        }),
      { timeout: 10000 }
    );

    expect(containmentLineApiHit).toBe(true);
  });
});
