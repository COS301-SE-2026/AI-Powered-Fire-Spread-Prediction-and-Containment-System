import { test, expect } from '@playwright/test';

test.describe('Auth Rate Limiting UI', () => {
    test('Display rate limit warning when recieve HTTP 429', async ({ page }) => {
        // intercept login route
        await page.route('**/auth/login*', async (route) => {
            await route.fulfill({
                status: 429,
                contentType: 'application/json',
                body: JSON.stringify({
                    detail: 'Incorrect credentials. Please wait 30  seconds before retrying to login.',
                }),
            });
        });

        await page.goto('/login');
        await page.fill('#email', 'user@example.com');
        await page.fill('#password', 'WrongPassword123');
        await page.click('button[type="submit"]');

        const apiErrorBox = page.locator('.text-flare.text-sm');
        await expect(apiErrorBox).toBeVisible({ timeout: 5000});
        await expect(apiErrorBox).toContainText('30 seconds');

        const submitButton = page.locator('button[type="submit"]');
        await expect(submitButton).toBeDisabled();
        await expect(submitButton).toContainText(/Try again in \d+s/);
    });
});