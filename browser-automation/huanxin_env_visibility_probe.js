const { ensureProfileDir } = require('./huanxin_profile');
const { chromium } = require('playwright');
const { launchPersistentContext } = require('./huanxin_browser_launch');

const URL = process.env.HUANXIN_TRAIN_DEV_URL ||
  'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=AI';

async function collect(page) {
  return page.evaluate(() => {
    const clean = (v) => (v || '').replace(/\s+/g, ' ').trim();
    const bodyText = clean(document.body.innerText || '');
    const rows = Array.from(document.querySelectorAll('tr')).map((tr) => clean(tr.innerText || '')).filter(Boolean);
    const visibleText = bodyText.slice(0, 8000);
    return {
      title: document.title,
      url: location.href,
      visibleHasAi1: visibleText.includes('ai1'),
      visibleHasAI: visibleText.includes('AI'),
      visibleHasAi2: visibleText.includes('ai2'),
      visibleHasEmpty: visibleText.includes('暂无开发环境'),
      visibleHasOnlyMine: visibleText.includes('仅我创建'),
      rowCount: rows.length,
      rowPreview: rows.slice(0, 12),
      bodyPreview: visibleText.slice(0, 1600),
    };
  });
}

async function tryClearOnlyMine(page) {
  const select = page.locator('.ant-select').filter({ hasText: '仅我创建' }).first();
  if (!(await select.count())) return { changed: false, reason: 'only_mine_select_not_found' };
  await select.click({ timeout: 10000 });
  await page.waitForTimeout(1000);

  const options = page.locator('.ant-select-dropdown .ant-select-item-option');
  const count = await options.count();
  for (let i = 0; i < count; i += 1) {
    const option = options.nth(i);
    const text = ((await option.innerText().catch(() => '')) || '').replace(/\s+/g, ' ').trim();
    const classes = await option.getAttribute('class').catch(() => '');
    const isVisible = await option.isVisible().catch(() => false);
    const isSelected = (classes || '').includes('ant-select-item-option-selected');
    if (!isVisible || !text || text.includes('仅我创建') || isSelected) continue;
    await option.click({ timeout: 10000 });
    await page.waitForTimeout(2000);
    return { changed: true, selected: text };
  }

  await page.keyboard.press('Escape').catch(() => {});
  return { changed: false, reason: 'no_visible_alternate_option_found' };
}

async function main() {
  const { profileDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;

  try {
    const page = context.pages()[0] || (await context.newPage());
    page.setDefaultTimeout(30000);
    await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(8000);

    const before = await collect(page);
    const filterAction = await tryClearOnlyMine(page);
    const after = await collect(page);

    console.log(JSON.stringify({ ok: true, before, filterAction, after }, null, 2));
  } finally {
    await context.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
