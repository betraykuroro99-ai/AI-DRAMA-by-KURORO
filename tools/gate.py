"""Human confirmation gates. Downstream tools refuse to run until the required gate is approved.

  gate.py <project> status
  gate.py <project> request <gate> --summary "<what the human is asked to confirm>"
  gate.py <project> approve <gate> [--note "<human's words>"]
  gate.py <project> reject  <gate> --note "<human's reason / requested changes>"

Gates: source, anchors_plan, anchors_review, voices_review, board, plan:<shot>, review:<shot>, assembly
Rules enforced here:
- Order: a gate can only be requested or approved after every earlier gate in ORDER is approved;
  plan:<shot>, review:<shot> and assembly need all of ORDER. If an earlier gate is rejected or
  re-requested later, everything after it stops counting as approved until it is approved again.
- story.json must pass check_story.py for its stage before anchors_plan, anchors_review,
  voices_review or board can be requested or approved.
- Only a requested (pending) gate can be approved. A plan:<shot> approval covers one run of
  run_shot.py: it becomes "used" once a paid task is submitted, so a re-roll needs --plan and a new approval.
Approvals are only recorded after the human confirms in chat; the brain never self-approves.
"""
import json
import os
import sys
import time
from pathlib import Path

ORDER = ["source", "anchors_plan", "anchors_review", "voices_review", "board"]
STORY_CHECKED = ORDER[1:]  # gates where the human is shown story.json content: it must be well-formed first
LABEL = {"pending": "pending", "approved": "approved", "rejected": "rejected", "used": "used", None: "not requested"}


def path(proj):
    return Path(proj).resolve() / "workflow.json"


def load(proj):
    p = path(proj)
    return json.loads(p.read_text()) if p.exists() else {"gates": {}, "log": []}


def save(proj, wf):
    tmp = path(proj).with_suffix(".json.tmp")
    tmp.write_text(json.dumps(wf, ensure_ascii=False, indent=1))
    os.replace(tmp, path(proj))


def check_name(gate):
    if not (gate in ORDER or gate == "assembly" or (gate.startswith(("plan:", "review:")) and gate.split(":", 1)[1])):
        sys.exit(f"Unknown gate: {gate} (available: {', '.join(ORDER)}, plan:<shot>, review:<shot>, assembly)")


def prereqs(gate):
    """Gates that must be approved before this one can be requested, approved or relied on."""
    return ORDER[:ORDER.index(gate)] if gate in ORDER else list(ORDER)


def status(proj, gate, wf=None):
    return (wf or load(proj))["gates"].get(gate, {}).get("status")


def missing(proj, gate, wf=None):
    wf = wf or load(proj)
    return [g for g in [*prereqs(gate), gate] if status(proj, g, wf) != "approved"]


def is_approved(proj, gate):
    return not missing(proj, gate)


def require(proj, *gates):
    wf = load(proj)
    lack = []
    for gate in gates:
        for g in missing(proj, gate, wf):
            item = f"{g}({LABEL.get(status(proj, g, wf), status(proj, g, wf))})"
            if item not in lack:
                lack.append(item)
    if lack:
        sys.exit("Waiting for human approval: " + ", ".join(lack) + " (request the gate and ask the user before running gate.py approve)")


def set_status(proj, gate, status_, note="", summary=""):
    check_name(gate)
    wf = load(proj)
    if status_ in ("pending", "approved"):
        before = [g for g in prereqs(gate) if status(proj, g, wf) != "approved"]
        if before:
            sys.exit(f"Prerequisite gates for {gate} are not approved: " + ", ".join(before))
    if status_ in ("pending", "approved") and gate in STORY_CHECKED:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import check_story
        errors, _ = check_story.check(Path(proj).resolve(), gate)
        if errors:
            sys.exit(f"Fix story.json before requesting {gate}: \n" + "\n".join("- " + e for e in errors))
    if status_ == "approved" and status(proj, gate, wf) != "pending":
        now = status(proj, gate, wf)
        hint = "This approval was used; run run_shot.py --plan and request a new approval for a reroll" if now == "used" else "Request the gate first (gate.py request or the corresponding tool), then ask the user"
        sys.exit(f"{gate} is {LABEL.get(now, now)}; cannot approve directly: {hint}")
    if status_ == "rejected" and status(proj, gate, wf) is None:
        sys.exit(f"{gate} has not been requested")
    g = wf["gates"].setdefault(gate, {})
    g.update({"status": status_, "at": time.strftime("%Y-%m-%d %H:%M:%S")})
    if note:
        g["note"] = note
    if summary:
        g["summary"] = summary
    wf["log"].append({"gate": gate, "status": status_, "note": note, "summary": summary, "at": g["at"]})
    save(proj, wf)
    print(json.dumps({gate: g}, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[2] not in ("status", "request", "approve", "reject") or (sys.argv[2] != "status" and len(sys.argv) < 4):
        sys.exit(__doc__)
    proj, cmd = sys.argv[1], sys.argv[2]
    if not Path(proj).is_dir():
        sys.exit(f"Project not found: {proj}")
    args = sys.argv[3:]
    opt = lambda k: args[args.index(k) + 1] if k in args and args.index(k) + 1 < len(args) else ""
    if cmd == "status":
        wf = load(proj)
        for k, v in wf["gates"].items():
            print(f"{k:18} {v['status']:10} {v.get('at', '')}  {v.get('note', '')[:60]}")
    elif cmd == "request":
        set_status(proj, args[0], "pending", summary=opt("--summary"))
    elif cmd == "approve":
        set_status(proj, args[0], "approved", note=opt("--note"))
    elif cmd == "reject":
        set_status(proj, args[0], "rejected", note=opt("--note"))
