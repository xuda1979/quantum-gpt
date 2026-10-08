const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // count file inputs in main page
  const fi = await page.locator('input[type=file]').count().catch(()=>0);
  console.log('file inputs(before):', fi);
  // click 上传附件
  const up = page.getByText('上传附件',{exact:false}).first();
  const has = await up.count().catch(()=>0);
  console.log('上传附件 present:', has);
  if (has){ await up.click({force:true}).catch(()=>{}); await page.waitForTimeout(1800); }
  await page.screenshot({path:'/tmp/asi1_upload.png'}).catch(()=>{});
  const fi2 = await page.locator('input[type=file]').count().catch(()=>0);
  console.log('file inputs(after):', fi2);
  // dump any dialog text
  const dlg = await page.locator('.ant-modal, [role=dialog]').allInnerTexts().catch(()=>[]);
  console.log('DIALOG:', JSON.stringify(dlg).slice(0,400));
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
