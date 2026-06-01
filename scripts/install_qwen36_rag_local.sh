#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$ROOT/.venv-qwen36-rag}"
MODEL_SIZE="27b"
QUANTIZATION="Q4_K_M"
DOCS_DIR="$ROOT/docs/external/quantum-sdk-docs-latest"
ISQ_TRAIN_COT_RAG_DIR="$ROOT/docs/generated/isq_train_cot_rag"
INDEX_PATH="$ROOT/artifacts/quantum-rag/qwen36-quantum-docs-index.pkl.gz"
SUMMARY_JSON="$ROOT/artifacts/quantum-rag/qwen36-quantum-docs-summary.json"
FETCH_MANIFEST="$ROOT/artifacts/quantum-rag/qwen36-docs-fetch-manifest.json"
MAX_PAGES_PER_SOURCE="${QWEN36_RAG_MAX_PAGES_PER_SOURCE:-80}"
MAX_DEPTH="${QWEN36_RAG_MAX_DEPTH:-8}"
SLEEP_SECONDS="${QWEN36_RAG_SLEEP_SECONDS:-0.05}"
SKIP_MODEL_DOWNLOAD=0
SKIP_DOC_FETCH=0
SKIP_LLAMA_INSTALL=0
DRY_RUN=0
SMOKE=0
DOC_SOURCES=()

usage() {
  cat <<'EOF'
Usage: scripts/install_qwen36_rag_local.sh [options]

Install the CPU-only Qwen3.6 + quantum-doc RAG stack locally.

Options:
  --model-size 27b               Model family to download (default: 27b).
  --quantization NAME            GGUF quantization (default: Q4_K_M).
  --max-pages-per-source N       Doc crawl cap per source; 0 means uncapped (default: 80).
  --max-depth N                  Link-follow depth for each doc source.
  --sleep-seconds N              Delay between doc fetches (default: 0.05).
  --source ID                    Crawl only one source id; repeatable.
  --exhaustive-docs              Crawl without a per-source page cap.
  --skip-model-download          Install deps and build RAG, but do not download GGUF.
  --skip-doc-fetch               Do not fetch docs; build from existing docs directory.
  --skip-llama-install           Do not install/build llama.cpp.
  --dry-run                      Print planned actions without downloads or installs.
  --smoke                        Fast local smoke: Arclight only, 2 pages, no model download.
  -h, --help                     Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model-size)
      MODEL_SIZE="$2"
      shift 2
      ;;
    --quantization)
      QUANTIZATION="$2"
      shift 2
      ;;
    --max-pages-per-source)
      MAX_PAGES_PER_SOURCE="$2"
      shift 2
      ;;
    --max-depth)
      MAX_DEPTH="$2"
      shift 2
      ;;
    --sleep-seconds)
      SLEEP_SECONDS="$2"
      shift 2
      ;;
    --source)
      DOC_SOURCES+=("$2")
      shift 2
      ;;
    --exhaustive-docs)
      MAX_PAGES_PER_SOURCE=0
      shift
      ;;
    --skip-model-download)
      SKIP_MODEL_DOWNLOAD=1
      shift
      ;;
    --skip-doc-fetch)
      SKIP_DOC_FETCH=1
      shift
      ;;
    --skip-llama-install)
      SKIP_LLAMA_INSTALL=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --smoke)
      SMOKE=1
      SKIP_MODEL_DOWNLOAD=1
      SKIP_LLAMA_INSTALL=1
      MAX_PAGES_PER_SOURCE=2
      MAX_DEPTH=1
      SLEEP_SECONDS=0
      DOC_SOURCES=("arclight-isq")
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$MODEL_SIZE" in
  27b)
    HF_REPO="unsloth/Qwen3.6-27B-GGUF"
    MODEL_STEM="Qwen3.6-27B"
    MODEL_DIR="$ROOT/models/Qwen3.6-27B-GGUF"
    ;;
  *)
    echo "Unsupported --model-size '$MODEL_SIZE'. This release supports 27b." >&2
    exit 2
    ;;
esac

case "$QUANTIZATION" in
  UD-*)
    MODEL_FILE="${MODEL_STEM}-${QUANTIZATION}.gguf"
    ;;
  IQ2_M|IQ2_XXS|IQ3_XXS|Q2_K_XL|Q3_K_XL|Q4_K_XL|Q5_K_XL|Q6_K_XL|Q8_K_XL)
    MODEL_FILE="${MODEL_STEM}-UD-${QUANTIZATION}.gguf"
    ;;
  *)
    MODEL_FILE="${MODEL_STEM}-${QUANTIZATION}.gguf"
    ;;
esac

ENV_FILE="$ROOT/.qwen36-rag-local.env"

run() {
  echo "+ $*"
  if [[ "$DRY_RUN" == "0" ]]; then
    "$@"
  fi
}

echo "== Qwen3.6 local quantum RAG installer =="
echo "root: $ROOT"
echo "model: $HF_REPO :: $MODEL_FILE"
echo "docs:  $DOCS_DIR"
echo "index: $INDEX_PATH"

if [[ "$DRY_RUN" == "1" ]]; then
  echo "dry-run: no changes will be made"
fi

run "$PYTHON_BIN" -m venv "$VENV_DIR"
if [[ "$DRY_RUN" == "0" ]]; then
  source "$VENV_DIR/bin/activate"
else
  echo "+ source $VENV_DIR/bin/activate"
fi
run python -m pip install --upgrade pip
run python -m pip install -r "$ROOT/requirements/qwen36-rag-local.txt"

if [[ "$SKIP_LLAMA_INSTALL" == "0" ]]; then
  if command -v llama-server >/dev/null 2>&1; then
    LLAMA_SERVER="$(command -v llama-server)"
  elif command -v brew >/dev/null 2>&1 && [[ "$(uname -s)" == "Darwin" ]]; then
    if [[ "$DRY_RUN" == "1" ]]; then
      run brew install llama.cpp
    else
      echo "+ brew install llama.cpp"
      if ! brew install llama.cpp; then
        if command -v llama-server >/dev/null 2>&1; then
          echo "brew returned nonzero, but llama-server is available; continuing."
        else
          echo "brew install llama.cpp failed and llama-server is unavailable." >&2
          exit 1
        fi
      fi
    fi
    LLAMA_SERVER="$(command -v llama-server || true)"
  else
    LLAMA_CPP_DIR="$ROOT/.local/llama.cpp"
    if [[ ! -d "$LLAMA_CPP_DIR/.git" ]]; then
      run git clone --depth 1 https://github.com/ggml-org/llama.cpp "$LLAMA_CPP_DIR"
    fi
    run cmake -S "$LLAMA_CPP_DIR" -B "$LLAMA_CPP_DIR/build" -DGGML_CUDA=OFF -DGGML_METAL=OFF -DLLAMA_BUILD_SERVER=ON -DCMAKE_BUILD_TYPE=Release
    run cmake --build "$LLAMA_CPP_DIR/build" --config Release --parallel
    LLAMA_SERVER="$LLAMA_CPP_DIR/build/bin/llama-server"
  fi
else
  LLAMA_SERVER="${LLAMA_SERVER:-llama-server}"
fi

if [[ "$SKIP_MODEL_DOWNLOAD" == "0" ]]; then
  run mkdir -p "$MODEL_DIR"
  run python - "$HF_REPO" "$MODEL_FILE" "$MODEL_DIR" <<'PY'
import inspect
import sys
from huggingface_hub import hf_hub_download

repo_id, filename, local_dir = sys.argv[1:4]
kwargs = {
    "repo_id": repo_id,
    "filename": filename,
    "local_dir": local_dir,
}
parameters = inspect.signature(hf_hub_download).parameters
if "local_dir_use_symlinks" in parameters:
    kwargs["local_dir_use_symlinks"] = False
if "resume_download" in parameters:
    kwargs["resume_download"] = True
path = hf_hub_download(**kwargs)
print(path)
PY
fi

if [[ "$SKIP_DOC_FETCH" == "0" ]]; then
  FETCH_ARGS=(
    "$ROOT/scripts/fetch_quantum_docs.py"
    --output-dir "$DOCS_DIR"
    --manifest-json "$FETCH_MANIFEST"
    --max-pages-per-source "$MAX_PAGES_PER_SOURCE"
    --max-depth "$MAX_DEPTH"
    --sleep-seconds "$SLEEP_SECONDS"
  )
  if [[ ${#DOC_SOURCES[@]} -gt 0 ]]; then
    for source_id in "${DOC_SOURCES[@]}"; do
      FETCH_ARGS+=(--source "$source_id")
    done
  fi
  run python "${FETCH_ARGS[@]}"
fi

run python "$ROOT/scripts/build_quantum_rag.py" \
  --root "$ROOT/docs/quantum_libraries" \
  --root "$ISQ_TRAIN_COT_RAG_DIR" \
  --root "$DOCS_DIR" \
  --output "$INDEX_PATH" \
  --summary-json "$SUMMARY_JSON" \
  --chunk-size 1800 \
  --chunk-overlap 240 \
  --min-chunk-chars 180 \
  --dense-components 256

if [[ "$DRY_RUN" == "0" ]]; then
  cat > "$ENV_FILE" <<EOF
QWEN36_RAG_ROOT="$ROOT"
QWEN36_RAG_VENV="$VENV_DIR"
QWEN36_RAG_MODEL_REPO="$HF_REPO"
QWEN36_RAG_MODEL_FILE="$MODEL_FILE"
QWEN36_RAG_MODEL_PATH="$MODEL_DIR/$MODEL_FILE"
QWEN36_RAG_INDEX="$INDEX_PATH"
QWEN36_RAG_DOCS_DIR="$DOCS_DIR"
QWEN36_RAG_SUMMARY_JSON="$SUMMARY_JSON"
QWEN36_RAG_FETCH_MANIFEST="$FETCH_MANIFEST"
QWEN36_RAG_LLAMA_SERVER="${LLAMA_SERVER:-llama-server}"
QWEN36_RAG_HOST="127.0.0.1"
QWEN36_RAG_PORT="8011"
QWEN36_RAG_CTX_SIZE="8192"
QWEN36_RAG_MODEL_ALIAS="qwen3.6-${MODEL_SIZE}-rag"
EOF
fi

echo "== done =="
echo "env: $ENV_FILE"
echo "preflight: scripts/check_qwen36_rag_local.py"
echo "start server: scripts/start_qwen36_rag_local.sh"
echo "query: scripts/query_qwen36_rag_local.sh 'How do I build a Bell pair in Qiskit?'"
