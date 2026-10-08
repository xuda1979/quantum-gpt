#!/usr/bin/env node
/**
 * Rehydrate the base Chromium Huanxin profile using the latest callback URL
 * captured from the Safari keepalive log.
 *
 * This does not open a visible login flow by itself. It replays a previously
 * captured authenticated callback into the persistent Chromium profile and then
 * verifies whether the app surface becomes available again.
 */

const fs = require('fs');
const path = require('path');
const { getBaseProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');

const DEFAULT_TRAIN_DEV_URL =
  process.env.HUANXIN_TRAIN_DEV_URL ||
  'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=AI';
const DEFAULT_KEEPALIVE_LOG = '/tmp/huanxin-safari-keepalive.launchd.log';
const DEFAULT_RESULT_PATH = '/tmp/huanxin-browser-profile-repair.json';

function parseArgs(argv) {
  const args = {
    callbackUrl: null,
    keepaliveLog: DEFAULT_KEEPALIVE_LOG,
    trainDevUrl: DEFAULT_TRAIN_DEV_URL,
    waitMs: 12000,
    resultPath: DEFAULT_RESULT_PATH,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === '--callback-url') {
      args.callbackUrl = argv[++i];
      continue;
    }
    if (token === '--keepalive-log') {
      args.keepaliveLog = argv[++i];
      continue;
    }
    if (token === '--train-dev-url') {
      args.trainDevUrl = argv[++i];
      continue;
    }
    if (token === '--wait-ms') {
      args.waitMs = parseInt(argv[++i], 10);
      continue;
    }
    if (token === '--result-path') {
      args.resultPath = argv[++i];
      continue;
    }
    throw new Error(`Unknown argument: ${token}`);
  }

  return args;
}

function extractCallbackUrlFromLog(logPath) {
  const content = fs.readFileSync(logPath, 'utf8');
  const lines = content.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const callbackRows = [];
  for (const line of lines) {
    if (!line.startsWith('{')) continue;
    try {
      const row = JSON.parse(line);
      const directUrl = String(row.url || '');
      if (directUrl.includes('session_state=') && directUrl.includes('code=')) {
        callbackRows.push(directUrl);
        continue;
      }
      const detail = String(row.detail || '');
      if (detail.includes('session_state=') && detail.includes('code=')) {
        callbackRows.push(detail);
      }
    } catch {
      // ignore malformed lines
    }
  }
  return callbackRows.length > 0 ? callbackRows[callbackRows.length - 1] : null;
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

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const callbackUrl =
    args.callbackUrl || (fs.existsSync(args.keepaliveLog) ? extractCallbackUrlFromLog(args.keepaliveLog) : null);

  if (!callbackUrl) {
    throw new Error(`No callback URL with code/session_state found in ${args.keepaliveLog}`);
  }

  const profileDir = getBaseProfileDir();
  fs.mkdirSync(profileDir, { recursive: true });

  const launch = await launchPersistentContext(profileDir);
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

  try {
    await page.goto(callbackUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(args.waitMs);
    pushTrace('after_callback');

    if (classifyUrl(page.url()) !== 'app_surface') {
      await page.goto(args.trainDevUrl, { waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
      await page.waitForTimeout(Math.max(4000, Math.floor(args.waitMs / 2)));
      pushTrace('after_train_dev');
    }

    const bodyText = ((await page.locator('body').innerText().catch(() => '')) || '').replace(/\s+/g, ' ').trim();
    const result = {
      ok: classifyUrl(page.url()) === 'app_surface',
      callbackUrl,
      finalUrl: page.url(),
      finalUrlState: classifyUrl(page.url()),
      bodyPreview: bodyText.slice(0, 400),
      profileDir,
      browserMode: launch.browserMode,
      launchFallbackUsed: launch.fallbackUsed,
      trace,
    };

    if (args.resultPath) {
      fs.mkdirSync(path.dirname(path.resolve(args.resultPath)), { recursive: true });
      fs.writeFileSync(path.resolve(args.resultPath), JSON.stringify(result, null, 2));
    }

    console.log(JSON.stringify(result, null, 2));

    if (!result.ok) {
      process.exitCode = 2;
    }
  } finally {
    await context.close().catch(() => {});
  }
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
