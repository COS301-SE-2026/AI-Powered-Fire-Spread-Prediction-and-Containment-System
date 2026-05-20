import { test, expect } from '@playwright/test';

test('user can report a fire with location, description, and photo', async ({ page }) => {
  await page.goto('/report-fire'); // update to the actual route

  await page.getByTestId('fire-location').fill('Corner of 5th Ave and Pine St');
  await page.getByTestId('fire-description').fill('Brush fire near the treeline, moderate wind.');

  await page.getByTestId('fire-photo').setInputFiles('app/frontend/src/testing/fixtures/fire.jpg');

  await page.getByRole('button', { name: 'Submit report' }).click();

  await expect(page.getByText('Report submitted')).toBeVisible();
});