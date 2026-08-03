import {test, expect} from "@playwright/test"

test.describe('Guest Public Dashboard',()=> {
    //navigates to dashboard page before each test
    test.beforeEach(async ({page})=>{
        await page.goto('http://localhost:3000/');
        await page.getByRole('img', { name: 'Fire Spread Prediction Logo' }).click();
        await page.getByRole('button', { name: 'Sign in as Guest' }).click();
    });
    test('all major components render', async({page})=>{
        //header
        await expect(page.locator('header')).toBeVisible();
        //nearby reports
        await expect(page.getByRole('heading', { name: 'Nearby Reports' })).toBeVisible();
        //buttons
        await expect(page.getByRole('button', { name: 'Report Fire' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Recenter' })).toBeVisible();
    });


});
