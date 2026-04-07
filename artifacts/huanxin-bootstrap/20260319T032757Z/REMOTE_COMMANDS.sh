set -euo pipefail
mkdir -p /root/root/work/quantum-gpt
cd /root/root/work/quantum-gpt

# Create required directories before pasting file contents.
mkdir -p data/seed
mkdir -p evals/runner
mkdir -p evals/tasks/quantum/bell_pair_construction
mkdir -p training

# Paste each file from the local bundle into the matching remote path.
# Example pattern:
# cat > relative/path.py <<'EOF'
# ...paste validated file contents...
# EOF

# After pasting files, run the baseline local-equivalent gate where possible:
python3 evals/runner/run_eval.py
