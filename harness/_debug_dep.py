import os
import sys

sys.path.insert(0, "harness")
import harness_lib as H
import qgh

for sub in ("agents", "briefs", "locks", "standup", "probes"):
    os.makedirs(os.path.join(qgh.STATE, sub), exist_ok=True)
ev = os.path.join(qgh.STATE, "EVENTS.jsonl")
if os.path.exists(ev):
    os.remove(ev)
qgh.save_json(os.path.join(qgh.STATE, "QUEUE.json"), {"cards": [], "seq": 0})
qgh.save_json(os.path.join(qgh.STATE, "FLEET.json"), {"agents": []})


def card(title, lane="fixer", deps=None, **kw):
    kw.setdefault("why", "goal edge")
    kw.setdefault("acceptance", ["acceptance criteria"])
    return H.new_card(title=title, lane=lane, deps=deps or [], **kw)


q = qgh.load_queue(qgh.STATE)
blocker = H.add_card(q, card("hopeless blocker"))
blocker["status"] = "dead"
blocker["bounce_reason"] = "genuine failure 3 strikes"
H.add_card(q, card("recovery owner", deps=[blocker["id"]]))
qgh.save_queue(qgh.STATE, q)

ev = os.path.join(qgh.STATE, "EVENTS.jsonl")
if os.path.exists(ev):
    os.remove(ev)
q = qgh.load_queue(qgh.STATE)
q["cards"] = [c for c in q["cards"] if c["id"] == blocker["id"]]
qgh.save_queue(qgh.STATE, q)

q = qgh.load_queue(qgh.STATE)
print(
    "Before: cards={} statuses={}".format(
        [c["id"] for c in q["cards"]], [c["status"] for c in q["cards"]]
    )
)
print("Before: crc=%d ptn=%s" % (qgh.claimable_ready_count(q), qgh.planner_topup_needed(q)))

qgh._reconcile_dep_blockers()

q = qgh.load_queue(qgh.STATE)
print(
    "After: cards={} statuses={}".format(
        [c["id"] for c in q["cards"]], [c["status"] for c in q["cards"]]
    )
)
print("After: crc=%d ptn=%s" % (qgh.claimable_ready_count(q), qgh.planner_topup_needed(q)))
