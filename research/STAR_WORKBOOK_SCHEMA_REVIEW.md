# Independent review: Nawara STAR Source Data workbook schema

## Registered question

The separate `star-workbook-schema-001` registration asks only whether the listed publisher XLSX contains reusable paired CLCa intensity and clathrin axial-proxy time series with event IDs, time fields and biological grouping. The axial proxy is conditional; workbook schema cannot independently validate membrane shape. One publisher HTML request and one capped XLSX request are allowed, with no retry or fallback. The first access, size or format failure stops the task.

## Review criteria

For any event-level reuse, verify actual sheet/header/row structure and exact same-event key, time units/cadence, normalization and optical-value meaning, cell and experimental-repeat IDs, selection/censoring, and mapping to the paper's reported cohorts. Summary curves, figure statistics or columns without a reliable joint key do not satisfy the event-level contract. Public access and file bytes/hash are provenance, not proof of biological independence or shape validation. No fit or inference follows automatically even if event rows exist.

## Result

The sole scripted attempt started at 17:39:55 UTC. Its first, registered publisher HTML request failed before an HTTP response with local `URLError: [WinError 10013]` (socket access forbidden by this environment). The result ledger retains that one request as reserved and records `stopped_at_first_failure`; no workbook request, bytes, URL, sheet, field or event row was obtained. The one-request stop honors the registration. This is an **environment access failure**, not evidence that the publisher file is unavailable or that an event-level dataset does not exist. The workbook schema question remains unanswered, and there is no basis for empirical reuse or a numerical biological contrast.

The script records the request before opening the socket, enforces the byte/elapsed caps and refuses a repeated invocation or alternate link if it cannot identify exactly one Source Data XLSX. No source data, raw movie, fit or tracking call was run. The saved ledger is the evidence for the stopped attempt; no retry or escalation is justified within this task.

One possible next task is a *separately registered, finite model-conditional observation calculation* for the two TIRF channels. It could assess algebraic identifiability and error correlation between coat abundance and an axial coordinate derived from the same two measured intensities, including poor conditioning when penetration depths approach equality. That would clarify the proxy's independence limits without any author data or network call. It would not repair the workbook access gap, demonstrate an observed coat/shape lag, validate membrane shape, or test a biological mechanism. A repeat access rescue or a fit based on the inaccessible workbook is not warranted here.
