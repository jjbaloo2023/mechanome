# Akamatsu CME code inventory — bounded pinned pass

**Disposition:** partial, pinned code/analysis contract; no deposited Figure 7
table was verified. This pass retrieved no archive, binary, or movie; it saved
five source/configuration text files as inert data and executed no author code.
The complete request ledger and retained
responses are in [actin-inventory-001](metadata/actin-inventory-001/).

## Pin and retrieval bounds

`main` resolved at 2026-09-29T12:02:58Z to commit
`e0d5426515abaa37fdc9cd3151e108480a0337eb`, whose Git commit tree is
`c5b54f0ff429515519a8355ef309aa07e28598e1`; its committer date is
2019-08-21. This pins the inspected current branch tip, but does **not** prove
that it is the paper-version revision. Thirteen retained requests all returned
HTTP 200, with zero failures, five source-text files including README, and
261,830 response-body bytes (cap 1,048,576). Each status, UTC response date,
body bytes, SHA-256, and Git blob identity where available is recorded in
`metadata/actin-inventory-001/REQUEST_LEDGER.md`.

The untruncated root tree contains `cytosim`, `ImageAnalysisPipeline`,
`fluorescence_quantification`, and `kymograph_analysis`. The bounded subtree
walk inspected only `cytosim/configs`,
`cytosim/parameter_sweeps_pythonReporting/simulations`, the
`vary_spring_stiffness` configuration subtree, and `cytosim/plotting_python`.
It is not an absence audit of the repository.

## What the retained configuration verifies

The `vary_spring_stiffness` subtree has nine `.cym` configuration blobs and no
output files in that *specific* subtree. The retained endpoints are
`vary_spring_stiffness0000.cym` (Git blob
`ff728ebcc796c1761d3baa5b5d54204cd4d484d0`) and `...0008.cym` (blob
`b04b928ca84b7d6d268a140cebdecf5410e2a6fc`). Their exact diff is one setting:
line 257 changes `confine = first_surface, 1, insidecell` to
`confine = first_surface, 50000, insidecell`. The preceding comment labels this
field spring stiffness and gives pN/µm (lines 249--255). This verifies a
pair-level sweep with all other text in those two files held equal; it does not
identify a Figure 7 run or establish a membrane-tension-to-spring-
stiffness calibration.

The separately retained `cytosim/endocytosis.cym` sets the corresponding
`first_surface` confinement stiffness to 150 pN/µm at line 255; it uses 200
Arp2/3 couples (line 579) and a 15-s run with 150 frames (lines 596--602).
The dimensional equality 150 pN/µm = 0.15 pN/nm matches the article's
medium-tension number but does not, by itself, prove that this config generated
Figure 7 or validate a physical conversion. The article's tension labels and
the Cytosim spring coefficient remain distinct quantities in this inventory.

The `.cym` sweep endpoint also declares `time_step = 0.00005` (line 12),
`viscosity = 1` (line 17), and `growing_force = 5` pN (line 94), while its
`set simul` declaration names `internalize.cym` (line 7). Those are verified configuration values,
not a complete Fig. 7 held-fixed control table: the figure identity and all
otherwise-fixed controls were not established within the five-file bound.

## Analysis and output contract

The retained `plot_multiple_param_sweeps_Akamatsu_2019.ipynb` (blob
`dc0d515d885023a8ba43eed6afc9d605621ff956`) is an analysis notebook with
embedded Jupyter outputs, but not a verified raw or matched per-run Figure 7
table. Its cells load external pickle paths such as
`dataframes/<parameter>_solid_allparams.pkl`, `...solid_propertiess.pkl`,
`...hip1r_clusters_ends_recalibrated.pkl`, `...associated_arp_allparams.pkl`,
and `...branched_actin_bound_ends_bending.pkl` (notebook lines 673--699).
The notebook's mapping table names a `vary_spring_stiffness_output` directory,
but that is an input/output path name rather than verification of an included
table or matched per-run time series.

The notebook supplies an independently inspectable aggregation pattern:
`last_timepoints` and `last_timepoints_count` select time 10 through 15,
aggregate within `(param_sweep, run, time)`, then report by-configuration means
and standard deviations (lines 1005--1027). This is a direct aggregation of
the retained time rows by configuration; it does not first form per-run means
or select each run's relative final five seconds. The calls apply it to near-base
ends (1079--1081), Arp2/3 (1111--1113), bending energy (1141--1143), and
attached filaments (1174--1176). That is compatible with the paper's reported
last-five-second summaries, but this bounded check did not establish it as the
exact Figure 7 notebook/run set, nor retrieve the pickle inputs. The same
notebook also has a distinct 12-s internalization estimator (lines 739--762),
so it must not be substituted for the Fig. 7 last-five-second statement.

The larger `parameter_sweep_analysis_plots_Akamatsu_2019.ipynb` is listed in
the retained plotting-tree metadata as 4,436,919 bytes, exceeding the entire
retrieval budget; it was not fetched or range-bypassed.

## Unaccepted follow-up option

A separately registered, small saved-table availability check could target the
specific `vary_spring_stiffness_output`/Figure 7 candidate at this pinned
revision and establish whether the named pickles or a compact tabular export
actually exists, together with its run/config identifiers. Until then, output
writing/reading code and path names do not establish a matched Figure 7 raw
time-series dataset. This is only an option for lead selection; it does not
authorize a repeat metadata check or displace the separately scoped experimental
feasibility alternative.
