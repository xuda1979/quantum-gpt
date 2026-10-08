const http = require('http');
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { bridgePageViaSafariSso } = require('./huanxin_repair_profile_via_safari_sso');
const { assertAutomationAllowed } = require('./huanxin_manual_lock');

const ENV_PORTS = { AI: 19006, ai1: 19001, ai2: 19002, ai3: 19003, ASI1: 20646, ASI2: 19004, ASI3: 20653 };

function redactAuthUrl(value) {
  try {
    const url = new URL(String(value));
    for (const key of ['code', 'state', 'session_state']) {
      if (url.searchParams.has(key)) url.searchParams.set(key, '[redacted]');
    }
    if (url.hash.includes('?')) {
      const [hashPath, hashQuery] = url.hash.split('?');
      const params = new URLSearchParams(hashQuery);
      for (const key of ['code', 'state', 'session_state']) {
        if (params.has(key)) params.set(key, '[redacted]');
      }
      url.hash = `${hashPath}?${params.toString()}`;
    }
    return url.toString();
  } catch {
    return String(value || '').replace(/([?&](?:code|state|session_state)=)[^&#]+/g, '$1[redacted]');
  }
}

function usage() {
  console.error('Usage: node huanxin_shell_exec.js <envName> --command <shell command>');
  process.exit(1);
}

/**
 * Try to send a command to an already-running daemon.
 * Returns the JSON result, or null if the daemon is not available.
 */
function tryDaemon(envName, command, waitMs) {
  const portFilePath = `/tmp/huanxin-daemon-${envName}.port`;
  let port;
  try {
    port = parseInt(fs.readFileSync(portFilePath, 'utf8').trim(), 10);
  } catch {
    return Promise.resolve(null);
  }

  return new Promise((resolve) => {
    const body = JSON.stringify({ command, waitMs });
    const requestTimeoutMs = Math.max(waitMs + 10000, 30000);
    const req = http.request(
      {
        hostname: '127.0.0.1',
        port,
        path: '/exec',
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
        timeout: requestTimeoutMs,
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch {
            resolve(null);
          }
        });
      }
    );
    req.on('error', () => resolve(null));
    req.on('timeout', () => {
      req.destroy();
      resolve(null);
    });
    req.write(body);
    req.end();
  });
}

async function tryDaemonFileTransport(envName, command, waitMs) {
  const dir = `/tmp/huanxin-daemon-${envName}.ipc`;
  try {
    if (!fs.existsSync(dir)) {
      return null;
    }
  } catch {
    return null;
  }

  const requestId = `${Date.now()}-${process.pid}-${Math.random().toString(36).slice(2, 8)}`;
  const requestPath = path.join(dir, `${requestId}.request.json`);
  const responsePath = path.join(dir, `${requestId}.response.json`);
  fs.writeFileSync(requestPath, JSON.stringify({ command, waitMs }, null, 2));

  // The daemon's terminal injection path retries up to 3 times, so a single
  // request can legitimately outlive `waitMs` by a wide margin.
  const waitMultiplierRaw = parseInt(process.env.HUANXIN_DAEMON_FILE_WAIT_MULTIPLIER || '3', 10);
  const waitMultiplier = Number.isFinite(waitMultiplierRaw) && waitMultiplierRaw > 0 ? waitMultiplierRaw : 3;
  const graceMsRaw = parseInt(process.env.HUANXIN_DAEMON_FILE_WAIT_GRACE_MS || '15000', 10);
  const graceMs = Number.isFinite(graceMsRaw) && graceMsRaw >= 0 ? graceMsRaw : 15000;
  const deadline = Date.now() + Math.max(waitMs * waitMultiplier + graceMs, 45000);
  while (Date.now() < deadline) {
    try {
      if (fs.existsSync(responsePath)) {
        const parsed = JSON.parse(fs.readFileSync(responsePath, 'utf8'));
        try {
          fs.unlinkSync(requestPath);
        } catch {}
        try {
          fs.unlinkSync(responsePath);
        } catch {}
        return parsed;
      }
    } catch {
      return null;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  const processingPath = requestPath.replace(/\.request\.json$/, '.processing.json');
  return {
    ok: false,
    error: fs.existsSync(processingPath) ? 'daemon_file_timeout_processing' : 'daemon_file_timeout_no_response',
    envName,
    requestId,
    requestPath,
    responsePath,
    processingPath,
  };
}

function allowStandaloneFallback() {
  return process.env.HUANXIN_ALLOW_STANDALONE_FALLBACK === '1';
}

function parseArgs(argv) {
  const envName = argv[0];
  if (!envName) usage();

  let command = null;
  let waitMs = 10000;
  let requireDaemon = false;
  let skipDaemon = false;
  for (let index = 1; index < argv.length; index += 1) {
    if (argv[index] === '--command') {
      command = argv[index + 1] || null;
      index += 1;
      continue;
    }
    if (argv[index] === '--wait-ms') {
      waitMs = parseInt(argv[index + 1] || '10000', 10);
      index += 1;
      continue;
    }
    if (argv[index] === '--require-daemon') {
      requireDaemon = true;
      continue;
    }
    if (argv[index] === '--skip-daemon') {
      skipDaemon = true;
      continue;
    }
    usage();
  }

  if (!command) usage();
  return { envName, command, waitMs, requireDaemon, skipDaemon };
}

async function detectPageState(page) {
  const url = page.url();
  const bodyText = ((await page.locator('body').innerText().catch(() => '')) || '').replace(/\s+/g, ' ').trim();
  const lowerUrl = url.toLowerCase();
  const lowerText = bodyText.toLowerCase();

  if (
    lowerUrl.includes('/auth/realms/') ||
    lowerUrl.includes('openid-connect/auth') ||
    lowerUrl.includes('login') ||
    lowerText.includes('短信登录') ||
    lowerText.includes('密码登录') ||
    lowerText.includes('获取验证码')
  ) {
    return { state: 'login_required', url, bodyPreview: bodyText.slice(0, 300) };
  }

  const rowTexts = await page.locator('tr').evaluateAll((rows) =>
    rows
      .map((row) => (row.innerText || row.textContent || '').replace(/\s+/g, ' ').trim())
      .filter(Boolean)
      .slice(0, 20)
  ).catch(() => []);

  return {
    state: 'ready',
    url,
    bodyPreview: bodyText.slice(0, 300),
    rowPreview: rowTexts,
  };
}

const DEFAULT_TRAIN_DEV_URL =
  'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=AI';
const TRAIN_DEV_URL = process.env.HUANXIN_TRAIN_DEV_URL || DEFAULT_TRAIN_DEV_URL;
const SHELL_DEBUG_KEY = Symbol('huanxinShellDebug');

function redactAuthUrl(value) {
  if (!value) {
    return value;
  }
  const text = String(value);
  try {
    const parsed = new URL(text);
    const sensitiveKeys = new Set(['code', 'session_state', 'state', 'nonce', 'token', 'access_token', 'id_token']);
    for (const key of Array.from(parsed.searchParams.keys())) {
      if (sensitiveKeys.has(key.toLowerCase())) {
        parsed.searchParams.set(key, '[REDACTED]');
      }
    }
    if (parsed.hash) {
      const [route, rawQuery = ''] = parsed.hash.slice(1).split('?');
      const params = new URLSearchParams(rawQuery);
      for (const key of Array.from(params.keys())) {
        if (sensitiveKeys.has(key.toLowerCase())) {
          params.set(key, '[REDACTED]');
        }
      }
      parsed.hash = params.toString() ? `${route}?${params.toString()}` : route;
    }
    if (parsed.pathname.toLowerCase().includes('/auth/realms/') && parsed.pathname.includes('openid-connect/auth')) {
      return `${parsed.origin}${parsed.pathname}?[REDACTED_AUTH_QUERY]`;
    }
    return parsed.toString();
  } catch {
    return text
      .replace(/([?&#](?:code|session_state|state|nonce|token|access_token|id_token)=)[^&#]+/gi, '$1[REDACTED]')
      .replace(/(openid-connect\/auth\?)[^#\s]+/gi, '$1[REDACTED_AUTH_QUERY]');
  }
}

function getApiAuthToken() {
  return process.env.HUANXIN_API_KEY || process.env.HUANXIN_APPCODE || '';
}

async function tryApiAuthSmoke(page) {
  const token = getApiAuthToken();
  if (!token) {
    return null;
  }
  return page.evaluate(async ({ token: bearer }) => {
    const response = await fetch('/kunlun/web/project/v1/detail', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${bearer}`,
      },
      credentials: 'include',
    }).catch((error) => ({ ok: false, status: 0, statusText: error.message }));
    return {
      ok: Boolean(response && response.ok),
      status: response && response.status,
      statusText: response && response.statusText,
    };
  }, { token });
}

function getSafariSsoBridgeWaitMs() {
  const raw = process.env.HUANXIN_SAFARI_SSO_BRIDGE_WAIT_MS || '15000';
  const parsed = parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 10000;
}

function parseJsonObjectMaybe(text) {
  if (typeof text !== 'string' || !text.trim()) {
    return null;
  }
  try {
    const parsed = JSON.parse(text);
    return parsed && typeof parsed === 'object' ? parsed : null;
  } catch {
    return null;
  }
}

function firstNullWebsocketUrl(candidates) {
  for (const candidate of candidates) {
    const match = String(candidate || '').match(/wss?:\/\/[^"'\s]*\/null/i);
    if (match) {
      return match[0];
    }
  }
  return null;
}

function buildShellEndpointFailure(envName, diagnostics) {
  const shellVisitHit = diagnostics.shellVisitHit || null;
  const request = parseJsonObjectMaybe(shellVisitHit ? shellVisitHit.postData : '') || null;
  let response = parseJsonObjectMaybe(shellVisitHit ? shellVisitHit.body : '');
  if (!response && shellVisitHit && shellVisitHit.status !== undefined) {
    response = { status: shellVisitHit.status };
  } else if (response && shellVisitHit && shellVisitHit.status !== undefined && !('status' in response)) {
    response.status = shellVisitHit.status;
  }
  const websocketNullUrl = firstNullWebsocketUrl([
    diagnostics.bodyPreview,
    diagnostics.consoleHit && diagnostics.consoleHit.text,
    diagnostics.requestFailedHit && diagnostics.requestFailedHit.url,
    diagnostics.websocketHit && diagnostics.websocketHit.url,
  ]);
  const websocket404Seen =
    /Unexpected response code:\s*404/i.test(String((diagnostics.consoleHit && diagnostics.consoleHit.text) || '')) ||
    /404/i.test(String((diagnostics.requestFailedHit && diagnostics.requestFailedHit.failureText) || ''));
  const code = response && response.code !== undefined ? response.code : 'unknown';
  const podName = request && request.podName ? ` pod=${request.podName}` : '';
  const shellType = request && request.type ? ` type=${request.type}` : '';
  return {
    kind: 'shell_endpoint_unavailable',
    envName,
    request,
    response,
    websocketNullUrl,
    websocket404Seen,
    consoleHit: diagnostics.consoleHit || null,
    requestFailedHit: diagnostics.requestFailedHit || null,
    summary:
      `getShellVisitUrl code=${code} for env=${envName}${podName}${shellType}; ` +
      `frontend fell through to ${websocketNullUrl || '/kunlun/null'}`,
  };
}

function ensureShellDiagnostics(page) {
  if (page[SHELL_DEBUG_KEY]) {
    return page[SHELL_DEBUG_KEY];
  }
  const state = {
    consoleEvents: [],
    shellVisitResponses: [],
    requestFailed: [],
    websockets: [],
  };
  const pushBounded = (items, value, limit = 12) => {
    items.push(value);
    if (items.length > limit) {
      items.splice(0, items.length - limit);
    }
  };
  page.on('console', (message) => {
    try {
      pushBounded(state.consoleEvents, {
        type: message.type(),
        text: message.text(),
      });
    } catch {}
  });
  page.on('response', async (response) => {
    try {
      const url = response.url();
      if (!url.includes('/web/develop/v1/getShellVisitUrl')) {
        return;
      }
      let body = '';
      try {
        body = await response.text();
      } catch {}
      pushBounded(state.shellVisitResponses, {
        status: response.status(),
        url: redactAuthUrl(url),
        method: response.request().method(),
        postData: response.request().postData() || null,
        body: body.slice(0, 2000),
      });
    } catch {}
  });
  page.on('requestfailed', (request) => {
    try {
      pushBounded(state.requestFailed, {
        url: redactAuthUrl(request.url()),
        method: request.method(),
        failureText: request.failure() ? request.failure().errorText : null,
      });
    } catch {}
  });
  page.on('websocket', (websocket) => {
    try {
      pushBounded(state.websockets, {
        url: redactAuthUrl(websocket.url()),
      });
    } catch {}
  });
  page[SHELL_DEBUG_KEY] = state;
  return state;
}

async function openShell(page, envName) {
  ensureShellDiagnostics(page);
  const trackShellDiagnostics = (candidate) => {
    if (candidate) {
      ensureShellDiagnostics(candidate);
    }
    return candidate;
  };
  const encodedEnvName = encodeURIComponent(envName);
  let environmentPage = null;
  const maxShellOpenCycles = parseInt(String(process.env.HUANXIN_SHELL_OPEN_CYCLES || '3'), 10);
  const isTargetEnvPage = (candidate) => {
    const candidateUrl = candidate.url();
    if (
      candidateUrl.includes('/train-dev/environment/')
      && (candidateUrl.includes(`name=${encodedEnvName}`) || candidateUrl.includes(`name=${envName}`))
    ) {
      return true;
    }

    return false;
  };

  const findExistingEnvPage = () =>
    page
      .context()
      .pages()
      .find((candidate) => isTargetEnvPage(candidate));
  const closeEnvPages = async () => {
    const envPages = page
      .context()
      .pages()
      .filter(
        (candidate) =>
          candidate !== page &&
          !candidate.isClosed() &&
          isTargetEnvPage(candidate)
      );
    for (const candidate of envPages) {
      await candidate.close({ runBeforeUnload: false }).catch(() => {});
    }
    environmentPage = null;
  };

  let lastError = null;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const existingPage = findExistingEnvPage();
      if (existingPage) {
        trackShellDiagnostics(existingPage);
        await existingPage.bringToFront().catch(() => {});
        await existingPage.waitForTimeout(1000);
        environmentPage = existingPage;
        break;
      }

      // The AI train-dev SPA can keep background requests open indefinitely, so
      // `networkidle` may never settle even when the page is already usable.
      // Match the Safari-SSO repair flow and advance on DOM readiness instead.
      await page.goto(TRAIN_DEV_URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
      await page.waitForTimeout(3000);
      let pageState = await detectPageState(page);
      if (pageState.state === 'login_required') {
        const apiAuthSmoke = await tryApiAuthSmoke(page).catch((error) => ({
          ok: false,
          status: 0,
          statusText: error.message,
        }));
        if (apiAuthSmoke && apiAuthSmoke.ok) {
          await page.goto(TRAIN_DEV_URL, { waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
          await page.waitForTimeout(3000);
          pageState = await detectPageState(page);
          if (pageState.state !== 'login_required') {
            continue;
          }
        }
        if (process.env.HUANXIN_ALLOW_SAFARI_SSO_BRIDGE !== '1') {
          throw new Error(
            `Huanxin auth expired before opening ${envName}; Safari SSO bridge is disabled to avoid foreground browser interruption. API-key smoke=${JSON.stringify(apiAuthSmoke)}.`
          );
        }
        const repair = await bridgePageViaSafariSso(page, {
          authUrl: pageState.url,
          targetUrl: TRAIN_DEV_URL,
          waitMs: getSafariSsoBridgeWaitMs(),
          resultPath: `/tmp/huanxin-${envName}-daemon-safari-sso-bridge.json`,
        });
        if (!repair.ok) {
          throw new Error(
            `Huanxin auth expired before opening ${envName}; Safari SSO bridge failed at ${redactAuthUrl(pageState.url)}. Final state=${repair.finalUrlState}. Body preview: ${repair.bodyPreview}`
          );
        }
        await page.waitForTimeout(3000);
        pageState = await detectPageState(page);
        if (pageState.state === 'login_required') {
          throw new Error(
            `Huanxin auth repair did not stick for ${envName}; login_required still visible at ${redactAuthUrl(pageState.url)}. Body preview: ${pageState.bodyPreview}`
          );
        }
      }

      const directEnvPage = findExistingEnvPage();
      if (directEnvPage) {
        trackShellDiagnostics(directEnvPage);
        await directEnvPage.bringToFront().catch(() => {});
        await directEnvPage.waitForTimeout(1000);
        environmentPage = directEnvPage;
        break;
      }

      const currentUrl = page.url();
      if (
        currentUrl.includes('/train-dev/environment/') && currentUrl.includes(`name=${encodedEnvName}`)
      ) {
        environmentPage = trackShellDiagnostics(page);
        break;
      }

      // TRAIN_DEV_URL is hardcoded to a single, specific environment's detail page
      // (historically the "AI" env). It's only useful here as a login/auth-state
      // smoke check. When the requested envName differs from whatever env that
      // hardcoded URL happens to land on, we must explicitly navigate to the
      // environment *list* page so the row-based lookup below has a list of rows to
      // search, instead of silently searching for a `tr` on a single env's detail
      // page (which has none, and previously led to a misrouting fallback bug).
      if (!currentUrl.includes(`name=${encodedEnvName}`)) {
        const listUrl = `${currentUrl.split('#')[0]}#/train-dev`;
        await page.goto(listUrl, { waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
        await page.waitForTimeout(3000);
      }
      // IMPORTANT: this is only a valid shortcut if the currently-loaded page's URL
      // actually matches the requested envName. DEFAULT_TRAIN_DEV_URL is hardcoded to
      // the "AI" environment, and a restored/copied browser profile can carry over an
      // already-open, already-ready "AI" terminal session. Without this guard, this
      // fallback would silently misroute every other env's exec calls onto the "AI"
      // environment's pod whenever "AI" happened to already have a visible terminal
      // surface, which is a correctness-critical routing bug (bit us in production for
      // ASI2/ASI3 after a daemon restart reused a profile copy with an existing "AI" tab).
      const directSurfaceOnTargetEnv =
        page.url().includes('/train-dev/environment/') && page.url().includes(`name=${encodedEnvName}`);
      const directSurfaceDetected =
        directSurfaceOnTargetEnv &&
        (await page
          .locator('.dev-terminal-tabs, button:has-text("Shell终端"), .jupyter-terminal-container')
          .first()
          .isVisible()
          .catch(() => false));
      if (directSurfaceDetected) {
        environmentPage = trackShellDiagnostics(page);
        break;
      }

      const row = page.locator('tr', { hasText: envName }).first();
      const rowVisible = await row.waitFor({ state: 'visible', timeout: 60000 }).then(() => true).catch(() => false);
      if (!rowVisible) {
        const bodyText = ((await page.locator('body').innerText().catch(() => '')) || '').replace(/\s+/g, ' ').trim();
        // Same routing-safety guard as directSurfaceDetected above: only accept this
        // "already looks like a ready env detail page" fallback if the current page's
        // URL actually belongs to the requested envName. Without this check, landing on
        // *any* environment's detail page (e.g. the hardcoded DEFAULT_TRAIN_DEV_URL's
        // "AI" env, or a stale/leftover tab from a copied browser profile) that happens
        // to show generic Shell-terminal/开发环境详情 markers would be silently accepted
        // as if it were the requested env, misrouting exec calls to the wrong pod.
        const onTargetEnvPage =
          page.url().includes('/train-dev/environment/') && page.url().includes(`name=${encodedEnvName}`);
        if (onTargetEnvPage && /Shell终端|提交任务|开发环境详情|打开环境/i.test(bodyText)) {
          environmentPage = trackShellDiagnostics(page);
          break;
        }
        throw new Error(`Environment row for ${envName} was not visible. body=${bodyText.slice(0, 500)}`);
      }
      const openButton = row.getByRole('button', { name: '打开' }).first();
      const startButton = row.getByRole('button', { name: '运行' }).first();

      let clicked = false;
      let startTriggered = false;
      for (let poll = 0; poll < 20; poll += 1) {
        const existingAfterLoad = findExistingEnvPage();
        if (existingAfterLoad) {
          trackShellDiagnostics(existingAfterLoad);
          await existingAfterLoad.bringToFront().catch(() => {});
          await existingAfterLoad.waitForTimeout(1000);
          return existingAfterLoad;
        }

        const enabled = await openButton.isEnabled().catch(() => false);
        const rowText = ((await row.textContent().catch(() => '')) || '').replace(/\s+/g, ' ').trim();
        const startVisible = await startButton.isVisible().catch(() => false);
        const startEnabled = await startButton.isEnabled().catch(() => false);
        const spinning = await page.locator('.ant-spin-spinning, .ant-spin-blur').count().catch(() => 0);
        if (!startTriggered && (rowText.includes('已停止') || rowText.includes('已锁定') || rowText.includes('失败')) && startVisible && startEnabled && spinning === 0) {
          await startButton.click({ timeout: 15000 });
          startTriggered = true;
          await page.waitForTimeout(8000);
          continue;
        }
        if (rowText.includes('启动中')) {
          await page.waitForTimeout(10000);
          continue;
        }
        if (enabled && spinning === 0) {
          await openButton.click({ timeout: 15000 });
          clicked = true;
          break;
        }
        await page.waitForTimeout(2000);
      }

      if (!clicked) {
        const rowText = ((await row.textContent().catch(() => '')) || '').replace(/\s+/g, ' ').trim();
        const enabled = await openButton.isEnabled().catch(() => false);
        const spinning = await page.locator('.ant-spin-spinning, .ant-spin-blur').count().catch(() => 0);
        throw new Error(
          `Open button for ${envName} never became clickable. enabled=${enabled} spinning=${spinning} row=${rowText}`
        );
      }
      await page.waitForTimeout(5000);
      lastError = null;
      break;
    } catch (error) {
      lastError = error;
      const message = String(error && (error.stack || error.message || error));
      if (message.includes('login_required')) {
        throw error;
      }
      if (attempt === 3) {
        throw error;
      }
      await page.reload({ waitUntil: 'domcontentloaded', timeout: 180000 }).catch(() => {});
      await page.waitForTimeout(4000);
    }
  }

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const openEnvironmentSurface = async () => {
    const currentExisting = findExistingEnvPage();
    if (currentExisting) {
      trackShellDiagnostics(currentExisting);
      await currentExisting.bringToFront().catch(() => {});
      await currentExisting.waitForTimeout(1000).catch(() => {});
      environmentPage = currentExisting;
      return currentExisting;
    }
    await page.goto(TRAIN_DEV_URL, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);
    const directEnvPage = findExistingEnvPage();
    if (directEnvPage) {
      trackShellDiagnostics(directEnvPage);
      await directEnvPage.bringToFront().catch(() => {});
      await directEnvPage.waitForTimeout(1000).catch(() => {});
      environmentPage = directEnvPage;
      return directEnvPage;
    }
    const row = page.locator('tr', { hasText: envName }).first();
    await row.waitFor({ state: 'visible', timeout: 60000 });
    const openButton = row.getByRole('button', { name: '打开' }).first();
    const startButton = row.getByRole('button', { name: '运行' }).first();
    for (let poll = 0; poll < 20; poll += 1) {
      const existingAfterLoad = findExistingEnvPage();
      if (existingAfterLoad) {
        trackShellDiagnostics(existingAfterLoad);
        await existingAfterLoad.bringToFront().catch(() => {});
        await existingAfterLoad.waitForTimeout(1000).catch(() => {});
        environmentPage = existingAfterLoad;
        return existingAfterLoad;
      }

      const rowText = ((await row.textContent().catch(() => '')) || '').replace(/\s+/g, ' ').trim();
      const startVisible = await startButton.isVisible().catch(() => false);
      const startEnabled = await startButton.isEnabled().catch(() => false);
      const openEnabled = await openButton.isEnabled().catch(() => false);
      const spinning = await page.locator('.ant-spin-spinning, .ant-spin-blur').count().catch(() => 0);

      if ((rowText.includes('已停止') || rowText.includes('已锁定') || rowText.includes('失败')) && startVisible && startEnabled && spinning === 0) {
        await startButton.click({ timeout: 15000 });
        await page.waitForTimeout(8000);
        continue;
      }
      if (rowText.includes('启动中')) {
        await page.waitForTimeout(10000);
        continue;
      }

      if (openEnabled && spinning === 0) {
        await openButton.click({ timeout: 15000 });
        await page.waitForTimeout(5000);
        break;
      }

      await page.waitForTimeout(2000);
    }

    const pages = page.context().pages();
    const opened = findExistingEnvPage() || pages[pages.length - 1];
    if (opened) {
      trackShellDiagnostics(opened);
      await opened.bringToFront().catch(() => {});
      await opened.waitForTimeout(1000).catch(() => {});
      environmentPage = opened;
    }
    return opened;
  };
  const pages = page.context().pages();
  let activePage = trackShellDiagnostics(environmentPage || pages[pages.length - 1]);
  const refreshActivePage = async () => {
    if (activePage && !activePage.isClosed()) {
      trackShellDiagnostics(activePage);
      return activePage;
    }
    const replacement =
      findExistingEnvPage() ||
      page
        .context()
        .pages()
        .find((candidate) => !candidate.isClosed() && candidate.url().includes('/train-dev/environment/'));
    if (replacement) {
      activePage = trackShellDiagnostics(replacement);
      await activePage.bringToFront().catch(() => {});
      await activePage.waitForTimeout(500).catch(() => {});
    }
    return activePage;
  };

  const shellTrigger = () => activePage.getByText('Shell终端', { exact: true }).first();
  const waitForSpinnerToClear = async (timeoutMs = 30000) => {
    const spinner = activePage.locator('.ant-spin-spinning, .ant-spin-blur, [aria-busy="true"]').first();
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      const visible = await spinner.isVisible().catch(() => false);
      if (!visible) return;
      await activePage.waitForTimeout(500);
    }
  };

  const shellTabSelected = async () => {
    const selected = await shellTrigger().getAttribute('aria-selected').catch(() => null);
    return selected === 'true';
  };

  const terminalSurfaceSnapshot = async () => {
    return activePage.evaluate(() => {
      const isVisible = (element) => {
        if (!element) return false;
        const rect = element.getBoundingClientRect();
        const style = window.getComputedStyle(element);
        return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
      };
      const terminal = document.querySelector('.terminal.xterm, .xterm, [class*="xterm"]');
      const helper = document.querySelector('.xterm-helper-textarea, textarea[class*="xterm"]');
      const rows = document.querySelector('.xterm-rows, [class*="xterm-rows"]');
      const cursor = document.querySelector('.xterm-cursor, [class*="xterm-cursor"]');
      const bodyText = ((document.body?.innerText) || (document.body?.textContent) || '')
        .replace(/\u00a0/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
      const terminalText = ((terminal?.innerText) || (terminal?.textContent) || '')
        .replace(/\u00a0/g, ' ')
        .trim();
      const statusTexts = Array.from(document.querySelectorAll('button, span, div'))
        .filter(isVisible)
        .map((element) => ((element.innerText || element.textContent || '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim()))
        .filter(Boolean)
        .filter((text) => /连接中|已断开|断开|刷新|重连|reconnect|refresh|connecting|disconnected/i.test(text))
        .slice(0, 20);
      const statusPreview = statusTexts.join(' | ');
      return {
        hasTerminal: Boolean(terminal),
        hasHelper: Boolean(helper),
        hasRows: Boolean(rows),
        hasCursor: Boolean(cursor),
        disconnected: /已断开|断开|disconnected/i.test(bodyText),
        connecting: /连接中|connecting/i.test(statusPreview || bodyText),
        statusPreview,
        terminalPreview: terminalText.slice(-200),
      };
    }).catch(() => ({
      hasTerminal: false,
      hasHelper: false,
      hasRows: false,
      hasCursor: false,
      disconnected: false,
      connecting: false,
      statusPreview: '',
      terminalPreview: '',
    }));
  };
  const detectShellVisitUrlFailure = async () => {
    const pageSignals = await activePage.evaluate(() => {
      const bodyText = ((document.body?.innerText) || (document.body?.textContent) || '')
        .replace(/\u00a0/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
      const hasNullSocket = /wss?:\/\/[^ ]+\/null/i.test(bodyText);
      const terminalFailure = /获取shell终端信息失败/i.test(bodyText);
      return {
        bodyPreview: bodyText.slice(0, 1200),
        hasNullSocket,
        terminalFailure,
      };
    }).catch(() => ({
      bodyPreview: '',
      hasNullSocket: false,
      terminalFailure: false,
    }));
    const diagnostics = activePage[SHELL_DEBUG_KEY] || page[SHELL_DEBUG_KEY] || {
      consoleEvents: [],
      shellVisitResponses: [],
      requestFailed: [],
      websockets: [],
    };
    const consoleHit = diagnostics.consoleEvents.find((item) =>
      /wss:\/\/aihuanxin\.cn\/kunlun\/null|getshellvisiturl|获取shell终端信息失败/i.test(String(item.text || ''))
    );
    const shellVisitHit = diagnostics.shellVisitResponses.find((item) =>
      /"code"\s*:\s*170022|获取shell终端信息失败/i.test(String(item.body || ''))
    );
    const requestFailedHit = diagnostics.requestFailed.find((item) =>
      /getshellvisiturl|\/kunlun\/null/i.test(`${String(item.url || '')} ${String(item.failureText || '')}`)
    );
    const websocketHit = diagnostics.websockets.find((item) =>
      /wss?:\/\/[^"'\s]*\/null/i.test(String(item.url || ''))
    );
    return {
      ...pageSignals,
      consoleHit: consoleHit || null,
      shellVisitHit: shellVisitHit || null,
      requestFailedHit: requestFailedHit || null,
      websocketHit: websocketHit || null,
    };
  };
  const terminalHasPrompt = async () => {
    const snapshot = await readTerminalText(activePage).catch(() => ({ text: '' }));
    const lines = String(snapshot.text || '')
      .split('\n')
      .map((line) => line.trimEnd())
      .filter(Boolean);
    const lastLine = lines[lines.length - 1] || '';
    return /[#$>]\s*$/.test(lastLine);
  };
  const nudgeTerminalSurface = async () => {
    try {
      const terminalInput = await focusTerminal(activePage);
      await terminalInput.evaluate((element) => {
        element.value = '';
      }).catch(() => {});
      await activePage.keyboard.press('Enter').catch(() => {});
      await activePage.waitForTimeout(400);
      await activePage.keyboard.insertText('\u0003').catch(() => {});
      await activePage.waitForTimeout(800);
      return true;
    } catch {
      return false;
    }
  };
  const clickShellReconnect = async () => {
    return activePage.evaluate(() => {
      const isVisible = (element) => {
        if (!element) return false;
        const rect = element.getBoundingClientRect();
        const style = window.getComputedStyle(element);
        return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
      };
      const isUsableButton = (element) => {
        const button = element?.closest?.('button') || element;
        return button && button.tagName === 'BUTTON' && !button.disabled && isVisible(button);
      };
      const clickButton = (button) => {
        button.scrollIntoView({ block: 'center', inline: 'center' });
        button.click();
        return true;
      };

      // Huanxin sometimes leaves the xterm black with a small shell-status
      // chip such as "已断开" or "连接中" and a refresh button immediately to
      // its right. Prefer that local toolbar button over any page-level
      // refresh icon elsewhere in the SPA.
      const shellStatusElements = Array.from(document.querySelectorAll('span,div,p,label'))
        .filter((element) => /已断开|断开|disconnected|连接中|connecting/i.test(element.innerText || element.textContent || ''))
        .filter(isVisible);
      const nearbyCandidates = [];
      for (const statusElement of shellStatusElements) {
        const statusRect = statusElement.getBoundingClientRect();
        for (const button of Array.from(document.querySelectorAll('button')).filter(isUsableButton)) {
          const rect = button.getBoundingClientRect();
          const centerY = rect.top + rect.height / 2;
          const statusCenterY = statusRect.top + statusRect.height / 2;
          const isSameToolbar = Math.abs(centerY - statusCenterY) <= 36;
          const isNearbyRight = rect.left >= statusRect.right - 6 && rect.left <= statusRect.right + 260;
          if (isSameToolbar && isNearbyRight) {
            nearbyCandidates.push({
              button,
              distance: Math.abs(rect.left - statusRect.right) + Math.abs(centerY - statusCenterY),
            });
          }
        }
      }
      nearbyCandidates.sort((a, b) => a.distance - b.distance);
      if (nearbyCandidates[0]) {
        return clickButton(nearbyCandidates[0].button);
      }

      const iconButtons = Array.from(
        document.querySelectorAll('.anticon-reload, .anticon-sync, .anticon-redo, .anticon-retweet')
      )
        .map((element) => element.closest('button'))
        .filter(isUsableButton);
      if (iconButtons[0]) {
        return clickButton(iconButtons[0]);
      }

      const buttonFromText = Array.from(document.querySelectorAll('button')).find((button) => {
        if (!isUsableButton(button)) return false;
        const text = `${button.innerText || ''} ${button.title || ''} ${button.getAttribute('aria-label') || ''}`;
        return /刷新|重连|连接|reload|refresh|reconnect/i.test(text);
      });
      if (buttonFromText) {
        return clickButton(buttonFromText);
      }
      return false;
    }).catch(() => false);
  };

  for (let shellOpenCycle = 1; shellOpenCycle <= Math.max(1, maxShellOpenCycles); shellOpenCycle += 1) {
    if (shellOpenCycle > 1) {
      await closeEnvPages();
      await sleep(3000);
      activePage = await openEnvironmentSurface();
    } else {
      await sleep(3000);
      await refreshActivePage();
    }

    for (let attempt = 1; attempt <= 20; attempt += 1) {
      if (await shellTabSelected()) {
        break;
      }
      await waitForSpinnerToClear(3000).catch(() => {});
      try {
        await shellTrigger().click({ timeout: 5000 });
      } catch (error) {
        const message = String(error && (error.stack || error.message || error));
        if (!message.includes('intercepts pointer events') && !message.includes('Timeout')) {
          throw error;
        }
        await activePage.waitForTimeout(1000);
        continue;
      }
      await activePage.waitForTimeout(1000);
    }

    if (!(await shellTabSelected())) {
      if (shellOpenCycle < Math.max(1, maxShellOpenCycles)) {
        continue;
      }
      throw new Error(`Failed to activate Shell终端 tab for ${envName} after repeated spinner-aware retries.`);
    }
    await activePage.waitForTimeout(5000);

    let promptReady = false;
    let surfaceReadyWithoutPrompt = false;
    let interactiveSurfaceSeenAt = 0;
    let nudgedInteractiveSurface = false;
    let connectingSeenAt = 0;
    let lastReconnectAt = 0;
    let shellVisitFailureSeen = false;

    for (let reconnectAttempt = 0; reconnectAttempt < 5; reconnectAttempt += 1) {
      await refreshActivePage();
      if (reconnectAttempt === 0) {
        const bodyText = await activePage.locator('body').innerText().catch(() => '');
        if (/已断开|断开|disconnected/i.test(bodyText)) {
          await clickShellReconnect();
          lastReconnectAt = Date.now();
          await sleep(8000);
          await refreshActivePage();
        }
      }
      const terminalReadyDeadline = Date.now() + 60000;
      while (Date.now() < terminalReadyDeadline) {
        await refreshActivePage();
        if (await terminalHasPrompt()) {
          promptReady = true;
          break;
        }
        const shellVisitFailure = await detectShellVisitUrlFailure();
        if (
          shellVisitFailure.terminalFailure ||
          /wss:\/\/aihuanxin\.cn\/kunlun\/null/i.test(shellVisitFailure.bodyPreview || '') ||
          shellVisitFailure.consoleHit ||
          shellVisitFailure.shellVisitHit
        ) {
          shellVisitFailureSeen = true;
          break;
        }
        const surfaceSnapshot = await terminalSurfaceSnapshot();
        const hasInteractiveSurface =
          surfaceSnapshot.hasTerminal &&
          surfaceSnapshot.hasHelper &&
          (surfaceSnapshot.hasRows || surfaceSnapshot.hasCursor);
        if (surfaceSnapshot.connecting) {
          if (!connectingSeenAt) {
            connectingSeenAt = Date.now();
          }
          interactiveSurfaceSeenAt = 0;
          nudgedInteractiveSurface = false;
          if (Date.now() - connectingSeenAt >= 15000 && Date.now() - lastReconnectAt >= 12000) {
            const clickedConnectingReconnect = await clickShellReconnect();
            if (clickedConnectingReconnect) {
              lastReconnectAt = Date.now();
              await sleep(5000);
              await refreshActivePage();
              continue;
            }
          }
        } else {
          connectingSeenAt = 0;
        }
        if (surfaceSnapshot.disconnected) {
          interactiveSurfaceSeenAt = 0;
          nudgedInteractiveSurface = false;
          await clickShellReconnect();
          lastReconnectAt = Date.now();
          await sleep(5000);
          await refreshActivePage();
          continue;
        }
        if (hasInteractiveSurface && !surfaceSnapshot.connecting) {
          if (!interactiveSurfaceSeenAt) {
            interactiveSurfaceSeenAt = Date.now();
          }
          if (!nudgedInteractiveSurface && Date.now() - interactiveSurfaceSeenAt >= 5000) {
            await nudgeTerminalSurface();
            nudgedInteractiveSurface = true;
            continue;
          }
          if (Date.now() - interactiveSurfaceSeenAt >= 10000) {
            surfaceReadyWithoutPrompt = true;
            break;
          }
        } else {
          interactiveSurfaceSeenAt = 0;
          nudgedInteractiveSurface = false;
        }
        await activePage.waitForTimeout(1000);
      }
      if (promptReady || surfaceReadyWithoutPrompt || shellVisitFailureSeen) {
        break;
      }
      const clickedReconnect = await clickShellReconnect();
      if (!clickedReconnect) {
        break;
      }
      await sleep(5000);
      await refreshActivePage();
      await shellTrigger().click({ timeout: 5000 }).catch(() => {});
    }

    if (promptReady || surfaceReadyWithoutPrompt) {
      return activePage;
    }
    if (shellVisitFailureSeen && shellOpenCycle < Math.max(1, maxShellOpenCycles)) {
      continue;
    }

    const snapshot = await readTerminalText(activePage).catch(() => ({ text: '', debug: {} }));
    const surfaceSnapshot = await terminalSurfaceSnapshot();
    const shellVisitFailure = await detectShellVisitUrlFailure();
    const hasInteractiveSurface =
      surfaceSnapshot.hasTerminal &&
      surfaceSnapshot.hasHelper &&
      (surfaceSnapshot.hasRows || surfaceSnapshot.hasCursor) &&
      !surfaceSnapshot.disconnected &&
      !surfaceSnapshot.connecting;
    if (hasInteractiveSurface) {
      return activePage;
    }
    if (
      /获取shell终端信息失败/i.test(surfaceSnapshot.statusPreview || '') ||
      shellVisitFailure.terminalFailure ||
      /wss:\/\/aihuanxin\.cn\/kunlun\/null/i.test(shellVisitFailure.bodyPreview || '') ||
      shellVisitFailure.consoleHit ||
      shellVisitFailure.shellVisitHit ||
      shellVisitFailure.requestFailedHit ||
      shellVisitFailure.websocketHit
    ) {
      const failure = buildShellEndpointFailure(envName, shellVisitFailure);
      const error = new Error(
        `Shell terminal for ${envName} failed because the Huanxin shell endpoint API returned no terminal URL. ` +
          `${failure.summary}. ` +
          `surface=${JSON.stringify(surfaceSnapshot)} bodyPreview=${JSON.stringify(shellVisitFailure.bodyPreview)} ` +
          `consoleHit=${JSON.stringify(shellVisitFailure.consoleHit)} shellVisitHit=${JSON.stringify(shellVisitFailure.shellVisitHit)} ` +
          `requestFailedHit=${JSON.stringify(shellVisitFailure.requestFailedHit)} websocketHit=${JSON.stringify(shellVisitFailure.websocketHit)}`
      );
      error.huanxinFailure = failure;
      throw error;
    }
    throw new Error(
      `Shell terminal for ${envName} did not reach a prompt after reconnect attempts. ` +
        `Terminal preview: ${String(snapshot.text || '').slice(-500)} ` +
        `surface=${JSON.stringify(surfaceSnapshot)}`
    );
  }

  throw new Error(`Shell terminal for ${envName} did not open after ${Math.max(1, maxShellOpenCycles)} full cycles.`);
}

async function focusTerminal(activePage) {
  const terminal = activePage.locator('.terminal.xterm, .xterm, [class*="xterm"]').first();
  const terminalInput = activePage.locator('.xterm-helper-textarea, textarea[class*="xterm"]').first();
  await terminal.waitFor({ state: 'visible', timeout: 30000 });
  await terminalInput.waitFor({ state: 'attached', timeout: 30000 });
  await terminal.click({ timeout: 10000, force: true });
  await terminalInput.click({ timeout: 5000, force: true }).catch(() => {});
  await terminalInput.evaluate((element) => element.focus());
  await activePage.waitForTimeout(300);
  return terminalInput;
}

async function readTerminalText(activePage) {
  return activePage.evaluate(() => {
    const rowContainer = document.querySelector('.terminal.xterm .xterm-rows, .xterm-rows, [class*="xterm-rows"]');
    const accessibilityContainer = document.querySelector(
      '.terminal.xterm .xterm-accessibility, .xterm-accessibility, [class*="xterm-accessibility"]'
    );
    const helper = document.querySelector(
      '.terminal.xterm .xterm-helper-textarea, .xterm-helper-textarea, textarea[class*="xterm"]'
    );

    const collectChildrenText = (container) => {
      if (!container) return [];
      return Array.from(container.children)
        .map((row) => (row.textContent || '').replace(/\u00a0/g, ' ').trimEnd())
        .filter((line) => line.length > 0);
    };

    const collectContainerText = (container) => {
      if (!container) return [];
      const childLines = collectChildrenText(container);
      if (childLines.length > 0) return childLines;
      return (container.textContent || '')
        .replace(/\u00a0/g, ' ')
        .split('\n')
        .map((line) => line.trimEnd())
        .filter((line) => line.length > 0);
    };

    const rowLines = collectContainerText(rowContainer);
    const accessibilityLines = collectContainerText(accessibilityContainer);
    const terminalElement = document.querySelector('.terminal.xterm, .xterm, [class*="xterm"]');
    const terminalText = ((terminalElement?.innerText) || (terminalElement?.textContent) || '')
      .replace(/\u00a0/g, ' ')
      .split('\n')
      .map((line) => line.trimEnd())
      .filter((line) => line.length > 0);

    let lines = accessibilityLines.length > rowLines.length ? accessibilityLines : rowLines;
    if (terminalText.length > lines.length) {
      lines = terminalText;
    }

    return {
      text: lines.join('\n'),
      debug: {
        rowCount: rowContainer ? rowContainer.children.length : 0,
        accessibilityCount: accessibilityContainer ? accessibilityContainer.children.length : 0,
        rowTextLength: rowContainer ? ((rowContainer.textContent || '').length) : 0,
        accessibilityTextLength: accessibilityContainer ? ((accessibilityContainer.textContent || '').length) : 0,
        helperValue: helper ? helper.value : null,
        activeTag: document.activeElement ? document.activeElement.tagName : null,
        activeClassName: document.activeElement ? (document.activeElement.className || '') : '',
      },
    };
  });
}

async function sendCommand(activePage, command, waitMs = 10000) {
  const terminalInput = activePage.locator('.xterm-helper-textarea').first();
  const sendInterrupt = async () => {
    await terminalInput.evaluate((element) => {
      element.value = '';
    }).catch(() => {});
    await activePage.keyboard.insertText('\u0003').catch(() => {});
    await activePage.waitForTimeout(250);
  };
  const clearTerminal = async () => {
    await activePage.keyboard.press('Control+L').catch(() => {});
    await activePage.waitForTimeout(250);
    await activePage.keyboard.press('Control+L').catch(() => {});
    await activePage.waitForTimeout(250);
  };
  const injectionModes = ['insertText', 'locatorType', 'keyboardType'];
  const injectLiteralCommand = async (mode, literalCommand) => {
    await terminalInput.evaluate((element) => {
      element.value = '';
    }).catch(() => {});
    if (mode === 'locatorType') {
      await terminalInput.type(literalCommand, { delay: 1 });
      return;
    }
    if (mode === 'keyboardType') {
      await activePage.keyboard.type(literalCommand, { delay: 1 });
      return;
    }
    await activePage.keyboard.insertText(literalCommand);
  };

  const waitForPrompt = async (timeoutMs = 8000) => {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      const snapshot = await readTerminalText(activePage);
      const text = snapshot.text;
      const lines = text.split('\n').map((line) => line.trimEnd()).filter(Boolean);
      const lastLine = lines[lines.length - 1] || '';
      if (/[#$>]\s*$/.test(lastLine)) return text;
      await activePage.waitForTimeout(300);
    }
    return (await readTerminalText(activePage)).text;
  };

  const waitForStableAfterEnd = async (endMarker, timeoutMs = 3000) => {
    const deadline = Date.now() + timeoutMs;
    let lastText = '';
    let stableCount = 0;
    while (Date.now() < deadline) {
      await activePage.waitForTimeout(250);
      const snapshot = await readTerminalText(activePage);
      const text = snapshot.text;
      if (text === lastText) {
        stableCount += 1;
      } else {
        stableCount = 0;
        lastText = text;
      }
      const lines = text.split('\n').map((line) => line.trimEnd()).filter(Boolean);
      const lastLine = lines[lines.length - 1] || '';
      if (text.includes(endMarker) && /[#$>]\s*$/.test(lastLine) && stableCount >= 2) {
        return { text, debug: snapshot.debug };
      }
    }
    return readTerminalText(activePage);
  };

  let lastAttemptError = null;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    const injectionMode = injectionModes[Math.min(attempt - 1, injectionModes.length - 1)];
    await focusTerminal(activePage);

    // Break out of any lingering heredoc / secondary prompt state before we
    // try to inject fresh markers into the shell.
    await sendInterrupt();

    // Flush prior prompt/output before issuing a new command.
    await waitForPrompt().catch(() => {});
    await clearTerminal();
    const beforeSnapshot = await readTerminalText(activePage);
    const before = beforeSnapshot.text;

    // Use unique start/end markers. Encode the payload as a temporary script so
    // multiline commands and heredocs cannot swallow the wrapper markers.
    const token = `OC_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const startMarker = `__${token}_START__`;
    const endMarker = `__${token}_END__`;
    const statusMarker = `__${token}_STATUS__`;
    const scriptPath = `/tmp/huanxin_cmd_${token}.sh`;
    const encodedCommand = Buffer.from(`set +e\n${command}\n`, 'utf8').toString('base64');
    const wrappedCmd =
      `printf '${startMarker}\\n'; ` +
      `__oc_script='${scriptPath}'; ` +
      `printf '%s' '${encodedCommand}' | base64 -d > "$__oc_script"; ` +
      `__oc_decode_status=$?; ` +
      `if [ "$__oc_decode_status" -eq 0 ]; then bash "$__oc_script"; __oc_status=$?; else __oc_status="$__oc_decode_status"; fi; ` +
      `rm -f "$__oc_script"; ` +
      `printf '\\n${statusMarker}:%s\\n${endMarker}\\n' "$__oc_status"`;
    const literalCommand = `   ${wrappedCmd}`;
    await injectLiteralCommand(injectionMode, literalCommand);
    await activePage.keyboard.press('Enter');

    const deadline = Date.now() + waitMs;
    let after = '';
    let afterDebug = null;
    let sawStartMarker = false;
    let sawEndMarker = false;
    const markerPrintedOnOwnLine = (text, marker) =>
      text
        .split('\n')
        .map((line) => line.trim())
        .some((line) => line === marker);

    while (Date.now() < deadline) {
      await activePage.waitForTimeout(500);
      const snapshot = await readTerminalText(activePage);
      after = snapshot.text;
      afterDebug = snapshot.debug;
      sawStartMarker = sawStartMarker || markerPrintedOnOwnLine(after, startMarker);
      sawEndMarker = sawEndMarker || markerPrintedOnOwnLine(after, endMarker);
      if (sawEndMarker) {
        const stable = await waitForStableAfterEnd(endMarker);
        after = stable.text;
        afterDebug = stable.debug;
        break;
      }
    }

    if (!after.includes(startMarker) && !after.includes(endMarker)) {
      lastAttemptError = new Error(
        `Terminal never showed command markers on attempt ${attempt} using ${injectionMode}; retrying command injection.`
      );
      await activePage.waitForTimeout(1000);
      continue;
    }

    if (!sawEndMarker) {
      lastAttemptError = new Error(
        `Terminal did not print completion marker on attempt ${attempt} using ${injectionMode} before timeout; retrying command injection.`
      );
      await sendInterrupt();
      await activePage.waitForTimeout(1000);
      continue;
    }

    let output = '';
    let commandStatus = 0;
    const afterLines = after.split('\n');
    const trimmedAfterLines = afterLines.map((line) => line.trim());
    const startLineIdx = trimmedAfterLines.findIndex((line) => line === startMarker);
    const statusLineIdx = trimmedAfterLines.findIndex(
      (line, index) => index > startLineIdx && line.startsWith(`${statusMarker}:`)
    );
    const endLineIdx = trimmedAfterLines.findIndex((line, index) => index > startLineIdx && line === endMarker);

    if (statusLineIdx >= 0) {
      const statusLine = trimmedAfterLines[statusLineIdx];
      const parsedStatus = Number.parseInt(statusLine.slice(statusMarker.length + 1), 10);
      if (!Number.isNaN(parsedStatus)) {
        commandStatus = parsedStatus;
      }
    }

    if (startLineIdx >= 0) {
      const payloadEndIdx =
        statusLineIdx >= 0 ? statusLineIdx : (endLineIdx >= 0 ? endLineIdx : afterLines.length);
      output = afterLines.slice(startLineIdx + 1, payloadEndIdx).join('\n');
    } else {
      const beforeLines = before.split('\n');
      output = afterLines.slice(beforeLines.length).join('\n');
    }

    output = output.replace(/^\n+/, '').replace(/\n+$/, '');

    // Remove echoed wrapper fragments and prompt lines around the captured payload.
    const promptLike = /^.*[#$>]\s*$/;
    let outputLines = output.split('\n');
    const firstMarkerLine = outputLines.findIndex((line) => line.includes(startMarker));
    if (firstMarkerLine >= 0) {
      outputLines = outputLines.slice(firstMarkerLine + 1);
    }
    const lastMarkerLine = outputLines.findIndex((line) => line.includes(endMarker));
    if (lastMarkerLine >= 0) {
      outputLines = outputLines.slice(0, lastMarkerLine);
    }
    output = outputLines.join('\n');

    const escapeRegex = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const escapedStartMarker = escapeRegex(startMarker);
    const escapedEndMarker = escapeRegex(endMarker);
    const escapedStatusMarker = escapeRegex(statusMarker);
    const wrapperRegex = new RegExp(`^.*printf '(?:${escapedStartMarker}\\n|\\n?${escapedEndMarker}\\n)'.*$`);
    const wrapperFragmentRegex = /^\\n';\s.*printf '\\$/;
    outputLines = output.split('\n').filter((line) => {
      const trimmed = line.trim();
      if (!trimmed) return false;
      if (promptLike.test(trimmed)) return false;
      if (line.includes(startMarker) || line.includes(endMarker)) return false;
      if (line.includes(statusMarker)) return false;
      if (wrapperRegex.test(line) || wrapperFragmentRegex.test(line)) return false;
      if (trimmed === "'" || trimmed === ";" || trimmed === "n") return false;
      return true;
    });
    output = outputLines.join('\n').trim();

    return {
      before,
      after,
      output,
      commandStatus,
      commandOk: commandStatus === 0,
      debug: { before: beforeSnapshot.debug, after: afterDebug },
    };
  }

  throw lastAttemptError || new Error('Failed to inject command into Huanxin terminal after retries.');
}

async function main() {
  assertAutomationAllowed('huanxin_shell_exec');
  const { envName, command, waitMs, requireDaemon, skipDaemon } = parseArgs(process.argv.slice(2));
  const standaloneAllowed = allowStandaloneFallback();

  // Try the persistent daemon first — avoids launching a new browser
  if (!skipDaemon) {
    const daemonStartedAt = Date.now();
    const daemonResult = await tryDaemon(envName, command, waitMs);
    if (daemonResult) {
      daemonResult.transport = 'daemon';
      daemonResult.durationMs = daemonResult.durationMs ?? (Date.now() - daemonStartedAt);
      console.log(JSON.stringify(daemonResult, null, 2));
      if (daemonResult.ok === false) {
        process.exitCode = 1;
      }
      return;
    }
    const fileResult = await tryDaemonFileTransport(envName, command, waitMs);
    if (fileResult) {
      fileResult.transport = 'daemon_file';
      fileResult.durationMs = fileResult.durationMs ?? (Date.now() - daemonStartedAt);
      console.log(JSON.stringify(fileResult, null, 2));
      if (fileResult.ok === false) {
        process.exitCode = 1;
      }
      return;
    }
  }

  if (requireDaemon) {
    throw new Error(`Huanxin daemon for ${envName} is not available`);
  }

  if (!standaloneAllowed && !skipDaemon) {
    throw new Error(
      `Huanxin daemon transport for ${envName} is unavailable and standalone fallback is disabled. ` +
        `Set HUANXIN_ALLOW_STANDALONE_FALLBACK=1 only for explicit recovery/debugging.`
    );
  }

  // No daemon running — fall back to standalone browser (headless by default)
  const { profileDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;

  try {
    const page = context.pages()[0] || (await context.newPage());
    page.setDefaultTimeout(30000);

    const startedAt = Date.now();
    let activePage = null;
    try {
      activePage = await openShell(page, envName);
      const { before, after, output, commandStatus, commandOk, debug } = await sendCommand(activePage, command, waitMs);

      await activePage.screenshot({ path: `browser-automation/huanxin-shell-${envName}.png`, fullPage: true });
      console.log(
        JSON.stringify(
          {
            ok: true,
            envName,
            transport: 'standalone',
            browserMode: launch.browserMode,
            launchFallbackUsed: launch.fallbackUsed,
            url: redactAuthUrl(activePage.url()),
            command,
            durationMs: Date.now() - startedAt,
            output: output || '',
            commandStatus,
            commandOk,
            before,
            after,
            debug,
          },
          null,
          2
        )
      );
    } catch (error) {
      const debugPage = activePage && !activePage.isClosed() ? activePage : page;
      const failureDebug = {
        envName,
        command,
        browserMode: launch.browserMode,
        launchFallbackUsed: launch.fallbackUsed,
        screenshotPath: `browser-automation/huanxin-shell-${envName}-failure.png`,
      };
      if (debugPage && !debugPage.isClosed()) {
        failureDebug.url = debugPage.url();
        failureDebug.pageState = await detectPageState(debugPage).catch((innerError) => ({
          error: String(innerError && (innerError.stack || innerError.message || innerError)),
        }));
        failureDebug.terminal = await readTerminalText(debugPage).catch((innerError) => ({
          error: String(innerError && (innerError.stack || innerError.message || innerError)),
        }));
        await debugPage
          .screenshot({ path: failureDebug.screenshotPath, fullPage: true })
          .catch((innerError) => {
            failureDebug.screenshotError = String(innerError && (innerError.stack || innerError.message || innerError));
          });
      }
      error.message = `${error.message}\nFailure debug: ${JSON.stringify(failureDebug)}`;
      throw error;
    }
  } finally {
    await context.close();
  }
}

module.exports = {
  DEFAULT_TRAIN_DEV_URL,
  TRAIN_DEV_URL,
  focusTerminal,
  openShell,
  readTerminalText,
  sendCommand,
};

if (require.main === module) {
  main().catch((error) => {
    console.error(error);
    process.exit(error && error.code === 'HUANXIN_MANUAL_MODE_LOCKED' ? 125 : 1);
  });
}
