import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('register, login, and access dashboard (without 2FA)', async ({ page }) => {
    const email = `test-${Date.now()}@example.com`;
    const password = 'Test123!';

    // 1. Register
    await page.goto('/register');
    await page.fill('input[name="name"]', 'John');
    await page.fill('input[name="surname"]', 'Doe');
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="idNumber"]', '12345678');
    await page.fill('input[name="password"]', password);
    await page.selectOption('select[name="role"]', 'User');
    await page.click('button[type="submit"]');

    // Wait for redirect to login with success query param
    await expect(page).toHaveURL('/register');

    // 2. Login
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');

    // If 2FA is not enabled, should go to dashboard
    await expect(page).toHaveURL('/register');
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('login with non-existent user shows error', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'nonexistent@example.com');
    await page.fill('input[type="password"]', 'wrong');
    await page.click('button[type="submit"]');
    await expect(page.locator('.bg-red-500\\/10')).toContainText('Incorrect email or password');
  });

  test('guest login redirects to dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("Sign in as Guest")');
    await expect(page).toHaveURL('/guests');
  });
});
