const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  await page.getByText('Shell终端',{exact:false}).first().click({force:true}).catch(()=>{});
  await page.waitForTimeout(5000);
  await page.screenshot({path:'/tmp/asi1_shell.png'}).catch(()=>{});
  const t = await page.locator('.xterm-rows').first().innerText().catch(()=>'');
  console.log('XTERM:['+t.replace(/\n+/g,' / ').slice(0,200)+']');
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
