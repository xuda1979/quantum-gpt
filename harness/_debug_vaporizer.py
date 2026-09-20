import importlib
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

tmp = tempfile.mkdtemp(prefix="qgh-vapor-")
QGH_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qgh.py")

os.environ["QGH_STATE_DIR"] = tmp
spec = importlib.util.spec_from_file_location("qgh_vapor_test", QGH_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.cmd_init(None)

H = mod.H


def _card(mod, title, lane, **over):
    c = mod.H.new_card(title, lane, "goal edge", ["acceptance"], budget_min=5)
    for k, v in over.items():
        c[k] = v
    return c


expired = "2026-09-09T01:00:00Z"
cards = [
    _card(
        mod,
        "runner-dead",
        "fixer",
        id="C-0001",
        status="running",
        deadline_utc=expired,
        claimed_by=99999,
    ),
    _card(mod, "ready-0002", "fixer", id="C-0002", status="ready"),
    _card(mod, "ready-0003", "fixer", id="C-0003", status="ready"),
    _card(mod, "ready-0004", "fixer", id="C-0004", status="ready"),
    _card(mod, "ready-0005", "fixer", id="C-0005", status="ready"),
]
H.save_json(os.path.join(tmp, "QUEUE.json"), dict(cards=cards, seq=5))

q_disk = H.load_queue(tmp)
add_a = _card(mod, "concurrent-add-A", "fixer", id="C-0006", status="ready")
add_b = _card(mod, "concurrent-add-B", "fixer", id="C-0008", status="ready")
H.add_card(q_disk, add_a, state_dir=tmp)
H.add_card(q_disk, add_b, state_dir=tmp)
H.save_queue(tmp, q_disk)

disk_queue = json.load(open(os.path.join(tmp, "QUEUE.json")))
print("Disk has %d cards: %s" % (len(disk_queue["cards"]), [c["id"] for c in disk_queue["cards"]]))

stale = dict(cards=[dict(c) for c in cards], seq=5)
real_load = H.load_json


def _stale_load(path, default=None):
    return stale if str(path).endswith("QUEUE.json") else real_load(path, default)


H.load_json = _stale_load

bounced = H.bounce_dead_running_cards(tmp, pid_alive_fn=lambda pid: False)
H.load_json = real_load

print(f"Bounced: {bounced}")

result = json.load(open(os.path.join(tmp, "QUEUE.json")))
ids = set(c["id"] for c in result["cards"])
print("After bounce, %d cards: %s" % (len(result["cards"]), sorted(ids)))
print("C-0006 in ids: %s" % ("C-0006" in ids))
print("C-0008 in ids: %s" % ("C-0008" in ids))

events_path = os.path.join(tmp, "EVENTS.jsonl")
if os.path.exists(events_path):
    events = [l for l in open(events_path) if l.strip()]
    print("Events: %d lines" % len(events))
    for e in events:
        print(f"  {e.strip()}")
else:
    print("No EVENTS.jsonl")

terminal = H.history_terminal_card_ids(tmp)
print(f"Terminal ids: {terminal}")

shutil.rmtree(tmp)
