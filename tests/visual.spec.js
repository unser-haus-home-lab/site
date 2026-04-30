const { test, expect } = require('@playwright/test');

test('homepage visual regression', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Wait 1.5 seconds for the JS animations and the clock to settle
  await page.waitForTimeout(1500);
  
  // Take a full-page snapshot and compare it to the baseline
  await expect(page).toHaveScreenshot('homepage.png', {
    fullPage: true,
    maxDiffPixelRatio: 0.05 // Allow up to 5% pixel difference to prevent flaky tests on font-rendering variations
  });
});
