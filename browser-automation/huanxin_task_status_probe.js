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
const { isOnTargetAppRoute } = require('./huanxin_submit_task_run');

const BASE_URL = TRAIN_DEV_URL.split('#')[0];
const DEFAULT_ASI1_URL =
  `${BASE_URL}#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=ASI1`;

function parseArgs(argv) {
  const args = {
    url: process.env.HUANXIN_TASK_STATUS_URL || DEFAULT_ASI1_URL,
    taskName: '',
    taskId: '',
    openDetail: false,
    openPodLog: false,
    waitMs: 12000,
    dumpJson: 'browser-automation/huanxin-task-status-probe.json',
    screenshot: '',
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--url') {
      args.url = argv[++index];
      continue;
    }
    if (token === '--task-name') {
      args.taskName = argv[++index];
      continue;
    }
    if (token === '--task-id') {
      args.taskId = argv[++index];
      continue;
    }
    if (token === '--wait-ms') {
      args.waitMs = parseInt(argv[++index], 10);
      continue;
    }
    if (token === '--open-detail') {
      args.openDetail = true;
      continue;
    }
    if (token === '--open-pod-log') {
      args.openDetail = true;
      args.openPodLog = true;
      continue;
    }
    if (token === '--dump-json') {
      args.dumpJson = argv[++index];
      continue;
    }
    if (token === '--screenshot') {
      args.screenshot = argv[++index];
      continue;
    }
    throw new Error(`Unknown argument: ${token}`);
  }

  if (!args.taskName && !args.taskId) {
    throw new Error('Pass --task-name or --task-id');
  }
  return args;
}

function getAppBaseUrl(url) {
  return String(url || '').split('#')[0] || TRAIN_DEV_URL.split('#')[0];
}

function cleanText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function parseJsonMaybe(value) {
  try {
    return JSON.parse(String(value || ''));
  } catch {
    return null;
  }
}

function latestEventMatching(apiEvents, predicate) {
  for (let index = apiEvents.length - 1; index >= 0; index -= 1) {
    if (predicate(apiEvents[index])) {
      return apiEvents[index];
    }
  }
  return null;
}

function decodeTaskDetailEvent(event) {
  const payload = parseJsonMaybe(event && event.responsePreview);
  return payload && payload.data ? payload.data : null;
}

async function fetchTaskDetailById(page, taskId) {
  if (!taskId) {
    return null;
  }
  const response = await page.evaluate(async (id) => {
    const result = await fetch(`/kunlun/web/task/v1/detail?id=${encodeURIComponent(id)}`, {
      method: 'GET',
      credentials: 'include',
    });
    return { ok: result.ok, status: result.status, text: await result.text() };
  }, taskId).catch((error) => ({ ok: false, status: 0, text: JSON.stringify({ error: error.message }) }));
  const payload = parseJsonMaybe(response.text);
  return payload?.data || null;
}

async function fetchTaskList(page, keyword = '') {
  const response = await page.evaluate(async (taskKeyword) => {
    const payload = {
      pageNum: 1,
      pageSize: 20,
      projectId: ['21b4208dde424e96b159362ef49c9c96'],
      status: [],
      resGroupId: [],
      order: null,
      currentUser: 1,
      keyword: taskKeyword || '',
    };
    const result = await fetch('/kunlun/web/task/v1/list', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    });
    return {
      ok: result.ok,
      status: result.status,
      requestPreview: JSON.stringify(payload),
      text: await result.text(),
    };
  }, keyword).catch((error) => ({
    ok: false,
    status: 0,
    requestPreview: '',
    text: JSON.stringify({ error: error.message }),
  }));
  return response;
}

async function collectPodLogFromApi(page, apiEvents, matchedTask) {
  if (!matchedTask || !matchedTask.id) {
    return null;
  }
  const taskId = matchedTask.id;
  const detailResponse = await page.evaluate(async (id) => {
    const result = await fetch(`/kunlun/web/task/v1/detail?id=${encodeURIComponent(id)}`, {
      method: 'GET',
      credentials: 'include',
    });
    return { ok: result.ok, status: result.status, text: await result.text() };
  }, taskId).catch((error) => ({ ok: false, status: 0, text: JSON.stringify({ error: error.message }) }));
  const detailPayload = parseJsonMaybe(detailResponse.text);
  const detail = detailPayload?.data || null;
  const podListResponse = await page.evaluate(async (id) => {
    const result = await fetch('/kunlun/web/task/v1/pod/list', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ id, pageNum: 1, pageSize: 10 }),
    });
    return { ok: result.ok, status: result.status, text: await result.text() };
  }, taskId).catch((error) => ({ ok: false, status: 0, text: JSON.stringify({ error: error.message }) }));
  const podList = parseJsonMaybe(podListResponse.text);
  const podName =
    podList?.data?.list?.[0]?.podName ||
    detail?.podList?.[0]?.podName ||
    detail?.podInfoList?.[0]?.podName ||
    detail?.podName ||
    '';
  if (!podName) {
    return {
      method: 'api',
      ok: false,
      reason: 'pod_name_missing',
      taskDetail: detail,
    };
  }

  const now = new Date();
  const start = new Date(now.getTime() - 12 * 60 * 60 * 1000);
  const format = (date) => {
    const pad = (value) => String(value).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  };
  const requestPayload = {
    pageNum: 1,
    pageSize: 500,
    podName,
    startTime: matchedTask.startTime || matchedTask.submitTime || format(start),
    endTime: format(now),
    key: [],
    resGroupId: String(matchedTask.resGroupId || ''),
    order: '',
  };
  const response = await page.evaluate(async (payload) => {
    const result = await fetch('/kunlun/web/task/v1/pod/log', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    });
    return {
      ok: result.ok,
      status: result.status,
      text: await result.text(),
    };
  }, requestPayload);
  const parsed = parseJsonMaybe(response.text);
  const podLogs = Array.isArray(parsed?.data?.podLogs) ? parsed.data.podLogs : [];
  return {
    method: 'api',
    ok: Boolean(response.ok && parsed && parsed.code === 0),
    status: response.status,
    requestPayload,
    responsePreview: String(response.text || '').slice(0, 12000),
    podLogs,
    loadMore: Boolean(parsed?.data?.loadMore),
    bodyPreview: podLogs.join('\n').slice(-12000),
    taskDetail: detail,
  };
}

async function ensureAppSurface(page, args) {
  await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(3000);
  await dismissKnownBlockingModals(page);

  let bridge = null;
  if (classifyUrl(page.url()) === 'login_required') {
    bridge = await bridgePageViaSafariSso(page, {
      authUrl: page.url(),
      targetUrl: args.url,
      waitMs: args.waitMs,
      resultPath: `/tmp/huanxin-task-status-probe-${Date.now()}.json`,
    });
    if (!bridge.ok) {
      throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
    }
    await page.waitForTimeout(3000);
  }
  if (!isOnTargetAppRoute(page.url(), args.url)) {
    await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
    await page.waitForTimeout(3000);
    await dismissKnownBlockingModals(page);
  }
  return bridge;
}

async function dismissKnownBlockingModals(page) {
  for (let attempt = 0; attempt < 6; attempt += 1) {
    const hasNotice = await page.locator('body').getByText(/系统服务升级维护|知道了/).count().catch(() => 0);
    if (!hasNotice) {
      break;
    }
    const clicked = await page.evaluate(() => {
      const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
      const isVisible = (element) => {
        if (!(element instanceof HTMLElement)) {
          return false;
        }
        const style = window.getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
      };
      const candidates = Array.from(document.querySelectorAll('.ant-modal button, .ant-modal-content button, button, [role="button"]'));
      for (const element of candidates.reverse()) {
        if (!isVisible(element)) {
          continue;
        }
        const text = clean(element.innerText || element.textContent || '');
        if (!/知道了|确定|确\s*定/.test(text)) {
          continue;
        }
        element.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
        element.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
        element.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        return true;
      }
      return false;
    }).catch(() => false);
    if (!clicked) {
      const button = page.getByRole('button', { name: /知道了|确定|确\s*定/ }).last();
      await button.click({ timeout: 5000, force: true }).catch(async () => {
        await button.evaluate((element) => element.click()).catch(() => {});
      });
      await page.keyboard.press('Escape').catch(() => {});
    }
    await page.waitForTimeout(1000);
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const { profileDir, isolated, sourceDir, autoIsolated, baseProfileLocked } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;
  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(30000);

  const apiEvents = [];
  page.on('response', async (response) => {
    const request = response.request();
    const url = response.url();
    if (!url.includes('/kunlun/web/') && !url.includes('/kunlun/api/')) {
      return;
    }
    if (!/\/(task|develop|log|container|pod|resource)\//.test(url)) {
      return;
    }
    let responseText = '';
    try {
      responseText = await response.text();
    } catch (error) {
      responseText = JSON.stringify({ unavailable: error.message });
    }
    apiEvents.push({
      method: request.method(),
      url,
      status: response.status(),
      requestPreview: String(request.postData() || '').slice(0, 2000),
      responsePreview: responseText.slice(0, 12000),
    });
  });

  let bridge = null;
  try {
    bridge = await ensureAppSurface(page, args);
    const taskListUrl = `${getAppBaseUrl(args.url)}#/train-task`;
    await page.goto(taskListUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(5000);

    let listEvents = apiEvents.filter((event) => event.url.includes('/kunlun/web/task/v1/list'));
    let latestEvent = listEvents[listEvents.length - 1] || null;
    if (!latestEvent) {
      const directList = await fetchTaskList(page, args.taskName || '');
      latestEvent = {
        method: 'POST',
        url: `${getAppBaseUrl(args.url)}/kunlun/web/task/v1/list`,
        status: directList.status,
        requestPreview: directList.requestPreview,
        responsePreview: String(directList.text || '').slice(0, 12000),
        source: 'direct_fetch',
      };
      apiEvents.push(latestEvent);
      listEvents = [latestEvent];
    }
    let matchedTask = null;
    if (latestEvent) {
      try {
        const payload = JSON.parse(latestEvent.responsePreview);
        const tasks = payload?.data?.list || [];
        matchedTask = tasks.find((task) => {
          if (args.taskId && task.id === args.taskId) {
            return true;
          }
          return Boolean(args.taskName && task.name === args.taskName);
        }) || null;
      } catch {}
    }
    if (!matchedTask && args.taskId) {
      const detail = await fetchTaskDetailById(page, args.taskId);
      if (detail) {
        matchedTask = {
          id: detail.id || args.taskId,
          name: detail.name || '',
          status: detail.status,
          resGroupId: detail.resGroupId,
          resGroupName: detail.resGroupName,
          submitTime: detail.submitTime,
          startTime: detail.startTime,
          endTime: detail.endTime,
          useTime: detail.useTime,
          resourceInfo: detail.resourceInfo,
          podList: detail.podList,
          podInfoList: detail.podInfoList,
          podName: detail.podName,
          detail,
        };
      }
    }

    let detailSummary = null;
    if (args.openDetail) {
      const selectorText = args.taskName || matchedTask?.name || '';
      let apiPodLogSummary = null;
      if (args.openPodLog && matchedTask?.id) {
        apiPodLogSummary = await collectPodLogFromApi(page, apiEvents, matchedTask);
      }
      const preClickEventCount = apiEvents.length;
      let taskLinkVisible = false;
      if (selectorText) {
        const taskLink = page.locator('span.ellipsis-text.hover.isModal', { hasText: selectorText }).first();
        taskLinkVisible = await taskLink.waitFor({ state: 'visible', timeout: 15000 }).then(() => true).catch(() => false);
        if (taskLinkVisible) {
          await taskLink.click({ timeout: 15000 });
          await page.waitForTimeout(8000);
        }
      }
      let podLogSummary = null;
      if (args.openPodLog) {
        const preLogEventCount = apiEvents.length;
        podLogSummary = apiPodLogSummary;
        if (!podLogSummary || !podLogSummary.ok) {
          podLogSummary = await collectPodLogFromApi(page, apiEvents, matchedTask);
        }
        const taskStillPending = matchedTask && [1, 2].includes(matchedTask.status);
        if ((!podLogSummary || !podLogSummary.ok) && !taskStillPending && taskLinkVisible) {
          const rowLocator = page.locator('.ant-table-row').filter({ hasText: args.taskId || selectorText }).first();
          const rowVisible = await rowLocator.isVisible().catch(() => false);
          const scope = rowVisible ? rowLocator : page;
          const logAction = scope.getByText('日志', { exact: true }).first();
          await logAction.waitFor({ state: 'visible', timeout: 30000 });
          await logAction.click({ timeout: 15000 });
          await page.waitForTimeout(8000);
          podLogSummary = {
            ...(podLogSummary || {}),
            method: 'ui',
            rowMatched: rowVisible,
            postLogApiEvents: apiEvents.slice(preLogEventCount),
            url: page.url(),
            bodyPreview: cleanText(await page.locator('body').innerText().catch(() => '')).slice(0, 12000),
          };
        }
      }
      detailSummary = {
        taskLinkVisible,
        postClickApiEvents: apiEvents.slice(preClickEventCount),
        podLogSummary,
        bodyPreview: cleanText(await page.locator('body').innerText().catch(() => '')).slice(0, 12000),
      };
    }

    const result = {
      ok: true,
      taskName: args.taskName,
      taskId: args.taskId,
      matchedTask,
      apiEvents,
      listEvents,
      detailSummary,
      browserMode: launch.browserMode,
      launchFallbackUsed: launch.fallbackUsed,
      bridge,
      usedProfile: { profileDir, isolated, sourceDir, autoIsolated, baseProfileLocked },
      url: page.url(),
      bodyPreview: String(await page.locator('body').innerText().catch(() => '')).replace(/\s+/g, ' ').trim().slice(0, 7000),
      timestamp: new Date().toISOString(),
    };

    if (args.screenshot) {
      fs.mkdirSync(path.dirname(path.resolve(args.screenshot)), { recursive: true });
      await page.screenshot({ path: path.resolve(args.screenshot), fullPage: true }).catch(() => {});
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

if (require.main === module) {
  main().catch((error) => {
    console.error(error.stack || error.message || String(error));
    process.exit(1);
  });
}
