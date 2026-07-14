const config = {
  testDir: '../testing',
  testMatch: [
    '**/reportFire/**/*.spec.@(js|ts|tsx)',
    '**/loginAndRegister/**/*.spec.@(js|ts|tsx)',
    '**/guests/**/*.spec.@(js|ts|tsx)',
  ],
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
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
  },
};

module.exports = config;
