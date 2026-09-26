"""Recovery and evidence-retention contracts; no provider or scientific sampling."""

import json
import sqlite3
from dataclasses import replace

import pytest

from mechanome.research import Blocked, Campaign, Charter, Result, Task


@pytest.fixture
def campaign(tmp_path):
    campaign = Campaign(
        tmp_path, Charter("discovery", "Map competing theories", "a" * 40, 100, 25)
    )
    yield campaign
    campaign.close()


def task(campaign, name="source", **changes):
    artifact = campaign.put_artifact(
        b"Frozen source fixture, not experimental evidence"
    )
    spec = Task(
        name,
        "What was measured?",
        "Measured versus inferred",
        ("direct", "inferred"),
        "Resolve the observation model",
        ("found", "inconclusive"),
        (artifact,),
        ("citation",),
        "Stop after one source",
        "source-worker",
        25,
    )
    return replace(spec, **changes)


def enqueue(campaign, **changes):
    token = campaign.acquire_lead("lead")
    spec = task(campaign, **changes)
    campaign.decide(token, "Audit measurement before building models", [spec])
    return token, spec


def test_restart_preserves_ownership_and_outstanding_reservation(campaign):
    token, spec = enqueue(campaign)
    attempt = campaign.start(token, spec.id)
    restarted = Campaign(campaign.directory)
    try:
        with pytest.raises(Blocked, match="known terminated"):
            restarted.acquire_lead("replacement")
        with pytest.raises(Blocked, match="Reconcile"):
            restarted.start(token, spec.id)
        assert restarted.budget()["reserved_cents"] == 25
        assert restarted.export()["attempts"][0]["id"] == attempt
    finally:
        restarted.close()


def test_expired_lead_cannot_commit_or_be_replaced_without_termination(campaign):
    token, spec = enqueue(campaign)
    campaign.db.execute("UPDATE lead SET expires=0")
    with pytest.raises(Blocked, match="expired"):
        campaign.decide(token, "late decision", [spec])
    with pytest.raises(Blocked, match="known terminated"):
        campaign.acquire_lead("replacement")
    campaign.terminate_lead(token, "Host observed process exit")
    replacement = campaign.acquire_lead("replacement")
    assert replacement > token
    with pytest.raises(Blocked, match="Stale"):
        campaign.start(token, spec.id)


def test_task_redelivery_and_atomic_decision(campaign):
    token, spec = enqueue(campaign)
    campaign.decide(token, "Redelivery", [spec])
    assert len(campaign.export()["tasks"]) == 1
    new = task(campaign, "new")
    with pytest.raises(Blocked, match="different instructions"):
        campaign.decide(
            token, "Must roll back both", [new, replace(spec, question="changed")]
        )
    assert len(campaign.export()["tasks"]) == 1


def test_valid_negative_survives_restart_and_duplicate_completion(campaign):
    token, spec = enqueue(campaign)
    attempt = campaign.start(token, spec.id)
    result = Result(
        "succeeded", "negative", "valid", "Prediction not supported", spec.inputs
    )
    campaign.finish(attempt, result, 12)
    campaign.finish(attempt, result, 12)
    assert campaign.budget()["spent_cents"] == 12
    with pytest.raises(Blocked, match="committed scientific result"):
        campaign.start(token, spec.id, "Try for a positive answer")
    with pytest.raises(Blocked, match="Conflicting"):
        campaign.finish(attempt, replace(result, outcome="positive"), 12)
    assert json.loads(campaign.export()["tasks"][0]["result"])["outcome"] == "negative"


def test_uncertain_request_requires_reconciliation(campaign):
    token, spec = enqueue(campaign)
    attempt = campaign.start(token, spec.id)
    campaign.uncertain(attempt, "Transport disconnected", "provider-123")
    failed = Result("cancelled", "unresolved", "unchecked", "Cancellation confirmed")
    with pytest.raises(Blocked, match="Reconcile"):
        campaign.finish(attempt, failed)
    with pytest.raises(Blocked, match="Reconcile"):
        campaign.start(token, spec.id, "retry")
    campaign.finish(
        attempt, failed, 5, reconciliation="Host observed final cancellation"
    )
    assert campaign.budget()["reserved_cents"] == 0
    assert (
        campaign.start(token, spec.id, "Narrow scope following cancellation") != attempt
    )


def test_solver_failure_is_not_negative_evidence(campaign):
    with pytest.raises(Blocked, match="not scientific refutation"):
        Result("solver_failed", "negative", "invalid", "No convergence")
    token, spec = enqueue(campaign)
    for number in range(3):
        attempt = campaign.start(
            token, spec.id, "Changed solver settings" if number else None
        )
        campaign.finish(
            attempt, Result("solver_failed", "unresolved", "invalid", "No convergence")
        )
    with pytest.raises(Blocked, match="Attempt limit"):
        campaign.start(token, spec.id, "Fourth attempt")
    assert campaign.export()["tasks"][0]["result"] is None


def test_reservations_preserve_review_funds(campaign):
    token = campaign.acquire_lead("lead")
    specs = [task(campaign, str(i)) for i in range(4)]
    review = task(campaign, "review", purpose="review")
    campaign.decide(token, "Reserve outstanding work", specs + [review])
    for spec in specs[:3]:
        campaign.start(token, spec.id)
    with pytest.raises(Blocked, match="Budget boundary"):
        campaign.start(token, specs[3].id)
    campaign.start(token, review.id)
    assert campaign.budget()["reserved_cents"] == 100


def test_corrupted_input_blocks_execution(campaign):
    token, spec = enqueue(campaign)
    (campaign.artifacts / spec.inputs[0]).write_bytes(b"changed")
    with pytest.raises(Blocked, match="Corrupted"):
        campaign.start(token, spec.id)
    with pytest.raises(Blocked, match="Corrupted"):
        campaign.export()


def test_audit_events_cannot_be_rewritten(campaign):
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        campaign.db.execute("DELETE FROM events")


def test_live_execution_cannot_be_enabled_by_draft_charter():
    with pytest.raises(Blocked, match="Live execution"):
        Charter("test", "goal", "a" * 40, mode="live")


def test_unknown_workers_count_toward_concurrency(campaign):
    token = campaign.acquire_lead("lead")
    specs = [task(campaign, str(i), cost_cents=0) for i in range(5)]
    campaign.decide(token, "Bound concurrency", specs)
    for spec in specs[:4]:
        attempt = campaign.start(token, spec.id)
        campaign.uncertain(attempt, "Process status unknown")
    with pytest.raises(Blocked, match="Worker limit"):
        campaign.start(token, specs[4].id)
