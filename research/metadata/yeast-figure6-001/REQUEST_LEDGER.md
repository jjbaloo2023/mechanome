# Request ledger — yeast-figure6-contract-001

Only the two named publisher CSVs are downloaded. Parsed-web accesses are
logged separately because they expose no raw-body byte telemetry.

| # | UTC response date | URL | Status | Bytes | SHA-256 | File | Cumulative |
| --- | --- | --- | ---: | ---: | --- | --- | ---: |
| 01 | 2026-09-29T13:32:52Z | `https://cdn.elifesciences.org/articles/44215/elife-44215-fig6-data1-v1.csv` | 200 | 39,769 | `bc92afb9ede060f63b794823f79ec153840ea4204fc394614ffbc174f70866fa` | Figure 6B average trajectories | 39,769 |
| 02 | 2026-09-29T13:33:16Z | `https://cdn.elifesciences.org/articles/44215/elife-44215-fig6-data2-v1.csv` | 200 | 210 | `bf468206a22020e839eae9ce6bc9a2a179fa1c3dab5f35b287d0bda9c4ba38d0` | Figure 6A median Act1 molecules | 39,979 |

Both direct publisher responses declared `Content-Type: text/csv`. No failed
requests occurred. Downloaded body total is 39,979 of 1,048,576 bytes.

Parsed-primary access ledger: the lead used the reserved one query at
2026-09-29T13:32:46Z for `site:elifesciences.org/articles/44215 "Figure 6"
"trajectories" "median"`; the indexed publisher PDF/figure caption verified
Figure 6 context. No raw PDF body was downloaded. The source used no search
query initially. The source then used its one permitted query for
`site:elifesciences.org/articles/44215 "Sla1" "95% confidence" trajectory
alignment`; indexed primary methods say inward-movement plot shading is a 95%
CI computed from trajectory/alignment error terms. No raw PDF body was
downloaded. Reviewer used zero; the team used its allocated two queries.
