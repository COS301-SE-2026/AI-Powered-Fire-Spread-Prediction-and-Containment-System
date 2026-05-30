// NOTE: This e2e test is using mock data for now until we have a proper db setup.
// Once proper db is setup, the proper endpoints will be subbed in

import {test, expect, Page} from '@playwright/test';

const MOCK_REQUESTS = [
    {
        request_id: 'req-1',
        user_id: 'user-1',
        user_full_name: 'James Smith',
        email: 'james@smith.com',
        role: 'firefighter',
        status: 'pending',
        created_at: '2026-05-20T09:12:00Z',
        firefighter_license_id: 'FF-1001',
    },
    {
        request_id: 'req-2',
        user_id: 'user-2',
        user_full_name: 'John Doe',
        email: 'john@doe.com',
        role: 'admin',
        status: 'pending',
        created_at: '2026-05-29T14:30:00Z',
    },
    {
        request_id: 'req-3',
        user_id: 'user31',
        user_full_name: 'Anna Smit',
        email: 'Anna@smit.com',
        role: 'firefighter',
        status: 'approved',
        created_at: '2026-05-18T11:00:00Z',
        firefighter_license_id: 'FF-1002',
    },
    {
        request_id: 'req-4',
        user_id: 'user-4',
        user_full_name: 'Lerato Botha',
        email: 'lerato@Botha.com',
        role: 'admin',
        status: 'rejected',
        created_at: '2026-05-17T08:45:00Z',
    },
    {
        request_id: 'req-5',
        user_id: 'user-5',
        user_full_name: 'Thabo Mokona',
        email: 'thabo@Mokona.com',
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
async function movkAction(page:Page, requestId: string, action: 'approve' | 'reject' | 'revoke', overrides: Partial<(typeof MOCK_REQUESTS)[0]> = {}) {
    const original = MOCK_REQUESTS.find((r) => r.request_id === requestId)!;
    const statusMap = {approve:'approved', reject: 'rejected', revoke: 'revoked'} as const;
    const updated = {...original, status: statusMap[action], ...overrides};

    await page.route(
        '**/api/admin/roles/role-requests/${requestId}/${action}',
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

        await expect(page.getByText('Anna Smit')).toBeVisible();
        await expect(page.getByText('James Smith')).not.toBeVisible();
    });

    test('"Rejected" tab shows only rejected requests', async ({page}) => {
        await page.getByRole('button', {name: /rejected/i}).click();

        await expect(page.getByText('Lerato Botha')).toBeVisible();
        await expect(page.getByText('James Smith')).not.toBeVisible();
    });

    test('"Revoked" tab shows only revoked requests', async ({page}) => {
        await page.getByRole('button', {name: /revoked/i}).click();

        await expect(page.getByText('Thabo Mokona')).toBeVisible();
        await expect(page.getByText('James Smith')).not.toBeVisible();
    });
});