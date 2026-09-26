"""Two-process persistence demonstration using a fixed, offline analytic task.

Run `python -m mechanome.research.demo prepare DIRECTORY --commit COMMIT`, then
`python -m mechanome.research.demo resume DIRECTORY` in a new process. This is
a scripted controller demo, not an LLM or an independent scientific reviewer.
"""

import argparse
import json

from mechanome.forward_cortex import self_validate

from .contracts import Charter, Result, Task, require
from .controller import Campaign


def prepare(directory, commit):
    campaign = Campaign(
        directory,
        Charter("persistence_demo", "Verify restart and analytic execution", commit),
    )
    try:
        require(not campaign.export()["tasks"], "Use a new directory for each demo")
        token = campaign.acquire_lead("demo-prepare")
        inputs = campaign.put_artifact(
            json.dumps(
                {
                    "model": "cortex",
                    "scope": "analytic self-check, not clathrin validation",
                }
            ).encode()
        )
        task = Task(
            "analytic-check",
            "Does the existing cortex analytic check pass?",
            "Implementation consistency",
            ("passes", "fails"),
            "Exercise durable execution without claiming biological validation",
            ("positive", "negative", "unresolved"),
            (inputs,),
            ("analytic_tolerance",),
            "One analytic self-check",
            "local-python",
        )
        campaign.decide(
            token, "Queue a bounded offline task before process exit", [task]
        )
        # No remote invocation exists: the synchronous lead has returned here.
        campaign.terminate_lead(
            token, "Synchronous prepare decision returned; no external invocation"
        )
        return {"status": "checkpointed", "next": "resume in a new process"}
    finally:
        campaign.close()


def resume(directory):
    campaign = Campaign(directory)
    try:
        snapshot = campaign.export()
        require(
            snapshot["charter"]["name"] == "persistence_demo", "Not a demo campaign"
        )
        task = next(row for row in snapshot["tasks"] if row["id"] == "analytic-check")
        if task["result"] is not None:
            return {"status": "already_complete", "attempts": len(snapshot["attempts"])}
        token = campaign.acquire_lead("demo-resume")
        attempt = campaign.start(token, "analytic-check")
        try:
            checks = self_validate()
            artifact = campaign.put_artifact(
                json.dumps(checks, sort_keys=True).encode()
            )
            result = Result(
                "succeeded",
                "positive" if checks["passed"] else "negative",
                "valid",
                "Existing analytic tolerance check; no empirical validation",
                (artifact,),
            )
        except Exception as error:
            campaign.finish(
                attempt, Result("solver_failed", "unresolved", "invalid", str(error))
            )
            campaign.terminate_lead(token, "Local worker raised and returned control")
            raise
        campaign.finish(attempt, result)
        campaign.terminate_lead(token, "Synchronous worker and lead finished")
        snapshot = campaign.export()
        (campaign.directory / "audit.json").write_text(
            json.dumps(snapshot, indent=2), encoding="utf-8"
        )
        return {
            "status": "complete",
            "outcome": result.outcome,
            "attempts": len(snapshot["attempts"]),
            "events": len(snapshot["events"]),
            "direct_api_cost_cents": 0,
        }
    finally:
        campaign.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "resume"))
    parser.add_argument("directory")
    parser.add_argument("--commit")
    args = parser.parse_args()
    if args.action == "prepare":
        if not args.commit:
            parser.error("prepare requires --commit")
        result = prepare(args.directory, args.commit)
    else:
        result = resume(args.directory)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
