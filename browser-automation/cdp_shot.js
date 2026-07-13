const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  await page.waitForTimeout(1500);
  await page.screenshot({path:'/tmp/asi1_now.png'}).catch(()=>{});
  const txt = await page.locator('.xterm-rows').first().innerText().catch(()=>'');
  console.log('ROWS:['+txt.replace(/\n+/g,' / ').slice(0,300)+']');
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
