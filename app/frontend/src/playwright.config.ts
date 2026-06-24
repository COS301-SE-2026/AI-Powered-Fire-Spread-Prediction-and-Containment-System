import { defineConfig } from '@playwright/test'

export default defineConfig({
    testDir: './testing',
    use: {
        baseURL: 'http://localhost:3000',
    },
    webServer: {
        command: 'yarn dev',
        url: 'http://localhost:3000',
        reuseExistingServer: true,
    },
});