const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // The reconnect button is the circular-arrow icon next to the 已断开 badge.
  // Try clicking the 已断开 badge itself then the refresh icon.
  const tried=[];
  for (const t of ['已断开','断开']) {
    const el = page.getByText(t, {exact:false}).first();
    if (await el.count().catch(()=>0)) { await el.click({force:true}).catch(()=>{}); tried.push('text:'+t); await page.waitForTimeout(800);}
  }
  // refresh icon: anticon reload / svg sibling. Click button near the badge.
  const reload = page.locator('button:has(svg), .anticon-reload, [aria-label="reload"]');
  const rc = await reload.count().catch(()=>0);
  // click the one positioned right after the badge (heuristic: 2nd control)
  for (let i=0;i<Math.min(rc,6);i++){
    const box = await reload.nth(i).boundingBox().catch(()=>null);
    if (box && box.y<260 && box.x>680 && box.x<760){ await reload.nth(i).click({force:true}).catch(()=>{}); tried.push('btn'+i+'@'+Math.round(box.x)); }
  }
  console.log('TRIED', JSON.stringify(tried));
  await page.waitForTimeout(3500);
  await page.screenshot({path:'/tmp/asi1_reconn.png'}).catch(()=>{});
  const txt = await page.locator('.xterm-rows').first().innerText().catch(()=>'');
  console.log('ROWS:['+txt.replace(/\n+/g,' / ').slice(0,200)+']');
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
