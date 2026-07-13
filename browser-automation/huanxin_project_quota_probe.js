#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const {
  TRAIN_DEV_URL,
  bridgePageViaSafariSso,
  classifyUrl,
} = require('./huanxin_repair_profile_via_safari_sso');

const BASE_URL = TRAIN_DEV_URL.split('#')[0];
const INTERESTING_PATTERN = [
  '加速卡',
  '配额',
  '用量',
  '资源',
  '开发环境',
  '训练任务',
  '运行',
  '停止',
  '锁定',
  'CPU',
  '内存',
  'NPU',
  'GPU',
  '剩余',
  '总量',
  '卡',
].join('|');

const ROUTES = [
  {
    label: 'train-dev-detail',
    url: TRAIN_DEV_URL,
    menuId: '/train-dev',
    parentMenuText: '模型训练',
  },
  {
    label: 'train-dev-list',
    url: `${BASE_URL}#/train-dev`,
    menuId: '/train-dev',
    parentMenuText: '模型训练',
  },
  {
    label: 'train-task-list',
    url: `${BASE_URL}#/train-task`,
    menuId: '/train-task',
    parentMenuText: '模型训练',
  },
  {
    label: 'project-space-details',
    url: `${BASE_URL}#/project-space-details`,
    menuId: '/project-space-details',
  },
  {
    label: 'project-usage-manage',
    url: `${BASE_URL}#/project-usage-manage`,
    menuId: '/project-usage-manage',
    parentMenuText: '运营运维',
  },
];

function parseArgs(argv) {
  const args = {
    waitMs: 8000,
    dumpJson: 'browser-automation/huanxin-project-quota-probe.json',
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--wait-ms') {
      args.waitMs = parseInt(argv[++index], 10);
      continue;
    }
    if (token === '--dump-json') {
      args.dumpJson = argv[++index];
      continue;
    }
    throw new Error(`Unknown argument: ${token}`);
  }

  return args;
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

function isOnTargetAppRoute(currentUrl, targetUrl) {
  return classifyUrl(currentUrl) === 'app_surface' && getRoutePath(currentUrl) === getRoutePath(targetUrl);
}

async function ensureAppSurface(page, waitMs) {
  await page.goto(TRAIN_DEV_URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(3000);

  let bridge = null;
  if (classifyUrl(page.url()) === 'login_required') {
    bridge = await bridgePageViaSafariSso(page, {
      authUrl: page.url(),
      targetUrl: TRAIN_DEV_URL,
      waitMs,
      resultPath: `/tmp/huanxin-project-quota-probe-${Date.now()}.json`,
    });
    if (!bridge.ok) {
      throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
    }
    await page.waitForTimeout(3000);
  }

  if (!isOnTargetAppRoute(page.url(), TRAIN_DEV_URL)) {
    await page.goto(TRAIN_DEV_URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);
  }

  return bridge;
}

async function maybeOpenParentMenu(page, parentMenuText) {
  if (!parentMenuText) {
    return false;
  }

  const parentMenu = page
    .locator('.ant-menu-submenu-title')
    .filter({ hasText: parentMenuText })
    .first();
  if (!(await parentMenu.count().catch(() => 0))) {
    return false;
  }

  await parentMenu.click({ timeout: 15000, force: true }).catch(() => {});
  await page.waitForTimeout(1000);
  return true;
}

async function tryClearOnlyMineFilter(page) {
  const select = page.locator('.ant-select').filter({ hasText: '仅我创建' }).first();
  if (!(await select.count().catch(() => 0))) {
    return { changed: false, reason: 'filter_not_found' };
  }

  await select.click({ timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(1000);

  const options = page.locator('.ant-select-dropdown .ant-select-item-option');
  const count = await options.count().catch(() => 0);
  for (let index = 0; index < count; index += 1) {
    const option = options.nth(index);
    const text = cleanText(await option.innerText().catch(() => ''));
    const classes = await option.getAttribute('class').catch(() => '');
    const isVisible = await option.isVisible().catch(() => false);
    const isSelected = String(classes || '').includes('ant-select-item-option-selected');
    if (!isVisible || !text || text.includes('仅我创建') || isSelected) {
      continue;
    }
    await option.click({ timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(2000);
    return { changed: true, selected: text };
  }

  await page.keyboard.press('Escape').catch(() => {});
  return { changed: false, reason: 'no_alternate_option_found' };
}

async function navigateToRoute(page, route, waitMs) {
  if (route.menuId === '/train-dev') {
    await page.goto(route.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(waitMs);
    return { ok: true, method: 'direct', menuId: route.menuId, url: page.url() };
  }

  await maybeOpenParentMenu(page, route.parentMenuText);

  const menuItem = page.locator(`li[data-menu-id="${route.menuId}"]`).first();
  const menuCount = await menuItem.count().catch(() => 0);
  if (menuCount > 0) {
    const visible = await menuItem.isVisible().catch(() => false);
    if (visible) {
      await menuItem.click({ timeout: 15000, force: true });
      await page.waitForTimeout(waitMs);
      return { ok: true, method: 'menu', menuId: route.menuId, url: page.url() };
    }
  }

  await page.goto(route.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(waitMs);
  return { ok: true, method: 'direct-fallback', menuId: route.menuId, url: page.url() };
}

async function collectRouteSummary(page, label) {
  return page.evaluate(({ label, patternSource }) => {
    const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
    const pattern = new RegExp(patternSource, 'i');
    const bodyText = document.body ? (document.body.innerText || document.body.textContent || '') : '';
    const normalizedBody = clean(bodyText);
    const lines = bodyText
      .split(/\n+/)
      .map((line) => clean(line))
      .filter(Boolean);
    const interestingLines = lines.filter((line) => pattern.test(line)).slice(0, 120);
    const headings = Array.from(
      document.querySelectorAll('h1, h2, h3, .ant-page-header-heading-title, .ant-card-head-title, .ant-breadcrumb')
    )
      .map((element) => clean(element.innerText || element.textContent || ''))
      .filter(Boolean)
      .slice(0, 40);
    const tableBlocks = Array.from(
      document.querySelectorAll('table, .ant-table, .ant-card, .ant-descriptions, .ant-statistic, .ant-alert, .ant-list')
    )
      .map((element) => clean(element.innerText || element.textContent || ''))
      .filter(Boolean)
      .slice(0, 40);
    const rowPreview = Array.from(document.querySelectorAll('tr, .ant-table-row'))
      .map((element) => clean(element.innerText || element.textContent || ''))
      .filter(Boolean)
      .slice(0, 60);
    const selectedMenu = Array.from(
      document.querySelectorAll('.ant-menu-item-selected, .ant-menu-submenu-selected .ant-menu-title-content')
    )
      .map((element) => clean(element.innerText || element.textContent || ''))
      .filter(Boolean)
      .slice(0, 20);

    return {
      label,
      title: document.title,
      url: location.href,
      headings,
      selectedMenu,
      rowPreview,
      interestingLines,
      tableBlocks,
      bodyPreview: normalizedBody.slice(0, 8000),
    };
  }, { label, patternSource: INTERESTING_PATTERN });
}

async function inspectAcceleratorUsageDetail(page, waitMs) {
  const triggerCandidates = [
    page.getByText('加速卡资源占用详情 查看', { exact: false }).first(),
    page.getByText('加速卡资源占用详情', { exact: false }).first(),
    page.getByRole('button', { name: '查看' }).first(),
    page.getByText(/^查看$/).first(),
  ];

  let clicked = false;
  let clickMethod = null;
  for (const candidate of triggerCandidates) {
    const count = await candidate.count().catch(() => 0);
    if (!count) {
      continue;
    }
    const visible = await candidate.isVisible().catch(() => false);
    if (!visible) {
      continue;
    }
    try {
      await candidate.click({ timeout: 15000, force: true });
      clicked = true;
      clickMethod = 'locator';
      break;
    } catch (_) {
      continue;
    }
  }

  if (!clicked) {
    clicked = await page.evaluate(() => {
      const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
      const isVisible = (element) => {
        if (!(element instanceof Element)) {
          return false;
        }
        const style = window.getComputedStyle(element);
        if (!style || style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
          return false;
        }
        const rect = element.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      };

      const nodes = Array.from(document.querySelectorAll('button, a, [role="button"], .ant-btn, .ant-typography'));
      const target = nodes.find((node) => {
        if (!isVisible(node)) {
          return false;
        }
        const text = clean(node.innerText || node.textContent || '');
        return text.includes('加速卡资源占用详情') || text === '查看';
      });
      if (!target) {
        return false;
      }
      target.click();
      return true;
    }).catch(() => false);
    if (clicked) {
      clickMethod = 'dom';
    }
  }

  if (!clicked) {
    return {
      opened: false,
      reason: 'trigger_not_found',
    };
  }

  await page.waitForTimeout(waitMs);

  const detail = await page.evaluate(({ patternSource }) => {
    const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
    const pattern = new RegExp(patternSource, 'i');
    const isVisible = (element) => {
      if (!(element instanceof Element)) {
        return false;
      }
      const style = window.getComputedStyle(element);
      if (!style || style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
        return false;
      }
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };

    const overlayTexts = Array.from(
      document.querySelectorAll('.ant-modal-root, .ant-modal-wrap, .ant-modal, .ant-drawer, .ant-drawer-content-wrapper')
    )
      .filter(isVisible)
      .map((element) => clean(element.innerText || element.textContent || ''))
      .filter(Boolean)
      .slice(0, 10);

    const bodyText = document.body ? (document.body.innerText || document.body.textContent || '') : '';
    const lines = bodyText
      .split(/\n+/)
      .map((line) => clean(line))
      .filter(Boolean);

    return {
      url: location.href,
      overlayTexts,
      interestingLines: lines.filter((line) => pattern.test(line)).slice(0, 160),
      tableBlocks: Array.from(document.querySelectorAll('table, .ant-table, .ant-descriptions, .ant-card, .ant-list'))
        .filter(isVisible)
        .map((element) => clean(element.innerText || element.textContent || ''))
        .filter(Boolean)
        .slice(0, 40),
      bodyPreview: clean(bodyText).slice(0, 10000),
    };
  }, { patternSource: INTERESTING_PATTERN });

  await page.keyboard.press('Escape').catch(() => {});
  await page.waitForTimeout(500).catch(() => {});

  return {
    opened: true,
    clickMethod,
    ...detail,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const { profileDir, isolated, sourceDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;
  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);

  try {
    const bridge = await ensureAppSurface(page, args.waitMs);
    const routeResults = [];

    for (const route of ROUTES) {
      const navigation = await navigateToRoute(page, route, args.waitMs);
      const filterAction = ['train-dev-list', 'train-task-list'].includes(route.label)
        ? await tryClearOnlyMineFilter(page).catch((error) => ({ changed: false, reason: error.message }))
        : null;
      const summary = await collectRouteSummary(page, route.label);
      const acceleratorUsageDetail = route.label === 'project-space-details'
        ? await inspectAcceleratorUsageDetail(page, args.waitMs).catch((error) => ({
          opened: false,
          reason: error.message,
        }))
        : null;
      routeResults.push({
        navigation,
        filterAction,
        acceleratorUsageDetail,
        ...summary,
      });
    }

    const result = {
      ok: true,
      browserMode: launch.browserMode,
      launchFallbackUsed: launch.fallbackUsed,
      bridge,
      usedProfile: {
        profileDir,
        isolated,
        sourceDir,
      },
      routes: routeResults,
      timestamp: new Date().toISOString(),
    };

    if (args.dumpJson) {
      fs.mkdirSync(path.dirname(path.resolve(args.dumpJson)), { recursive: true });
      fs.writeFileSync(path.resolve(args.dumpJson), JSON.stringify(result, null, 2), 'utf8');
    }

    console.log(JSON.stringify(result, null, 2));
  } finally {
    await context.close().catch(() => {});
  }
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
