const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error('Usage: node open_persistent.js <url>');
    process.exit(1);
  }

  const userDataDir = path.resolve('browser-automation/profile');
  fs.mkdirSync(userDataDir, { recursive: true });

  const context = await chromium.launchPersistentContext(userDataDir, {
    headless: false,
    slowMo: 50,
    viewport: { width: 1440, height: 900 },
  });

  const page = context.pages()[0] || await context.newPage();
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  console.log('PERSISTENT_BROWSER_READY');
  console.log(page.url());
  process.stdin.resume();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
