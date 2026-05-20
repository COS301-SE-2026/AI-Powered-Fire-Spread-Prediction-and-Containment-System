# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Authentication Flow >> login with non-existent user shows error
- Location: testing_config/e2e/auth.spec.ts:31:7

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('.bg-red-500\\/10')
Expected substring: "Incorrect email or password"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toContainText" with timeout 5000ms
  - waiting for locator('.bg-red-500\\/10')

```

```yaml
- heading "Welcome back" [level=2]
- text: Email
- textbox "Email":
  - /placeholder: example@something.co.za
  - text: nonexistent@example.com
- text: Password
- textbox "Password":
  - /placeholder: ••••••••
  - text: wrong
- button "Logging in..." [disabled]
- link "Register":
  - /url: /register
- button "Sign in as Guest"
- link "Forgot password?":
  - /url: /forgot-password
- text: •
- link "Can't log in?":
  - /url: /cant-login
- alert
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Authentication Flow', () => {
  4  |   test('register, login, and access dashboard (without 2FA)', async ({ page }) => {
  5  |     const email = `test-${Date.now()}@example.com`;
  6  |     const password = 'Test123!';
  7  | 
  8  |     // 1. Register
  9  |     await page.goto('/register');
  10 |     await page.fill('input[name="name"]', 'John');
  11 |     await page.fill('input[name="surname"]', 'Doe');
  12 |     await page.fill('input[name="email"]', email);
  13 |     await page.fill('input[name="idNumber"]', '12345678');
  14 |     await page.fill('input[name="password"]', password);
  15 |     await page.selectOption('select[name="role"]', 'User');
  16 |     await page.click('button[type="submit"]');
  17 | 
  18 |     // Wait for redirect to login with success query param
  19 |     await expect(page).toHaveURL(/login\?registered=true/);
  20 | 
  21 |     // 2. Login
  22 |     await page.fill('input[type="email"]', email);
  23 |     await page.fill('input[type="password"]', password);
  24 |     await page.click('button[type="submit"]');
  25 | 
  26 |     // If 2FA is not enabled, should go to dashboard
  27 |     await expect(page).toHaveURL('/dashboard');
  28 |     await expect(page.locator('h1')).toContainText('Dashboard');
  29 |   });
  30 | 
  31 |   test('login with non-existent user shows error', async ({ page }) => {
  32 |     await page.goto('/login');
  33 |     await page.fill('input[type="email"]', 'nonexistent@example.com');
  34 |     await page.fill('input[type="password"]', 'wrong');
  35 |     await page.click('button[type="submit"]');
> 36 |     await expect(page.locator('.bg-red-500\\/10')).toContainText('Incorrect email or password');
     |                                                    ^ Error: expect(locator).toContainText(expected) failed
  37 |   });
  38 | 
  39 |   test('guest login redirects to dashboard', async ({ page }) => {
  40 |     await page.goto('/login');
  41 |     await page.click('button:has-text("Sign in as Guest")');
  42 |     await expect(page).toHaveURL('/dashboard');
  43 |   });
  44 | });
  45 | 
```