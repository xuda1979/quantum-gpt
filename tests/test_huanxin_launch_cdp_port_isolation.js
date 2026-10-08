// Regression test for the 2026-09-18 environment-keeper fix.
//
// BUG: huanxin_browser_launch.js hardcoded `--remote-debugging-port=9224` in
// buildCommonLaunchOptions, so EVERY env's Chrome (ASI1/ASI2/ASI3) tried to
// bind ASI1's CDP port 9224. The second/third env's Chrome either failed to
// bind or stole ASI1's port -> "Target page, context or browser has been
// closed" crash -> ASI1/ASI3 could not stay up simultaneously. The keeper
// hands each env its own HUANXIN_CDP_PORT (ASI1=9224 ASI2=9225 ASI3=9226);
// the launch must honor it.
//
// This test asserts the per-env CDP port is wired through, with a 9224
// fallback when unset (preserves single-env behaviour).

const path = require('path');
const assert = require('assert');

const LAUNCH = path.join(__dirname, '..', 'browser-automation', 'huanxin_browser_launch.js');
const { buildCommonLaunchOptions } = require(LAUNCH);

function cdpPort(opts) {
  const arg = opts.args.find((a) => a.startsWith('--remote-debugging-port='));
  assert(arg, 'launch args must include --remote-debugging-port=');
  return Number(arg.split('=')[1]);
}

function test(name, fn) {
  try { fn(); console.log('PASS -', name); }
  catch (e) { console.log('FAIL -', name); console.log('  ', e.message); process.exitCode = 1; }
}

// use a throwaway profile dir (crashpad dir is created inside)
const os = require('os');
const fs = require('fs');
const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), 'hx-cdp-'));

test('ASI3 env uses HUANXIN_CDP_PORT=9226, NOT hardcoded 9224', () => {
  process.env.HUANXIN_CDP_PORT = '9226';
  const opts = buildCommonLaunchOptions(true, profileDir);
  assert.strictEqual(cdpPort(opts), 9226, 'ASI3 Chrome must bind 9226, not 9224');
});

test('ASI2 env uses HUANXIN_CDP_PORT=9225', () => {
  process.env.HUANXIN_CDP_PORT = '9225';
  const opts = buildCommonLaunchOptions(true, profileDir);
  assert.strictEqual(cdpPort(opts), 9225, 'ASI2 Chrome must bind 9225');
});

test('unset HUANXIN_CDP_PORT falls back to 9224 (single-env compat)', () => {
  delete process.env.HUANXIN_CDP_PORT;
  const opts = buildCommonLaunchOptions(true, profileDir);
  assert.strictEqual(cdpPort(opts), 9224, 'fallback must remain 9224');
});

test('per-env ports differ (isolation): 9224 vs 9225 vs 9226', () => {
  const ports = [];
  for (const p of ['9224', '9225', '9226']) {
    process.env.HUANXIN_CDP_PORT = p;
    ports.push(cdpPort(buildCommonLaunchOptions(true, profileDir)));
  }
  assert.deepStrictEqual(ports.sort(), [9224, 9225, 9226], 'each env must get a distinct CDP port');
});

if (process.exitCode) console.log('\nFAIL: CDP port isolation regressed'); else console.log('\nAll CDP port isolation tests passed');
