const { test, expect } = require('@playwright/test');

test('should load the homepage', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Fire Spread Prediction/);
  await expect(page.locator('text=Fire Spread Prediction')).toBeVisible();
});
