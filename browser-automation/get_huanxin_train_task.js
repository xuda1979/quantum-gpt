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
    if (url.includes('/web/') || url.includes('/api/')) {
      let preview = '';
      try { responsePreview = await response.text(); preview = responsePreview.slice(0, 4000); } catch {}
      networkEvents.push({ url, status: response.status(), preview });
    }
  });

  try {
    console.log("Navigating to:", TARGET_URL);
    await page.goto(TARGET_URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);

    if (classifyUrl(page.url()) === 'login_required') {
      await bridgePageViaSafariSso(page, {
        authUrl: page.url(),
        targetUrl: TARGET_URL,
        waitMs: 12000,
        resultPath: `/tmp/huanxin-train-task-bridge-${Date.now()}.json`
      });
      await page.waitForTimeout(3000);
    }

    // Escape the sandbox by going back to the main train-dev list page first
    const listUrl = 'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev';
    console.log("Navigating to main train-dev list to expose the full sidebar:", listUrl);
    await page.goto(listUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
    await page.waitForTimeout(3000);

    // Direct left sidebar navigation: click "训练任务" (Training Task)
    console.log("Locating sidebar menu item '训练任务'...");
    const sidebarItem = page.locator('.ant-menu-item, li, a, span').filter({ hasText: /^训练任务$/ }).first();
    const isVisible = await sidebarItem.isVisible().catch(() => false);
    if (isVisible) {
      console.log("Clicking '训练任务' menu item...");
      await sidebarItem.click({ timeout: 15000 });
      await page.waitForTimeout(5000);
    } else {
      console.log("Left sidebar menu item '训练任务' is not directly visible. Searching broadly...");
      await clickByVisibleText(page, '训练任务');
      await page.waitForTimeout(5000);
    }

    console.log("Current Page URL after navigation:", page.url());
    const mainBody = await page.locator('body').innerText().catch(() => '');
    console.log("Page Main Body Preview (first 2000 chars):");
    console.log(mainBody.slice(0, 2000));

    console.log(`Searching for task '${TASK_NAME}' in full training task table...`);
    const row = page.locator('tr.ant-table-row', { hasText: TASK_NAME }).first();
    const rowExists = await row.count();
    if (rowExists > 0) {
      console.log("Found task row on first page of Training Tasks!");
      const rowText = await row.innerText();
      console.log("Task Row details:", rowText);

      // Print row inner HTML to find action buttons
      const html = await row.innerHTML();
      console.log("Row cells HTML:");
      console.log(html);

      // Try to scroll the table horizontally if needed
      await page.evaluate(() => {
        const el = document.querySelector('.ant-table-body, .ant-table-content');
        if (el) el.scrollLeft = 2000;
      });
      await page.waitForTimeout(1000);

      // Find any buttons/links like "详情", "日志", "查看日志", "Console", etc.
      const actionItems = row.locator('button, a, span, div.ant-dropdown-trigger').filter({ hasText: /日志|详情|查看/ });
      const actionsCount = await actionItems.count();
      console.log(`Found ${actionsCount} action items matching '日志/详情/查看'.`);
      for (let i = 0; i < actionsCount; i++) {
        const item = actionItems.nth(i);
        const tag = await item.evaluate(n => n.tagName);
        const txt = await item.innerText();
        console.log(`Action ${i}: [${tag}] text="${txt}"`);
      }

      if (actionsCount > 0) {
        console.log("Clicking the first action item...");
        await actionItems.first().click({ timeout: 15000 });
        await page.waitForTimeout(5000);
        const afterClickBody = await page.locator('body').innerText().catch(() => '');
        console.log("Content after click (first 3000 chars):");
        console.log(afterClickBody.slice(0, 3000));
        
        // Let's print out captured network logs containing tail/log details!
        console.log("\n--- Captured logs from API responses ---");
        for (const ne of networkEvents) {
          if (ne.url.includes("log") || ne.url.includes("detail") || ne.url.includes("tail")) {
            console.log(`URL: ${ne.url}`);
            console.log(`Response: ${ne.preview}`);
            console.log("------------------------");
          }
        }
      }
    } else {
      console.log(`Task '${TASK_NAME}' was not found on the first page of the main list.`);
    }

    const screenshotPath = path.resolve(__dirname, `huanxin-train-page-${TASK_NAME}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
    console.log(`Saved screenshot to ${screenshotPath}`);

  } catch (err) {
    console.error("Error navigating / fetching logs:", err.stack || err.message || err);
  } finally {
    await context.close().catch(() => {});
  }
}

main();
