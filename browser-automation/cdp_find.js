const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  // dump clickable elements containing terminal/jupyter/vscode keywords
  const info = await page.evaluate(()=>{
    const out=[];
    const kws=['终端','Jupyter','VSCode','可视化','打开环境'];
    const els=document.querySelectorAll('a,button,div,span,li');
    for(const e of els){
      const t=(e.innerText||'').trim();
      if(!t||t.length>12) continue;
      for(const k of kws){
        if(t===k||t.includes(k)){
          const r=e.getBoundingClientRect();
          out.push({tag:e.tagName,cls:e.className&&String(e.className).slice(0,60),txt:t,href:e.getAttribute&&e.getAttribute('href'),x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),vis:r.width>0&&r.height>0});
          break;
        }
      }
    }
    return out;
  });
  console.log(JSON.stringify(info,null,1));
  await browser.close().catch(()=>{});
})().catch(e=>console.error('ERR',e.message));
