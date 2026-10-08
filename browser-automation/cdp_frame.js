const { chromium } = require('playwright');
const fs=require('fs');
const CMD = process.argv[2] ? fs.readFileSync(process.argv[2],'utf8').trim() : null;
const WAIT=parseInt(process.argv[3]||'5000',10);
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  const frames = page.frames();
  console.log('FRAMES', frames.length);
  // find frame containing an xterm
  let target=null;
  for (const f of frames){
    const c = await f.locator('.xterm-rows').count().catch(()=>0);
    if (c>0){ target=f; console.log('XTERM in frame:', f.url().slice(0,90), 'rows-blocks=',c); }
  }
  if(!target){ console.log('NO XTERM FRAME'); await browser.close(); return; }
  if (CMD){
    await target.locator('.xterm-screen,.xterm').first().click({force:true}).catch(()=>{});
    await page.waitForTimeout(250);
    await target.locator('.xterm-helper-textarea').first().focus().catch(()=>{});
    await page.keyboard.press('Control+C'); await page.waitForTimeout(350);
    await page.keyboard.insertText(CMD); await page.waitForTimeout(450);
    await page.keyboard.press('Enter');
    console.log('RAN len', CMD.length);
  }
  await page.waitForTimeout(WAIT);
  const txt = await target.locator('.xterm-rows').first().innerText().catch(()=>'');
  console.log('TERM TAIL:\n'+txt.split('\n').filter(l=>l.trim()).slice(-35).join('\n'));
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
