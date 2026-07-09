import {test, expect} from '@playwright/test';

const JAN = {id: 'req_1', name: 'Jan Alleman', email: 'j.alleman@email.com', role: 'firefighter', status: 'pending'};
const ANNA = {id: 'req_2', name: 'Anna Katerina', email: 'a.katerina@email.com', role: 'admin', status: 'pending'};
const PIET = {id: 'req_3', name: 'Piet Pompies', email: 'p.pompies.com', role: 'firefighter', status: 'approved'};


test.describe('Admin approve role change.', ()=> {

    test.beforeEach(async ({page}) => {
        await page.route(`**/api/admin/roles/role-requests`, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    data: [{
                            request_id: JAN.id, user_id: 'user_1', 
                            user_full_name: JAN.name, 
                            email: JAN.email, 
                            role: JAN.role, 
                            status: JAN.status, 
                            created_at: '2026-05-20T09:12:00Z', 
                            firefighter_license_id: 'FF-1001'},
                        {
                            request_id: ANNA.id, user_id: 'user_2', 
                            user_full_name: ANNA.name, 
                            email: ANNA.email, 
                            role: ANNA.role, 
                            status: ANNA.status, 
                            created_at: '2026-05-19T14:30:00Z'},
                        {
                            request_id: PIET.id, user_id: 'user_3', 
                            user_full_name: PIET.name, 
                            email: PIET.email, 
                            role: PIET.role, 
                            status: PIET.status, 
                            created_at: '2026-05-18T11:00:00Z', 
                            firefighter_license_id: 'FF-1002'},
                    ]
                })
            });
        });

        await page.addInitScript(() => {
            window.localStorage.setItem('auth-token', 'mocked-admin-jwt-token');
        });

        await page.goto('/admin/approvalPage');

    });

    //test that the table loads
    test('Renders the role request rows in the table on page load.', async ({page}) => {
        await expect(page.getByText(JAN.name)).toBeVisible();
        await expect(page.getByText(ANNA.name)).toBeVisible();
        await expect(page.getByText(PIET.name)).toBeVisible();
    });

    test('Every row in the table has a view button.', async ({page}) => {
        for (const user of [JAN, ANNA, PIET]) {
            await expect(page.locator(`[data-testid="view-request-${user.id}"]`)).toBeVisible();
        }
    });

    //tests modal views
    test('The modal opens with the correct user details when the View button is clicked.', async ({page}) => {
        await page.locator(`[data-testid="view-request-${ANNA.id}"]`).click();
        
        const modal= page.locator('dialog');
        await expect(modal).toBeVisible();
        await expect(modal.getByRole('paragraph').filter({hasText: ANNA.name})).toBeVisible();
        await expect(modal.getByRole('paragraph').filter({hasText: ANNA.email})).toBeVisible();
        await expect(modal.getByRole('paragraph').filter({hasText: ANNA.role})).toBeVisible();
        await expect(modal.getByText('pending', {exact: true})).toBeVisible();
    });

    test('The Approve and Reject buttons are visible for a pending request. The Revoke button is not visible for a pending request', async ({page}) => {
        await page.locator(`[data-testid="view-request-${ANNA.id}"]`).click();
        await expect(page.locator(`[data-testid="approve-btn"]`)).toBeVisible();
        await expect(page.locator(`[data-testid="reject-btn"]`)).toBeVisible();
        await expect(page.locator(`[data-testid="revoke-btn"]`)).not.toBeVisible();
    });

    test('The Approve and Reject buttons are not visible for an approved request. The Revoke button is visible for an approved request', async ({page}) => {
        await page.locator(`[data-testid="view-request-${PIET.id}"]`).click();
        await expect(page.locator(`[data-testid="approve-btn"]`)).not.toBeVisible();
        await expect(page.locator(`[data-testid="reject-btn"]`)).not.toBeVisible();
        await expect(page.locator(`[data-testid="revoke-btn"]`)).toBeVisible();
    });


    //test the approval of the admin role
    test("When approving an admin role request, the correct API is called and the modal is closed.", async ({page}) => {
        await page.route(`**/api/admin/roles/role-requests/${ANNA.id}/approve`, async (route) => {
            expect(route.request().method()).toBe('POST');
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({request_id: ANNA.id, status: 'approved'})
            });
        });

        await page.locator(`[data-testid="view-request-${ANNA.id}"]`).click();
        await expect(page.locator(`[data-testid="approve-btn"]`)).toBeVisible();
        await page.locator(`[data-testid="approve-btn"]`).click();

        //close of modal
        await expect(page.locator('dialog')).not.toBeVisible();
    });

    //test the reject of the admin role
    test("When rejecting an admin role request, the correct API is called and the modal is closed.", async ({page}) => {
        await page.route(`**/api/admin/roles/role-requests/${ANNA.id}/reject`, async (route) => {
            expect(route.request().method()).toBe('POST');
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({request_id: ANNA.id, status: 'rejected'})
            });
        });

        await page.locator(`[data-testid="view-request-${ANNA.id}"]`).click();
        await page.locator(`[data-testid="reject-btn"]`).click();

        //close of modal
        await expect(page.locator('dialog')).not.toBeVisible();
    });

    //test the revoking of the admin role
    test('Revoke an approved request succeeds when the correct API is called and the modal closes', async ({page}) => {
        await page.route(`**/api/admin/roles/role-requests/${PIET.id}/revoke`, async (route) => {
            expect(route.request().method()).toBe('POST');
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({request_id: PIET.id, status: 'revoked'})
            });
        });

        await page.locator(`[data-testid="view-request-${PIET.id}"]`).click();
        await page.locator(`[data-testid="revoke-btn"]`).click();

        //close of modal
        await expect(page.locator('dialog')).not.toBeVisible();
    });

    //closing the modal without changing anything about the request
    test('The x-button closed the modal', async ({page}) => {
        await page.locator(`[data-testid="view-request-${ANNA.id}"]`).click();
        await expect(page.locator('dialog')).toBeVisible();
        await page.locator(`[data-testid="modal-close-button"]`).click();
        await expect(page.locator('dialog')).not.toBeVisible();
    });
    

    //filters
    test('When selecting the pending tab only pending requests are visible', async ({page}) => {
        await page.getByRole('button', {name: 'pending'}).click();
        await expect(page.getByText(JAN.name)).toBeVisible();
        await expect(page.getByText(ANNA.name)).toBeVisible();
        await expect(page.getByText(PIET.name)).not.toBeVisible();
    });

    test('When selecting the approved tab only approved requests are visible', async ({page}) => {
        await page.getByRole('button', {name: 'approved'}).click();
        await expect(page.getByText(JAN.name)).not.toBeVisible();
        await expect(page.getByText(ANNA.name)).not.toBeVisible();
        await expect(page.getByText(PIET.name)).toBeVisible();
    });
});