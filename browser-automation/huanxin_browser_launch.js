const { chromium } = require('playwright');

function wantsHeadless() {
  return process.env.HUANXIN_HEADLESS !== '0';
}

function allowHeadedFallback() {
  return process.env.HUANXIN_ALLOW_HEADED_FALLBACK !== '0';
}

function buildCommonLaunchOptions(headless) {
  return {
    headless,
    executablePath: chromium.executablePath(),
    viewport: { width: 1600, height: 1000 },
    slowMo: 50,
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
    const context = await chromium.launchPersistentContext(profileDir, buildCommonLaunchOptions(attemptedHeadless));
    return { context, browserMode: attemptedHeadless ? 'headless' : 'headed', fallbackUsed: false };
  } catch (error) {
    if (!shouldRetryHeaded(error, attemptedHeadless)) {
      throw error;
    }

    console.error(
      '[huanxin_launch] Headless Chromium launch failed on Darwin; retrying with headed browser fallback.'
    );
    const context = await chromium.launchPersistentContext(profileDir, buildCommonLaunchOptions(false));
    return { context, browserMode: 'headed', fallbackUsed: true };
  }
}

module.exports = {
  allowHeadedFallback,
  buildCommonLaunchOptions,
  launchPersistentContext,
  shouldRetryHeaded,
  wantsHeadless,
};
