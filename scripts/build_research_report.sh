#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/research/RESEARCH-REPORT.tex"
OUTDIR="$ROOT/research/build"
LOG="$OUTDIR/RESEARCH-REPORT.log"

mkdir -p "$OUTDIR"

xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory "$OUTDIR" "$SRC"
xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory "$OUTDIR" "$SRC"

if grep -En "LaTeX Warning:|Package .* Warning:|Overfull \\\\hbox|Underfull \\\\hbox|Missing character:|Undefined control sequence|Emergency stop" "$LOG" >/dev/null; then
  echo "TeX warnings detected in $LOG" >&2
  grep -En "LaTeX Warning:|Package .* Warning:|Overfull \\\\hbox|Underfull \\\\hbox|Missing character:|Undefined control sequence|Emergency stop" "$LOG" >&2
  exit 1
fi

echo "Built $OUTDIR/RESEARCH-REPORT.pdf"
