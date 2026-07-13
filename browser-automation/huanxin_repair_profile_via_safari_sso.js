#!/usr/bin/env node
const { execFile } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { promisify } = require('util');
const { copyProfileTree, getBaseProfileDir, removeDirRobust, syncProfileTree } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');

const TRAIN_DEV_URL =
  process.env.HUANXIN_TRAIN_DEV_URL ||
  'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=AI';
const CAPTURE_SCRIPT = path.resolve(__dirname, '../scripts/huanxin_safari_capture_callback.sh');
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
  if (lower.includes('session_state=') && lower.includes('code=')) {
    return 'callback';
  }
  if (lower.includes('/kl-web') || lower.includes('/train-dev')) {
    return 'app_surface';
  }
  return 'unknown';
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
  const targetName = String(getHashSearchParam(targetUrl, 'name') || '').trim();
  if (!targetName) {
    return true;
  }
  return String(getHashSearchParam(currentUrl, 'name') || '').trim() === targetName;
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



function stripShellQuotes(value) {
  const text = String(value || '').trim();
  if ((text.startsWith("'") && text.endsWith("'")) || (text.startsWith('"') && text.endsWith('"'))) {
    return text.slice(1, -1);
  }
  return text;
}

function loadEnvFileIfPresent(filePath) {
  if (!fs.existsSync(filePath)) {
    return;
  }
  const text = fs.readFileSync(filePath, 'utf8');
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) {
      continue;
    }
    const match = line.match(/^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!match) {
      continue;
    }
    const [, key, rawValue] = match;
    if (process.env[key]) {
      continue;
    }
    process.env[key] = stripShellQuotes(rawValue);
  }
}

function loadHuanxinLoginEnv() {
  for (const filePath of [
    path.resolve(__dirname, '..', '.huanxin_login.env'),
    path.resolve(__dirname, '..', '.huanxin.env'),
    path.join(os.homedir(), '.codex', 'secrets', 'huanxin.env'),
  ]) {
    loadEnvFileIfPresent(filePath);
  }
}

function redactAuthUrl(value) {
  if (!value) {
    return value;
  }
  const text = String(value);
  if (!text) {
    return text;
  }
  try {
    const parsed = new URL(text);
    const lowerPath = parsed.pathname.toLowerCase();
    const sensitiveKeys = new Set(['code', 'session_state', 'state', 'nonce', 'token', 'access_token', 'id_token']);
    for (const key of Array.from(parsed.searchParams.keys())) {
      if (sensitiveKeys.has(key.toLowerCase())) {
        parsed.searchParams.set(key, '[REDACTED]');
      }
    }
    if (parsed.hash) {
      const [route, rawQuery = ''] = parsed.hash.slice(1).split('?');
      const params = new URLSearchParams(rawQuery);
      for (const key of Array.from(params.keys())) {
        if (sensitiveKeys.has(key.toLowerCase())) {
          params.set(key, '[REDACTED]');
        }
      }
      const nextQuery = params.toString();
      parsed.hash = nextQuery ? `${route}?${nextQuery}` : route;
    }
    if (lowerPath.includes('/auth/realms/') && lowerPath.includes('openid-connect/auth')) {
      return `${parsed.origin}${parsed.pathname}?[REDACTED_AUTH_QUERY]`;
    }
    return parsed.toString();
  } catch {
    return text
      .replace(/([?&#](?:code|session_state|state|nonce|token|access_token|id_token)=)[^&#]+/gi, '$1[REDACTED]')
      .replace(/(openid-connect\/auth\?)[^#\s]+/gi, '$1[REDACTED_AUTH_QUERY]');
  }
}

function sanitizeSafariCapture(capture) {
  if (!capture || typeof capture !== 'object') {
    return capture;
  }
  const sanitized = { ...capture };
  for (const key of ['callback_url', 'auth_redirect_url', 'visit_url', 'final_url']) {
    if (sanitized[key]) {
      sanitized[key] = redactAuthUrl(sanitized[key]);
    }
  }
  if (Array.isArray(sanitized.redirect_samples)) {
    sanitized.redirect_samples = sanitized.redirect_samples.slice(-8).map((sample) => ({
      ...sample,
      url: sample && sample.url ? redactAuthUrl(sample.url) : sample && sample.url,
    }));
    sanitized.redirect_samples_truncated = capture.redirect_samples.length > sanitized.redirect_samples.length;
    sanitized.redirect_sample_count = capture.redirect_samples.length;
  }
  return sanitized;
}

function sanitizeBridgeResult(result) {
  if (!result || typeof result !== 'object') {
    return result;
  }
  const sanitized = { ...result };
  for (const key of ['authUrl', 'finalUrl', 'legacyCallbackUrl']) {
    if (sanitized[key]) {
      sanitized[key] = redactAuthUrl(sanitized[key]);
    }
  }
  if (sanitized.safariCapture) {
    sanitized.safariCapture = sanitizeSafariCapture(sanitized.safariCapture);
  }
  if (Array.isArray(sanitized.trace)) {
    sanitized.trace = sanitized.trace.map((entry) => ({
      ...entry,
      url: entry && entry.url ? redactAuthUrl(entry.url) : entry && entry.url,
    }));
  }
  if (sanitized.passwordLoginResult && sanitized.passwordLoginResult.url) {
    sanitized.passwordLoginResult = {
      ...sanitized.passwordLoginResult,
      url: redactAuthUrl(sanitized.passwordLoginResult.url),
    };
  }
  return sanitized;
}

async function runPasswordLoginFallback(targetUrl) {
  loadHuanxinLoginEnv();
  if (process.env.HUANXIN_DISABLE_PASSWORD_LOGIN_FALLBACK === '1') {
    return { attempted: false, reason: 'disabled' };
  }
  if (!process.env.HUANXIN_LOGIN_PHONE || !process.env.HUANXIN_LOGIN_PASSWORD) {
    return { attempted: false, reason: 'missing_credentials' };
  }
  const scriptPath = path.resolve(__dirname, 'huanxin_password_login.js');
  try {
    const { stdout, stderr } = await execFileAsync(
      'node',
      [scriptPath, '--timeout', String(process.env.HUANXIN_PASSWORD_LOGIN_TIMEOUT_SECONDS || 180), '--url', targetUrl],
      {
        encoding: 'utf8',
        maxBuffer: 2 * 1024 * 1024,
        env: { ...process.env, HUANXIN_TRAIN_DEV_URL: targetUrl },
      }
    );
    let parsed = null;
    try {
      parsed = JSON.parse(String(stdout || '').trim());
    } catch {}
    return {
      attempted: true,
      ok: Boolean(parsed && parsed.state === 'authenticated_or_train_surface'),
      state: parsed && parsed.state,
      title: parsed && parsed.title,
      url: parsed && parsed.url ? redactAuthUrl(parsed.url) : undefined,
      stderrPreview: String(stderr || '').slice(0, 1000),
    };
  } catch (error) {
    let parsed = null;
    try {
      parsed = JSON.parse(String(error.stdout || '').trim());
    } catch {}
    return {
      attempted: true,
      ok: false,
      state: parsed && parsed.state ? parsed.state : 'password_login_failed',
      title: parsed && parsed.title,
      url: parsed && parsed.url ? redactAuthUrl(parsed.url) : undefined,
      captchaImage: parsed && parsed.captchaImage,
      message: parsed && parsed.message,
      stderrPreview: String(error.stderr || error.message || '').slice(0, 1000),
    };
  }
}

async function captureSafariCallback(authUrl) {
  if (process.env.HUANXIN_ALLOW_SAFARI_SSO_BRIDGE !== '1') {
    throw new Error(
      'Safari SSO bridge is disabled by default because it can foreground the user browser. ' +
        'Set HUANXIN_ALLOW_SAFARI_SSO_BRIDGE=1 only after explicit user approval.'
    );
  }
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
  const targetUrl = options.targetUrl || TRAIN_DEV_URL;
  const resultPath = options.resultPath || null;
  const trace = options.trace || [];
  const maxBridgeAttemptsRaw = parseInt(
    String(options.maxBridgeAttempts ?? process.env.HUANXIN_SAFARI_SSO_BRIDGE_MAX_ATTEMPTS ?? 2),
    10
  );
  const maxBridgeAttempts = Number.isFinite(maxBridgeAttemptsRaw) && maxBridgeAttemptsRaw > 0
    ? maxBridgeAttemptsRaw
    : 2;
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
  let result = null;

  for (let attempt = 1; attempt <= maxBridgeAttempts; attempt += 1) {
    const authUrl = options.authUrl || page.url();
    let capture = null;
    try {
      capture = await captureSafariCallback(authUrl);
    } catch (error) {
      if (isOnTargetAppRoute(page.url(), targetUrl)) {
        const diagnostics = await collectAuthDiagnostics(page);
        result = {
          ok: true,
          mode: 'already_authenticated_after_capture_failure',
          authUrl,
          bridgeAttempt: attempt,
          maxBridgeAttempts,
          safariCaptureError: error.message || String(error),
          finalUrl: page.url(),
          finalUrlState: classifyUrl(page.url()),
          trace,
          ...diagnostics,
        };
        break;
      }
      throw error;
    }

    if (!capture.callback_url) {
      await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
      await page.waitForTimeout(Math.max(3000, Math.floor(waitMs / 2)));
      pushTrace(`after_missing_callback_train_dev_attempt_${attempt}`);
      if (isOnTargetAppRoute(page.url(), targetUrl)) {
        const diagnostics = await collectAuthDiagnostics(page);
        result = {
          ok: true,
          mode: 'already_authenticated_missing_callback',
          authUrl,
          bridgeAttempt: attempt,
          maxBridgeAttempts,
          safariCapture: capture,
          finalUrl: page.url(),
          finalUrlState: classifyUrl(page.url()),
          trace,
          ...diagnostics,
        };
        break;
      }
      const passwordLoginResult = await runPasswordLoginFallback(targetUrl);
      if (passwordLoginResult.attempted && passwordLoginResult.ok) {
        await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
        await page.waitForTimeout(Math.max(3000, Math.floor(waitMs / 2)));
        pushTrace(`after_password_login_fallback_attempt_${attempt}`);
        if (isOnTargetAppRoute(page.url(), targetUrl)) {
          const diagnostics = await collectAuthDiagnostics(page);
          result = {
            ok: true,
            mode: 'password_login_fallback',
            authUrl,
            bridgeAttempt: attempt,
            maxBridgeAttempts,
            safariCapture: capture,
            passwordLoginResult,
            finalUrl: page.url(),
            finalUrlState: classifyUrl(page.url()),
            trace,
            ...diagnostics,
          };
          break;
        }
      }
      const diagnostics = await collectAuthDiagnostics(page);
      result = {
        ok: false,
        mode: 'missing_callback',
        authUrl,
        bridgeAttempt: attempt,
        maxBridgeAttempts,
        safariCapture: capture,
        passwordLoginResult,
        finalUrl: page.url(),
        finalUrlState: classifyUrl(page.url()),
        trace,
        ...diagnostics,
      };
      break;
    }

    await page.goto(capture.callback_url, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(waitMs);
    pushTrace(`after_callback_attempt_${attempt}`);

    if (classifyUrl(page.url()) !== 'app_surface') {
      await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
      await page.waitForTimeout(Math.max(4000, Math.floor(waitMs / 2)));
      pushTrace(`after_retry_train_dev_attempt_${attempt}`);
    }

    const diagnostics = await collectAuthDiagnostics(page);
    result = {
      ok: isOnTargetAppRoute(page.url(), targetUrl),
      mode: 'safari_sso_bridge',
      authUrl,
      bridgeAttempt: attempt,
      maxBridgeAttempts,
      safariCapture: capture,
      finalUrl: page.url(),
      finalUrlState: classifyUrl(page.url()),
      trace,
      ...diagnostics,
    };
    if (result.ok || attempt === maxBridgeAttempts) {
      break;
    }
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
    await page.waitForTimeout(Math.max(3000, Math.floor(waitMs / 2)));
    pushTrace(`before_bridge_retry_attempt_${attempt + 1}`);
  }

  const sanitizedResult = sanitizeBridgeResult(result);
  if (resultPath && sanitizedResult) {
    fs.writeFileSync(resultPath, JSON.stringify(sanitizedResult, null, 2));
  }
  return sanitizedResult;
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
        targetUrl: TRAIN_DEV_URL,
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
    const outputResult = sanitizeBridgeResult(result);
    fs.writeFileSync(args.resultPath, JSON.stringify(outputResult, null, 2));
    console.log(JSON.stringify(outputResult, null, 2));
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
  redactAuthUrl,
  sanitizeBridgeResult,
  sanitizeSafariCapture,
  runPasswordLoginFallback,
  loadHuanxinLoginEnv,
  getHashSearchParam,
  getRoutePath,
  isOnTargetAppRoute,
};

if (require.main === module) {
  main().catch((error) => {
    console.error(error.stack || error.message || String(error));
    process.exit(1);
  });
}
