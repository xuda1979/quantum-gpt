#!/usr/bin/env node
// Re-seed the headless daemon profile by capturing the OAuth callback from a
// logged-in Google Chrome session (background, no focus stealing) instead of
// Safari. Mirrors huanxin_repair_profile_via_safari_sso.js but uses Chrome JXA.
const { execFile } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { promisify } = require('util');
const { copyProfileTree, getBaseProfileDir, removeDirRobust, syncProfileTree } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const {
  TRAIN_DEV_URL,
  classifyUrl,
  collectAuthDiagnostics,
  isOnTargetAppRoute,
  redactAuthUrl,
} = require('./huanxin_repair_profile_via_safari_sso');

const execFileAsync = promisify(execFile);

function parseArgs(argv) {
  const args = { waitMs: 10000, resultPath: '/tmp/huanxin-browser-profile-repair-via-chrome.json' };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === '--wait-ms') { args.waitMs = parseInt(argv[++i], 10); continue; }
    if (token === '--result-path') { args.resultPath = argv[++i]; continue; }
    throw new Error(`Unknown argument: ${token}`);
  }
  return args;
}

function chromeCaptureScript(authUrl) {
  // The final expression value is written to stdout by osascript (JXA
  // console.log goes to stderr, so we return the JSON string instead).
  return `
function run() {
  const chrome = Application('Google Chrome');
  let win = null;
  try { win = chrome.windows()[0]; } catch (e) {}
  if (!win) { return JSON.stringify({ error: 'no_chrome_window' }); }
  const authUrl = ${JSON.stringify(authUrl)};
  win.tabs.push(chrome.Tab({ url: authUrl }));
  const tabs0 = win.tabs();
  const tab = tabs0[tabs0.length - 1];
  let callbackUrl = null, authRedirectUrl = null, sampleCount = 0;
  for (let i = 0; i < 160; i++) {
    let u = '';
    try { u = String(tab.url() || ''); } catch (e) { u = ''; }
    sampleCount++;
    if (!callbackUrl && u.indexOf('session_state=') !== -1 && u.indexOf('code=') !== -1) callbackUrl = u;
    if (!authRedirectUrl && u.indexOf('/auth/realms/') !== -1 && u.indexOf('openid-connect/auth') !== -1) authRedirectUrl = u;
    if (callbackUrl) break;
    delay(0.05);
  }
  let finalUrl = '';
  try { finalUrl = String(tab.url() || ''); } catch (e) {}
  try { tab.close(); } catch (e) {}
  return JSON.stringify({ callback_url: callbackUrl, auth_redirect_url: authRedirectUrl, final_url: finalUrl, sample_count: sampleCount });
}
run();
`;
}

async function captureChromeCallback(authUrl) {
  try {
    const { stdout, stderr } = await execFileAsync('osascript', ['-l', 'JavaScript'], {
      input: chromeCaptureScript(authUrl),
      encoding: 'utf8',
      maxBuffer: 10 * 1024 * 1024,
      timeout: 120000,
      killSignal: 'SIGKILL',
    });
    const text = String(stdout || '').trim() || String(stderr || '').trim();
    return JSON.parse(text);
  } catch (error) {
    const out = String(error.stdout || '').trim();
    if (out) {
      try { return JSON.parse(out); } catch (_) {}
    }
    throw new Error(
      `chrome_capture_failed: ${error.killed ? 'timeout/killed' : `exit=${error.code}`} stderr=${String(error.stderr || '').slice(0, 300)}`
    );
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const baseProfileDir = getBaseProfileDir();
  fs.mkdirSync(baseProfileDir, { recursive: true });
  const workingProfileDir = path.join(os.tmpdir(), `huanxin-profile-repair-chrome-${process.pid}-${Date.now()}`);
  copyProfileTree(baseProfileDir, workingProfileDir);

  const launch = await launchPersistentContext(workingProfileDir);
  const context = launch.context;
  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);

  let result = null;
  try {
    await page.goto(TRAIN_DEV_URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);
    const authUrl = page.url();

    if (classifyUrl(authUrl) !== 'login_required') {
      const diagnostics = await collectAuthDiagnostics(page);
      result = { ok: true, mode: 'already_authenticated', finalUrl: authUrl, finalUrlState: classifyUrl(authUrl), ...diagnostics };
    } else {
      const capture = await captureChromeCallback(authUrl);
      if (!capture.callback_url) {
        const diagnostics = await collectAuthDiagnostics(page);
        result = { ok: false, mode: 'missing_callback', authUrl: redactAuthUrl(authUrl), chromeCapture: { ...capture, callback_url: capture.callback_url ? '[REDACTED]' : null }, finalUrl: page.url(), finalUrlState: classifyUrl(page.url()), ...diagnostics };
      } else {
        await page.goto(capture.callback_url, { waitUntil: 'domcontentloaded', timeout: 180000 });
        await page.waitForTimeout(args.waitMs);
        if (classifyUrl(page.url()) !== 'app_surface') {
          await page.goto(TRAIN_DEV_URL, { waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
          await page.waitForTimeout(Math.max(4000, Math.floor(args.waitMs / 2)));
        }
        const diagnostics = await collectAuthDiagnostics(page);
        result = { ok: isOnTargetAppRoute(page.url(), TRAIN_DEV_URL), mode: 'chrome_sso_bridge', finalUrl: page.url(), finalUrlState: classifyUrl(page.url()), ...diagnostics };
      }
    }
    result.baseProfileDir = baseProfileDir;
    result.workingProfileDir = workingProfileDir;
    result.browserMode = launch.browserMode;
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

  fs.writeFileSync(args.resultPath, JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
  if (!result || !result.ok) process.exitCode = 2;
}

if (require.main === module) {
  main().catch((error) => { console.error(error.stack || error.message || String(error)); process.exit(1); });
}
