const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // go to env list
  await page.getByText('开发环境',{exact:false}).first().click({force:true}).catch(()=>{});
  await page.waitForTimeout(2500);
  const rows = await page.locator('tr').allInnerTexts().catch(()=>[]);
  for (const r of rows){ if(/ASI/.test(r)) console.log('ROW:', r.replace(/\n+/g,' | ')); }
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
