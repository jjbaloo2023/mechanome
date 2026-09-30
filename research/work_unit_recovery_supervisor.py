"""Run one registered dummy phase and record its observed process exit.

Each phase is a single-use invocation. Unknown status blocks every later phase.
This supervisor does not retry, kill on timeout, or reset a campaign.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mechanome.research import Campaign  # noqa: E402

RESEARCH = ROOT / "research"
RUN = RESEARCH / "work_unit_recovery_001"
LEDGER = RESEARCH / "work_unit_recovery_execution.json"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value, exclusive=False):
    if exclusive:
        with path.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
    else:
        temporary = path.with_suffix(path.suffix + ".pending")
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
        temporary.replace(path)


def run(phase):
    inputs = read(RESEARCH / "work_unit_recovery_execution_inputs.json")
    for name, expected in inputs["source_sha256"].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError(f"Frozen source changed: {name}")
    deadline = dt.datetime.fromisoformat(inputs["evidence_cutoff_utc"].replace("Z", "+00:00"))
    if dt.datetime.now(dt.timezone.utc) >= deadline:
        raise RuntimeError("Evidence deadline reached")
    ledger = read(LEDGER)
    rows = ledger["invocations"]
    if len(rows) != phase - 1 or len(rows) >= ledger["phase_cap"]:
        raise RuntimeError("Phase order or cumulative invocation cap rejects launch")
    if any(row["status"] != "completed" for row in rows):
        raise RuntimeError("Reconcile earlier failed or unknown execution; no replacement")
    RUN.mkdir(exist_ok=True)
    save(RUN / f"reservation-{phase}.json", {"phase": phase, "reserved_at_utc": now()}, True)
    log_path = RUN / f"phase-{phase}.log"
    command = [sys.executable, "-B", str(RESEARCH / "work_unit_recovery.py"),
               str(phase), str(RUN), "--commit", inputs["commit_metadata"]]
    row = {"phase": phase, "status": "reserved", "reserved_at_utc": now(),
           "command": command, "log": str(log_path.relative_to(ROOT)),
           "input_record_sha256": digest(RESEARCH / "work_unit_recovery_execution_inputs.json")}
    rows.append(row)
    save(LEDGER, ledger)
    try:
        with log_path.open("xb") as log:
            process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            row.update(status="running", pid=process.pid, started_at_utc=now())
            save(LEDGER, ledger)
            try:
                code = process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                row.update(status="unknown", observed_at_utc=now(),
                           reason="Timeout is not termination evidence. No later phase authorized.")
                save(LEDGER, ledger)
                return 2
        observed = now()
        row.update(exit_code=code, exit_observed_at_utc=observed)
        if code != 0:
            row.update(status="failed", reason="Observed nonzero process exit; no retry")
            save(RUN / f"exit-{phase}.json", dict(row), True)
            save(LEDGER, ledger)
            return 1
        output_path = RUN / f"phase-{phase}.json"
        output = read(output_path)
        if output["phase"] != phase or output["pid"] != process.pid or output["status"] != "completed":
            raise RuntimeError("Phase output identity does not match observed child")
        if process.pid in {previous["pid"] for previous in rows[:-1]}:
            raise RuntimeError("Registered distinct-PID demonstration was not met")
        receipt = {"phase": phase, "pid": process.pid, "status": "completed",
                   "exit_code": code, "exit_observed_at_utc": observed,
                   "phase_output_sha256": digest(output_path)}
        receipt_path = RUN / f"exit-{phase}.json"
        save(receipt_path, receipt, True)
        campaign = Campaign(RUN / "campaign")
        try:
            lead = campaign.export()["lead"]
            if len(lead) != 1 or lead[0]["token"] != output["token"] or lead[0]["state"] != "active":
                raise RuntimeError("Child must leave its current lead active for parent-observed retirement")
            campaign.terminate_lead(output["token"],
                                    f"Supervisor wait observed PID {process.pid} exit 0 at {observed}; "
                                    f"receipt SHA256 {digest(receipt_path)}")
            audit = campaign.export()
        finally:
            campaign.close()
        audit_path = RUN / f"post-exit-{phase}.json"
        save(audit_path, audit, True)
        row.update(status="completed", phase_output_sha256=digest(output_path),
                   exit_receipt_sha256=digest(receipt_path), post_exit_audit_sha256=digest(audit_path),
                   completed_at_utc=now())
        save(LEDGER, ledger)
        print(json.dumps({"phase": phase, "pid": process.pid, "exit_code": code,
                          "work_totals": audit["work_totals"], "lead_state": audit["lead"][0]["state"]}))
        return 0
    except BaseException as error:
        row.update(status="unknown" if "exit_code" not in row else "failed_supervision",
                   error=f"{type(error).__name__}: {error}", observed_at_utc=now())
        save(LEDGER, ledger)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", type=int, choices=(1, 2, 3))
    raise SystemExit(run(parser.parse_args().phase))
