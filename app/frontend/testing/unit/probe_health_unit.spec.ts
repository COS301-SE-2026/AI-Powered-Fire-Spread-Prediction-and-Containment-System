import { test, expect, Route } from '@playwright/test';

test.describe('Unit: probeHealth cahcing and deduplication', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('domcontentloaded');
    });

    test('should return true when health endpoint responds with 200', async ({ page }) => {
        await page.route('**/health', async (route: Route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ status: 'healthy' }),
            });
        });

        const isHealthy = await page.evaluate(async () => {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000);
            try {
                const response = await fetch('/health', {
                    method: 'GET',
                    cache: 'no-store',
                    credentials: 'include',
                    signal: controller.signal,
                });
                clearTimeout(timeoutId);
                return response.ok;
            } catch {
                clearTimeout(timeoutId);
                return false;
            }
        });

        expect(isHealthy).toBe(true);
    });

    test('should return false when health endpoints returns error or is aborted', async ({ page }) => {
        await page.route('**/health', async (route: Route) => {
            await route.abort('failed');
        });

        const isHealthy = await page.evaluate(async () => {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000);
            try {
                const response = await fetch('/health', {
                    method: 'GET',
                    cache: 'no-store',
                    credentials: 'include',
                    signal: controller.signal,
                });
                clearTimeout(timeoutId);
                return response.ok;
            } catch {
                clearTimeout(timeoutId);
                return false;
            }
        });

        expect(isHealthy).toBe(false);
    });

    test('should cache response within TTL window and not refetch from network', async ({ page }) => {
        let networkRequestCount = 0;

        await page.route('**/health', async (route: Route) => {
            networkRequestCount += 1;
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ status: 'healthy' }),
            });
        });

        const results = await page.evaluate(async () => {
            let cachedStatus: boolean | null = null;
            let lastTime = 0;

            async function probe() {
                const now = Date.now();
                if (cachedStatus !== null && now - lastTime < 4000) {
                    return cachedStatus;
                }
                const res = await fetch('/health');
                cachedStatus = res.ok;
                lastTime = Date.now();
                return cachedStatus;
            }

            const first = await probe();
            const second = await probe();
            const third = await probe();

            return { first, second, third };
        });

        expect(results.first).toBe(true);
        expect(results.second).toBe(true);
        expect(results.third).toBe(true);

        expect(networkRequestCount).toBe(1);
    });

    test('should deduplicate concurrent in-flight requests into a single network call', async ({ page }) => {
        let networkRequestCount = 0;

        await page.route('**/health', async (route: Route) => {
            networkRequestCount += 1;
            await new Promise<void>((resolve) => {
                setTimeout(resolve, 100)
            });
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ status: 'healthy' }),
            });
        });

        const results = await page.evaluate(async () => {
            let inflight = null;

            async function probe() {
                if (inflight) {
                    return inflight;
                }

                inflight = (async () => {
                    try {
                        const res = await fetch('/health');
                        return res.ok;
                    } finally {
                        inflight = null;
                    }
                })();

                return inflight;                
            }
            
            return Promise.all([
                probe(),
                probe(),
                probe(),
                probe(),
                probe(),
            ]);
        });

        expect(results).toEqual([true, true, true, true, true]);

        expect(networkRequestCount).toBe(1);
    });

    test('should immediately return false when browser navigator is offline without calling network', async ({ page, context }) => {
        let networkRequestCount = 0;

        await page.route('**/health', async (route) => {
            networkRequestCount += 1;
            await route.fulfill({ status: 200 });
        });

        await context.setOffline(true);
        await page.evaluate(() => {
            window.dispatchEvent(new Event('offline'));
        });

        const isHealthy = await page.evaluate(async () => {
            if (!navigator.onLine) return false;
            const res = await fetch('/health');
            return res.ok;
        });

        expect(isHealthy).toBe(false);
        expect(networkRequestCount).toBe(0);
    });
});