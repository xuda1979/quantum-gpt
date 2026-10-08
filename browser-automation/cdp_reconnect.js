const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // re-click Shell终端 tab to reconnect
  await page.locator('.ant-tabs-tab-btn', {hasText:'终端'}).first().click({timeout:8000}).catch(e=>console.log('tab',e.message));
  await page.waitForTimeout(4000);
  // click the terminal body and press Enter to wake
  await page.locator('.xterm-screen, .xterm').first().click({force:true}).catch(()=>{});
  await page.locator('.xterm-helper-textarea').first().focus().catch(()=>{});
  await page.keyboard.press('Enter');
  await page.waitForTimeout(2500);
  const txt = await page.locator('.xterm-rows').first().innerText().catch(()=>'');
  console.log('TAIL:\n'+txt.split('\n').filter(l=>l.trim()).slice(-8).join('\n'));
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
