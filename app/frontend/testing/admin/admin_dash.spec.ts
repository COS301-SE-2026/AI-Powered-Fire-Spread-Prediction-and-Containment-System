import { test, expect, type Page } from '@playwright/test';

async function login(page: Page) {
    await page.goto("http://localhost:3000/");
    await page.getByRole("button", { name: "Login" }).click();
    await page.getByRole("textbox", { name: "Email" }).click();
    await page.getByRole("textbox", { name: "Email" }).fill("sipho.n@fireaway.co.za");
    await page.getByRole("textbox", { name: "Password" }).click();
    await page.getByRole("textbox", { name: "Password" }).fill("Password123!");
    await page.getByRole("button", { name: "Login" }).click();
    }
test('Analytics e2e tests, check visibility of all components', async ({ page }) => {
  await login(page);
  await expect(page.getByRole('heading', { name: 'FireAway System Dashboard' })).toBeVisible();
  await expect(page.getByText('Active Fires')).toBeVisible();
  await expect(page.locator('div').filter({ hasText: /^Pending Approvals$/ })).toBeVisible();
  await expect(page.getByText('Total Users')).toBeVisible();
  await expect(page.getByText('System Status')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Recent Activity' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Incidents this week' })).toBeVisible();
  await expect(page.getByText('Predictions completed')).toBeVisible();
  await expect(page.getByText('Model health')).toBeVisible();
  await expect(page.getByText('Avg. prediction confidence')).toBeVisible();
  await expect(page.getByText('Data source sync')).toBeVisible();
});