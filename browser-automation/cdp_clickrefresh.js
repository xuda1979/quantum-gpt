const { chromium } = require('playwright');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // click exactly at the refresh icon location (between 已断开 badge and dropdown)
  await page.mouse.click(751, 224);
  await sleep(4000);
  await page.screenshot({path:'/tmp/asi1_refresh.png'}).catch(()=>{});
  const t = await page.locator('.xterm-rows').first().innerText().catch(()=>'');
  console.log('AFTER:['+t.replace(/\n+/g,' / ').slice(0,160)+']');
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
