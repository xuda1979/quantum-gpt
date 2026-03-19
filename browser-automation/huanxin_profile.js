const fs = require('fs');
const os = require('os');
const path = require('path');

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

function shouldSkipEntry(sourcePath) {
  const name = path.basename(sourcePath);
  return [
    'SingletonCookie',
    'SingletonLock',
    'SingletonSocket',
    'lockfile',
    '.org.chromium.Chromium',
  ].includes(name);
}

function ensureProfileDir() {
  const baseProfileDir = getBaseProfileDir();
  const resolvedProfileDir = getRequestedProfileDir();

  if (!process.env.HUANXIN_PROFILE_COPY_NAME) {
    fs.mkdirSync(resolvedProfileDir, { recursive: true });
    return { profileDir: resolvedProfileDir, isolated: false, sourceDir: baseProfileDir };
  }

  if (!fs.existsSync(baseProfileDir)) {
    throw new Error(`Base Huanxin profile does not exist: ${baseProfileDir}`);
  }

  fs.rmSync(resolvedProfileDir, { recursive: true, force: true });
  fs.mkdirSync(path.dirname(resolvedProfileDir), { recursive: true });
  fs.cpSync(baseProfileDir, resolvedProfileDir, {
    recursive: true,
    force: true,
    filter: (sourcePath) => !shouldSkipEntry(sourcePath),
  });

  return { profileDir: resolvedProfileDir, isolated: true, sourceDir: baseProfileDir };
}

module.exports = {
  ensureProfileDir,
  getBaseProfileDir,
  getRequestedProfileDir,
  sanitizeName,
};
