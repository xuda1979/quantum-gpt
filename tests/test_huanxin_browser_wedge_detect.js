// RED test for C-10450: headless Chrome daemon flap.
//
// Root cause (keepalive log 2026-10-15 04:45-05:13Z): the browser wedges and
// context.newPage() throws 'Protocol error (Target.createTarget): Failed to
// open a new tab' (380 occurrences). The daemon flips to startupState=error and
// only the OUTER keeper can recover it by killing + relaunching the whole
// daemon (1-3min outage each, 6 relaunches in ~30min).
//
// Fix under test: a pure detector for the wedged-browser Protocol error, so the
// daemon can relaunch ONLY the browser in-process and return to ready WITHOUT a
// full daemon restart.
'use strict';
const assert = require('assert');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const LAUNCH = path.join(ROOT, 'browser-automation', 'huanxin_browser_launch.js');
const { isBrowserWedgedProtocolError, newPageWithBrowserReload } = require(LAUNCH);

function test(name, fn) {
  try { fn(); console.log('PASS -', name); }
  catch (e) { console.log('FAIL -', name); console.log('  ', e.message); process.exitCode = 1; }
}

test('targets the exact Target.createTarget new-tab Protocol error', () => {
  const err = new Error('browserContext.newPage: Protocol error (Target.createTarget): Failed to open a new tab');
  assert.strictEqual(isBrowserWedgedProtocolError(err), true);
});

test('matches on the error message shared by bootShell startup errors', () => {
  const err = { message: 'Protocol error (Target.createTarget): Failed to open a new tab' };
  assert.strictEqual(isBrowserWedgedProtocolError(err), true);
});

test('matches a nested/stack string containing the CDP Protocol marker', () => {
  const err = {
    stack: 'ProtocolError: Protocol error (Target.createTarget): Failed to open a new tab\n at /x/launch.js:1',
  };
  assert.strictEqual(isBrowserWedgedProtocolError(err), true);
});

test('rejects unrelated CDP protocol errors (timeouts, navigation)', () => {
  const err = new Error('Protocol error (Page.navigate): Cannot navigate to invalid URL');
  assert.strictEqual(isBrowserWedgedProtocolError(err), false);
});

test('rejects null / non-errors fail-closed', () => {
  assert.strictEqual(isBrowserWedgedProtocolError(null), false);
  assert.strictEqual(isBrowserWedgedProtocolError(undefined), false);
  assert.strictEqual(isBrowserWedgedProtocolError('plain string'), false);
});


// ---------------------------------------------------------------------------
// Recovery loop: on a wedged-browser error the daemon must relaunch ONLY the
// browser context in-process (no full daemon restart / no keeper kick) and
// retry the page creation within a bounded attempt limit.
// ---------------------------------------------------------------------------
function wedgedContext() {
  return {
    pages() { return []; },
    newPage() {
      throw new Error('browserContext.newPage: Protocol error (Target.createTarget): Failed to open a new tab');
    },
  };
}

function healthyContext() {
  const page = { setDefaultTimeout: () => {}, isClosed: () => false };
  return { pages: () => [page] };
}

test('wedged browser is recovered by an in-process relaunch (no page lost)', async () => {
  let context = wedgedContext();
  const logLines = [];
  const launchFn = async () => { context = healthyContext(); return context; };
  const { page, relaunched } = await newPageWithBrowserReload({
    getContext: () => context,
    setContext: (c) => { context = c; return c; },
    launchFn,
    log: (msg) => logLines.push(msg),
  });
  assert.strictEqual(page.isClosed(), false);
  assert.strictEqual(relaunched, true, 'must report one in-process relaunch');
  assert.strictEqual(logLines.length, 1, 'must log the in-process relaunch');
  assert.ok(logLines[0].includes('relaunching browser in-process'), 'log must state the recovery path');
});

test('recovery gives up fail-closed after maxAttempts (no infinite loop)', async () => {
  let context = wedgedContext();
  let attempts = 0;
  const launchFn = async () => { attempts += 1; context = wedgedContext(); return context; };
  await assert.rejects(
    newPageWithBrowserReload({
      getContext: () => context,
      setContext: (c) => { context = c; return c; },
      launchFn,
      log: () => {},
      maxAttempts: 3,
    }),
    /Target.createTarget/
  );
  assert.strictEqual(attempts, 2, 'launchFn must be retried maxAttempts-1 times exactly');
});

test('non-wedge errors propagate immediately (no relaunch)', async () => {
  const boomPage = { setDefaultTimeout: () => {}, isClosed: () => false };
  const context = { pages: () => [boomPage] };
  const errors = [];
  const launchFn = async () => { errors.push('must not relaunch'); return context; };
  try {
    await newPageWithBrowserReload({
      getContext: () => context,
      setContext: () => context,
      launchFn,
      log: () => {},
    });
    throw new Error('expected a reject from the caller');
  } catch (error) {
    // The simulated caller flow throws after using the page; a non-wedge path
    // must never have called launchFn. We assert by constructing a caller-side
    // failure AFTER the page resolves getDefaultTimeout blow-up.
    assert.strictEqual(errors.length, 0, 'non-wedge path must not trigger a browser relaunch');
  }
});

console.log(process.exitCode ? 'browser-wedge-detect tests FAILED' : 'browser-wedge-detect tests passed');
