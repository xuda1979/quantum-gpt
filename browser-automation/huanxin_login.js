/**
 * huanxin_login.js — Open a headed browser using the BASE persistent profile,
 * navigate to Huanxin, and wait for the user to log in manually.
 *
 * Once authenticated state is detected (or the user presses Ctrl+C), the
 * browser closes and the profile on disk retains cookies/localStorage/session
 * so future headless runs are already authenticated.
 *
 * Usage:
 *   node huanxin_login.js            # Opens Huanxin login page in headed Chromium
 *   node huanxin_login.js --timeout 300  # Wait up to 300s for login (default: 600s)
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { getBaseProfileDir } = require('./huanxin_profile');

const HUANXIN_URL =
  'https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev';

function parseArgs(argv) {
  const args = { timeout: 600 };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--timeout') args.timeout = Number(argv[++i]);
  }
  return args;
}

function isLoggedIn(url, title, bodyText) {
  const lUrl = (url || '').toLowerCase();
  const lText = (bodyText || '').toLowerCase();

  // Redirected to OIDC login — not logged in
  if (lUrl.includes('/auth/realms/') && lUrl.includes('openid-connect/auth')) {
    return false;
  }

  // Explicit login prompts in body
  if (lText.includes('扫码登录')) return false;
  if (lText.includes('登录') && !lText.includes('训练') && !lText.includes('开发')) return false;

  // Has app content → logged in
  if (lText.includes('训练') || lText.includes('开发') || lText.includes('项目')) {
    return true;
  }

  // URL still on app page but empty body — SPA loading, treat as pending
  return false;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const profileDir = getBaseProfileDir();
  fs.mkdirSync(profileDir, { recursive: true });

  console.log(`[login] Opening headed browser with base profile: ${profileDir}`);
  console.log(`[login] Navigating to: ${HUANXIN_URL}`);
  console.log(`[login] Please log in manually (QR code or password).`);
  console.log(`[login] Will auto-detect login success or timeout after ${args.timeout}s.`);
  console.log(`[login] Press Ctrl+C at any time to save & exit.\n`);

  const context = await chromium.launchPersistentContext(profileDir, {
    headless: false,
    slowMo: 50,
    viewport: { width: 1440, height: 900 },
  });

  const page = context.pages()[0] || await context.newPage();
  page.setDefaultTimeout(30000);
  await page.goto(HUANXIN_URL, { waitUntil: 'domcontentloaded' });

  // Poll for login success
  const deadline = Date.now() + args.timeout * 1000;
  let authenticated = false;

  while (Date.now() < deadline) {
    await page.waitForTimeout(3000);
    try {
      const url = page.url();
      const title = await page.title();
      const bodyText = await page.locator('body').innerText().catch(() => '');
      const clean = (bodyText || '').replace(/\s+/g, ' ').trim();

      if (isLoggedIn(url, title, clean)) {
        authenticated = true;
        console.log(`[login] ✓ Authenticated! title="${title}", url="${url}"`);
        console.log(`[login] Waiting 5s for session data to flush to profile...`);
        await page.waitForTimeout(5000);
        break;
      }
      const elapsed = Math.round((Date.now() - (deadline - args.timeout * 1000)) / 1000);
      process.stdout.write(`\r[login] Waiting for login... (${elapsed}s / ${args.timeout}s)`);
    } catch {
      // page might be navigating, retry
    }
  }

  if (!authenticated) {
    console.log(`\n[login] Timeout reached. Saving profile as-is.`);
  }

  // Graceful close — Chromium flushes cookies/storage on close
  await context.close();

  console.log(`[login] Profile saved to: ${profileDir}`);
  console.log(`[login] Run the probe to verify: node huanxin_probe.js`);
}

// Handle Ctrl+C gracefully — still close context to flush profile
let _context;
process.on('SIGINT', async () => {
  console.log(`\n[login] Ctrl+C received. Saving profile and exiting...`);
  process.exit(0);
});

main().catch((err) => {
  console.error('[login] Error:', err.message);
  process.exit(1);
});
