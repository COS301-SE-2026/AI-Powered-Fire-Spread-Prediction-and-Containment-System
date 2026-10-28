let serverCommand = 'yarn dev';
if (process.env.CI) {
  serverCommand = 'yarn build && yarn start';
}

const config = {
  testDir: './testing',

  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { open: 'never ' }]],
  use: {
    headless: true,
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',
    actionTimeout: 0,
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'yarn dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
    timeout: 180000,
  },
};

module.exports = config;
