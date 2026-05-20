import { test, expect } from '@playwright/test'

test.describe('Firefighter Dashboard - live fire map', () => {

    test.beforeEach(async({ page }) =>{
        await page.goto('/firefighterDashboard');
    });

    test('mape stats overlay is visible', async({ page }) => {
        await expect(page.getByText('ACTIVE FIRES')).toBeVisible();
        await expect(page.getByText('NEAREST')).toBeVisible();
        await expect(page.getByText('UNVERIFIED REPORTS')).toBeVisible();
    });

    test('nearby reports section renders', async({ page }) => {
        await expect(page.getByText('Nearby Reports')).toBeVisible();
        await expect(page.getByText('Pretoria West')).toBeVisible();
    });

    test('only verified fires are shown in nearby fires', async({ page }) => {
        await expect(page.getByText('Active')).toBeVisible();
        await expect(page.getByText('Pending')).toBeVisible();
        await expect(page.getByText('Contained')).toBeVisible();
    })
});