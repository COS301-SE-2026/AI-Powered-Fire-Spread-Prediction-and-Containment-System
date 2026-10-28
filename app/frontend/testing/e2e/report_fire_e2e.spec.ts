import { test, expect } from '@playwright/test';

const tinyPng = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  'base64',
);

test.describe('report a fire journey', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test('guest can report a fire with a description and image', async ({ page }) => {
    await page.addInitScript(() => {
      document.addEventListener('DOMContentLoaded', () => {
        const style = document.createElement('style');
        style.textContent = 'nextjs-portal { display: none !important; }';
        document.head.appendChild(style);
      });
    });

    await page.route('**/health', route =>
      route.fulfill({
        status: 200,
        json: { status: 'ok' },
      }),
    );

    await page.route('**/api/uploads/photo', route =>
      route.fulfill({
        status: 201,
        json: {
          id: 'photo-1',
          url: '/fire.png',
        },
      }),
    );

    let submittedBody = '';

    await page.route('**/api/**/reported-fires', async route => {
      if (route.request().method() === 'POST') {
        submittedBody = route.request().postData() || '';

        await route.fulfill({
          status: 201,
          json: {
            id: 'test-1',
          },
        });

        return;
      }

      await route.continue();
    });

    await page.goto('/');

    await page.getByRole('link', {
      name: 'Get Started',
      exact: true,
    }).click();

    await page.getByRole('button', {
      name: 'Sign in as Guest',
    }).click();

    await page.getByRole('link', {
      name: 'Report a fire',
    }).click();

    await expect(page).toHaveURL(/\/guests\/report-fire/);

    const map = page.getByRole('region', { name: 'Map' });

    await expect(map).toBeVisible();

    await map.click({
      position: {
        x: 533,
        y: 156,
      },
    });

    await page
      .getByRole('textbox', { name: 'Description' })
      .fill('Big fire');

    await page.locator('input[type="file"]').setInputFiles({
      name: 'fire.png',
      mimeType: 'image/png',
      buffer: tinyPng,
    });

    const [response] = await Promise.all([
      page.waitForResponse(
        res =>
          res.url().includes('/reported-fires') &&
          res.request().method() === 'POST',
      ),
      page.getByRole('button', { name: /submit/i }).click(),
    ]);

    expect(response.ok()).toBeTruthy();
    expect(submittedBody).not.toBe('');
    expect(submittedBody).toContain('Big fire');
  });
});