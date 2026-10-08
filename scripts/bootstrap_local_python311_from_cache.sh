#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_PREFIX="$ROOT_DIR/.local-python/cpython-3.11.15"
PREFIX="$DEFAULT_PREFIX"
JOBS="${JOBS:-4}"
FORCE_REBUILD=0

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/bootstrap_local_python311_from_cache.sh [--prefix <dir>] [--jobs <n>] [--force-rebuild]

Builds a local CPython 3.11 from cached source artifacts plus an already-installed
local OpenSSL prefix. This is intended as an offline fallback when Homebrew can
no longer fetch python@3.11 over the network.
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix)
      PREFIX="$2"
      shift 2
      ;;
    --jobs)
      JOBS="$2"
      shift 2
      ;;
    --force-rebuild)
      FORCE_REBUILD=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

find_python_tarball() {
  local cache_dir="$HOME/Library/Caches/Homebrew/downloads"
  local matches=("$cache_dir"/*--Python-3.11.15.tgz)
  if [[ ${#matches[@]} -eq 0 || ! -f "${matches[0]}" ]]; then
    echo "Missing cached Python 3.11 source tarball under $cache_dir" >&2
    exit 1
  fi
  printf '%s\n' "${matches[0]}"
}

find_openssl_prefix() {
  local candidates=(
    "${OPENSSL_PREFIX:-}"
    "$HOME/homebrew/opt/openssl"
    "$HOME/homebrew/opt/openssl@3"
    "/opt/homebrew/opt/openssl"
    "/opt/homebrew/opt/openssl@3"
    "/usr/local/opt/openssl@3"
    "/usr/local/opt/openssl"
  )
  local candidate
  for candidate in "${candidates[@]}"; do
    [[ -n "$candidate" ]] || continue
    if [[ -f "$candidate/include/openssl/ssl.h" && -f "$candidate/lib/libssl.dylib" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  echo "Could not find a usable local OpenSSL prefix." >&2
  exit 1
}

verify_existing() {
  if [[ ! -x "$PREFIX/bin/python3.11" ]]; then
    return 1
  fi
  "$PREFIX/bin/python3.11" -c 'import ssl,sys; print(sys.version); print(ssl.OPENSSL_VERSION)' >/dev/null
}

if [[ "$FORCE_REBUILD" -eq 0 ]] && verify_existing; then
  "$PREFIX/bin/python3.11" -c 'import sys,ssl; print(sys.version); print(ssl.OPENSSL_VERSION)'
  exit 0
fi

PYTHON_TARBALL="$(find_python_tarball)"
OPENSSL_PREFIX_RESOLVED="$(find_openssl_prefix)"
BUILD_ROOT="${TMPDIR:-/tmp}/quantum-gpt-python311-build"
SRC_DIR="$BUILD_ROOT/Python-3.11.15"

rm -rf "$SRC_DIR"
mkdir -p "$BUILD_ROOT"
tar -xzf "$PYTHON_TARBALL" -C "$BUILD_ROOT"

cd "$SRC_DIR"
./configure \
  --prefix="$PREFIX" \
  --with-openssl="$OPENSSL_PREFIX_RESOLVED" \
  --enable-ipv6
make -j"$JOBS"
make install

"$PREFIX/bin/python3.11" -c 'import sys,ssl; print(sys.version); print(ssl.OPENSSL_VERSION)'
