import { test, expect } from "@playwright/test";

test.describe("Guest Public Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/guests");
    await page.waitForLoadState("networkidle");
  });
  
  test("shows Nearby Reports section", async ({ page }) => {
    await expect(page.locator("h2:has-text('Nearby Reports')")).toBeVisible();
    const nearbyReports = page.locator(".rounded-2xl.bg-carbon-side\\/40");
    await expect(nearbyReports).toBeVisible();
  });

  test("email alert registration form works", async ({ page }) => {
    const emailInput = page.locator('input[type="email"]');
    const registerButton = page.locator('button:has-text("Register")');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/register", { timeout: 10000 });
    await expect(page.locator("text=Registration successful")).toBeVisible({ timeout: 5000 });
  });

  test("map container is present", async ({ page }) => {
    const mapContainer = page.locator(".rounded-2xl.overflow-hidden.border.border-carbon-card");
    await expect(mapContainer).toBeVisible();
    page.on("console", (msg) => {
      if (msg.type() === "error" && msg.text().includes("Invalid LngLat")) {
      } else {
        console.log(`Console ${msg.type()}: ${msg.text()}`);
      }
    });
  });
});