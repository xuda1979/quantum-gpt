const fs = require('fs');
const os = require('os');
const path = require('path');
const { assertAutomationAllowed } = require('./huanxin_manual_lock');

function getBaseProfileDir() {
  return path.resolve(process.env.HUANXIN_BASE_PROFILE_DIR || path.join(__dirname, 'profile'));
}

function sanitizeName(value) {
  return String(value || 'default')
    .trim()
    .replace(/[^a-zA-Z0-9._-]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'default';
}

function getRequestedProfileDir() {
  if (process.env.HUANXIN_PROFILE_DIR) {
    return path.resolve(process.env.HUANXIN_PROFILE_DIR);
  }

  if (process.env.HUANXIN_PROFILE_COPY_NAME) {
    return path.join(os.tmpdir(), `huanxin-profile-${sanitizeName(process.env.HUANXIN_PROFILE_COPY_NAME)}`);
  }

  return getBaseProfileDir();
}

function baseProfileHasSingletonLock(baseProfileDir = getBaseProfileDir()) {
  return ['SingletonCookie', 'SingletonLock', 'SingletonSocket', 'lockfile'].some((name) =>
    fs.existsSync(path.join(baseProfileDir, name))
  );
}

function autoProfileCopyName() {
  return `auto-${Date.now()}-${process.pid}`;
}

function shouldSkipEntry(sourcePath) {
  const name = path.basename(sourcePath);
  const normalized = String(sourcePath).split(path.sep).join('/');
  if (
    normalized.includes('/Cache/') ||
    normalized.includes('/Code Cache/') ||
    normalized.includes('/GPUCache/') ||
    normalized.includes('/ShaderCache/') ||
    normalized.includes('/GrShaderCache/')
  ) {
    return true;
  }
  return [
    'SingletonCookie',
    'SingletonLock',
    'SingletonSocket',
    'lockfile',
    '.org.chromium.Chromium',
  ].includes(name);
}

function removeDirRobust(targetDir) {
  if (!fs.existsSync(targetDir)) {
    return;
  }

  for (let attempt = 1; attempt <= 5; attempt += 1) {
    try {
      fs.rmSync(targetDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
      return;
    } catch (err) {
      if (attempt === 5) {
        throw err;
      }
      const fallbackDir = `${targetDir}.stale-${Date.now()}-${process.pid}-${attempt}`;
      try {
        fs.renameSync(targetDir, fallbackDir);
        fs.rmSync(fallbackDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
        return;
      } catch (_) {
        Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 100 * attempt);
      }
    }
  }
}

function copyProfileTree(sourceDir, targetDir) {
  if (!fs.existsSync(sourceDir)) {
    throw new Error(`Huanxin profile source does not exist: ${sourceDir}`);
  }

  removeDirRobust(targetDir);
  fs.mkdirSync(path.dirname(targetDir), { recursive: true });
  if (fs.existsSync(targetDir)) {
    removeDirRobust(targetDir);
  }
  fs.cpSync(sourceDir, targetDir, {
    recursive: true,
    force: true,
    errorOnExist: false,
    dereference: false,
    filter: (sourcePath) => !shouldSkipEntry(sourcePath),
  });
}

function syncProfileTree(sourceDir, targetDir) {
  const backupDir = `${targetDir}.last-known-good`;
  if (fs.existsSync(targetDir)) {
    copyProfileTree(targetDir, backupDir);
  }
  copyProfileTree(sourceDir, targetDir);
  return { backupDir };
}

function ensureProfileDir() {
  assertAutomationAllowed('ensureProfileDir');
  const baseProfileDir = getBaseProfileDir();
  const explicitProfileDir = Boolean(process.env.HUANXIN_PROFILE_DIR);
  const explicitCopyName = Boolean(process.env.HUANXIN_PROFILE_COPY_NAME);
  if (!explicitProfileDir && !explicitCopyName && process.env.HUANXIN_AUTO_ISOLATE_LOCKED_PROFILE !== '0') {
    fs.mkdirSync(baseProfileDir, { recursive: true });
    if (baseProfileHasSingletonLock(baseProfileDir)) {
      process.env.HUANXIN_PROFILE_COPY_NAME = autoProfileCopyName();
    }
  }
  const resolvedProfileDir = getRequestedProfileDir();

  if (!process.env.HUANXIN_PROFILE_COPY_NAME) {
    fs.mkdirSync(resolvedProfileDir, { recursive: true });
    return {
      profileDir: resolvedProfileDir,
      isolated: false,
      sourceDir: baseProfileDir,
      autoIsolated: false,
      baseProfileLocked: false,
    };
  }

  if (!fs.existsSync(baseProfileDir)) {
    throw new Error(`Base Huanxin profile does not exist: ${baseProfileDir}`);
  }

  copyProfileTree(baseProfileDir, resolvedProfileDir);

  return {
    profileDir: resolvedProfileDir,
    isolated: true,
    sourceDir: baseProfileDir,
    autoIsolated: !explicitCopyName && !explicitProfileDir,
    baseProfileLocked: baseProfileHasSingletonLock(baseProfileDir),
  };
}

module.exports = {
  autoProfileCopyName,
  baseProfileHasSingletonLock,
  copyProfileTree,
  ensureProfileDir,
  getBaseProfileDir,
  getRequestedProfileDir,
  removeDirRobust,
  sanitizeName,
  syncProfileTree,
};
