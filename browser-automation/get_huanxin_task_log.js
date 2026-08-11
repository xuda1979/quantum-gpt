#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { TRAIN_DEV_URL, bridgePageViaSafariSso, classifyUrl } = require('./huanxin_repair_profile_via_safari_sso');

const TARGET_URL = 'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-868c196fb82d3e0b8cfbbe826d8afd0a?name=ASI2';
const TASK_NAME = process.argv[2] || 'asi2-dlora-2npu-0605-v11-2c';

async function clickByVisibleText(page, text) {
  const locator = page.getByText(text, { exact: true });
  const count = await locator.count().catch(() => 0);
  for (let i = 0; i < count; i++) {
    const candidate = locator.nth(i);
    if (await candidate.isVisible().catch(() => false)) {
      await candidate.click({ timeout: 10000 });
      return true;
    }
  }
  const locatorApprox = page.getByText(text);
  const countApprox = await locatorApprox.count().catch(() => 0);
  for (let i = 0; i < countApprox; i++) {
    const candidate = locatorApprox.nth(i);
    if (await candidate.isVisible().catch(() => false)) {
      await candidate.click({ timeout: 10000 });
      return true;
    }
  }
  return false;
}

async function main() {
  const { profileDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;
  let page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);
  const networkEvents = [];
  page.on('response', async (response) => {
    const request = response.request();
    const url = response.url();
    if (!/\/web\//.test(url) || !['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method())) {
      return;
    }
    let responsePreview = '';
    try { responsePreview = (await response.text()).slice(0, 4000); } catch (error) { responsePreview = '<<unavailable>>'; }
    networkEvents.push({ method: request.method(), url, status: response.status(), requestPreview: String(request.postData() || '').slice(0, 2000), responsePreview });
  });

  try {
    console.log("Navigating to target URL:", TARGET_URL);
    await page.goto(TARGET_URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);

    if (classifyUrl(page.url()) === 'login_required') {
      console.log("Login required, bridging via Safari SSO...");
      const bridge = await bridgePageViaSafariSso(page, {
        authUrl: page.url(),
        targetUrl: TARGET_URL,
        waitMs: 12000,
        resultPath: `/tmp/huanxin-task-log-bridge-${Date.now()}.json`
      });
      if (!bridge.ok) {
        throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
      }
      await page.waitForTimeout(3000);
    }

    console.log("Opening task list...");
    await clickByVisibleText(page, '任务列表');
    await page.waitForTimeout(4000);

    console.log("Checking if task list drawer is already open...");
    const initialRowsCount = await page.locator('tr.ant-table-row').count().catch(() => 0);
    if (initialRowsCount > 0) {
      console.log(`Task list drawer is already open with ${initialRowsCount} rows. Skipping click.`);
    } else {
      console.log("Opening task list via button click...");
      await clickByVisibleText(page, '任务列表');
      await page.waitForTimeout(4000);
    }

    console.log(`Locating task row for: ${TASK_NAME}...`);
    const row = page.locator('tr.ant-table-row', { hasText: TASK_NAME }).first();
    const count = await row.count();
    if (count === 0) {
      console.log(`Could not find row for task: ${TASK_NAME}`);
      return;
    }

    // Horizontal scroll of the table container to expose any hidden elements
    console.log("Attempting to scroll table container horizontally...");
    await page.evaluate(() => {
      const el = document.querySelector('.ant-table-body, .ant-table-content');
      if (el) {
        el.scrollLeft = 2000;
        console.log("Scrolled successfully, left is now:", el.scrollLeft);
      } else {
        console.log("Could not find table scrollable container!");
      }
    });
    await page.waitForTimeout(2000);

    // Capture a new screenshot after scrolling
    const scrollScreenshotPath = path.resolve(__dirname, `huanxin-task-row-scrolled-${TASK_NAME}.png`);
    await page.screenshot({ path: scrollScreenshotPath }).catch(() => {});
    console.log("Row inner HTML structure after scroll:");
    const rowHTML = await row.innerHTML();
    console.log(rowHTML);

    // Let us find and click any button or link in that row that might be "详情", "日志", "查看", etc.
    const buttonsInRow = row.locator('button, a, [role="button"], span').filter({ hasText: /详情|日志|查看/ });
    const btnCount = await buttonsInRow.count().catch(() => 0);
    console.log(`Found ${btnCount} detail/log buttons in the row.`);

    if (btnCount > 0) {
      const btn = buttonsInRow.first();
      const txt = await btn.innerText();
      console.log(`Clicking button: ${txt}`);
      await btn.click({ timeout: 15000 });
      await page.waitForTimeout(5000);
    } else {
      // Click the task name cell first (opens the detail modal)
      const nameCell = row.locator('span.ellipsis-text.hover.isModal').first();
      const nameVisible = await nameCell.isVisible().catch(() => false);
      if (nameVisible) {
        console.log("Clicking task name cell (detail modal)...");
        await nameCell.click({ timeout: 10000 });
        await page.waitForTimeout(6000);
      } else {
        // Fallback: click the "失败" tag
        const failedTag = row.locator('span').filter({ hasText: '失败' }).first();
        console.log("Clicking the failed tag...");
        await failedTag.click({ timeout: 10000 }).catch(() => {});
        await page.waitForTimeout(5000);
      }
    }

    console.log("Checking if a task log or details modal/drawer/page has been loaded...");
    const popupText = await page.locator('body').innerText().catch(() => '');
    console.log("Page layout preview after clicks (first 6000 chars):");
    console.log(popupText.slice(0, 6000));
    console.log("Page layout preview after clicks (LAST 6000 chars):");
    console.log(popupText.slice(-6000));

    // If there is any network request captured for logs, print them
    console.log("Captured network transactions during clicks:");
    for (const e of networkEvents) {
      if (e.url.includes("task") || e.url.includes("log")) {
        console.log(`Method: ${e.method} URL: ${e.url} Status: ${e.status}`);
        console.log("Response preview:", String(e.responsePreview || '').slice(0, 3000));
        console.log("------------------------");
      }
    }

    const finalScreenshotPath = path.resolve(__dirname, `huanxin-task-details-${TASK_NAME}.png`);
    await page.screenshot({ path: finalScreenshotPath, fullPage: true }).catch(() => {});
    console.log(`Saved final screenshot to ${finalScreenshotPath}`);

    // Capture screenshot of the task details page
    const screenshotPath = path.resolve(__dirname, `huanxin-task-log-${TASK_NAME}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
    console.log(`Saved screenshot to ${screenshotPath}`);

  } catch (err) {
    console.error("Error in logger:", err.stack || err.message || err);
  } finally {
    await context.close().catch(() => {});
  }
}

main();
