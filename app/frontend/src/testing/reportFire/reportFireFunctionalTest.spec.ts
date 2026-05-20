import { test, expect } from '@playwright/test';

test.describe('Report Fire page', () => {
  test('submits, shows reference/status, and resets', async ({ page }) => {
    // Mock Mapbox autocomplete
    await page.route(/api\.mapbox\.com\/geocoding\/v5\/mapbox\.places\/.*\.json/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          features: [
            { place_name: 'Corner of 5th Ave and Pine St', center: [-122.335167, 47.608013] },
          ],
        }),
      });
    });

    await page.goto('/reportfire');

    // Location must be selected, not just typed
    const locationInput = page.getByPlaceholder('Drop a pin or type your address');
    await locationInput.fill('Corner of 5th Ave');
    await page.getByRole('button', { name: 'Corner of 5th Ave and Pine St' }).click();

    // Description
    await page
      .getByPlaceholder('E.g., Surface line fire spreading northeast toward residential properties...')
      .fill('Brush fire near the treeline, moderate wind.');

    // Photo (required on desktop)
    await page.locator('input[type="file"]').setInputFiles('app/frontend/src/testing/fixtures/fire.jpg');

    // Submit
    await page.getByRole('button', { name: 'Submit Fire Report' }).click();

    // Status + reference number
    await expect(page.getByText('Report submitted')).toBeVisible();
    await expect(page.getByText(/Ref #FW-/)).toBeVisible();

    // If you want "Verified" done, the app must set statusIndex >= 2
    // await expect(page.getByText('Verified')).toBeVisible();

    // Reset assertions (form clears immediately)
    await expect(locationInput).toHaveValue('Click the map to drop a pin');
    await expect(
      page.getByPlaceholder('E.g., Surface line fire spreading northeast toward residential properties...')
    ).toHaveValue('');
  });
});