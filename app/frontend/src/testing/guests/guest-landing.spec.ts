import {test, expect} from "@playwright/test"

test.describe('Guest Public Dashboard',()=> {
    //navigates to dashboard page before each test
    test.beforeEach(async ({page})=>{
        await page.goto('/guests');
    });
    test('all major components render', async({page})=>{
        //header
        await expect(page.locator('h1:has-text("Incident Map")')).toBeVisible();
        await expect(page.locator('p:has-text("Public Fire Map View")')).toBeVisible();
        //map
        const mapContainer =page.locator('.rounded-2xl.overflow-hidden').first();
        await expect(mapContainer).toBeVisible();
        //nearby reports container
        await expect(page.locator('h2:has-text("Nearby Reports")')).toBeVisible();
        const reportsContainer =page.locator(String.raw`.rounded-2xl.bg-carbon-side\/40`);
        await expect(reportsContainer).toBeVisible();
    });
    test('async map load', async ({ page}) => {
        await Promise.all([
            page.goto('/guests'), // uses default 'load', but we don't await it alone
            expect(page.getByText('Initializing Public Map Canvas...')).toBeVisible(),
        ]);

        const mapCanvas =page.locator('.relative.flex.items-center.justify-center.size-6');
        await expect(mapCanvas).toBeVisible({timeout:10000});
    });

});
