import { test, expect } from '@playwright/test';

test.describe('Report Fire page', () => {
  test('submits, shows status/reference, resets form but keeps status, generates new ref on next submission', async ({ page }) => {
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

    // ─── FIRST SUBMISSION ───
    const locationInput = page.getByPlaceholder('Drop a pin or type your address');
    const descriptionInput = page.getByPlaceholder('E.g., Surface line fire spreading northeast toward residential properties...');

    await locationInput.fill('Corner of 5th Ave');
    await page.getByRole('button', { name: 'Corner of 5th Ave and Pine St' }).click();
    await descriptionInput.fill('Brush fire near the treeline, moderate wind.');
    await page.locator('input[type="file"]').setInputFiles('app/frontend/src/testing/fixtures/fire.jpg');

    await page.getByRole('button', { name: 'Submit Fire Report' }).click();

    // Capture first reference number
    const firstRefMatch = await page.locator('text=/Ref #FW-/').textContent();
    const firstRef = firstRefMatch?.match(/FW-[\w-]+/)?.[0];

    await expect(page.getByText('Report submitted')).toBeVisible();
    await expect(page.getByText(`Ref #${firstRef}`)).toBeVisible();

    // Wait for form reset (1s timeout in handleSubmit)
    await page.waitForTimeout(1100);

    // Form should be cleared, but status should still be visible
    await expect(locationInput).toHaveValue('Click the map to drop a pin');
    await expect(descriptionInput).toHaveValue('');
    await expect(page.getByText(`Ref #${firstRef}`)).toBeVisible(); // Status persists

    // ─── SECOND SUBMISSION ───
    await locationInput.fill('5th Ave and Elm');
    await page.getByRole('button', { name: 'Corner of 5th Ave and Pine St' }).click(); // Mock returns same result
    await descriptionInput.fill('Different fire location, spreading rapidly.');
    await page.locator('input[type="file"]').setInputFiles('app/frontend/src/testing/fixtures/fire.jpg');

    await page.getByRole('button', { name: 'Submit Fire Report' }).click();

    // Capture second reference number
    const secondRefMatch = await page.locator('text=/Ref #FW-/').textContent();
    const secondRef = secondRefMatch?.match(/FW-[\w-]+/)?.[0];

    // Verify new ref is different from first
    await expect(firstRef).not.toBe(secondRef);
    await expect(page.getByText(`Ref #${secondRef}`)).toBeVisible();
    await expect(page.getByText('Report submitted')).toBeVisible();
  });
});