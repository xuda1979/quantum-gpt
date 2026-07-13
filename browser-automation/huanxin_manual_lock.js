const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const MANUAL_MODE_LOCK = path.join(ROOT_DIR, '.huanxin_manual_mode');
const AUTOMATION_ENABLE_FILE = path.join(ROOT_DIR, '.huanxin_automation_enabled');

function isManualModeLocked() {
  return fs.existsSync(MANUAL_MODE_LOCK);
}

function isAutomationEnabled() {
  return fs.existsSync(AUTOMATION_ENABLE_FILE);
}

function assertAutomationAllowed(operation = 'Huanxin browser automation') {
  if (isAutomationEnabled() && !isManualModeLocked()) {
    return;
  }
  const reason = isManualModeLocked()
    ? `manual lock is active at ${MANUAL_MODE_LOCK}`
    : `automation enable file is missing at ${AUTOMATION_ENABLE_FILE}`;
  const message =
    `Huanxin browser automation is disabled (${reason}); refusing ${operation}. ` +
    'Create .huanxin_automation_enabled only when browser automation is intentionally allowed again.';
  const error = new Error(message);
  error.code = 'HUANXIN_MANUAL_MODE_LOCKED';
  error.lockPath = MANUAL_MODE_LOCK;
  error.enablePath = AUTOMATION_ENABLE_FILE;
  throw error;
}

module.exports = {
  AUTOMATION_ENABLE_FILE,
  MANUAL_MODE_LOCK,
  assertAutomationAllowed,
  isAutomationEnabled,
  isManualModeLocked,
};
