const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');

function usage() {
  console.error('Usage: node huanxin_open_env.js <envName> [--click-text <text>]');
  process.exit(1);
}

function parseArgs(argv) {
  const envName = argv[0];
  if (!envName) usage();

  let clickText = null;
  for (let index = 1; index < argv.length; index += 1) {
    if (argv[index] === '--click-text') {
      clickText = argv[index + 1] || null;
      index += 1;
      continue;
    }
    usage();
  }

  return { envName, clickText };
}

async function clickByVisibleText(page, text) {
  const exact = page.getByText(text, { exact: true }).first();
  if (await exact.count()) {
    await exact.click({ timeout: 10000 });
    return;
  }

  const fuzzy = page.getByText(text).first();
  if (await fuzzy.count()) {
    await fuzzy.click({ timeout: 10000 });
    return;
  }

  throw new Error(`Could not find clickable text: ${text}`);
}

async function main() {
  const { envName, clickText } = parseArgs(process.argv.slice(2));

  const headless = process.env.HUANXIN_HEADLESS !== '0';
  const holdOpen = process.env.HUANXIN_HOLD_OPEN === '1';

  const { profileDir } = ensureProfileDir();
  const launch = headless
    ? await launchPersistentContext(profileDir)
    : { context: await require('playwright').chromium.launchPersistentContext(profileDir, {
        headless,
        executablePath: require('playwright').chromium.executablePath(),
        viewport: { width: 1600, height: 1000 },
        slowMo: 50,
      }) };
  const context = launch.context;

  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);
  await page.goto(
    'https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev',
    { waitUntil: 'networkidle', timeout: 180000 }
  );
  await page.waitForTimeout(2000);

  const row = page.locator('tr', { hasText: envName }).first();
  await row.waitFor({ state: 'visible' });
  await row.getByRole('button', { name: '打开' }).click();
  await page.waitForTimeout(5000);

  const pages = context.pages();
  const activePage = pages[pages.length - 1];
  await activePage.waitForTimeout(3000);

  if (clickText) {
    await clickByVisibleText(activePage, clickText);
    await activePage.waitForTimeout(5000);
  }

  const summary = await activePage.evaluate(() => {
    const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
    const targets = Array.from(
      document.querySelectorAll(
        'button, a, [role="button"], input, textarea, [contenteditable="true"], .monaco-editor, .xterm, [class*="editor"], [class*="terminal"]'
      )
    )
      .map((element) => ({
        tag: element.tagName,
        text: clean(element.innerText || element.textContent || ''),
        placeholder: element.getAttribute('placeholder') || '',
        className: (element.getAttribute('class') || '').slice(0, 180),
        editable: element.getAttribute('contenteditable') || '',
      }))
      .filter((entry) => entry.text || entry.placeholder || /monaco|xterm|editor|terminal/i.test(entry.className))
      .slice(0, 120);

    return {
      title: document.title,
      url: location.href,
      text: clean(document.body.innerText || '').slice(0, 5000),
      targets,
    };
  });
  await activePage.screenshot({ path: `browser-automation/huanxin-open-${envName}.png`, fullPage: true });
  console.log(JSON.stringify(summary, null, 2));

  if (holdOpen) {
    process.stdin.resume();
    return;
  }

  await context.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
