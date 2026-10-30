import { test, expect } from '@playwright/test';

const tinyPng = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  'base64',
);

test.describe('report a fire journey', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test('guest can report a fire with a description and image', async ({
    page,
  }) => {
    await page.addInitScript(() => {
      document.addEventListener('DOMContentLoaded', () => {
        const style = document.createElement('style');
        style.textContent =
          'nextjs-portal { display: none !important; }';
        document.head.appendChild(style);
      });
    });

    await page.route('**/health', route =>
      route.fulfill({
        status: 200,
        json: { status: 'ok' },
      }),
    );

    let uploadCalled = false;

    await page.route('**/api/uploads/photo', route => {
      uploadCalled = true;

      return route.fulfill({
        status: 201,
        json: {
          object_key: 'fire.png',
        },
      });
    });

    let submittedBody = '';
    let reportRequestHit = false;

    await page.route('**/api/**/reported-fires', async route => {
      if (route.request().method() === 'POST') {
        reportRequestHit = true;
        submittedBody = route.request().postData() || '';

        await route.fulfill({
          status: 201,
          json: {
            id: 'test-1',
            reference_number: 'TEST-001',
          },
        });

        return;
      }

      await route.continue();
    });

    await page.goto('/');

    await page
      .getByRole('link', {
        name: 'Get Started',
        exact: true,
      })
      .click();

    await page.getByRole('button', {
      name: 'Sign in as Guest',
    }).click();

    await page.getByRole('link', {
      name: 'Report a fire',
    }).click();

    await expect(page).toHaveURL(/\/guests\/report-fire/);

    const map = page.getByRole('region', {
      name: 'Map',
    });

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

    await page.getByRole('button', {
      name: 'Submit Fire Report',
    }).click();

    await expect
      .poll(() => reportRequestHit)
      .toBe(true);

    expect(uploadCalled).toBe(true);
    expect(reportRequestHit).toBe(true);

    expect(submittedBody).not.toBe('');
    expect(submittedBody).toContain('Big fire');
  });
});
