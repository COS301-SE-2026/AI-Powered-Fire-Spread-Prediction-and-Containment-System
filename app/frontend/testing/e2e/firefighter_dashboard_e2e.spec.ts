import { test, expect, Page, Locator } from '@playwright/test';

const EMAIL = process.env.E2E_FIREFIGHTER_EMAIL || 'thandiwe.k@fireaway.co.za';
const PASSWORD = process.env.E2E_FIREFIGHTER_PASSWORD;

async function login(page: Page) {
  await page.goto('/');
  await page.getByRole('link', { name: 'Get started with FireAway' }).click();
  await page.getByRole('button', { name: 'Login' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill(EMAIL);
  await page.getByRole('textbox', { name: 'Password' }).fill(PASSWORD as string);
  await page.getByRole('button', { name: 'Login' }).click();
}

async function toggleAndExpectFlip(toggle: Locator) {
  const before = await toggle.getAttribute('aria-checked');
  let expected = 'true';
  if (before === 'true') {
    expected = 'false';
  }
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-checked', expected);
}

test.describe('firefighter dashboard', () => {
  test.skip(!PASSWORD, 'Set E2E_FIREFIGHTER_PASSWORD to run this test');

  test.use({
    viewport: { width: 1280, height: 720 },
    geolocation: { latitude: -25.7479, longitude: 28.2293 },
    permissions: ['geolocation'],
  });

  test('firefighter can use the map, layers and containment line tool', async ({ page }) => {
    await login(page);
    await page.getByRole('button', { name: 'Dismiss' }).click();

    const water = page.getByRole('switch', { name: 'Show Water' });
    await toggleAndExpectFlip(water);
    await toggleAndExpectFlip(water);

    const resources = page.getByRole('switch', { name: 'Show Resources' });
    await toggleAndExpectFlip(resources);
    await toggleAndExpectFlip(resources);

    await page.getByRole('button', { name: /Jacaranda Drive/ }).click();
    await page.getByRole('button', { name: /Silver Lakes Boundary/ }).click();
    await page.getByRole('button', { name: /Water Tank/ }).first().click();
    await page.getByRole('button', { name: 'Center map location on me' }).click();

    const map = page.getByRole('region', { name: 'Map' });
    await page.getByRole('button', { name: 'Log containment line Draw' }).click();
    await map.click({ position: { x: 342, y: 326 } });
    await map.dblclick({ position: { x: 486, y: 254 } });

    await page.getByRole('img', { name: 'Map marker' }).first().click();

    await page.goto('/firefighter/simulation');
    await expect(page).toHaveURL(/\/firefighter\/simulation/);
  });
});