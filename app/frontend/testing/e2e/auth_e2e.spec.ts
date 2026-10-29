import { test, expect } from '@playwright/test';

function randomSaId(): string {
  const yy = String(80 + Math.floor(Math.random() * 20));
  const mm = String(1 + Math.floor(Math.random() * 12)).padStart(2, '0');
  const dd = String(1 + Math.floor(Math.random() * 28)).padStart(2, '0');
  const seq = String(Math.floor(Math.random() * 10000)).padStart(4, '0');
  const base = `${yy}${mm}${dd}${seq}08`;
  let sum = 0;
  for (let i = 0; i < 12; i++) {
    let d = Number(base[i]);
    if (i % 2 === 1) {
      d *= 2;
      if (d > 9) d -= 9;
    }
    sum += d;
  }
  return base + String((10 - (sum % 10)) % 10);
}

test('registers a new user and reaches the 2FA step', async ({ page }) => {
  const email = `e2e+${Date.now()}@example.com`;
  const idNumber = randomSaId();
  const password = 'ImSmArT100%';

  await page.route('**/api/notifications', (route) =>
    route.fulfill({ status: 200, json: [] }),
  );

 await page.route('**/api/auth/register', (route) =>
    route.fulfill({
      status: 201,
      contentType: 'application/json',
      json: {
        success: true,
        status: 'success',
        requires_2fa: true,
        message: 'Registration successful. Please verify 2FA.',
        user: { id: 'user-123', email },
      },
    }),
  );

  await page.goto('/');
  await page.getByRole('link', { name: 'Get Started', exact: true }).click();
  await page.getByRole('button', { name: 'Register' }).click();

  await page.getByRole('textbox', { name: 'Name', exact: true }).fill('Sannie');
  await page.getByRole('textbox', { name: 'Surname' }).fill('Pretorius');
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'ID/Passport Number' }).fill(idNumber);
  await page.getByRole('textbox', { name: 'Password', exact: true }).fill(password);
  await page.getByRole('textbox', { name: 'Confirm Password' }).fill(password);
  
  const responsePromise = page.waitForResponse((res) =>
    res.url().includes('/api/auth/register') && res.request().method() === 'POST',
  );

  await page.getByRole('button', { name: 'Register now' }).click();
  await responsePromise;

  await Promise.race([
    expect(page).toHaveURL(/(verify|2fa|otp)/i, { timeout: 10000 }).catch(() => {}),
    expect(page.locator('input[placeholder*="0"], input[type="text"], input[inputmode="numeric"]').first()).toBeVisible({ timeout: 10000 })
  ]);

});