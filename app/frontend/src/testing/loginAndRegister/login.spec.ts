import { test, expect } from "@playwright/test";

/* 

test.describe("Login Flow", () => {
  test("successful login redirects to dashboard", async ({ page }) => {
    // First register a user (using the registration flow)
    const email = `test-${Date.now()}@example.com`;
    await page.goto("/register");
    await page.fill('input[name="name"]', "John");
    await page.fill('input[name="surname"]', "Doe");
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="idNumber"]', "12345678");
    await page.fill('input[name="password"]', "Test123!");
    await page.selectOption('select[name="role"]', "User");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/login\?registered=true/);

    // Now login
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', "Test123!");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/dashboard");
  });

*/

test.describe("Login Flow", () => {

  test("guest login redirects to dashboard", async ({ page }) => {
    await page.goto("/login");
    await page.click('button:has-text("Sign in as Guest")');
    await expect(page).toHaveURL("/guests/guestsLanding");
  });
});