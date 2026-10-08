const { chromium } = require('playwright');
const fs=require('fs');
const URL=fs.readFileSync('/tmp/run_eval_url.txt','utf8').trim();
const CMD="curl -fsSL '"+URL+"' -o /tmp/r.sh && bash /tmp/r.sh";
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // xterm is in main page
  const screen = page.locator('.xterm-screen, .xterm').first();
  const cnt = await page.locator('.xterm').count();
  console.log('xterm count(main):', cnt);
  await screen.click({timeout:8000, force:true}).catch(e=>console.log('click err',e.message));
  await page.waitForTimeout(500);
  // ensure focus on helper textarea
  await page.locator('.xterm-helper-textarea').first().focus().catch(()=>{});
  await page.waitForTimeout(300);
  await page.keyboard.type(CMD, {delay:5});
  await page.waitForTimeout(400);
  await page.keyboard.press('Enter');
  console.log('TYPED len', CMD.length);
  await page.waitForTimeout(9000);
  await page.screenshot({path:'/tmp/asi1_term_after.png'}).catch(()=>{});
  const txt = await page.locator('.xterm-rows').first().innerText().catch(()=>'');
  console.log('TERM TAIL:\n'+txt.split('\n').filter(l=>l.trim()).slice(-25).join('\n'));
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
