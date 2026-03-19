const { chromium } = require('playwright');
const { ensureProfileDir } = require('./huanxin_profile');

function usage() {
  console.error('Usage: node huanxin_shell_exec.js <envName> --command <shell command>');
  process.exit(1);
}

function parseArgs(argv) {
  const envName = argv[0];
  if (!envName) usage();

  let command = null;
  for (let index = 1; index < argv.length; index += 1) {
    if (argv[index] === '--command') {
      command = argv[index + 1] || null;
      index += 1;
      continue;
    }
    usage();
  }

  if (!command) usage();
  return { envName, command };
}

async function openShell(page, envName) {
  let lastError = null;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      await page.goto(
        'https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev',
        { waitUntil: 'networkidle', timeout: 180000 }
      );
      await page.waitForTimeout(3000);

      const row = page.locator('tr', { hasText: envName }).first();
      await row.waitFor({ state: 'visible', timeout: 60000 });
      await row.getByRole('button', { name: '打开' }).click({ timeout: 15000 });
      await page.waitForTimeout(5000);
      lastError = null;
      break;
    } catch (error) {
      lastError = error;
      if (attempt === 3) {
        throw error;
      }
      await page.reload({ waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
      await page.waitForTimeout(4000);
    }
  }

  const pages = page.context().pages();
  const activePage = pages[pages.length - 1];
  await activePage.waitForTimeout(3000);

  const shellTrigger = activePage.getByText('Shell终端', { exact: true }).first();
  await shellTrigger.click({ timeout: 10000 });
  await activePage.waitForTimeout(5000);
  return activePage;
}

async function focusTerminal(activePage) {
  const terminal = activePage.locator('.terminal.xterm').first();
  const terminalInput = activePage.locator('.xterm-helper-textarea').first();
  await terminal.waitFor({ state: 'visible', timeout: 30000 });
  await terminalInput.waitFor({ state: 'attached', timeout: 30000 });
  await terminal.click({ timeout: 10000, force: true });
  await terminalInput.evaluate((element) => element.focus());
  await activePage.waitForTimeout(300);
  return terminalInput;
}

async function readTerminalText(activePage) {
  return activePage.evaluate(() => {
    const rows = Array.from(document.querySelectorAll('.terminal.xterm .xterm-rows')).map((node) =>
      (node.textContent || '').replace(/\u00a0/g, ' ')
    );
    return rows
      .join('\n')
      .split('\n')
      .map((line) => line.replace(/\s+/g, ' ').trim())
      .filter(Boolean)
      .join('\n');
  });
}

async function sendCommand(activePage, command, waitMs = 2500) {
  await focusTerminal(activePage);
  const before = await readTerminalText(activePage);
  await activePage.keyboard.insertText(command);
  await activePage.keyboard.press('Enter');
  await activePage.waitForTimeout(waitMs);
  const after = await readTerminalText(activePage);
  return { before, after };
}

async function main() {
  const { envName, command } = parseArgs(process.argv.slice(2));
  const { profileDir } = ensureProfileDir();
  const context = await chromium.launchPersistentContext(profileDir, {
    headless: process.env.HUANXIN_HEADLESS === '1',
    viewport: { width: 1600, height: 1000 },
    slowMo: 50,
  });

  try {
    const page = context.pages()[0] || (await context.newPage());
    page.setDefaultTimeout(30000);

    const activePage = await openShell(page, envName);
  const { before, after } = await sendCommand(activePage, command);

    await activePage.screenshot({ path: `browser-automation/huanxin-shell-${envName}.png`, fullPage: true });
    console.log(
      JSON.stringify(
        {
          ok: true,
          envName,
          url: activePage.url(),
          command,
          before,
          after,
        },
        null,
        2
      )
    );
  } finally {
    await context.close();
  }
}

module.exports = {
  focusTerminal,
  openShell,
  readTerminalText,
  sendCommand,
};

if (require.main === module) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
