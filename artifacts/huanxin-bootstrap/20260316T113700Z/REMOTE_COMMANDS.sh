set -euo pipefail
mkdir -p /root/root/work/quantum-gpt
cd /root/root/work/quantum-gpt

# Create required directories before pasting file contents.
mkdir -p data/seed
mkdir -p data/seed/splits-auto-seed
mkdir -p evals/runner
mkdir -p research

# Paste each file from the local bundle into the matching remote path.
# Example pattern:
# cat > relative/path.py <<'EOF'
# ...paste validated file contents...
# EOF

# After pasting files, run the baseline local-equivalent gate where possible:
python3 evals/runner/run_eval.py
