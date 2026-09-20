"""C-9017: every durable-source citation inside a restored shell must RESOLVE.

RED (measured 2026-09-17 against the live QUEUE.json): the C-9017 restore
pass stamped five terminal cards (C-0005, C-0008, C-0037, C-0047,
C-0063) with "Durable completion evidence: standup-2.md ... standup-6.md
EVENTS.jsonl dispatched/reaped ledger" -- but harness/state/standup/
holds ONLY standup-7.md .. standup-37.md (measured: find -iname
'*standup*' over the whole tree). standup-1..6 do not exist anywhere,
so those citations name sources that cannot be checked -- the exact
failure mode this card exists to prevent (acceptance must be derived
from a durable source that exists).

The invariant, scoped to the C-9017 triage set (the shell enumeration
recorded in harness/state/shell_triage_C-9017.md): every source
citation inside acceptance/result/why of a triaged card must resolve --
  - standup-N.md     -> harness/state/standup/standup-N.md exists
  - briefs/<id>.md   -> harness/state/briefs/<id>.md exists
  - C-XXXX card refs -> id present in QUEUE.json OR any EVENTS.jsonl
                        record keyed id/card (durable recovery ledger)

Card-id resolution is checked on acceptance+result only: a restored
"why" embeds the card_added title verbatim (e.g. C-0076's
"(training-container sibling of C-0042)" is the EVENTS.jsonl
card_added title itself), so ids inside why are quotations of a
durable record, not new citations.

Same binding idiom as test_dep_graph_rebaseline_v4_p1_shells.py:
asserted against the LIVE harness/state/QUEUE.json.
"""

import json
import os
import re
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")
EVENTS_PATH = os.path.join(HARNESS_DIR, "state", "EVENTS.jsonl")
TRIAGE_PATH = os.path.join(HARNESS_DIR, "state", "shell_triage_C-9017.md")
STANDUP_DIR = os.path.join(HARNESS_DIR, "state", "standup")
BRIEFS_DIR = os.path.join(HARNESS_DIR, "state", "briefs")

STANDUP_TOKEN = re.compile(r"standup-(\d+)\.md")
BRIEF_TOKEN = re.compile(r"briefs/([A-Za-z0-9_.-]+?)(?:\.md)?(?=[\s,;.)]|$)")
CARD_TOKEN = re.compile(r"\bC-\d{4}\b")
TRIAGE_LINE = re.compile(r"^- (C-\d{4})\b", re.MULTILINE)


def load_live_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_triage_ids():
    with open(TRIAGE_PATH, encoding="utf-8") as f:
        return set(TRIAGE_LINE.findall(f.read()))


def load_event_card_ids():
    ids = set()
    with open(EVENTS_PATH, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            cid = e.get("id") or e.get("card")
            if cid:
                ids.add(cid)
            for tok in CARD_TOKEN.findall(str(e.get("title") or "")):
                ids.add(tok)
    return ids


class TestShellRestoreCitationsResolve(unittest.TestCase):
    def setUp(self):
        for p in (QUEUE_PATH, EVENTS_PATH, TRIAGE_PATH):
            self.assertTrue(os.path.exists(p), "missing " + p)
        self.q = load_live_queue()
        self.cards = dict((c["id"], c) for c in self.q["cards"])
        self.triage_ids = load_triage_ids()
        self.event_ids = load_event_card_ids()

    def test_triage_record_nonempty(self):
        self.assertGreaterEqual(
            len(self.triage_ids),
            26,
            "shell_triage_C-9017.md lost its per-id enumeration",
        )

    def test_standup_citations_resolve(self):
        offenders = []
        for cid in sorted(self.triage_ids):
            c = self.cards.get(cid)
            if not c:
                continue
            text = (
                " ".join(c.get("acceptance") or [])
                + " "
                + (c.get("result") or "")
                + " "
                + (c.get("why") or "")
            )
            for n in sorted(set(STANDUP_TOKEN.findall(text))):
                path = os.path.join(STANDUP_DIR, f"standup-{n}.md")
                if not os.path.exists(path):
                    offenders.append(f"{cid} cites standup-{n}.md MISSING")
        self.assertEqual(
            offenders,
            [],
            "restored shells cite standup files that do not exist "
            "(name only durable sources): " + "; ".join(offenders),
        )

    def test_brief_citations_resolve(self):
        offenders = []
        for cid in sorted(self.triage_ids):
            c = self.cards.get(cid)
            if not c:
                continue
            text = (
                " ".join(c.get("acceptance") or [])
                + " "
                + (c.get("result") or "")
                + " "
                + (c.get("why") or "")
            )
            for b in sorted(set(BRIEF_TOKEN.findall(text))):
                if not os.path.exists(os.path.join(BRIEFS_DIR, b + ".md")):
                    offenders.append(f"{cid} cites briefs/{b}.md MISSING")
        self.assertEqual(
            offenders,
            [],
            "restored shells cite brief files that do not exist: " + "; ".join(offenders),
        )

    def test_card_id_citations_resolve(self):
        offenders = []
        for cid in sorted(self.triage_ids):
            c = self.cards.get(cid)
            if not c:
                continue
            # acceptance+result only -- why quotes the card_added title
            text = " ".join(c.get("acceptance") or []) + " " + (c.get("result") or "")
            for ref in sorted(set(CARD_TOKEN.findall(text))):
                if ref == cid:
                    continue
                if ref not in self.cards and ref not in self.event_ids:
                    offenders.append(f"{cid} cites card {ref}: not in QUEUE.json or EVENTS.jsonl")
        self.assertEqual(
            offenders,
            [],
            "restored shells cite card ids with no durable record: " + "; ".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
