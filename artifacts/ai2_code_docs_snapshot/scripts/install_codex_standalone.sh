#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/install_codex_standalone.sh [--version-tag <tag>] [--install-dir <dir>]

Examples:
  scripts/install_codex_standalone.sh
  scripts/install_codex_standalone.sh --version-tag rust-v0.117.0
  scripts/install_codex_standalone.sh --install-dir "$HOME/.local/bin"
EOF
  exit 1
}

VERSION_TAG=""
INSTALL_DIR="${HOME}/.local/bin"
URL_OVERRIDE="${CODEX_STANDALONE_URL:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version-tag)
      VERSION_TAG="${2:-}"
      [[ -n "$VERSION_TAG" ]] || usage
      shift 2
      ;;
    --install-dir)
      INSTALL_DIR="${2:-}"
      [[ -n "$INSTALL_DIR" ]] || usage
      shift 2
      ;;
    --url)
      URL_OVERRIDE="${2:-}"
      [[ -n "$URL_OVERRIDE" ]] || usage
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
  Linux) ;;
  *)
    echo "Unsupported OS for this helper: $OS" >&2
    exit 1
    ;;
esac

case "$ARCH" in
  x86_64|amd64)
    ASSET="codex-x86_64-unknown-linux-musl.tar.gz"
    EXTRACTED_NAME="codex-x86_64-unknown-linux-musl"
    ;;
  aarch64|arm64)
    ASSET="codex-aarch64-unknown-linux-musl.tar.gz"
    EXTRACTED_NAME="codex-aarch64-unknown-linux-musl"
    ;;
  *)
    echo "Unsupported Linux architecture for Codex standalone install: $ARCH" >&2
    exit 1
    ;;
esac

if command -v curl >/dev/null 2>&1; then
  FETCH=(curl -fL)
elif command -v wget >/dev/null 2>&1; then
  FETCH=(wget -O-)
else
  echo "Need curl or wget to download Codex." >&2
  exit 1
fi

if [[ -n "$URL_OVERRIDE" ]]; then
  URL="$URL_OVERRIDE"
elif [[ -n "$VERSION_TAG" ]]; then
  URL="https://github.com/openai/codex/releases/download/${VERSION_TAG}/${ASSET}"
else
  URL="https://github.com/openai/codex/releases/latest/download/${ASSET}"
fi

mkdir -p "$INSTALL_DIR"
TMP_DIR="$(mktemp -d)"
ARCHIVE_PATH="${TMP_DIR}/${ASSET}"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Downloading ${URL}" >&2
"${FETCH[@]}" "$URL" > "$ARCHIVE_PATH"

tar -xzf "$ARCHIVE_PATH" -C "$TMP_DIR"

if [[ ! -f "${TMP_DIR}/${EXTRACTED_NAME}" ]]; then
  echo "Did not find extracted Codex binary at ${TMP_DIR}/${EXTRACTED_NAME}" >&2
  exit 1
fi

install -m 0755 "${TMP_DIR}/${EXTRACTED_NAME}" "${INSTALL_DIR}/codex"

echo "Installed Codex to ${INSTALL_DIR}/codex" >&2
if ! command -v rg >/dev/null 2>&1; then
  echo "Warning: rg is not installed; Codex works best with ripgrep available on PATH." >&2
fi
"${INSTALL_DIR}/codex" --version
