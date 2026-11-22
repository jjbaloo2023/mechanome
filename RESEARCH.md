# Mechanome methods and evidence

Mechanome develops models and inference tools for cell mechanics. Its membrane
engine, `curvo`, combines forward model search with conditional inverse inference.
The CME campaign has established descriptive geometry results, mathematical
identifiability limits, and observation-software checks. It has not selected a
biological mechanism or recovered calibrated forces from the assessed public
cap-fit tables. Start with [the reviewed findings](research/FINDINGS.md).

This guide supersedes the earlier scientific reference. The
[original reference at checkpoint 47f66f8](https://github.com/jjbaloo2023/mechanome/blob/47f66f8/RESEARCH.md)
and [historical manuscript](MANUSCRIPT.md) retain earlier demonstrations and
interpretations. Their numerical tables and figures have not been regenerated
by this correction. Original study files remain unchanged.

## Models and units

The membrane evaluator is [curvo/evaluator_tier0.py](curvo/evaluator_tier0.py).
It minimizes energy within declared tube or spherical-cap shape families.
Lengths use nm, mean curvature uses nm^-1, bending rigidity uses kBT, membrane
tension uses kBT/nm^2, and force uses pN. The conversion constant is defined in
[curvo/constants.py](curvo/constants.py).

For a tube with zero spontaneous curvature, the closed-form radius is
`R = sqrt(kappa / (2*sigma))`. Its holding force is
`f = 2*pi*sqrt(2*kappa*sigma)*kBT_zJ` in pN under those internal units.
Agreement with the numerical minimum checks implementation of that model;
it does not establish agreement with independently measured forces.

For a spherical cap of fixed area `A` and opening angle `psi`,
`R = sqrt(A / (2*pi*(1-cos(psi))))`. The energy includes bending, perimeter,
membrane tension, and active-force work. Mean curvature is `1/R` for a sphere
and `1/(2*R)` for a cylinder; spontaneous curvature enters the bending term as
`(2/R-c0)^2`. Shape-stage thresholds are model readouts; crossing one does not
measure membrane scission.

The forward search in [curvo/orchestrator.py](curvo/orchestrator.py) proposes
player representations and parameters, validates them, and evaluates the model.
A successful search finds a feasible combination within its tolerance;
it does not establish uniqueness, protein causality, or a biological mechanism.
AlphaFold signals inform representation proposals, not experimentally established
mechanical roles. Run the offline example in [README.md](README.md).

## Inverse inference and validation scope

[curvo/analyze.py](curvo/analyze.py) connects perception, parameter inference,
restricted-model comparison, and reporting. Its model assumes a 24-frame
side-view movie and renderer-specific geometry, imaging, and assembly assumptions.
Active-force magnitude uses the synthetic renderer's actin-intensity calibration;
this calibration cannot be assumed for an arbitrary experimental actin channel.

Posterior widths, correlations, and prior bounds assess identifiability.
Synthetic recovery checks whether known simulation inputs can be recovered under
the tested model and noise assumptions. Neither a narrow posterior nor synthetic
recovery alone establishes experimental accuracy. Model preference is conditional
on the hypotheses and observation likelihood. Capped fits remain provisional.
Point estimates additionally require an explicit supported synthetic observation
context. Custom coverage or calibration conditions remain exploratory; see
[CODEBASE.md](CODEBASE.md). Numerical evidence errors are retained and must leave
a conservative separation from every competitor before a decisive verdict.
The old force calibration predates the geometry-validity repair and is retired;
current analyses withhold point estimates and decisive mechanisms pending a
reviewed recovery qualification of the updated pipeline.

[validation/tether_sted.py](validation/tether_sted.py) uses published membrane
parameters from Roy et al. (2020), doi:10.1021/acs.nanolett.9b05232, to generate
radii and reference forces, add simulated radius noise, and invert the radii.
**It loads no measured radius/force pairs.** Its bias and interval-coverage
numbers describe synthetic tube recovery. Earlier descriptions of this example
as real force-paired validation were incorrect. Its geometry also differs from
the spherical-cap movie pipeline.

The schema distinguishes GROUNDED, MEASURED, and LINKED records. GROUNDED is a
software tier, not proof that an input was measured. The tether emitter marks
its input as synthetic and the membrane registry uses `built_analytic` /
`analytic_limit`. The tether example does not support real force-paired status.

## Supported results and evidence routes

| Question | Reviewed result | Scope and source |
| --- | --- | --- |
| Do static cap-fit curves transfer? | Rankings change with cell line and inclusion policy | Population geometry, not within-pit dynamics; [geometry transfer](research/GEOMETRY_TRANSFER_FINDINGS.md) |
| Can shape identify mechanical sources? | Recovery depends on boundaries, mechanics, and sufficiently known loading | Conditional mathematics; [known-load recovery](research/KNOWN_LOAD_RECOVERY_FINDINGS.md) |
| Do two channels identify coat mean height? | Distinct positive distributions give identical signals and different mean heights | Exact idealized counterexample; [distribution findings](research/STAR_DISTRIBUTION_FINDINGS.md) |
| What did the tracking repair verify? | Consistent populations, matching, and scoring denominators | Software contract, not endpoint calibration; [tracking findings](research/TRACKING_METRIC_FINDINGS.md) |
| Did the nonlinear numerical branch validate? | Bounded attempts failed the physical-residual gate | No accepted numerical K/K3 result; [final attempt](research/NONLINEAR_NUMERICAL_FINDINGS_003.md) |

The [study index](research/INDEX.md) links full derivations, designs, sources,
results, reviews, and retained failures. The [assessment](research/ASSESSMENT.md)
explains what evidence would support stronger inference. Source-access failures
and missing controls are not negative biological results. Independent review
records document checks of their stated scope, not journal peer review or novelty.

## Other scales and reproduction

The `mechanome` package includes tissue junction balance, cortical tension,
adhesion-bond kinetics, channel gating, and a saved structural screen. Forward
kernels check analytic limits and published parameter anchors. Those checks are
distinct from validation against independent raw experimental datasets. Screen
hash checks establish saved ranking integrity; imports do not rerun the screen.
See [CODEBASE.md](CODEBASE.md) for entry points.

[research/REPRODUCE.md](research/REPRODUCE.md) gives the checkpoint software checks,
a read-only exact counterexample check, input locators and hashes, and historical
runner restrictions. Frozen runners must not overwrite old results. Software
tests do not revalidate historical scientific claims. Dependency ranges support
installation; they are not a frozen scientific environment. Record the commit,
Python and dependency versions, input identities, and numerical tolerances for
new calculations. Operational status belongs in [research/NEXT_CYCLE.md](research/NEXT_CYCLE.md).
