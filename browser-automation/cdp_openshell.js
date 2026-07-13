const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  const before = ctx.pages().length;
  // click Shell终端
  const popupP = ctx.waitForEvent('page', {timeout:15000}).catch(()=>null);
  await page.getByText('Shell终端',{exact:false}).first().click({timeout:8000}).catch(async()=>{
    await page.getByText('终端',{exact:false}).first().click({timeout:8000}).catch(()=>{});
  });
  await page.waitForTimeout(4000);
  const popup = await popupP;
  const pages = ctx.pages();
  console.log('pages now:', pages.length, '(was', before+')');
  for(const p of pages){ console.log('  PAGE', p.url().slice(0,110)); }
  const term = popup || pages[pages.length-1];
  if(term){
    await term.bringToFront().catch(()=>{});
    await term.waitForTimeout(3000);
    console.log('TERM URL:', term.url());
    const t = await term.locator('body').innerText().catch(()=>'');
    console.log('TERM BODY (first 600):', t.slice(0,600));
    await term.screenshot({path:'/tmp/asi1_term.png'}).catch(()=>{});
  }
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
