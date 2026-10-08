#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { TRAIN_DEV_URL, bridgePageViaSafariSso, classifyUrl } = require('./huanxin_repair_profile_via_safari_sso');

const TARGET_URL = 'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-868c196fb82d3e0b8cfbbe826d8afd0a?name=ASI2';

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
        resultPath: `/tmp/huanxin-poll-task-${Date.now()}.json`
      });
      if (!bridge.ok) {
        throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
      }
      await page.waitForTimeout(3000);
    }

    console.log("Opening task list...");
    const clicked = await clickByVisibleText(page, '任务列表');
    if (!clicked) {
      console.log("Could not find 任务列表 button!");
    }
    await page.waitForTimeout(4000);

    console.log("Gathering table rows...");
    const rows = page.locator('tr.ant-table-row');
    const count = await rows.count();
    console.log(`Found ${count} rows.`);
    
    const taskDetails = [];
    for (let i = 0; i < count; i++) {
      const row = rows.nth(i);
      const text = await row.innerText();
      const parts = text.split('\n').map(p => p.trim()).filter(Boolean);
      taskDetails.push({ index: i + 1, rText: parts.join(' | ') });
    }
    console.log("\n--- HTML Task List Details ---");
    taskDetails.forEach(t => console.log(`[Row ${t.index}] ${t.rText}`));
    console.log("------------------------------\n");

  } catch (err) {
    console.error("Error in poller:", err.stack || err.message || err);
  } finally {
    await context.close().catch(() => {});
  }
}

main();
