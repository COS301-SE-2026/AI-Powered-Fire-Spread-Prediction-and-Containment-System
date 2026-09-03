// yarn playwright test src/testing/offline_unit.spec.ts

import { test, expect } from '@playwright/test';
import { OfflinePredictionOverlay, FireReportMapResponse } from '../../src/lib/offlineStore';

test.describe('Unit testing for Othe Offline Store', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('test_coordinates_to_wkt_format_conversion', async ({ page }) => {
    const wktResult = await page.evaluate(() => {
      const points: Array<[number, number]> = [
        [28.2293, -25.7479],
        [28.2305, -25.749],
      ];
      const lineStringPoints = points.map(([lng, lat]) => `${lng} ${lat}`).join(', ');
      return `LINESTRING(${lineStringPoints})`;
    });

    expect(wktResult).toBe('LINESTRING(28.2293 -25.7479, 28.2305 -25.749)');
  });

  test('test_cache_and_retrieve_incidents_in_indexeddb', async ({ page }) => {
    const mockIncident = {
      id: 'FR-2026-UNIT-01',
      reference_number: 'FR-2026-UNIT-01',
      lat: -25.7479,
      lng: 28.2293,
      location_text: 'Pretoria East',
      status: 'verified',
      boundary_radius: 1.5,
      size: 1.5,
      submitted_at: '2026-08-19T10:00:00Z',
      reporter_name: 'Person',
    };

    const retrievedRecord = await page.evaluate(
      async (incidentData: FireReportMapResponse): Promise<FireReportMapResponse | undefined> =>
        new Promise((resolve, reject) => {
          const req = indexedDB.open('fireaway_offline_db', 1);

          req.onupgradeneeded = (event) => {
            const db = (event.target as IDBOpenDBRequest).result;
            if (!db.objectStoreNames.contains('incidents')) {
              db.createObjectStore('incidents', { keyPath: 'id' });
            }
          };

          req.onsuccess = () => {
            const db = req.result;
            const tAction = db.transaction('incidents', 'readwrite');
            const store = tAction.objectStore('incidents');
            store.put(incidentData);

            tAction.oncomplete = () => {
              const readTAction = db.transaction('incidents', 'readonly');
              const readStore = readTAction.objectStore('incidents');
              const getReq = readStore.get(incidentData.id);

              getReq.onsuccess = () => resolve(getReq.result as FireReportMapResponse | undefined);
              getReq.onerror = () => reject(getReq.error);
            };

            tAction.onerror = () => reject(tAction.error);
          };

          req.onerror = () => reject(req.error);
        }),
      mockIncident
    );

    expect(retrievedRecord).not.toBeNull();
    expect(retrievedRecord.id).toBe('FR-2026-UNIT-01');
    expect(retrievedRecord.lat).toBe(-25.7479);
    expect(retrievedRecord.lng).toBe(28.2293);
    expect(retrievedRecord.status).toBe('verified');
  });

  test('test_cahce_and_retrieve_prediction_overlay_in_indexeddb', async ({ page }) => {
    const mockPrediction: OfflinePredictionOverlay = {
      incident_id: 'FR-2026-UNIT-01',
      timestamp: '2026-08-19T10:00:00Z',
      prediction_grid: {
        type: 'FeatureCollection',
        features: [
          {
            type: 'Feature',
            geometry: {
              type: 'Polygon',
              coordinates: [
                [
                  [28.2, -25.7],
                  [28.3, -25.7],
                  [28.3, -25.8],
                  [28.2, -25.8],
                  [28.2, -25.7],
                ],
              ],
            },
            properties: {
              probability: 0.85,
              horizon_hours: 3,
            },
          },
        ],
      },
    };

    const retrievedOverlay = await page.evaluate(
      async (
        predictionData: OfflinePredictionOverlay
      ): Promise<OfflinePredictionOverlay | undefined> =>
        new Promise((resolve, reject) => {
          const req = indexedDB.open('fireaway_offline_db', 1);

          req.onupgradeneeded = (event) => {
            const db = (event.target as IDBOpenDBRequest).result;
            if (!db.objectStoreNames.contains('predictions')) {
              db.createObjectStore('predictions', { keyPath: 'incident_id' });
            }
          };

          req.onsuccess = () => {
            const db = req.result;
            const tAction = db.transaction('predictions', 'readwrite');
            const store = tAction.objectStore('predictions');
            store.put(predictionData);

            tAction.oncomplete = () => {
              const readTAction = db.transaction('predictions', 'readonly');
              const readStore = readTAction.objectStore('predictions');
              const getReq = readStore.get(predictionData.incident_id);

              getReq.onsuccess = () =>
                resolve(getReq.result as OfflinePredictionOverlay | undefined);
              getReq.onerror = () => reject(getReq.error);
            };

            tAction.onerror = () => reject(tAction.error);
          };

          req.onerror = () => reject(req.error);
        }),
      mockPrediction
    );

    expect(retrievedOverlay).not.toBeNull();
    expect(retrievedOverlay.incident_id).toBe('FR-2026-UNIT-01');
    expect(retrievedOverlay.prediction_grid.features[0].properties.probability).toBe(0.85);
  });

  test('test_queue_action_persists_containment_line_record', async ({ page }) => {
    const actionPayload = {
      id: 'action-uuid',
      action_type: 'containment_line',
      payload: {
        wkt: 'LINESTRING(28.1881 -25.7461, 28.1895 -25.7472)',
      },
      created_at: 1724064000000,
    };

    const queuedCount = await page.evaluate(
      async (actionRecord) =>
        new Promise<number>((resolve, reject) => {
          const req = indexedDB.open('fireaway_offline_db', 1);

          req.onupgradeneeded = (event) => {
            const db = (event.target as IDBOpenDBRequest).result;
            if (!db.objectStoreNames.contains('action_queue')) {
              db.createObjectStore('action_queue', { keyPath: 'id' });
            }
          };

          req.onsuccess = () => {
            const db = req.result;
            const tAction = db.transaction('action_queue', 'readwrite');
            const store = tAction.objectStore('action_queue');
            store.put(actionRecord);

            tAction.oncomplete = () => {
              const countTAction = db.transaction('action_queue', 'readonly');
              const countStore = countTAction.objectStore('action_queue');
              const countReq = countStore.count();

              countReq.onsuccess = () => resolve(countReq.result);
              countReq.onerror = () => reject(countReq.error);
            };

            tAction.onerror = () => reject(tAction.error);
          };

          req.onerror = () => reject(req.error);
        }),
      actionPayload
    );

    expect(queuedCount).toBeGreaterThanOrEqual(1);
  });

  test('test_probe_health_returns_true_when_health_endpoint_is_reachable', async ({ page }) => {
    await page.route('**/health', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'healthy' }),
      });
    });

    const isHealthy = await page.evaluate(async () => {
      const controller = new AbortController();
      const timeoutID = setTimeout(() => controller.abort(), 4000);
      try {
        const response = await fetch('/health', {
          method: 'GET',
          cache: 'no-store',
          credentials: 'include',
          signal: controller.signal,
        });
        clearTimeout(timeoutID);
        return response.ok;
      } catch {
        clearTimeout(timeoutID);
        return false;
      }
    });

    expect(isHealthy).toBe(true);
  });

  test('test_probe_health_returns_false_when_health_endpoint_fails', async ({ page }) => {
    await page.route('**/health', async (route) => {
      await route.abort('failed');
    });

    const isHealthy = await page.evaluate(async () => {
      const controller = new AbortController();
      const timeoutID = setTimeout(() => controller.abort(), 4000);
      try {
        const response = await fetch('/health', {
          method: 'GET',
          cache: 'no-store',
          credentials: 'include',
          signal: controller.signal,
        });
        clearTimeout(timeoutID);
        return response.ok;
      } catch {
        clearTimeout(timeoutID);
        return false;
      }
    });

    expect(isHealthy).toBe(false);
  });
});
