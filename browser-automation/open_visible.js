const { chromium } = require('playwright');

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error('Usage: node open_visible.js <url>');
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: false, slowMo: 50 });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  console.log('VISIBLE_BROWSER_READY');
  console.log(page.url());
  process.stdin.resume();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
