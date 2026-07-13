#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { TRAIN_DEV_URL, bridgePageViaSafariSso, classifyUrl } = require('./huanxin_repair_profile_via_safari_sso');

const TASK_ID = process.argv[2] || 'dt-838e5ec45e7d431ebfe74e132d255b9a';
const TARGET_URL = `https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-task/train-task-detail/${TASK_ID}`;

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
    console.log("Navigating directly to task details URL:", TARGET_URL);
    await page.goto(TARGET_URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(4000);

    if (classifyUrl(page.url()) === 'login_required') {
      console.log("Login required, bridging via Safari SSO...");
      await bridgePageViaSafariSso(page, {
        authUrl: page.url(),
        targetUrl: TARGET_URL,
        waitMs: 12000,
        resultPath: `/tmp/huanxin-task-detail-bridge-${Date.now()}.json`
      });
      await page.waitForTimeout(4000);
    }

    // Wait for the detail tabs element to be loaded
    console.log("Waiting for detail content to load...");
    await page.locator('.ant-tabs-nav-list, body').first().waitFor({ state: 'visible', timeout: 30000 });
    await page.waitForTimeout(2000);

    const bodyText = await page.locator('body').innerText().catch(() => '');
    console.log("=== Basic Page Info ===");
    console.log(bodyText.slice(0, 2000));
    console.log("=======================\n");

    const tabsList = ['错误信息', '运行日志', '性能监控', '基本信息'];
    for (const tabName of tabsList) {
      console.log(`Checking/Clicking tab: "${tabName}"...`);
      const clicked = await clickByVisibleText(page, tabName);
      if (clicked) {
        console.log(`Successfully clicked tab "${tabName}". Waiting for logs to render...`);
        await page.waitForTimeout(4000);
        
        // Take screenshot of this tab
        const tabScreenshot = path.resolve(__dirname, `huanxin-task-${TASK_ID}-${tabName}.png`);
        await page.screenshot({ path: tabScreenshot }).catch(() => {});
        console.log(`Saved screenshot for ${tabName} to ${tabScreenshot}`);

        // Extract container text (usually in <pre> or .log-container or .ant-card-body etc.)
        const visibleText = await page.locator('body').innerText().catch(() => '');
        console.log(`--- Content under tab "${tabName}" (up to 4000 chars) ---`);
        console.log(visibleText.slice(0, 4000));
        console.log("==================================================\n");
      } else {
        console.log(`Could not click tab "${tabName}".`);
      }
    }

    console.log("\n--- Captured AJAX Responses ---");
    for (const ne of networkEvents) {
      if (ne.url.includes("log") || ne.url.includes("detail") || ne.url.includes("err")) {
        console.log(`URL: ${ne.url}`);
        console.log(`Response: ${ne.preview}`);
        console.log("-----------------------------------------");
      }
    }

  } catch (err) {
    console.error("Error fetching task details:", err.stack || err.message || err);
  } finally {
    await context.close().catch(() => {});
  }
}

main();
