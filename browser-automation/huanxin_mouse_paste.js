const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

function usage() {
  console.error(
    'Usage: node huanxin_mouse_paste.js <url> --click-text <text> [--paste-file <file>] [--replace] [--submit-shortcut cmd-enter|ctrl-enter|none]'
  );
  process.exit(1);
}

function parseArgs(argv) {
  if (argv.length < 2) usage();

  const args = {
    url: argv[0],
    clickText: null,
    pasteFile: null,
    replace: false,
    submitShortcut: 'none',
  };

  for (let index = 1; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--click-text') {
      args.clickText = argv[++index];
      continue;
    }
    if (token === '--paste-file') {
      args.pasteFile = argv[++index];
      continue;
    }
    if (token === '--replace') {
      args.replace = true;
      continue;
    }
    if (token === '--submit-shortcut') {
      args.submitShortcut = argv[++index] || 'none';
      continue;
    }
    usage();
  }

  if (!args.clickText) usage();
  return args;
}

async function clickByVisibleText(page, text) {
  const exactLocator = page.getByText(text, { exact: true }).first();
  if (await exactLocator.count()) {
    await exactLocator.click({ timeout: 10000 });
    return;
  }

  const fuzzyLocator = page.getByText(text).first();
  if (await fuzzyLocator.count()) {
    await fuzzyLocator.click({ timeout: 10000 });
    return;
  }

  throw new Error(`Could not find clickable text: ${text}`);
}

async function submitIfRequested(page, submitShortcut) {
  if (submitShortcut === 'cmd-enter') {
    await page.keyboard.press('Meta+Enter');
    return;
  }
  if (submitShortcut === 'ctrl-enter') {
    await page.keyboard.press('Control+Enter');
    return;
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const userDataDir = path.resolve(process.env.HUANXIN_PROFILE_DIR || 'browser-automation/profile');
  fs.mkdirSync(userDataDir, { recursive: true });

  const context = await chromium.launchPersistentContext(userDataDir, {
    headless: false,
    slowMo: 50,
    viewport: { width: 1440, height: 900 },
  });

  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);
  await page.goto(args.url, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);

  await clickByVisibleText(page, args.clickText);
  await page.waitForTimeout(500);

  if (args.pasteFile) {
    const text = fs.readFileSync(path.resolve(args.pasteFile), 'utf8');
    if (args.replace) {
      await page.keyboard.press('Meta+A');
      await page.waitForTimeout(150);
    }
    await page.keyboard.insertText(text);
    await page.waitForTimeout(300);
    await submitIfRequested(page, args.submitShortcut);
  }

  console.log(
    JSON.stringify(
      {
        ok: true,
        url: page.url(),
        clickText: args.clickText,
        pasteFile: args.pasteFile,
        replace: args.replace,
        submitShortcut: args.submitShortcut,
      },
      null,
      2
    )
  );

  process.stdin.resume();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
