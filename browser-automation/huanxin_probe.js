const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { ensureProfileDir } = require('./huanxin_profile');

const HUANXIN_URL =
  'https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev';

function parseArgs(argv) {
  const args = {
    url: HUANXIN_URL,
    headless: true,
    screenshot: 'browser-automation/huanxin-probe.png',
    dumpHtml: 'browser-automation/huanxin-probe.html',
    dumpJson: 'browser-automation/huanxin-probe.json',
    persistent: true,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === '--url') {
      args.url = argv[++i];
      continue;
    }
    if (token === '--headed') {
      args.headless = false;
      continue;
    }
    if (token === '--screenshot') {
      args.screenshot = argv[++i];
      continue;
    }
    if (token === '--dump-html') {
      args.dumpHtml = argv[++i];
      continue;
    }
    if (token === '--dump-json') {
      args.dumpJson = argv[++i];
      continue;
    }
    if (token === '--no-persistent') {
      args.persistent = false;
      continue;
    }
    throw new Error(`Unknown argument: ${token}`);
  }

  return args;
}

async function launchContext(args) {
  if (args.persistent) {
    const profileInfo = ensureProfileDir();
    return chromium.launchPersistentContext(profileInfo.profileDir, {
      headless: args.headless,
      slowMo: args.headless ? 0 : 50,
      viewport: { width: 1440, height: 900 },
    });
  }

  const browser = await chromium.launch({ headless: args.headless, slowMo: args.headless ? 0 : 50 });
  return browser.newContext({ viewport: { width: 1440, height: 900 } });
}

function cleanText(value) {
  return (value || '').replace(/\s+/g, ' ').trim();
}

function classifyState(url, title, bodyText, surfaceSummary) {
  const lowerUrl = (url || '').toLowerCase();
  const lowerTitle = (title || '').toLowerCase();
  const lowerText = (bodyText || '').toLowerCase();

  // OIDC redirect to Keycloak login page — definitive login_required
  if (lowerUrl.includes('/auth/realms/') && lowerUrl.includes('openid-connect/auth')) {
    return 'login_required';
  }

  // Explicit login keywords in URL or body text
  if (
    lowerUrl.includes('login') ||
    lowerText.includes('扫码登录') ||
    (lowerText.includes('登录') && !lowerText.includes('训练') && !lowerText.includes('开发'))
  ) {
    return 'login_required';
  }

  if (surfaceSummary && surfaceSummary.hasLikelyRemoteSurface) {
    return 'authenticated_surface_ready';
  }

  // SPA shell loaded but no content yet — likely still hydrating or stalled.
  if (lowerUrl.includes('kl-web') && !lowerText) {
    return 'spa_loading';
  }

  if (lowerUrl.includes('train-dev') || lowerText.includes('训练') || lowerText.includes('开发')) {
    return 'train_surface_or_project_page';
  }

  return 'unknown';
}

async function waitForUsefulSurface(page) {
  const snapshots = [];

  for (let attempt = 1; attempt <= 3; attempt += 1) {
    if (attempt > 1) {
      await page.reload({ waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
      await page.waitForTimeout(5000);
    }

    const title = await page.title().catch(() => '');
    const url = page.url();
    const bodyText = cleanText(await page.locator('body').innerText().catch(() => ''));
    const surfaceSummary = await collectSurfaceSummary(page).catch(() => ({
      interesting: [],
      likelyTerminalTargets: [],
      likelyEditorTargets: [],
      hasLikelyRemoteSurface: false,
    }));
    const state = classifyState(url, title, bodyText, surfaceSummary);

    snapshots.push({
      attempt,
      title,
      url,
      state,
      bodyPreview: bodyText.slice(0, 400),
      hasLikelyRemoteSurface: surfaceSummary.hasLikelyRemoteSurface,
    });

    if (state !== 'spa_loading') {
      return { title, url, bodyText, surfaceSummary, state, attempts: snapshots };
    }
  }

  const last = snapshots[snapshots.length - 1] || {
    title: '',
    url: page.url(),
    state: 'spa_loading',
    bodyPreview: '',
    hasLikelyRemoteSurface: false,
  };
  const bodyText = cleanText(await page.locator('body').innerText().catch(() => ''));
  const surfaceSummary = await collectSurfaceSummary(page).catch(() => ({
    interesting: [],
    likelyTerminalTargets: [],
    likelyEditorTargets: [],
    hasLikelyRemoteSurface: false,
  }));
  return {
    title: last.title,
    url: last.url,
    bodyText,
    surfaceSummary,
    state: 'spa_loading',
    attempts: snapshots,
  };
}

async function collectSurfaceSummary(page) {
  return page.evaluate(() => {
    const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
    const selectors = [
      'button',
      'a',
      '[role="button"]',
      'input',
      'textarea',
      '[contenteditable="true"]',
      '.monaco-editor',
      '.xterm',
      '[class*="editor"]',
      '[class*="terminal"]',
      '[class*="console"]',
      '[data-testid]'
    ].join(', ');

    const interesting = Array.from(document.querySelectorAll(selectors))
      .map((element) => {
        const text = clean(element.innerText || element.textContent || '');
        const placeholder = element.getAttribute('placeholder') || '';
        const role = element.getAttribute('role') || '';
        const className = (element.getAttribute('class') || '').slice(0, 240);
        const id = element.id || '';
        const editable = element.getAttribute('contenteditable') || '';
        const testId = element.getAttribute('data-testid') || '';
        return {
          tag: element.tagName,
          text: text.slice(0, 200),
          placeholder: placeholder.slice(0, 200),
          role,
          className,
          id,
          editable,
          testId,
        };
      })
      .filter((entry) => entry.text || entry.placeholder || entry.className || entry.id || entry.testId)
      .slice(0, 300);

    const lowerSignals = interesting.map((entry) =>
      [entry.tag, entry.text, entry.placeholder, entry.role, entry.className, entry.id, entry.testId]
        .join(' ')
        .toLowerCase()
    );

    const likelyTerminal = interesting.filter((entry) => {
      const signal = [entry.text, entry.placeholder, entry.className, entry.id, entry.testId].join(' ').toLowerCase();
      return (
        signal.includes('terminal') ||
        signal.includes('console') ||
        signal.includes('shell') ||
        signal.includes('xterm') ||
        signal.includes('命令') ||
        signal.includes('终端')
      );
    });

    const likelyEditor = interesting.filter((entry) => {
      const signal = [entry.text, entry.placeholder, entry.className, entry.id, entry.testId].join(' ').toLowerCase();
      return (
        entry.editable === 'true' ||
        signal.includes('editor') ||
        signal.includes('monaco') ||
        signal.includes('code') ||
        signal.includes('文件') ||
        signal.includes('编辑')
      );
    });

    return {
      interesting,
      likelyTerminalTargets: likelyTerminal.slice(0, 30),
      likelyEditorTargets: likelyEditor.slice(0, 30),
      hasLikelyRemoteSurface: likelyTerminal.length > 0 || likelyEditor.length > 0,
    };
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const profileInfo = args.persistent ? ensureProfileDir() : null;
  const context = await launchContext(args);
  const page = context.pages?.()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);

  await page.goto(args.url, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(8000);

  const { title, url, bodyText, surfaceSummary, state, attempts } = await waitForUsefulSurface(page);
  const links = await page
    .locator('a')
    .evaluateAll((nodes) =>
      nodes
        .map((node) => ({ text: (node.textContent || '').replace(/\s+/g, ' ').trim(), href: node.getAttribute('href') || '' }))
        .filter((item) => item.text || item.href)
        .slice(0, 30)
    )
    .catch(() => []);
  if (args.screenshot) {
    fs.mkdirSync(path.dirname(path.resolve(args.screenshot)), { recursive: true });
    await page.screenshot({ path: path.resolve(args.screenshot), fullPage: true }).catch(() => {});
  }

  if (args.dumpHtml) {
    fs.mkdirSync(path.dirname(path.resolve(args.dumpHtml)), { recursive: true });
    fs.writeFileSync(path.resolve(args.dumpHtml), await page.content(), 'utf8');
  }

  const result = {
    ok: true,
    title,
    url,
    state,
    bodyPreview: bodyText.slice(0, 1200),
    attemptTrace: attempts,
    links,
    surfaceSummary,
    timestamp: new Date().toISOString(),
    usedPersistentProfile: args.persistent,
    profileInfo: profileInfo
      ? {
          profileDir: profileInfo.profileDir,
          isolated: profileInfo.isolated,
          sourceDir: profileInfo.sourceDir,
        }
      : null,
  };

  if (args.dumpJson) {
    fs.mkdirSync(path.dirname(path.resolve(args.dumpJson)), { recursive: true });
    fs.writeFileSync(path.resolve(args.dumpJson), JSON.stringify(result, null, 2), 'utf8');
  }

  console.log(JSON.stringify(result, null, 2));

  await context.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
