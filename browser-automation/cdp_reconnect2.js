const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  // switch to Jupyter tab then back to Shell终端 to force terminal re-init
  await page.locator('.ant-tabs-tab-btn', {hasText:'Jupyter'}).first().click({timeout:6000}).catch(()=>{});
  await page.waitForTimeout(1500);
  await page.locator('.ant-tabs-tab-btn', {hasText:'终端'}).first().click({timeout:6000}).catch(()=>{});
  await page.waitForTimeout(3000);
  // also try clicking any reconnect/refresh control near status
  const reconnnectBtns = await page.evaluate(()=>{
    const out=[];
    document.querySelectorAll('button,.anticon,[class*=reload],[class*=refresh],[title*=连接],[title*=刷新]').forEach(b=>{
      const t=(b.getAttribute('title')||b.getAttribute('aria-label')||b.innerText||'').trim();
      if(t) out.push(t.slice(0,20));
    });
    return [...new Set(out)].slice(0,15);
  });
  console.log('controls:', JSON.stringify(reconnnectBtns));
  await page.locator('.xterm-screen, .xterm').first().click({force:true}).catch(()=>{});
  await page.locator('.xterm-helper-textarea').first().focus().catch(()=>{});
  await page.keyboard.insertText('echo WOKE_$(date +%s)');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  const txt = await page.locator('.xterm-rows').first().innerText().catch(()=>'');
  console.log('TAIL:\n'+txt.split('\n').filter(l=>l.trim()).slice(-6).join('\n'));
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
