#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { ensureProfileDir } = require('./huanxin_profile');
const { launchPersistentContext } = require('./huanxin_browser_launch');
const { bridgePageViaSafariSso, classifyUrl } = require('./huanxin_repair_profile_via_safari_sso');

const ROOT = path.resolve(__dirname, '..');

function usage() {
  console.error(
    'Usage: node browser-automation/huanxin_jupyter_upload.js --env ASI1 --source <local-file> --remote-path <remote-path> [--jupyter-url <url>] [--wait-ms 30000]'
  );
  process.exit(2);
}

function parseArgs(argv) {
  const args = { env: '', source: '', remotePath: '', jupyterUrl: '', waitMs: 30000 };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === '--env') {
      args.env = argv[++i] || '';
    } else if (token === '--source') {
      args.source = argv[++i] || '';
    } else if (token === '--remote-path') {
      args.remotePath = argv[++i] || '';
    } else if (token === '--jupyter-url') {
      args.jupyterUrl = argv[++i] || '';
    } else if (token === '--wait-ms') {
      args.waitMs = Number.parseInt(argv[++i] || '30000', 10);
    } else {
      usage();
    }
  }
  if (!args.env || !args.source || !args.remotePath) {
    usage();
  }
  return args;
}

function readEnvConfig(envName) {
  const { execFileSync } = require('child_process');
  return JSON.parse(
    execFileSync('python3', ['scripts/huanxin_env_config.py', '--env', envName], {
      cwd: ROOT,
      encoding: 'utf8',
    })
  );
}

async function ensureAppSurface(page, targetUrl, waitMs) {
  await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(3000);
  if (classifyUrl(page.url()) === 'login_required') {
    const bridge = await bridgePageViaSafariSso(page, {
      authUrl: page.url(),
      targetUrl,
      waitMs,
      resultPath: `/tmp/huanxin-jupyter-upload-sso-${Date.now()}.json`,
    });
    if (!bridge || !bridge.ok) {
      throw new Error(`Safari SSO bridge failed: ${JSON.stringify(bridge)}`);
    }
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
    await page.waitForTimeout(3000);
  }
}

async function getJupyterUrl(page, envId) {
  const result = await page.evaluate(async (id) => {
    const response = await fetch(`/kunlun/web/develop/v1/detail?id=${encodeURIComponent(id)}`, {
      method: 'GET',
      credentials: 'include',
    });
    const text = await response.text();
    let json = null;
    try {
      json = JSON.parse(text);
    } catch {}
    return { status: response.status, text, json };
  }, envId);
  const url = result.json && result.json.data && result.json.data.jupyterUrl;
  if (!url) {
    throw new Error(`Could not resolve jupyterUrl: ${JSON.stringify(result).slice(0, 2000)}`);
  }
  return url;
}

function contentsApiUrl(jupyterUrl, remotePath) {
  const base = new URL(jupyterUrl);
  const cleaned = String(remotePath || '').replace(/^\/+/, '');
  const prefix = base.pathname.replace(/\/lab\/?$/, '');
  base.pathname = `${prefix}/api/contents/${cleaned}`;
  base.search = '';
  base.hash = '';
  return base.toString();
}

async function uploadViaJupyter(page, jupyterUrl, remotePath, base64Content, byteLength, sha256) {
  await page.goto(jupyterUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForTimeout(5000);
  const apiUrl = contentsApiUrl(jupyterUrl, remotePath);
  return page.evaluate(
    async ({ apiUrl: target, remotePath: pathName, content, byteLength: bytes, sha256: sha }) => {
      const parent = pathName.split('/').slice(0, -1).filter(Boolean);
      let current = '';
      for (const part of parent) {
        current = current ? `${current}/${part}` : part;
        const folderUrl = target.split('/api/contents/')[0] + '/api/contents/' + encodeURIComponent(current).replace(/%2F/g, '/');
        await fetch(folderUrl, {
          method: 'PUT',
          credentials: 'include',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ type: 'directory' }),
        }).catch(() => null);
      }
      const response = await fetch(target, {
        method: 'PUT',
        credentials: 'include',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          type: 'file',
          format: 'base64',
          content,
        }),
      });
      const text = await response.text();
      let json = null;
      try {
        json = JSON.parse(text);
      } catch {}
      if (!response.ok) {
        return { ok: false, status: response.status, text: text.slice(0, 2000), json };
      }
      const check = await fetch(target, { method: 'GET', credentials: 'include' });
      const checkText = await check.text();
      let checkJson = null;
      try {
        checkJson = JSON.parse(checkText);
      } catch {}
      return {
        ok: response.ok && check.ok,
        status: response.status,
        checkStatus: check.status,
        path: json && json.path,
        name: json && json.name,
        size: json && json.size,
        expectedBytes: bytes,
        sha256: sha,
        checkSize: checkJson && checkJson.size,
        checkType: checkJson && checkJson.type,
      };
    },
    { apiUrl, remotePath: remotePath.replace(/^\/+/, ''), content: base64Content, byteLength, sha256 }
  );
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const source = path.resolve(args.source);
  const data = fs.readFileSync(source);
  const crypto = require('crypto');
  const sha256 = crypto.createHash('sha256').update(data).digest('hex');
  const envConfig = readEnvConfig(args.env);
  const { profileDir } = ensureProfileDir();
  const launch = await launchPersistentContext(profileDir);
  const context = launch.context;
  const page = context.pages()[0] || (await context.newPage());
  page.setDefaultTimeout(args.waitMs);
  await ensureAppSurface(page, envConfig.train_dev_url, args.waitMs);
  const jupyterUrl = args.jupyterUrl || (await getJupyterUrl(page, envConfig.env_id));
  const result = await uploadViaJupyter(page, jupyterUrl, args.remotePath, data.toString('base64'), data.length, sha256);
  await context.close();
  console.log(
    JSON.stringify(
      {
        ok: Boolean(result && result.ok),
        env: args.env,
        source,
        remotePath: args.remotePath,
        bytes: data.length,
        sha256,
        jupyterUrl: jupyterUrl.replace(/\/lab.*/, '/lab'),
        result,
      },
      null,
      2
    )
  );
  if (!result || !result.ok) {
    process.exit(1);
  }
}

main().catch((error) => {
  console.error(error && (error.stack || error.message || error));
  process.exit(1);
});
