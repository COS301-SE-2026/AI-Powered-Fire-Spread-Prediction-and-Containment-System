import {expect,test} from "@playwright/test";
test('test', async ({ page }) => {
  await page.goto('/guests/guestsLanding');
  //checks the marker
  await expect(page.locator('.relative.inline-flex').first()).toBeVisible();
  //checks the animation
  await expect(page.locator('.animate-ping').first()).toBeVisible();
  //checks the radius (probably going to become a check for the points of a polygon object)
  await expect(page.locator('id="fire-radius"'))
});