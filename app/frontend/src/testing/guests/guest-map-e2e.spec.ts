// import {expect,test} from "@playwright/test";
// test('test', async ({ page }) => {
//   await page.goto('http://localhost:3000/');
//   await page.getByRole('img', { name: 'Fire Spread Prediction Logo' }).click();
//   await page.getByRole('button', { name: 'Sign in as Guest' }).click();
//   //checks the marker
//   await expect(page.locator('div:nth-child(9) > .relative.flex > .relative')).toBeVisible();
//   //checks the animation
//   await expect(page.locator('.animate-ping').first()).toBeVisible();
//   //checks the radius (probably going to become a check for the points of a polygon object)
//   await expect(page.locator('id="fire-radius"'))
// });