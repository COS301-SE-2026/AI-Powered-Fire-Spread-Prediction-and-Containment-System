import { test, expect } from '@playwright/test'

test.describe('Firefighter Dashboard - live fire map', () => {

    test.beforeEach(async({ page }) =>{
        await page.goto('/firefighter/firefighterDashboard');
    });

    test('Main page renders', async ({page}) =>{
        await expect(page.getByRole('main')).toBeVisible();
    })

    test('nearby reports section renders', async({ page }) => {
        await expect(page.getByText('Nearby Reports')).toBeVisible();
        await expect(page.getByText('Pretoria West')).toBeVisible();
    });

    test('Map renders', async ({ page }) => {
        await expect(page.getByRole('region', { name: 'Map' })).toBeVisible();      
    })

    test('All quick action map overlay stats are rendered', async ({page}) => {
        await expect(page.getByText('3', { exact: true })).toBeVisible();
        await page.getByText('2.7 km').click();
        await page.getByText('9', { exact: true }).click();
    })

    test('All quick action buttons are rendered', async ({page}) => {
        await expect(page.getByRole('button', { name: 'Unit position View team on map' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Report a fire New fire' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Log containment line Draw' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Spread Simulation View AI' })).toBeVisible();
    })

    test('All environment variables are rendered', async ({page}) => {
        await expect(page.locator('div').filter({ hasText: /^38°CTemperature$/ }).first()).toBeVisible();
        await expect(page.locator('div').filter({ hasText: /^18 km\/hWind NW$/ }).first()).toBeVisible();
        await expect(page.locator('div').filter({ hasText: /^HighFire Danger$/ }).first()).toBeVisible();
        await expect(page.locator('div').filter({ hasText: /^32%Humidity$/ }).first()).toBeVisible();
    })
});