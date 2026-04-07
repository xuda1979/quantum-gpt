import json
from pathlib import Path
p = Path('/root/root/work/quantum-gpt/outputs/fast-lora-qwen25-1p5b-interface-prefix-semantic-v4-true20/metrics.json')
if p.exists():
    print(p.read_text())
else:
    print(json.dumps({'exists': False, 'path': str(p)}))
