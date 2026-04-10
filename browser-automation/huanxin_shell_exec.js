const http = require('http');
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { bridgePageViaSafariSso } = require('./huanxin_repair_profile_via_safari_sso');

const ENV_PORTS = { ai1: 19001, ai2: 19002 };

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
  'https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev';
const TRAIN_DEV_URL = process.env.HUANXIN_TRAIN_DEV_URL || DEFAULT_TRAIN_DEV_URL;

function getSafariSsoBridgeWaitMs() {
  const raw = process.env.HUANXIN_SAFARI_SSO_BRIDGE_WAIT_MS || '10000';
  const parsed = parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 10000;
}

async function openShell(page, envName) {
  const findExistingEnvPage = () =>
    page
      .context()
      .pages()
      .find(
        (candidate) =>
          candidate.url().includes('/train-dev/environment/') && candidate.url().includes(`name=${envName}`)
      );

  let lastError = null;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const existingPage = findExistingEnvPage();
      if (existingPage) {
        await existingPage.bringToFront().catch(() => {});
        await existingPage.waitForTimeout(1000);
        return existingPage;
      }

      // Always start from the canonical train-dev route for this workspace.
      await page.goto(TRAIN_DEV_URL, { waitUntil: 'networkidle', timeout: 180000 });
      await page.waitForTimeout(3000);
      let pageState = await detectPageState(page);
      if (pageState.state === 'login_required') {
        const repair = await bridgePageViaSafariSso(page, {
          authUrl: pageState.url,
          waitMs: getSafariSsoBridgeWaitMs(),
          resultPath: `/tmp/huanxin-${envName}-daemon-safari-sso-bridge.json`,
        });
        if (!repair.ok) {
          throw new Error(
            `Huanxin auth expired before opening ${envName}; Safari SSO bridge failed at ${pageState.url}. Final state=${repair.finalUrlState}. Body preview: ${repair.bodyPreview}`
          );
        }
        await page.waitForTimeout(3000);
        pageState = await detectPageState(page);
        if (pageState.state === 'login_required') {
          throw new Error(
            `Huanxin auth repair did not stick for ${envName}; login_required still visible at ${pageState.url}. Body preview: ${pageState.bodyPreview}`
          );
        }
      }

      const row = page.locator('tr', { hasText: envName }).first();
      await row.waitFor({ state: 'visible', timeout: 60000 });
      const openButton = row.getByRole('button', { name: '打开' }).first();
      const startButton = row.getByRole('button', { name: '运行' }).first();

      let clicked = false;
      let startTriggered = false;
      for (let poll = 0; poll < 20; poll += 1) {
        const existingAfterLoad = findExistingEnvPage();
        if (existingAfterLoad) {
          await existingAfterLoad.bringToFront().catch(() => {});
          await existingAfterLoad.waitForTimeout(1000);
          return existingAfterLoad;
        }

        const enabled = await openButton.isEnabled().catch(() => false);
        const rowText = ((await row.textContent().catch(() => '')) || '').replace(/\s+/g, ' ').trim();
        const startVisible = await startButton.isVisible().catch(() => false);
        const startEnabled = await startButton.isEnabled().catch(() => false);
        const spinning = await page.locator('.ant-spin-spinning, .ant-spin-blur').count().catch(() => 0);
        if (!startTriggered && rowText.includes('已停止') && startVisible && startEnabled && spinning === 0) {
          await startButton.click({ timeout: 15000 });
          startTriggered = true;
          await page.waitForTimeout(8000);
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

  const pages = page.context().pages();
  const activePage = pages[pages.length - 1];
  await activePage.waitForTimeout(3000);

  const shellTrigger = activePage.getByText('Shell终端', { exact: true }).first();
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
    const selected = await shellTrigger.getAttribute('aria-selected').catch(() => null);
    return selected === 'true';
  };

  for (let attempt = 1; attempt <= 20; attempt += 1) {
    if (await shellTabSelected()) {
      break;
    }
    await waitForSpinnerToClear(3000).catch(() => {});
    try {
      await shellTrigger.click({ timeout: 5000 });
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
    throw new Error(`Failed to activate Shell终端 tab for ${envName} after repeated spinner-aware retries.`);
  }
  await activePage.waitForTimeout(5000);
  return activePage;
}

async function focusTerminal(activePage) {
  const terminal = activePage.locator('.terminal.xterm').first();
  const terminalInput = activePage.locator('.xterm-helper-textarea').first();
  await terminal.waitFor({ state: 'visible', timeout: 30000 });
  await terminalInput.waitFor({ state: 'attached', timeout: 30000 });
  await terminal.click({ timeout: 10000, force: true });
  await terminalInput.evaluate((element) => element.focus());
  await activePage.waitForTimeout(300);
  return terminalInput;
}

async function readTerminalText(activePage) {
  return activePage.evaluate(() => {
    const rowContainer = document.querySelector('.terminal.xterm .xterm-rows');
    const accessibilityContainer = document.querySelector('.terminal.xterm .xterm-accessibility');
    const helper = document.querySelector('.terminal.xterm .xterm-helper-textarea');

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
    const terminalText = ((document.querySelector('.terminal.xterm')?.innerText) || (document.querySelector('.terminal.xterm')?.textContent) || '')
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
    await focusTerminal(activePage);

    // Break out of any lingering heredoc / secondary prompt state before we
    // try to inject fresh markers into the shell.
    await sendInterrupt();

    // Flush prior prompt/output before issuing a new command.
    await waitForPrompt().catch(() => {});
    await clearTerminal();
    const beforeSnapshot = await readTerminalText(activePage);
    const before = beforeSnapshot.text;

    // Use unique start/end markers and preserve literal newlines in the command.
    const token = `OC_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const startMarker = `__${token}_START__`;
    const endMarker = `__${token}_END__`;
    const wrappedCmd = `printf '${startMarker}\\n'; ${command}; printf '\\n${endMarker}\\n'`;

    const literalCommand = `${wrappedCmd}${wrappedCmd.endsWith('\n') ? '' : '\n'}`;
    await terminalInput.evaluate((element) => {
      element.value = '';
    }).catch(() => {});
    await activePage.keyboard.insertText(literalCommand);
    await activePage.keyboard.press('Enter');

    const deadline = Date.now() + waitMs;
    let after = '';
    let afterDebug = null;
    let sawStartMarker = false;
    let sawEndMarker = false;
    while (Date.now() < deadline) {
      await activePage.waitForTimeout(500);
      const snapshot = await readTerminalText(activePage);
      after = snapshot.text;
      afterDebug = snapshot.debug;
      sawStartMarker = sawStartMarker || after.includes(startMarker);
      sawEndMarker = sawEndMarker || after.includes(endMarker);
      if (sawEndMarker) {
        const stable = await waitForStableAfterEnd(endMarker);
        after = stable.text;
        afterDebug = stable.debug;
        break;
      }
    }

    if (!after.includes(startMarker) && !after.includes(endMarker)) {
      lastAttemptError = new Error(
        `Terminal never showed command markers on attempt ${attempt}; retrying command injection.`
      );
      await activePage.waitForTimeout(1000);
      continue;
    }

    let output = '';
    const afterLines = after.split('\n');
    const startLineIdx = afterLines.findIndex((line) => line.includes(startMarker));
    if (startLineIdx >= 0) {
      const candidateLines = [];
      for (let index = startLineIdx + 1; index < afterLines.length; index += 1) {
        const line = afterLines[index];
        if (line.includes(endMarker)) break;
        candidateLines.push(line);
      }
      output = candidateLines.join('\n');
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
    const wrapperRegex = new RegExp(`^.*printf '(?:${escapedStartMarker}\\n|\\n?${escapedEndMarker}\\n)'.*$`);
    const wrapperFragmentRegex = /^\\n';\s.*printf '\\$/;
    outputLines = output.split('\n').filter((line) => {
      const trimmed = line.trim();
      if (!trimmed) return false;
      if (promptLike.test(trimmed)) return false;
      if (line.includes(startMarker) || line.includes(endMarker)) return false;
      if (wrapperRegex.test(line) || wrapperFragmentRegex.test(line)) return false;
      if (trimmed === "'" || trimmed === ";" || trimmed === "n") return false;
      return true;
    });
    output = outputLines.join('\n').trim();

    return { before, after, output, debug: { before: beforeSnapshot.debug, after: afterDebug } };
  }

  throw lastAttemptError || new Error('Failed to inject command into Huanxin terminal after retries.');
}

async function main() {
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

  if (!standaloneAllowed) {
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
    const activePage = await openShell(page, envName);
    const { before, after, output, debug } = await sendCommand(activePage, command, waitMs);

    await activePage.screenshot({ path: `browser-automation/huanxin-shell-${envName}.png`, fullPage: true });
    console.log(
      JSON.stringify(
        {
          ok: true,
          envName,
          transport: 'standalone',
          browserMode: launch.browserMode,
          launchFallbackUsed: launch.fallbackUsed,
          url: activePage.url(),
          command,
          durationMs: Date.now() - startedAt,
          output: output || '',
          before,
          after,
          debug,
        },
        null,
        2
      )
    );
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
    process.exit(1);
  });
}
