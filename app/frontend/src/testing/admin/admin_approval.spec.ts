import {test, expect} from '@playwright/test';

test.describe('Admin approve role change.', ()=> {

    test.beforeEach(async ({page}) => {
        //mock JWT Admin Token
        await page.addInitScript(() => {
            window.localStorage.setItem(
                'auth-token',
                'mocked-admin-jwt-token'
            )
        });

        //admin role approval form
        await page.goto('/admin/role-management');
    });

    test('SUCCESS: Handles admin clicking on firefighter radio button and clicking "Approve".', async ({page}) => {
        //is the structure of the form correct
        //need to add check for form (sub-issue on project board)

        //note-to-self tells framework to scan DOM tree to find element that matches what is in the parentheses
        const userCard = page.locator('[data-testid="requesting-user-details"]');
        await expect(userCard).toBeVisible();
        await expect(userCard).toContainText('Piet Pompies (piet.pompies@mail.com)');

        //select radiogroup firefighter button
        const firefighterRadio = page.locator('input[type="radio"][data-testid="role-option-firefighter"]');
        await expect(firefighterRadio).toBeVisible();
        await firefighterRadio.check();
        await expect(firefighterRadio).toBeChecked();

        //network intercept
        await page.route('**/api/admin/role-approval', async (route) => {
            const request = route.request();
            const payload = JSON.parse(request.postData() ?? '{}');

            expect(payload.action).toBe('approve');
            expect(payload.target_role).toBe('Firefighter');

            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    status: 'success',
                    updated_role: 'Firefighter'
                })
            });
        });

        //onClick approve
        const approveButton = page.locator('[data-testid="submit-approve-button"]');
        await expect(approveButton).toBeVisible();
        await approveButton.click();

        await expect(page.locator('.alert-success')).toBeVisible();
    });

    test('NAVIGATION: Handles when an admin clicks on the cancel button -> should navigate back to the main page.', async ({ page }) => {
        const cancelButton = page.locator('[data-testid="cancel-approval-button"]');
        await expect(cancelButton).toBeVisible();

        //onClickCancelButton
        await cancelButton.click();

        //verify navigation back to main
        await expect(page).toHaveURL(/\/admin\/dashboard|\/admin/);
    });

    test('SUCCESS: Handles admin clicking on admin radio button and clicking "Approve".', async ({page}) => {
        //is the structure of the form correct
        //need to add check for form (sub-issue on project board)

        //note-to-self tells framework to scan DOM tree to find element that matches what is in the parentheses
        const userCard = page.locator('[data-testid="requesting-user-details"]');
        await expect(userCard).toBeVisible();
        await expect(userCard).toContainText('Piet Pompies (piet.pompies@mail.com)');

        //select radiogroup admin button
        const adminRadio = page.locator('input[type="radio"][data-testid="role-option-admin"]');
        await expect(adminRadio).toBeVisible();
        await adminRadio.check();
        await expect(adminRadio).toBeChecked();

        //network intercept
        await page.route('**/api/admin/role-approval', async (route) => {
            const request = route.request();
            const payload = JSON.parse(request.postData() ?? '{}');

            expect(payload.action).toBe('approve');
            expect(payload.target_role).toBe('Admin');

            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    status: 'success',
                    updated_role: 'Admin'
                })
            });
        });

        //onClick approve
        const approveButton = page.locator('[data-testid="submit-approve-button"]');
        await expect(approveButton).toBeVisible();
        await approveButton.click();

        await expect(page.locator('.alert-success')).toBeVisible();
    });
});