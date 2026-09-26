// accessibility verification

import AxeBuilder from '@axe-core/playwright';
import { test, expect, Route } from '@playwright/test';

const PUBLIC_ROUTES = [
    { name: 'Landing Page', path: '/' },
    { name: 'Public Guest Map', path: '/guest/map' },
    { name: 'Help Menu', path: '/help_menu/help_menu' },
    { name: 'Volunteer Worker', path: '/volunteer' },
    { name: 'Login Page', path: '/login' },
];

test.describe('Accessibility and WCAG 2.1 AA Verification', () => {
    const MOCK_FIRE_INCIDENTS = [
        {
            id: 'FR-2026-PRETORIA-01',
            reference_number: 'FR-2026-PRETORIA-01',
            lat: -25.7479,
            lng: 28.2293,
            location_text: 'Pretoria East Nature Reserve',
            status: 'verified',
            boundary_radius: 1.5,
            size: 1.5,
            submitted_at: '2026-08-19T10:00:00Z',
            reporter_name: 'Person',
        },
    ];

    test.beforeEach(async ({ page }) => {
        await page.route('**/health', async (route: Route) => route.fulfill ({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ status: 'healthy' }),
        }));

        const fulfillIncidents = async (route: Route): Promise<void> => route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(MOCK_FIRE_INCIDENTS),
        });

        await page.route('**/api/v1/incidents/public', fulfillIncidents);
        await page.route('**/api/guests/reported-fires**', fulfillIncidents);
        await page.route('**/api/reports**', fulfillIncidents);
    });

    test('Public landing page passes WCAG 2.1 Level AA automated exe scan', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        const accessibilityScanResults = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();

        const severeViolations = accessibilityScanResults.violations.filter(
            (v) => v.impact === 'critical' || v.impact === 'serious'
        );

        expect(severeViolations).toEqual([]);
        expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('Interactive navigation elements support keyboard traversal and visible focus', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        await page.keyboard.press('Tab');

        const focusedTag = await page.evaluate(() => document.activeElement?.tagName.toLowerCase());
        expect(['a', 'button', 'input']).toContain(focusedTag);

        const outlineStyle = await page.evaluate(() => {
            const el = document.activeElement;
            if (!el) return 'none';
            const styles = window.getComputedStyle(el);
            return styles.outlineStyle !== 'none' || styles.boxShadow !== 'none';
        });

        expect(outlineStyle).toBe(true);
    });

    test('Public images, icons and buttons expose accessible names', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        const invalidImagesCount = await page.evaluate(() => {
            const images = Array.from (document.querySelectorAll('img'));
            return images.filter((img) => !img.hasAttribute('alt')).length;
        });
        expect(invalidImagesCount).toBe(0);

        const invalidButtonsCount = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            return buttons.filter((btn) => {
                const text = btn.innerText.trim();
                const ariaLabel = btn.getAttribute('aria-label');
                const ariaLabelledBy = btn.getAttribute('aria-labelledby');
                return !text && !ariaLabel && !ariaLabelledBy;
            }).length;
        });
        expect(invalidButtonsCount).toBe(0);
    });
});