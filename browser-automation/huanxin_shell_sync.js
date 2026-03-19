const { execFileSync } = require('child_process');
const path = require('path');
const { chromium } = require('playwright');
const { ensureProfileDir } = require('./huanxin_profile');
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
  const archive = execFileSync('tar', ['-czf', '-', ...sources], {
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
  const chunks = chunkString(archiveBase64, 8000);
  const remoteBaseName = '/tmp/huanxin-quantum-gpt-upload';

  const { profileDir } = ensureProfileDir();
  const context = await chromium.launchPersistentContext(profileDir, {
    headless: process.env.HUANXIN_HEADLESS === '1',
    viewport: { width: 1600, height: 1000 },
    slowMo: 50,
  });

  try {
    const page = context.pages()[0] || (await context.newPage());
    page.setDefaultTimeout(30000);

    const activePage = await openShell(page, envName);
    await sendCommand(
      activePage,
      `mkdir -p ${shellQuote(remoteDir)} && rm -f ${remoteBaseName}.tgz ${remoteBaseName}.tgz.b64 && : > ${remoteBaseName}.tgz.b64`,
      1500
    );

    for (const chunk of chunks) {
      const appendCommand = `printf '%s' '${chunk}' >> ${remoteBaseName}.tgz.b64`;
      await sendCommand(activePage, appendCommand, 400);
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

    const { before, after } = await sendCommand(activePage, extractCommand, 7000);
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
