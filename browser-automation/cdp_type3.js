const { chromium } = require('playwright');
const fs=require('fs');
const URL=fs.readFileSync('/tmp/run_eval_url.txt','utf8').trim();
const CMD="curl -fsSL '"+URL+"' -o /tmp/r.sh && bash /tmp/r.sh";
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  await page.locator('.xterm-screen, .xterm').first().click({force:true}).catch(()=>{});
  await page.waitForTimeout(300);
  await page.locator('.xterm-helper-textarea').first().focus().catch(()=>{});
  // clear any partial line
  await page.keyboard.press('Control+C');
  await page.waitForTimeout(400);
  // insert exact text (no per-key dropping)
  await page.keyboard.insertText(CMD);
  await page.waitForTimeout(500);
  await page.keyboard.press('Enter');
  console.log('INSERTED len', CMD.length);
  await page.waitForTimeout(12000);
  const txt = await page.locator('.xterm-rows').first().innerText().catch(()=>'');
  console.log('TERM TAIL:\n'+txt.split('\n').filter(l=>l.trim()).slice(-30).join('\n'));
  await page.screenshot({path:'/tmp/asi1_term_after.png'}).catch(()=>{});
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
