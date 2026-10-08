const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // Go to 开发环境 (dev environment) list to find start/启动 control.
  const dev = page.getByText('开发环境',{exact:false}).first();
  if (await dev.count().catch(()=>0)) { await dev.click({force:true}).catch(()=>{}); await page.waitForTimeout(2500); }
  await page.screenshot({path:'/tmp/asi1_envlist.png'}).catch(()=>{});
  // collect visible action words
  const words=['启动','开机','重启','运行中','已停止','已锁定','停止','恢复','重新连接'];
  const found={};
  for (const w of words){ const c=await page.getByText(w,{exact:false}).count().catch(()=>0); if(c)found[w]=c; }
  console.log('STATE_WORDS', JSON.stringify(found));
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
