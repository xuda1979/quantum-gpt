const { chromium } = require('playwright');

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error('Usage: node open_page.js <url>');
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.setDefaultTimeout(30000);

  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.screenshot({ path: 'page-shot.png', fullPage: true });
  console.log(JSON.stringify({
    title: await page.title(),
    url: page.url(),
  }, null, 2));

  await browser.close();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
