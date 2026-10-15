const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { assertAutomationAllowed } = require('./huanxin_manual_lock');

function wantsHeadless() {
  // Hard rule (user): never open a visible browser/tabs. Headless only, no env escape hatch.
  return true;
}

function allowHeadedFallback() {
  // Hard rule (user): headed fallback is banned; the env override was removed 2026-08-04.
  return false;
}

function resolveExecutablePath() {
  if (process.env.HUANXIN_BROWSER_EXECUTABLE_PATH) {
    return path.resolve(process.env.HUANXIN_BROWSER_EXECUTABLE_PATH);
  }
  if (process.platform === 'darwin') {
    const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
    if (fs.existsSync(chromePath)) {
      return chromePath;
    }
  }
  return chromium.executablePath();
}

function buildIsolatedBrowserEnv(profileDir) {
  const launchHomeDir = process.env.HUANXIN_LAUNCH_HOME_DIR
    ? path.resolve(process.env.HUANXIN_LAUNCH_HOME_DIR)
    : path.join(profileDir, '.chromium-home');
  const applicationSupportDir = path.join(
    launchHomeDir,
    'Library',
    'Application Support',
    'Google',
    'Chrome for Testing'
  );
  const cacheDir = path.join(launchHomeDir, 'Library', 'Caches');
  const configDir = path.join(launchHomeDir, '.config');
  const xdgCacheDir = path.join(launchHomeDir, '.cache');

  for (const dir of [applicationSupportDir, cacheDir, configDir, xdgCacheDir]) {
    fs.mkdirSync(dir, { recursive: true });
  }

  return {
    ...process.env,
    HOME: launchHomeDir,
    XDG_CONFIG_HOME: configDir,
    XDG_CACHE_HOME: xdgCacheDir,
  };
}

function buildCommonLaunchOptions(headless, profileDir) {
  const launchHomeDir = process.env.HUANXIN_LAUNCH_HOME_DIR
    ? path.resolve(process.env.HUANXIN_LAUNCH_HOME_DIR)
    : path.join(profileDir, '.chromium-home');
  const crashpadDir = path.join(launchHomeDir, 'crashpad');
  fs.mkdirSync(crashpadDir, { recursive: true });

  const viewportWidth = Number.parseInt(process.env.HUANXIN_VIEWPORT_WIDTH || '1600', 10);
  const viewportHeight = Number.parseInt(process.env.HUANXIN_VIEWPORT_HEIGHT || '1000', 10);
  return {
    headless,
    executablePath: resolveExecutablePath(),
    viewport: {
      width: Number.isFinite(viewportWidth) && viewportWidth > 0 ? viewportWidth : 1600,
      height: Number.isFinite(viewportHeight) && viewportHeight > 0 ? viewportHeight : 1000,
    },
    slowMo: 50,
    ignoreHTTPSErrors: true,
    env: buildIsolatedBrowserEnv(profileDir),
    args: [
      // Each env's daemon is launched with HUANXIN_CDP_PORT (keeper sets
      // ASI1=9224 ASI2=9225 ASI3=9226) for per-env Chrome isolation. This was
      // previously HARDCODED to 9224, so ASI2/ASI3 Chrome also tried to bind
      // ASI1's port -> port-in-use / 'browser has been closed' crash and envs
      // could not stay up simultaneously. Use the env's port (fallback 9224).
      `--remote-debugging-port=${process.env.HUANXIN_CDP_PORT || '9224'}`,
      '--remote-allow-origins=*',
      '--proxy-server=direct://',
      '--proxy-bypass-list=*',
      `--crash-dumps-dir=${crashpadDir}`,
      '--disable-crash-reporter',
      '--disable-crashpad-for-testing',
      '--disable-web-security',
      '--allow-running-insecure-content',
      '--ignore-certificate-errors-spki-list=*',
      '--disable-features=HttpsOnlyMode,SitePerProcess',
      '--reduce-security-for-testing',
      '--unsafely-treat-insecure-origin-as-secure=aihuanxin.cn',
    ],
  };
}

function shouldRetryHeaded(error, attemptedHeadless) {
  if (!attemptedHeadless) return false;
  if (process.platform !== 'darwin') return false;
  if (!allowHeadedFallback()) return false;

  const message = String(error && (error.stack || error.message || error));
  return isHeadlessChromiumLaunchCrash(message);
}

// C-10450: detect the wedged-browser CDP error that makes context.newPage()
// throw 'Protocol error (Target.createTarget): Failed to open a new tab'. This
// is a RUNTIME browser wedge (headless Chrome alive but its target manager is
// not answering), distinct from a launch-time crash. The daemon uses this to
// relaunch ONLY the browser in-process instead of forcing a full daemon
// restart by the keeper (measured 380 occurrences + 6 keeper relaunches in the
// 04:45-05:13Z window on ASI2/ASI3). Fail-closed: any error that is not the
// exact CDP new-tab marker returns false.
function isBrowserWedgedProtocolError(error) {
  const message = String((error && (error.stack || error.message)) || '');
  return message.includes('Protocol error (Target.createTarget)');
}

// C-10450: close the wedged persistent browser context and relaunch the
// browser on the same profile dir. Returns the fresh launch record (context,
// browserMode, fallbackUsed) so the daemon can keep serving WITHOUT a full
// daemon restart. Fail-open on close (a wedged browser may not close cleanly).
async function relaunchBrowserOnWedge(profileDir, previousContext) {
  if (previousContext) {
    try {
      await previousContext.close();
    } catch {}
  }
  const relaunched = await launchPersistentContext(profileDir);
  return {
    context: relaunched.context,
    browserMode: relaunched.browserMode,
    launchFallbackUsed: relaunched.fallbackUsed,
  };
}

// C-10450: bounded in-process browser relaunch+retry loop. When the CDP
// target manager wedges, context.newPage() throws the Target.createTarget
// Protocol error. Instead of letting the keeper kill+restart the WHOLE daemon
// (1-3min outage), try to recover in-process: relaunch the browser on the same
// profile and retry page acquisition. maxAttempts bounds the loop; any
// non-wedge error or exhaustion propagates fail-closed.
async function newPageWithBrowserReload(opts) {
  const { getContext, setContext, launchFn, log, maxAttempts = 3 } = opts;
  let current = getContext();
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const pages = current.pages ? current.pages() : [];
      const candidate = pages.find((p) => !p.isClosed()) || (await current.newPage());
      candidate.setDefaultTimeout(30000);
      return { page: candidate, relaunched: attempt > 1 };
    } catch (error) {
      if (attempt >= maxAttempts || !isBrowserWedgedProtocolError(error)) throw error;
      log('[daemon] Browser wedged (' + error.message + '), relaunching browser in-process...');
      current = setContext(await launchFn());
    }
  }
  throw new Error('newPageWithBrowserReload: exhausted attempts');
}

function isHeadlessChromiumLaunchCrash(message) {
  return (
    message.includes('MachPortRendezvousServer') ||
    message.includes('bootstrap_check_in') ||
    message.includes('signal=SIGABRT') ||
    message.includes('signal=SIGTRAP') ||
    message.includes('Target page, context or browser has been closed')
  );
}

function launchFailureAdvice(error) {
  const message = String(error && (error.stack || error.message || error));
  if (process.platform === 'darwin' && isHeadlessChromiumLaunchCrash(message) && !allowHeadedFallback()) {
    return (
      'Headless Chrome for Testing crashed on macOS. ' +
      'Browser automation stayed non-interrupting, so headed fallback was not attempted. ' +
      'Set HUANXIN_BROWSER_EXECUTABLE_PATH to a working Chromium/Chrome binary.'
    );
  }
  return '';
}

async function launchPersistentContext(profileDir) {
  assertAutomationAllowed('launchPersistentContext');
  const attemptedHeadless = wantsHeadless();
  try {
    const context = await chromium.launchPersistentContext(
      profileDir,
      buildCommonLaunchOptions(attemptedHeadless, profileDir)
    );
    return { context, browserMode: attemptedHeadless ? 'headless' : 'headed', fallbackUsed: false };
  } catch (error) {
    if (!shouldRetryHeaded(error, attemptedHeadless)) {
      const advice = launchFailureAdvice(error);
      if (advice) {
        error.message = `${error.message}\n[huanxin_launch_advice] ${advice}`;
      }
      throw error;
    }

    console.error(
      '[huanxin_launch] Headless Chromium launch failed on Darwin; retrying with headed browser fallback.'
    );
    const context = await chromium.launchPersistentContext(profileDir, buildCommonLaunchOptions(false, profileDir));
    return { context, browserMode: 'headed', fallbackUsed: true };
  }
}

module.exports = {
  allowHeadedFallback,
  isBrowserWedgedProtocolError,
  newPageWithBrowserReload,
  relaunchBrowserOnWedge,
  buildCommonLaunchOptions,
  buildIsolatedBrowserEnv,
  isHeadlessChromiumLaunchCrash,
  launchPersistentContext,
  launchFailureAdvice,
  resolveExecutablePath,
  shouldRetryHeaded,
  wantsHeadless,
};
