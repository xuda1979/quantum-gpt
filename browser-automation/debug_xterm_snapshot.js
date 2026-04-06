const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const pages = browser.contexts().flatMap((ctx) => ctx.pages());
  const target = pages.find((page) => page.url().includes('aihuanxin.cn'));

  if (!target) {
    console.error(JSON.stringify({ ok: false, error: 'no_aihuanxin_page_found' }, null, 2));
    process.exit(1);
  }

  const snapshot = await target.evaluate(() => {
    const rowContainer = document.querySelector('.terminal.xterm .xterm-rows');
    const accessibilityContainer = document.querySelector('.terminal.xterm .xterm-accessibility');
    const helper = document.querySelector('.terminal.xterm .xterm-helper-textarea');
    const viewport = document.querySelector('.terminal.xterm .xterm-viewport');
    const cursor = document.querySelector('.terminal.xterm .xterm-cursor-layer');

    const takeRows = (container) => {
      if (!container) return [];
      return Array.from(container.children).slice(-20).map((row, index) => ({
        index,
        tag: row.tagName,
        className: row.className || '',
        text: (row.textContent || '').replace(/\u00a0/g, ' '),
        html: (row.innerHTML || '').slice(0, 400),
      }));
    };

    return {
      title: document.title,
      url: location.href,
      activeElement: document.activeElement ? {
        tag: document.activeElement.tagName,
        className: document.activeElement.className || '',
      } : null,
      terminalPresent: !!document.querySelector('.terminal.xterm'),
      helperPresent: !!helper,
      helperValue: helper ? helper.value : null,
      viewportScrollTop: viewport ? viewport.scrollTop : null,
      viewportScrollHeight: viewport ? viewport.scrollHeight : null,
      rowCount: rowContainer ? rowContainer.children.length : 0,
      accessibilityCount: accessibilityContainer ? accessibilityContainer.children.length : 0,
      cursorPresent: !!cursor,
      rowTexts: takeRows(rowContainer),
      accessibilityTexts: takeRows(accessibilityContainer),
      terminalText: (document.querySelector('.terminal.xterm')?.textContent || '').replace(/\u00a0/g, ' '),
    };
  });

  console.log(JSON.stringify({ ok: true, snapshot }, null, 2));
  await browser.close();
})();
