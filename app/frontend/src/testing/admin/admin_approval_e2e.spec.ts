// NOTE: This e2e test is using mock data for now until we have a proper db setup.
// Once proper db is setup, the proper endpoints will be subbed in

import {test, expect, Page} from '@playwright/test';

const MOCK_REQUESTS = [
    {
        request_id: 'req_1',
        user_id: 'user_1',
        user_full_name: 'James Smith',
        email: 'j.smith@email.com',
        role: 'firefighter',
        status: 'pending',
        created_at: '2026-05-20T09:12:00Z',
        firefighter_license_id: 'FF-1001',
    },
    {
        request_id: 'req_2',
        user_id: 'user_2',
        user_full_name: 'Anna Dlamini',
        email: 'a.dlamini@email.com',
        role: 'admin',
        status: 'pending',
        created_at: '2026-05-29T14:30:00Z',
    },
    {
        request_id: 'req_3',
        user_id: 'user_3',
        user_full_name: 'Peter Nkosi',
        email: 'p.nkosi@email.com',
        role: 'firefighter',
        status: 'approved',
        created_at: '2026-05-18T11:00:00Z',
        firefighter_license_id: 'FF-1002',
    },
    {
        request_id: 'req_4',
        user_id: 'user_4',
        user_full_name: 'Lerato Botha',
        email: 'l.botha@email.com',
        role: 'admin',
        status: 'rejected',
        created_at: '2026-05-17T08:45:00Z',
    },
    {
        request_id: 'req_5',
        user_id: 'user_5',
        user_full_name: 'Thabo Mokoena',
        email: 't.mokoena@email.com',
        role: 'firefighter',
        status: 'revoked',
        created_at: '2026-05-16T10:20:00Z',
        firefighter_license_id: 'FF-2001',
    },
];

// Intercept GET /api/admin/roles/role-requests and returns provided list
// Called at start of most tests so page loads with controlled data
async function mockGetRequests(page: Page, requests = MOCK_REQUESTS){
    await page.route('**/api/admin/roles/role-requests', (route) => 
        route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({data: requests, total: requests.length}),
        })
    );
}

// Intercept a specific action endpoint (approve/reject/revoke) and return updated version of targeted request
async function mockAction(page:Page, requestId: string, action: 'approve' | 'reject' | 'revoke', overrides: Partial<(typeof MOCK_REQUESTS)[0]> = {}) {
    const original = MOCK_REQUESTS.find((r) => r.request_id === requestId);
    if (!original) throw new Error(`No request found with id: ${requestId}`);
    
    const statusMap = {approve:'approved', reject: 'rejected', revoke: 'revoked'} as const;
    const updated = {...original, status: statusMap[action], ...overrides};

    await page.route(
        `**/api/admin/roles/role-requests/${requestId}/${action}`,
        (route) =>
            route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify(updated),
            })
    );
}

// Load page
test.describe('Page load', () => {
    test('renders page heading', async ({page}) => {
        await mockGetRequests(page);
        await page.goto('/admin/approvalPage');
        await expect(page.getByRole('heading', {name: /role approvals/i})).toBeVisible();
        await expect(page.getByText(/manage user role requests/i)).toBeVisible();
    });

    test('displays all requests returned by the API', async ({page}) => {
        await mockGetRequests(page);
        await page.goto('/admin/approvalPage');
        
        for(const req of MOCK_REQUESTS){
            await expect(page.getByText(req.user_full_name)).toBeVisible();
        }
    });

    test('shows an error message when the API returns a non-ok response', async ({page}) => {
        await page.route('**/api/admin/roles/role-requests', (route) =>
            route.fulfill({status: 500})
        );

        await page.goto('/admin/approvalPage');
        await expect(page.getByTestId('error-message')).toBeVisible();
        await expect(page.getByText(/failed to load role requests/i)).toBeVisible();
    });

    test('shows an error message when the API call throws a network error', async ({page}) => {
        await page.route('**/api/admin/roles/role-requests', (route) => route.abort());
        await page.goto('/admin/approvalPage');

        await expect(page.getByTestId('error-message')).toBeVisible();
        await expect(page.getByText(/unable to connect/i)).toBeVisible();
    });

});


// Filter tabs
test.describe('Filter tabs', () => {
    test.beforeEach(async ({page}) => {
        await mockGetRequests(page);
        await page.goto('/admin/approvalPage');
    });

    test('"ALL" tab shows every request', async ({page}) => {
        await page.getByRole('button', {name: /all/i}).click();

        for (const req of MOCK_REQUESTS){
            await expect(page.getByText(req.user_full_name)).toBeVisible();
        }
    });

    test('"Pending" tab shows only pending requests', async ({page}) => {
        await page.getByRole('button', {name: /pending/i}).click();

        const pending = MOCK_REQUESTS.filter((r) => r.status === 'pending');
        const others = MOCK_REQUESTS.filter((r) => r.status !== 'pending');

        for (const req of pending){
            await expect(page.getByText(req.user_full_name)).toBeVisible();
        }

        for (const req of others){
            await expect(page.getByText(req.user_full_name)).not.toBeVisible();
        }
    });

    test('"Approved" tab shows only approved requests', async ({page}) => {
        await page.getByRole('button', {name: /approved/i}).click();

        await expect(page.getByText('Peter Nkosi')).toBeVisible();
        await expect(page.getByText('James Smith')).not.toBeVisible();
    });

    test('"Rejected" tab shows only rejected requests', async ({page}) => {
        await page.getByRole('button', {name: /rejected/i}).click();

        await expect(page.getByText('Lerato Botha')).toBeVisible();
        await expect(page.getByText('James Smith')).not.toBeVisible();
    });

    test('"Revoked" tab shows only revoked requests', async ({page}) => {
        await page.getByRole('button', {name: /revoked/i}).click();

        await expect(page.getByText('Thabo Mokoena')).toBeVisible();
        await expect(page.getByText('James Smith')).not.toBeVisible();
    });
});


// Revoke action
test.describe('Revoke', () => {
    test('revoking an approved request updates status in the table', async ({page}) => {
        await mockGetRequests(page);
        await mockAction(page, 'req_3', 'revoke');
        await page.goto('/admin/approvalPage');

        const row = page.getByRole('row', {name: /peter nkosi/i});
        await row.getByRole('button', {name: /view/i}).click();
        await page.getByTestId('revoke-btn').click();

        await expect(page.getByTestId('approval-modal')).not.toBeVisible();
        await expect(row.getByText(/revoked/i)).toBeVisible();
       
    });

    test('A failed revoke API call keeps modal open', async ({page}) => {
        await mockGetRequests(page);
        await page.route('**/api/admin/roles/role-requests/req_3/revoke', (route) => 
            route.fulfill({status: 400})
        );

        await page.goto('/admin/approvalPage');

        const row = page.getByRole('row', {name: /peter nkosi/i});
        await row.getByRole('button', {name: /view/i}).click();
        await page.getByTestId('revoke-btn').click();

        await expect(page.getByTestId('approval-modal')).toBeVisible();
    
    });
});


// Full admin journeys
test.describe('Admin journeys', () => {
    test('admin approves a pending firefighter request', async ({page}) => {
        await mockGetRequests(page);
        await mockAction(page, 'req_1', 'approve');
        await page.goto('/admin/approvalPage');

        // See request in table under Pending
        await page.getByRole('button', {name: /pending/i}).click();
        await expect(page.getByText('James Smith')).toBeVisible();

        // Open the modal and verify details
        await page.getByRole('row', {name: /james smith/i}).getByRole('button', {name: /view/i}).click();
        await expect(page.getByTestId('approval-modal')).toBeVisible();

        // Approve
        await page.getByTestId('approve-btn').click();
        await expect(page.getByTestId('approval-modal')).not.toBeVisible();

        // Request now under Approved tab
        await page.getByRole('button', {name: /approved/i}).click();
        await expect(page.getByText('James Smith')).toBeVisible();
    });

    test('admin rejects then cannot re-process the same request', async ({page}) => {
        await mockGetRequests(page);
        await mockAction(page, 'req_2', 'reject');
        await page.goto('/admin/approvalPage');

        // Reject request
        await page.getByRole('row', {name: /anna dlamini/i}).getByRole('button', {name: /view/i}).click();
        await page.getByTestId('reject-btn').click();
        await expect(page.getByTestId('approval-modal')).not.toBeVisible();

        // Open now-rejected request - no action buttons should be present
        await page.getByRole('row', {name: /anna dlamini/i}).getByRole('button', {name: /view/i}).click();
        await expect(page.getByTestId('approve-btn')).not.toBeVisible();
        await expect(page.getByTestId('reject-btn')).not.toBeVisible();
    });

    test('admin approves then revokes a request', async ({page}) => {
        await mockGetRequests(page);
        await mockAction(page, 'req_1', 'approve');
        await page.goto('/admin/approvalPage');

        // Approve first
        await page.getByRole('row', {name: /james smith/i}).getByRole('button', {name: /view/i}).click();
        await page.getByTestId('approve-btn').click();
        await expect(page.getByTestId('approval-modal')).not.toBeVisible();

        // Mock revoke endpoint for the newly approved request
        await page.route('**/api/admin/roles/role-requests/req_1/revoke', (route) => 
            route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({...MOCK_REQUESTS[0], status: 'revoked'}),
            })
        );

        // Open approved request and revoke it
        await page.getByRole('row', {name: /james smith/i}).getByRole('button', {name: /view/i}).click();
        await page.getByTestId('revoke-btn').click();
        await expect(page.getByTestId('approval-modal')).not.toBeVisible();

        // Verify shows as revoked
        const row = page.getByRole('row', {name: /james smith/i});
        await expect(row.getByText(/revoked/i)).toBeVisible();
    });
});
