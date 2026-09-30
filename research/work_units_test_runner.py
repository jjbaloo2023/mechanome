"""Lead-only, bounded local regression execution for offline-work-units-001."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/work_units_test_runs.json"


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(r["status"] == "running" for r in ledger["test_invocations"]):
        raise RuntimeError("Reconcile the outstanding test process before another invocation")
    number = len(ledger["test_invocations"]) + 1
    if number > ledger["test_invocation_cap"]:
        raise RuntimeError("Cumulative pytest invocation cap reached")
    relative = f"research/work_units_pytest_{number:02d}.log"
    files = ["mechanome/research/contracts.py", "mechanome/research/controller.py",
             "tests/test_research_controller.py", "tests/test_research_work_units.py"]
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
               "--basetemp", f"research/.pytest-work-units-{number:02d}", *files[2:]]
    record = {"invocation": number, "started_at_utc": now(), "status": "running",
              "log": relative, "command": command,
              "input_sha256": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files}}
    with (ROOT / relative).open("x", encoding="utf-8") as stream:
        ledger["test_invocations"].append(record)
        LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
        try:
            result = subprocess.run(command, cwd=ROOT, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=90)
            record.update(status="completed", exit_code=result.returncode)
        except BaseException as exc:
            record.update(status="failed", error=repr(exc))
            raise
        finally:
            record["finished_at_utc"] = now()
            LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print((ROOT / relative).read_text(encoding="utf-8"))
    print(json.dumps(record))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
