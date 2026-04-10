/**
 * Persistent Huanxin browser daemon.
 *
 * Launches the browser ONCE, opens the env shell, and keeps it alive.
 * Accepts commands via a local HTTP server so other scripts don't need
 * to launch/close the browser for every command.
 *
 * Usage:
 *   node huanxin_browser_daemon.js ai1 [--port 19001]
 *   node huanxin_browser_daemon.js ai2 [--port 19002]
 *
 * Then from any process:
 *   curl -s http://127.0.0.1:19001/exec -d '{"command":"ls"}'
 *   curl -s http://127.0.0.1:19001/health
 *   curl -s -X POST http://127.0.0.1:19001/stop
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { openShell, readTerminalText, sendCommand, focusTerminal } = require('./huanxin_shell_exec');

const ENV_PORTS = { ai1: 19001, ai2: 19002 };

function parseArgs(argv) {
  const args = { env: null, port: null };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--port') {
      args.port = parseInt(argv[++i], 10);
    } else if (argv[i] === '--env') {
      args.env = argv[++i];
    } else if (!args.env && !argv[i].startsWith('-')) {
      args.env = argv[i];
    }
  }
  if (!args.env) {
    console.error('Usage: node huanxin_browser_daemon.js <env> [--port <port>]');
    process.exit(1);
  }
  if (!args.port) args.port = ENV_PORTS[args.env] || 19000;
  return args;
}

function pidFile(env) {
  return `/tmp/huanxin-daemon-${env}.pid`;
}
function portFile(env) {
  return `/tmp/huanxin-daemon-${env}.port`;
}
function fileTransportDir(env) {
  return `/tmp/huanxin-daemon-${env}.ipc`;
}
function ensureFileTransportDir(env) {
  const dir = fileTransportDir(env);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

// Simple mutex so concurrent HTTP requests don't interleave terminal input
let busy = false;
let busySinceMs = null;
let busyLabel = null;
const waiting = [];
async function withLock(fn, label = 'exec') {
  if (busy) {
    await new Promise((resolve) => waiting.push(resolve));
  }
  busy = true;
  busySinceMs = Date.now();
  busyLabel = label;
  try {
    return await fn();
  } finally {
    busy = false;
    busySinceMs = null;
    busyLabel = null;
    if (waiting.length > 0) waiting.shift()();
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  // Check for existing daemon
  const pf = pidFile(args.env);
  if (fs.existsSync(pf)) {
    const oldPid = parseInt(fs.readFileSync(pf, 'utf8').trim(), 10);
    try {
      process.kill(oldPid, 0);
      console.error(
        `Daemon for ${args.env} already running (PID ${oldPid}). Kill it first: kill ${oldPid}`
      );
      process.exit(1);
    } catch {
      // stale pid file
    }
  }

  const { profileDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;
  const ipcDir = ensureFileTransportDir(args.env);

  async function ensureLauncherPage() {
    let candidate = context.pages().find((page) => !page.isClosed()) || null;
    if (!candidate) {
      candidate = await context.newPage();
    }
    candidate.setDefaultTimeout(30000);
    return candidate;
  }

  let launcherPage = null;
  let activePage = null;
  let startupState = 'booting';
  let startupError = null;
  let startupPromise = null;

  async function bootShell() {
    startupState = 'booting';
    startupError = null;
    try {
      launcherPage = await ensureLauncherPage();
      activePage = await openShell(launcherPage, args.env);
      startupState = 'ready';
      startupError = null;
      return activePage;
    } catch (err) {
      startupState = 'error';
      startupError = err.message;
      console.error('Failed to open shell:', err.message);
      throw err;
    } finally {
      startupPromise = null;
    }
  }

  function startBoot() {
    if (!startupPromise) {
      startupPromise = bootShell();
    }
    return startupPromise;
  }

  async function ensureReady() {
    let lastError = null;
    for (let attempt = 1; attempt <= 2; attempt += 1) {
      if (startupState === 'ready' && activePage && !activePage.isClosed()) {
        return;
      }
      try {
        await startBoot();
        return;
      } catch (error) {
        lastError = error;
        if (attempt < 2) {
          await new Promise((resolve) => setTimeout(resolve, 1500));
        }
      }
    }
    throw lastError || new Error(`Failed to initialize shell for ${args.env}`);
  }

  const startTime = Date.now();
  let lastActivity = Date.now();
  let commandCount = 0;
  let lastCommand = null;
  let lastCommandStartedAt = null;
  let lastCommandCompletedAt = null;
  let lastCommandDurationMs = null;

  async function reopenShell(reason) {
    console.error(reason);
    try {
      if (activePage && !activePage.isClosed()) {
        await activePage.close().catch(() => {});
      }
    } catch {}
    startupState = 'booting';
    startupError = null;
    launcherPage = await ensureLauncherPage();
    activePage = await openShell(launcherPage, args.env);
    startupState = 'ready';
    startupError = null;
  }

  // Attempt to re-open shell if the page went stale or disconnected
  async function ensureShell() {
    await ensureReady();
    try {
      const text = (await readTerminalText(activePage)).text;
      const disconnected = text.includes('Terminal long time idle, disconnect') ||
        (text.includes('disconnect') && text.trim().endsWith('disconnect.'));
      if (disconnected) {
        await reopenShell('[daemon] Terminal disconnected (idle), re-opening shell...');
      }
    } catch {
      await reopenShell('[daemon] Shell stale, re-opening...');
    }
  }

  // Write state files
  fs.writeFileSync(pf, String(process.pid));
  fs.writeFileSync(portFile(args.env), String(args.port));
  fs.writeFileSync(
    path.join(ipcDir, 'daemon.json'),
    JSON.stringify(
      {
        ok: true,
        env: args.env,
        pid: process.pid,
        profileDir,
        browserMode: launch.browserMode,
        launchFallbackUsed: launch.fallbackUsed,
        startedAt: new Date().toISOString(),
      },
      null,
      2
    )
  );

  async function runCommand(command, wait) {
    const result = await withLock(async () => {
      await ensureReady();
      await ensureShell();
      lastActivity = Date.now();
      commandCount++;
      lastCommand = command;
      lastCommandStartedAt = new Date().toISOString();
      const startedAtMs = Date.now();
      const { before, after, output, debug } = await sendCommand(activePage, command, wait);
      lastCommandCompletedAt = new Date().toISOString();
      lastCommandDurationMs = Date.now() - startedAtMs;

      await activePage
        .screenshot({
          path: path.resolve(__dirname, `huanxin-shell-${args.env}.png`),
          fullPage: true,
        })
        .catch(() => {});

      return {
        ok: true,
        envName: args.env,
        browserMode: launch.browserMode,
        launchFallbackUsed: launch.fallbackUsed,
        url: activePage.url(),
        command,
        output: output || '',
        before,
        after,
        debug,
        durationMs: lastCommandDurationMs,
        startedAt: lastCommandStartedAt,
        completedAt: lastCommandCompletedAt,
      };
    }, 'exec');
    return result;
  }

  let fileLoopBusy = false;
  async function pollFileTransport() {
    if (fileLoopBusy) return;
    fileLoopBusy = true;
    try {
      const entries = fs
        .readdirSync(ipcDir, { withFileTypes: true })
        .filter((entry) => entry.isFile() && entry.name.endsWith('.request.json'))
        .sort((a, b) => a.name.localeCompare(b.name));
      for (const entry of entries) {
        const requestPath = path.join(ipcDir, entry.name);
        const claimPath = requestPath.replace(/\.request\.json$/, '.processing.json');
        try {
          fs.renameSync(requestPath, claimPath);
        } catch {
          continue;
        }
        const responsePath = claimPath.replace(/\.processing\.json$/, '.response.json');
        try {
          const raw = fs.readFileSync(claimPath, 'utf8');
          const parsed = JSON.parse(raw);
          const result = await runCommand(String(parsed.command || ''), Number(parsed.waitMs || 30000));
          fs.writeFileSync(responsePath, JSON.stringify(result, null, 2));
        } catch (err) {
          fs.writeFileSync(responsePath, JSON.stringify({ ok: false, error: err.message }, null, 2));
        } finally {
          try {
            fs.unlinkSync(claimPath);
          } catch {}
        }
      }
    } finally {
      fileLoopBusy = false;
    }
  }

  const fileLoop = setInterval(() => {
    pollFileTransport().catch(() => {});
  }, 500);

  function readBody(req) {
    return new Promise((resolve) => {
      let data = '';
      req.on('data', (chunk) => (data += chunk));
      req.on('end', () => resolve(data));
    });
  }

  const server = http.createServer(async (req, res) => {
    res.setHeader('Content-Type', 'application/json');

    if (req.method === 'GET' && req.url === '/health') {
      res.end(
        JSON.stringify({
          ok: true,
          ready: startupState === 'ready',
          startupState,
          startupError,
          env: args.env,
          pid: process.pid,
          port: args.port,
          uptime: Math.round((Date.now() - startTime) / 1000),
          commandCount,
          lastActivity: new Date(lastActivity).toISOString(),
          lastCommand,
          lastCommandStartedAt,
          lastCommandCompletedAt,
          lastCommandDurationMs,
          busy,
          busyAgeMs: busySinceMs === null ? 0 : Math.max(0, Date.now() - busySinceMs),
          busyLabel,
          pendingRequestCount: waiting.length,
          currentUrl:
            activePage && !activePage.isClosed()
              ? activePage.url()
              : launcherPage && !launcherPage.isClosed()
                ? launcherPage.url()
                : null,
          browserMode: launch.browserMode,
          launchFallbackUsed: launch.fallbackUsed,
        })
      );
      return;
    }

    if (req.method === 'POST' && req.url === '/exec') {
      const body = await readBody(req);
      let parsed;
      try {
        parsed = JSON.parse(body);
      } catch {
        res.statusCode = 400;
        res.end(JSON.stringify({ ok: false, error: 'invalid JSON' }));
        return;
      }

      const { command, waitMs, timeout } = parsed;
      const wait = waitMs || timeout || 30000;
      if (!command) {
        res.statusCode = 400;
        res.end(JSON.stringify({ ok: false, error: 'missing command' }));
        return;
      }

      try {
        const result = await runCommand(command, wait);
        res.end(JSON.stringify(result, null, 2));
      } catch (err) {
        res.statusCode = 500;
        res.end(JSON.stringify({ ok: false, error: err.message }));
      }
      return;
    }

    if (req.method === 'POST' && req.url === '/stop') {
      res.end(JSON.stringify({ ok: true, message: 'shutting down' }));
      cleanup();
      setTimeout(() => process.exit(0), 500);
      return;
    }

    if (req.method === 'GET' && req.url === '/terminal') {
      try {
        const text = await withLock(async () => {
          await ensureReady();
          return (await readTerminalText(activePage)).text;
        }, 'terminal');
        res.end(JSON.stringify({ ok: true, terminal: text }));
      } catch (err) {
        res.statusCode = 500;
        res.end(JSON.stringify({ ok: false, error: err.message }));
      }
      return;
    }

    res.statusCode = 404;
    res.end(JSON.stringify({ ok: false, error: 'not found' }));
  });

  server.listen(args.port, '127.0.0.1', () => {
    const info = {
      ok: true,
      daemon: true,
      env: args.env,
      port: args.port,
      pid: process.pid,
      profileDir,
      browserMode: launch.browserMode,
      launchFallbackUsed: launch.fallbackUsed,
    };
    console.log(JSON.stringify(info, null, 2));
    startBoot().catch(() => {});
  });

  function cleanup() {
    clearInterval(fileLoop);
    try {
      fs.unlinkSync(pf);
    } catch {}
    try {
      fs.unlinkSync(portFile(args.env));
    } catch {}
    try {
      fs.rmSync(ipcDir, { recursive: true, force: true });
    } catch {}
    context.close().catch(() => {});
    server.close();
  }

  process.on('SIGTERM', () => {
    cleanup();
    process.exit(0);
  });
  process.on('SIGINT', () => {
    cleanup();
    process.exit(0);
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
