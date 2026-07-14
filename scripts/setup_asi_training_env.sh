#!/usr/bin/env bash
# Setup ASI training environment: install peft, accelerate, transformers 5.6.0, huggingface_hub.
# Run this on the Huanxin NPU box (ASI1/ASI2/ASI3) after the container is freshly started.
# Usage: bash scripts/setup_asi_training_env.sh
set -euo pipefail

echo "=== Installing Python dependencies for Qwen3.6 SFT training ==="

# 1. Copy peft and accelerate from py_deps to site-packages
SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])")
echo "site-packages: $SITE_PACKAGES"

if [[ -d /root/work/filestorage/py_deps/peft ]]; then
  cp -rn /root/work/filestorage/py_deps/peft "$SITE_PACKAGES/"
  cp -rn /root/work/filestorage/py_deps/peft-0.19.1.dist-info "$SITE_PACKAGES/"
  echo " Installed peft 0.19.1 from py_deps"
elif [[ -f /root/work/quantum-gpt/tools/wheels/peft-0.14.0-py3-none-any.whl ]]; then
  pip3 install --no-deps /root/work/quantum-gpt/tools/wheels/peft-0.14.0-py3-none-any.whl
  echo " Installed peft 0.14.0 from wheel"
else
  echo "ERROR: peft not found" >&2; exit 1
fi

if [[ -d /root/work/filestorage/py_deps/accelerate ]]; then
  cp -rn /root/work/filestorage/py_deps/accelerate "$SITE_PACKAGES/"
  cp -rn /root/work/filestorage/py_deps/accelerate-1.14.0.dist-info "$SITE_PACKAGES/"
  echo " Installed accelerate 1.14.0 from py_deps"
elif [[ -f /root/work/quantum-gpt/tools/wheels/accelerate-1.4.0-py3-none-any.whl ]]; then
  pip3 install --no-deps /root/work/quantum-gpt/tools/wheels/accelerate-1.4.0-py3-none-any.whl
  echo " Installed accelerate 1.4.0 from wheel"
else
  echo "ERROR: accelerate not found" >&2; exit 1
fi

# 2. Install transformers 5.6.0 (has native qwen3_5 support)
if [[ -f /root/work/software/quantum-gpt/vendor/transformers-560-aarch64-py311/transformers-5.6.0-py3-none-any.whl ]]; then
  pip3 install --no-deps --force-reinstall /root/work/software/quantum-gpt/vendor/transformers-560-aarch64-py311/transformers-5.6.0-py3-none-any.whl
  echo " Installed transformers 5.6.0"
else
  echo "ERROR: transformers 5.6.0 wheel not found" >&2; exit 1
fi

# 3. Install huggingface_hub 1.22.0 (compatible with transformers 5.6.0)
if [[ -f /root/work/software/quantum-gpt/vendor/transformers-560-aarch64-py311/huggingface_hub-1.22.0-py3-none-any.whl ]]; then
  pip3 install --no-deps --force-reinstall /root/work/software/quantum-gpt/vendor/transformers-560-aarch64-py311/huggingface_hub-1.22.0-py3-none-any.whl
  echo " Installed huggingface_hub 1.22.0"
else
  echo "ERROR: huggingface_hub wheel not found" >&2; exit 1
fi

# 4. Apply NPU modeling patch
if [[ -f /root/work/software/quantum-gpt/scripts/patch_qwen3_5_npu_modeling.py ]]; then
  python3 /root/work/software/quantum-gpt/scripts/patch_qwen3_5_npu_modeling.py
  echo " Applied NPU modeling patch"
fi

# 5. Verify
echo "=== Verification ==="
python3 -c "
import transformers, huggingface_hub, peft, accelerate, torch
import transformers.models.qwen3_5
print(f'transformers={transformers.__version__}')
print(f'huggingface_hub={huggingface_hub.__version__}')
print(f'peft={peft.__version__}')
print(f'accelerate={accelerate.__version__}')
print(f'torch={torch.__version__}')
print('qwen3_5 import OK')
try:
    import torch_npu
    print(f'torch_npu={torch_npu.__version__}, npu_available={torch.npu.is_available()}')
except:
    print('torch_npu not available')
print('=== SETUP COMPLETE ===')
"
