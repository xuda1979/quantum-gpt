#!/usr/bin/env node

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { openShell, sendCommand } = require('./huanxin_shell_exec');

const DEFAULT_ENV_NAME = 'AI';
const DEFAULT_REMOTE_ROOT = '/root/software/quantum-gpt';
const DEFAULT_MODEL_SOURCE = '/root/work/filestorage/Qwen3.6-27B';
const DEFAULT_LOCAL_PATHS = [
  'training',
  'data/generated/omnicoder-quantum-generalization-holdout-v1',
];

function parseArgs(argv) {
  const options = {
    envName: DEFAULT_ENV_NAME,
    remoteRoot: DEFAULT_REMOTE_ROOT,
    modelSource: DEFAULT_MODEL_SOURCE,
    chunkSize: 16000,
    skipPeftInstall: false,
    localPaths: [...DEFAULT_LOCAL_PATHS],
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--env' && argv[index + 1]) {
      options.envName = argv[index + 1];
      index += 1;
      continue;
    }
    if (token === '--remote-root' && argv[index + 1]) {
      options.remoteRoot = argv[index + 1];
      index += 1;
      continue;
    }
    if (token === '--model-source' && argv[index + 1]) {
      options.modelSource = argv[index + 1];
      index += 1;
      continue;
    }
    if (token === '--chunk-size' && argv[index + 1]) {
      const parsed = Number.parseInt(argv[index + 1], 10);
      if (!Number.isFinite(parsed) || parsed <= 0) {
        throw new Error(`Invalid --chunk-size value: ${argv[index + 1]}`);
      }
      options.chunkSize = parsed;
      index += 1;
      continue;
    }
    if (token === '--skip-peft-install') {
      options.skipPeftInstall = true;
      continue;
    }
    if (token === '--local-path' && argv[index + 1]) {
      options.localPaths.push(argv[index + 1]);
      index += 1;
      continue;
    }
    throw new Error(`Unknown or incomplete argument: ${token}`);
  }

  return options;
}

function shQuote(value) {
  return `'${String(value).replace(/'/g, `'"'"'`)}'`;
}

function packagePayload(repoRoot, localPaths) {
  const tmpTarPath = path.join(os.tmpdir(), `huanxin-ai-sft-payload-${Date.now()}-${process.pid}.tgz`);
  const pack = spawnSync('tar', ['-czf', tmpTarPath, ...localPaths], {
    cwd: repoRoot,
    stdio: 'inherit',
  });
  if ((pack.status ?? 1) !== 0) {
    throw new Error(`tar failed with exit code ${pack.status ?? 'unknown'}`);
  }
  return tmpTarPath;
}

function buildChunks(buffer, chunkSize) {
  const encoded = buffer.toString('base64');
  const chunks = [];
  for (let index = 0; index < encoded.length; index += chunkSize) {
    chunks.push(encoded.slice(index, index + chunkSize));
  }
  return { encodedLength: encoded.length, chunks };
}

function summarizeResult(result) {
  return JSON.stringify(
    {
      commandStatus: result.commandStatus,
      commandOk: result.commandOk,
      output: result.output,
      before: result.before,
      after: result.after,
    },
    null,
    2
  );
}

async function runRemoteCommand(page, label, command, waitMs) {
  const result = await sendCommand(page, command, waitMs);
  if (!result.commandOk) {
    throw new Error(`${label || 'remote command'} failed:\n${summarizeResult(result)}`);
  }
  if (label) {
    const output = String(result.output || '').trim();
    console.log(`${label}: ${output || '[no output]'}`);
  }
  return result;
}

async function main() {
  const repoRoot = path.resolve(__dirname, '..');
  const options = parseArgs(process.argv.slice(2));
  const tmpTarPath = packagePayload(repoRoot, options.localPaths);

  try {
    const { encodedLength, chunks } = buildChunks(fs.readFileSync(tmpTarPath), options.chunkSize);
    console.log(`Prepared ${chunks.length} chunks from ${encodedLength} base64 chars.`);

    const remoteRoot = options.remoteRoot.replace(/\/+$/, '');
    const remoteModelDir = `${remoteRoot}/models/Qwen3.6-27B`;
    const remoteBase64Path = '/tmp/huanxin_ai_sft_payload.tgz.b64';
    const remoteTarPath = '/tmp/huanxin_ai_sft_payload.tgz';
    const extractCommand = [
      `python3 -c ${shQuote(`import base64; src=${JSON.stringify(remoteBase64Path)}; dst=${JSON.stringify(remoteTarPath)}; data=open(src,'rb').read(); open(dst,'wb').write(base64.b64decode(data)); print(len(data))`)}`,
      `mkdir -p ${shQuote(remoteRoot)}`,
      `tar -xzf ${shQuote(remoteTarPath)} -C ${shQuote(remoteRoot)}`,
      `rm -rf ${shQuote(remoteModelDir)}`,
      `ln -s ${shQuote(options.modelSource)} ${shQuote(remoteModelDir)}`,
      `test -f ${shQuote(`${remoteRoot}/training/qwen_sft_peft.py`)}`,
      `test -f ${shQuote(`${remoteRoot}/data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl`)}`,
      `test -f ${shQuote(`${remoteRoot}/data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl`)}`,
      'echo BOOTSTRAP_OK',
    ].join(' && ');
    const dependencyProbeCommand = `cd ${shQuote(remoteRoot)} && python3 -c ${shQuote("import importlib.util,json; mods=['torch','transformers','peft']; print(json.dumps({'modules':{m:bool(importlib.util.find_spec(m)) for m in mods}}))")}`;
    const preflightCommand = [
      `cd ${shQuote(remoteRoot)}`,
      `test -d ${shQuote(remoteModelDir)}`,
      `python3 -c ${shQuote("import importlib.util,json; mods=['torch','transformers','peft']; print(json.dumps({'modules':{m:bool(importlib.util.find_spec(m)) for m in mods}}))")}`,
      `python3 -c ${shQuote(`from pathlib import Path; root = Path(${JSON.stringify(remoteRoot)}); print(root.joinpath('training/qwen_sft_peft.py').exists()); print(root.joinpath('data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl').exists()); print(root.joinpath('data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl').exists()); print(root.joinpath('models/Qwen3.6-27B').resolve())`)}`,
    ].join(' && ');

    const { profileDir } = ensureProfileDir();
    console.log(`Using profile: ${profileDir}`);
    console.log('Launching browser context...');
    const launch = await launchPersistentContext(profileDir);
    const context = launch.context;

    try {
      const page = context.pages()[0] || (await context.newPage());
      page.setDefaultTimeout(30000);
      console.log(`Opening ${options.envName} shell...`);
      const shellPage = await openShell(page, options.envName);
      console.log(`${options.envName} shell ready.`);

      await runRemoteCommand(
        shellPage,
        'init',
        [
          `mkdir -p ${shQuote(remoteRoot)}`,
          `mkdir -p ${shQuote(`${remoteRoot}/models`)}`,
          `: > ${shQuote(remoteBase64Path)}`,
        ].join(' && '),
        180000
      );

      for (let index = 0; index < chunks.length; index += 1) {
        const label = (index + 1) % 5 === 0 || index === chunks.length - 1 ? `chunk ${index + 1}/${chunks.length}` : '';
        await runRemoteCommand(
          shellPage,
          label,
          `printf '%s' '${chunks[index]}' >> ${shQuote(remoteBase64Path)}`,
          180000
        );
      }

      await runRemoteCommand(shellPage, 'extract', extractCommand, 240000);
      await runRemoteCommand(shellPage, 'dependency probe before peft install', dependencyProbeCommand, 180000);

      if (!options.skipPeftInstall) {
        await runRemoteCommand(
          shellPage,
          'install peft',
          [
            `cd ${shQuote(remoteRoot)}`,
            'python3 -m pip install --no-input peft >/tmp/huanxin_peft_install.log 2>&1',
            'tail -n 20 /tmp/huanxin_peft_install.log',
          ].join(' && '),
          600000
        );
      }

      await runRemoteCommand(shellPage, 'post-bootstrap preflight', preflightCommand, 240000);
    } finally {
      await context.close().catch(() => {});
    }
  } finally {
    fs.rmSync(tmpTarPath, { force: true });
  }
}

main().catch((error) => {
  console.error(error && (error.stack || error.message || error));
  process.exit(1);
});