const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // find the ASI1 row and click its 打开 action
  const row = page.locator('tr', { hasText: 'ASI1' }).first();
  if (await row.count().catch(()=>0)) {
    const open = row.getByText('打开',{exact:true}).first();
    await open.click({force:true}).catch(async()=>{ await row.getByText('打开',{exact:false}).first().click({force:true}).catch(()=>{}); });
    console.log('CLICKED ASI1 打开');
  } else { console.log('NO ASI1 ROW'); }
  await page.waitForTimeout(4000);
  // a dialog may ask Jupyter/VSCode/Shell — screenshot
  await page.screenshot({path:'/tmp/asi1_open.png'}).catch(()=>{});
  const t = await page.locator('.xterm-rows').first().innerText().catch(()=>'');
  console.log('XTERM:['+t.replace(/\n+/g,' / ').slice(0,160)+']');
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
