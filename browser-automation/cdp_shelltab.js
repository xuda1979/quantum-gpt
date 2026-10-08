const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  // click the Shell终端 tab button
  const tab = page.locator('.ant-tabs-tab-btn', {hasText:'终端'}).first();
  await tab.click({timeout:8000}).catch(async e=>{ console.log('tabclick err',e.message); await page.getByText('Shell终端').first().click({force:true}).catch(()=>{}); });
  await page.waitForTimeout(5000);
  // look for iframes
  const frames = page.frames();
  console.log('FRAMES:', frames.length);
  for(const f of frames){ console.log('  frame:', f.url().slice(0,110)); }
  // look for xterm / terminal canvas / textarea
  const probe = await page.evaluate(()=>{
    const r={};
    r.xterm = document.querySelectorAll('.xterm,.xterm-screen,.terminal').length;
    r.iframes = Array.from(document.querySelectorAll('iframe')).map(i=>i.src).slice(0,5);
    r.textareas = document.querySelectorAll('textarea').length;
    r.canvas = document.querySelectorAll('canvas').length;
    // any 'open/连接/启动' button in shell panel
    const btns=[]; document.querySelectorAll('button,a,div.ant-btn').forEach(b=>{const t=(b.innerText||'').trim(); if(t&&t.length<=10&&/连接|打开|启动|进入|开启|新建|创建|Open|Connect/.test(t))btns.push(t);});
    r.btns=[...new Set(btns)];
    return r;
  });
  console.log('PROBE:', JSON.stringify(probe));
  await page.screenshot({path:'/tmp/asi1_shelltab.png'}).catch(()=>{});
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
