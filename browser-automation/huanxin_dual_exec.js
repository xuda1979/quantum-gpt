const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

function usage() {
  console.error(
    'Usage: node browser-automation/huanxin_dual_exec.js --ai1-command <cmd> --ai2-command <cmd> [--remote-dir <dir> --source <path> ...]'
  );
  process.exit(1);
}

function parseArgs(argv) {
  const args = {
    ai1Command: null,
    ai2Command: null,
    remoteDir: null,
    sources: [],
    out: null,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--ai1-command') {
      args.ai1Command = argv[index + 1] || null;
      index += 1;
      continue;
    }
    if (token === '--ai2-command') {
      args.ai2Command = argv[index + 1] || null;
      index += 1;
      continue;
    }
    if (token === '--remote-dir') {
      args.remoteDir = argv[index + 1] || null;
      index += 1;
      continue;
    }
    if (token === '--source') {
      args.sources.push(argv[index + 1] || '');
      index += 1;
      continue;
    }
    if (token === '--out') {
      args.out = argv[index + 1] || null;
      index += 1;
      continue;
    }
    usage();
  }

  if (!args.ai1Command || !args.ai2Command) {
    usage();
  }

  if ((args.remoteDir && args.sources.length === 0) || (!args.remoteDir && args.sources.length > 0)) {
    usage();
  }

  if (args.sources.some((value) => !value)) {
    usage();
  }

  return args;
}

function runNodeScript(scriptPath, scriptArgs, extraEnv, cwd) {
  return new Promise((resolve) => {
    execFile(process.execPath, [scriptPath, ...scriptArgs], {
      cwd,
      env: { ...process.env, ...extraEnv },
      maxBuffer: 1024 * 1024 * 64,
    }, (error, stdout, stderr) => {
      resolve({
        ok: !error,
        exitCode: error && typeof error.code === 'number' ? error.code : 0,
        stdout,
        stderr,
      });
    });
  });
}

async function runEnvTask(envName, command, remoteDir, sources, cwd) {
  const scriptDir = __dirname;
  const profileCopyName = `${envName}-${Date.now()}`;
  const extraEnv = {
    HUANXIN_PROFILE_COPY_NAME: profileCopyName,
    HUANXIN_HEADLESS: process.env.HUANXIN_HEADLESS || '1',
  };

  const result = {
    envName,
    profileCopyName,
  };

  if (remoteDir && sources.length > 0) {
    result.sync = await runNodeScript(
      path.join(scriptDir, 'huanxin_shell_sync.js'),
      [envName, '--remote-dir', remoteDir, ...sources.flatMap((source) => ['--source', source])],
      extraEnv,
      cwd
    );
    if (!result.sync.ok) {
      return result;
    }
  }

  result.exec = await runNodeScript(
    path.join(scriptDir, 'huanxin_shell_exec.js'),
    [envName, '--command', command],
    extraEnv,
    cwd
  );

  return result;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const cwd = process.cwd();

  const [ai1, ai2] = await Promise.all([
    runEnvTask('ai1', args.ai1Command, args.remoteDir, args.sources, cwd),
    runEnvTask('ai2', args.ai2Command, args.remoteDir, args.sources, cwd),
  ]);

  const summary = {
    ok: Boolean(ai1.exec?.ok && ai2.exec?.ok),
    remoteDir: args.remoteDir,
    sources: args.sources,
    ai1,
    ai2,
    timestamp: new Date().toISOString(),
  };

  const outPath = args.out || path.resolve('browser-automation/huanxin-dual-exec.json');
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(summary, null, 2), 'utf8');
  console.log(JSON.stringify(summary, null, 2));

  if (!summary.ok) {
    process.exit(1);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
