const { chromium } = require('playwright');
const fs=require('fs');
const CMD=fs.readFileSync(process.argv[2]||'/tmp/eval_cmd.txt','utf8').trim();
const WAIT=parseInt(process.argv[3]||'14000',10);
const IDX=process.argv[4]||'last';
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  const screens = page.locator('.xterm-screen, .xterm');
  const n = await screens.count();
  const sel = IDX==='last' ? screens.last() : screens.nth(parseInt(IDX,10));
  await sel.click({force:true}).catch(()=>{});
  await page.waitForTimeout(300);
  const ta = page.locator('.xterm-helper-textarea');
  const taSel = IDX==='last' ? ta.last() : ta.nth(parseInt(IDX,10));
  await taSel.focus().catch(()=>{});
  await page.keyboard.press('Control+C'); await page.waitForTimeout(400);
  await page.keyboard.insertText(CMD); await page.waitForTimeout(500);
  await page.keyboard.press('Enter');
  console.log('RAN len', CMD.length, 'xterms=', n, 'idx=', IDX);
  await page.waitForTimeout(WAIT);
  const rows = page.locator('.xterm-rows');
  const rn = await rows.count();
  for (let i=0;i<rn;i++){
    const t = await rows.nth(i).innerText().catch(()=>'');
    const lines = t.split('\n').filter(l=>l.trim());
    if (lines.length) { console.log(`--- xterm-rows[${i}] tail ---\n`+lines.slice(-30).join('\n')); }
  }
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
