# Huanxin bootstrap command sheet
# bundle_label: huanxin-cpu-bootstrap
# created_at_utc: 2026-03-16T14:35:22.052674+00:00
# remote_root: /root/root/work/quantum-gpt

set -euo pipefail
mkdir -p /root/root/work/quantum-gpt
cd /root/root/work/quantum-gpt
pwd
python3 --version

# Paste validated files below, preserving exact relative paths.
# sha256 19119d3982552ad4d5d7adb24e5d72380d012da25120485b81b547723e2cf4ed  training/requirements-huanxin-cpu.txt
mkdir -p training
cat > training/requirements-huanxin-cpu.txt <<'EOF'
# paste local contents of training/requirements-huanxin-cpu.txt here
EOF

# sha256 3274a9bf23988d4b9e20b3bcb2da4873ac204538606fc09812cfeab02edadd9a  training/huanxin_cpu_smoke.py
mkdir -p training
cat > training/huanxin_cpu_smoke.py <<'EOF'
# paste local contents of training/huanxin_cpu_smoke.py here
EOF

# sha256 6f1c12e33ef85b1ee13aa6642a8b52dccdeb0629fdb943f3d250c4ac07bd3c39  training/qwen_sft_peft.py
mkdir -p training
cat > training/qwen_sft_peft.py <<'EOF'
# paste local contents of training/qwen_sft_peft.py here
EOF

# sha256 544881061873c41694dd94950e482431bea1fb184d3589eba8e792596e7396ca  data/seed/train-chat.jsonl
mkdir -p data/seed
cat > data/seed/train-chat.jsonl <<'EOF'
# paste local contents of data/seed/train-chat.jsonl here
EOF

# sha256 d87c741f094d89ff44e960e017932358a8eed63b0de1d5cd2e4b57e3e2b9aeac  data/seed/splits-auto-seed/train.jsonl
mkdir -p data/seed/splits-auto-seed
cat > data/seed/splits-auto-seed/train.jsonl <<'EOF'
# paste local contents of data/seed/splits-auto-seed/train.jsonl here
EOF

# sha256 f6219bd726decb537d0d583410170af6cbb37bd00328666424ee059f50b5b41c  data/seed/splits-auto-seed/val.jsonl
mkdir -p data/seed/splits-auto-seed
cat > data/seed/splits-auto-seed/val.jsonl <<'EOF'
# paste local contents of data/seed/splits-auto-seed/val.jsonl here
EOF

# sha256 cd270e52f276ec28204583019518ad67c0d41ebcc88039885c25c95b2ed4a51c  research/huanxin-remote-env-manifest.md
mkdir -p research
cat > research/huanxin-remote-env-manifest.md <<'EOF'
# paste local contents of research/huanxin-remote-env-manifest.md here
EOF

# sha256 9ed56ffc4fe2c6418daef33af1f9c43f48364f8d93f6d2364f016b3b8cbc8614  research/huanxin-remote-bootstrap-plan.md
mkdir -p research
cat > research/huanxin-remote-bootstrap-plan.md <<'EOF'
# paste local contents of research/huanxin-remote-bootstrap-plan.md here
EOF

# sha256 3858d46e64359c5f0f9458316839a270b64fa6199e75da38c643dfdf9f576135  research/huanxin-cpu-bootstrap-sequence.md
mkdir -p research
cat > research/huanxin-cpu-bootstrap-sequence.md <<'EOF'
# paste local contents of research/huanxin-cpu-bootstrap-sequence.md here
EOF

# Local-file syntax preflight on the remote host before package install.
python3 -m py_compile training/huanxin_cpu_smoke.py training/qwen_sft_peft.py

# Install the minimal CPU bootstrap stack.
python3 -m pip install --upgrade pip
python3 -m pip install -r training/requirements-huanxin-cpu.txt

# Tokenizer and dataset smoke.
python3 training/huanxin_cpu_smoke.py --model-name /root/root/work/quantum-gpt/models/OmniCoder-9B --dataset data/seed/splits-auto-seed/train.jsonl

# Optional full model-load smoke.
python3 training/huanxin_cpu_smoke.py --model-name /root/root/work/quantum-gpt/models/OmniCoder-9B --dataset data/seed/splits-auto-seed/train.jsonl --load-model

# Optional 1-step PEFT startup smoke after model load succeeds.
python3 training/qwen_sft_peft.py --model-name /root/root/work/quantum-gpt/models/OmniCoder-9B --train-file data/seed/splits-auto-seed/train.jsonl --eval-file data/seed/splits-auto-seed/val.jsonl --output-dir outputs/qwen35-1p5b-peft-smoke --device cpu --max-steps 1 --per-device-batch-size 1 --gradient-accumulation-steps 1

