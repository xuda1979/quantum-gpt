// Click reconnect refresh, wait for live prompt, then immediately run cmd.
const { chromium } = require('playwright');
const fs=require('fs');
const CMD=fs.readFileSync(process.argv[2],'utf8').replace(/\n$/,'');
const WAIT=parseInt(process.argv[3]||'8000',10);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  const rows=()=>page.locator('.xterm-rows').first().innerText().catch(()=>'');
  // click refresh button up to 3x until prompt is live (no 'disconnect' tail)
  let liveNow=false;
  for(let k=0;k<3 && !liveNow;k++){
    await page.mouse.click(751,224); await sleep(4500);
    await page.locator('.xterm-screen,.xterm').first().click({force:true}).catch(()=>{});
    await page.locator('.xterm-helper-textarea').first().focus().catch(()=>{});
    await page.keyboard.press('Enter'); await sleep(1500);
    const t=await rows(); liveNow = t.includes('# ') && !/disconnect/i.test(t.split('\n').filter(x=>x.trim()).slice(-1)[0]||'');
  }
  // run command now
  await page.locator('.xterm-helper-textarea').first().focus().catch(()=>{});
  await page.keyboard.press('Control+C'); await sleep(350);
  await page.keyboard.insertText(CMD); await sleep(450);
  await page.keyboard.press('Enter');
  await sleep(WAIT);
  const t=await rows();
  console.log('LIVE='+liveNow+'\nTAIL:\n'+t.split('\n').filter(l=>l.trim()).slice(-28).join('\n'));
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
