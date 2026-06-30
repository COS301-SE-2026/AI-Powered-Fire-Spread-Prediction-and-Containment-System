import { test, expect } from "@playwright/test";

test.describe("Registration Flow", () => {
  test("complete register process as User", async ({ page }) => {
    const email = `test-${Date.now()}@example.com`;
    await page.goto("/register");
    await page.fill('input[name="name"]', "John");
    await page.fill('input[name="surname"]', "Doe");
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="idNumber"]', "12345678");
    await page.fill('input[name="password"]', "Test123!");
    await page.selectOption('select[name="role"]', "User");
    await expect(page.locator('input[name="licenceNumber"]')).toBeHidden();
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/register");
  });

  test("register as Firefighter shows licence field", async ({ page }) => {
    await page.goto("/register");
    await page.selectOption('select[name="role"]', "Firefighter");
    await expect(page.locator('input[name="licenceNumber"]')).toBeVisible();
    const email = `fire-${Date.now()}@example.com`;
    await page.fill('input[name="name"]', "Jane");
    await page.fill('input[name="surname"]', "Firefighter");
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="idNumber"]', "87654321");
    await page.fill('input[name="licenceNumber"]', "FF-12345");
    await page.fill('input[name="password"]', "Fire123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/register');
  });

  test('shows "Email already registered" error on duplicate email', async ({ page }) => {
    await page.route('**/api/register', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Email already registered' }),
      });
    });
    await page.goto('/register');
    await page.fill('input[name="name"]', 'Test');
    await page.fill('input[name="surname"]', 'User');
    await page.fill('input[name="email"]', 'duplicate@example.com');
    await page.fill('input[name="idNumber"]', '0123456789123'); 
    await page.fill('input[name="password"]', 'ValidPass123');  
    await page.fill('input[name="confirmPassword"]', 'ValidPass123');
    await page.click('button[type="submit"]');
    const errorDiv = page.locator('.bg-flare\\/10');
    await expect(errorDiv).toBeVisible();
    await expect(errorDiv).toContainText('Email already registered');
    await expect(page).toHaveURL('/register');
  });
});