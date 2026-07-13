// Reconnect shell if needed, wait for a LIVE prompt, then run cmdFile, wait, read.
const { chromium } = require('playwright');
const fs=require('fs');
const CMD=fs.readFileSync(process.argv[2],'utf8').trim();
const WAIT=parseInt(process.argv[3]||'8000',10);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  const rows=()=>page.locator('.xterm-rows').first().innerText().catch(()=>'');
  async function live(){ const t=await rows(); return t.includes('# ') && !t.includes('Terminal long time idle'); }
  // try to get a live prompt: click shell tab, refresh, press enter
  for (let attempt=0; attempt<4; attempt++){
    if (await live()) break;
    await page.getByText('Shell终端',{exact:false}).first().click({force:true}).catch(()=>{});
    await sleep(1500);
    // click refresh/reconnect button near badge
    const reload=page.locator('button:has(svg)');
    const rc=await reload.count().catch(()=>0);
    for(let i=0;i<Math.min(rc,8);i++){const b=await reload.nth(i).boundingBox().catch(()=>null); if(b&&b.y<260&&b.x>700&&b.x<770){await reload.nth(i).click({force:true}).catch(()=>{});}}
    await sleep(2500);
    await page.locator('.xterm-screen,.xterm').first().click({force:true}).catch(()=>{});
    await page.locator('.xterm-helper-textarea').first().focus().catch(()=>{});
    await page.keyboard.press('Enter'); await sleep(2500);
  }
  const wasLive=await live();
  // run
  await page.locator('.xterm-screen,.xterm').first().click({force:true}).catch(()=>{});
  await page.locator('.xterm-helper-textarea').first().focus().catch(()=>{});
  await page.keyboard.press('Control+C'); await sleep(400);
  await page.keyboard.insertText(CMD); await sleep(500);
  await page.keyboard.press('Enter');
  await sleep(WAIT);
  const t=await rows();
  console.log('LIVE='+wasLive+' RANlen='+CMD.length);
  console.log('TAIL:\n'+t.split('\n').filter(l=>l.trim()).slice(-30).join('\n'));
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
