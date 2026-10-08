#!/usr/bin/env node
const fs = require('fs');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { bridgePageViaSafariSso } = require('./huanxin_repair_profile_via_safari_sso');

function usage() {
  console.error('Usage: node browser-automation/huanxin_service_terminal_exec.js --url <service terminal url> [--command <cmd>] [--wait-ms <ms>] [--no-bridge]');
  process.exit(1);
}

function parseArgs(argv) {
  const args = { url: null, command: null, waitMs: 10000, noBridge: false };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === '--url') { args.url = argv[++i] || null; continue; }
    if (token === '--command') { args.command = argv[++i] || null; continue; }
    if (token === '--wait-ms') { args.waitMs = parseInt(argv[++i] || '10000', 10); continue; }
    if (token === '--no-bridge') { args.noBridge = true; continue; }
    usage();
  }
  if (!args.url) usage();
  if (!Number.isFinite(args.waitMs) || args.waitMs < 1000) args.waitMs = 10000;
  return args;
}

function clean(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function classifyUrl(url) {
  const lower = String(url || '').toLowerCase();
  if (lower.includes('/auth/realms/') || lower.includes('openid-connect/auth') || lower.includes('login')) return 'login_required';
  if (lower.includes('/kl-web')) return 'app_surface';
  return 'unknown';
}

async function collectSummary(page) {
  return page.evaluate(() => {
    const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
    const targets = Array.from(document.querySelectorAll('button, a, [role="button"], input, textarea, [contenteditable="true"], .xterm, [class*="terminal"], [class*="xterm"]'))
      .map((el) => ({
        tag: el.tagName,
        role: el.getAttribute('role') || '',
        text: clean(el.innerText || el.textContent || '').slice(0, 300),
        title: el.getAttribute('title') || '',
        aria: el.getAttribute('aria-label') || '',
        placeholder: el.getAttribute('placeholder') || '',
        className: (el.getAttribute('class') || '').slice(0, 220),
      }))
      .filter((entry) => entry.text || entry.title || entry.aria || entry.placeholder || /terminal|xterm/i.test(entry.className))
      .slice(0, 120);
    return {
      title: document.title,
      url: location.href,
      bodyPreview: clean(document.body?.innerText || '').slice(0, 5000),
      xtermCount: document.querySelectorAll('.xterm, [class*="xterm"]').length,
      textareaCount: document.querySelectorAll('textarea').length,
      targets,
    };
  });
}

async function readTerminalText(page) {
  return page.evaluate(() => {
    const rowContainer = document.querySelector('.terminal.xterm .xterm-rows, .xterm-rows, [class*="xterm-rows"]');
    const accessibilityContainer = document.querySelector('.terminal.xterm .xterm-accessibility, .xterm-accessibility, [class*="xterm-accessibility"]');
    const helper = document.querySelector('.terminal.xterm .xterm-helper-textarea, .xterm-helper-textarea, textarea[class*="xterm"]');
    const collect = (container) => {
      if (!container) return [];
      const childLines = Array.from(container.children || []).map((row) => (row.textContent || '').replace(/\u00a0/g, ' ').trimEnd()).filter(Boolean);
      if (childLines.length) return childLines;
      return (container.textContent || '').replace(/\u00a0/g, ' ').split('\n').map((line) => line.trimEnd()).filter(Boolean);
    };
    const rowLines = collect(rowContainer);
    const accessLines = collect(accessibilityContainer);
    const terminalElement = document.querySelector('.terminal.xterm, .xterm, [class*="xterm"]');
    const terminalText = ((terminalElement?.innerText) || (terminalElement?.textContent) || '').replace(/\u00a0/g, ' ').split('\n').map((line) => line.trimEnd()).filter(Boolean);
    let lines = accessLines.length > rowLines.length ? accessLines : rowLines;
    if (terminalText.length > lines.length) lines = terminalText;
    return {
      text: lines.join('\n'),
      debug: {
        rowCount: rowContainer ? rowContainer.children.length : 0,
        accessibilityCount: accessibilityContainer ? accessibilityContainer.children.length : 0,
        helperAttached: Boolean(helper),
        helperValue: helper ? helper.value : null,
        activeTag: document.activeElement ? document.activeElement.tagName : null,
        activeClassName: document.activeElement ? (document.activeElement.className || '') : '',
      },
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

async function terminalHasPrompt(page) {
  const snapshot = await readTerminalText(page).catch(() => ({ text: '' }));
  const lines = String(snapshot.text || '').split('\n').map((line) => line.trimEnd()).filter(Boolean);
  const lastLine = lines[lines.length - 1] || '';
  return /[#$>]\s*$/.test(lastLine);
}

async function clickReconnect(page) {
  return page.evaluate(() => {
    const isVisible = (el) => {
      if (!el) return false;
      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);
      return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    };
    const usableButton = (el) => {
      const button = el?.closest?.('button') || el;
      return button && button.tagName === 'BUTTON' && !button.disabled && isVisible(button);
    };
    const clickButton = (button) => { button.scrollIntoView({ block: 'center', inline: 'center' }); button.click(); return true; };
    const textButton = Array.from(document.querySelectorAll('button')).find((button) => {
      if (!usableButton(button)) return false;
      const text = `${button.innerText || ''} ${button.title || ''} ${button.getAttribute('aria-label') || ''}`;
      return /刷新|重连|连接|reload|refresh|reconnect/i.test(text);
    });
    if (textButton) return clickButton(textButton);
    const iconButton = Array.from(document.querySelectorAll('.anticon-reload, .anticon-sync, .anticon-redo, .anticon-retweet')).map((el) => el.closest('button')).find(usableButton);
    if (iconButton) return clickButton(iconButton);
    return false;
  }).catch(() => false);
}

async function waitForTerminalReady(page) {
  await page.locator('.terminal.xterm, .xterm, [class*="xterm"]').first().waitFor({ state: 'visible', timeout: 180000 });
  const startText = await page.locator('body').innerText().catch(() => '');
  if (/已断开|断开|disconnected/i.test(startText)) {
    await clickReconnect(page);
    await page.waitForTimeout(8000);
  }
  let ready = false;
  for (let reconnect = 0; reconnect < 4 && !ready; reconnect += 1) {
    const deadline = Date.now() + 90000;
    while (Date.now() < deadline) {
      if (await terminalHasPrompt(page)) { ready = true; break; }
      await page.waitForTimeout(1000);
    }
    if (!ready) {
      const clicked = await clickReconnect(page);
      if (!clicked) break;
      await page.waitForTimeout(7000);
    }
  }
  if (!ready) {
    const snap = await readTerminalText(page).catch(() => ({ text: '', debug: {} }));
    throw new Error(`service terminal did not reach prompt. preview=${String(snap.text || '').slice(-800)} debug=${JSON.stringify(snap.debug || {})}`);
  }
}

async function sendCommand(page, command, waitMs) {
  const input = await focusTerminal(page);
  const endMarker = `__HUANXIN_SERVICE_RUN_${Date.now()}_${Math.random().toString(36).slice(2, 8)}__`;
  const wrapped = `${command}; printf '\\n${endMarker}:%s\\n' "$?"`;
  const modes = ['insertText', 'locatorType', 'keyboardType'];
  let lastError = null;
  for (let attempt = 0; attempt < modes.length; attempt += 1) {
    try {
      await input.evaluate((el) => { el.value = ''; }).catch(() => {});
      // Break out of any lingering heredoc/secondary prompt state before issuing a fresh command.
      await page.keyboard.insertText('\u0003').catch(() => {});
      await page.waitForTimeout(300);
      await input.evaluate((el) => { el.value = ''; }).catch(() => {});
      if (modes[attempt] === 'locatorType') await input.type(wrapped, { delay: 1 });
      else if (modes[attempt] === 'keyboardType') await page.keyboard.type(wrapped, { delay: 1 });
      else await page.keyboard.insertText(wrapped);
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);
      const deadline = Date.now() + waitMs;
      let snapshot = { text: '', debug: {} };
      while (Date.now() < deadline) {
        snapshot = await readTerminalText(page);
        if (snapshot.text.includes(endMarker)) {
          await page.waitForTimeout(1000);
          snapshot = await readTerminalText(page);
          const match = snapshot.text.match(new RegExp(`${endMarker}:(\\d+)`));
          return { ok: true, mode: modes[attempt], exitCode: match ? Number(match[1]) : null, endMarker, terminalText: snapshot.text, debug: snapshot.debug };
        }
        await page.waitForTimeout(500);
      }
      throw new Error(`timeout waiting for marker ${endMarker}`);
    } catch (error) {
      lastError = error;
      await page.keyboard.insertText('\u0003').catch(() => {});
      await page.waitForTimeout(1000);
    }
  }
  throw lastError || new Error('command injection failed');
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const { profileDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;
  const page = context.pages()[0] || await context.newPage();
  page.setDefaultTimeout(30000);
  const result = { ok: false, browserMode: launch.browserMode, launchFallbackUsed: launch.fallbackUsed };
  try {
    await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(5000);
    result.afterGoto = await collectSummary(page).catch((error) => ({ error: String(error) }));
    if (classifyUrl(page.url()) === 'login_required') {
      if (args.noBridge) throw new Error(`login required at ${page.url()}`);
      const bridge = await bridgePageViaSafariSso(page, {
        authUrl: page.url(),
        targetUrl: args.url,
        waitMs: 12000,
        resultPath: '/tmp/huanxin-service-terminal-sso.json',
      });
      result.bridge = bridge;
      if (!bridge || !bridge.ok) throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
      await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 180000 });
      await page.waitForTimeout(5000);
    }
    result.afterAuth = await collectSummary(page).catch((error) => ({ error: String(error) }));
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
    fs.writeFileSync('/tmp/huanxin-service-terminal-last.json', JSON.stringify(result, null, 2));
    await context.close().catch(() => {});
  }
  console.log(JSON.stringify(result, null, 2));
}

main().catch((error) => {
  const payload = { ok: false, error: String(error && (error.stack || error.message || error)) };
  try { fs.writeFileSync('/tmp/huanxin-service-terminal-last-error.json', JSON.stringify(payload, null, 2)); } catch {}
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
});
