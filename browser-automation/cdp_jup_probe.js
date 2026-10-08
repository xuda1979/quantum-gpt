const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  await page.getByText('Jupyter',{exact:true}).first().click({force:true}).catch(()=>{});
  await page.waitForTimeout(6000);
  console.log('FRAMES:', page.frames().length);
  for (const f of page.frames()){
    const url=f.url();
    const fi = await f.locator('input[type=file]').count().catch(()=>0);
    const upBtn = await f.getByText('Upload',{exact:false}).count().catch(()=>0);
    const newBtn = await f.locator('text=New').count().catch(()=>0);
    if (url.includes('lab')||url.includes('jupyter')||url.includes('ingress')||fi>0)
      console.log('FRAME', url.slice(0,70), 'fileInputs=',fi,'Upload=',upBtn,'New=',newBtn);
  }
  await page.screenshot({path:'/tmp/asi1_jup.png'}).catch(()=>{});
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
