#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { TRAIN_DEV_URL, bridgePageViaSafariSso, classifyUrl } = require('./huanxin_repair_profile_via_safari_sso');

const TARGET_URL = 'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-task';
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
    if (url.includes('/web/') || url.includes('/api/')) {
      let preview = '';
      try {
        const text = await response.text();
        preview = text.slice(0, 4000);
      } catch {}
      networkEvents.push({ url, status: response.status(), preview });
    }
  });

  try {
    console.log("Navigating directly to Training Task page:", TARGET_URL);
    await page.goto(TARGET_URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);

    if (classifyUrl(page.url()) === 'login_required') {
      console.log("Login required, bridging via Safari SSO...");
      await bridgePageViaSafariSso(page, {
        authUrl: page.url(),
        targetUrl: TARGET_URL,
        waitMs: 12000,
        resultPath: `/tmp/huanxin-click-task-bridge-${Date.now()}.json`
      });
      await page.waitForTimeout(3000);
    }

    console.log(`Locating task row for: ${TASK_NAME}...`);
    // Wait for at least one table row to be visible first to ensure page is loaded
    await page.locator('tr.ant-table-row').first().waitFor({ state: 'visible', timeout: 30000 }).catch(() => {
      console.log("Timed out waiting for tr.ant-table-row to be visible.");
    });
    await page.waitForTimeout(2000);

    const row = page.locator('tr.ant-table-row', { hasText: TASK_NAME }).first();
    const rowExists = await row.count();
    if (rowExists === 0) {
      console.log(`Could not find task '${TASK_NAME}' on first page.`);
      return;
    }

    const taskSpan = row.locator('span.ellipsis-text.hover.isModal').first();
    console.log("Clicking the task name span trigger...");
    await taskSpan.scrollIntoViewIfNeeded();
    await taskSpan.click({ timeout: 15000 });
    await page.waitForTimeout(5000);

    console.log("Locating the opened drawer or modal...");
    const drawer = page.locator('.ant-drawer-content, .ant-modal-content').last();
    const drawerVisible = await drawer.isVisible().catch(() => false);
    console.log("Drawer or modal visible:", drawerVisible);

    if (drawerVisible) {
      const drawerText = await drawer.innerText().catch(() => '');
      console.log("\n--- Drawer / Modal Initial Text ---");
      console.log(drawerText.slice(0, 4000));
      console.log("---------------------------------\n");

      // Check for available tabs inside the drawer/modal
      const tabs = drawer.locator('.ant-tabs-tab, .ant-menu-item, span').filter({ hasText: /日志|运行日志|失败原因|实时日志|错误/ });
      const tabsCount = await tabs.count().catch(() => 0);
      console.log(`Found ${tabsCount} tab elements in the details drawer.`);
      for (let i = 0; i < tabsCount; i++) {
        const text = await tabs.nth(i).innerText().catch(() => '');
        console.log(`Tab ${i}: "${text}"`);
      }

      // Try clicking them to retrieve stdout/stderr
      const tabTexts = ['运行日志', '日志', '实时日志', 'Logs', 'Log', '控制台', '错误信息', '失败原因'];
      for (const tabText of tabTexts) {
        const tabEl = drawer.locator('span, div, button, a').filter({ hasText: tabText }).first();
        const tabVisible = await tabEl.isVisible().catch(() => false);
        if (tabVisible) {
          console.log(`Clicking tab: ${tabText}...`);
          await tabEl.click({ timeout: 10000 }).catch(async () => {
            await tabEl.evaluate(node => node.click());
          });
          await page.waitForTimeout(3000);
          
          console.log(`--- Content after clicking tab "${tabText}" ---`);
          const currentDrawerText = await drawer.innerText().catch(() => '');
          console.log(currentDrawerText.slice(0, 4000));
          console.log("==========================================");
        }
      }
    } else {
      console.log("Could not open details drawer/modal!");
    }

    // Print captured API response previews to see if they returned fail/log reason
    console.log("\n--- Captured API logs ---");
    for (const ne of networkEvents) {
      if (ne.url.includes("log") || ne.url.includes("detail") || ne.url.includes("info")) {
        console.log(`URL: ${ne.url}`);
        console.log(`Response: ${ne.preview}`);
        console.log("------------------------");
      }
    }

    const screenshotPath = path.resolve(__dirname, `huanxin-task-details-full-${TASK_NAME}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
    console.log(`Saved screenshot to ${screenshotPath}`);

  } catch (err) {
    console.error("Error clicking/logging:", err.stack || err.message || err);
  } finally {
    await context.close().catch(() => {});
  }
}

main();
