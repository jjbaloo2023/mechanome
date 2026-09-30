"""Lead-only bounded test execution for tracking-metric-contract-001.
Each test invocation and tracker call consumes the persistent attempt budget
before it starts; output paths are unique and old logs are never overwritten.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
import contextlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
LEDGER = ROOT / "research/tracking_metric_test_runs.json"

def now():
    return datetime.now(timezone.utc).isoformat()

def save(ledger):
    LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")

def main():
    import pytest
    from validation import tracking
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if len(ledger["test_invocations"]) >= ledger["test_invocation_cap"]:
        raise RuntimeError("Cumulative test-invocation limit reached")
    if any(x["status"] == "running" for x in ledger["test_invocations"]):
        raise RuntimeError("A prior test invocation has unknown completion; reconcile first")
    number = len(ledger["test_invocations"]) + 1
    relative = f"research/tracking_metric_pytest_{number:02d}.log"
    log = (ROOT / relative).open("x", encoding="utf-8")
    record = {"invocation": number, "started_at_utc": now(), "status": "running",
        "log": relative, "tracker_calls": [], "input_sha256": {
            f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest()
            for f in ["validation/tracking.py", "tests/test_tracking_validation.py", "tests/test_orchestration.py"]}}
    ledger["test_invocations"].append(record)
    save(ledger)
    original = tracking.run_tracking
    def counted(*args, **kwargs):
        if ledger["tracker_movie_runs_reserved"] >= ledger["tracker_movie_run_cap"]:
            raise RuntimeError("Cumulative tracker-movie limit reached")
        ledger["tracker_movie_runs_reserved"] += 1
        call = {"started_at_utc": now(), "status": "reserved"}
        record["tracker_calls"].append(call)
        save(ledger)
        try:
            result = original(*args, **kwargs)
        except BaseException:
            call.update(status="failed", finished_at_utc=now())
            save(ledger)
            raise
        ledger["tracker_movie_runs_completed"] += 1
        call.update(status="completed", finished_at_utc=now())
        save(ledger)
        return result
    tracking.run_tracking = counted
    try:
        with log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            code = int(pytest.main(["-q", "-p", "no:cacheprovider",
                "tests/test_tracking_validation.py", "tests/test_orchestration.py"]))
    except BaseException as exc:
        record.update(status="failed", error=repr(exc), finished_at_utc=now())
        save(ledger)
        raise
    finally:
        tracking.run_tracking = original
    record.update(status="completed", exit_code=code, finished_at_utc=now())
    save(ledger)
    print((ROOT/relative).read_text(encoding="utf-8"))
    print(json.dumps({"invocation":number,"exit_code":code,
        "cumulative_tracker_calls":ledger["tracker_movie_runs_reserved"],"log":relative}))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
