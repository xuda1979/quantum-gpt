const { chromium } = require('playwright');
const ASI1='https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=ASI1';
const PHONE='xuda2025', PASS='Gat2026$$$$';
(async()=>{
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0];
  let page = ctx.pages()[0] || await ctx.newPage();
  await page.goto(ASI1, {waitUntil:'domcontentloaded', timeout:60000}).catch(e=>console.log('goto:',e.message));
  await page.waitForTimeout(3000);
  // switch to password login tab
  await page.getByText('密码登录',{exact:true}).click({timeout:8000}).catch(()=>{});
  await page.waitForTimeout(1000);
  // fill phone + password
  for (const sel of ['input[placeholder*="账号"]','input[placeholder*="手机"]','input[type="text"]']){
    const loc=page.locator(sel).first();
    if(await loc.isVisible().catch(()=>false)){ await loc.fill(PHONE).catch(()=>{}); break; }
  }
  const pw=page.locator('input[type="password"]').first();
  if(await pw.isVisible().catch(()=>false)) await pw.fill(PASS).catch(()=>{});
  // check agreement + auto-login checkboxes
  for(const cb of await page.locator('input[type="checkbox"]').all()){
    if(!(await cb.isChecked().catch(()=>true))) await cb.check({force:true}).catch(()=>{});
  }
  console.log('PREFILLED phone+password+checkboxes. Waiting for you to type CAPTCHA and click 登录...');
  // poll for authenticated state
  const deadline=Date.now()+1200000;
  let lastUrl='';
  while(Date.now()<deadline){
    const url=page.url();
    if(url!==lastUrl){ console.log('url:',url.slice(0,90)); lastUrl=url; }
    if(/train-dev/.test(url) && !/\/auth\/realms\//.test(url)){
      // confirm we left the login page (page content has training surface)
      const body=await page.locator('body').innerText().catch(()=>'');
      if(body.includes('训练')||body.includes('开发')||body.includes('终端')||body.includes('Terminal')||url.includes('environment/dl-')){
        console.log('AUTHENTICATED state=authenticated_or_train_surface url='+url.slice(0,90));
        break;
      }
    }
    await page.waitForTimeout(2000);
  }
  console.log('done');
  await browser.close().catch(()=>{});
})().catch(e=>{console.error('ERR',e.message);process.exit(1)});
