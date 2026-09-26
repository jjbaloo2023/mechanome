# DASC primary-methods note — dasc-methods-001

**Primary source read.** Wang X, Chen Z, Mettlen M, et al. “DASC, a sensitive
classifier for measuring discrete early stages in clathrin-mediated endocytosis,”
*eLife* 2020;9:e53686, DOI [10.7554/eLife.53686](https://doi.org/10.7554/eLife.53686),
open primary copy at [PMC7192580](https://pmc.ncbi.nlm.nih.gov/articles/PMC7192580/).
The math-preserving primary JATS snapshot used for equation and table claims is
[`PMC7192580.jats.xml`](metadata/dasc-methods-001/PMC7192580.jats.xml)
(334,644 bytes; retrieved 2026-09-22 from
`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7192580/fullTextXML`;
SHA-256 `99C288FD03D3E0EC4D9ABA72074D7FCAE14BD40B2DBE0952A1E071C4B5BD5E0E`).
The smaller text-oriented companion is
[`PMC7192580.xml`](metadata/dasc-methods-001/PMC7192580.xml) (217,627 bytes,
from `https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC7192580/unicode`).
Together retained source bytes are 552,271 (<2 MiB). Exact locators below
refer to the published paper's Results/Figures and Materials and methods headings.

## What DASC labels—and what it does not

DASC takes cmeAnalysis **single-channel TIRF intensity tracks** of clathrin
structures (CSs). Published **Equation 1** defines the intensity trace
`I_n(t)`; **Equation 2** defines disassembly risk `D(i,t)` as the log ratio of
summed downward-transition probabilities to summed upward-transition
probabilities for that intensity/time state; **Equation 3** maps each
intensity trace to a D-series.  The three features are: `d1`, the mean of the
D-series (**Equation 4**); `d2`, the log of its range normalized by lifetime
(**Equation 5**); and `d3`, a standardized third moment/skewness (**Equation
6**).  They are then k-medoids clustered (Euclidean distance, `k=3`) into
**AC**, **CCP**, and **OT** labels. See Results, “Disassembly Asymmetry Score
Classification (DASC): a new method to analyze CCP growth and stabilization”
and “DASC accurately identifies dynamically distinct CS subpopulations,”
Figure 1C–F and Figure 2A; Methods, “Computational flow of DAS analysis.”

The labels are algorithmic classes of fluorescence dynamics, not direct
fission/scission observations.  The authors explicitly say the DASC CCP group
can include late-abortive as well as productive CCPs (Discussion, “Unbiased
classification…”); their future-work statement calls for dual-channel tests to
identify kinetically distinct subpopulations.  Thus CCP% is a published
*stabilization efficiency* proxy, not an unconditional count of scission
events.

## Observation, selection, and censoring boundaries

Tracks come from 1 frame/s TIRF movies and cmeAnalysis detection/tracking
(Materials and methods, “Microscopy imaging and quantification”).  DASC needs
about >=200,000 intensity traces from ~20 movies/condition, adequate SNR for
dim ACs, and 7.5-minute movies to avoid truncating most long-lived tracks
(Discussion, “The applicability and application of DASC”).  It is unsuitable
for endogenous-level CLCa signal in their setup and for cells with abundant
static lattices (Results, Figure 2—figure supplement 1 discussion).

For **initiation**, they counted *all trackable CSs*, including invalid tracks:
`CS init = N_total/(cell area × movie duration)`.  Invalid means not always
diffraction-limited and/or containing consecutive gaps.  For **CCP%**, they
used `N_CCP/N_valid`, so the denominator excludes invalid traces (Methods,
“Computational flow of DAS analysis”). This is material selection: the αAP2(PIP2−)
events were dimmer, and the authors attribute a discrepancy from earlier lower
initiation estimates partly to more early events being invalid in prior
valid-track-only analysis (Results, Figure 3C and Figure 3—figure supplement
1).  Movie length is intended to limit right-censoring, but not proof that it
eliminates it; detection and gap rules remain intensity/SNR-sensitive.

Clustering has a hard boundary over continuous, overlapping AC/CCP data.  The
10% nearest the AC/CCP boundary had intermediate properties; removing them
lowered both control and siCALM CCP% but retained the relative siCALM effect
(Results, Figure 2—figure supplement 2A–E). The AP2 perturbation Results
explicitly state that control-derived k-medoids boundaries were applied to
perturbation tracks. Methods step 9 has apparently conflicting repeat-clustering
wording; paper-version implementation remains unresolved (DASC_ANALYSIS_RULES.md).
Same-day controls were required, while the cross-day EAP screen pooled
intensity-adjusted controls and made 300 no-replacement 20-movie bootstrap
control/siMock draws (Methods, “Data pooling for conditions acquired on different days”; Figure 4G and
Figure 5A).

## Published perturbation outcomes (not new predictions)

* **αAP2 PIP2-binding contrast.** Cells were α-AP2 siRNA-reconstituted with
  siRNA-resistant WT or PIP2-binding-defective αAP2 K57E/Y58E (Materials and
  methods, “Cell culture…”). Figure 3A–C/Table 1 report PIP2− vs WT: AC
  fraction increased, CCP% fell 27% (***), all-track initiation rose 36% (***),
  CCP rate rose 27% (**) and median CCP lifetime decreased (*). Figure 3C
  states no AC-lifetime change.  This verifies a phenotype consistent with
  impaired AP2-PIP2-mediated stabilization, but dimmer mutant CSs and the
  track-validity boundary prevent treating it as a clean absolute initiation or
  scission measurement.
* **CALM knockdown.** Figure 4B–F/Table 1 report siCALM vs siControl:
  initiation **−38%***, CCP% **−30%***, CCP rate **−67%***, median CCP
  lifetime **+25%***, TfR internalization **+21%*** and TfR efficiency
  **−64%***.  The text reports both more short- and long-lived CCPs.  This is
  a published CALM-loss phenotype, not an experiment that isolates CALM's
  curvature-sensing/driving mechanism from expression, recruitment, or other
  CALM functions; the authors themselves discuss cell-type/redundancy context
  (Discussion, “DASC reveals functions…”).

## EPI/TIRF geometry boundary

The primary paper uses nearly simultaneous 488-nm EPI/TIRF acquisition,
classifies tracks from the **TIRF** trace, cohorts by lifetime, and estimates
the center displacement/invagination `Δz` from adjusted EPI and TIRF cohort
intensities.  It reports the **normalized** quantity `Δz/h`, where `h` is the
characteristic TIRF-field depth (Results, Figure 3F and Figure 3—figure
supplement 3A–G; Methods, “Averaged intensity and Δz time course”). The paper
reports h = 115 nm as a setup setting, not an independently verified calibration
of the deposited AP2 movies. The EPI channel
is adjusted to match initial TIRF growth rate because their linear intensity
ranges differ.  Figure 3F reports that 20-s DASC CCP cohorts gain this depth
proxy whereas AC cohorts do not; intensity-matched subset results are Figure
3—figure supplement 3E–G.  It measures an optical, cohort-averaged normalized
depth proxy—not an unconditional absolute curvature, vesicle radius, or
scission time. Ordinary one-channel deposited TIRF movies cannot supply it.

## One feasible contrast if a new reanalysis is later authorized

Prefer **αAP2 WT vs PIP2−**, restricted to their same acquisition date, for a
bounded fluorescence-dynamics feasibility check: the perturbation is a defined
rescue/mutant pair and avoids the broader pleiotropy/isoform compensation of
CALM depletion.  Reproducing lower CCP% in PIP2− with a fixed-control DASC
pipeline is an engineering **reproduction target/expectation**, because the
paper already reported it; report invalid-track fractions and intensity
distributions alongside it.  A genuinely new sensitivity question is whether
the effect's magnitude/classification stability persists under transparent,
pre-specified detection and valid-track rules.  Either result would not
distinguish a direct curvature mechanism from altered AP2 activation,
recruitment, or detection.  The archive contains single-channel CLCa movies,
so this contrast cannot independently test the published EPI/TIRF depth claim
without additional dual-illumination data.
