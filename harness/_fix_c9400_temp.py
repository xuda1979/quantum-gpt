import os
import sys

sys.path.insert(0, "harness")
import harness_lib as hl

state_dir = os.path.join("harness", "state")
lock_path = os.path.join(state_dir, "locks", "queue-fixer.lock")

tok = hl.acquire_lock(lock_path)
if tok is None:
    print("FAILED_TO_ACQUIRE_LOCK")
    sys.exit(1)

try:
    q = hl.load_queue(state_dir)
    cards = dict()
    for c in q.get("cards", []):
        cards[c.get("id")] = c
    c = cards["C-9393"]
    before = list(c.get("deps", []))
    deps = c.get("deps", [])
    if "C-9394" not in deps:
        deps.append("C-9394")
    after = list(c.get("deps", []))
    print("BEFORE", before)
    print("AFTER", after)
    hl.save_queue(state_dir, q)
    print("SAVED")
finally:
    hl.release_lock(lock_path, tok)
    print("RELEASED")
