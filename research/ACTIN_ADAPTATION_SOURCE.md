# Akamatsu et al. 2020: bounded load-adaptation source note

**Primary source.** M. Akamatsu *et al.*, “Principles of self-organization and
load adaptation by the actin cytoskeleton during clathrin-mediated endocytosis,”
*eLife* 9:e49840 (2020), DOI
[10.7554/eLife.49840](https://doi.org/10.7554/eLife.49840). The official eLife
HTML endpoint returned a JavaScript challenge, but the article's indexed
primary-text/PDF result supplied the Results, Methods, and Figure 7 locators
used below. This is a source check, not a reproduction.

## Concrete comparison

Figure 7 is the usable load-adaptation prediction beyond pit geometry. The
agent-based Cytosim network is run at membrane tensions 0.015, 0.15, and 1
pN/nm (Fig. 7B--D); Fig. 7E--H summarize 144 simulations, using the last five
seconds. The reported sweep is membrane tension. The source does not, in the
Figure 7 description, enumerate every otherwise-fixed model parameter, so this
note does **not** claim a fully independently verified held-fixed parameter
table.

Its comparison is precise: the dashed line in Fig. 7E is a *constructed
non-adapting reference*, not a separately simulated rival mechanism. Methods
define it by fixing internalization work \(E=\tfrac12kx^2\), calibrating from
the low-load \(k=0.01\) pN/nm case, then increasing load \(k\); fixed \(E\)
therefore predicts decreasing displacement \(x\). (The Fig. 7 low-tension
panel is labeled 0.015 pN/nm, while the Methods' \(k\) is the calibrated
spring resistance/load coefficient. Figure 1 identifies resistance as the
force--internalization slope and relates it to membrane tension; the exact
conversion used for Fig. 7 needs verification. The two numerical labels should
therefore not be called an inconsistency or assumed to name the same quantity.)
The adaptive network instead changes work with load through its modeled assembly
and organization. Thus a freely
prescribed-force cap trajectory is not a falsifiable alternative to this
comparison unless it is given the same load law, energy/work constraint, and
spatial-network constraints.

At 1 pN/nm, internalization slows but exceeds this constant-energy expectation
(Fig. 7E). In the same simulations, barbed ends near the pit base rise (Fig.
7F), the number of filaments in the Hip1R-bound network rises (Fig. 7G), and
base-proximal bending energy rises (Fig. 7H). The article links this chain to
more base encounters, Arp2/3 binding/nucleation, and bending. This supplies a
**proposed synthesis for a test**, rather than a directly reported experiment:
across a controlled load increase, residual
internalization above the fixed-energy curve should co-vary with a
base-proximal actin-network measure, rather than geometry alone.

## Output versus observable

The Fig. 7 quantities are **simulation outputs**: pit internalization, count of
barbed ends near base, count of Hip1R-bound-network filaments, and bending
energy. “Near base/neck” is an analysis cutoff of 7.5 nm from the relevant
membrane surface (Methods); it is not itself a direct optical readout. The
experimental-side evidence cited by the article includes live-cell fluorescence
trajectories/molecule counts, endogenous Arp2/3 molecule counting, and bent
filaments in cryo-electron tomography. This bounded check did **not** verify a
tension-conditioned experimental measurement of the Fig. 7 network metrics or
a measured nanometre displacement matched to Fig. 7E; those Fig. 7 curves
remain simulation output. A valid experiment therefore needs a calibrated load
or tension perturbation plus time-resolved pit displacement and an independently
defined base/neck-proximal actin (or Arp2/3) measurement. Total actin intensity
alone does not identify the simulated 7.5-nm barbed-end count or bending energy.

## Small verified public next artifact

The Methods link the public repository
[DrubinBarnes/Akamatsu_CME_manuscript](https://github.com/DrubinBarnes/Akamatsu_CME_manuscript)
for analysis code. Its landing page verifies it is public, GPL-3.0 licensed, and
contains `cytosim`, `fluorescence_quantification`, and `ImageAnalysisPipeline`.
The smallest defensible next step is **metadata/README and file-inventory
inspection only** to locate the Fig. 7 analysis inputs and confirm whether an
extractable tabular time series exists; no archive download, code execution, or
claim that deposited files reproduce Fig. 7 is warranted from the landing page.

## Scope limit

This article supports an adaptive-network prediction conditioned on its
agent-based network and spring-load construction. It neither calibrates the
repository's prescribed active work term nor makes curvature alone an estimator
of actin force, barbed-end number, or network energy.
