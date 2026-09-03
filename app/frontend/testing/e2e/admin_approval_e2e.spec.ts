// // NOTE: This e2e test is using mock data for now until we have a proper db setup.
// // Once proper db is setup, the proper endpoints will be subbed in

// import { test, expect, Page } from '@playwright/test';

// async function login(page: Page) {
//   await page.goto('http://localhost:3000/');
//   await page.getByRole('button', { name: 'Login' }).click();
//   await page.getByRole('textbox', { name: 'Email' }).click();
//   await page.getByRole('textbox', { name: 'Email' }).fill('sipho.n@fireaway.co.za');
//   await page.getByRole('textbox', { name: 'Password' }).click();
//   await page.getByRole('textbox', { name: 'Password' }).fill('Password123!');
//   await page.getByRole('button', { name: 'Login' }).click();
//   await page.waitForURL('**/admin/**', { timeout: 15000 });
// }
// test('test', async ({ page }) => {
//   await login(page);
//   await page.locator('aside').hover();
//   await page.getByRole('link', { name: 'Role Approvals' }).click();
//   await expect(page.getByRole('heading', { name: 'Role Approvals' })).toBeVisible();
//   await expect(page.getByRole('columnheader', { name: 'Name' })).toBeVisible();
//   await page.getByRole('button', { name: 'pending' }).click();
//   await expect(page.getByText('pending').nth(1)).toBeVisible();
//   await page.getByRole('button', { name: 'approved' }).click();
//   await expect(page.getByText('approved').nth(1)).toBeVisible();
//   await page.getByRole('button', { name: 'rejected' }).click();
//   await expect(page.getByText('rejected').nth(1)).toBeVisible();
//   await page.getByRole('button', { name: 'revoked' }).click();
//   await expect(page.getByText('revoked').nth(1)).toBeVisible();
// });
