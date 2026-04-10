const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

function wantsHeadless() {
  return process.env.HUANXIN_HEADLESS !== '0';
}

function allowHeadedFallback() {
  return process.env.HUANXIN_ALLOW_HEADED_FALLBACK !== '0';
}

function resolveExecutablePath() {
  if (process.env.HUANXIN_BROWSER_EXECUTABLE_PATH) {
    return path.resolve(process.env.HUANXIN_BROWSER_EXECUTABLE_PATH);
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

  return {
    headless,
    executablePath: resolveExecutablePath(),
    viewport: { width: 1600, height: 1000 },
    slowMo: 50,
    env: buildIsolatedBrowserEnv(profileDir),
    args: [
      `--crash-dumps-dir=${crashpadDir}`,
      '--disable-crash-reporter',
      '--disable-crashpad-for-testing',
    ],
  };
}

function shouldRetryHeaded(error, attemptedHeadless) {
  if (!attemptedHeadless) return false;
  if (process.platform !== 'darwin') return false;
  if (!allowHeadedFallback()) return false;

  const message = String(error && (error.stack || error.message || error));
  return (
    message.includes('MachPortRendezvousServer') ||
    message.includes('bootstrap_check_in') ||
    message.includes('signal=SIGABRT') ||
    message.includes('Target page, context or browser has been closed')
  );
}

async function launchPersistentContext(profileDir) {
  const attemptedHeadless = wantsHeadless();
  try {
    const context = await chromium.launchPersistentContext(
      profileDir,
      buildCommonLaunchOptions(attemptedHeadless, profileDir)
    );
    return { context, browserMode: attemptedHeadless ? 'headless' : 'headed', fallbackUsed: false };
  } catch (error) {
    if (!shouldRetryHeaded(error, attemptedHeadless)) {
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
  launchPersistentContext,
  resolveExecutablePath,
  shouldRetryHeaded,
  wantsHeadless,
};
