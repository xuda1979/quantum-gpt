// TDD: huanxin /exec wedge fixes (2026-08-27 infra mission — debug lane #21).
// The recurring wedge: page.evaluate/keyboard calls have NO timeout; a
// renderer stall wedges withLock's busy=true forever (health stays green).
// Ranked fixes under test:
//   (1) readTerminalText bounded to the last N rows
//   (2) per-call timeouts via Promise.race on evaluate/keyboard
//   (3) exec-side hard deadline around sendCommand with a structured error
//   (4) stuck-lock watchdog in withLock (busyAgeMs > N -> force-release +
//       reopen)
// A simulated stall must NOT wedge: every path below resolves or rejects
// within a bounded time.
'use strict';
const assert = require('assert');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SHELL_EXEC = path.join(ROOT, 'browser-automation', 'huanxin_shell_exec.js');
const DAEMON = path.join(ROOT, 'browser-automation', 'huanxin_browser_daemon.js');

// ---------------------------------------------------------------------------
// Fixtures: a fake page whose I/O can hang (the renderer-stall simulation)
// ---------------------------------------------------------------------------
function makeStalledPage({ hangEvaluate = true, hangAll = false } = {}) {
  const hang = () => new Promise(() => {});
  const ok = async () => undefined;
  const locator = () => ({
    waitFor: hangAll ? hang : ok,
    click: hangAll ? hang : ok,
    type: hangAll ? hang : ok,
    evaluate: hangEvaluate ? hang : ok,
    first: () => locator(),
  });
  return {
    evaluate: hangEvaluate ? hang : ok,
    keyboard: {
      insertText: hangAll ? hang : ok,
      type: hangAll ? hang : ok,
      press: hangAll ? hang : ok,
    },
    locator,
    waitForTimeout: async () => {},
  };
}

function bounded(promise, ms, label) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error(`TEST HANG: ${label} exceeded ${ms}ms`)), ms);
    promise.then(
      (v) => { clearTimeout(t); resolve(v); },
      (e) => { clearTimeout(t); reject(e); }
    );
  });
}

let failures = 0;
function check(name, fn) {
  return bounded(Promise.resolve().then(fn), 15000, name).then(
    () => console.log(`ok - ${name}`),
    (err) => { failures += 1; console.log(`FAIL - ${name}: ${err && err.message}`); }
  );
}

async function main() {
  // -------------------------------------------------------------------------
  // (1) readTerminalText bounded to the last N rows
  // -------------------------------------------------------------------------
  await check('readTerminalText bounds output to the last N rows', async () => {
    process.env.HUANXIN_TERMINAL_MAX_LINES = '50';
    delete require.cache[require.resolve(SHELL_EXEC)];
    const { readTerminalText } = require(SHELL_EXEC);
    // fake DOM: a terminal with 600 rows; the evaluate closure runs in node
    const fakeRows = {
      children: Array.from({ length: 600 }, (_, i) => ({ textContent: `row-${i}` })),
    };
    global.document = {
      querySelector: () => fakeRows,
      activeElement: null,
    };
    try {
      const page = {
        evaluate: async (fn, arg) => fn({ maxLines: arg.maxLines }),
        locator: () => ({ waitFor: async () => {}, click: async () => {}, first: () => ({}) }),
        keyboard: { insertText: async () => {}, type: async () => {}, press: async () => {} },
        waitForTimeout: async () => {},
      };
      const result = await readTerminalText(page);
      const outLines = result.text.split('\n');
      assert.strictEqual(outLines.length, 50, `got ${outLines.length} lines`);
      assert.strictEqual(outLines[outLines.length - 1], 'row-599'); // the NEWEST rows
      assert.strictEqual(result.debug.maxLines, 50);
    } finally {
      delete global.document;
      delete process.env.HUANXIN_TERMINAL_MAX_LINES;
    }
  });

  // -------------------------------------------------------------------------
  // (2) per-call timeout: a stalled evaluate rejects with HUANXIN_TIMEOUT
  // -------------------------------------------------------------------------
  await check('readTerminalText on a stalled page rejects bounded (HUANXIN_TIMEOUT)', async () => {
    process.env.HUANXIN_PAGE_IO_TIMEOUT_MS = '300';
    delete require.cache[require.resolve(SHELL_EXEC)];
    const { readTerminalText } = require(SHELL_EXEC);
    const page = makeStalledPage({ hangEvaluate: true });
    const started = Date.now();
    let code = null;
    try {
      await bounded(readTerminalText(page), 5000, 'readTerminalText-stall');
    } catch (err) {
      code = err.code;
    }
    const elapsed = Date.now() - started;
    assert.strictEqual(code, 'HUANXIN_TIMEOUT', `got code ${code}`);
    assert(elapsed < 5000, `took ${elapsed}ms (unbounded)`);
    delete process.env.HUANXIN_PAGE_IO_TIMEOUT_MS;
  });

  // -------------------------------------------------------------------------
  // (3) exec-side hard deadline: sendCommand rejects structured, bounded
  // -------------------------------------------------------------------------
  await check('sendCommand on a fully stalled page rejects with HUANXIN_EXEC_DEADLINE', async () => {
    process.env.HUANXIN_PAGE_IO_TIMEOUT_MS = '5000'; // per-call guard LONGER than the deadline
    process.env.HUANXIN_EXEC_HARD_DEADLINE_MS = '600'; // the hard deadline fires first
    delete require.cache[require.resolve(SHELL_EXEC)];
    const { sendCommand } = require(SHELL_EXEC);
    const page = makeStalledPage({ hangEvaluate: true, hangAll: true });
    const started = Date.now();
    let code = null;
    try {
      await bounded(sendCommand(page, 'echo hi', 200), 10000, 'sendCommand-stall');
    } catch (err) {
      code = err.code;
    }
    const elapsed = Date.now() - started;
    assert.strictEqual(code, 'HUANXIN_EXEC_DEADLINE', `got code ${code}`);
    assert(elapsed < 10000 && elapsed > 400, `took ${elapsed}ms`);
    delete process.env.HUANXIN_PAGE_IO_TIMEOUT_MS;
    delete process.env.HUANXIN_EXEC_HARD_DEADLINE_MS;
  });

  // -------------------------------------------------------------------------
  // (4) withLock stuck-lock watchdog: force-release + reopen callback
  // -------------------------------------------------------------------------
  await check('withLock watchdog force-releases a stuck lock and reopens', async () => {
    process.env.HUANXIN_LOCK_MAX_AGE_MS = '300';
    delete require.cache[require.resolve(DAEMON)];
    const daemon = require(DAEMON);
    let reopenCalls = 0;
    let reopenReason = null;
    daemon._resetLockStateForTests();
    daemon.setLockWatchdogReopen((reason) => {
      reopenCalls += 1;
      reopenReason = reason;
    });
    const stuck = () => new Promise(() => {}); // never resolves (the wedge)
    const first = daemon.withLock(stuck, 'exec-stuck');
    await new Promise((resolve) => setTimeout(resolve, 150)); // holder acquired
    // second caller must NOT wait forever: the watchdog force-releases
    const secondStart = Date.now();
    const second = await bounded(
      daemon.withLock(async () => 'second-ran', 'exec-second'),
      5000,
      'withLock-second'
    );
    const secondElapsed = Date.now() - secondStart;
    assert.strictEqual(second, 'second-ran');
    assert(secondElapsed < 5000, `second caller waited ${secondElapsed}ms`);
    assert.strictEqual(reopenCalls, 1, `reopen called ${reopenCalls} times`);
    assert(reopenReason && reopenReason.includes('force-released'), reopenReason);
    // the abandoned fn's late completion must not corrupt the lock
    await new Promise((resolve) => setTimeout(resolve, 100));
    const third = await bounded(
      daemon.withLock(async () => 'third-ran', 'exec-third'),
      2000,
      'withLock-third'
    );
    assert.strictEqual(third, 'third-ran');
    delete process.env.HUANXIN_LOCK_MAX_AGE_MS;
  });

  if (failures > 0) {
    console.error(`\n${failures} test(s) FAILED`);
    process.exit(1);
  }
  console.log('\nall wedge-fix tests passed');
  process.exit(0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
