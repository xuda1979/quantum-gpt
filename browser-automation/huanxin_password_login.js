const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { getRequestedProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');

const DEFAULT_TRAIN_DEV_URL =
  process.env.HUANXIN_TRAIN_DEV_URL ||
  'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=AI';

function usage() {
  console.error(`Usage:
  HUANXIN_LOGIN_PHONE=... HUANXIN_LOGIN_PASSWORD=... [HUANXIN_CAPTCHA_CODE=...] node browser-automation/huanxin_password_login.js [--headed] [--timeout 180] [--url URL]

Environment:
  HUANXIN_LOGIN_PHONE      Login phone number or username.
  HUANXIN_LOGIN_PASSWORD   Login password. Never pass this as a CLI argument.
  HUANXIN_CAPTCHA_CODE     Optional graphical captcha value, if Huanxin asks for one.
  HUANXIN_CAPTCHA_CODE_FILE Optional file path; when set, save captcha image and wait for this file.
`);
  process.exit(2);
}

function parseArgs(argv) {
  const args = {
    url: DEFAULT_TRAIN_DEV_URL,
    timeout: 180,
    headed: process.env.HUANXIN_HEADLESS === '0',
    screenshot: 'browser-automation/huanxin-password-login.png',
    captchaImage: 'browser-automation/huanxin-password-login-captcha.png',
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--url') {
      args.url = argv[++index];
      continue;
    }
    if (token === '--timeout') {
      args.timeout = Number(argv[++index]);
      continue;
    }
    if (token === '--headed') {
      args.headed = true;
      continue;
    }
    if (token === '--headless') {
      args.headed = false;
      continue;
    }
    if (token === '--screenshot') {
      args.screenshot = argv[++index];
      continue;
    }
    if (token === '--captcha-image') {
      args.captchaImage = argv[++index];
      continue;
    }
    usage();
  }

  if (!Number.isFinite(args.timeout) || args.timeout <= 0) {
    throw new Error('--timeout must be a positive number of seconds');
  }

  return args;
}

function cleanText(value) {
  return (value || '').replace(/\s+/g, ' ').trim();
}

async function waitForCaptchaCodeFile(filePath, timeoutMs) {
  if (!filePath) {
    return '';
  }
  const resolved = path.resolve(filePath);
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const value = fs.existsSync(resolved) ? cleanText(fs.readFileSync(resolved, 'utf8')) : '';
    if (value) {
      return value;
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  return '';
}

function classifyPage(url, bodyText) {
  const lowerUrl = (url || '').toLowerCase();
  const lowerText = (bodyText || '').toLowerCase();

  if (lowerUrl.includes('/auth/realms/') || lowerUrl.includes('openid-connect/auth')) {
    return 'login_required';
  }
  if (lowerText.includes('扫码登录') || lowerText.includes('密码登录') || lowerText.includes('获取验证码')) {
    return 'login_required';
  }
  if (lowerUrl.includes('train-dev') || lowerText.includes('训练') || lowerText.includes('开发')) {
    return 'authenticated_or_train_surface';
  }
  return 'unknown';
}

async function summarize(page, extra = {}) {
  const bodyText = cleanText(await page.locator('body').innerText().catch(() => ''));
  return {
    ok: true,
    state: classifyPage(page.url(), bodyText),
    title: await page.title().catch(() => ''),
    url: page.url(),
    bodyPreview: bodyText.slice(0, 600),
    timestamp: new Date().toISOString(),
    ...extra,
  };
}

async function waitForTerminalState(page, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  let last = await summarize(page).catch(() => ({ state: 'unknown' }));
  let iter = 0;

  while (Date.now() < deadline) {
    await page.waitForTimeout(2000);
    iter += 1;
    last = await summarize(page).catch(() => last);
    if (process.env.HUANXIN_LOGIN_DEBUG === '1' && iter % 3 === 0) {
      try {
        console.error(JSON.stringify({ debugTick: iter, url: page.url(), state: last.state, t: new Date().toISOString() }));
        await page.screenshot({ path: path.resolve('browser-automation/huanxin-login-postsubmit.png'), fullPage: true }).catch(() => {});
      } catch (_) {}
    }
    if (last.state !== 'login_required' && last.state !== 'unknown') {
      return last;
    }
    const hasError = await page
      .locator('.alert, #code-error, [class*="error"], [class*="Error"]')
      .evaluateAll((nodes) => cleanText(nodes.map((node) => node.innerText || node.textContent || '').join(' ')))
      .catch(() => '');
    if (hasError) {
      return { ...last, state: 'login_error', errorText: hasError.slice(0, 600) };
    }
  }

  return { ...last, state: 'login_timeout' };
}

async function launchContext(profileDir, headed) {
  if (!headed) {
    const launch = await launchPersistentContext(profileDir);
    return launch.context;
  }

  const executablePath = process.env.HUANXIN_BROWSER_EXECUTABLE_PATH || chromium.executablePath();
  return chromium.launchPersistentContext(profileDir, {
    headless: false,
    executablePath,
    slowMo: 50,
    viewport: { width: 1440, height: 900 },
  });
}

async function switchToPasswordLogin(page) {
  await page.getByText('密码登录', { exact: true }).click({ timeout: 10000 }).catch(async () => {
    await page.evaluate(() => {
      if (window.app && typeof window.app.toggleLogin === 'function') {
        window.app.toggleLogin(2, 'click');
      }
    });
  });
  await page.waitForTimeout(800);
}

async function fillViaVue(page, credentials) {
  return page.evaluate(({ phone, password, captcha }) => {
    if (!window.app) {
      return false;
    }
    if (typeof window.app.toggleLogin === 'function') {
      window.app.toggleLogin(2, 'click');
    }
    window.app.agreement = true;
    window.app.rememberMe = true;
    window.app.form = {
      ...window.app.form,
      username: phone,
      phoneNumber: phone,
      password,
      captchaCode: captcha || window.app.form.captchaCode || '',
      terms: true,
    };
    window.app.origin = 'password';
    window.app.isPwsLoginType = true;
    return true;
  }, credentials);
}

async function fillVisibleInputs(page, credentials) {
  const username = page.locator('#username, input[name="username"], input[placeholder*="用户名"], input[placeholder*="手机"]').first();
  if (await username.count()) {
    await username.fill(credentials.phone);
  }

  const password = page.locator('#password, input[name="password"], input[type="password"], input[placeholder*="密码"]').first();
  if (await password.count()) {
    await password.fill(credentials.password);
  }

  if (credentials.captcha) {
    const captcha = page.locator('#captchaCode, input[name="captchaCode"], input[placeholder*="图形验证码"]').first();
    if (await captcha.count()) {
      await captcha.fill(credentials.captcha);
    }
  }
}

async function fillCaptchaInputSilently(page, captcha) {
  return page.evaluate((value) => {
    if (window.app) {
      window.app.form = { ...window.app.form, captchaCode: value };
    }
    const candidates = Array.from(document.querySelectorAll('#captchaCode, input[name="captchaCode"], input[placeholder*="图形验证码"]'));
    const input = candidates.find((element) => {
      const rect = element.getBoundingClientRect();
      const style = window.getComputedStyle(element);
      return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    }) || candidates[0];
    if (!input) {
      return false;
    }
    input.value = value;
    return true;
  }, captcha);
}

async function ensureCheckboxes(page) {
  await page.evaluate(() => {
    if (window.app) {
      window.app.agreement = true;
      window.app.rememberMe = true;
      window.app.form = { ...window.app.form, terms: true };
    }
  });

  const boxes = await page.locator('input[type="checkbox"], .ant-checkbox-input').all();
  for (const box of boxes) {
    const checked = await box.isChecked().catch(() => false);
    if (!checked) {
      await box.check({ force: true }).catch(async () => {
        await box.evaluate((element) => {
          element.checked = true;
          element.dispatchEvent(new Event('change', { bubbles: true }));
          element.dispatchEvent(new Event('input', { bubbles: true }));
        });
      });
    }
  }
}

async function saveCaptchaImage(page, targetPath) {
  const resolved = path.resolve(targetPath);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  const captchaInput = page.locator('#captchaCode, input[name="captchaCode"], input[placeholder*="图形验证码"]').first();
  const inputBox = await captchaInput.boundingBox().catch(() => null);
  if (inputBox) {
    const clip = {
      x: Math.max(0, inputBox.x + inputBox.width * 0.66),
      y: Math.max(0, inputBox.y - 18),
      width: Math.min(180, inputBox.width * 0.36),
      height: Math.min(90, inputBox.height + 36),
    };
    await page.screenshot({ path: resolved, clip }).catch(() => null);
    if (fs.existsSync(resolved)) {
      return resolved;
    }
  }

  const candidates = await page.locator('img[alt*="图形验证码"], .captcha-code img, img').all();
  for (const candidate of candidates) {
    const visible = await candidate.isVisible().catch(() => false);
    if (!visible) {
      continue;
    }
    await candidate.screenshot({ path: resolved }).catch(() => null);
    if (fs.existsSync(resolved)) {
      return resolved;
    }
  }
  return null;
}

async function submitLogin(page, hasCaptcha) {
  await page.locator('#kc-login, [name="login"], text=登录').first().click({ force: true, timeout: 10000 }).catch(async () => {
    if (!hasCaptcha) {
      throw new Error('Login button was not clickable.');
    }
    const submitted = await page.evaluate(() => {
      if (window.app && typeof window.app.login === 'function') {
        window.app.login(true);
        return true;
      }
      return false;
    });
    if (!submitted) {
      throw new Error('Login button was not clickable and Vue login fallback was unavailable.');
    }
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const phone = process.env.HUANXIN_LOGIN_PHONE || '';
  const password = process.env.HUANXIN_LOGIN_PASSWORD || '';
  const captchaCodeFile = process.env.HUANXIN_CAPTCHA_CODE_FILE || '';
  let captcha = process.env.HUANXIN_CAPTCHA_CODE || '';
  if (!phone || !password) {
    usage();
  }

  const profileDir = getRequestedProfileDir();
  fs.mkdirSync(profileDir, { recursive: true });

  const context = await launchContext(profileDir, args.headed);
  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);

  try {
    await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(5000);

    const initial = await summarize(page);
    if (initial.state !== 'login_required') {
      console.log(JSON.stringify({ ...initial, alreadyAuthenticated: true }, null, 2));
      return;
    }

    await switchToPasswordLogin(page);
    await fillViaVue(page, { phone, password, captcha });
    await fillVisibleInputs(page, { phone, password, captcha });
    await ensureCheckboxes(page);

    if (args.screenshot) {
      const resolvedScreenshot = path.resolve(args.screenshot);
      fs.mkdirSync(path.dirname(resolvedScreenshot), { recursive: true });
      await page.screenshot({ path: resolvedScreenshot, fullPage: true }).catch(() => {});
    }

    const captchaInputVisible = await page.locator('#captchaCode, input[name="captchaCode"], input[placeholder*="图形验证码"]').first().isVisible().catch(() => false);
    if (captchaInputVisible && !captcha) {
      const captchaImage = await saveCaptchaImage(page, args.captchaImage);
      captcha = await waitForCaptchaCodeFile(captchaCodeFile, args.timeout * 1000);
      if (captcha) {
        await fillCaptchaInputSilently(page, captcha);
        await ensureCheckboxes(page);
        if (args.screenshot) {
          const parsed = path.parse(path.resolve(args.screenshot));
          await page.screenshot({
            path: path.join(parsed.dir, `${parsed.name}.after-captcha${parsed.ext}`),
            fullPage: true,
          }).catch(() => {});
        }
      } else if (process.env.HUANXIN_HOLD_OPEN_ON_CAPTCHA === '1') {
        console.error(JSON.stringify({
          ok: false,
          state: 'captcha_manual_hold',
          url: page.url(),
          title: await page.title().catch(() => ''),
          captchaImage,
          message: 'Browser is held open for manual CAPTCHA/password login in the Codex Huanxin profile.',
          timestamp: new Date().toISOString(),
        }, null, 2));
        const manualResult = await waitForTerminalState(page, args.timeout * 1000);
        console.log(JSON.stringify({ ...manualResult, manualCaptchaHold: true }, null, 2));
        if (manualResult.state !== 'authenticated_or_train_surface') {
          process.exitCode = 1;
        }
        return;
      } else {
      console.log(JSON.stringify({
        ok: false,
        state: 'captcha_required',
        url: page.url(),
        title: await page.title().catch(() => ''),
        captchaImage,
        captchaCodeFileConfigured: Boolean(captchaCodeFile),
        message: 'Password, account, remember-me, and agreement fields are filled, but Huanxin requires HUANXIN_CAPTCHA_CODE before the script can submit.',
        timestamp: new Date().toISOString(),
      }, null, 2));
      process.exitCode = 3;
      return;
      }
    }

    await submitLogin(page, Boolean(captcha));
    const result = await waitForTerminalState(page, args.timeout * 1000);
    console.log(JSON.stringify(result, null, 2));
    if (result.state !== 'authenticated_or_train_surface') {
      process.exitCode = 1;
    }
  } finally {
    await page.waitForTimeout(3000).catch(() => {});
    await context.close().catch(() => {});
  }
}

main().catch((error) => {
  console.error(JSON.stringify({
    ok: false,
    state: 'error',
    message: error.message,
    timestamp: new Date().toISOString(),
  }, null, 2));
  process.exit(1);
});
