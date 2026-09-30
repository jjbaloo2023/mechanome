# Myo1E public data: found, with unresolved grouping and measurement definitions

Accepted after [independent review](MYO1E_REPOSITORY_REVIEW.md), 29 September 2026. The [pinned repository](https://github.com/DrubinBarnes/Smith_et_al_Myosin1E_Manuscript/tree/aa43f751b03378783b3226a719b64773bff8e91a) contains a real 226,600-byte track table, `three_color_tracking_myosin1e_osmotic_shock.csv`. It has 1,709 rows and 17 columns. This resolves the earlier browser-cache availability gap; it does not yet support a Figure 4 reproduction.

The [source inventory](MYO1E_REPOSITORY_SOURCE.md) and [request ledger](metadata/myo1e-repository-001/REQUEST_LEDGER.md) record three successful requests and 236,777 response-body bytes. The untruncated tree has 14 entries. The saved revision is not proven to be the article-analysis revision. No author code ran.

## What prevents an interpretable comparison

| Issue | Verified evidence | Consequence |
| --- | --- | --- |
| Group identifiers | Condition 1 has both `1-1` and `1-Jan` through `6-Jan`; other groups also have date-like labels | Possible spreadsheet coercion, not a proven repair. Do not merge labels or count raw strings as independent movies |
| Conditions and replication | Numeric condition and replicate codes lack a verified codebook in the retained table | No inferred osmolarity labels, biological replicates or baseline/post pairs |
| Measurement and denominator | Channel assignments, positivity criteria and Figure 4C denominator are unverified | Cannot substitute positive/all for positive/negative, or estimate recruitment from a possibly selected cohort |
| Event selection | Track categories and lifetime patterns are present, but their definitions are not established | Do not equate a 301 value with an uncensored physical lifetime or a completed internalization |

Lead and reviewer independently parsed the CSV. No cells are blank and no complete rows are exact duplicates; these checks do not establish grouping integrity. The [primary-source assessment](MYO1E_FINDINGS.md) also identifies possible baseline/post acquisition pairing and a ratio-versus-percentage wording distinction. These are specific constraints on our reanalysis, not findings that the published biology is wrong.

## Decision and next question

Stop acquisition for this candidate under the registered gate. The larger notebook and corresponding two-color table were not fetched, and no automatic retrieval follows. An authoritative codebook and original group identifiers would be a new evidential input; no user action is required now. Preserve the unmodified CSV locally, with hashes and metadata in the [manifest](myo1e_repository_manifest.json).

The next distinct question is analytic: could a change in the distribution of observed event durations change marginal recruitment even if recruitment probability conditional on duration were unchanged? A bounded derivation can define a falsifiable observable null and its minimum data requirements without pretending the current table satisfies them. This is queued in [NEXT_CYCLE.md](NEXT_CYCLE.md), not a result or an empirical fit. It avoids another access loop and stays separate from force recovery.
