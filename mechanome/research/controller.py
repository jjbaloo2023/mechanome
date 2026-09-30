"""Single-host, transactional research state. No model or worker owns this database.

Flow: acquire lead -> decide and enqueue -> start attempt -> finish -> review.
Unknown executions retain their reservations and block automatic replacements.
All costs use integer cents; this is bookkeeping, not a provider billing limit.
"""

import hashlib
import json
import re
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from .contracts import Charter, Task, money, payload, require


def encode(value):
    return json.dumps(value, sort_keys=True, allow_nan=False)


class Campaign:
    def __init__(self, directory, charter=None):
        self.directory = Path(directory)
        if charter is None:
            require(
                (self.directory / "research.sqlite").is_file(),
                "Campaign does not exist",
            )
        self.directory.mkdir(parents=True, exist_ok=True)
        self.artifacts = self.directory / "artifacts"
        self.artifacts.mkdir(exist_ok=True)
        self.db = sqlite3.connect(
            self.directory / "research.sqlite", isolation_level=None
        )
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS configuration (id INTEGER PRIMARY KEY CHECK(id=1), body TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS lead (id INTEGER PRIMARY KEY CHECK(id=1), token INTEGER NOT NULL,
                owner TEXT NOT NULL, expires REAL NOT NULL, state TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, body TEXT NOT NULL, result TEXT);
            CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY, task TEXT NOT NULL REFERENCES tasks(id),
                state TEXT NOT NULL, reserved INTEGER NOT NULL, cost INTEGER NOT NULL DEFAULT 0,
                request_id TEXT UNIQUE, result TEXT);
            CREATE TABLE IF NOT EXISTS work_units (task TEXT NOT NULL REFERENCES tasks(id), call_id TEXT NOT NULL,
                attempt TEXT NOT NULL REFERENCES attempts(id), kind TEXT NOT NULL, units INTEGER NOT NULL,
                state TEXT NOT NULL, reconciliation TEXT, PRIMARY KEY(task,call_id));
            CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, time REAL NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL);
            CREATE TRIGGER IF NOT EXISTS immutable_event_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'Events are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS immutable_event_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'Events are immutable'); END;
        """)
        with self.transaction():
            row = self.db.execute("SELECT body FROM configuration").fetchone()
            if row is None:
                require(charter is not None, "Charter required")
                self.db.execute(
                    "INSERT INTO configuration VALUES (1, ?)",
                    (encode(payload(charter)),),
                )
                self.event("charter", payload(charter))
            elif charter is not None:
                require(
                    Charter(**json.loads(row["body"])) == charter,
                    "Existing charter is immutable; use a new campaign",
                )
            self.charter = Charter(
                **json.loads(
                    self.db.execute("SELECT body FROM configuration").fetchone()[0]
                )
            )

    def close(self):
        self.db.close()

    @contextmanager
    def transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def event(self, kind, body):
        self.db.execute(
            "INSERT INTO events(time,kind,body) VALUES (?,?,?)",
            (time.time(), kind, encode(body)),
        )

    def put_artifact(self, content):
        digest = hashlib.sha256(content).hexdigest()
        path = self.artifacts / digest
        try:
            with path.open("xb") as stream:
                stream.write(content)
        except FileExistsError:
            pass
        self.read_artifact(digest)
        return digest

    def read_artifact(self, digest):
        require(bool(re.fullmatch("[0-9a-f]{64}", digest)), "Invalid artifact hash")
        path = self.artifacts / digest
        require(path.is_file(), f"Missing artifact {digest}")
        content = path.read_bytes()
        require(
            hashlib.sha256(content).hexdigest() == digest,
            f"Corrupted artifact {digest}",
        )
        return content

    def acquire_lead(self, owner, ttl=300):
        require(bool(owner) and 0 < ttl <= 3600, "Owner and bounded lease required")
        with self.transaction():
            row = self.db.execute("SELECT * FROM lead").fetchone()
            require(
                row is None or row["state"] == "terminated",
                "Previous invocation must be known terminated, even after lease expiry",
            )
            token = row["token"] + 1 if row else 1
            self.db.execute(
                "INSERT OR REPLACE INTO lead VALUES (1,?,?,?,?)",
                (token, owner, time.time() + ttl, "active"),
            )
            self.event("lead_acquired", {"owner": owner, "token": token})
        return token

    def fence(self, token):
        row = self.db.execute("SELECT * FROM lead").fetchone()
        require(
            row is not None
            and row["token"] == token
            and row["state"] == "active"
            and row["expires"] > time.time(),
            "Stale or expired lead token",
        )

    def terminate_lead(self, token, evidence):
        """Trusted controller calls only after observing termination, not on timeout."""
        require(bool(evidence.strip()), "Termination evidence required")
        with self.transaction():
            row = self.db.execute("SELECT * FROM lead").fetchone()
            require(row is not None and row["token"] == token, "Stale lead token")
            self.db.execute("UPDATE lead SET state='terminated' WHERE id=1")
            self.event("lead_terminated", {"token": token, "evidence": evidence})

    def decide(self, token, rationale, tasks):
        require(bool(rationale.strip()), "Decision rationale required")
        with self.transaction():
            self.fence(token)
            for task in tasks:
                for digest in task.inputs:
                    self.read_artifact(digest)
                body = encode(payload(task))
                previous = self.db.execute(
                    "SELECT body FROM tasks WHERE id=?", (task.id,)
                ).fetchone()
                require(
                    previous is None or Task(**json.loads(previous[0])) == task,
                    "Task ID reused with different instructions",
                )
                self.db.execute(
                    "INSERT OR IGNORE INTO tasks(id,body) VALUES (?,?)", (task.id, body)
                )
            self.event(
                "decision",
                {
                    "token": token,
                    "rationale": rationale,
                    "tasks": [t.id for t in tasks],
                    "charter_version": self.charter.version,
                },
            )

    def task(self, task_id):
        row = self.db.execute(
            "SELECT body FROM tasks WHERE id=?", (task_id,)
        ).fetchone()
        require(row is not None, "Unknown task")
        return Task(**json.loads(row[0]))

    def budget(self):
        row = self.db.execute(
            "SELECT COALESCE(SUM(cost),0), COALESCE(SUM(reserved),0) FROM attempts"
        ).fetchone()
        return {
            "spent_cents": row[0],
            "reserved_cents": row[1],
            "limit_cents": self.charter.budget_cents,
        }

    def work_totals(self, task_id=None):
        where, values = ("", ()) if task_id is None else (" WHERE task=?", (task_id,))
        rows = self.db.execute(
            "SELECT kind, COALESCE(SUM(units),0) AS units FROM work_units" + where + " GROUP BY kind", values
        ).fetchall()
        return {row["kind"]: row["units"] for row in rows}

    def _unresolved_work(self, task_id, attempt=None):
        sql = "SELECT * FROM work_units WHERE task=? AND state IN ('reserved','unknown')"
        values = [task_id]
        if attempt is not None:
            sql += " AND attempt=?"
            values.append(attempt)
        return self.db.execute(sql, values).fetchall()

    def start(self, token, task_id, retry_reason=None):
        with self.transaction():
            self.fence(token)
            task = self.task(task_id)
            require(
                self.db.execute(
                    "SELECT result FROM tasks WHERE id=?", (task_id,)
                ).fetchone()[0]
                is None,
                "Task already has a committed scientific result",
            )
            previous = self.db.execute(
                "SELECT * FROM attempts WHERE task=? ORDER BY rowid", (task_id,)
            ).fetchall()
            require(not self._unresolved_work(task_id), "Reconcile reserved or unknown work before retry")
            require(
                not any(r["state"] in {"running", "unknown"} for r in previous),
                "Reconcile outstanding attempt before retry",
            )
            require(len(previous) < self.charter.max_attempts, "Attempt limit reached")
            require(
                not previous or bool(retry_reason and retry_reason.strip()),
                "Replacement requires changed-method rationale",
            )
            active = self.db.execute(
                "SELECT COUNT(*) FROM attempts WHERE state IN ('running','unknown')"
            ).fetchone()[0]
            require(active < self.charter.max_workers, "Worker limit reached")
            for digest in task.inputs:
                self.read_artifact(digest)
            budget = self.budget()
            limit = self.charter.budget_cents
            if task.purpose == "exploration":
                limit -= self.charter.review_reserve_cents
            require(
                budget["spent_cents"] + budget["reserved_cents"] + task.cost_cents
                <= limit,
                "Budget boundary: checkpoint; preserve review reserve",
            )
            attempt = uuid.uuid4().hex
            self.db.execute(
                "INSERT INTO attempts(id,task,state,reserved) VALUES (?,?,'running',?)",
                (attempt, task_id, task.cost_cents),
            )
            self.event(
                "attempt_started",
                {
                    "attempt": attempt,
                    "task": task_id,
                    "retry_reason": retry_reason,
                    "worker": task.worker,
                },
            )
        return attempt

    def reserve_work(self, token, attempt, call_id, kind, units):
        """Atomically reserve an offline dummy-work unit before invoking a callback.

        Reservations are lifetime accounting: reconciliation never refunds them.
        A terminal duplicate returns ``execute=False``; it is not permission to
        invoke a callback again.  This does not provide exactly-once side effects.
        """
        require(isinstance(call_id, str) and bool(call_id.strip()), "Stable call ID required")
        require(isinstance(kind, str) and kind == kind.strip() and kind.replace("_", "").isalnum(), "Canonical work kind required")
        require(type(units) is int and units > 0, "Work units must be positive integer")
        with self.transaction():
            self.fence(token)
            attempt_row = self.db.execute("SELECT * FROM attempts WHERE id=?", (attempt,)).fetchone()
            require(attempt_row is not None and attempt_row["state"] == "running", "Attempt is not running")
            task = self.task(attempt_row["task"])
            existing = self.db.execute("SELECT * FROM work_units WHERE task=? AND call_id=?", (task.id, call_id)).fetchone()
            if existing is not None:
                require(existing["kind"] == kind and existing["units"] == units, "Conflicting task-scoped call identity")
                require(existing["state"] not in {"reserved", "unknown"}, "Reconcile unresolved call before replacement")
                return {"execute": False, "status": "terminal_duplicate", "call_id": call_id,
                        "state": existing["state"], "attempt": existing["attempt"]}
            require(not self._unresolved_work(task.id), "Reconcile reserved or unknown work before new call ID")
            campaign_limits, task_limits = dict(self.charter.work_unit_limits), dict(task.work_unit_limits)
            require(kind in campaign_limits and kind in task_limits, "Undeclared work kind")
            campaign_used = self.work_totals().get(kind, 0)
            task_used = self.work_totals(task.id).get(kind, 0)
            require(campaign_used + units <= campaign_limits[kind], "Campaign work-unit cap reached")
            require(task_used + units <= task_limits[kind], "Task work-unit cap reached")
            self.db.execute("INSERT INTO work_units(task,call_id,attempt,kind,units,state) VALUES (?,?,?,?,?,'reserved')",
                            (task.id, call_id, attempt, kind, units))
            self.event("work_reserved", {"token": token, "attempt": attempt, "task": task.id,
                                         "call_id": call_id, "kind": kind, "units": units})
            return {"execute": True, "status": "reserved", "call_id": call_id, "attempt": attempt}

    def run_guarded_work(self, token, attempt, call_id, kind, units, callback):
        """Reserve first, then run a local dummy callback only when execution is allowed."""
        reservation = self.reserve_work(token, attempt, call_id, kind, units)
        if not reservation["execute"]:
            return reservation
        return {**reservation, "value": callback()}

    def mark_work_unknown(self, token, task_id, call_id, evidence):
        require(bool(evidence and evidence.strip()), "Unknown work needs evidence")
        with self.transaction():
            self.fence(token)
            row = self.db.execute("SELECT * FROM work_units WHERE task=? AND call_id=?", (task_id, call_id)).fetchone()
            require(row is not None and row["state"] == "reserved", "Work is not reserved")
            self.db.execute("UPDATE work_units SET state='unknown', reconciliation=? WHERE task=? AND call_id=?",
                            (evidence, task_id, call_id))
            self.event("work_unknown", {"token": token, "task": task_id, "call_id": call_id, "evidence": evidence})

    def reconcile_work(self, token, task_id, call_id, terminal_state, evidence):
        require(terminal_state in {"completed", "cancelled", "failed"}, "Work reconciliation needs terminal state")
        require(bool(evidence and evidence.strip()), "Work reconciliation evidence required")
        with self.transaction():
            self.fence(token)
            row = self.db.execute("SELECT * FROM work_units WHERE task=? AND call_id=?", (task_id, call_id)).fetchone()
            require(row is not None and row["state"] in {"reserved", "unknown"}, "Work is not unresolved")
            self.db.execute("UPDATE work_units SET state=?, reconciliation=? WHERE task=? AND call_id=?",
                            (terminal_state, evidence, task_id, call_id))
            self.event("work_reconciled", {"token": token, "task": task_id, "call_id": call_id,
                                            "state": terminal_state, "evidence": evidence})

    def uncertain(self, attempt, reason, request_id=None):
        with self.transaction():
            row = self.db.execute(
                "SELECT * FROM attempts WHERE id=?", (attempt,)
            ).fetchone()
            require(
                row is not None and row["state"] == "running", "Attempt is not running"
            )
            require(bool(reason.strip()), "Uncertainty reason required")
            self.db.execute(
                "UPDATE attempts SET state='unknown',request_id=? WHERE id=?",
                (request_id, attempt),
            )
            self.event(
                "attempt_unknown",
                {"attempt": attempt, "reason": reason, "request_id": request_id},
            )

    def finish(self, attempt, result, cost_cents=0, reconciliation=None):
        money(cost_cents)
        with self.transaction():
            row = self.db.execute(
                "SELECT * FROM attempts WHERE id=?", (attempt,)
            ).fetchone()
            require(row is not None, "Unknown attempt")
            require(not self._unresolved_work(row["task"], attempt), "Reconcile reserved or unknown work before finishing")
            body = encode(payload(result))
            if row["state"] == "finished":
                require(
                    row["result"] == body and row["cost"] == cost_cents,
                    "Conflicting duplicate result",
                )
                return
            require(
                row["state"] != "unknown"
                or bool(reconciliation and reconciliation.strip()),
                "Reconcile unknown provider/process status first",
            )
            for digest in result.artifacts:
                self.read_artifact(digest)
            self.db.execute(
                "UPDATE attempts SET state='finished',reserved=0,cost=?,result=? WHERE id=?",
                (cost_cents, body, attempt),
            )
            if result.execution == "succeeded" and result.quality == "valid":
                self.db.execute(
                    "UPDATE tasks SET result=? WHERE id=? AND result IS NULL",
                    (body, row["task"]),
                )
            self.event(
                "attempt_finished",
                {
                    "attempt": attempt,
                    "result": payload(result),
                    "cost_cents": cost_cents,
                    "reconciliation": reconciliation,
                },
            )
            if cost_cents > row["reserved"]:
                self.event(
                    "cost_overrun",
                    {
                        "attempt": attempt,
                        "reserved": row["reserved"],
                        "actual": cost_cents,
                    },
                )

    def export(self):
        """Frozen audit state; rerunning a model is a new attempt, not replay."""
        with self.transaction():
            snapshot = {"charter": payload(self.charter), "budget": self.budget()}
            for table in ("tasks", "attempts", "work_units", "events", "lead"):
                snapshot[table] = [
                    dict(row)
                    for row in self.db.execute(f"SELECT * FROM {table} ORDER BY rowid")
                ]
            for path in self.artifacts.iterdir():
                self.read_artifact(path.name)
            snapshot["artifact_hashes"] = sorted(
                p.name for p in self.artifacts.iterdir()
            )
            snapshot["work_totals"] = self.work_totals()
        return snapshot
