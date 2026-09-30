"""Lead-supervised, three-process dummy recovery demonstration.

The supervisor, not this process, records exit receipts and terminates each
phase's lead after observing normal process exit.  This script never self-
terminates a lead and never runs scientific work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from mechanome.research import Blocked, Campaign, Charter, Result, Task


EXPECTED_COMMIT = "e2fee6b46b790f113849de237d5f7ab849530714"
TASK_ID = "work-unit-recovery-task"
CALL_1 = b'{"call_id":"call-1","kind":"dummy","units":1}\n'
CALL_2 = b'{"call_id":"call-2","kind":"dummy","units":1}\n'


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


def write_exclusive(path: Path, content: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(content)


def task_spec(campaign: Campaign) -> Task:
    source = campaign.put_artifact(b"work-unit-recovery-001 dummy-only source\n")
    return Task(
        id=TASK_ID,
        question="Do guarded dummy reservations survive ordinary process exits?",
        uncertainty="Callback acknowledgement may be lost after evidence is written.",
        alternatives=("stop after unresolved reservation",),
        rationale="Bounded offline recovery demonstration",
        expected_outcomes=("persisted reservation blocks replacement",),
        inputs=(source,),
        required_checks=("exit receipt", "marker hash", "work cap"),
        stop_condition="Three supervised phases or a preserved failure",
        worker="lead-supervised-dummy",
        work_unit_limits=(("dummy", 2),),
    )


def marker_callback(path: Path, content: bytes):
    def callback():
        write_exclusive(path, content)
        return sha256_bytes(content)
    return callback


def rejected_callback(label: str):
    def callback():
        raise AssertionError(f"Rejected callback {label} was invoked")
    return callback


def output_path(run_dir: Path, phase: int) -> Path:
    return run_dir / f"phase-{phase}.json"


def marker_path(run_dir: Path, call_id: str) -> Path:
    return run_dir / "evidence" / f"{call_id}.json"


def work_rows(audit: dict) -> dict:
    return {row["call_id"]: row for row in audit["work_units"]}


def running_attempts(audit: dict) -> list[dict]:
    return [row for row in audit["attempts"] if row["state"] == "running"]


def load_phase_output(run_dir: Path, phase: int) -> tuple[dict, bytes]:
    path = output_path(run_dir, phase)
    content = path.read_bytes()
    body = json.loads(content)
    require(body["phase"] == phase and body["status"] == "completed", "Prior phase output is not completed")
    require(isinstance(body.get("pid"), int) and body["pid"] > 0, "Prior phase PID missing")
    return body, content


def validate_receipt(run_dir: Path, phase: int) -> dict:
    output, content = load_phase_output(run_dir, phase)
    receipt = json.loads((run_dir / f"exit-{phase}.json").read_text(encoding="utf-8"))
    require(receipt.get("phase") == phase, "Exit receipt phase mismatch")
    require(receipt.get("status") == "completed" and receipt.get("exit_code") == 0, "Prior process did not exit successfully")
    require(receipt.get("phase_output_sha256") == sha256_bytes(content), "Prior phase output hash mismatch")
    require(receipt.get("pid") == output["pid"], "Prior output PID mismatch")
    audit = json.loads((run_dir / f"post-exit-{phase}.json").read_text(encoding="utf-8"))
    lead_rows = audit.get("lead", [])
    require(len(lead_rows) == 1 and lead_rows[0].get("state") == "terminated", "Prior lead was not supervisor-terminated")
    require(lead_rows[0].get("token") == output["token"], "Post-exit audit token mismatch")
    return output


def save_phase(run_dir: Path, phase: int, started: str, token, attempt, checks: dict, audit: dict, status="completed", error=None):
    body = {"phase": phase, "status": status, "pid": os.getpid(), "token": token,
            "attempt": attempt, "checks": checks, "audit": audit,
            "started_at_utc": started, "finished_at_utc": now()}
    if error is not None:
        body["error"] = error
    write_exclusive(output_path(run_dir, phase), (json.dumps(body, indent=2, sort_keys=True) + "\n").encode())


def phase_one(run_dir: Path):
    campaign = Campaign(run_dir / "campaign", Charter("work-unit-recovery", "offline dummy recovery", EXPECTED_COMMIT,
                                                         max_workers=1, work_unit_limits=(("dummy", 2),)))
    token = campaign.acquire_lead("phase-1", ttl=300)
    campaign.decide(token, "create one shared recovery attempt", [task_spec(campaign)])
    attempt = campaign.start(token, TASK_ID)
    marker = marker_path(run_dir, "call-1")
    reservation = campaign.run_guarded_work(token, attempt, "call-1", "dummy", 1, marker_callback(marker, CALL_1))
    require(reservation["execute"] is True and marker.read_bytes() == CALL_1, "Phase 1 marker failed")
    checks = {"callback_count": 1, "call_1_state": "reserved", "marker_call_1_sha256": sha256_bytes(CALL_1),
              "work_totals": campaign.work_totals(TASK_ID)}
    audit = campaign.export()
    require(checks["work_totals"] == {"dummy": 1}, "Phase 1 work total mismatch")
    require(work_rows(audit)["call-1"]["state"] == "reserved", "Phase 1 work state mismatch")
    require(len(running_attempts(audit)) == 1, "Phase 1 lacks one running attempt")
    campaign.close()
    return token, attempt, checks, audit


def phase_two(run_dir: Path):
    prior = validate_receipt(run_dir, 1)
    campaign = Campaign(run_dir / "campaign")
    token = campaign.acquire_lead("phase-2", ttl=300)
    require(token != prior["token"], "Phase 2 did not acquire a replacement lead")
    attempt = prior["attempt"]
    checks = {"prior_phase_1_pid": prior["pid"], "same_id_blocked": False, "new_id_blocked": False}
    before = campaign.export()
    require(campaign.work_totals(TASK_ID) == {"dummy": 1}, "Phase 2 persisted work mismatch")
    require(work_rows(before)["call-1"]["state"] == "reserved", "Phase 2 work state mismatch")
    require(len(running_attempts(before)) == 1 and running_attempts(before)[0]["id"] == attempt, "Phase 2 attempt mismatch")
    for call_id, name, reason in (("call-1", "same_id_blocked", "Reconcile unresolved call"),
                                  ("call-new", "new_id_blocked", "before new call ID")):
        try:
            campaign.run_guarded_work(token, attempt, call_id, "dummy", 1, rejected_callback(call_id))
        except Blocked as error:
            require(reason in str(error), f"Unexpected Phase 2 rejection: {error}")
            checks[name] = True
        else:
            raise AssertionError(f"Unresolved {call_id} was not blocked")
    marker = marker_path(run_dir, "call-1")
    require(marker.read_bytes() == CALL_1 and sha256_bytes(marker.read_bytes()) == sha256_bytes(CALL_1), "Call-1 evidence mismatch")
    campaign.reconcile_work(token, TASK_ID, "call-1", "completed", f"marker sha256 {sha256_bytes(CALL_1)}")
    replay = campaign.run_guarded_work(token, attempt, "call-1", "dummy", 1, rejected_callback("terminal-call-1"))
    require(replay["execute"] is False and replay["status"] == "terminal_duplicate", "Call-1 replay executed")
    call_2 = marker_path(run_dir, "call-2")
    reservation = campaign.run_guarded_work(token, attempt, "call-2", "dummy", 1, marker_callback(call_2, CALL_2))
    require(reservation["execute"] is True and call_2.read_bytes() == CALL_2, "Phase 2 marker failed")
    campaign.reconcile_work(token, TASK_ID, "call-2", "completed", f"marker sha256 {sha256_bytes(CALL_2)}")
    checks.update({"terminal_replay_skipped": True, "callback_count": 1, "marker_call_2_sha256": sha256_bytes(CALL_2),
                   "work_totals": campaign.work_totals(TASK_ID), "pid_differs_prior": os.getpid() != prior["pid"]})
    audit = campaign.export()
    campaign.close()
    return token, attempt, checks, audit


def phase_three(run_dir: Path):
    prior = validate_receipt(run_dir, 2)
    campaign = Campaign(run_dir / "campaign")
    token = campaign.acquire_lead("phase-3", ttl=300)
    require(token != prior["token"], "Phase 3 did not acquire a replacement lead")
    attempt = prior["attempt"]
    checks = {"prior_phase_2_pid": prior["pid"], "terminal_replays_skipped": []}
    before = campaign.export()
    states = work_rows(before)
    require(campaign.work_totals(TASK_ID) == {"dummy": 2}, "Phase 3 cumulative work mismatch")
    require({name: states[name]["state"] for name in ("call-1", "call-2")} == {"call-1": "completed", "call-2": "completed"}, "Phase 3 terminal work mismatch")
    require(len(running_attempts(before)) == 1 and running_attempts(before)[0]["id"] == attempt, "Phase 3 attempt mismatch")
    for call_id in ("call-1", "call-2"):
        replay = campaign.run_guarded_work(token, attempt, call_id, "dummy", 1, rejected_callback(f"terminal-{call_id}"))
        require(replay["execute"] is False and replay["status"] == "terminal_duplicate", "Terminal replay executed")
        checks["terminal_replays_skipped"].append(call_id)
    try:
        campaign.run_guarded_work(token, attempt, "call-3", "dummy", 1, rejected_callback("over-cap"))
    except Blocked as error:
        require("Campaign work-unit cap" in str(error), f"Unexpected cap rejection: {error}")
        checks["over_cap_blocked"] = True
    else:
        raise AssertionError("Over-cap request was not blocked")
    for call_id, expected in (("call-1", CALL_1), ("call-2", CALL_2)):
        content = marker_path(run_dir, call_id).read_bytes()
        require(content == expected, f"{call_id} evidence mismatch")
    require(sorted(path.name for path in (run_dir / "evidence").iterdir()) == ["call-1.json", "call-2.json"], "Evidence directory has unexpected markers")
    audit_before_finish = campaign.export()
    artifact = campaign.put_artifact((json.dumps(audit_before_finish, sort_keys=True) + "\n").encode())
    campaign.finish(attempt, Result("succeeded", "inconclusive", "valid", "dummy recovery complete", (artifact,)))
    checks.update({"callback_count": 0, "work_totals": campaign.work_totals(TASK_ID), "software_artifact": artifact,
                   "pid_differs_prior": os.getpid() != prior["pid"]})
    audit = campaign.export()
    campaign.close()
    return token, attempt, checks, audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", type=int, choices=(1, 2, 3))
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    require(args.commit == EXPECTED_COMMIT, "Unexpected commit argument")
    args.run_dir.mkdir(parents=True, exist_ok=True)
    (args.run_dir / "evidence").mkdir(exist_ok=True)
    started, token, attempt = now(), None, None
    try:
        runner = {1: phase_one, 2: phase_two, 3: phase_three}[args.phase]
        token, attempt, checks, audit = runner(args.run_dir)
        save_phase(args.run_dir, args.phase, started, token, attempt, checks, audit)
    except Exception as error:
        if not output_path(args.run_dir, args.phase).exists():
            save_phase(args.run_dir, args.phase, started, token, attempt, {}, {}, "failed", f"{type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    main()
