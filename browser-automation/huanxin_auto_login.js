// Self-contained Huanxin auto-login with red-character captcha solving + retry.
//
// Flow: launch persistent context -> if already authenticated, done. Otherwise
// switch to password login, fill credentials, then loop:
//   capture captcha image -> solve with scripts/solve_huanxin_captcha.py ->
//   fill -> submit -> check state. On "图形验证码有误" (captcha incorrect),
//   click the captcha image to refresh and retry, up to --max-attempts times.
//
// Usage:
//   HUANXIN_LOGIN_PHONE=xuda2025 HUANXIN_LOGIN_PASSWORD='...' \
//     node browser-automation/huanxin_auto_login.js --url URL [--max-attempts 10] [--headed]
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');
const { getRequestedProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');

const REPO_ROOT = path.resolve(__dirname, '..');
const SOLVER = path.join(REPO_ROOT, 'scripts', 'solve_huanxin_captcha.py');
const PYTHON = process.env.HUANXIN_SOLVER_PYTHON || path.join(REPO_ROOT, '.venv', 'bin', 'python');

const DEFAULT_URL =
  process.env.HUANXIN_TRAIN_DEV_URL ||
  'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-868c196fb82d3e0b8cfbbe826d8afd0a?name=ASI2';

function parseArgs(argv) {
  const args = {
    url: DEFAULT_URL,
    timeout: 60,
    maxAttempts: 12,
    headed: process.env.HUANXIN_HEADLESS === '0',
    captchaImage: 'browser-automation/huanxin-autologin-captcha.png',
    screenshot: 'browser-automation/huanxin-autologin.png',
  };
  for (let i = 0; i < argv.length; i += 1) {
    const t = argv[i];
    if (t === '--url') { args.url = argv[++i]; continue; }
    if (t === '--timeout') { args.timeout = Number(argv[++i]); continue; }
    if (t === '--max-attempts') { args.maxAttempts = Number(argv[++i]); continue; }
    if (t === '--headed') { args.headed = true; continue; }
    if (t === '--headless') { args.headed = false; continue; }
    if (t === '--captcha-image') { args.captchaImage = argv[++i]; continue; }
    if (t === '--screenshot') { args.screenshot = argv[++i]; continue; }
  }
  return args;
}

function cleanText(v) { return (v || '').replace(/\s+/g, ' ').trim(); }

function classifyPage(url, bodyText) {
  const u = (url || '').toLowerCase();
  const t = (bodyText || '').toLowerCase();
  if (u.includes('/auth/realms/') || u.includes('openid-connect/auth')) return 'login_required';
  if (t.includes('扫码登录') || t.includes('密码登录') || t.includes('获取验证码')) return 'login_required';
  if (u.includes('train-dev') || t.includes('训练') || t.includes('开发')) return 'authenticated_or_train_surface';
  return 'unknown';
}

async function summarize(page) {
  const bodyText = cleanText(await page.locator('body').innerText().catch(() => ''));
  return {
    state: classifyPage(page.url(), bodyText),
    title: await page.title().catch(() => ''),
    url: page.url(),
    bodyPreview: bodyText.slice(0, 400),
  };
}

async function readErrorText(page) {
  return page
    .locator('.alert, #code-error, [class*="error"], [class*="Error"], .ant-message, .el-message')
    .evaluateAll((nodes) => nodes.map((n) => n.innerText || n.textContent || '').join(' '))
    .catch(() => '');
}

async function launchContext(profileDir, headed) {
  if (!headed) {
    const launch = await launchPersistentContext(profileDir);
    return launch.context;
  }
  const executablePath = process.env.HUANXIN_BROWSER_EXECUTABLE_PATH || chromium.executablePath();
  return chromium.launchPersistentContext(profileDir, {
    headless: false, executablePath, slowMo: 50, viewport: { width: 1440, height: 900 },
  });
}

async function switchToPasswordLogin(page) {
  await page.getByText('密码登录', { exact: true }).click({ timeout: 8000 }).catch(async () => {
    await page.evaluate(() => {
      if (window.app && typeof window.app.toggleLogin === 'function') window.app.toggleLogin(2, 'click');
    });
  });
  await page.waitForTimeout(600);
}

async function fillCredentials(page, phone, password) {
  await page.evaluate(({ phone, password }) => {
    if (window.app) {
      if (typeof window.app.toggleLogin === 'function') window.app.toggleLogin(2, 'click');
      window.app.agreement = true;
      window.app.rememberMe = true;
      window.app.form = { ...window.app.form, username: phone, phoneNumber: phone, password, terms: true };
      window.app.origin = 'password';
      window.app.isPwsLoginType = true;
    }
  }, { phone, password });
  const u = page.locator('#username, input[name="username"], input[placeholder*="用户名"], input[placeholder*="手机"]').first();
  if (await u.count()) await u.fill(phone).catch(() => {});
  const p = page.locator('#password, input[name="password"], input[type="password"], input[placeholder*="密码"]').first();
  if (await p.count()) await p.fill(password).catch(() => {});
}

async function ensureCheckboxes(page) {
  await page.evaluate(() => {
    if (window.app) {
      window.app.agreement = true; window.app.rememberMe = true;
      window.app.form = { ...window.app.form, terms: true };
    }
  });
  const boxes = await page.locator('input[type="checkbox"], .ant-checkbox-input').all();
  for (const box of boxes) {
    const checked = await box.isChecked().catch(() => false);
    if (!checked) {
      await box.check({ force: true }).catch(async () => {
        await box.evaluate((el) => { el.checked = true; el.dispatchEvent(new Event('change', { bubbles: true })); });
      });
    }
  }
}

function captchaImgLocator(page) {
  return page.locator('img[alt*="图形验证码"], .captcha-code img, .captcha img, img[src*="captcha"], img[src*="kaptcha"]').first();
}

async function saveCaptchaImage(page, targetPath) {
  const resolved = path.resolve(targetPath);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  const img = captchaImgLocator(page);
  if (await img.count()) {
    const visible = await img.isVisible().catch(() => false);
    if (visible) {
      await img.screenshot({ path: resolved }).catch(() => null);
      if (fs.existsSync(resolved)) return resolved;
    }
  }
  // Fallback: clip next to the captcha input.
  const input = page.locator('#captchaCode, input[name="captchaCode"], input[placeholder*="图形验证码"]').first();
  const box = await input.boundingBox().catch(() => null);
  if (box) {
    const clip = {
      x: Math.max(0, box.x + box.width * 0.66), y: Math.max(0, box.y - 18),
      width: Math.min(180, box.width * 0.36), height: Math.min(90, box.height + 36),
    };
    await page.screenshot({ path: resolved, clip }).catch(() => null);
    if (fs.existsSync(resolved)) return resolved;
  }
  return null;
}

function solveCaptcha(imagePath) {
  try {
    const out = execFileSync(PYTHON, [SOLVER, imagePath], { encoding: 'utf8', timeout: 30000 });
    return cleanText(out);
  } catch (e) {
    return '';
  }
}

async function fillCaptcha(page, value) {
  await page.evaluate((v) => {
    if (window.app) window.app.form = { ...window.app.form, captchaCode: v };
  }, value);
  const input = page.locator('#captchaCode, input[name="captchaCode"], input[placeholder*="图形验证码"]').first();
  if (await input.count()) {
    await input.fill('').catch(() => {});
    await input.fill(value).catch(() => {});
  }
}

async function refreshCaptcha(page) {
  const img = captchaImgLocator(page);
  if (await img.count()) {
    await img.click({ timeout: 4000 }).catch(() => {});
  }
  await page.waitForTimeout(900);
}

async function submitLogin(page) {
  await page.locator('#kc-login, [name="login"], text=登录').first().click({ force: true, timeout: 8000 }).catch(async () => {
    await page.evaluate(() => { if (window.app && typeof window.app.login === 'function') window.app.login(true); });
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const phone = process.env.HUANXIN_LOGIN_PHONE || '';
  const password = process.env.HUANXIN_LOGIN_PASSWORD || '';
  if (!phone || !password) {
    console.error(JSON.stringify({ ok: false, state: 'error', message: 'HUANXIN_LOGIN_PHONE and HUANXIN_LOGIN_PASSWORD required' }));
    process.exit(2);
  }
  const profileDir = getRequestedProfileDir();
  fs.mkdirSync(profileDir, { recursive: true });
  const context = await launchContext(profileDir, args.headed);
  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);

  const attempts = [];
  try {
    await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(4000);
    let s = await summarize(page);
    if (s.state === 'authenticated_or_train_surface') {
      console.log(JSON.stringify({ ok: true, alreadyAuthenticated: true, ...s }, null, 2));
      return;
    }
    await switchToPasswordLogin(page);
    await fillCredentials(page, phone, password);
    await ensureCheckboxes(page);

    for (let attempt = 1; attempt <= args.maxAttempts; attempt += 1) {
      const imgPath = await saveCaptchaImage(page, args.captchaImage);
      const code = imgPath ? solveCaptcha(imgPath) : '';
      attempts.push({ attempt, code, imgPath });
      if (process.env.HUANXIN_LOGIN_DEBUG === '1') {
        console.error(JSON.stringify({ attempt, code, imgPath }));
      }
      if (!code) {
        await refreshCaptcha(page);
        continue;
      }
      await fillCaptcha(page, code);
      await ensureCheckboxes(page);
      await submitLogin(page);
      await page.waitForTimeout(3500);
      s = await summarize(page);
      if (s.state === 'authenticated_or_train_surface') {
        console.log(JSON.stringify({ ok: true, attempts: attempt, code, ...s }, null, 2));
        return;
      }
      const err = cleanText(await readErrorText(page));
      attempts[attempts.length - 1].error = err.slice(0, 200);
      // Captcha wrong or any login error: refresh captcha and retry.
      await refreshCaptcha(page);
      await fillCredentials(page, phone, password);
      await ensureCheckboxes(page);
    }
    console.log(JSON.stringify({ ok: false, state: 'login_failed', attempts, ...(await summarize(page)) }, null, 2));
    process.exitCode = 1;
  } catch (error) {
    console.error(JSON.stringify({ ok: false, state: 'error', message: error.message, attempts }, null, 2));
    process.exitCode = 1;
  } finally {
    await page.waitForTimeout(1500).catch(() => {});
    await context.close().catch(() => {});
  }
}

main();
