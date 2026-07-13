const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { TRAIN_DEV_URL, bridgePageViaSafariSso, classifyUrl } = require('./huanxin_repair_profile_via_safari_sso');

function getAppBaseUrl(url) {
  return String(url || '').split('#')[0] || String(TRAIN_DEV_URL).split('#')[0];
}

function cleanText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

async function ensureAppSurface(page) {
  const listUrl = `${getAppBaseUrl(TRAIN_DEV_URL)}#/train-dev`;
  await page.goto(listUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(3000);

  if (classifyUrl(page.url()) === 'login_required') {
    const bridge = await bridgePageViaSafariSso(page, {
      authUrl: page.url(),
      targetUrl: listUrl,
      waitMs: 8000,
      resultPath: `/tmp/huanxin-stop-env-bridge-${Date.now()}.json`,
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

async function stopEnvironment(page, envName) {
  const row = page.locator('tr', { hasText: envName }).first();
  await row.waitFor({ state: 'visible', timeout: 60000 });
  
  const stopButton = row.locator('button, a').filter({ hasText: '停止' }).first();
  const exists = await stopButton.count();
  if (exists === 0) {
    console.log(`Environment ${envName} has no "停止" button. Might already be stopped/locked.`);
    return;
  }

  console.log(`Clicking "停止" for environment ${envName}...`);
  await stopButton.click({ timeout: 15000 });
  await page.waitForTimeout(2000);

  // Handle confirm dialog if any
  await page.waitForTimeout(2000);
  const confirmBtnList = page.locator('button').filter({ hasText: /确\s*定/ });
  const count = await confirmBtnList.count();
  let confirmBtn = null;
  for (let i = 0; i < count; i++) {
    const btn = confirmBtnList.nth(i);
    if (await btn.isVisible()) {
      confirmBtn = btn;
      break;
    }
  }
  if (confirmBtn) {
    console.log('Confirm dialog detected, clicking "确定"...');
    await confirmBtn.click();
    await page.waitForTimeout(5000);
  } else {
    console.log('No visible confirm button found.');
  }

  console.log(`Waiting for ${envName} to stop...`);
  for (let poll = 0; poll < 30; poll += 1) {
    const rowText = cleanText(await row.textContent().catch(() => ''));
    console.log(`Row status poll ${poll}: ${rowText}`);
    if (rowText.includes('已停止') || rowText.includes('已锁定')) {
      console.log(`SUCCESS: ${envName} is now stopped/locked.`);
      return;
    }
    await page.waitForTimeout(3000);
  }

  throw new Error(`Timeout waiting for ${envName} to enter stopped/locked state.`);
}

async function main() {
  const envName = 'ASI1';
  const { profileDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;

  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(40000);
  
  try {
    await ensureAppSurface(page);
    await stopEnvironment(page, envName);
    console.log(JSON.stringify({ ok: true, envName, stopped: true }));
  } catch (error) {
    console.error(`Error stopping environment ${envName}:`, error);
    console.log(JSON.stringify({ ok: false, error: error.message }));
  } finally {
    await context.close().catch(() => {});
  }
}

main().catch(console.error);
