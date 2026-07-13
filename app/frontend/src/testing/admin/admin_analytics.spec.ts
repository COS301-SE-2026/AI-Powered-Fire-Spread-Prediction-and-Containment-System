import { test, expect } from '@playwright/test';

test('Analytics e2e tests, check visibility of all components', async ({ page }) => {
  await page.goto('/admin/analytics');
  await expect(page.getByText('Total Users20')).toBeVisible();
  await expect(page.getByText('Pending Role Requests7')).toBeVisible();
  await expect(page.getByText('Total Firefighters5')).toBeVisible();
  await expect(page.getByText('Total Admins3')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Pending Role Requests' }).nth(1)).toBeVisible();
  await page.getByRole('link', { name: 'Manage all' }).click();
  await expect(page.getByRole('heading', { name: 'Role Approvals' })).toBeVisible();
});