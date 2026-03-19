const { chromium } = require('playwright');

async function main() {
  const context = await chromium.launchPersistentContext(
    process.env.HUANXIN_PROFILE_DIR || 'browser-automation/profile',
    {
    headless: true,
    viewport: { width: 1600, height: 1000 },
    }
  );

  const page = context.pages()[0] || (await context.newPage());
  await page.goto(
    'https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev',
    { waitUntil: 'networkidle', timeout: 180000 }
  );
  await page.waitForTimeout(3000);

  const data = await page.evaluate(() => {
    const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
    const nodes = Array.from(
      document.querySelectorAll(
        'button, a, [role="button"], input, textarea, [contenteditable="true"], .monaco-editor, .xterm, [class*="editor"], [class*="terminal"]'
      )
    );

    const interesting = nodes
      .map((element) => ({
        tag: element.tagName,
        text: clean(element.innerText || element.textContent || ''),
        placeholder: element.getAttribute('placeholder') || '',
        role: element.getAttribute('role') || '',
        className: (element.getAttribute('class') || '').slice(0, 200),
        id: element.id || '',
        editable: element.getAttribute('contenteditable') || '',
      }))
      .filter((entry) => entry.text || entry.placeholder || entry.className || entry.id)
      .slice(0, 250);

    return {
      title: document.title,
      text: clean(document.body.innerText || '').slice(0, 6000),
      interesting,
    };
  });

  await page.screenshot({ path: 'browser-automation/huanxin-live-surface.png', fullPage: true });
  console.log(JSON.stringify(data, null, 2));
  await context.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
