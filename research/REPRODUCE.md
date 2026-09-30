# Reproduce and verify this checkpoint

Start with [FINDINGS.md](FINDINGS.md) and [INDEX.md](INDEX.md). Passing the checks
below verifies software contracts and bounded synthetic cases. It does not
repeat the public-data audit or validate biological mechanisms.

## Install and run the offline checks

From the repository root, with Python 3.10 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev,inference,plots]"
$checks = Get-Content research/checkpoint_tests.txt
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:MPLCONFIGDIR = Join-Path $PWD '.pytest-checkpoint-mpl'
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --basetemp .pytest-checkpoint-run @checks
```

Installation needs package access. The selected tests themselves need no API
keys, downloads, raw microscopy or Bayesian sampling. The explicit
[selection](checkpoint_tests.txt) covers the controller, input/annotation audit
rules, adapter and consumer gates, geometry counterexample, cap identifiability,
linear benchmark, small passive solver cases, coordinate repair, observation
controls and core integration boundaries. It retains tests of rejected historical
implementations; passing those tests does not overturn their recorded rejection.

Use a fresh `--basetemp` path for each concurrent run; pytest owns and clears that
directory. Do not point it at evidence or a dataset. The full repository suite
also has external-service, sampling and cache-dependent tests and is a separate
validation scope. Tested versions and this checkpoint's outcome are recorded
in [PROGRESS.md](PROGRESS.md).

## Inspect or repeat a study

Each row of the index links assumptions, code, outputs and review. Synthetic
`passive_area_states_001/*.npz` are included because the observation study consumes
them. Frozen source/design copies, failures and rejected outputs are also included.
Compare their SHA-256 values with the corresponding result records or manifests;
`locmofit_adapter_manifest.json` covers the final adapter implementation and tests.
The repository's `.gitattributes` disables newline conversion for these archived
files and the adapter sources covered by that manifest.

Historical runner entry points are **not a batch reproduction interface**: some
write fixed output names, enforce exclusive creation or have elapsed UTC
deadlines. Some audits overwrite a fixed report. Inspect a runner before using
it. For a new calculation, register a new design, deadline and output name,
preserve the prior source/result, and record the review. Do not overwrite an
accepted or rejected attempt just to refresh its timestamp.

## External inputs and caches

A clean clone includes derived summaries, source inventories, checksums and
synthetic states. It does not include raw microscopy, the downloaded S-BIAD566
fit CSVs, third-party source code or downloaded paper/sidecar payloads. Local
absolute paths in historical logs describe that run's machine; they are not
portable input locations. Resolve inputs using these retained records:

| External input | Retrieval and identity record |
| --- | --- |
| S-BIAD566 processed cap-fit tables | [data audit](data_audit.json) gives URLs, sizes and SHA-256; [geometry lock](geometry_inputs.lock.json) pins the comparison inputs |
| Shape2Fate annotation CSVs and inventory | [retrieval record](metadata/dynamic-annotations-001/retrieval.json) and [dataset metadata](metadata/dynamic-metadata-001/shape2fate_record.json) |
| DASC article XML | [methods/source note](DASC_METHODS.md) gives primary-source URLs and the JATS hash |
| DASC metadata spreadsheet and Word readme | [provenance](metadata/dasc-metadata-001/PROVENANCE.md) and [Figshare inventory](metadata/dasc-metadata-001/figshare-article-12198225.json) |
| Dynamin archive directory/footer byte ranges | [range manifest](metadata/dynamin-manifest-001/manifest.json) |
| Pinned SMAP spherical-cap source | [provenance](locmofit_cap_source_current_provenance.json) gives the exact commit URL, Git blob and SHA-256 |

Historical source notes retain their original local-cache links. Those payloads
are intentionally unbundled; use the public URLs recorded beside them. The old
`locmofit_contract_manifest.json` also lists the unbundled SMAP `.m` file; its
absence in a clone is an external-input requirement, not a lost local result.
Verify the recorded hashes after retrieval before comparing with a frozen run.
Public availability alone is not treated as redistribution permission.

## Offline persistence demo

Use a new ignored directory and the commit being tested:

```powershell
$baselineCommit = git rev-parse HEAD
.\.venv\Scripts\python.exe -m mechanome.research.demo prepare .pytest-controller-demo --commit $baselineCommit
.\.venv\Scripts\python.exe -m mechanome.research.demo resume .pytest-controller-demo
.\.venv\Scripts\python.exe -m mechanome.research.demo resume .pytest-controller-demo
```

The separate processes create SQLite events, hashed artifacts and `audit.json`.
The final resume reports `already_complete` without another attempt. This is a
scripted restart/idempotency demonstration, not autonomous scientific reasoning.
The baseline commit is recorded metadata; it does not attest a clean worktree.

## Offline work-unit checkpoint

The [accepted extension](WORK_UNITS_FINDINGS.md) was checked by one lead-owned
pytest invocation: 17 tests, all passed. [Ledger](work_units_test_runs.json) pins
tested source; [source ZIP](work_units_source_001.zip) retains its bytes. To check
a future checkout without altering historical logs, run the two targeted files
with a fresh scratch `--basetemp`:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --basetemp .pytest-work-units-new tests/test_research_controller.py tests/test_research_work_units.py
```

This is dummy work only. Do not reuse the registered historical runner to refresh
accepted evidence; its invocation cap belongs to that attempt. The tests reopen
SQLite connections in one process and race two threads. They do not constitute
a separate-process crash/reboot demonstration or live-agent enforcement.

## Preserved process-recovery failure and diagnostic

The [recovery attempt](WORK_UNIT_RECOVERY_FINDINGS.md) stopped after one phase;
its scripts are single-use historical entry points with a failed persistent
ledger. Do not rerun them or reset their counters. The [snapshot ZIP](work_unit_recovery_attempt_001.zip)
retains SQLite, marker, logs and the exact scripts. [Direct-interpreter preflight](PROCESS_IDENTITY_FINDINGS.md)
has its own exclusive single-run records and likewise must not be rerun in place.
Inspect hashes and JSON outputs without opening the frozen SQLite for writes.
Neither is a biological computation or a complete crash/reboot test.

## Repaired continuation checkpoint

The [accepted repair](WORK_UNIT_RECOVERY_REPAIR_FINDINGS.md) used only the remaining
two phase launches and one callback. Its [snapshot](work_unit_recovery_attempt_002.zip)
contains the preserved-state continuation, honest reconciliation record, phase
receipts and final audit. Verify its [manifest](work_unit_recovery_repair_manifest.json)
and [lead audit](work_unit_recovery_repair_audit.json); do not rerun `prepare` or
phase commands in place. The original failure and spent budget remain part of
this result. The accepted controller's 17-test checkpoint is unchanged; no new
pytest run occurred. These scripts are bounded demonstration records, not a
live-agent execution service or a reusable batch reproduction interface.

## Independent-control and Bucher workbook checkpoint

The source decisions and their small JSON inventories are bundled; the two
CC BY 4.0 processed Excel payloads are ignored in `.cache-bucher-em-001/`.
[Registered file identities](bucher_em_contract_design.json) pin public URLs,
byte lengths and publisher MD5. The [observed inventory](bucher_em_contract_001.json)
adds SHA-256 and retrieval times. `inspect_bucher_em_contract.py` performs a
bounded network retrieval and ZIP/XML inspection; it is not an offline test.
The [count record](bucher_em_contract_counts_001.json) states its header-subtraction
algorithm and unresolved discrepancy. No new production test suite was needed
for this source/schema stage; the earlier 114-test checkpoint is a separate run.

## Inclusion and exact nonlinear checkpoints

[Bucher inclusion provenance](metadata/bucher-inclusion-001/source_provenance.json)
pins the only added supplement PDF (972,260 bytes, ignored cache). The source
note gives PDF pages and extraction details. The package checker uses only
standard-library ZIP/XML and the two verified EM files; its [frozen result](bucher_inclusion_package_001.json)
records script/design hashes and actual execution times. Reexecution writes a
fixed result filename: copy the script, design and corresponding cache into a
separate scratch directory before rerunning, preserving this frozen evidence.

The [nonlinear graph result](NONLINEAR_SOURCE_FINDINGS.md) is analytic. Two
independent specialist derivations and the lead derivation agree; there is no
numerical run or test-suite claim. Its manifest pins energy/conventions, theory,
findings and review. Neither new checkpoint reruns the earlier114-test suite.

## Compact-source uniqueness and actual-profile existence

The [uniqueness](NONLINEAR_UNIQUENESS_FINDINGS.md) and [existence](NONLINEAR_EXISTENCE_FINDINGS.md)
results are analytic, with separate theory, boundary/order checks and independent
reviews. Their manifests pin the accepted artifacts. Input snapshots preserve the
exact NEXT_CYCLE.md bytes used when designs were registered; the current direction
file is intentionally mutable. No production test suite or numerical solver was
run for these proofs.

The [numerical contract](nonlinear_numerical_design.json) remains fixed. Attempt1
made one solver call and failed while saving output; its source/results are
frozen and must not be rerun or overwritten. The002candidate and preflight checks
preceded the retained attempt 2 failure; do not rerun that fixed-output execution. Preserve
input hashes and report failure rather than widening the finite case set.
Its finite reservoir, sampled margins and original compatibility residual do not
establish measurement precision or biological source identification.

## Latest numerical failure and saved-polynomial diagnosis

Attempt 2 is frozen by [its manifest](nonlinear_numerical_manifest_002.json).
All 26 statuses were zero, but physical residuals failed. Do not run its
fixed-output runner again. The [independent reanalysis](nonlinear_numerical_reanalysis_002.py)
and [defect diagnosis](nonlinear_residual_postmortem.py) use saved coefficients
and perform no new BVP solves. They write fixed report names: inspect or copy
those scripts to fresh output paths for any reproduction, keeping frozen
reports intact. The [mesh plan](nonlinear_numerical_mesh_plan.json) describes a
fixed final mesh proposal and its required preflight; actual execution is recorded separately.

The [resumed 003 preflight](NONLINEAR_MESH_PREFLIGHT_FINDINGS_RESUMED.md) is now
accepted. Its [manifest](nonlinear_mesh_preflight_manifest.json) pins the actual
tested source, harness and checks. Three harness runs included two preserved
failures and a final pass, with zero BVP calls. Do not overwrite frozen check
reports by rerunning their fixed-output harness.

[Final attempt 3](NONLINEAR_NUMERICAL_FINDINGS_003.md) completed and failed physical validation. The [manifest](nonlinear_numerical_manifest_003.json) pins execution, profiles, results and review. [Independent saved-data reanalysis](nonlinear_numerical_reanalysis_003.py) made no BVP calls. It also writes a fixed report: use a fresh output path if reproduction is needed. Do not rerun the numerical solver or preflight harness; the three-attempt branch is closed. No numerical K/K3 result exists.

## Fixed known-load comparison

The [known-load theorem](KNOWN_LOAD_RECOVERY_FINDINGS.md) is analytic. Its [manifest](known_load_recovery_manifest.json) pins the design, proof, data comparison and independent review. Verify the force-balance sign, compact-support terminal value, first-exit bound and Gronwall estimate in those notes. No BVP or empirical fit was run; a software test suite would not verify the theorem or supply the missing measured controls.

## Pinned actin-code inventory

[Findings](ACTIN_CODE_FINDINGS.md) and the [manifest](actin_code_inventory_manifest.json) record static source inspection, not an executed simulation. `artifact_sha256` covers retained study notes and API metadata; `local_cache_sha256` covers author texts and headers excluded from Git. Missing local cache after cloning is expected, not hash corruption. Use the [request ledger](metadata/actin-inventory-001/REQUEST_LEDGER.md) for pinned identities if later retrieval is justified. Do not run the downloaded notebook or infer Figure 7 reproduction from embedded displays. This cycle used integrity and independent source review, not software tests or new solver calls.

## Myo1E feasibility and public table

The [feasibility manifest](myo1e_feasibility_manifest.json) preserves the source decision; the [repository manifest](myo1e_repository_manifest.json) preserves the table inventory. Notes and API metadata are in `artifact_sha256`; the unchanged CSV and HTTP headers are local input caches in `local_cache_sha256` and excluded from Git. A clone therefore need not contain those caches. The [request ledger](metadata/myo1e-repository-001/REQUEST_LEDGER.md) records pinned request identities and hashes. No author notebook was executed and no empirical effect was calculated. Do not repair date-like group IDs or run a condition comparison without verified definitions. Acquisition is stopped under the saved design, not automatically retried by reproduction instructions.

## Duration-composition design and yeast screen

The [duration manifest](recruitment_duration_manifest.json) freezes an independently reviewed population bound, [exact Fraction arithmetic](recruitment_duration_arithmetic.json) and PNG/SVG illustration. Inputs are hypothetical rational numbers; no empirical fit or solver ran. The sharpness proof is in the theory note, not established solely by arithmetic checks. The [yeast screen manifest](yeast_observables_screen_manifest.json) preserves indexed primary-source listings, corrected attribution and a disclosed query-cap overrun. No yeast source-data body has yet been retrieved or reproduced. Follow the separately bounded next task rather than treating listed filenames as validated observations.

## Yeast Figure 6 public source contract

The [manifest](yeast_figure6_contract_manifest.json) freezes the design, source
contract, independent review, findings, static table checks and request ledger.
The two CSVs and HTTP headers are preserved locally under
`research/metadata/yeast-figure6-001/` and excluded from Git. A fresh checkout
therefore contains the metadata and reported aggregates, not those cached bodies.
The [ledger](metadata/yeast-figure6-001/REQUEST_LEDGER.md) records exact publisher
URLs, 39,979 total body bytes and SHA-256 checks for deliberate later retrieval.
Do not silently redownload as part of an integrity check. The [static checks](yeast_figure6_table_checks.json)
record 1,106 finite time rows, increasing times within each block and no zero
`n`; they are schema checks, not biological tests. No trajectory contrasts,
error propagation or genotype significance test were executed.

## Synthetic dimming checkpoint

[The manifest](synthetic_dimming_manifest.json) freezes the executed source,
second-run results, controls, independent review, separate numeric reanalysis
and exact tracker snapshot. No external dataset is required. The historical
runner writes fixed output names and imports the live tracker; **do not rerun
it in place**, particularly after a validator repair. Reproduction requires
an isolated output directory and the frozen tracker hash. Each original main
invocation executed141tracker movies; [the attempt audit](synthetic_dimming_execution_audit.json)
records two invocations/282movies, which exceeded150. First-run artifacts were
not retained. The single-run checks do not establish attempt-level compliance.
The lead reanalysis uses saved rows and fixed-seed noise reconstruction, calls
no tracker and retains90numeric fixed-center transforms. Both saved scripts
parse, and the numeric reanalysis exited0. New reproduction work must register
its own scope/cumulative budget and preserve the accepted evidence.

## Tracking metric contract v2

[The reviewed repair](TRACKING_METRIC_FINDINGS.md) changes top-level validator
scores to all-presence and exposes an explicit detectable block. Sweep field
names now identify their population. The [manifest](tracking_metric_manifest.json)
freezes accepted source/tests and logs; current source hashes are dated working-tree
observations, while immutable copies preserve the accepted version for later review.
The targeted command was pytest on `tests/test_tracking_validation.py` and
`tests/test_orchestration.py`, executed by the [lead runner](tracking_metric_test_runner.py)
with a persistent cumulative ledger:15passed,1tracker movie. The final sweep key
rename was checked against the tested source hash, not followed by a repeated movie.
Do not reuse the archived runner/ledger in place for a future task: register fresh
invocation output paths and budgets. No broad software suite was rerun this cycle.
The new regression file is included in the ordinary offline checkpoint test list.

## Geometry transfer checkpoint

The [manifest](geometry_transfer_manifest.json) freezes the design, executable,
checks, empirical outputs, ledger, independent review, figure and no-fit audit.
The lead ran `.venv\Scripts\python.exe research/geometry_transfer.py --checks`
once (4 synthetic NNLS calls, including one expected finite-area rejection),
then `--run` once (27 empirical calls). The executable reserves calls before
execution and refuses reuse of an invocation, including after failure. Do not
reset its ledger or overwrite accepted output to reproduce a result.

The [separate audit](check_geometry_transfer.py) reconstructs predictions using
independent formulas and checks 207 group/model MAEs against the saved result,
without any fitting. It also opens its report exclusively; deliberate later
reproduction requires a fresh report path and a separately recorded budget.
S-BIAD566 caches remain excluded from Git. Existing source SHA-256, published
MD5 and old comparison locks must pass before computation. No automatic
redownload or lock refresh is part of this checkpoint. The PNG/SVG are static
plots of these saved scores with no uncertainty bars; all 27 fold/model scores
remain in the JSON. Final Ruff F checks passed for both new Python files.

## Campaign synthesis and endpoint screen

The [synthesis manifest](campaign_synthesis_manifest.json) pins the design,
review, actin prerequisite note, and ZIPs of the prior and accepted navigation.
The ordinary front doors remain mutable; their acceptance hashes are dated
observations. Both ZIPs were read back and their contents matched registered
input or accepted output hashes. No software tests or calculations ran.

The [endpoint manifest](endpoint_public_manifest.json) pins a source feasibility
assessment, not downloaded event data. The paper's selected-case results are
literature evidence, not independently reproduced tracker metrics. Two queries
and two parsed primary opens were used; no files or movies were retrieved.
No source fetch, simulation or fit is required to inspect these checkpoints.

## Two-channel public listing and observation result

The [source manifest](paired_shape_public_manifest.json) freezes the two-query,
three-open screen. The [schema manifest](star_workbook_schema_manifest.json)
freezes the first local socket failure; no workbook bytes were acquired. Do not
rerun its one-shot inspector as an access rescue. The public listing is not a
verified event table.

The [observation manifest](star_observation_manifest.json) freezes a symbolic
inverse/covariance proof and one [exact arithmetic invocation](star_observation_checks.json)
with six registered hypothetical cases. Review the [theory](STAR_OBSERVATION_THEORY.md)
and [checker](star_observation_checks.py); the result-file guard refuses a repeat.
No pytest, fit, Monte Carlo, raw microscopy or production-code change was part
of this stage. Shared-error algebra does not validate the published full STAR
observation model or infer a biological lag.

## Final distribution counterexample

The [manifest](star_distribution_manifest.json) preserves one registered positive
four-point pair, the [proof](STAR_DISTRIBUTION_THEORY.md), [review](STAR_DISTRIBUTION_REVIEW.md),
[checker](star_distribution_checks.py) and [sole exact result](star_distribution_checks.json).
The checker verifies equal first/second exponential moments and the rational
log-product 27/32. Monotonicity of log gives the strict mean-height difference;
no floating-point approximation or search is needed. The exclusive result-file
creation refuses repeat execution. No pytest or production-code change applies.
