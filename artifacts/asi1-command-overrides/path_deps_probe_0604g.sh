set -euo pipefail
echo __ASI1_PATH_DEPS_0604G__
pwd
ls -ld /workspace/quantum-gpt || true
ls -ld /root/work/filestorage/Qwen3.6-35B-A3B || true
python3 -c "import importlib.util as u; print('torch',u.find_spec('torch') is not None); print('torch_npu',u.find_spec('torch_npu') is not None); print('transformers',u.find_spec('transformers') is not None); print('peft',u.find_spec('peft') is not None); print('accelerate',u.find_spec('accelerate') is not None)"
echo __ASI1_PATH_DEPS_DONE__
