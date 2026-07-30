import { test, expect } from "@playwright/test";
 
test.describe("Report a Fire, Frontend (real API)", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3000/");
    await page.getByRole("button", { name: "Login" }).click();
    await page.getByRole("textbox", { name: "Email" }).click();
    await page.getByRole("textbox", { name: "Email" }).fill("amahle.d@fireaway.co.za");
    await page.getByRole("textbox", { name: "Password" }).click();
    await page.getByRole("textbox", { name: "Password" }).fill("Password123!");
    await page.getByRole("button", { name: "Login" }).click();
 
    await page.locator('aside').hover();
    await page.getByRole('link', { name: 'Report a Fire' }).click(); 
  });
 
  test("updates location field on search and change in map", async ({ page }) => {
    const searchInput = page.locator(
      'input[placeholder*="Drop a pin or type your address"]'
    );
    await searchInput.fill("Pretoria");
    await page.getByRole('button', { name: 'Pretoria, Gauteng, South' }).click();
    await expect(searchInput).toHaveValue("Pretoria, Gauteng, South Africa");
 
    const pinMarkerSelector =
      '.mapboxgl-marker.mapboxgl-marker-anchor-bottom[aria-label="Map marker"]';
    await page.waitForSelector(pinMarkerSelector, { state: "visible", timeout: 10000 });
  });
 
  // test("submits a report and shows ref#", async ({ page }) => {
  //   const searchInput = page.locator(
  //     'input[placeholder*="Drop a pin or type your address"]'
  //   );
  //   await searchInput.fill("Pretoria");
  //   await page.getByRole('button', { name: 'Pretoria, Gauteng, South' }).click();
 
  //   const descriptionField = page.locator("textarea");
  //   await descriptionField.fill("Test fire from E2E");
 
  //   const fileInput = page.locator('input[type="file"]');
  //   await fileInput.setInputFiles({
  //     name: "test.jpg",
  //     mimeType: "image/jpeg",
  //     buffer: Buffer.from("fake"),
  //   });
 
  //   const submitButton = page.locator(
  //     'button[type="submit"]:has-text("Submit Fire Report")'
  //   );
 
  //   const responsePromise = page.waitForResponse(
  //     (res) =>
  //       res.url().includes("/api/users/reported-fires") &&
  //       res.request().method() === "POST"
  //   );
 
  //   await submitButton.click();
 
  //   const response = await responsePromise;
  //   expect(response.ok()).toBeTruthy();
  //   const body = await response.json();
  //   expect(body.reference_number).toMatch(/^FR-\d{4}-[A-Z0-9]+$/);
 
  //   await expect(page.locator(`text=${body.reference_number}`)).toBeVisible({
  //     timeout: 10000,
  //   });
  //   await expect(page.locator("text=Report submitted")).toBeVisible();
 
  //   await expect(
  //     page.locator('input[placeholder*="Drop a pin or type your address"]')
  //   ).toBeVisible({timeout:1500});
  // });
 
  test("shows error when no location selected", async ({ page }) => {
    const descriptionField = page.locator("textarea");
    await descriptionField.fill("Test fire");
 
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: "test.jpg",
      mimeType: "image/jpeg",
      buffer: Buffer.from("fake"),
    });
 
    const submitButton = page.locator(
      'button[type="submit"]:has-text("Submit Fire Report")'
    );
    await submitButton.click();
 
    await expect(page.locator("text=/Please select a valid location/i")).toBeVisible();
  });
 
  // test("shows error when photo is missing on desktop", async ({ page }) => {
  //   const searchInput = page.getByRole('textbox', { name: 'Drop a pin or type your' });
  //   await searchInput.fill("Pretoria");
  //   await page.getByRole('button', { name: 'Pretoria, Gauteng, South' }).click();
 
  //   const descriptionField = page.locator("textarea");
  //   await descriptionField.fill("Test fire");
 
  //   const submitButton = page.locator(
  //     'button[type="submit"]:has-text("Submit Fire Report")'
  //   );
  //   await submitButton.click();
 
  //   await expect(
  //     page.locator("text=/Field evidence attachment is mandatory on desktop/i")
  //   ).toBeVisible();
  // });
});