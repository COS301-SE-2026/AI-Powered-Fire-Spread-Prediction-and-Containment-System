import {test, expect} from '@playwright/test';

const JAN = {id: 'req_1', name: 'Jan Alleman', email: 'j.alleman@email.com', role: 'firefighter', status: 'pending'};
const ANNA = {id: 'req_2', name: 'Anna Katerina', email: 'a.katerina@email.com', role: 'admin', status: 'pending'};
const PIET = {id: 'req_3', name: 'Piet Pompies', email: 'j.alleman@email.com', role: 'firefighter', status: 'approved'};


test.describe('Admin approve role change.', ()=> {

    test.beforeEach(async ({page}) => {
        await page.route('**/api/admin/roles/role-requests', async (route) => {
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

        await page.goto('/admin/role-management');

    });

    //test that the table loads
    test('table: REnders the role request rows on page load.', async ({page}) => {
        await expect(page.getByText(JAN.name)).toBeVisible();
        await expect(page.getByText(ANNA.name)).toBeVisible();
        await expect(page.getByText(PIET.name)).toBeVisible();
    })

});