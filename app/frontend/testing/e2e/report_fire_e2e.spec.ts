import { test, expect } from '@playwright/test';

const tinyPng = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  'base64',
);

test.describe('report a fire journey', () => {
    test.use({ viewport: { width: 1280, height: 720 } });
    
    test('guest can report a fire with a description and image', async ({ page }) => {
        page.on('request', (req) => {
            if (req.method() !== 'GET') {
                console.log('REQUEST', req.method(), req.url());
            }
        });
        
        page.on('requestfailed', (req) => {
            console.log('FAILED', req.url(), req.failure()?.errorText);
            });

        await page.route('**/api/**', async (route) => {
            if (route.request().method() === 'POST') {
                await route.fulfill({ status: 201, json: { id: 'test-1' } });
            } else {
                await route.continue();
            }
    });

    await page.goto('/');

    await page.getByRole('link', { name: 'Get Started', exact: true }).click();
    await page.getByRole('button', { name: 'Sign in as Guest' }).click();

    await page.getByRole('link', { name: 'Report a fire' }).click();
    await expect(page).toHaveURL(/\/guests\/report-fire/);

    const map = page.getByRole('region', { name: 'Map' });
    await expect(map).toBeVisible();
    await map.click({ position: { x: 533, y: 156 } });

    await page.getByRole('textbox', { name: 'Description' }).fill('Big fire');

    await page.locator('input[type="file"]').setInputFiles({
      name: 'fire.png',
      mimeType: 'image/png',
      buffer: tinyPng,
    });

    const responsePromise = page.waitForResponse(
      (res) => res.url().includes('/api/') && res.request().method() === 'POST',
    );
    await page.getByRole('button', { name: 'Submit Fire Report' }).click();
    const response = await responsePromise;
    expect(response.ok()).toBeTruthy();

    await expect(page.getByText(/Report submitted #FR-\d{4}-\d+/).first()).toBeVisible();
  });
});