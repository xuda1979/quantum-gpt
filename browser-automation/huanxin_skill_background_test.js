const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync, spawn } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const DEFAULT_ENV = 'AI';

function stripShellQuotes(value) {
  const text = String(value || '').trim();
  if (
    (text.startsWith("'") && text.endsWith("'")) ||
    (text.startsWith('"') && text.endsWith('"'))
  ) {
    return text.slice(1, -1);
  }
  return text;
}

function loadEnvFileIfPresent(filePath) {
  if (!fs.existsSync(filePath)) {
    return;
  }
  const text = fs.readFileSync(filePath, 'utf8');
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) {
      continue;
    }
    const match = line.match(/^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!match) {
      continue;
    }
    const [, key, rawValue] = match;
    if (process.env[key]) {
      continue;
    }
    process.env[key] = stripShellQuotes(rawValue);
  }
}

function loadHuanxinSecrets() {
  for (const filePath of [
    path.join(ROOT_DIR, '.huanxin_login.env'),
    path.join(ROOT_DIR, '.huanxin.env'),
    path.join(os.homedir(), '.codex', 'secrets', 'huanxin.env'),
  ]) {
    loadEnvFileIfPresent(filePath);
  }
}

function resolveTrainDevUrl(envName, explicitUrl) {
  if (explicitUrl) {
    return explicitUrl;
  }
  if (process.env.HUANXIN_TRAIN_DEV_URL) {
    return process.env.HUANXIN_TRAIN_DEV_URL;
  }
  try {
    return execFileSync(
      'python3',
      ['scripts/huanxin_env_config.py', '--env', envName, '--field', 'train_dev_url'],
      { cwd: ROOT_DIR, encoding: 'utf8' }
    ).trim();
  } catch {
    return '';
  }
}

function parseArgs(argv) {
  const args = {
    envName: process.env.HUANXIN_TEST_ENV || DEFAULT_ENV,
    jobId: process.env.HUANXIN_SKILL_TEST_JOB_ID || `huanxin-skill-test-${new Date().toISOString().replace(/[-:.]/g, '').slice(0, 15)}Z`,
    waitMs: Number(process.env.HUANXIN_TEST_WAIT_MS || 180000),
    mode: process.env.HUANXIN_SKILL_TEST_MODE || 'full',
    url: process.env.HUANXIN_TRAIN_DEV_URL || '',
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--env') {
      args.envName = argv[++index];
      continue;
    }
    if (token === '--job-id') {
      args.jobId = argv[++index];
      continue;
    }
    if (token === '--wait-ms') {
      args.waitMs = Number(argv[++index]);
      continue;
    }
    if (token === '--mode') {
      args.mode = argv[++index];
      continue;
    }
    if (token === '--url') {
      args.url = argv[++index];
      continue;
    }
    throw new Error(`Unknown argument: ${token}`);
  }

  if (!args.jobId || /[^a-zA-Z0-9._-]/.test(args.jobId)) {
    throw new Error('job id must contain only letters, numbers, dot, underscore, or dash');
  }
  if (!Number.isFinite(args.waitMs) || args.waitMs <= 0) {
    throw new Error('wait-ms must be a positive number');
  }
  if (!['full', 's3-only'].includes(args.mode)) {
    throw new Error('mode must be one of: full, s3-only');
  }
  args.url = resolveTrainDevUrl(args.envName, args.url);
  return args;
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function nowIso() {
  return new Date().toISOString();
}

function truncate(value, maxChars = 20000) {
  const text = String(value || '');
  if (text.length <= maxChars) return text;
  return `${text.slice(0, maxChars)}\n...[truncated ${text.length - maxChars} chars]`;
}

function redactors() {
  return [
    process.env.HUANXIN_LOGIN_PASSWORD,
    process.env.HUANXIN_LOGIN_PHONE,
    process.env.INER_SECRET_ACCESS_KEY,
  ].filter(Boolean);
}

function redact(text) {
  let out = String(text || '');
  for (const secret of redactors()) {
    out = out.split(secret).join('[REDACTED]');
  }
  return out;
}

class State {
  constructor(paths, args) {
    this.paths = paths;
    this.payload = {
      ok: false,
      state: 'running',
      jobId: args.jobId,
      envName: args.envName,
      mode: args.mode,
      trainDevUrl: args.url,
      rootDir: ROOT_DIR,
      startedAt: nowIso(),
      completedAt: null,
      currentStep: null,
      steps: [],
      artifacts: {
        jobDir: paths.jobDir,
        logPath: paths.logPath,
        statePath: paths.statePath,
      },
    };
    this.write();
  }

  log(line) {
    fs.appendFileSync(this.paths.logPath, `${nowIso()} ${redact(line)}\n`);
  }

  write() {
    fs.writeFileSync(this.paths.statePath, `${JSON.stringify(this.payload, null, 2)}\n`);
  }

  startStep(name) {
    const step = { name, state: 'running', startedAt: nowIso(), completedAt: null };
    this.payload.currentStep = name;
    this.payload.steps.push(step);
    this.log(`[step:start] ${name}`);
    this.write();
    return step;
  }

  finishStep(step, update = {}) {
    Object.assign(step, update, { state: update.state || 'ok', completedAt: nowIso() });
    this.log(`[step:${step.state}] ${step.name}`);
    this.write();
  }

  failStep(step, error, update = {}) {
    Object.assign(step, update, {
      state: 'failed',
      completedAt: nowIso(),
      error: redact(error && (error.stack || error.message || String(error))),
    });
    this.payload.state = 'failed';
    this.payload.currentStep = step.name;
    this.log(`[step:failed] ${step.name}: ${step.error}`);
    this.write();
  }

  complete(ok) {
    this.payload.ok = Boolean(ok);
    this.payload.state = ok ? 'completed' : 'failed';
    this.payload.currentStep = null;
    this.payload.completedAt = nowIso();
    this.write();
  }
}

function runCommand(command, args, options = {}) {
  const startedAt = Date.now();
  const timeoutMs = options.timeoutMs || 300000;
  const chromeApp = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  const env = {
    ...process.env,
    HUANXIN_ALLOW_HEADED_FALLBACK: process.env.HUANXIN_ALLOW_HEADED_FALLBACK || '1',
    HUANXIN_BROWSER_EXECUTABLE_PATH:
      process.env.HUANXIN_BROWSER_EXECUTABLE_PATH || (fs.existsSync(chromeApp) ? chromeApp : ''),
    ...(options.env || {}),
  };
  const cwd = options.cwd || ROOT_DIR;

  return new Promise((resolve) => {
    const child = spawn(command, args, { cwd, env, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill('SIGTERM');
      setTimeout(() => child.kill('SIGKILL'), 3000).unref();
    }, timeoutMs);

    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });
    child.on('close', (code, signal) => {
      clearTimeout(timer);
      resolve({
        ok: code === 0 && !timedOut,
        code,
        signal,
        timedOut,
        durationMs: Date.now() - startedAt,
        stdout: truncate(redact(stdout)),
        stderr: truncate(redact(stderr)),
      });
    });
  });
}

function parseJsonFromOutput(output) {
  const text = String(output || '').trim();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {}

  const start = text.indexOf('{');
  const end = text.lastIndexOf('}');
  if (start >= 0 && end > start) {
    try {
      return JSON.parse(text.slice(start, end + 1));
    } catch {}
  }
  return null;
}

async function checkedStep(state, name, fn) {
  const step = state.startStep(name);
  try {
    const result = await fn(step);
    if (result && result.ok === false) {
      const error = new Error(result.message || result.error || `${name} returned ok=false`);
      state.failStep(step, error, result);
      throw error;
    }
    state.finishStep(step, result || {});
    return result;
  } catch (error) {
    if (step.state !== 'failed') {
      state.failStep(step, error);
    }
    throw error;
  }
}

function commandSummary(result, includeStdout = true) {
  return {
    ok: result.ok,
    code: result.code,
    signal: result.signal,
    timedOut: result.timedOut,
    durationMs: result.durationMs,
    stdout: includeStdout ? result.stdout : truncate(result.stdout, 3000),
    stderr: truncate(result.stderr, 6000),
  };
}

function classifyFailure(result) {
  const text = `${result.stderr || ''}\n${result.stdout || ''}`;
  if (
    text.includes('Crashpad') ||
    text.includes('Operation not permitted') ||
    text.includes('bootstrap_check_in') ||
    text.includes('signal=SIGTRAP') ||
    text.includes('Target page, context or browser has been closed')
  ) {
    return 'browser_launch_blocked';
  }
  if (text.includes('lookup iner.aihuanxin.cn') || text.includes('no such host')) {
    return 's3_dns_blocked';
  }
  if (text.includes('AccessDenied')) {
    return 's3_access_denied';
  }
  if (text.includes('captcha_required')) {
    return 'captcha_required';
  }
  if (text.includes('login_required') || text.includes('密码登录') || text.includes('短信登录')) {
    return 'login_required';
  }
  return result.ok ? null : 'command_failed';
}

async function probeSession(state, args, label) {
  const probePath = path.join(state.paths.jobDir, `${label}.probe.json`);
  const htmlPath = path.join(state.paths.jobDir, `${label}.probe.html`);
  const pngPath = path.join(state.paths.jobDir, `${label}.probe.png`);
  const result = await runCommand(
    'node',
    [
      'browser-automation/huanxin_probe.js',
      '--url',
      args.url,
      '--dump-json',
      probePath,
      '--dump-html',
      htmlPath,
      '--screenshot',
      pngPath,
    ],
    { timeoutMs: 240000, env: { HUANXIN_TRAIN_DEV_URL: args.url } }
  );
  const parsed = fs.existsSync(probePath) ? JSON.parse(fs.readFileSync(probePath, 'utf8')) : parseJsonFromOutput(result.stdout);
  return {
    ...commandSummary(result, false),
    failureKind: classifyFailure(result),
    probeState: parsed && parsed.state,
    probeUrl: parsed && parsed.url,
    probeJson: probePath,
    probeHtml: htmlPath,
    probeScreenshot: pngPath,
  };
}

async function ensureLogin(state, args) {
  const first = await probeSession(state, args, 'initial');
  if (first.probeState && first.probeState !== 'login_required') {
    return { ...first, loginAction: 'not_needed' };
  }

  const repair = await runCommand('bash', ['scripts/repair_huanxin_browser_profile.sh', '--wait-ms', '45000'], {
    timeoutMs: 300000,
    env: {
      HUANXIN_TRAIN_DEV_URL: args.url,
      HUANXIN_ALLOW_SAFARI_SSO_BRIDGE: '1',
      HUANXIN_ALLOW_HEADED_FALLBACK: '1',
      HUANXIN_PROFILE_REPAIR_RESULT_PATH: path.join(state.paths.jobDir, 'profile-repair.json'),
      HUANXIN_PROFILE_REPAIR_STATE_PATH: path.join(state.paths.jobDir, 'profile-repair-state.json'),
    },
  });
  const repairParsed = parseJsonFromOutput(repair.stdout) || {};
  if (repair.ok || repairParsed.ok) {
    const afterRepair = await probeSession(state, args, 'post-repair');
    if (afterRepair.probeState && afterRepair.probeState !== 'login_required') {
      return {
        ...afterRepair,
        loginAction: 'safari_sso_repair',
        repair: commandSummary(repair, false),
      };
    }
  }

  const hasCredentials = Boolean(process.env.HUANXIN_LOGIN_PHONE && process.env.HUANXIN_LOGIN_PASSWORD);
  if (!hasCredentials) {
    return {
      ...first,
      ok: false,
      state: 'needs_credentials',
      failureKind: 'login_required',
      loginAction: 'auto_login_failed_missing_credentials',
      message:
        'Auto-login could not authenticate ASI1: Safari SSO repair did not capture a callback, and HUANXIN_LOGIN_PHONE/HUANXIN_LOGIN_PASSWORD are not available.',
      repair: commandSummary(repair, false),
      repairState: repairParsed.state || repairParsed.finalUrlState || repairParsed.mode || null,
      repairMessage: repairParsed.message || repairParsed.mode || null,
    };
  }

  const login = await runCommand(
    'node',
    ['browser-automation/huanxin_password_login.js', '--timeout', '180', '--url', args.url],
    { timeoutMs: 300000, env: { HUANXIN_TRAIN_DEV_URL: args.url } }
  );
  const loginParsed = parseJsonFromOutput(login.stdout) || {};
  if (!login.ok || loginParsed.state === 'captcha_required') {
    return {
      ...commandSummary(login, false),
      failureKind: classifyFailure(login),
      state: loginParsed.state || 'login_failed',
      loginAction: 'password_login_failed',
      captchaImage: loginParsed.captchaImage,
      message: loginParsed.message,
    };
  }

  const second = await probeSession(state, args, 'post-login');
  return { ...second, loginAction: 'password_login', loginState: loginParsed.state };
}

async function uploadProbeToS3(state, args) {
  const probeDir = path.join(state.paths.jobDir, 's3-probe');
  ensureDir(probeDir);
  const probePath = path.join(probeDir, 'probe.txt');
  const content = [
    `job_id=${args.jobId}`,
    `env=${args.envName}`,
    `timestamp=${nowIso()}`,
    'payload=huanxin-s3-background-skill-test',
    '',
  ].join('\n');
  fs.writeFileSync(probePath, content, 'utf8');

const script = `
set -euo pipefail
source scripts/iner_s3_env.sh
cfg="$(mktemp "\${TMPDIR:-/tmp}/iner-rclone.XXXXXX.conf")"
trap 'rm -f "$cfg"' EXIT
iner_write_rclone_config "$cfg"
dest_root="\${INER_S3_ROOT%/}/.skill-test/\${HUANXIN_SKILL_TEST_JOB_ID}"
rclone copyto "$HUANXIN_SKILL_TEST_PROBE" "$dest_root/probe.txt" --config "$cfg" --s3-no-check-bucket --no-traverse
rclone cat "$dest_root/probe.txt" --config "$cfg" --s3-no-check-bucket
`;
  const result = await runCommand('bash', ['-lc', script], {
    timeoutMs: 180000,
    env: {
      HUANXIN_SKILL_TEST_JOB_ID: args.jobId,
      HUANXIN_SKILL_TEST_PROBE: probePath,
    },
  });

  return {
    ...commandSummary(result),
    failureKind: classifyFailure(result),
    localProbe: probePath,
    s3RootSuffix: `.skill-test/${args.jobId}`,
    verifiedCatContainsJobId: result.stdout.includes(args.jobId),
  };
}

async function syncProbeFromS3ToAI(state, args) {
  const remoteRoot = `/root/software/huanxin-skill-test/${args.jobId}`;
  const result = await runCommand('bash', ['scripts/ai_sync_from_s3.sh'], {
    timeoutMs: 420000,
    env: {
      HUANXIN_WAIT_MS: String(args.waitMs),
      HUANXIN_S3_ROOT: `iner:software/quantum-gpt/.skill-test/${args.jobId}`,
      AI_REMOTE_ROOT: remoteRoot,
      HUANXIN_USE_DAEMON: '1',
      HUANXIN_ALLOW_STANDALONE_FALLBACK: '0',
    },
  });
  return {
    ...commandSummary(result, false),
    failureKind: classifyFailure(result),
    remoteRoot,
  };
}

async function runRemoteCommand(state, args) {
  const remoteRoot = `/root/software/huanxin-skill-test/${args.jobId}`;
  const marker = `__HX_SKILL_TEST_${args.jobId.replace(/[^A-Za-z0-9]/g, '_')}__`;
  const command = [
    `cd '${remoteRoot}'`,
    `printf '${marker}\\n'`,
    'pwd',
    'whoami',
    'test -f probe.txt',
    'cat probe.txt',
  ].join(' && ');
  const result = await runCommand('bash', ['scripts/huanxin_shell.sh', args.envName, command], {
    timeoutMs: 300000,
    env: {
      HUANXIN_WAIT_MS: String(args.waitMs),
      HUANXIN_USE_DAEMON: '1',
      HUANXIN_ALLOW_STANDALONE_FALLBACK: '0',
    },
  });
  return {
    ...commandSummary(result, false),
    failureKind: classifyFailure(result),
    remoteRoot,
    marker,
    markerObserved: result.stdout.includes(marker),
    probeContentObserved: result.stdout.includes('huanxin-s3-background-skill-test'),
  };
}

async function main() {
  loadHuanxinSecrets();
  const args = parseArgs(process.argv.slice(2));
  const jobDir = path.join(ROOT_DIR, '.huanxin_jobs', args.jobId);
  ensureDir(jobDir);
  const paths = {
    jobDir,
    statePath: path.join(jobDir, 'state.json'),
    logPath: path.join(jobDir, 'runner.log'),
  };
  const state = new State(paths, args);

  try {
    if (args.mode === 's3-only') {
      await checkedStep(state, 'local_to_s3_probe_upload', async () => uploadProbeToS3(state, args));
      const failed = state.payload.steps.some((step) => step.state === 'failed' || step.ok === false);
      const missingEvidence = state.payload.steps.some(
        (step) => Object.prototype.hasOwnProperty.call(step, 'verifiedCatContainsJobId') && !step.verifiedCatContainsJobId
      );
      state.complete(!failed && !missingEvidence);
      if (failed || missingEvidence) {
        process.exitCode = 1;
      }
      return;
    }

    await checkedStep(state, 'login_or_session_probe', async () => ensureLogin(state, args));

    const loginStep = state.payload.steps.find((step) => step.name === 'login_or_session_probe');
    if (loginStep && ['needs_credentials', 'captcha_required', 'login_failed'].includes(loginStep.state)) {
      throw new Error(`Cannot continue without authenticated Huanxin session: ${loginStep.state}`);
    }

    await checkedStep(state, 'remote_env_start_and_shell_probe', async () => {
      const marker = `__HX_ENV_READY_${args.jobId.replace(/[^A-Za-z0-9]/g, '_')}__`;
      const result = await runCommand(
        'bash',
        ['scripts/huanxin_shell.sh', args.envName, `printf '${marker}\\n'; pwd; whoami; hostname`],
        {
          timeoutMs: 300000,
          env: {
            HUANXIN_WAIT_MS: String(args.waitMs),
            HUANXIN_USE_DAEMON: '1',
            HUANXIN_ALLOW_STANDALONE_FALLBACK: '0',
          },
        }
      );
      return {
        ...commandSummary(result, false),
        failureKind: classifyFailure(result),
        marker,
        markerObserved: result.stdout.includes(marker),
      };
    });

    await checkedStep(state, 'local_to_s3_probe_upload', async () => uploadProbeToS3(state, args));
    await checkedStep(state, 's3_to_ai_probe_sync', async () => syncProbeFromS3ToAI(state, args));
    await checkedStep(state, 'remote_command_after_sync', async () => runRemoteCommand(state, args));

    const failed = state.payload.steps.some((step) => step.state === 'failed' || step.ok === false);
    const missingEvidence = state.payload.steps.some(
      (step) =>
        (Object.prototype.hasOwnProperty.call(step, 'markerObserved') && !step.markerObserved) ||
        (Object.prototype.hasOwnProperty.call(step, 'verifiedCatContainsJobId') && !step.verifiedCatContainsJobId) ||
        (Object.prototype.hasOwnProperty.call(step, 'probeContentObserved') && !step.probeContentObserved)
    );
    state.complete(!failed && !missingEvidence);
    if (failed || missingEvidence) {
      process.exitCode = 1;
    }
  } catch (error) {
    state.payload.finalError = redact(error && (error.stack || error.message || String(error)));
    state.complete(false);
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(redact(error && (error.stack || error.message || String(error))));
  process.exit(1);
});
