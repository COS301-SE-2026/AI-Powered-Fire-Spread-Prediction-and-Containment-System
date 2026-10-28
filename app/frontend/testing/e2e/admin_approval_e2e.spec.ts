import { test, expect, Page } from '@playwright/test';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'sipho.n@fireaway.co.za';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD;

const STATUSES = ['pending', 'approved', 'rejected', 'revoked'];

async function login(page: Page) {
  await page.goto('/');
  await page.getByRole('link', { name: 'Get Started', exact: true }).click();
  await page.getByRole('button', { name: 'Login' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill(ADMIN_EMAIL);
  await page.getByRole('textbox', { name: 'Password' }).fill(ADMIN_PASSWORD as string);
  await page.getByRole('button', { name: 'Login' }).click();
  await page.waitForURL('**/admin/**', { timeout: 15000 });
}

test.describe('admin role approvals', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test.skip(!ADMIN_PASSWORD, 'Set E2E_ADMIN_PASSWORD to run this test');

  test('admin can filter role requests by status', async ({ page }) => {
    await login(page);

    await page.locator('aside').hover();
    await page.getByRole('link', { name: 'Role Approvals' }).click();

    await expect(page.getByRole('heading', { name: 'Role Approvals' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Name' })).toBeVisible();

    for (const status of STATUSES) {
      await page.getByRole('button', { name: status, exact: true }).click();
      await expect(
        page.getByRole('row').filter({ hasText: status }).first(),
      ).toBeVisible();
    }
  });
});