#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { bridgePageViaSafariSso, classifyUrl } = require('./huanxin_repair_profile_via_safari_sso');
const { assertAutomationAllowed } = require('./huanxin_manual_lock');

function usage() {
  console.error(
    'Usage: node browser-automation/huanxin_env_terminal_exec.js --env <env-name> [--command <cmd>] [--wait-ms <ms>] [--dump-json <path>] [--no-bridge]'
  );
  process.exit(1);
}

function parseArgs(argv) {
  const args = {
    envName: null,
    command: null,
    waitMs: 10000,
    dumpJson: null,
    noBridge: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === '--env') {
      args.envName = argv[++i] || null;
      continue;
    }
    if (token === '--command') {
      args.command = argv[++i] || null;
      continue;
    }
    if (token === '--wait-ms') {
      args.waitMs = parseInt(argv[++i] || '10000', 10);
      continue;
    }
    if (token === '--dump-json') {
      args.dumpJson = argv[++i] || null;
      continue;
    }
    if (token === '--no-bridge') {
      args.noBridge = true;
      continue;
    }
    usage();
  }
  if (!args.envName) usage();
  if (!Number.isFinite(args.waitMs) || args.waitMs < 1000) args.waitMs = 10000;
  return args;
}

function clean(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function readEnvConfig(envName) {
  const scriptPath = path.resolve(__dirname, '../scripts/huanxin_env_config.py');
  const { execFileSync } = require('child_process');
  const stdout = execFileSync('python3', [scriptPath, '--env', envName], {
    cwd: path.resolve(__dirname, '..'),
    encoding: 'utf8',
  });
  const payload = JSON.parse(stdout);
  if (!payload || typeof payload !== 'object') {
    throw new Error(`Invalid env config for ${envName}`);
  }
  return payload;
}

async function collectSummary(page) {
  return page.evaluate(() => {
    const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
    return {
      title: document.title,
      url: location.href,
      bodyPreview: clean(document.body?.innerText || '').slice(0, 4000),
    };
  });
}

async function hasTerminalSurface(page) {
  return page.evaluate(() => {
    const terminal = document.querySelector('.terminal.xterm, .xterm, [class*="xterm"]');
    const helper = document.querySelector('.xterm-helper-textarea, textarea[class*="xterm"]');
    const rows = document.querySelector('.xterm-rows, [class*="xterm-rows"]');
    return Boolean(terminal && (helper || rows));
  }).catch(() => false);
}

async function openShellTab(page) {
  const tab = page.getByText('Shell终端', { exact: true }).first();
  await tab.waitFor({ state: 'visible', timeout: 30000 });
  await tab.click({ timeout: 10000, force: true }).catch(async () => {
    await tab.evaluate((element) => element.click());
  });
  await page.waitForTimeout(8000);
}

async function ensureAppSurface(page, targetUrl, noBridge) {
  await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(5000);
  if (classifyUrl(page.url()) === 'login_required') {
    if (noBridge) {
      throw new Error(`login required at ${page.url()}`);
    }
    const bridge = await bridgePageViaSafariSso(page, {
      authUrl: page.url(),
      targetUrl,
      waitMs: 12000,
      resultPath: '/tmp/huanxin-env-terminal-exec-sso.json',
    });
    if (!bridge || !bridge.ok) {
      throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
    }
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(5000);
  }
}

async function discoverTerminalUrl(page, envConfig) {
  const result = await page.evaluate(async ({ envId }) => {
    const collectJson = async (input, init) => {
      const response = await fetch(input, {
        ...init,
        credentials: 'include',
        headers: {
          'content-type': 'application/json',
          ...(init && init.headers ? init.headers : {}),
        },
      });
      const text = await response.text();
      let json = null;
      try {
        json = JSON.parse(text);
      } catch {}
      return { ok: response.ok, status: response.status, text, json };
    };

    const detail = await collectJson(`/kunlun/web/develop/v1/detail?id=${encodeURIComponent(envId)}`, {
      method: 'GET',
      headers: {},
    });
    const detailData = detail.json && detail.json.data;
    const podInfoList = Array.isArray(detailData && detailData.podInfoList) ? detailData.podInfoList : [];
    const firstPod = podInfoList.find((item) => item && item.podName) || null;
    if (!firstPod) {
      return {
        ok: false,
        blocker: 'missing_pod',
        detail,
      };
    }
    const shellPayload = {
      id: envId,
      podName: firstPod.podName,
      type: 'terminal',
    };
    const shellVisit = await collectJson('/kunlun/web/develop/v1/getShellVisitUrl', {
      method: 'POST',
      body: JSON.stringify(shellPayload),
    });
    return {
      ok: Boolean(shellVisit.json && shellVisit.json.code === 0 && shellVisit.json.data),
      envId,
      detail,
      podName: firstPod.podName,
      containerId: firstPod.containerId || null,
      shellPayload,
      shellVisit,
      terminalUrl: shellVisit.json && shellVisit.json.data ? shellVisit.json.data : null,
    };
  }, { envId: envConfig.env_id });
  return result;
}

async function readTerminalText(page) {
  return page.evaluate(() => {
    const collect = (selector) => {
      const node = document.querySelector(selector);
      if (!node) return [];
      const children = Array.from(node.children || []);
      const lines = children.map((row) => (row.textContent || '').replace(/\u00a0/g, ' ').trimEnd()).filter(Boolean);
      if (lines.length) return lines;
      return (node.textContent || '')
        .replace(/\u00a0/g, ' ')
        .split('\n')
        .map((line) => line.trimEnd())
        .filter(Boolean);
    };
    const rowLines = collect('.terminal.xterm .xterm-rows, .xterm-rows, [class*="xterm-rows"]');
    const accessLines = collect('.terminal.xterm .xterm-accessibility, .xterm-accessibility, [class*="xterm-accessibility"]');
    const terminalElement = document.querySelector('.terminal.xterm, .xterm, [class*="xterm"]');
    const terminalText = ((terminalElement?.innerText) || (terminalElement?.textContent) || '')
      .replace(/\u00a0/g, ' ')
      .split('\n')
      .map((line) => line.trimEnd())
      .filter(Boolean);
    let lines = accessLines.length > rowLines.length ? accessLines : rowLines;
    if (terminalText.length > lines.length) lines = terminalText;
    return {
      text: lines.join('\n'),
      activeTag: document.activeElement ? document.activeElement.tagName : null,
    };
  });
}

async function focusTerminal(page) {
  const terminal = page.locator('.terminal.xterm, .xterm, [class*="xterm"]').first();
  const input = page.locator('.xterm-helper-textarea, textarea[class*="xterm"]').first();
  await terminal.waitFor({ state: 'visible', timeout: 60000 });
  await input.waitFor({ state: 'attached', timeout: 60000 });
  await terminal.click({ timeout: 10000, force: true });
  await input.click({ timeout: 5000, force: true }).catch(() => {});
  await input.evaluate((el) => el.focus()).catch(() => {});
  await page.waitForTimeout(300);
  return input;
}

async function clickReconnect(page) {
  return page.evaluate(() => {
    const visible = (el) => {
      if (!el) return false;
      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);
      return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    };
    const buttons = Array.from(document.querySelectorAll('button'));
    const target = buttons.find((button) => {
      if (button.disabled || !visible(button)) return false;
      const text = `${button.innerText || ''} ${button.title || ''} ${button.getAttribute('aria-label') || ''}`;
      return /刷新|重连|连接|reload|refresh|reconnect/i.test(text);
    });
    if (!target) return false;
    target.scrollIntoView({ block: 'center', inline: 'center' });
    target.click();
    return true;
  }).catch(() => false);
}

async function waitForTerminalReady(page) {
  await page.locator('.terminal.xterm, .xterm, [class*="xterm"]').first().waitFor({ state: 'visible', timeout: 180000 });
  for (let reconnect = 0; reconnect < 4; reconnect += 1) {
    const deadline = Date.now() + 90000;
    while (Date.now() < deadline) {
      const snapshot = await readTerminalText(page).catch(() => ({ text: '' }));
      const lines = String(snapshot.text || '').split('\n').map((line) => line.trimEnd()).filter(Boolean);
      const lastLine = lines[lines.length - 1] || '';
      if (/[#$>]\s*$/.test(lastLine)) {
        return;
      }
      await page.waitForTimeout(1000);
    }
    const clicked = await clickReconnect(page);
    if (!clicked) break;
    await page.waitForTimeout(7000);
  }
  const snap = await readTerminalText(page).catch(() => ({ text: '' }));
  throw new Error(`terminal did not reach prompt. preview=${String(snap.text || '').slice(-800)}`);
}

async function sendCommand(page, command, waitMs) {
  const input = await focusTerminal(page);
  const endMarker = `__HUANXIN_ENV_RUN_${Date.now()}_${Math.random().toString(36).slice(2, 8)}__`;
  const wrapped = `${command}; printf '\\n${endMarker}:%s\\n' "$?"`;
  await input.evaluate((el) => { el.value = ''; }).catch(() => {});
  await page.keyboard.press('Control+C').catch(() => {});
  await page.waitForTimeout(300);
  await page.keyboard.insertText(wrapped);
  await page.keyboard.press('Enter');
  const deadline = Date.now() + waitMs;
  let snapshot = { text: '' };
  while (Date.now() < deadline) {
    snapshot = await readTerminalText(page);
    if (snapshot.text.includes(endMarker)) {
      const match = snapshot.text.match(new RegExp(`${endMarker}:(\\d+)`));
      return {
        ok: true,
        exitCode: match ? Number(match[1]) : null,
        endMarker,
        terminalText: snapshot.text,
      };
    }
    await page.waitForTimeout(500);
  }
  throw new Error(`timeout waiting for marker ${endMarker}`);
}

async function main() {
  assertAutomationAllowed('huanxin_env_terminal_exec');
  const args = parseArgs(process.argv.slice(2));
  const envConfig = readEnvConfig(args.envName);
  const { profileDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;
  const page = context.pages()[0] || await context.newPage();
  page.setDefaultTimeout(30000);
  const result = {
    ok: false,
    envName: args.envName,
    envConfig,
    browserMode: launch.browserMode,
    launchFallbackUsed: launch.fallbackUsed,
  };
  try {
    await ensureAppSurface(page, envConfig.train_dev_url, args.noBridge);
    result.afterAuth = await collectSummary(page).catch((error) => ({ error: String(error) }));
    const terminalInfo = await discoverTerminalUrl(page, envConfig);
    result.terminalInfo = terminalInfo;
    let terminalSurfacePresent = await hasTerminalSurface(page);
    if (!terminalSurfacePresent) {
      await openShellTab(page).catch(() => {});
      terminalSurfacePresent = await hasTerminalSurface(page);
    }
    if (!terminalInfo.ok || !terminalInfo.terminalUrl) {
      result.terminalFallbackUsed = true;
      if (!terminalSurfacePresent) {
        throw new Error(`failed to resolve terminal url and no terminal surface visible after opening Shell终端: ${JSON.stringify(terminalInfo)}`);
      }
      await waitForTerminalReady(page);
      result.terminalReady = true;
      if (args.command) {
        result.command = args.command;
        result.exec = await sendCommand(page, args.command, args.waitMs);
      } else {
        result.terminalSnapshot = await readTerminalText(page);
      }
      result.ok = true;
      return;
    }
    if (!terminalSurfacePresent) {
      await page.goto(terminalInfo.terminalUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
      await page.waitForTimeout(5000);
    }
    result.afterTerminalGoto = await collectSummary(page).catch((error) => ({ error: String(error) }));
    await waitForTerminalReady(page);
    result.terminalReady = true;
    if (args.command) {
      result.command = args.command;
      result.exec = await sendCommand(page, args.command, args.waitMs);
    } else {
      result.terminalSnapshot = await readTerminalText(page);
    }
    result.ok = true;
  } finally {
    const outputPath = args.dumpJson || '/tmp/huanxin-env-terminal-exec-last.json';
    try {
      fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
    } catch {}
    await context.close().catch(() => {});
  }
  console.log(JSON.stringify(result, null, 2));
}

main().catch((error) => {
  const payload = { ok: false, error: String(error && (error.stack || error.message || error)) };
  try {
    fs.writeFileSync('/tmp/huanxin-env-terminal-exec-last-error.json', JSON.stringify(payload, null, 2));
  } catch {}
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
});
