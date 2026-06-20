import {test, expect} from "@playwright/test";
//mock data from seed.py in backend
 const MOCK_REPORTS = [
  {
    reference_number: 'FR-2026-001',
    location_text: 'LC de Villiers Sports Grounds, Hatfield',
    description: 'Brush fire starting near the northern fence along the road.',
    lat: -25.7480,
    lng: 28.2435,
    boundary_radius_km: 0.5,
    status: 'verified',
    status_index: 2,
    created_at: '2026-01-15T10:00:00Z',
  },
  {
    reference_number: 'FR-2026-002',
    location_text: 'Groenkloof Nature Reserve',
    description: 'Heavy smoke visible from the main hiking trail.',
    lat: -25.7800,
    lng: 28.2000,
    boundary_radius_km: 2.0,
    status: 'pending',
    status_index: 1,
    created_at: '2026-01-15T11:00:00Z',
  },
  {
    reference_number: 'FR-2026-003',
    location_text: 'Struben Dam Bird Sanctuary',
    description: 'Small contained fire, looks like an abandoned braai.',
    lat: -25.7681,
    lng: 28.2933,
    boundary_radius_km: 0.1,
    status: 'received',
    status_index: 0,
    created_at: '2026-01-15T12:00:00Z',
  },
  {
    reference_number: 'FR-2026-004',
    location_text: 'Rietvlei Nature Reserve',
    description: 'Large veld fire spreading quickly towards the eastern border.',
    lat: -25.8800,
    lng: 28.2800,
    boundary_radius_km: 3.5,
    status: 'notified',
    status_index: 3,
    created_at: '2026-01-15T13:00:00Z',
  },
  {
    reference_number: 'FR-2026-005',
    location_text: 'Moreleta Kloof Nature Reserve',
    description: 'Smell of smoke and ash falling, but can\'t see the flames.',
    lat: -25.8180,
    lng: 28.2890,
    boundary_radius_km: 1.0,
    status: 'received',
    status_index: 0,
    created_at: '2026-01-15T14:00:00Z',
  },
  {
    reference_number: 'FR-2026-006',
    location_text: 'Faerie Glen Nature Reserve',
    description: 'Fire on the ridge, moving up the hill.',
    lat: -25.7760,
    lng: 28.2930,
    boundary_radius_km: 1.5,
    status: 'verified',
    status_index: 2,
    created_at: '2026-01-15T15:00:00Z',
  },
  {
    reference_number: 'FR-2026-007',
    location_text: 'Wonderboom Nature Reserve',
    description: 'Smoke coming from the northern slope of the Magaliesberg.',
    lat: -25.6800,
    lng: 28.1900,
    boundary_radius_km: 2.5,
    status: 'pending',
    status_index: 1,
    created_at: '2026-01-15T16:00:00Z',
  },
  {
    reference_number: 'FR-2026-008',
    location_text: 'Pretoria National Botanical Garden',
    description: 'Fire near the eastern boundary wall.',
    lat: -25.7300,
    lng: 28.2700,
    boundary_radius_km: 0.3,
    status: 'notified',
    status_index: 3,
    created_at: '2026-01-15T17:00:00Z',
  },
  {
    reference_number: 'FR-2026-009',
    location_text: 'Roodeplaat Dam Nature Reserve',
    description: 'Veld fire near the southern picnic site.',
    lat: -25.6300,
    lng: 28.3600,
    boundary_radius_km: 4.0,
    status: 'verified',
    status_index: 2,
    created_at: '2026-01-15T18:00:00Z',
  },
  {
    reference_number: 'FR-2026-010',
    location_text: 'Fountains Valley Recreation Resort',
    description: 'Thick smoke near the train tracks.',
    lat: -25.7820,
    lng: 28.1960,
    boundary_radius_km: 0.8,
    status: 'received',
    status_index: 0,
    created_at: '2026-01-15T19:00:00Z',
  },
  {
    reference_number: 'FR-2026-011',
    location_text: 'Vacant lot, Erasmuskloof',
    description: 'Grass fire near the highway offramp.',
    lat: -25.8100,
    lng: 28.2600,
    boundary_radius_km: 0.2,
    status: 'verified',
    status_index: 2,
    created_at: '2026-01-15T20:00:00Z',
  },
  {
    reference_number: 'FR-2026-012',
    location_text: 'Centurion field near N1',
    description: 'Large grass fire causing poor visibility on the N1.',
    lat: -25.8500,
    lng: 28.1800,
    boundary_radius_km: 1.2,
    status: 'pending',
    status_index: 1,
    created_at: '2026-01-15T21:00:00Z',
  },
  {
    reference_number: 'FR-2026-013',
    location_text: 'Pretoria West Industrial Area',
    description: 'Chemical smoke rising from an industrial yard.',
    lat: -25.7500,
    lng: 28.1500,
    boundary_radius_km: 0.5,
    status: 'notified',
    status_index: 3,
    created_at: '2026-01-15T22:00:00Z',
  },
  {
    reference_number: 'FR-2026-014',
    location_text: 'Atterbury Road grass verge',
    description: 'Small fire on the side of the road, looks like someone threw a cigarette.',
    lat: -25.7900,
    lng: 28.3100,
    boundary_radius_km: 0.1,
    status: 'received',
    status_index: 0,
    created_at: '2026-01-15T23:00:00Z',
  },
  {
    reference_number: 'FR-2026-015',
    location_text: 'Silver Lakes boundary',
    description: 'Fire in the open field approaching the estate wall.',
    lat: -25.7600,
    lng: 28.3500,
    boundary_radius_km: 1.8,
    status: 'verified',
    status_index: 2,
    created_at: '2026-01-16T00:00:00Z',
  },
  {
    reference_number: 'FR-2026-016',
    location_text: 'Menlyn Maine construction site brush',
    description: 'Debris fire getting out of control due to wind.',
    lat: -25.7800,
    lng: 28.2800,
    boundary_radius_km: 0.4,
    status: 'pending',
    status_index: 1,
    created_at: '2026-01-16T01:00:00Z',
  },
  {
    reference_number: 'FR-2026-017',
    location_text: 'Lynnwood Road crossing',
    description: 'Rubbish burning under the bridge, spreading to dry grass.',
    lat: -25.7600,
    lng: 28.2500,
    boundary_radius_km: 0.2,
    status: 'received',
    status_index: 0,
    created_at: '2026-01-16T02:00:00Z',
  },
  {
    reference_number: 'FR-2026-018',
    location_text: 'Voortrekker Monument hillside',
    description: 'Flames visible on the southern slope from the highway.',
    lat: -25.7700,
    lng: 28.1700,
    boundary_radius_km: 3.0,
    status: 'verified',
    status_index: 2,
    created_at: '2026-01-16T03:00:00Z',
  },
];

const MOCK_NEW_REPORT_RESPONSE = {
  reference_number: 'FR-2026-999',
  message: 'Report submitted successfully',
};
const MOCK_GEOCODE_FORWARD = {
  features: [
    {
      place_name: 'Pretoria, Gauteng, South Africa',
      center: [28.0473, -25.7461],
    },
  ],
};
const MOCK_GEOCODE_REVERSE = {
  features: [
    {
      place_name: '3 Akademia, Pretoria, Gauteng 0083, South Africa',
    },
  ],
};

test.describe('Report a Fire, Frontend (mocked API)',()=>{
    test.beforeEach(async({page})=>{
        //mock GET /api/reports
        await page.route('**/api/users/reported-fires', async (route)=>{
            if(route.request().method()=='GET'){
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify(MOCK_REPORTS),
                });
            }else {
                await route.continue();
            }
        });
        //mock POST /api/reports
        await page.route('**/api/users/reported-fires',async (route)=>{
            if(route.request().method()=='POST'){
                const payload=JSON.parse(route.request().postData()||'{}');
            
            await route.fulfill({
                status: 200,  
                contentType: 'application/json', 
                body: JSON.stringify(MOCK_NEW_REPORT_RESPONSE),
            });
        }else {
            await route.continue();
        }
        });
        await page.route('https://api.mapbox.com/geocoding/v5/mapbox.places/*', async (route) => {
            const url = new URL(route.request().url());
            if (url.pathname.includes('mapbox.places') && !url.pathname.includes('reverse')) {
              await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify(MOCK_GEOCODE_FORWARD),
              });
            } else {
              await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify(MOCK_GEOCODE_REVERSE),
              });
            }
          });
        await page.goto('/user/report')
    });
    test('Map loads and displays',async ({ page }) => {

    await page.waitForSelector('.mapboxgl-canvas');
    await expect(page.locator('text=Failed to load')).toBeHidden();
    await expect(page.locator('input[placeholder*="Drop a pin or type your address"]')).toBeVisible();
  });

})
