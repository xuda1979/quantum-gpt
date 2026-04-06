const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const contexts = browser.contexts();
  for (const ctx of contexts) {
    for (const page of ctx.pages()) {
      const url = page.url();
      if (url.includes('aihuanxin')) {
        console.log('Found page:', url);
        const hasXterm = await page.evaluate(() => {
          const el = document.querySelector('.terminal.xterm');
          const rows = document.querySelector('.terminal.xterm .xterm-rows');
          const allXterm = document.querySelectorAll('[class*="xterm"]');
          const allTerminal = document.querySelectorAll('[class*="terminal"]');
          return {
            hasTerminal: !!el,
            hasRows: !!rows,
            xtermCount: allXterm.length,
            terminalCount: allTerminal.length,
            xtermClasses: Array.from(allXterm).slice(0,5).map(e => e.className.substring(0,80)),
            terminalClasses: Array.from(allTerminal).slice(0,5).map(e => e.className.substring(0,80)),
          };
        });
        console.log(JSON.stringify(hasXterm, null, 2));
      }
    }
  }
  process.exit(0);
})();
