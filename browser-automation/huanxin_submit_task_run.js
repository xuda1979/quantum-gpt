#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const {
  TRAIN_DEV_URL,
  bridgePageViaSafariSso,
  classifyUrl,
} = require('./huanxin_repair_profile_via_safari_sso');

const ROOT_DIR = path.resolve(__dirname, '..');

function buildDefaultTaskName() {
  const now = new Date();
  const month = String(now.getUTCMonth() + 1).padStart(2, '0');
  const day = String(now.getUTCDate()).padStart(2, '0');
  const hour = String(now.getUTCHours()).padStart(2, '0');
  const minute = String(now.getUTCMinutes()).padStart(2, '0');
  return `qwen36-35b-grpo-${month}${day}-${hour}${minute}`;
}

function parseArgs(argv) {
  const args = {
    url: TRAIN_DEV_URL,
    waitMs: 12000,
    taskName: buildDefaultTaskName(),
    imageName: 'qwen3.5-27B-35B-122B-397B-031626-zx',
    resourceGroup: 'huanxin-all-resource',
    resourceGroupType: '公共资源组',
    priority: process.env.HUANXIN_TASK_PRIORITY || '中',
    instanceCount: 1,
    acceleratorCardsPerInstance: null,
    cpuPerInstance: null,
    memoryPerInstance: null,
    remoteRoot: '',
    launcherScript: 'scripts/launch_qwen36_35b_a3b_agentic_grpo.sh',
    launcherArgs: [],
    outputDir: '',
    logPath: '',
    overrideCommandFile: '',
    autoOverrideCodeContents: process.env.HUANXIN_AUTO_OVERRIDE_CODECONTENTS !== '0',
    directSubmitFallback: process.env.HUANXIN_DIRECT_SUBMIT_FALLBACK !== '0',
    directSubmitOnly: process.env.HUANXIN_DIRECT_SUBMIT_ONLY === '1',
    ignoreProjectQuotaText: process.env.HUANXIN_IGNORE_PROJECT_QUOTA_TEXT === '1',
    submit: false,
    openTaskListAfterSubmit: true,
    screenshot: 'browser-automation/huanxin-submit-task-run.png',
    dumpHtml: 'browser-automation/huanxin-submit-task-run.html',
    dumpJson: 'browser-automation/huanxin-submit-task-run.json',
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--url') {
      args.url = argv[++index];
      continue;
    }
    if (token === '--wait-ms') {
      args.waitMs = parseInt(argv[++index], 10);
      continue;
    }
    if (token === '--task-name') {
      args.taskName = argv[++index];
      continue;
    }
    if (token === '--image-name') {
      args.imageName = argv[++index];
      continue;
    }
    if (token === '--resource-group') {
      args.resourceGroup = argv[++index];
      continue;
    }
    if (token === '--resource-group-type') {
      args.resourceGroupType = argv[++index];
      continue;
    }
    if (token === '--priority') {
      args.priority = argv[++index];
      continue;
    }
    if (token === '--instance-count') {
      args.instanceCount = parseInt(argv[++index], 10);
      continue;
    }
    if (token === '--accelerator-cards') {
      args.acceleratorCardsPerInstance = parseInt(argv[++index], 10);
      continue;
    }
    if (token === '--cpu-cores') {
      args.cpuPerInstance = parseInt(argv[++index], 10);
      continue;
    }
    if (token === '--memory-gb') {
      args.memoryPerInstance = parseInt(argv[++index], 10);
      continue;
    }
    if (token === '--remote-root') {
      args.remoteRoot = argv[++index];
      continue;
    }
    if (token === '--launcher-script') {
      args.launcherScript = argv[++index];
      continue;
    }
    if (token === '--launcher-arg') {
      args.launcherArgs.push(argv[++index]);
      continue;
    }
    if (token === '--output-dir') {
      args.outputDir = argv[++index];
      continue;
    }
    if (token === '--log-path') {
      args.logPath = argv[++index];
      continue;
    }
    if (token === '--override-command-file') {
      args.overrideCommandFile = argv[++index];
      continue;
    }
    if (token === '--no-auto-codecontents-override') {
      args.autoOverrideCodeContents = false;
      continue;
    }
    if (token === '--no-direct-submit-fallback') {
      args.directSubmitFallback = false;
      continue;
    }
    if (token === '--direct-submit-only') {
      args.directSubmitOnly = true;
      continue;
    }
    if (token === '--ignore-project-quota-text') {
      args.ignoreProjectQuotaText = true;
      continue;
    }
    if (token === '--submit') {
      args.submit = true;
      continue;
    }
    if (token === '--no-task-list') {
      args.openTaskListAfterSubmit = false;
      continue;
    }
    if (token === '--screenshot') {
      args.screenshot = argv[++index];
      continue;
    }
    if (token === '--dump-html') {
      args.dumpHtml = argv[++index];
      continue;
    }
    if (token === '--dump-json') {
      args.dumpJson = argv[++index];
      continue;
    }
    throw new Error(`Unknown argument: ${token}`);
  }

  if (!/^[A-Za-z0-9][A-Za-z0-9()\- ]{0,29}$/.test(args.taskName)) {
    throw new Error(
      `Task name must be <=30 characters, start with a letter/number, and only contain letters, numbers, spaces, parentheses, or hyphens: ${args.taskName}`
    );
  }

  return args;
}

function classifySubmitBlocker(visibleMessages, { ignoreProjectQuotaText = false } = {}) {
  const messages = Array.isArray(visibleMessages) ? visibleMessages : [];
  if (
    !ignoreProjectQuotaText &&
    messages.some((message) => String(message || '').includes('超出项目空间配额'))
  ) {
    return 'project_quota_exceeded';
  }
  return null;
}

function cleanText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function getRoutePath(url) {
  const value = String(url || '');
  const hashIndex = value.indexOf('#');
  if (hashIndex === -1) {
    return '';
  }
  return value.slice(hashIndex + 1).split('?')[0];
}

function getHashSearchParam(url, paramName) {
  const value = String(url || '');
  const hashIndex = value.indexOf('#');
  if (hashIndex === -1) {
    return '';
  }
  const hash = value.slice(hashIndex + 1);
  const queryIndex = hash.indexOf('?');
  if (queryIndex === -1) {
    return '';
  }
  return new URLSearchParams(hash.slice(queryIndex + 1)).get(paramName) || '';
}

function isOnTargetAppRoute(currentUrl, targetUrl) {
  if (classifyUrl(currentUrl) !== 'app_surface' || getRoutePath(currentUrl) !== getRoutePath(targetUrl)) {
    return false;
  }
  const targetName = cleanText(getHashSearchParam(targetUrl, 'name'));
  if (!targetName) {
    return true;
  }
  return cleanText(getHashSearchParam(currentUrl, 'name')) === targetName;
}

function getAppBaseUrl(url) {
  return String(url || '').split('#')[0] || TRAIN_DEV_URL.split('#')[0];
}

function findEnvironmentPage(context, envName) {
  const encodedEnvName = encodeURIComponent(envName || '');
  return context
    .pages()
    .find(
      (candidate) =>
        !candidate.isClosed() &&
        candidate.url().includes('/train-dev/environment/') &&
        (!envName || candidate.url().includes(`name=${encodedEnvName}`) || candidate.url().includes(`name=${envName}`))
    );
}

async function findUsableEnvironmentPage(context, envName) {
  const encodedEnvName = encodeURIComponent(envName || '');
  const candidates = context
    .pages()
    .filter(
      (candidate) =>
        !candidate.isClosed() &&
        candidate.url().includes('/train-dev/environment/') &&
        (!envName || candidate.url().includes(`name=${encodedEnvName}`) || candidate.url().includes(`name=${envName}`))
    )
    .reverse();

  for (const candidate of candidates) {
    if (await pageHasOpenedEnvironmentSurface(candidate)) {
      return candidate;
    }
  }
  return null;
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function applyLauncherEnvOverrides(env, args) {
  if (!args.remoteRoot) {
    return;
  }
  env.HUANXIN_REMOTE_ROOT = args.remoteRoot;
  env.HUANXIN_PREFLIGHT_REMOTE_ROOT = args.remoteRoot;
  env.ASI1_AGENTIC_TASK_REMOTE_ROOT = args.remoteRoot;
  env.ASI1_ARCHIVE_REMOTE_ROOT = args.remoteRoot;
  env.ASI1_EMBEDDED_WHEELHOUSE_REMOTE_ROOT = args.remoteRoot;
  env.ASI1_PREFLIGHT_REMOTE_ROOT = args.remoteRoot;
  env.ASI1_SIGNED_WHEELHOUSE_REMOTE_ROOT = args.remoteRoot;
  env.ASI1_WHEELHOUSE_REMOTE_ROOT = args.remoteRoot;
}

function deriveLaunchSpec(args) {
  if (args.overrideCommandFile) {
    const executionCommand = fs.readFileSync(path.resolve(args.overrideCommandFile), 'utf8').replace(/\r\n/g, '\n');
    return {
      remote_root: args.remoteRoot || '/root/software/quantum-gpt',
      execution_command: executionCommand,
      executionCommand,
      remote_command: executionCommand,
      output_dir: args.outputDir || '',
      log_path: args.logPath || '',
      job_name: args.taskName,
    };
  }
  const scriptPath = path.isAbsolute(args.launcherScript)
    ? args.launcherScript
    : path.resolve(ROOT_DIR, args.launcherScript);
  const env = { ...process.env };
  if (args.outputDir) {
    env.HUANXIN_AGENTIC_OUTPUT_DIR = args.outputDir;
  }
  if (args.logPath) {
    env.HUANXIN_AGENTIC_LOG_PATH = args.logPath;
  }
  applyLauncherEnvOverrides(env, args);

  const output = execFileSync('bash', [scriptPath, '--dry-run', ...args.launcherArgs], {
    cwd: ROOT_DIR,
    env,
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  const spec = JSON.parse(output);
  const remoteRoot = args.remoteRoot || spec.remote_root || '/root/software/quantum-gpt';
  spec.executionCommand = spec.execution_command || `cd ${shellQuote(remoteRoot)} && ${spec.remote_command}`;
  return spec;
}

function inferAcceleratorCardsFromCommand(executionCommand) {
  const nprocMatch = String(executionCommand || '').match(/--nproc_per_node=(\d+)/);
  if (nprocMatch) {
    const parsed = Number.parseInt(nprocMatch[1], 10);
    if (Number.isFinite(parsed) && parsed > 0) {
      return parsed;
    }
  }

  const visibleMatch = String(executionCommand || '').match(/ASCEND_RT_VISIBLE_DEVICES=([^\s&;]+)/);
  if (!visibleMatch) {
    return null;
  }

  const count = visibleMatch[1]
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean).length;
  return count > 0 ? count : null;
}

function resolveResourceConfig(args, launchSpec) {
  const inferredCards = inferAcceleratorCardsFromCommand(launchSpec.executionCommand);
  const acceleratorCardsPerInstance = args.acceleratorCardsPerInstance ?? inferredCards ?? 1;

  return {
    instanceCount: args.instanceCount,
    acceleratorCardsPerInstance,
    cpuPerInstance: args.cpuPerInstance ?? 20,
    memoryPerInstance: args.memoryPerInstance ?? 240,
  };
}

async function clickLocator(candidate, options = {}) {
  try {
    await candidate.click({ timeout: 15000, force: Boolean(options.force) });
    return true;
  } catch (error) {
    if (!options.force) {
      try {
        await candidate.click({ timeout: 15000, force: true });
        return true;
      } catch {}
    }
    try {
      await candidate.evaluate((element) => element.click());
      return true;
    } catch {}
  }
  return false;
}

async function clickByVisibleText(page, text, options = {}) {
  for (const locator of [page.getByText(text, { exact: true }), page.getByText(text)]) {
    const count = await locator.count().catch(() => 0);
    for (let index = 0; index < count; index += 1) {
      const candidate = locator.nth(index);
      const visible = await candidate.isVisible().catch(() => false);
      if (!visible) {
        continue;
      }
      if (await clickLocator(candidate, options)) {
        return true;
      }
    }
  }

  const clicked = await page.evaluate((wanted) => {
    const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
    const elements = Array.from(document.querySelectorAll('button, [role="button"], a, span, div'));
    for (const element of elements) {
      const label = clean(element.innerText || element.textContent || '');
      if (label !== wanted) {
        continue;
      }
      const style = window.getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      if (style.visibility === 'hidden' || style.display === 'none' || rect.width <= 0 || rect.height <= 0) {
        continue;
      }
      const clickable = element.closest('button, [role="button"], a') || element;
      clickable.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
      clickable.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
      clickable.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      return true;
    }
    return false;
  }, text).catch(() => false);
  if (clicked) {
    await page.waitForTimeout(1000);
    return true;
  }
  return false;
}

async function pageHasOpenedEnvironmentSurface(page) {
  const bodyText = cleanText(await page.locator('body').innerText().catch(() => ''));
  const signals = ['Jupyter', 'VSCode', 'Shell终端', '提交任务'];
  return signals.filter((signal) => bodyText.includes(signal)).length >= 2;
}

async function inferEnvironmentName(page, url) {
  const candidates = [url, page.url()];
  for (const candidateUrl of candidates) {
    const hashName = cleanText(getHashSearchParam(candidateUrl, 'name') || '');
    if (hashName) {
      return hashName;
    }
    try {
      const parsed = new URL(candidateUrl);
      const name = cleanText(parsed.searchParams.get('name') || '');
      if (name) {
        return name;
      }
    } catch {}
  }

  const ignoredTitles = new Set(['站内消息', '消息中心']);
  for (const selector of ['.content-title', '.ant-page-header-heading-title']) {
    const titleLocator = page.locator(selector).first();
    const titleCount = await titleLocator.count().catch(() => 0);
    if (titleCount === 0) {
      continue;
    }
    const titleText = cleanText(await titleLocator.innerText().catch(() => ''));
    if (titleText && !ignoredTitles.has(titleText)) {
      return titleText;
    }
  }

  const bodyText = cleanText(await page.locator('body').innerText().catch(() => ''));
  const bodyMatch = bodyText.match(/打开环境\s+([^\s]+)/);
  if (bodyMatch && cleanText(bodyMatch[1])) {
    return cleanText(bodyMatch[1]);
  }

  return '';
}

async function ensureEnvironmentOpened(page, args) {
  const targetEnvName = await inferEnvironmentName(page, args.url);
  if (await pageHasOpenedEnvironmentSurface(page)) {
    const currentEnvName = await inferEnvironmentName(page, page.url());
    if (!targetEnvName || currentEnvName === targetEnvName) {
      return page;
    }
  }

  const envName = targetEnvName;
  if (!envName) {
    return;
  }

  const listUrl = `${getAppBaseUrl(args.url)}#/train-dev`;
  const context = page.context();
  const existingEnvPage = await findUsableEnvironmentPage(context, envName);
  if (existingEnvPage) {
    await existingEnvPage.bringToFront().catch(() => {});
    await existingEnvPage.waitForTimeout(1500);
    return existingEnvPage;
  }

  await page.goto(listUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(3000);

  const row = page.locator('tr', { hasText: envName }).first();
  try {
    await row.waitFor({ state: 'visible', timeout: 60000 });
  } catch (rowErr) {
    if (process.env.HUANXIN_SUBMIT_DEBUG === '1') {
      const dump = await page.evaluate(() => ({
        url: location.href.slice(0, 140),
        trCount: document.querySelectorAll('tr').length,
        body: document.body.innerText.slice(0, 300),
        kcStore: localStorage.getItem('encryptionStore') ? 'present' : 'absent',
      })).catch(() => ({}));
      console.error('HUANXIN_SUBMIT_DEBUG row-timeout dump:', JSON.stringify(dump));
    }
    throw rowErr;
  }
  const openButton = row.getByRole('button', { name: '打开' }).first();
  const startButton = row.getByRole('button', { name: '运行' }).first();

  let openClicked = false;
  for (let poll = 0; poll < 30; poll += 1) {
    const existingPage = await findUsableEnvironmentPage(context, envName);
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
      openClicked = true;
      await page.waitForTimeout(5000);

      const newEnvPage =
        (await findUsableEnvironmentPage(context, envName)) ||
        (context.pages().length > pagesBeforeOpen ? context.pages()[context.pages().length - 1] : null);
      if (newEnvPage) {
        await newEnvPage.bringToFront().catch(() => {});
        await newEnvPage.waitForTimeout(1500);
        return newEnvPage;
      }

      if (await pageHasOpenedEnvironmentSurface(page)) {
        return page;
      }
    }

    await page.waitForTimeout(2000);
  }

  if (!openClicked) {
    const rowText = cleanText(await row.textContent().catch(() => ''));
    throw new Error(`Failed to open environment ${envName}. Row preview: ${rowText}`);
  }
  return page;
}

async function ensureAppSurface(page, args) {
  const targetBase = String(args.url || '').split('#')[0];
  const currentUrl = String(await page.url());
  const alreadyOnApp = Boolean(
    targetBase &&
      currentUrl.startsWith(targetBase) &&
      !String(currentUrl).includes('openid-connect/auth')
  );
  if (!alreadyOnApp) {
    await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);
  }

  let bridge = null;
  if (classifyUrl(page.url()) === 'login_required') {
    bridge = await bridgePageViaSafariSso(page, {
      authUrl: page.url(),
      targetUrl: args.url,
      waitMs: args.waitMs,
      resultPath: `/tmp/huanxin-submit-task-run-${Date.now()}.json`,
    });
    if (!bridge.ok) {
      throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
    }
    await page.waitForTimeout(3000);
  }

  if (!isOnTargetAppRoute(page.url(), args.url)) {
    await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);
  }

  for (let poll = 0; poll < 20; poll += 1) {
    if (await pageHasOpenedEnvironmentSurface(page)) {
      return { bridge, page };
    }
    await page.waitForTimeout(1000);
  }

  const activePage = await ensureEnvironmentOpened(page, args);

  const actualEnvName = await inferEnvironmentName(activePage, activePage.url());
  const targetEnvName = await inferEnvironmentName(page, args.url);
  if (targetEnvName && actualEnvName && actualEnvName !== targetEnvName) {
    throw new Error(`Opened environment name mismatch: expected ${targetEnvName}, got ${actualEnvName}`);
  }

  return { bridge, page: activePage };
}

async function ensureAuthenticatedProjectPage(page, args) {
  const listUrl = `${getAppBaseUrl(args.url)}#/train-dev`;
  await page.goto(listUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(3000);

  let bridge = null;
  if (classifyUrl(page.url()) === 'login_required') {
    bridge = await bridgePageViaSafariSso(page, {
      authUrl: page.url(),
      targetUrl: listUrl,
      waitMs: args.waitMs,
      resultPath: `/tmp/huanxin-submit-task-run-${Date.now()}.json`,
    });
    if (!bridge.ok) {
      throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
    }
    await page.waitForTimeout(3000);
  }

  if (!isOnTargetAppRoute(page.url(), listUrl)) {
    await page.goto(listUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);
  }

  return { bridge, page };
}

async function waitForVisible(locator, timeout = 30000) {
  await locator.waitFor({ state: 'visible', timeout });
  return locator;
}

async function openSubmitDrawer(page) {
  await dismissKnownBlockingModals(page);
  const clickSubmitTask = async () => {
    let clicked = false;
    const submitButtons = page.locator('button, [role="button"], a').filter({ hasText: '提交任务' });
    const submitButtonCount = await submitButtons.count().catch(() => 0);
    for (let index = 0; index < submitButtonCount; index += 1) {
      const candidate = submitButtons.nth(index);
      if (!(await candidate.isVisible().catch(() => false))) {
        continue;
      }
      if (await clickLocator(candidate, { force: true })) {
        clicked = true;
        break;
      }
    }
    if (!clicked) {
      clicked = await clickByVisibleText(page, '提交任务');
    }
    return clicked;
  };

  let clicked = false;
  clicked = await clickSubmitTask();
  if (!clicked) {
    const preview = cleanText(await page.locator('body').innerText().catch(() => '')).slice(0, 1000);
    throw new Error(`Could not click 提交任务. Body preview: ${preview}`);
  }
  await dismissKnownBlockingModals(page);
  if (!(await page.locator('.ant-drawer-content-wrapper').last().isVisible().catch(() => false))) {
    await clickSubmitTask();
  }
  try {
    await waitForVisible(page.locator('.ant-drawer-content-wrapper').last(), 45000);
    await waitForVisible(page.locator('form.train-create-form').last(), 45000);
  } catch (error) {
    await dismissKnownBlockingModals(page);
    await clickSubmitTask();
    await waitForVisible(page.locator('.ant-drawer-content-wrapper').last(), 15000);
    await waitForVisible(page.locator('form.train-create-form').last(), 15000);
  }
  await page.waitForTimeout(1500);
}

async function openSubmitDrawerOldUnused(page) {
  await dismissKnownBlockingModals(page);
  let clicked = false;
  const submitButtons = page.locator('button, [role="button"], a').filter({ hasText: '提交任务' });
  const submitButtonCount = await submitButtons.count().catch(() => 0);
  for (let index = 0; index < submitButtonCount; index += 1) {
    const candidate = submitButtons.nth(index);
    if (!(await candidate.isVisible().catch(() => false))) {
      continue;
    }
    if (await clickLocator(candidate, { force: true })) {
      clicked = true;
      break;
    }
  }
  if (!clicked) {
    clicked = await clickByVisibleText(page, '提交任务');
  }
  if (!clicked) {
    const preview = cleanText(await page.locator('body').innerText().catch(() => '')).slice(0, 1000);
    throw new Error(`Could not click 提交任务. Body preview: ${preview}`);
  }
  try {
    await waitForVisible(page.locator('.ant-drawer-content-wrapper').last(), 45000);
    await waitForVisible(page.locator('form.train-create-form').last(), 45000);
  } catch (error) {
    const diagnostics = await collectSubmitDiagnostics(page).catch(() => null);
    const summary = await collectPageSummary(page).catch(() => null);
    throw new Error(
      `Submit drawer did not open after clicking 提交任务: ${error.message}; diagnostics=${JSON.stringify({
        diagnostics,
        summary,
      }).slice(0, 4000)}`
    );
  }
  await page.waitForTimeout(1500);
}

async function dismissKnownBlockingModals(page) {
  for (let attempt = 0; attempt < 6; attempt += 1) {
    const hasNotice = await page.locator('body').getByText(/系统服务升级维护|知道了/).count().catch(() => 0);
    if (!hasNotice) {
      break;
    }
    const clicked = await page.evaluate(() => {
      const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
      const isVisible = (element) => {
        if (!(element instanceof HTMLElement)) {
          return false;
        }
        const style = window.getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
      };
      const candidates = Array.from(document.querySelectorAll('.ant-modal button, .ant-modal-content button, button, [role="button"]'));
      for (const element of candidates.reverse()) {
        if (!isVisible(element)) {
          continue;
        }
        const text = clean(element.innerText || element.textContent || '');
        if (!/知道了|确定|确\s*定/.test(text)) {
          continue;
        }
        element.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
        element.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
        element.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        return true;
      }
      return false;
    }).catch(() => false);
    if (!clicked) {
      const button = page.getByRole('button', { name: /知道了|确定|确\s*定/ }).last();
      await button.click({ timeout: 5000, force: true }).catch(async () => {
        await button.evaluate((element) => element.click()).catch(() => {});
      });
      await page.keyboard.press('Escape').catch(() => {});
    }
    await page.waitForTimeout(1000);
  }
}

async function selectRadioButtonGroupOption(page, groupText, optionText) {
  const group = page.locator('.ant-radio-group').filter({ hasText: groupText }).first();
  const option = group.locator('label').filter({ hasText: optionText }).first();
  const count = await option.count().catch(() => 0);
  if (count === 0) {
    return false;
  }
  await option.click({ timeout: 15000 });
  return true;
}


async function choosePriority(page, priority) {
  const wanted = cleanText(priority || '');
  if (!wanted) {
    return false;
  }
  const labels = page.locator('label.ant-radio-button-wrapper, label').filter({ hasText: wanted });
  const count = await labels.count().catch(() => 0);
  for (let index = 0; index < count; index += 1) {
    const candidate = labels.nth(index);
    if (!(await candidate.isVisible().catch(() => false))) {
      continue;
    }
    const text = cleanText(await candidate.innerText().catch(() => ''));
    if (text === wanted) {
      await candidate.click({ timeout: 15000 }).catch(async () => {
        await candidate.evaluate((element) => element.click());
      });
      return true;
    }
  }
  return false;
}

async function chooseImageRowFromActiveTab(page, imageName, timeout = 15000) {
  const row = page.locator('tr.ant-table-row').filter({ hasText: imageName }).first();
  await waitForVisible(row, timeout);
  return row;
}

async function chooseImage(page, imageName) {
  let row = null;
  let lastError = null;
  const imageTabs = [null, '自定义镜像', '平台预置镜像'];

  for (const imageTab of imageTabs) {
    if (imageTab) {
      await selectRadioButtonGroupOption(page, '镜像', imageTab).catch(() => false);
      await page.waitForTimeout(1200);
    }
    try {
      row = await chooseImageRowFromActiveTab(page, imageName, imageTab ? 20000 : 12000);
      break;
    } catch (error) {
      lastError = error;
    }
  }

  if (!row) {
    const imageEvents = [];
    for (const event of globalThis.__huanxinSubmitTaskNetworkEvents || []) {
      if (String(event.url || '').includes('/image/')) {
        imageEvents.push({
          url: event.url,
          status: event.status,
          responsePreview: String(event.responsePreview || '').slice(0, 1200),
        });
      }
    }
    const bodyPreview = cleanText(await page.locator('body').innerText().catch(() => '')).slice(0, 3000);
    throw new Error(
      `Could not find image row ${imageName}. Tried active, custom, and preset image tabs. bodyPreview=${bodyPreview} imageEvents=${JSON.stringify(imageEvents)} cause=${lastError ? lastError.message : 'no-row'}`
    );
  }
  const radio = row.locator('input[type="radio"]').first();
  await radio.check({ force: true }).catch(async () => {
    await row.click({ timeout: 15000 });
  });
  const selected = page.locator('.selector-image .ellipsis-text').filter({ hasText: imageName }).first();
  const confirmed = await page
    .waitForFunction(
      ([selectedSelector, expected]) => {
        const pill = document.querySelector(selectedSelector);
        const pillText = pill ? (pill.textContent || '').replace(/\s+/g, ' ').trim() : '';
        const bodyText = (document.body && document.body.innerText ? document.body.innerText : '').replace(/\s+/g, ' ').trim();
        const selectedRow = Array.from(document.querySelectorAll('tr.ant-table-row')).find((element) =>
          (element.textContent || '').includes(expected)
        );
        const rowChecked = selectedRow
          ? Boolean(selectedRow.querySelector('input[type="radio"]')?.checked)
          : false;
        return (
          pillText.includes(expected) ||
          bodyText.includes(`已选镜像： ${expected}`) ||
          bodyText.includes(`已选镜像：${expected}`) ||
          rowChecked
        );
      },
      ['.selector-image .ellipsis-text', imageName],
      { timeout: 15000 }
    )
    .then(() => true)
    .catch(() => false);
  if (!confirmed) {
    const bodyPreview = cleanText(await page.locator('body').innerText().catch(() => '')).slice(0, 3000);
    throw new Error(`Could not confirm image selection ${imageName}. bodyPreview=${bodyPreview}`);
  }
  await waitForVisible(selected, 1000).catch(() => {});
}

async function chooseResourceGroupType(page, label) {
  const group = page.locator('.resource-radio-group').first();
  const normalized = cleanText(label);
  const aliases = [normalized];
  if (normalized === '个人资源组' || normalized.toLowerCase() === 'personal') {
    aliases.push('专属资源组');
  }
  if (normalized === '公共资源组' || normalized.toLowerCase() === 'public') {
    aliases.push('公共资源组');
  }
  let clicked = false;
  for (const alias of aliases) {
    if (await clickByVisibleText(group, alias).catch(() => false)) {
      clicked = true;
      break;
    }
  }
  if (!clicked) {
    const option = group.locator('label').first();
    const count = await option.count().catch(() => 0);
    if (count === 0) {
      return;
    }
    await option.click({ timeout: 15000 }).catch(async () => {
      await option.evaluate((element) => element.click()).catch(() => {});
    });
  }
}

async function chooseResourceGroup(page, resourceGroup) {
  // Try to find the resource group row and select it via radio button
  const row = page.locator('tr.ant-table-row').filter({ hasText: resourceGroup }).first();
  const rowCount = await row.count().catch(() => 0);
  if (rowCount > 0) {
    await row.scrollIntoViewIfNeeded().catch(() => {});
    const radio = row.locator('input[type="radio"]').first();
    const radioCount = await radio.count().catch(() => 0);
    if (radioCount > 0) {
      await radio.check({ force: true }).catch(async () => {
        await row.locator('label').first().click({ force: true }).catch(async () => {
          await row.click({ force: true }).catch(() => {});
        });
      });
    } else {
      await row.click({ force: true }).catch(() => {});
    }
  } else {
    // Fallback: try generic text-based click
    const candidates = [
      page.getByText(resourceGroup, { exact: false }).first(),
      page.locator('label').filter({ hasText: resourceGroup }).first(),
      page.locator('tr').filter({ hasText: resourceGroup }).first(),
    ];
    let clicked = false;
    for (const candidate of candidates) {
      if ((await candidate.count().catch(() => 0)) === 0) continue;
      if (await clickLocator(candidate, { force: true })) {
        clicked = true;
        break;
      }
    }
    if (!clicked) {
      await page.evaluate((wanted) => {
        const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
        const candidates = Array.from(document.querySelectorAll('tr, label, [role="row"]'));
        for (const element of candidates) {
          if (!clean(element.innerText || element.textContent || '').includes(wanted)) continue;
          const radio = element.querySelector('input[type="radio"]');
          if (radio) { radio.click(); return true; }
          element.click();
          return true;
        }
        return false;
      }, resourceGroup).catch(() => false);
    }
  }

  // Wait for confirmation that the resource group is selected
  const confirmed = await page.waitForFunction(
    ([selector, expected]) => {
      const element = document.querySelector(selector);
      const text = element && (element.textContent || '').replace(/\s+/g, ' ').trim();
      return text === expected || document.body.innerText.includes(`已选资源组：${expected}`);
    },
    ['.resource-header p span', resourceGroup],
    { timeout: 10000 }
  ).then(() => true).catch(() => false);

  if (!confirmed) {
    // Check if the radio is now checked
    const radioChecked = await row.locator('input[type="radio"]').first().isChecked().catch(() => {
      // Try by ID
      return page.locator('#basic_resGroupId').isChecked().catch(() => false);
    });
    if (!radioChecked) {
      const currentSelected = cleanText(await page.locator('.resource-header p span').first().innerText().catch(() => ''));
      // '-' means nothing is selected
      if (currentSelected && currentSelected !== '-') {
        return;
      }
      const bodyPreview = cleanText(await page.locator('body').innerText().catch(() => '')).slice(0, 2000);
      throw new Error(`Could not confirm resource group ${resourceGroup}. currentSelected=${currentSelected} bodyPreview=${bodyPreview}`);
    }
  }
  await waitForVisible(page.locator('.resource-header p span').first(), 1000).catch(() => {});
}

async function fillTaskName(page, taskName) {
  const input = page.locator('#basic_name').first();
  await waitForVisible(input, 15000);
  await input.fill(taskName);
}

function executionCommandProbe(executionCommand) {
  const value = String(executionCommand);
  return value.length > 1000 ? value.slice(0, 96) : value;
}

function shouldAutoOverrideCodeContents(executionCommand, overrideCommandFile = '', launchSpec = null) {
  const remoteCommand = String((launchSpec && launchSpec.remote_command) || '').replace(/\r\n/g, '\n');
  const hasStructuredRemoteLines = Boolean(remoteCommand.trim() && remoteCommand.includes('\n'));
  return (
    !overrideCommandFile &&
    (
      String(executionCommand || '').length > 9000 ||
      Boolean(launchSpec && launchSpec.single_line_execution) ||
      hasStructuredRemoteLines
    )
  );
}

function encodeCommandLineForTask(line) {
  return Buffer.from(encodeURIComponent(String(line)), 'utf8').toString('base64');
}

function decodeCommandLineFromTask(encodedLine) {
  return decodeURIComponent(Buffer.from(String(encodedLine), 'base64').toString('utf8'));
}

function codeContentsFromCommand(command) {
  return String(command || '').split('\n').map(encodeCommandLineForTask);
}

function taskCodeCommandFromLaunchSpec(launchSpec = null) {
  if (!launchSpec) {
    return '';
  }
  const remoteCommand = String(launchSpec.remote_command || '').replace(/\r\n/g, '\n');
  if (remoteCommand.trim()) {
    return remoteCommand;
  }
  return String(launchSpec.executionCommand || '').replace(/\r\n/g, '\n');
}

function applyResourceConfigToCreatePayload(payload, resourceConfig) {
  if (!resourceConfig) {
    return payload;
  }
  payload.count = resourceConfig.instanceCount;
  payload.resourceInfo = {
    ...(payload.resourceInfo || {}),
    cpu: resourceConfig.cpuPerInstance,
    gpu: resourceConfig.acceleratorCardsPerInstance,
    mem: resourceConfig.memoryPerInstance,
    gpuType: (payload.resourceInfo || {}).gpuType || '昇腾910B',
  };
  return payload;
}

async function installCreatePayloadOverrideText(page, overrideCommand, source, resourceConfig = null) {
  const overrideCodeContents = codeContentsFromCommand(overrideCommand);
  const summary = {
    source,
    lines: overrideCodeContents.length,
    encodedBytes: overrideCodeContents.reduce((total, item) => total + item.length, 0),
    resourceConfig,
  };
  await page.route('**/kunlun/web/task/v1/create', async (route) => {
    const request = route.request();
    const payload = JSON.parse(request.postData() || '{}');
    payload.codeContents = overrideCodeContents;
    applyResourceConfigToCreatePayload(payload, resourceConfig);
    await route.continue({
      method: request.method(),
      headers: {
        ...request.headers(),
        'content-type': 'application/json',
      },
      postData: JSON.stringify(payload),
    });
  });
  return summary;
}

function normalizePriority(priority) {
  const value = cleanText(priority);
  if (value === '高' || value.toLowerCase() === 'high') {
    return 'high';
  }
  if (value === '低' || value.toLowerCase() === 'low') {
    return 'low';
  }
  return 'med';
}

function inferImagePayload(imageName) {
  if (imageName === 'quantumstim') {
    return {
      imageType: 'personal',
      imageVersion: 'V1',
      imageId: 6273,
      imageName,
      imageGroupId: 3458,
    };
  }
  if (imageName === 'qwen3.5-27B-35B-122B-397B-031626-zx') {
    return {
      imageType: 'preset',
      imageVersion: '',
      imageId: 395,
      imageName,
      imageGroupId: '',
    };
  }
  if (imageName === 'pytorch_v1.1:2.4.0-npu-py310-ubuntu22.04-aarch64') {
    return {
      imageType: 'preset',
      imageVersion: '',
      imageId: 402,
      imageName,
      imageGroupId: '',
    };
  }
  return {
    imageType: 'personal',
    imageVersion: 'V1',
    imageId: null,
    imageName,
    imageGroupId: '',
  };
}

function buildCreateTaskPayload({
  taskName,
  imageName,
  resourceGroup,
  resourceGroupType,
  priority,
  resourceConfig,
  executionCommand,
}) {
  const image = inferImagePayload(imageName);
  if (image.imageId == null) {
    throw new Error(`Direct submit fallback cannot infer image id for ${imageName}`);
  }
  return {
    resGroupId: 154,
    resGroupName: resourceGroup,
    resGroupType:
      cleanText(resourceGroupType) === '公共资源组'
        ? 'public'
        : cleanText(resourceGroupType) === '专属资源组' || cleanText(resourceGroupType) === '个人资源组'
          ? 'personal'
          : cleanText(resourceGroupType) || 'public',
    name: taskName,
    count: resourceConfig.instanceCount,
    imageType: image.imageType,
    imageVersion: image.imageVersion,
    imageId: image.imageId,
    imageName: image.imageName,
    codeContents: codeContentsFromCommand(executionCommand),
    resourceInfo: {
      gpuType: '昇腾910B',
      gpu: resourceConfig.acceleratorCardsPerInstance,
      cpu: resourceConfig.cpuPerInstance,
      mem: resourceConfig.memoryPerInstance,
    },
    imageGroupId: image.imageGroupId,
    presetDatasetIds: [],
    personalDatasetVersionIds: [],
    priority: normalizePriority(priority),
    maxRetry: 0,
  };
}

function summarizeCreateTaskPayload(payload) {
  return {
    name: payload.name,
    lines: Array.isArray(payload.codeContents) ? payload.codeContents.length : 0,
    encodedBytes: Array.isArray(payload.codeContents)
      ? payload.codeContents.reduce((total, item) => total + String(item).length, 0)
      : 0,
    firstLine: Array.isArray(payload.codeContents) && payload.codeContents.length
      ? decodeCommandLineFromTask(payload.codeContents[0]).slice(0, 160)
      : '',
    imageId: payload.imageId,
    imageName: payload.imageName,
    resourceInfo: payload.resourceInfo,
    priority: payload.priority,
  };
}

function redactSensitiveString(value) {
  let text = String(value);
  const envSecrets = [
    process.env.AWS_ACCESS_KEY_ID,
    process.env.AWS_SECRET_ACCESS_KEY,
    process.env.S3_ACCESS_KEY_ID,
    process.env.S3_SECRET_ACCESS_KEY,
  ].filter(Boolean);
  for (const secret of envSecrets) {
    text = text.split(String(secret)).join('[REDACTED]');
  }
  text = text.replace(/(access_key_id\s*=\s*)[^\s'"\\]+/gi, '$1[REDACTED]');
  text = text.replace(/(secret_access_key\s*=\s*)[^\s'"\\]+/gi, '$1[REDACTED]');
  text = text.replace(/(AWS_ACCESS_KEY_ID=)(['"]?)[^\s'"\\]+\2/g, '$1$2[REDACTED]$2');
  text = text.replace(/(AWS_SECRET_ACCESS_KEY=)(['"]?)[^\s'"\\]+\2/g, '$1$2[REDACTED]$2');
  text = text.replace(/(export\s+AWS_ACCESS_KEY_ID=)(['"]?)[^\s'"\\]+\2/g, '$1$2[REDACTED]$2');
  text = text.replace(/(export\s+AWS_SECRET_ACCESS_KEY=)(['"]?)[^\s'"\\]+\2/g, '$1$2[REDACTED]$2');
  text = text.replace(/("access_key_id\s*=\s*)[^"\\]+/gi, '$1[REDACTED]');
  text = text.replace(/("secret_access_key\s*=\s*)[^"\\]+/gi, '$1[REDACTED]');
  text = text.replace(
    /([A-Za-z0-9+/=]{24,})/g,
    (match) => {
      try {
        const decoded = Buffer.from(match, 'base64').toString('utf8');
        const unescaped = decodeURIComponent(decoded);
        if (/access_key_id|secret_access_key|AWS_SECRET_ACCESS_KEY|AWS_ACCESS_KEY_ID/i.test(unescaped)) {
          return '[REDACTED_BASE64_COMMAND]';
        }
      } catch {}
      return match;
    }
  );
  return text;
}

function redactSensitive(value) {
  if (typeof value === 'string') {
    return redactSensitiveString(value);
  }
  if (Array.isArray(value)) {
    return value.map((item) => redactSensitive(item));
  }
  if (value && typeof value === 'object') {
    const result = {};
    for (const [key, item] of Object.entries(value)) {
      if (/secret|credential|access[_-]?key/i.test(key)) {
        result[key] = '[REDACTED]';
      } else {
        result[key] = redactSensitive(item);
      }
    }
    return result;
  }
  return value;
}

async function directCreateTask(page, payload) {
  return page.evaluate(async (createPayload) => {
    const response = await fetch('/kunlun/web/task/v1/create', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(createPayload),
    });
    const text = await response.text();
    let json = null;
    try {
      json = JSON.parse(text);
    } catch {}
    return {
      ok: response.ok && json && json.code === 0,
      status: response.status,
      text: text.slice(0, 4000),
      json,
    };
  }, payload);
}

async function installCreatePayloadOverride(page, commandFile, resourceConfig = null) {
  if (!commandFile) {
    return null;
  }
  const resolved = path.resolve(commandFile);
  const overrideCommand = fs.readFileSync(resolved, 'utf8').replace(/\r\n/g, '\n');
  return installCreatePayloadOverrideText(page, overrideCommand, resolved, resourceConfig);
}

async function fillExecutionCommand(page, executionCommand) {
  const container = page.locator('#shellCode').first();
  await waitForVisible(container, 15000);
  await container.scrollIntoViewIfNeeded().catch(() => {});

  const editor = container.locator('.cm-content[contenteditable="true"], [role="textbox"][contenteditable="true"]').first();
  await waitForVisible(editor, 15000);
  await editor.click({ timeout: 15000 });
  await editor.fill(executionCommand).catch(async () => {
    const modifier = process.platform === 'darwin' ? 'Meta' : 'Control';
    await editor.press(`${modifier}+A`).catch(() => {});
    await editor.press('Backspace').catch(() => {});
    await page.keyboard.insertText(executionCommand);
  });
  const isLargeCommand = executionCommand.length > 1000;
  const verifyTimeout = isLargeCommand ? 45000 : 10000;
  const expectedProbe = executionCommandProbe(executionCommand);
  const verifyPromise = page.waitForFunction(
    ([selector, expected]) => {
      const element = document.querySelector(selector);
      if (!element) {
        return false;
      }
      const text = (element.textContent || element.innerText || '').replace(/\s+/g, ' ').trim();
      const expectedText = expected.replace(/\s+/g, ' ').trim();
      return expectedText
        .split(/\s+/)
        .slice(0, 3)
        .every((token) => text.includes(token));
    },
    ['#shellCode .cm-content', expectedProbe],
    { timeout: verifyTimeout }
  );
  if (isLargeCommand && process.env.HUANXIN_STRICT_COMMAND_VERIFY !== '1') {
    await verifyPromise.catch(() => {
      console.warn('[huanxin_submit_task_run] Large execution command verification timed out; continuing after editor insertion.');
    });
    return;
  }
  await verifyPromise;
}

async function fillNumericInput(page, selector, value) {
  const visibleDrawer = page.locator('.ant-drawer-content-wrapper:visible').last();
  const drawerCandidates = visibleDrawer.locator(selector);
  const drawerCount = await drawerCandidates.count().catch(() => 0);
  const candidates = drawerCount > 0 ? drawerCandidates : page.locator(selector);
  const count = await candidates.count().catch(() => 0);
  let input = candidates.first();
  for (let index = 0; index < count; index += 1) {
    const candidate = candidates.nth(index);
    if (await candidate.isVisible().catch(() => false)) {
      input = candidate;
      break;
    }
  }
  if ((await input.count().catch(() => 0)) === 0) {
    throw new Error(`Could not find numeric input ${selector}`);
  }
  await input.scrollIntoViewIfNeeded().catch(() => {});
  if (!(await input.isVisible().catch(() => false))) {
    const bodyPreview = cleanText(await page.locator('body').innerText().catch(() => '')).slice(0, 2000);
    throw new Error(`Numeric input ${selector} is not visible. bodyPreview=${bodyPreview}`);
  }

  const expected = String(value);
  await input.click({ timeout: 15000 });
  await input.fill(expected).catch(async () => {
    const modifier = process.platform === 'darwin' ? 'Meta' : 'Control';
    await input.press(`${modifier}+A`).catch(() => {});
    await input.press('Backspace').catch(() => {});
    await page.keyboard.insertText(expected);
  });

  await input.evaluate((element, nextValue) => {
    element.value = String(nextValue);
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
    element.blur();
  }, expected).catch(() => {});

  await page.waitForFunction(
    ([inputSelector, nextValue]) => {
      const elements = Array.from(document.querySelectorAll(inputSelector));
      return elements.some((element) => {
        if (!(element instanceof HTMLInputElement)) {
          return false;
        }
        const rawValue = String(element.value || '').trim();
        const ariaValue = String(element.getAttribute('aria-valuenow') || '').trim();
        return rawValue === nextValue || ariaValue === nextValue;
      });
    },
    [selector, expected],
    { timeout: 10000 }
  );
}

async function fillResourceConfig(page, resourceConfig) {
  // All fields may not exist in all form layouts; skip missing ones gracefully.
  // Resource values are also corrected via installCreatePayloadOverride route handler.
  const drawerEl = page.locator('.ant-drawer-content-wrapper:visible').last();
  const tryFill = async (selector, value) => {
    try {
      const candidates = drawerEl.locator(selector);
      const count = await candidates.count().catch(() => 0);
      if (count === 0) return;
      const visible = await candidates.first().isVisible().catch(() => false);
      if (!visible) return;
      await fillNumericInput(page, selector, value);
    } catch (_err) {
      // field missing or not interactable — payload override will correct values
    }
  };
  await tryFill('#basic_count', resourceConfig.instanceCount);
  await tryFill('#basic_formResourceCpuCoreNumber', resourceConfig.cpuPerInstance);
  await tryFill('#basic_formResourceMemory', resourceConfig.memoryPerInstance);
  await tryFill('#basic_formResourceNumber', resourceConfig.acceleratorCardsPerInstance);
}

async function isButtonDisabled(locator) {
  return locator.evaluate((element) => {
    const className = element.getAttribute('class') || '';
    return Boolean(element.disabled) || element.getAttribute('aria-disabled') === 'true' || /disabled/.test(className);
  });
}

async function readInstanceResourceState(page) {
  const readInt = async (selector) => {
    const input = page.locator(selector).first();
    const count = await input.count().catch(() => 0);
    if (count === 0) {
      return null;
    }

    const rawValue = cleanText(
      (await input.inputValue().catch(async () => input.getAttribute('value').catch(() => ''))) || ''
    );
    const directValue = Number.parseInt(rawValue, 10);
    if (Number.isFinite(directValue)) {
      return directValue;
    }

    const ariaValue = cleanText((await input.getAttribute('aria-valuenow').catch(() => '')) || '');
    const parsedAriaValue = Number.parseInt(ariaValue, 10);
    return Number.isFinite(parsedAriaValue) ? parsedAriaValue : null;
  };

  const bodyText = cleanText(await page.locator('body').innerText().catch(() => ''));
  const quotaMatch = bodyText.match(/当前项目空间加速卡剩余\/总量为：\s*(\d+)\s*\/\s*(\d+)卡/);
  const instanceCount = await readInt('#basic_count');
  const acceleratorCardsPerInstance = await readInt('#basic_formResourceNumber');

  return {
    alertText: quotaMatch ? quotaMatch[0] : '',
    quotaRemaining: quotaMatch ? Number.parseInt(quotaMatch[1], 10) : null,
    quotaTotal: quotaMatch ? Number.parseInt(quotaMatch[2], 10) : null,
    instanceCount,
    acceleratorCardsPerInstance,
    cpuPerInstance: await readInt('#basic_formResourceCpuCoreNumber'),
    memoryPerInstance: await readInt('#basic_formResourceMemory'),
    requestedAcceleratorCards:
      Number.isFinite(instanceCount) && Number.isFinite(acceleratorCardsPerInstance)
        ? instanceCount * acceleratorCardsPerInstance
        : null,
  };
}

async function collectVisibleMessages(page) {
  return page.evaluate(() => {
    const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
    const isVisible = (element) => {
      if (!(element instanceof HTMLElement)) {
        return false;
      }
      const style = window.getComputedStyle(element);
      if (!style || style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
        return false;
      }
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };

    const selectors = [
      '.ant-form-item-explain-error',
      '.ant-form-item-explain-warning',
      '.ant-message-notice-content',
      '.ant-notification-notice',
      '.ant-modal-confirm-content',
    ];
    const seen = new Set();
    const messages = [];

    for (const selector of selectors) {
      for (const element of document.querySelectorAll(selector)) {
        if (!isVisible(element)) {
          continue;
        }
        const text = clean(element.textContent || '');
        if (!text || seen.has(text)) {
          continue;
        }
        seen.add(text);
        messages.push(text);
      }
    }

    return messages.slice(0, 20);
  });
}

async function collectVisibleMessagesWithRetry(page, waitMs = 3000, intervalMs = 250) {
  const deadline = Date.now() + waitMs;
  const seen = new Set();

  while (Date.now() <= deadline) {
    const messages = await collectVisibleMessages(page);
    for (const message of messages) {
      seen.add(message);
    }
    if (seen.size > 0) {
      break;
    }
    await page.waitForTimeout(intervalMs);
  }

  return Array.from(seen);
}

async function isSubmitDrawerOpen(page) {
  return page.locator('.ant-drawer-content.train-create-drawer').last().isVisible().catch(() => false);
}

async function collectSubmitDiagnostics(page) {
  return page.evaluate(() => {
    const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
    const isVisible = (element) => {
      if (!(element instanceof HTMLElement)) {
        return false;
      }
      const style = window.getComputedStyle(element);
      if (!style || style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
        return false;
      }
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };
    const rectOf = (element) => {
      const rect = element.getBoundingClientRect();
      return {
        x: Math.round(rect.x),
        y: Math.round(rect.y),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
      };
    };
    const drawers = Array.from(document.querySelectorAll('.ant-drawer-content-wrapper, .ant-drawer-content'))
      .filter(isVisible)
      .map((element) => ({
        className: (element.getAttribute('class') || '').slice(0, 240),
        rect: rectOf(element),
        textPreview: clean(element.innerText || element.textContent || '').slice(0, 1000),
      }));
    const buttons = Array.from(document.querySelectorAll('.ant-drawer-content-wrapper button, .ant-drawer-content button'))
      .filter(isVisible)
      .map((element) => ({
        text: clean(element.innerText || element.textContent || ''),
        disabled: Boolean(element.disabled) || element.getAttribute('aria-disabled') === 'true',
        ariaDisabled: element.getAttribute('aria-disabled'),
        className: (element.getAttribute('class') || '').slice(0, 240),
        rect: rectOf(element),
      }));
    const errors = Array.from(
      document.querySelectorAll('.ant-form-item-explain-error, .ant-form-item-explain-warning, [role="alert"]')
    )
      .filter(isVisible)
      .map((element) => clean(element.innerText || element.textContent || ''))
      .filter(Boolean)
      .slice(0, 40);
    return {
      activeElement: document.activeElement
        ? {
            tagName: document.activeElement.tagName,
            id: document.activeElement.id || '',
            className: (document.activeElement.getAttribute('class') || '').slice(0, 240),
            text: clean(document.activeElement.innerText || document.activeElement.textContent || '').slice(0, 240),
          }
        : null,
      drawerCount: drawers.length,
      drawers: drawers.slice(-4),
      buttons: buttons.slice(-20),
      errors,
    };
  });
}

async function findConfirmButton(page) {
  const drawerButtons = page.locator('.ant-drawer-content-wrapper:visible .ant-drawer-footer button.kl-create-btn');
  const drawerButtonCount = await drawerButtons.count().catch(() => 0);
  for (let index = drawerButtonCount - 1; index >= 0; index -= 1) {
    const candidate = drawerButtons.nth(index);
    if (await candidate.isVisible().catch(() => false)) {
      await candidate.scrollIntoViewIfNeeded().catch(() => {});
      return candidate;
    }
  }

  const createButtons = page.locator('.ant-drawer-content-wrapper:visible button.kl-create-btn');
  const createButtonCount = await createButtons.count().catch(() => 0);
  for (let index = createButtonCount - 1; index >= 0; index -= 1) {
    const candidate = createButtons.nth(index);
    if (await candidate.isVisible().catch(() => false)) {
      await candidate.scrollIntoViewIfNeeded().catch(() => {});
      return candidate;
    }
  }

  const buttons = page.locator('.ant-drawer-content-wrapper:visible').getByRole('button', { name: /确\s*定|确定/ });
  const count = await buttons.count().catch(() => 0);
  for (let index = count - 1; index >= 0; index -= 1) {
    const candidate = buttons.nth(index);
    if (await candidate.isVisible().catch(() => false)) {
      await candidate.scrollIntoViewIfNeeded().catch(() => {});
      return candidate;
    }
  }
  throw new Error('Could not find visible 确 定 button');
}

async function collectPageSummary(page) {
  return page.evaluate(() => {
    const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
    const isVisible = (element) => {
      if (!(element instanceof HTMLElement)) {
        return false;
      }
      const style = window.getComputedStyle(element);
      if (!style || style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
        return false;
      }
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };

    const buttons = Array.from(document.querySelectorAll('button, [role="button"]'))
      .filter(isVisible)
      .map((element) => ({
        text: clean(element.innerText || element.textContent || ''),
        disabled: Boolean(element.disabled) || element.getAttribute('aria-disabled') === 'true',
        className: (element.getAttribute('class') || '').slice(0, 240),
      }))
      .filter((entry) => entry.text || entry.className)
      .slice(0, 120);

    const headings = Array.from(
      document.querySelectorAll('h1, h2, h3, h4, .ant-drawer-title, .ant-modal-title, label, legend')
    )
      .filter(isVisible)
      .map((element) => clean(element.innerText || element.textContent || ''))
      .filter(Boolean)
      .slice(0, 120);

    return {
      title: document.title,
      url: location.href,
      bodyPreview: clean(document.body.innerText || '').slice(0, 7000),
      headings,
      buttons,
    };
  });
}

async function maybeOpenTaskList(page, taskName) {
  try {
    const clicked = await clickByVisibleText(page, '任务列表', { force: true });
    if (!clicked) {
      return {
        opened: false,
        summary: await collectPageSummary(page).catch(() => null),
      };
    }
    await page.waitForTimeout(4000);
    const summary = await collectPageSummary(page);
    return {
      opened: true,
      taskNameVisible: summary.bodyPreview.includes(taskName),
      summary,
    };
  } catch (error) {
    return {
      opened: false,
      error: error.message,
      summary: await collectPageSummary(page).catch(() => null),
    };
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const launchSpec = deriveLaunchSpec(args);
  const resourceConfig = resolveResourceConfig(args, launchSpec);
  let context;
  let launch = null;
  let profileDir = '';
  let isolated = false;
  let sourceDir = '';
  let autoIsolated = false;
  let baseProfileLocked = false;
  if (process.env.HUANXIN_CDP_ENDPOINT) {
    // Drive an already-authenticated browser (e.g. the daemon's on port 9224)
    // instead of launching a fresh one — the SPA never honors stored tokens on
    // fresh init, so a pre-authenticated browser avoids the whole SSO dance.
    const { chromium } = require('playwright');
    const cdpBrowser = await chromium.connectOverCDP(process.env.HUANXIN_CDP_ENDPOINT);
    context = cdpBrowser.contexts()[0] || (await cdpBrowser.newContext());
  } else {
    const profile = ensureProfileDir();
    profileDir = profile.profileDir;
    isolated = profile.isolated;
    sourceDir = profile.sourceDir;
    autoIsolated = profile.autoIsolated;
    baseProfileLocked = profile.baseProfileLocked;
    launch = await launchPersistentContext(profileDir);
    context = launch.context;
  }
  let page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);

  const networkEvents = [];
  globalThis.__huanxinSubmitTaskNetworkEvents = networkEvents;
  page.on('response', async (response) => {
    const request = response.request();
    const method = request.method();
    const url = response.url();
    if (!/\/web\//.test(url) && !/\/api\//.test(url)) {
      return;
    }
    if (!['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
      return;
    }
    let responsePreview = '';
    try {
      responsePreview = (await response.text()).slice(0, 4000);
    } catch (error) {
      responsePreview = `<<unavailable: ${error.message}>>`;
    }
    networkEvents.push({
      method,
      url,
      status: response.status(),
      requestPreview: String(request.postData() || '').slice(0, 2000),
      responsePreview,
    });
  });

  let bridge = null;
  try {
    const appSurface = args.directSubmitOnly
      ? await ensureAuthenticatedProjectPage(page, args)
      : await ensureAppSurface(page, args);
    bridge = appSurface.bridge;
    page = appSurface.page;
    page.setDefaultTimeout(30000);

    if (args.directSubmitOnly) {
      const executionCommand = args.overrideCommandFile
        ? fs.readFileSync(path.resolve(args.overrideCommandFile), 'utf8').replace(/\r\n/g, '\n')
        : taskCodeCommandFromLaunchSpec(launchSpec);
      const directPayload = buildCreateTaskPayload({
        taskName: args.taskName,
        imageName: args.imageName,
        resourceGroup: args.resourceGroup,
        resourceGroupType: args.resourceGroupType,
        priority: args.priority,
        resourceConfig,
        executionCommand,
      });
      const directResponse = args.submit
        ? await directCreateTask(page, directPayload)
        : { ok: false, skipped: true, status: null, text: 'dry_run' };
      const result = {
        ok: true,
        submit: args.submit,
        browserMode: launch ? launch.browserMode : 'cdp',
        launchFallbackUsed: launch ? launch.fallbackUsed : false,
        bridge,
        taskName: args.taskName,
        imageName: args.imageName,
        resourceGroup: args.resourceGroup,
        resourceGroupType: args.resourceGroupType,
        priority: args.priority,
        resourceConfig,
        usedProfile: {
          profileDir: profileDir || 'cdp',
          isolated,
          sourceDir,
          autoIsolated,
          baseProfileLocked,
        },
        launchSpec,
        executionCommand,
        networkEvents,
        submitResult: {
          submitted: Boolean(directResponse.ok),
          blockedReason: directResponse.ok ? null : 'direct_submit_failed',
          clickAttempted: false,
          drawerOpenAfterClick: false,
          postClickNetworkEvents: [],
          visibleMessages: [],
          resourceState: null,
          createPayloadOverride: summarizeCreateTaskPayload(directPayload),
          directSubmitOnly: {
            attempted: true,
            payloadSummary: summarizeCreateTaskPayload(directPayload),
            response: directResponse,
          },
          taskList: null,
        },
        timestamp: new Date().toISOString(),
      };
      const publicResult = redactSensitive(result);
      if (args.dumpJson) {
        fs.writeFileSync(args.dumpJson, JSON.stringify(publicResult, null, 2));
      }
      console.log(JSON.stringify(publicResult, null, 2));
      return;
    }

    await openSubmitDrawer(page);

    await fillTaskName(page, args.taskName);
    await choosePriority(page, args.priority);
    await chooseImage(page, args.imageName);
    await chooseResourceGroupType(page, args.resourceGroupType);
    await chooseResourceGroup(page, args.resourceGroup);
    const shouldOverrideCodeContents = shouldAutoOverrideCodeContents(
      launchSpec.executionCommand,
      args.overrideCommandFile,
      launchSpec
    ) && args.autoOverrideCodeContents;
    const editorCommand = shouldOverrideCodeContents
      ? 'echo __HUANXIN_CODECONTENTS_OVERRIDE__'
      : launchSpec.executionCommand;
    await fillExecutionCommand(page, editorCommand);
    await fillResourceConfig(page, resourceConfig);
    const createPayloadOverride = args.overrideCommandFile
      ? await installCreatePayloadOverride(page, args.overrideCommandFile, resourceConfig)
      : shouldOverrideCodeContents
        ? await installCreatePayloadOverrideText(
            page,
            taskCodeCommandFromLaunchSpec(launchSpec),
            'auto_large_execution_command',
            resourceConfig
          )
        : null;

    const confirmButton = await findConfirmButton(page);
    const confirmDisabled = await isButtonDisabled(confirmButton);
    const preSubmitDiagnostics = await collectSubmitDiagnostics(page);
    if (confirmDisabled) {
      const error = new Error('Confirm button is still disabled after filling required fields');
      error.submitDiagnostics = preSubmitDiagnostics;
      throw error;
    }

    const resourceState = await readInstanceResourceState(page);

    let submitResult = {
      submitted: false,
      blockedReason: null,
      clickAttempted: false,
      drawerOpenAfterClick: await isSubmitDrawerOpen(page),
      postClickNetworkEvents: [],
      visibleMessages: [],
      resourceState,
      createPayloadOverride,
      preSubmitDiagnostics,
      postSubmitDiagnostics: null,
      taskList: null,
    };

    if (args.submit) {
      const preClickEventCount = networkEvents.length;
      submitResult.clickAttempted = true;
      await confirmButton.click({ timeout: 15000, force: true }).catch(async () => {
        await confirmButton.evaluate((element) => element.click());
      });
      await page.waitForTimeout(8000);

      submitResult.drawerOpenAfterClick = await isSubmitDrawerOpen(page);
      submitResult.postClickNetworkEvents = networkEvents.slice(preClickEventCount);
      submitResult.visibleMessages = await collectVisibleMessagesWithRetry(page);
      submitResult.postSubmitDiagnostics = await collectSubmitDiagnostics(page);
      submitResult.submitted = !submitResult.drawerOpenAfterClick;

      submitResult.blockedReason = classifySubmitBlocker(submitResult.visibleMessages, {
        ignoreProjectQuotaText: args.ignoreProjectQuotaText,
      });

      if (submitResult.visibleMessages.some((message) => message.includes('当前项目空间加速卡剩余/总量'))) {
        submitResult.resourceWarning = resourceState.alertText;
      }

      if (args.openTaskListAfterSubmit && submitResult.submitted) {
        submitResult.taskList = await maybeOpenTaskList(page, args.taskName);
        submitResult.submitted = Boolean(submitResult.taskList?.taskNameVisible) || submitResult.submitted;
      }

      if (!submitResult.submitted && !submitResult.blockedReason) {
        submitResult.blockedReason = 'submit_transition_not_observed';
        if (args.directSubmitFallback) {
          const directPayload = buildCreateTaskPayload({
            taskName: args.taskName,
            imageName: args.imageName,
            resourceGroup: args.resourceGroup,
            resourceGroupType: args.resourceGroupType,
            priority: args.priority,
            resourceConfig,
            executionCommand: taskCodeCommandFromLaunchSpec(launchSpec),
          });
          const directResponse = await directCreateTask(page, directPayload);
          submitResult.directSubmitFallback = {
            attempted: true,
            payloadSummary: summarizeCreateTaskPayload(directPayload),
            response: directResponse,
          };
          if (directResponse.ok) {
            submitResult.submitted = true;
            submitResult.blockedReason = null;
            submitResult.drawerOpenAfterClick = false;
            if (args.openTaskListAfterSubmit) {
              submitResult.taskList = await maybeOpenTaskList(page, args.taskName);
            }
          }
        }
      }
    }

    const summary = await collectPageSummary(page);
    const result = {
      ok: !args.submit || (submitResult.submitted && !submitResult.blockedReason),
      submit: args.submit,
      browserMode: launch ? launch.browserMode : 'cdp',
      launchFallbackUsed: launch ? launch.fallbackUsed : false,
      bridge,
      taskName: args.taskName,
      imageName: args.imageName,
      resourceGroup: args.resourceGroup,
      resourceGroupType: args.resourceGroupType,
      priority: args.priority,
      resourceConfig,
      usedProfile: {
        profileDir: profileDir || 'cdp',
        isolated,
        sourceDir,
        autoIsolated,
        baseProfileLocked,
      },
      launchSpec,
      executionCommand: launchSpec.executionCommand,
      networkEvents,
      submitResult,
      ...summary,
      timestamp: new Date().toISOString(),
    };

    if (args.screenshot) {
      fs.mkdirSync(path.dirname(path.resolve(args.screenshot)), { recursive: true });
      await page.screenshot({ path: path.resolve(args.screenshot), fullPage: true }).catch(() => {});
    }
    if (args.dumpHtml) {
      fs.mkdirSync(path.dirname(path.resolve(args.dumpHtml)), { recursive: true });
      fs.writeFileSync(path.resolve(args.dumpHtml), await page.content(), 'utf8');
    }
    if (args.dumpJson) {
      fs.mkdirSync(path.dirname(path.resolve(args.dumpJson)), { recursive: true });
      fs.writeFileSync(path.resolve(args.dumpJson), JSON.stringify(redactSensitive(result), null, 2), 'utf8');
    }

    console.log(JSON.stringify(redactSensitive(result), null, 2));
  } finally {
    if (!process.env.HUANXIN_CDP_ENDPOINT) {
      await context.close().catch(() => {});
    }
  }
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error.stack || error.message || String(error));
    process.exit(1);
  });
}

module.exports = {
  deriveLaunchSpec,
  executionCommandProbe,
  shouldAutoOverrideCodeContents,
  encodeCommandLineForTask,
  decodeCommandLineFromTask,
  codeContentsFromCommand,
  taskCodeCommandFromLaunchSpec,
  normalizePriority,
  inferImagePayload,
  buildCreateTaskPayload,
  summarizeCreateTaskPayload,
  applyResourceConfigToCreatePayload,
  classifySubmitBlocker,
  ensureEnvironmentOpened,
  ensureAppSurface,
  getHashSearchParam,
  getRoutePath,
  isOnTargetAppRoute,
};
