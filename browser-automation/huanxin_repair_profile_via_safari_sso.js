#!/usr/bin/env node
const { execFile } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { promisify } = require('util');
const { copyProfileTree, getBaseProfileDir, removeDirRobust, syncProfileTree } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');

const TRAIN_DEV_URL =
  'https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev';
const CAPTURE_SCRIPT =
  process.env.HUANXIN_CAPTURE_SCRIPT ||
  path.resolve(__dirname, '../scripts/huanxin_safari_capture_callback.sh');
const execFileAsync = promisify(execFile);

function parseArgs(argv) {
  const args = {
    waitMs: 10000,
    resultPath: '/tmp/huanxin-browser-profile-repair-via-safari.json',
    legacyCallbackUrl: null,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === '--wait-ms') {
      args.waitMs = parseInt(argv[++i], 10);
      continue;
    }
    if (token === '--result-path') {
      args.resultPath = argv[++i];
      continue;
    }
    if (token === '--callback-url') {
      args.legacyCallbackUrl = argv[++i];
      continue;
    }
    throw new Error(`Unknown argument: ${token}`);
  }
  return args;
}

function classifyUrl(url) {
  const lower = String(url || '').toLowerCase();
  if (lower.includes('/auth/realms/') && lower.includes('openid-connect/auth')) {
    return 'login_required';
  }
  // Check app_surface BEFORE callback — a URL can have auth params AND be on the app
  if (lower.includes('/kl-web') || lower.includes('/train-dev')) {
    return 'app_surface';
  }
  if (lower.includes('session_state=') && lower.includes('code=')) {
    return 'callback';
  }
  return 'unknown';
}

async function collectAuthDiagnostics(page) {
  const bodyText = ((await page.locator('body').innerText().catch(() => '')) || '').replace(/\s+/g, ' ').trim();
  const localStorageKeys = await page.evaluate(() => Object.keys(window.localStorage || {})).catch(() => []);
  const sessionStorageKeys = await page
    .evaluate(() => Object.keys(window.sessionStorage || {}))
    .catch(() => []);
  const cookies = await page.context().cookies().catch(() => []);

  return {
    bodyPreview: bodyText.slice(0, 400),
    localStorageKeys: localStorageKeys.slice(0, 50),
    sessionStorageKeys: sessionStorageKeys.slice(0, 50),
    cookieNames: cookies
      .filter((cookie) => String(cookie.domain || '').includes('aihuanxin.cn'))
      .map((cookie) => cookie.name)
      .sort(),
  };
}

async function captureSafariCallback(authUrl) {
  let lastError = null;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const { stdout } = await execFileAsync('bash', [CAPTURE_SCRIPT, '--url', authUrl], {
        encoding: 'utf8',
        maxBuffer: 10 * 1024 * 1024,
      });
      return JSON.parse(stdout);
    } catch (error) {
      lastError = error;
      if (attempt < 3) {
        await new Promise((resolve) => setTimeout(resolve, 1500));
        continue;
      }
    }
  }

  const stderr = String(lastError?.stderr || '').trim();
  const stdout = String(lastError?.stdout || '').trim();
  const detail = [stderr, stdout].filter(Boolean).join(' | ');
  if (detail) {
    throw new Error(`Safari callback capture failed after retries: ${detail}`);
  }
  throw lastError || new Error('Safari callback capture failed after retries.');
}

async function bridgePageViaSafariSso(page, options = {}) {
  const waitMs = options.waitMs ?? 10000;
  const resultPath = options.resultPath || null;
  const authUrl = options.authUrl || page.url();
  const trace = options.trace || [];
  const pushTrace =
    options.pushTrace ||
    ((label) => {
      trace.push({
        label,
        url: page.url(),
        classified: classifyUrl(page.url()),
        timestamp: new Date().toISOString(),
      });
    });
  const capture = await captureSafariCallback(authUrl);

  if (capture.callback_url && process.env.HUANXIN_FORGE_KC_CALLBACK === '1') {
    // The captured callback's state may belong to the SSO vehicle's own rerolled
    // flow rather than this browser's kc-callback entry. The SPA validates state
    // against localStorage but (observed 2026-08-20) does NOT validate the id_token
    // nonce, so forging the entry for the captured state makes the exchange succeed.
    const stateMatch = String(capture.callback_url).match(/[?&]state=([a-f0-9-]+)/);
    if (stateMatch) {
      const forgedState = stateMatch[1];
      try {
        await page.evaluate(
          ({ st }) => {
            const existing = Object.entries(localStorage).filter(([k]) =>
              k.startsWith('kc-callback')
            );
            let redirectUri = existing.length
              ? JSON.parse(existing[0][1]).redirectUri
              : encodeURIComponent(location.href.split('#')[0]);
            if (!redirectUri) {
              redirectUri = encodeURIComponent('https://aihuanxin.cn/kunlun/kl-web');
            }
            const nonce =
              typeof crypto !== 'undefined' && crypto.randomUUID
                ? crypto.randomUUID()
                : '00000000-0000-4000-8000-000000000000';
            localStorage.setItem(
              `kc-callback-${st}`,
              JSON.stringify({
                state: st,
                nonce,
                redirectUri,
                expires: Date.now() + 30 * 60 * 1000,
              })
            );
          },
          { st: forgedState }
        );
      } catch (forgeErr) {
        // Non-fatal: fall through to the normal replay path.
      }
    }
  }

  if (!capture.callback_url) {
    const diagnostics = await collectAuthDiagnostics(page);
    const result = {
      ok: false,
      mode: 'missing_callback',
      authUrl,
      safariCapture: capture,
      finalUrl: page.url(),
      finalUrlState: classifyUrl(page.url()),
      trace,
      ...diagnostics,
    };
    if (resultPath) {
      fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));
    }
    return result;
  }

  await page.goto(capture.callback_url, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(waitMs);
  pushTrace('after_callback');

  if (classifyUrl(page.url()) !== 'app_surface') {
    await page.goto(TRAIN_DEV_URL, { waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
    await page.waitForTimeout(Math.max(4000, Math.floor(waitMs / 2)));
    pushTrace('after_retry_train_dev');
  }

  const diagnostics = await collectAuthDiagnostics(page);
  const result = {
    ok: classifyUrl(page.url()) === 'app_surface',
    mode: 'safari_sso_bridge',
    authUrl,
    safariCapture: capture,
    finalUrl: page.url(),
    finalUrlState: classifyUrl(page.url()),
    trace,
    ...diagnostics,
  };
  if (resultPath) {
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));
  }
  return result;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const baseProfileDir = getBaseProfileDir();
  fs.mkdirSync(baseProfileDir, { recursive: true });
  const workingProfileDir = path.join(os.tmpdir(), `huanxin-profile-repair-${process.pid}-${Date.now()}`);
  copyProfileTree(baseProfileDir, workingProfileDir);

  const launch = await launchPersistentContext(workingProfileDir);
  const context = launch.context;
  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);

  const trace = [];
  const pushTrace = (label) => {
    trace.push({
      label,
      url: page.url(),
      classified: classifyUrl(page.url()),
      timestamp: new Date().toISOString(),
    });
  };

  let result = null;
  try {
    await page.goto(TRAIN_DEV_URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);
    pushTrace('after_train_dev');

    const authUrl = page.url();
    if (classifyUrl(authUrl) !== 'login_required') {
      const diagnostics = await collectAuthDiagnostics(page);
      result = {
        ok: true,
        mode: 'already_authenticated',
        finalUrl: authUrl,
        finalUrlState: classifyUrl(authUrl),
        baseProfileDir,
        workingProfileDir,
        browserMode: launch.browserMode,
        launchFallbackUsed: launch.fallbackUsed,
        trace,
        ...diagnostics,
      };
    } else {
      result = await bridgePageViaSafariSso(page, {
        authUrl,
        waitMs: args.waitMs,
        resultPath: args.resultPath,
        trace,
        pushTrace,
      });
      if (args.legacyCallbackUrl) {
        result.legacyCallbackUrl = args.legacyCallbackUrl;
      }
    }
    result.baseProfileDir = baseProfileDir;
    result.workingProfileDir = workingProfileDir;
    result.browserMode = launch.browserMode;
    result.launchFallbackUsed = launch.fallbackUsed;
  } finally {
    await context.close().catch(() => {});
    if (result && result.ok) {
      const syncInfo = syncProfileTree(workingProfileDir, baseProfileDir);
      result.profileSyncedToBase = true;
      result.baseProfileBackupDir = syncInfo.backupDir;
    } else if (result) {
      result.profileSyncedToBase = false;
      result.profileSyncSkippedReason = 'repair_failed_on_isolated_copy';
    }
    removeDirRobust(workingProfileDir);
  }

  if (result) {
    fs.writeFileSync(args.resultPath, JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result, null, 2));
    if (!result.ok) {
      process.exitCode = 2;
    }
  }
}

module.exports = {
  TRAIN_DEV_URL,
  bridgePageViaSafariSso,
  captureSafariCallback,
  classifyUrl,
  collectAuthDiagnostics,
};

if (require.main === module) {
  main().catch((error) => {
    console.error(error.stack || error.message || String(error));
    process.exit(1);
  });
}
