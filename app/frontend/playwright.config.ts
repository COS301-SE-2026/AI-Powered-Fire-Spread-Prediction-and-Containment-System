let serverCommand = 'yarn dev';

const config = {
  testDir: './testing',

  timeout: 60000,
  expect: {
    timeout: 15000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { open: 'never' }]],
  use: {
    headless: true,
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',
    actionTimeout: 15000,
    navigationTimeout: 60000,
    trace: 'on-first-retry',
  },
  webServer: {
    command: serverCommand,
    port: 3000,
    reuseExistingServer: !process.env.CI,
    timeout: 240000,
  },
};

module.exports = config;
