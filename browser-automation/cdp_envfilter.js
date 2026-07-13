const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // toggle 仅我创建 filter (checkbox/switch) then refresh
  const f = page.getByText('仅我创建',{exact:false}).first();
  if (await f.count().catch(()=>0)) { await f.click({force:true}).catch(()=>{}); await page.waitForTimeout(1500); }
  // click refresh circular button near search
  const rb = page.locator('button:has(svg)').first();
  await rb.click({force:true}).catch(()=>{});
  await page.waitForTimeout(2500);
  await page.screenshot({path:'/tmp/asi1_envfilter.png'}).catch(()=>{});
  // gather row text
  const rows = await page.locator('tr').allInnerTexts().catch(()=>[]);
  console.log('ROWS', JSON.stringify(rows.slice(0,12)));
  const empty = await page.getByText('暂无开发环境',{exact:false}).count().catch(()=>0);
  console.log('EMPTY?', empty);
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
