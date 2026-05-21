// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: '.',
  testMatch: '**/tests/e2e/**/*.spec.js',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  timeout: 30000,
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'concierge',
      testMatch: 'concierge/tests/e2e/**/*.spec.js',
      use: { baseURL: 'http://localhost:3001' },
    },
    {
      name: 'email_mvp',
      testMatch: 'email_mvp/tests/e2e/**/*.spec.js',
      use: { baseURL: 'http://localhost:3002' },
    },
    {
      name: 'cpe_calculator',
      testMatch: 'cpe_calculator/tests/e2e/**/*.spec.js',
      use: { baseURL: 'http://localhost:3003' },
    },
    {
      name: 'crosssell_mvp',
      testMatch: 'crosssell_mvp/tests/e2e/**/*.spec.js',
      use: { baseURL: 'http://localhost:3004' },
    },
    {
      name: 'drug_reference_mvp',
      testMatch: 'drug_reference_mvp/tests/e2e/**/*.spec.js',
      use: { baseURL: 'http://localhost:3005' },
    },
  ],
});
