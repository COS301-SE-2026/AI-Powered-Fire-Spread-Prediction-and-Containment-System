// NOTE: This e2e test is using mock data for now until we have a proper db setup.
// Once proper db is setup, the proper endpoints will be subbed in

import {test, expect, Page} from '@playwright/test';

const MOCK_REQUESTS = [
    {
        request_id: 'req-1',
        user_id: 'user-1',
        fullname: 'James Smith',
        email: 'james@smith.com',
        role: 'firefighter',
        status: 'pending',
        created_at: '2026-05-20T09:12:00Z',
        firefighter_license_id: 'FF-1001',
    },
    {
        request_id: 'req-2',
        user_id: 'user-2',
        fullname: 'John Doe',
        email: 'john@doe.com',
        role: 'admin',
        status: 'pending',
        created_at: '2026-05-29T14:30:00Z',
    },
    {
        request_id: 'req-3',
        user_id: 'user31',
        fullname: 'Anna Smit',
        email: 'Anna@smit.com',
        role: 'firefighter',
        status: 'approved',
        created_at: '2026-05-18T11:00:00Z',
        firefighter_license_id: 'FF-1002',
    },
    {
        request_id: 'req-4',
        user_id: 'user-4',
        fullname: 'Lerato Botha',
        email: 'lerato@Botha.com',
        role: 'admin',
        status: 'rejected',
        created_at: '2026-05-17T08:45:00Z',
    },
    {
        request_id: 'req-5',
        user_id: 'user-5',
        fullname: 'Thabo Mokona',
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