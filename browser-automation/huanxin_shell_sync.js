const { execFileSync } = require('child_process');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { openShell, readTerminalText, sendCommand } = require('./huanxin_shell_exec');

function usage() {
  console.error(
    'Usage: node huanxin_shell_sync.js <envName> --remote-dir <path> --source <path> [--source <path> ...]'
  );
  process.exit(1);
}

function parseArgs(argv) {
  const envName = argv[0];
  if (!envName) usage();

  const args = {
    envName,
    remoteDir: null,
    sources: [],
  };

  for (let index = 1; index < argv.length; index += 1) {
    const token = argv[index];
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
    usage();
  }

  if (!args.remoteDir || args.sources.length === 0 || args.sources.some((value) => !value)) {
    usage();
  }

  return args;
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'"'"'`)}'`;
}

function buildArchiveBase64(workspaceRoot, sources) {
  const archive = execFileSync('tar', [
    '--exclude=.DS_Store',
    '--exclude=*.egg-info',
    '--exclude=__pycache__',
    '--exclude=.pytest_cache',
    '--exclude=.mypy_cache',
    '--exclude=.ruff_cache',
    '-czf',
    '-',
    ...sources,
  ], {
    cwd: workspaceRoot,
    env: { ...process.env, COPYFILE_DISABLE: '1' },
    maxBuffer: 1024 * 1024 * 64,
  });
  return archive.toString('base64');
}

function chunkString(value, chunkSize) {
  const chunks = [];
  for (let index = 0; index < value.length; index += chunkSize) {
    chunks.push(value.slice(index, index + chunkSize));
  }
  return chunks;
}

async function main() {
  const { envName, remoteDir, sources } = parseArgs(process.argv.slice(2));
  const workspaceRoot = process.cwd();
  const archiveBase64 = buildArchiveBase64(workspaceRoot, sources);
  const chunkSizeRaw = parseInt(process.env.HUANXIN_SHELL_SYNC_CHUNK_SIZE || '1024', 10);
  const chunkSize = Number.isFinite(chunkSizeRaw) && chunkSizeRaw > 0 ? chunkSizeRaw : 1024;
  const chunkWaitRaw = parseInt(process.env.HUANXIN_SHELL_SYNC_CHUNK_WAIT_MS || '20000', 10);
  const chunkWaitMs = Number.isFinite(chunkWaitRaw) && chunkWaitRaw > 0 ? chunkWaitRaw : 20000;
  const extractWaitRaw = parseInt(process.env.HUANXIN_SHELL_SYNC_EXTRACT_WAIT_MS || '30000', 10);
  const extractWaitMs = Number.isFinite(extractWaitRaw) && extractWaitRaw > 0 ? extractWaitRaw : 30000;
  const chunks = chunkString(archiveBase64, chunkSize);
  const remoteBaseName = '/tmp/huanxin-quantum-gpt-upload';

  const { profileDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;

  try {
    const page = context.pages()[0] || (await context.newPage());
    page.setDefaultTimeout(30000);

    const activePage = await openShell(page, envName);
    await sendCommand(
      activePage,
      `mkdir -p ${shellQuote(remoteDir)} && rm -f ${remoteBaseName}.tgz ${remoteBaseName}.tgz.b64 && : > ${remoteBaseName}.tgz.b64 && echo __SYNC_INIT_OK__`,
      5000
    );

    for (let index = 0; index < chunks.length; index += 1) {
      const chunk = chunks[index];
      const appendCommand = `printf '%s' '${chunk}' >> ${remoteBaseName}.tgz.b64 && echo __SYNC_CHUNK_${index + 1}__`;
      await sendCommand(activePage, appendCommand, chunkWaitMs);
      if ((index + 1) % 25 === 0 || index + 1 === chunks.length) {
        console.error(`uploaded chunk ${index + 1}/${chunks.length}`);
      }
    }

    const extractCommand = [
      `base64 -d ${remoteBaseName}.tgz.b64 > ${remoteBaseName}.tgz`,
      `tar -xzf ${remoteBaseName}.tgz -C ${shellQuote(remoteDir)}`,
      `find ${shellQuote(remoteDir)} -name '._*' -delete`,
      `rm -f ${remoteBaseName}.tgz ${remoteBaseName}.tgz.b64`,
      `cd ${shellQuote(remoteDir)}`,
      `pwd`,
      `find . -maxdepth 3 -type f | sort | sed -n '1,200p'`,
    ].join(' && ');

    const { before, after } = await sendCommand(activePage, extractCommand, extractWaitMs);
    await activePage.screenshot({ path: `browser-automation/huanxin-shell-sync-${envName}.png`, fullPage: true });

    console.log(
      JSON.stringify(
        {
          ok: true,
          envName,
          remoteDir,
          sources,
          archiveBytes: Buffer.from(archiveBase64, 'base64').length,
          chunkCount: chunks.length,
          url: activePage.url(),
          before,
          after,
          terminal: await readTerminalText(activePage),
        },
        null,
        2
      )
    );
  } finally {
    await context.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
