# Geometry transfer implementation

`geometry_transfer.py` is the registered executable for
`geometry-transfer-001`.  It imports the existing verified reader, selector and
geometry basis from `compare_geometry.py`; it does not change old code, inputs,
or results.

`--checks` reserves a distinct synthetic-check invocation and performs four
NNLS calls: exact recovery for the three frozen basis forms and the expected
constant-area zero-coefficient boundary rejection.  This remains below the
six-call synthetic cap.  It also performs no-NNLS arithmetic checks for two
unequally grouped training lines and a held-out-group leak.  `--run` requires a
completed synthetic-check invocation, then reserves the sole empirical-grid invocation
before output creation, then makes exactly one NNLS fit for every fixed
policy/held-out-line/model combination (3 x 3 x 3 = 27).  Any existing
empirical invocation in the ledger refuses a rerun, including after failure.

Before every NNLS call, the script appends a reserved call to the mutable
execution ledger and checks its cumulative per-kind cap.  It records source
hashes per invocation.  Immutable check and empirical result filenames are
opened only with `x`; while an invocation is running, a caught exception records
its error in the ledger and writes the partial failed output before propagating
the failure.

For each line holdout, rows are weighted so each training line has total
squared weight `1/L_train`, each group within that line has
`1/(L_train*G_line)`, and each row in that group has
`1/(L_train*G_line*n_group)`.  The output retains all coefficients, training
and target group IDs, per-target-group MAE, equal-target-group MAE, equal-held-
out-line grand means, and train/target angular support including target rows
outside the train range.  A held-out line/group leak, rank failure, or nonfinite
or nonpositive constant-area result stops rather than retunes the grid.

This is a descriptive transfer calculation.  It does not provide calibrated
uncertainty, mechanism inference, or a biological replication.
