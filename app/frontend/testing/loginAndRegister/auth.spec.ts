import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {

  test('login with non-existent user shows error', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    await page.getByRole('button', { name: 'Login' }).click();
    await page.getByRole('textbox', { name: 'Email' }).click();
    await page.getByRole('textbox', { name: 'Email' }).fill('wawa@bla.com');
    await page.getByRole('textbox', { name: 'Email' }).press('Tab');
    await page.getByRole('textbox', { name: 'Password' }).fill('kakakaka');
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(page.getByText('Email incorrect please enter')).toBeVisible();
});

  test('guest login redirects to dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: 'Sign in as Guest' }).click();
    await expect(page).toHaveURL('/guests/live-map');
  });
});
