# Myo1E observable feasibility — bounded primary-source note

**Paper identity/status.** Smith *et al.*, “Class-I myosin responds to changes
in membrane tension during clathrin-mediated endocytosis in human induced
pluripotent stem cells,” *PNAS* **123**(9):e2532817123 (issue 3 March 2026),
DOI [10.1073/pnas.2532817123](https://doi.org/10.1073/pnas.2532817123),
PMCID [PMC12956820](https://pmc.ncbi.nlm.nih.gov/articles/PMC12956820/), PMID
41734073. The article is accepted (26 January 2026), published open access;
the source pass used parsed PMC text. Access and byte accounting are in
[ACCESS_LEDGER.md](metadata/myo1e-feasibility-001/ACCESS_LEDGER.md).

## What comparison is actually available

The concrete public comparison is an **across-condition** hypotonic-shock
experiment, not a calibrated per-event tension measurement. Cells received 300
(no shock), 225, 150, or 75 mOsm media (Results, Fig. 4 introduction,
PMC lines 212--217). At 75 mOsm the paper reports more Myo1E-positive CME
sites (about 8% to 33%) and higher Myo1E-positive initiation rate; Fig. 4B--G
also reports active/persistent-site ratio, Dnm2 lifetime/intensity, and AP2
displacement (caption, lines 223--225). The control is both untreated medium
and addition of iso-osmolar 300 mOsm medium. Sampling reported in the caption
is 24 control movies and 6 movies per osmotic-shock condition; gray points are
per movie and colored triangles technical-replicate means. Tracks/events are
nested within those movies, so event counts are not independent biological
replicates. The caption does not identify independent cultures, cells, or
experiment days, so the effective biological unit is unresolved. Hypotonic
shock is a tension-raising intervention with possible osmotic/cortical effects;
it is not a clean, isolated calibrated-tension dial.

There is a denominator and pairing constraint for any table: Fig. 4C's caption
calls the quantity a Myo1E-positive-to-negative **ratio** per movie, while the
Results describe about 8% to 33% of sites (lines 216, 223--225). A later table
must preserve and verify whether it is \(N_+/(N_++N_-)\) or \(N_+/N_-\); these
must not be silently interchanged. The osmotic-shock Methods say one control
movie was acquired before solution addition and imaging started 10 s after
addition (line 301). That indicates possible within-acquisition pairing whose
identifiers must be retained, rather than assuming that the 24 control and six
shock movies are wholly independent groups.

This does connect a tension-raising intervention, a Myo1E signal, and an event
proxy: in triple-tagged ADM cells, AP2-RFP marks event appearance and the
Dnm2-GFP peak marks the authors' scission timing proxy (Methods/Results,
lines 154--155; image processing, lines 306--308). Myo1E-JF635 is the third
channel, linked downstream to AP2/Dnm2 tracks (lines 306--308). The proxy is
track lifetime/initiation/active-versus-persistent classification and Dnm2
timing, **not** direct confirmation of vesicle internalization.

Myo1E and ArpC3/actin-module evidence is not a single same-event triple-channel
measurement in this source. ArpC3 is measured in the AP2/Dnm2/ArpC3 ADA
background, separately from ADM Myo1E movies. Fig. 5 compares control and
Myo1E-knockout cells across osmotic conditions: at 75 mOsm it reports fewer
ArpC3-associated CME sites in knockout, longer ArpC3 lifetimes, and lower
normalized mean ArpC3 intensity only at the highest shock (lines 232--242).
It is strong condition/genotype evidence, but does not pair Myo1E and ArpC3
intensities on the same CME event. Fluorescence here is a tagged-protein
localization/intensity measurement; it is not force, barbed-end number, or
calibrated actin mass.

## What microaspiration does and does not add

Fig. 3 gives a separate before/after, cell-level fluorescence response to a
mechanical intervention. A pipette aspirates until membrane enters it (lines
197--200); Fig. 3B and D show baseline-normalized ArpC3 and Myo1E intensity
traces, respectively, with 95% confidence intervals across 51 surrounding-cell
traces (ArpC3) and 23 cells (Myo1E) (caption, lines 206--207). Methods say the
needle was run at constant force but provide no numeric force/tension value and
analyze colony cells surrounding the pulled cell because the aspirated cell
often leaves the TIRF field (lines 294--297). This supports an intervention
response, not a measured local tension or within-aspirated-cell CME outcome.

## Selection and observation limits

TIRF acquired one focal plane at 1 frame/s for 5 min (Methods, lines 277--280).
`cmeAnalysis` extracted diffraction-limited spots; AP2 was the CME fiducial,
Dnm2 a secondary scission marker, and the JF635 channel was tracked separately
then linked to CCPs (lines 306--308). For the baseline Myo1E analysis, valid
events had lifetimes 20--300 s, while persistent events were >300/301 s
(Results lines 166--168; Fig. 2 caption lines 187--189). Thus the reported
selection censors very short and long tracks from the active-event analysis;
the exact previously published selection criteria are cited but not reproduced
in the primary text excerpt. Baseline Myo1E-positive/negative event comparisons
also condition on detectable Myo1E and differ in lifetime distribution (Fig. 1,
lines 162--168), so they cannot establish that Myo1E recruitment causes a
same-event tension change.

## Feasibility disposition

The smallest descriptive comparison worth a separately specified table check is:
movie-level Fig. 4C/D condition records (osmolarity, movie/technical replicate,
Myo1E-positive and -negative CME-track counts with the documented denominator,
area/time for initiation rate, and pre/post movie/well identifiers), joined only
to the stated track definitions. A compatible negative result would be no
condition-associated change in the declared Fig. 4C metric or initiation rate
after pairing/cluster accounting. This comparison can describe
intervention-associated Myo1E recruitment and CME-track behavior; it cannot
estimate tension, force, barbed ends, or establish an individual-event causal
rescue.

The data statement names the analysis notebook repository
`DrubinBarnes/Smith_et_al_Myosin1E_Manuscript` (PMC lines 508--510; reference
54, lines 443--444); it says other data are in the article and/or supporting
information, not that raw tables are deposited. The single allowed official
landing attempt was a cache miss, so no public small table, path, schema, or
deposited output has been verified. This is an exact availability gap, not
evidence that data are absent. No table download is authorized in this stage.
