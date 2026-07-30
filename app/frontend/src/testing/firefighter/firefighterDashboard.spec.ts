import { test, expect } from '@playwright/test'

test.describe('Firefighter Dashboard - live fire map', () => {

    test.beforeEach(async({ page }) =>{
        await page.goto('http://localhost:3000/');
        await page.getByRole('button', { name: 'Login' }).click();
        await page.getByRole('textbox', { name: 'Email' }).click();
        await page.getByRole('textbox', { name: 'Email' }).fill('thandiwe.k@fireaway.co.za');
        await page.getByRole('textbox', { name: 'Email' }).press('Tab');
        await page.getByRole('textbox', { name: 'Password' }).fill('Password123!');
        await page.getByRole('button', { name: 'Login' }).click();
    });
    test('nearby reports section renders', async({ page }) => {
        await expect(page.getByText('Nearby Reports')).toBeVisible();
    });

    test('Map renders', async ({ page }) => {
        await expect(page.getByRole('region', { name: 'Map' })).toBeVisible();
    })

    test('All quick action map overlay stats are rendered', async ({page}) => {
        await expect(page.getByText('Active Fires')).toBeVisible();
        await expect(page.getByText('Nearest')).toBeVisible();
        await expect(page.getByText('Unverified Reports')).toBeVisible();
        await expect(page.getByText('LIVE FIRE MAPClear Lines')).toBeVisible();
    })

    test('All quick action buttons are rendered', async ({page}) => {
        await expect(page.getByRole('button', { name: 'View all reports View team on' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Report a fire New fire' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Log containment line Draw' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Simulate fires View AI' })).toBeVisible();
    })

    test('All environment variables are rendered', async ({page}) => {
        await expect(page.locator('.lucide.lucide-wind > path:nth-child(3)')).toBeVisible();
        await expect(page.locator('.lucide.lucide-thermometer > path')).toBeVisible();
        await expect(page.locator('.lucide.lucide-flame > path')).toBeVisible();
        await expect(page.locator('.lucide.lucide-droplets')).toBeVisible();

    })
});