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
      '--remote-debugging-port=9224',
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
  buildCommonLaunchOptions,
  buildIsolatedBrowserEnv,
  isHeadlessChromiumLaunchCrash,
  launchPersistentContext,
  launchFailureAdvice,
  resolveExecutablePath,
  shouldRetryHeaded,
  wantsHeadless,
};
