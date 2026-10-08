const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { TRAIN_DEV_URL, bridgePageViaSafariSso, classifyUrl } = require('./huanxin_repair_profile_via_safari_sso');

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

function cleanText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function getAppBaseUrl(url) {
  return String(url || '').split('#')[0] || String(TRAIN_DEV_URL).split('#')[0];
}

function findEnvironmentPage(context, envName) {
  const encodedEnvName = encodeURIComponent(envName || '');
  return context.pages().find(
    (candidate) =>
      !candidate.isClosed() &&
      candidate.url().includes('/train-dev/environment/') &&
      (!envName || candidate.url().includes(`name=${encodedEnvName}`) || candidate.url().includes(`name=${envName}`))
  );
}

async function pageLooksLikeEnvironment(page, envName) {
  const url = page.url();
  const encodedEnvName = encodeURIComponent(envName || '');
  if (url.includes('/train-dev/environment/') && (url.includes(`name=${encodedEnvName}`) || url.includes(`name=${envName}`))) {
    return true;
  }

  const bodyText = cleanText(await page.locator('body').innerText().catch(() => ''));
  return bodyText.includes(`打开环境 ${envName}`);
}

async function ensureAppSurface(page, envName) {
  const listUrl = `${getAppBaseUrl(TRAIN_DEV_URL)}#/train-dev`;
  await page.goto(listUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(3000);

  if (classifyUrl(page.url()) === 'login_required') {
    const bridge = await bridgePageViaSafariSso(page, {
      authUrl: page.url(),
      targetUrl: listUrl,
      waitMs: 8000,
      resultPath: `/tmp/huanxin-open-env-${envName}-${Date.now()}.json`,
    });
    if (!bridge.ok) {
      throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
    }
    await page.waitForTimeout(3000);
  }

  if (classifyUrl(page.url()) !== 'app_surface') {
    await page.goto(listUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);
  }
}

async function dismissBlockingAnnouncements(page) {
  await page
    .evaluate(() => {
      const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
      const candidates = Array.from(
        document.querySelectorAll('button, [role="button"], .ant-modal-close, .ant-drawer-close, .close')
      );
      for (const element of candidates) {
        const text = clean(element.innerText || element.textContent || element.getAttribute('aria-label'));
        if (/^(知道了|我知道了|确定|确认|关闭|取消|OK|Close|×|x)$/i.test(text)) {
          element.click();
        }
      }

      for (const selector of ['.system-announcement-wrap', '.mask']) {
        for (const element of document.querySelectorAll(selector)) {
          element.style.pointerEvents = 'none';
        }
      }
    })
    .catch(() => {});
  await page.waitForTimeout(500).catch(() => {});
}

async function openEnvironment(page, envName) {
  const context = page.context();
  const existingEnvPage = findEnvironmentPage(context, envName);
  if (existingEnvPage) {
    await existingEnvPage.bringToFront().catch(() => {});
    await existingEnvPage.waitForTimeout(1500);
    return existingEnvPage;
  }

  if (await pageLooksLikeEnvironment(page, envName)) {
    await page.bringToFront().catch(() => {});
    await page.waitForTimeout(1500);
    return page;
  }

  const row = page.locator('tr', { hasText: envName }).first();
  await row.waitFor({ state: 'visible', timeout: 60000 });
  const openButton = row.getByRole('button', { name: '打开' }).first();
  const startButton = row.getByRole('button', { name: '运行' }).first();

  for (let poll = 0; poll < 30; poll += 1) {
    await dismissBlockingAnnouncements(page);
    const existingPage = findEnvironmentPage(context, envName);
    if (existingPage) {
      await existingPage.bringToFront().catch(() => {});
      await existingPage.waitForTimeout(1500);
      return existingPage;
    }

    const rowText = cleanText(await row.textContent().catch(() => ''));
    const startVisible = await startButton.isVisible().catch(() => false);
    const startEnabled = await startButton.isEnabled().catch(() => false);
    const openEnabled = await openButton.isEnabled().catch(() => false);
    const spinning = await page.locator('.ant-spin-spinning, .ant-spin-blur').count().catch(() => 0);
    const shouldStart = (rowText.includes('已停止') || rowText.includes('已锁定')) && startVisible && startEnabled;

    if (shouldStart && spinning === 0) {
      await startButton.click({ timeout: 15000 });
      await page.waitForTimeout(8000);
      continue;
    }

    if (openEnabled && spinning === 0) {
      const pagesBeforeOpen = context.pages().length;
      await openButton.click({ timeout: 15000 });
      await page.waitForTimeout(5000);

      const newEnvPage =
        findEnvironmentPage(context, envName) ||
        (context.pages().length > pagesBeforeOpen ? context.pages()[context.pages().length - 1] : null);
      if (newEnvPage) {
        await newEnvPage.bringToFront().catch(() => {});
        await newEnvPage.waitForTimeout(1500);
        return newEnvPage;
      }

      if (await pageLooksLikeEnvironment(page, envName)) {
        await page.bringToFront().catch(() => {});
        await page.waitForTimeout(1500);
        return page;
      }
    }

    await page.waitForTimeout(2000);
  }

  const rowText = cleanText(await row.textContent().catch(() => ''));
  throw new Error(`Failed to open environment ${envName}. Row preview: ${rowText}`);
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
  await ensureAppSurface(page, envName);
  const activePage = await openEnvironment(page, envName);
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
