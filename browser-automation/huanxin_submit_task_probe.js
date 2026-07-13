#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const {
  TRAIN_DEV_URL,
  bridgePageViaSafariSso,
  classifyUrl,
} = require('./huanxin_repair_profile_via_safari_sso');

function parseArgs(argv) {
  const args = {
    url: TRAIN_DEV_URL,
    clickText: '提交任务',
    waitMs: 12000,
    screenshot: 'browser-automation/huanxin-submit-task-probe.png',
    dumpHtml: 'browser-automation/huanxin-submit-task-probe.html',
    dumpJson: 'browser-automation/huanxin-submit-task-probe.json',
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--url') {
      args.url = argv[++index];
      continue;
    }
    if (token === '--click-text') {
      args.clickText = argv[++index];
      continue;
    }
    if (token === '--wait-ms') {
      args.waitMs = parseInt(argv[++index], 10);
      continue;
    }
    if (token === '--screenshot') {
      args.screenshot = argv[++index];
      continue;
    }
    if (token === '--dump-html') {
      args.dumpHtml = argv[++index];
      continue;
    }
    if (token === '--dump-json') {
      args.dumpJson = argv[++index];
      continue;
    }
    throw new Error(`Unknown argument: ${token}`);
  }

  return args;
}

function cleanText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

async function clickByVisibleText(page, text) {
  for (const locator of [page.getByText(text, { exact: true }), page.getByText(text)]) {
    const count = await locator.count().catch(() => 0);
    for (let index = 0; index < count; index += 1) {
      const candidate = locator.nth(index);
      const visible = await candidate.isVisible().catch(() => false);
      if (!visible) {
        continue;
      }
      await candidate.click({ timeout: 15000 });
      return true;
    }
  }
  return false;
}

async function collectPageSummary(page) {
  return page.evaluate(() => {
    const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
    const isVisible = (element) => {
      if (!(element instanceof HTMLElement)) {
        return false;
      }
      const style = window.getComputedStyle(element);
      if (!style || style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
        return false;
      }
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };
    const labelFor = (element) => {
      if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement || element instanceof HTMLSelectElement) {
        if (element.labels && element.labels.length > 0) {
          return clean(element.labels[0].innerText || element.labels[0].textContent || '');
        }
      }
      const formItem = element.closest('.ant-form-item, .ant-form-item-control, .ant-form-item-row');
      if (formItem) {
        const label = formItem.querySelector('label, .ant-form-item-label');
        if (label) {
          return clean(label.innerText || label.textContent || '');
        }
      }
      const previous = element.previousElementSibling;
      if (previous && isVisible(previous)) {
        const text = clean(previous.innerText || previous.textContent || '');
        if (text) {
          return text;
        }
      }
      return '';
    };

    const buttons = Array.from(document.querySelectorAll('button, [role="button"]'))
      .filter(isVisible)
      .map((element) => ({
        text: clean(element.innerText || element.textContent || ''),
        disabled: Boolean(element.disabled) || element.getAttribute('aria-disabled') === 'true',
        className: (element.getAttribute('class') || '').slice(0, 240),
      }))
      .filter((entry) => entry.text || entry.className)
      .slice(0, 80);

    const fields = Array.from(
      document.querySelectorAll('input, textarea, select, [role="combobox"], .ant-select-selector, .ant-upload')
    )
      .filter(isVisible)
      .map((element) => ({
        tag: element.tagName,
        type: element.getAttribute('type') || '',
        label: labelFor(element),
        placeholder: element.getAttribute('placeholder') || '',
        ariaLabel: element.getAttribute('aria-label') || '',
        text: clean(element.innerText || element.textContent || ''),
        className: (element.getAttribute('class') || '').slice(0, 240),
      }))
      .slice(0, 120);

    const panels = Array.from(
      document.querySelectorAll('[role="dialog"], .ant-drawer-content-wrapper, .ant-modal-content, .ant-drawer-body')
    )
      .filter(isVisible)
      .map((element) => ({
        className: (element.getAttribute('class') || '').slice(0, 240),
        text: clean(element.innerText || element.textContent || '').slice(0, 2000),
      }))
      .filter((entry) => entry.text)
      .slice(0, 20);

    const headings = Array.from(
      document.querySelectorAll('h1, h2, h3, h4, .ant-drawer-title, .ant-modal-title, label, legend')
    )
      .filter(isVisible)
      .map((element) => clean(element.innerText || element.textContent || ''))
      .filter(Boolean)
      .slice(0, 80);

    return {
      title: document.title,
      url: location.href,
      bodyPreview: clean(document.body.innerText || '').slice(0, 5000),
      headings,
      buttons,
      fields,
      panels,
    };
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const { profileDir, isolated, sourceDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;
  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);

  let bridge = null;
  try {
    await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);

    if (classifyUrl(page.url()) === 'login_required') {
      bridge = await bridgePageViaSafariSso(page, {
        authUrl: page.url(),
        targetUrl: args.url,
        waitMs: args.waitMs,
        resultPath: `/tmp/huanxin-submit-task-probe-${Date.now()}.json`,
      });
      if (!bridge.ok) {
        throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
      }
      await page.waitForTimeout(3000);
    }

    if (!page.url().includes('/train-dev/environment/')) {
      await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
      await page.waitForTimeout(3000);
    }

    const clicked = await clickByVisibleText(page, args.clickText);
    if (!clicked) {
      const preview = cleanText(await page.locator('body').innerText().catch(() => '')).slice(0, 1000);
      throw new Error(`Could not click visible text: ${args.clickText}. Body preview: ${preview}`);
    }

    await page.waitForTimeout(5000);

    const summary = await collectPageSummary(page);
    const result = {
      ok: true,
      browserMode: launch.browserMode,
      launchFallbackUsed: launch.fallbackUsed,
      clickText: args.clickText,
      bridge,
      usedProfile: {
        profileDir,
        isolated,
        sourceDir,
      },
      ...summary,
      timestamp: new Date().toISOString(),
    };

    if (args.screenshot) {
      fs.mkdirSync(path.dirname(path.resolve(args.screenshot)), { recursive: true });
      await page.screenshot({ path: path.resolve(args.screenshot), fullPage: true }).catch(() => {});
    }
    if (args.dumpHtml) {
      fs.mkdirSync(path.dirname(path.resolve(args.dumpHtml)), { recursive: true });
      fs.writeFileSync(path.resolve(args.dumpHtml), await page.content(), 'utf8');
    }
    if (args.dumpJson) {
      fs.mkdirSync(path.dirname(path.resolve(args.dumpJson)), { recursive: true });
      fs.writeFileSync(path.resolve(args.dumpJson), JSON.stringify(result, null, 2), 'utf8');
    }

    console.log(JSON.stringify(result, null, 2));
  } finally {
    await context.close().catch(() => {});
  }
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
