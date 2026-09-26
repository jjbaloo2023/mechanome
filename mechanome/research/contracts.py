"""Small, explicit contracts shared by the controller and trusted workers."""

from dataclasses import asdict, dataclass


class Blocked(ValueError):
    """A transition needs evidence, reconciliation, or a different charter."""


def require(condition, reason):
    if not condition:
        raise Blocked(reason)


def money(value):
    require(type(value) is int and value >= 0, "Cost must be nonnegative integer cents")


@dataclass(frozen=True)
class Charter:
    name: str
    goal: str
    frozen_commit: str
    budget_cents: int = 0
    review_reserve_cents: int = 0
    max_workers: int = 4
    max_attempts: int = 3
    version: int = 1
    mode: str = "offline"

    def __post_init__(self):
        require(bool(self.name.strip() and self.goal.strip()), "Name and goal required")
        require(
            len(self.frozen_commit) == 40
            and all(c in "0123456789abcdef" for c in self.frozen_commit),
            "Freeze a full Git commit",
        )
        money(self.budget_cents)
        money(self.review_reserve_cents)
        require(
            self.review_reserve_cents <= self.budget_cents, "Reserve exceeds budget"
        )
        require(
            type(self.max_workers) is int and 1 <= self.max_workers <= 4,
            "Use 1-4 workers",
        )
        require(
            type(self.max_attempts) is int and 1 <= self.max_attempts <= 3,
            "Use 1-3 attempts",
        )
        require(
            type(self.version) is int and self.version > 0,
            "Positive charter version required",
        )
        require(
            self.mode == "offline",
            "Live execution is not implemented; a draft charter cannot authorize spending",
        )


@dataclass(frozen=True)
class Task:
    id: str
    question: str
    uncertainty: str
    alternatives: tuple[str, ...]
    rationale: str
    expected_outcomes: tuple[str, ...]
    inputs: tuple[str, ...]
    required_checks: tuple[str, ...]
    stop_condition: str
    worker: str
    cost_cents: int = 0
    purpose: str = "exploration"

    def __post_init__(self):
        for name in (
            "id",
            "question",
            "uncertainty",
            "rationale",
            "stop_condition",
            "worker",
        ):
            require(bool(getattr(self, name).strip()), f"Task needs {name}")
        for name in ("alternatives", "expected_outcomes", "inputs", "required_checks"):
            values = getattr(self, name)
            require(
                bool(values) and all(isinstance(v, str) and v.strip() for v in values),
                f"Task needs {name}",
            )
            object.__setattr__(self, name, tuple(values))
        require(
            len(set(self.required_checks)) == len(self.required_checks),
            "Duplicate required check",
        )
        money(self.cost_cents)
        require(
            self.purpose in {"exploration", "review", "synthesis"},
            "Unknown task purpose",
        )


@dataclass(frozen=True)
class Result:
    execution: str
    outcome: str
    quality: str
    summary: str
    artifacts: tuple[str, ...] = ()

    def __post_init__(self):
        require(
            self.execution
            in {"succeeded", "solver_failed", "invalid_output", "cancelled"},
            "Unknown execution status",
        )
        require(
            self.outcome in {"positive", "negative", "inconclusive", "unresolved"},
            "Unknown scientific outcome",
        )
        require(
            self.quality in {"unchecked", "valid", "invalid"},
            "Unknown evidence quality",
        )
        require(bool(self.summary.strip()), "A result needs a summary")
        require(
            self.execution == "succeeded" or self.outcome == "unresolved",
            "Execution failure is not scientific refutation",
        )
        require(
            self.quality != "valid" or self.execution == "succeeded",
            "Failed execution cannot yield valid evidence",
        )
        require(
            self.execution != "succeeded" or bool(self.artifacts),
            "Successful result needs artifacts",
        )


def payload(value):
    return asdict(value)
