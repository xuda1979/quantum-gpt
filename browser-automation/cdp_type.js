const { chromium } = require('playwright');
const fs=require('fs');
const URL=fs.readFileSync('/tmp/run_eval_url.txt','utf8').trim();
const CMD="curl -fsSL '"+URL+"' -o /tmp/r.sh && bash /tmp/r.sh";
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // find the lab iframe element handle
  const labFrameEl = await page.locator('iframe').filter({}).elementHandle().catch(()=>null);
  // click into the xterm screen of the lab iframe
  const frame = page.frames().find(f=>f.url().includes('/lab'));
  if(!frame){ console.log('NO LAB FRAME'); await browser.close(); return; }
  console.log('lab frame:', frame.url().slice(0,90));
  // click terminal area to focus
  const screen = frame.locator('.xterm-screen, .xterm, .jp-Terminal, .terminal').first();
  await screen.click({timeout:8000}).catch(async e=>{console.log('screen click err',e.message);});
  await page.waitForTimeout(800);
  // type command then Enter (exact keystrokes, no wrapping)
  await page.keyboard.type(CMD, {delay:6});
  await page.waitForTimeout(400);
  await page.keyboard.press('Enter');
  console.log('TYPED CMD len', CMD.length);
  await page.waitForTimeout(6000);
  await page.screenshot({path:'/tmp/asi1_term_after.png'}).catch(()=>{});
  // try read terminal text
  const txt = await frame.locator('.xterm-rows, .xterm-screen').first().innerText().catch(()=>'');
  console.log('TERM TEXT TAIL:', txt.slice(-700));
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
