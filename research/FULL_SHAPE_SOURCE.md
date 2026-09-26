# Hassinger full-shape source (arXiv:1604.08629v1)

Primary HTML checked 2026-09-23; these locators apply only to [arXiv:1604.08629v1](https://arxiv.org/html/1604.08629v1), not the related PNAS 2017 DOI 10.1073/pnas.1617705114.

**Equations/convention.** Main Eq. (1), HTML 76-80: `W=k(H-C)^2+kbar K`. The authors define their `k` as twice the usual Helfrich modulus. Therefore repository `kappa/2(2H-c0)^2` matches only with `k=2*kappa`, `C=c0/2`; retain this factor-of-two conversion. Main Eq. (2), 80-82: `k Delta(H-C)+2k(H-C)(2H^2-K)-2kH(H-C)^2=p+2lambda H+f dot n`. Eq. (3), 83-86, gives tension variation. `f` is force per area; total force is its area integral (480-481). Units: Table 1, 550-567.

**Source discrepancy (unresolved).** v1 main Eq. (3), HTML 85, prints `lambda_,alpha=-2k(H-C)C_,alpha-f dot a_alpha`. Its own supplement S13/S14, 331-336, and axisymmetric S27/S32c/S40c, 383/407/442, instead print the curvature-gradient term with **plus** sign. The accessible narrow search did not yield an authoritative published-PNAS equation page, so this is not resolved as a typo. Also S6 caption calls its intermediate case `0.002` (619), whereas Fig. 4/main text use `0.02` (103,106); treat it as another v1 internal conflict. Linear O(C) benchmark is unaffected; a nonlinear BVP needs a variational sign check before implementation.

**Full BVP.** The six variables are `r,z,psi,H,L,lambda`; first-order system S18/S22/S24/S26/S27 (342-385). Conditions S28a,b (386-390): `r(0+)=L(0+)=psi(0+)=0; z(S)=psi(S)=0; lambda(S)=lambda0`. Pulling adds `z(0+)=zp` (S29); pinching `H(0+)=Hp` (S30). This is a finite patch joined to a flat tension reservoir.

**Area/outputs.** `a(s)=2pi integral r ds` (S35, 415-423); coat arc length and coat area can change in opposite directions through instability (485-495). Tension energy uses whole-patch `lambda0(A_tot-A_proj)` (S44, 528-539), not coat area. Fig. 2: high `0.2` versus low `0.002 pN/nm`; low-tension area growth reaches Omega and stops at 5-nm neck gap (89-95). Fig. 4: at `0.02`, `A_coat` 20,065 to 20,105 nm^2 snaps, plotted against tip mean curvature (102-110). Fig. 6 reports >100 kBT branch gap (118-127). Fig. 8 fixes 17,593 nm^2 while force bridges branches (132-134).

**Guardrail.** Compare local tip curvature, depth, neck, coat/total/support areas separately. This source cannot directly validate a spherical-cap area signature: its tension is surface tension and its force is distributed on a specified support.
