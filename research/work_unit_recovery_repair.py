"""Evidence-preserving continuation of the stopped local dummy demonstration.

The original phase stays failed. Preparation restores its charged state; only
the two remaining phases may run, once each, through the verified interpreter.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mechanome.research import Blocked, Campaign  # noqa: E402
from research import work_unit_recovery as original  # noqa: E402

RESEARCH = ROOT / "research"
RUN = RESEARCH / "work_unit_recovery_002"
INPUTS = RESEARCH / "work_unit_recovery_repair_inputs.json"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def save(path, value, exclusive=True):
    temporary = path if exclusive else path.with_suffix(path.suffix + ".pending")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
    if not exclusive:
        temporary.replace(path)


def verified_inputs():
    inputs = read(INPUTS)
    require(inputs["reconciliation_approved"] is True, "Independent acceptance required")
    require(inputs["code_review_approved"] is True, "Code review required")
    for path, expected in inputs["source_sha256"].items():
        require(digest(ROOT / path) == expected, f"Changed input: {path}")
    deadline = dt.datetime.fromisoformat(inputs["evidence_cutoff_utc"].replace("Z", "+00:00"))
    require(dt.datetime.now(dt.timezone.utc) < deadline, "Evidence deadline reached")
    return inputs


def prepare():
    verified_inputs()
    prior = read(RESEARCH / "work_unit_recovery_execution.json")
    require(len(prior["invocations"]) == 1, "Original launch expenditure changed")
    require(prior["invocations"][0]["status"] == "failed_supervision", "Original failure missing")
    approval_path = RESEARCH / "work_unit_recovery_reconciliation_approval.json"
    approval = read(approval_path)
    require(approval["decision"] == "accept_controlled_local_reconciliation_only", "Wrong reconciliation scope")
    for path, expected in approval["evidence_sha256"].items():
        require(digest(ROOT / path) == expected, f"Reconciliation evidence changed: {path}")
    failure = read(RESEARCH / "work_unit_recovery_failure_audit.json")
    lookup = read(RESEARCH / "work_unit_recovery_001" / "process_lookup_cmdlet.json")
    pids = {failure["observed_launcher_pid"], failure["phase_self_reported_pid"]}
    require(set(lookup["queried_pids"]) == pids and not lookup["matches"], "Wrong or nonempty process lookup")
    require(len(lookup["errors"]) == 2 and all(error["id"].startswith("NoProcessFoundForGivenId,") for error in lookup["errors"]), "Explicit PID absence is required")
    require(all(any(str(pid) in error["message"] for error in lookup["errors"]) for pid in pids), "Absence evidence does not identify both PIDs")
    require(dt.datetime.fromisoformat(lookup["observed_at_utc"].replace("Z", "+00:00")) > dt.datetime.fromisoformat(prior["invocations"][0]["exit_observed_at_utc"]), "Process lookup must follow failed supervision")
    RUN.mkdir(exist_ok=False)
    (RUN / "campaign" / "artifacts").mkdir(parents=True)
    (RUN / "evidence").mkdir()
    with zipfile.ZipFile(RESEARCH / "work_unit_recovery_attempt_001.zip") as archive:
        prefix = "research/work_unit_recovery_001/"
        require(archive.read(prefix + "campaign/research.sqlite-wal") == b"", "Unapplied WAL is not supported")
        phase = json.loads(archive.read(prefix + "phase-1.json"))
        require(phase["phase"] == 1 and phase["status"] == "completed", "Original output mismatch")
        names = ["campaign/research.sqlite", "evidence/call-1.json"]
        hashes = phase["audit"]["artifact_hashes"]
        require(len(hashes) == 1 and len(hashes[0]) == 64 and all(c in "0123456789abcdef" for c in hashes[0]), "Unexpected original artifacts")
        names.append("campaign/artifacts/" + hashes[0])
        for name in names:
            with (RUN / name).open("xb") as stream:
                stream.write(archive.read(prefix + name))
    marker = RUN / "evidence" / "call-1.json"
    require(marker.read_bytes() == original.CALL_1, "Original marker mismatch")
    reconciliation = {"kind": "later_controlled_local_reconciliation", "created_at_utc": now(),
                      "approval_sha256": digest(approval_path), "original_phase_status": "failed_supervision",
                      "original_attempt": phase["attempt"], "original_token": phase["token"],
                      "marker_sha256": digest(marker), "rationale": approval["rationale"],
                      "limitations": approval["limitations"], "work_state": "reserved_until_phase2_verification",
                      "prior_phase_launches": 1, "prior_dummy_callbacks": 1}
    campaign = Campaign(RUN / "campaign")
    try:
        audit = campaign.export()
        for table, expected in failure["database_state"].items():
            require(audit[table] == expected, f"Restored state differs from frozen failure: {table}")
        require(audit["work_totals"] == {"dummy": 1}, "Original unit was not retained")
        require(len(audit["work_units"]) == 1 and audit["work_units"][0]["state"] == "reserved", "Original reserved row missing")
        work = audit["work_units"][0]
        require(work["call_id"] == "call-1" and work["task"] == original.TASK_ID and work["attempt"] == phase["attempt"] and work["units"] == 1 and work["kind"] == "dummy", "Original work identity changed")
        require(len(audit["tasks"]) == 1 and audit["tasks"][0]["id"] == original.TASK_ID, "Original task changed")
        require(len(audit["attempts"]) == 1 and audit["attempts"][0]["id"] == phase["attempt"] and audit["attempts"][0]["state"] == "running", "Original attempt changed")
        require(len(audit["lead"]) == 1 and audit["lead"][0]["token"] == phase["token"] and audit["lead"][0]["state"] == "active", "Original lead changed")
        save(RUN / "reconciliation.json", reconciliation)
        campaign.terminate_lead(phase["token"],
                                "Later independently reviewed local reconciliation; original target exit code/ancestry unverified; record SHA256 "
                                + digest(RUN / "reconciliation.json"))
        save(RUN / "prepared-audit.json", campaign.export())
    finally:
        campaign.close()
    save(RUN / "execution.json", {"logical_task": "work-unit-recovery", "attempt_number": 2,
                                  "prior_invocations": prior["invocations"], "prior_dummy_callbacks": 1,
                                  "phase_cap": 3, "dummy_cap": 2, "new_invocations": []})
    print(json.dumps({"prepared": True, "retained_units": 1, "remaining_launches": 2, "remaining_callbacks": 1}))


def phase_two():
    reconciliation = read(RUN / "reconciliation.json")
    require(reconciliation["approval_sha256"] == digest(RESEARCH / "work_unit_recovery_reconciliation_approval.json"), "Reconciliation approval changed")
    require(reconciliation["original_phase_status"] == "failed_supervision", "Prior failure was relabeled")
    campaign = Campaign(RUN / "campaign")
    try:
        token = campaign.acquire_lead("repair-phase-2", ttl=300)
        attempt = reconciliation["original_attempt"]
        before = campaign.export()
        failure = read(RESEARCH / "work_unit_recovery_failure_audit.json")
        for table in ("attempts", "work_units"):
            require(before[table] == failure["database_state"][table], f"Phase2 changed original {table}")
        require(token > reconciliation["original_token"], "Lead token was not advanced")
        require(before["work_totals"] == {"dummy": 1} and len(before["work_units"]) == 1, "Charged unit changed")
        require(before["work_units"][0]["state"] == "reserved" and before["work_units"][0]["call_id"] == "call-1", "Unresolved call changed")
        require(len(before["attempts"]) == 1 and before["attempts"][0]["id"] == attempt and before["attempts"][0]["state"] == "running", "Attempt changed")
        checks = {}
        for call_id, reason in [("call-1", "Reconcile unresolved call"), ("call-new", "before new call ID")]:
            try:
                campaign.run_guarded_work(token, attempt, call_id, "dummy", 1, original.rejected_callback(call_id))
            except Blocked as error:
                require(reason in str(error), f"Unexpected rejection: {error}")
                checks[call_id + "_blocked"] = str(error)
            else:
                raise AssertionError("Unresolved call was allowed")
        marker = RUN / "evidence" / "call-1.json"
        require(marker.read_bytes() == original.CALL_1 and digest(marker) == reconciliation["marker_sha256"], "Marker evidence changed")
        campaign.reconcile_work(token, original.TASK_ID, "call-1", "completed", "Verified exact original marker; later reconciliation record " + digest(RUN / "reconciliation.json"))
        replay = campaign.run_guarded_work(token, attempt, "call-1", "dummy", 1, original.rejected_callback("call-1 replay"))
        require(replay["execute"] is False and replay["status"] == "terminal_duplicate", "Replay was not skipped")
        marker2 = RUN / "evidence" / "call-2.json"
        result = campaign.run_guarded_work(token, attempt, "call-2", "dummy", 1, original.marker_callback(marker2, original.CALL_2))
        require(result["execute"] is True and marker2.read_bytes() == original.CALL_2, "Second marker failed")
        campaign.reconcile_work(token, original.TASK_ID, "call-2", "completed", "Verified exact marker SHA256 " + digest(marker2))
        audit = campaign.export()
        require(audit["work_totals"] == {"dummy": 2} and len(audit["work_units"]) == 2 and all(row["state"] == "completed" for row in audit["work_units"]), "Final work state mismatch")
        checks.update(callback_count=1, original_replay_skipped=True, work_totals=audit["work_totals"])
        return token, attempt, checks, audit
    finally:
        campaign.close()


def child(phase):
    verified_inputs()
    started = now()
    if phase == 2:
        token, attempt, checks, audit = phase_two()
    else:
        token, attempt, checks, audit = original.phase_three(RUN)
        require(len(audit["attempts"]) == 1 and audit["attempts"][0]["state"] == "finished", "Original attempt did not finish")
        require(len(audit["work_units"]) == 2 and all(row["state"] == "completed" for row in audit["work_units"]), "Work remains unresolved")
    save(RUN / f"phase-{phase}.json", {"phase": phase, "status": "completed", "pid": os.getpid(),
                                      "parent_pid": os.getppid(), "token": token, "attempt": attempt,
                                      "checks": checks, "audit": audit, "started_at_utc": started,
                                      "finished_at_utc": now()})


def run(phase):
    inputs = verified_inputs()
    ledger_path = RUN / "execution.json"
    ledger = read(ledger_path)
    rows = ledger["new_invocations"]
    require(len(ledger["prior_invocations"]) == 1 and len(rows) == phase - 2, "Cumulative phase order mismatch")
    require(1 + len(rows) < ledger["phase_cap"] and all(row["status"] == "completed" for row in rows), "Phase cap or unresolved execution blocks launch")
    save(RUN / f"reservation-{phase}.json", {"phase": phase, "reserved_at_utc": now()})
    row = {"phase": phase, "status": "reserved", "reserved_at_utc": now(),
           "command": [inputs["base_executable"], "-B", str(Path(__file__).resolve()), "child", str(phase)],
           "input_sha256": digest(INPUTS), "parent_pid": os.getpid()}
    rows.append(row)
    save(ledger_path, ledger, exclusive=False)
    try:
        with (RUN / f"phase-{phase}.log").open("xb") as log:
            process = subprocess.Popen(row["command"], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            row.update(status="running", pid=process.pid, started_at_utc=now())
            save(ledger_path, ledger, exclusive=False)
            code = process.wait(timeout=30)
            row.update(exit_code=code, exit_observed_at_utc=now())
        require(code == 0, f"Phase exited {code}; no retry")
        output_path = RUN / f"phase-{phase}.json"
        output = read(output_path)
        require(output["status"] == "completed" and output["phase"] == phase and output["pid"] == process.pid and output["parent_pid"] == os.getpid(), "Observed process identity mismatch")
        require(process.pid not in {old["pid"] for old in rows[:-1]}, "Distinct continuation PIDs required")
        receipt = {"phase": phase, "status": "completed", "pid": process.pid, "parent_pid": os.getpid(),
                   "exit_code": code, "exit_observed_at_utc": row["exit_observed_at_utc"],
                   "phase_output_sha256": digest(output_path)}
        save(RUN / f"exit-{phase}.json", receipt)
        campaign = Campaign(RUN / "campaign")
        try:
            lead = campaign.export()["lead"]
            require(len(lead) == 1 and lead[0]["state"] == "active" and lead[0]["token"] == output["token"], "Child must leave current lead active")
            campaign.terminate_lead(output["token"], "Parent observed matching child PID and exit0; receipt SHA256 " + digest(RUN / f"exit-{phase}.json"))
            audit = campaign.export()
            save(RUN / f"post-exit-{phase}.json", audit)
        finally:
            campaign.close()
        row.update(status="completed", completed_at_utc=now(), output_sha256=digest(output_path),
                   exit_receipt_sha256=digest(RUN / f"exit-{phase}.json"))
        save(ledger_path, ledger, exclusive=False)
        print(json.dumps({"phase": phase, "pid": process.pid, "exit_code": code, "work_totals": audit["work_totals"], "lead_state": audit["lead"][0]["state"]}))
    except BaseException as error:
        row.update(status="unknown" if "exit_code" not in row else "failed", error=f"{type(error).__name__}: {error}", observed_at_utc=now())
        save(ledger_path, ledger, exclusive=False)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run", "child"))
    parser.add_argument("phase", type=int, nargs="?", choices=(2, 3))
    args = parser.parse_args()
    if args.action == "prepare":
        require(args.phase is None, "Preparation has no phase")
        prepare()
    else:
        require(args.phase is not None, "Phase required")
        {"run": run, "child": child}[args.action](args.phase)
