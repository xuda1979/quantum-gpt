const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto('https://gemini.google.com/share/246603d1cbff');
  await page.waitForTimeout(5000); // let it render
  const text = await page.evaluate(() => document.body.innerText);
  console.log("TEXT_START");
  console.log(text);
  console.log("TEXT_END");
  await browser.close();
})();
