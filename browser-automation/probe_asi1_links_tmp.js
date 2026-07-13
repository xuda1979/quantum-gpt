const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
(async()=>{
 const {profileDir}=ensureProfileDir();
 const launch=await launchPersistentContext(profileDir);
 const page=launch.context.pages()[0] || await launch.context.newPage();
 await page.goto('https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=ASI1',{waitUntil:'domcontentloaded',timeout:180000});
 await page.waitForTimeout(5000);
 const out=await page.evaluate(()=>{
  const clean=s=>String(s||'').replace(/\s+/g,' ').trim();
  const els=[...document.querySelectorAll('a,button,[role=button]')].map((e,i)=>({i,tag:e.tagName,text:clean(e.innerText||e.textContent),href:e.href||e.getAttribute('href')||'',cls:String(e.className||''),disabled:e.disabled||e.getAttribute('aria-disabled')||''})).filter(x=>x.text||x.href).slice(0,200);
  return {url:location.href, text:clean(document.body.innerText).slice(0,3000), els};
 });
 console.log(JSON.stringify(out,null,2));
 await launch.context.close();
})().catch(e=>{console.error(e);process.exit(1)});
