import {test, expect, type Page} from '@playwright/test';

const DASHBOARD_ROUTE = '/registeredUser/registeredUserLanding';
const DESKTOP_VIEW = {width: 1200, height: 800};

test.describe('Registered User Landing Page', () => {
    test.beforeEach(async ({page}) => {
        await page.goto(DASHBOARD_ROUTE);
    });

    test('Loads and renders page header', async ({page}) => {
        await expect(page.getByRole('heading', {name: 'Welcome'})).toBeVisible();
        await expect(page.getByText('Public Fire Map View')).toBeVisible();
    });

    test('Shows loading state before map initializes, then map renders', async({page}) => {
        const loadingText = page.getByText('Initializing Map');

        const sawLoadingOrAlreadyLoaded = await Promise.race([
            loadingText.isVisible().catch(() => false),
            page.waitForTimeout(50).then(() => true),
        ]);
        expect(sawLoadingOrAlreadyLoaded).toBeTruthy();
        await expect(loadingText).toBeHidden({timeout: 10_000});
    });

    test('Renders NearbyReport side panel', async ({page}) => {
        await expect(page.getByText('Nearby Reports')).toBeVisible();
    });

});

const SIDEBAR_LINKS: {label: string; expectedHref: string}[] = [
    {label: 'Home', expectedHref: '/registeredUser/registeredUserLanding'},
    {label: 'Report a Fire', expectedHref: '/registeredUser/registeredReportFire'},
    {label: 'Fire Simulation', expectedHref: '/registeredUser/registeredUnderConstruction'},
    {label: 'Notifications', expectedHref: '/registeredUser/registeredUnderConstruction'},
    {label: 'Community', expectedHref: '/registeredUser/registeredUnderConstruction'},
    {label: 'Settings', expectedHref: '/registeredUser/registeredUnderConstruction'},
];

test.describe('Sidebar menu navigation', () => {
    test.beforeEach(async ({page}) => {
        await page.setViewportSize(DESKTOP_VIEW);
        await page.goto(DASHBOARD_ROUTE);
        await page.locator('aside').hover();
    });

    const sidebar = (page: Page) => page.locator('aside');

    for (const {label, expectedHref} of SIDEBAR_LINKS){
        test(`"${label}" has correct href`, async ({page}) => {
            await expect(sidebar(page).getByRole('link', {name: label})).toHaveAttribute('href', expectedHref);
        });
    }

    test('Clicking Logout calls router.push("login)', async ({page}) => {
        await page.route('**/login', (route) =>
            route.fulfill({status: 200, contentType: 'text/html', body: '<html></html>'})
        );

        await page.getByRole('button', {name: 'Logout'}).click();
        await expect(page).toHaveURL(/\/login$/);
    });

    test('Activce menu items reflect current route', async({page}) => {
        await expect(page.getByRole('link', {name: 'Home', exact: true})).toHaveClass(/bg-smoke-hover/);
    });
});
