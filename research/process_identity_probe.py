"""Single-use, zero-work child-process identity probe; never opens a campaign."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


if __name__ == "__main__":
    if sys.argv[1:] == ["--child"]:
        print(json.dumps({"pid": os.getpid(), "parent_pid": os.getppid(),
                          "executable": sys.executable, "reported_at_utc": now()}))
    else:
        root = Path(__file__).resolve().parent
        design = json.loads((root / "process_identity_design.json").read_text(encoding="utf-8"))
        deadline = dt.datetime.fromisoformat(design["evidence_cutoff_utc"].replace("Z", "+00:00"))
        if dt.datetime.now(dt.timezone.utc) >= deadline:
            raise RuntimeError("Preflight evidence deadline reached")
        record = {"reserved_at_utc": now(), "status": "reserved", "subprocess_cap": 1,
                  "parent_pid": os.getpid(), "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "command": [sys._base_executable, "-B", str(Path(__file__).resolve()), "--child"],
                  "dummy_callbacks": 0, "scientific_calls": 0}
        with (root / "process_identity_probe_reservation.json").open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
        try:
            with (root / "process_identity_probe_001.log").open("xb") as output:
                process = subprocess.Popen(record["command"], stdout=output, stderr=subprocess.STDOUT)
                record.update(status="running", launched_pid=process.pid, started_at_utc=now())
                with (root / "process_identity_probe_started.json").open("x", encoding="utf-8") as stream:
                    json.dump(record, stream, indent=2)
                code = process.wait(timeout=30)
                record.update(exit_code=code, exit_observed_at_utc=now(), status="exited")
            child = json.loads((root / "process_identity_probe_001.log").read_text(encoding="utf-8"))
            record["child"] = child
            record["passed"] = code == 0 and child["pid"] == process.pid and child["parent_pid"] == os.getpid()
            record["status"] = "completed" if record["passed"] else "failed_identity"
        except BaseException as error:
            record.update(status="unknown" if "exit_code" not in record else "failed_output",
                          error=f"{type(error).__name__}: {error}", observed_at_utc=now(), passed=False)
        with (root / "process_identity_probe_001.json").open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
            stream.write("\n")
        print(json.dumps(record))
        raise SystemExit(0 if record.get("passed") else 1)
