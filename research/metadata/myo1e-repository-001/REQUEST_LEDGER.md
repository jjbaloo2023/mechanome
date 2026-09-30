# Request ledger — myo1e-repository-contract-001

Caps: 5 requests, 1,048,576 body bytes, and 3 source/table blobs. Body bytes
are retained response-body bytes; each response has its headers saved alongside.

| # | UTC response date | Request | Status | Bytes | SHA-256 | Kind | Cumulative |
| --- | --- | --- | ---: | ---: | --- | --- | ---: |
| 01 | 2026-09-29T12:38:11Z | `GET /repos/DrubinBarnes/Smith_et_al_Myosin1E_Manuscript/commits?per_page=1` | 200 | 5,181 | `ef9239922cb870d56b5674594bb88d703a53c6b32fa85a6e7b6a46695e7e1e65` | metadata | 5,181 |
| 02 | 2026-09-29T12:38:48Z | `GET /repos/DrubinBarnes/Smith_et_al_Myosin1E_Manuscript/git/trees/2c7f823b1cad4d458fd383877b7ed841e220e655?recursive=1` | 200 | 4,996 | `cf4aa39f14a26288789d5e73533db4ca22df9f086dda22087a42e09d2daec57b` | metadata; `truncated=false`, 14 entries | 10,177 |
| 03 | 2026-09-29T12:39:11Z | `GET /repos/DrubinBarnes/Smith_et_al_Myosin1E_Manuscript/git/blobs/51fecfa7b3460ce6be63167389d41170733bf363` | 200 | 226,600 | `c5278b8e41ade42ed46a75ae9c1728ccd9a9ecbef50d2fd671bea5347e74e347` | table blob 1/3: `three_color_tracking_myosin1e_osmotic_shock.csv` | 236,777 |

`01-commit.json` pins the current default-branch response at
`aa43f751b03378783b3226a719b64773bff8e91a`, tree
`2c7f823b1cad4d458fd383877b7ed841e220e655`, committer date 2025-11-12. That
is a repository revision identity, not proof of the paper-version revision.

The retained table's Git blob identity comes from the untruncated pinned tree:
`51fecfa7b3460ce6be63167389d41170733bf363`. Three requests and one table blob
are retained; 236,777 bytes is below the cap. No failed request occurred.
