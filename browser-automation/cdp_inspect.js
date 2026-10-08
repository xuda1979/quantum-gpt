const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  const page = ctx.pages().find(p=>p.url().includes('train-dev')) || ctx.pages()[0];
  await page.bringToFront().catch(()=>{});
  console.log('URL:', page.url());
  const body = await page.locator('body').innerText().catch(()=>'');
  console.log('--- BODY TEXT (first 1500) ---');
  console.log(body.slice(0,1500));
  // look for terminal/console/jupyter buttons
  for(const kw of ['终端','Terminal','控制台','WebShell','网页终端','JupyterLab','Jupyter','打开','进入','登录','SSH']){
    const loc=page.getByText(kw,{exact:false});
    const n=await loc.count().catch(()=>0);
    if(n) console.log('FOUND text x'+n+':', kw);
  }
  await page.screenshot({path:'/tmp/asi1_env.png', fullPage:false}).catch(()=>{});
  await browser.close().catch(()=>{});
})().catch(e=>{console.error('ERR',e.message)});
