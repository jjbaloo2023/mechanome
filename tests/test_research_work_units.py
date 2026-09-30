"""Dummy-only regression cases for offline cumulative work reservations."""
import json
import threading

import pytest

from mechanome.research import Blocked, Campaign, Charter, Result, Task


def _campaign(tmp_path, cap=2, task_cap=None):
    task_cap = cap if task_cap is None else task_cap
    campaign = Campaign(tmp_path / "work", Charter("work", "guard dummy work", "a" * 40,
                                                     work_unit_limits=(("dummy", cap),)))
    token = campaign.acquire_lead("lead")
    source = campaign.put_artifact(b"source")
    task = Task("dummy-task", "guard callback", "unknown", ("do nothing",), "cap test",
                ("blocked",), (source,), ("guard",), "stop", "worker",
                work_unit_limits=(("dummy", task_cap),))
    campaign.decide(token, "reserve dummy work", [task])
    return campaign, token, task


def _failed():
    return Result("solver_failed", "unresolved", "invalid", "dummy failure")


def test_cap_and_terminal_duplicate_never_invoke_dummy_callback(tmp_path):
    campaign, token, task = _campaign(tmp_path, cap=2)
    try:
        attempt = campaign.start(token, task.id)
        calls = []
        assert campaign.run_guarded_work(token, attempt, "call-1", "dummy", 2, lambda: calls.append("ran"))["execute"]
        campaign.reconcile_work(token, task.id, "call-1", "completed", "dummy callback returned")
        duplicate = campaign.run_guarded_work(token, attempt, "call-1", "dummy", 2, lambda: calls.append("duplicate"))
        assert duplicate == {"execute": False, "status": "terminal_duplicate", "call_id": "call-1", "state": "completed", "attempt": attempt}
        assert calls == ["ran"]
        with pytest.raises(Blocked, match="Conflicting task-scoped"):
            campaign.reserve_work(token, attempt, "call-1", "dummy", 1)
        with pytest.raises(Blocked, match="Campaign work-unit cap"):
            campaign.run_guarded_work(token, attempt, "call-2", "dummy", 1, lambda: calls.append("over-cap"))
        assert calls == ["ran"]
    finally:
        campaign.close()


def test_unknown_or_reserved_work_blocks_finish_and_retry_until_fenced_reconciliation(tmp_path):
    campaign, token, task = _campaign(tmp_path)
    try:
        attempt = campaign.start(token, task.id)
        campaign.reserve_work(token, attempt, "call-1", "dummy", 1)
        campaign.mark_work_unknown(token, task.id, "call-1", "transport uncertain")
        callbacks = []
        with pytest.raises(Blocked, match="before new call ID"):
            campaign.run_guarded_work(token, attempt, "call-2", "dummy", 1, lambda: callbacks.append("bypass"))
        assert callbacks == []
        with pytest.raises(Blocked, match="Reconcile reserved or unknown work"):
            campaign.finish(attempt, _failed())
        campaign.uncertain(attempt, "host lost worker")
        with pytest.raises(Blocked, match="Reconcile"):
            campaign.start(token, task.id, "retry")
        campaign.reconcile_work(token, task.id, "call-1", "cancelled", "host observed no callback")
        campaign.finish(attempt, _failed(), reconciliation="attempt reconciled")
        assert campaign.start(token, task.id, "retry after reconciliation") != attempt
    finally:
        campaign.close()


def test_restart_and_second_connection_keep_lifetime_cap_and_stale_fencing(tmp_path):
    campaign, token, task = _campaign(tmp_path, cap=1)
    attempt = campaign.start(token, task.id)
    campaign.reserve_work(token, attempt, "call-1", "dummy", 1)
    second = Campaign(campaign.directory)
    try:
        assert second.work_totals(task.id) == {"dummy": 1}
        other = Task("other-task", "second contender", "unknown", ("stop",), "campaign cap",
                     ("blocked",), task.inputs, ("guard",), "stop", "worker",
                     work_unit_limits=(("dummy", 1),))
        campaign.decide(token, "add concurrent contender", [other])
        other_attempt = campaign.start(token, other.id)
        with pytest.raises(Blocked, match="Campaign work-unit cap"):
            second.reserve_work(token, other_attempt, "call-2", "dummy", 1)
        campaign.terminate_lead(token, "first host stopped")
        replacement = second.acquire_lead("replacement")
        with pytest.raises(Blocked, match="Stale or expired"):
            campaign.reserve_work(token, attempt, "call-3", "dummy", 1)
        second.reconcile_work(replacement, task.id, "call-1", "cancelled", "restarted host inspected state")
        assert second.export()["work_totals"] == {"dummy": 1}
    finally:
        second.close()
        campaign.close()


def test_two_connection_concurrent_reservations_cannot_cross_campaign_cap(tmp_path):
    campaign, token, task = _campaign(tmp_path, cap=1)
    try:
        other = Task("thread-task", "second contender", "unknown", ("stop",), "campaign cap",
                     ("blocked",), task.inputs, ("guard",), "stop", "worker",
                     work_unit_limits=(("dummy", 1),))
        campaign.decide(token, "add thread contender", [other])
        first_attempt = campaign.start(token, task.id)
        second_attempt = campaign.start(token, other.id)
        barrier = threading.Barrier(2)
        results = []

        def reserve_from_fresh_connection(attempt, call_id):
            local = Campaign(campaign.directory)
            try:
                barrier.wait(timeout=5)
                results.append(local.reserve_work(token, attempt, call_id, "dummy", 1))
            except Blocked as error:
                results.append({"blocked": str(error)})
            finally:
                local.close()

        threads = [threading.Thread(target=reserve_from_fresh_connection, args=(first_attempt, "thread-a")),
                   threading.Thread(target=reserve_from_fresh_connection, args=(second_attempt, "thread-b"))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        assert not any(thread.is_alive() for thread in threads)
        assert sum(row.get("execute") is True for row in results) == 1
        assert sum("Campaign work-unit cap" in row.get("blocked", "") for row in results) == 1
        assert campaign.work_totals() == {"dummy": 1}
    finally:
        campaign.close()


def test_task_cap_survives_retry_and_invalid_units_do_not_reserve(tmp_path):
    campaign, token, task = _campaign(tmp_path, cap=3, task_cap=2)
    try:
        attempt = campaign.start(token, task.id)
        with pytest.raises(Blocked, match="positive integer"):
            campaign.reserve_work(token, attempt, "bad-zero", "dummy", 0)
        with pytest.raises(Blocked, match="positive integer"):
            campaign.reserve_work(token, attempt, "bad-bool", "dummy", True)
        def raised_callback():
            raise RuntimeError("dummy callback failure")
        with pytest.raises(RuntimeError, match="dummy callback"):
            campaign.run_guarded_work(token, attempt, "call-1", "dummy", 1, raised_callback)
        with pytest.raises(Blocked, match="Reconcile reserved or unknown work"):
            campaign.finish(attempt, _failed())
        campaign.reconcile_work(token, task.id, "call-1", "failed", "dummy callback raised")
        campaign.finish(attempt, _failed())
        retry = campaign.start(token, task.id, "retry")
        duplicate_callbacks = []
        duplicate = campaign.run_guarded_work(token, retry, "call-1", "dummy", 1,
                                              lambda: duplicate_callbacks.append("reran"))
        assert duplicate["execute"] is False and duplicate["status"] == "terminal_duplicate"
        assert duplicate_callbacks == []
        campaign.reserve_work(token, retry, "call-2", "dummy", 1)
        campaign.reconcile_work(token, task.id, "call-2", "cancelled", "no callback")
        campaign.finish(retry, _failed())
        third = campaign.start(token, task.id, "last allowed attempt")
        with pytest.raises(Blocked, match="Task work-unit cap"):
            campaign.reserve_work(token, third, "call-3", "dummy", 1)
    finally:
        campaign.close()


def test_legacy_json_defaults_reload_and_redeliver_without_rewrite(tmp_path):
    root = tmp_path / "legacy"
    charter = Charter("legacy", "reload old bodies", "b" * 40)
    campaign = Campaign(root, charter)
    token = campaign.acquire_lead("lead")
    try:
        source = campaign.put_artifact(b"legacy")
        task = Task("legacy-task", "reload", "unknown", ("stop",), "compatibility", ("ok",),
                    (source,), ("legacy",), "stop", "worker")
        campaign.decide(token, "store legacy-compatible task", [task])
        charter = json.loads(campaign.db.execute("SELECT body FROM configuration").fetchone()[0])
        charter.pop("work_unit_limits")
        task_body = json.loads(campaign.db.execute("SELECT body FROM tasks WHERE id=?", (task.id,)).fetchone()[0])
        task_body.pop("work_unit_limits")
        campaign.db.execute("UPDATE configuration SET body=?", (json.dumps(charter, sort_keys=True),))
        campaign.db.execute("UPDATE tasks SET body=? WHERE id=?", (json.dumps(task_body, sort_keys=True), task.id))
        campaign.terminate_lead(token, "close first host")
        campaign.close()
        campaign = Campaign(root, Charter("legacy", "reload old bodies", "b" * 40))
        assert campaign.charter.work_unit_limits == ()
        assert campaign.task(task.id).work_unit_limits == ()
        redelivery = campaign.acquire_lead("replacement")
        campaign.decide(redelivery, "redeliver legacy task", [task])
        assert campaign.db.execute("SELECT body FROM tasks WHERE id=?", (task.id,)).fetchone()[0] == json.dumps(task_body, sort_keys=True)
    finally:
        campaign.close()
