const path = require('path');

const launchOptions = process.env.PLAYWRIGHT_BROWSER_EXECUTABLE
  ? { executablePath: process.env.PLAYWRIGHT_BROWSER_EXECUTABLE }
  : {};

module.exports = {
  testDir: __dirname,
  timeout: 30000,
  workers: 1,
  reporter: 'line',
  use: {
    headless: true,
    launchOptions,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure'
  },
  outputDir: path.join(__dirname, 'test-results')
};
