import { test, expect } from '@playwright/test';

test.describe('Report Fire page', () => {
  test('submits, shows status/reference, resets form but keeps status, generates new ref on next submission', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  await page.getByRole('button', { name: 'Login' }).click();
  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill('amahle.d@fireaway.co.za');
  await page.getByRole('textbox', { name: 'Password' }).click();
  await page.getByRole('textbox', { name: 'Password' }).fill('Password123!');
  await page.getByRole('button', { name: 'Login' }).click();
  await page.getByRole('link', { name: 'Report a Fire' }).click();
  await page.getByRole('textbox', { name: 'Drop a pin or type your' }).click();
  await page.getByRole('textbox', { name: 'Drop a pin or type your' }).fill('Pretoria');
  await page.getByRole('button', { name: 'Pretoria, Gauteng, South Africa', exact: true }).click();
  await page.getByRole('textbox', { name: 'Description' }).click();
  await page.getByRole('textbox', { name: 'Description' }).fill('HUGE FIRE');
  await page.getByRole('button', { name: 'Attach Image' }).click();
  await page.locator('input[type="file"]').setInputFiles('logo-small.png');
  await page.getByRole('button', { name: 'Submit Fire Report' }).click();
  await expect(page.getByText('Report submitted #FR-2026-')).toBeVisible();
  await page.getByRole('textbox', { name: 'Drop a pin or type your' }).click();
  await page.getByRole('textbox', { name: 'Drop a pin or type your' }).fill('Johannesburg');
  await page.getByRole('button', { name: 'Johannesburg, Gauteng, South Africa', exact: true }).click();
  await page.getByRole('textbox', { name: 'Description' }).click();
  await page.getByRole('textbox', { name: 'Description' }).fill('ANOTHER MASSIVE FIRE');
  await page.getByRole('region', { name: 'Map' }).click();
  await page.getByText('+').click();
  await page.getByRole('region', { name: 'Map' }).press('Tab');
  await expect(page.getByText('+')).toBeVisible();
  await page.getByRole('button', { name: 'Submit Fire Report' }).click();
  await expect(page.getByText('Field evidence attachment is')).toBeVisible();
  await page.getByRole('button', { name: 'Attach Image' }).click();
  await page.locator('input[type="file"]').setInputFiles('logo-small.png');
  await page.getByRole('button', { name: 'Submit Fire Report' }).click();
});
});