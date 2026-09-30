# Recruitment versus duration composition: a prospective test

Accepted after [independent review](RECRUITMENT_DURATION_REVIEW.md), 29 September 2026. A marginal increase in positive tracks can arise while the probability of positivity at any given observed duration remains unchanged. The [theory note](RECRUITMENT_DURATION_THEORY.md) defines that restricted observable null and derives bounds that can falsify it when its inputs are measured.

For a common conditional positivity function between zero and one, the difference in marginal positive fractions cannot exceed the total-variation distance between the two population duration distributions. Fixing the baseline positive fraction gives a sharper feasible interval by allocating baseline probability to the largest or smallest duration likelihood ratios. The derivation covers atoms and durations absent from the baseline condition. These are standard probability results applied to the measurement question, not claims of mathematical or biological novelty.

An arbitrary exact two-bin example illustrates why the sharper constraint matters. Its coarse feasible interval is [0, 0.9], but its baseline-constrained interval is [0.15, 0.775]. A hypothetical positive fraction of 0.85 passes the first and fails the second. [Exact-fraction arithmetic](recruitment_duration_arithmetic.json) checks the allocations; no study data or numerical solver was used.

The result is a population compatibility bound, not an automatic significance test. Raw empirical total variation may be one simply because continuous sample values differ. Coarse duration bins require a stronger, common within-bin positivity assumption. Uncertainty must reflect independent sampling units, selection and censoring. Total observed duration can itself be affected by recruitment, so conditioning on it does not isolate a causal exposure clock or prove force generation.

The [Myo1E table contract](MYO1E_REPOSITORY_FINDINGS.md) does not establish the needed eligible positive/negative cohort, denominator or grouping. No biological inequality was evaluated. This analytic branch stops at one useful prospective design. The [manifest](recruitment_duration_manifest.json) preserves the proof, review and arithmetic.

## Next direction

Repeated extensions of this bound cannot repair missing observations. A separate bounded primary-source screen will examine yeast endocytosis for a public joint protein-recruitment and inward-motion/event dataset with an explicit perturbation and grouping contract. This expands the organism scope within the user's broad clathrin question; yeast and mammalian mechanical assumptions must remain distinct. No previously closed dataset is reopened, and no new paper's measurements will be treated as force without calibration.
