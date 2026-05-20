# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Authentication Flow >> register, login, and access dashboard (without 2FA)
- Location: testing_config/e2e/auth.spec.ts:4:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: expect(page).toHaveURL(expected) failed

Expected pattern: /login\?registered=true/
Received string:  "http://localhost:3000/register"
Timeout: 5000ms

Call log:
  - Expect "toHaveURL" with timeout 5000ms
    14 × unexpected value "http://localhost:3000/register"

```

```yaml
- heading "Create account" [level=2]
- text: Name
- textbox "Name": John
- text: Surname
- textbox "Surname": Doe
- text: Email
- textbox "Email": test-1779297413734@example.com
- text: ID/Passport Number
- textbox "ID/Passport Number": "12345678"
- text: Password
- textbox "Password": Test123!
- text: Role
- combobox "Role":
  - option "User" [selected]
  - option "Firefighter"
- button "Registering..." [disabled]
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
> 19 |     await expect(page).toHaveURL(/login\?registered=true/);
     |                        ^ Error: expect(page).toHaveURL(expected) failed
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
  36 |     await expect(page.locator('.bg-red-500\\/10')).toContainText('Incorrect email or password');
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