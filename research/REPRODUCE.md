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
