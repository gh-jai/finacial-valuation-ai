# M4 growth-company scaling-and-fade implementation review

Reviewer: FVI maintainer
Review date: 2026-08-02
Valuation IDs/versions: `GCV-SYNTH-ASSET-LIGHT/0.1.0`, `GCV-SYNTH-CAPACITY/0.1.0`

## Source fidelity and scope

- [x] All 30 claims are original paraphrases with exact Chapter 10 locations.
- [x] The source boundary is printed pages 323-357 and PDF pages 371-405.
- [x] Relative valuation, Monte Carlo, real options, voting premiums, and convertible decomposition have not entered the M4 engine.
- [x] No PDF, raw extract, copied table, figure, long quotation, or sequential source text is committed.

## Classification and composition

- [x] Each synthetic subject clears the M3 young-company boundary with evidence.
- [x] M2 narrative assertions map both ways to all material M4 inputs.
- [x] DCF arithmetic delegates to `WFL-VAL-001`.
- [x] The capacity benchmark uses M3 failure semantics once without rerunning the M3 forecast.
- [x] The M1 or M3 equity-bridge path is selected explicitly.

## Scale, margin, and reinvestment

- [x] Base-period values are current or reconciled to the valuation date.
- [x] Revenue growth and duration are supported by absolute scale, market, competition, and company evidence.
- [x] Target margin and convergence timing are explicit.
- [x] Exactly one primary reinvestment method applies to each forecast segment.
- [x] The capacity holiday has support and a defined end.
- [x] Invested capital and implied ROC are independently recomputed and economically plausible for the synthetic cases.

## Risk and terminal state

- [x] Period discount rates match the growth, margin, financing, and tax narratives.
- [x] No unsupported short regression history is used.
- [x] Stable growth is below terminal cost of capital and within the M1 ceiling.
- [x] Stable ROC, reinvestment, margin, risk, and leverage describe one mature company in each case.
- [x] Terminal FCFF is rebuilt from stable-state drivers.
- [x] Cumulative discounting and terminal present value are independently recomputed.
- [x] Failure risk and future financing are not double counted.

## Sensitivity and decision integrity

- [x] Alternative narratives and fade paths remain separate valuation objects.
- [x] Sensitivity and break-even analysis do not overwrite the approved base case.
- [x] The observed synthetic market price is a comparison, not a calibration target.
- [x] Limitations and terminal-value concentration are disclosed.

Decision: `[x] approve  [ ] request changes  [ ] reject`

Findings: The implementation satisfies the approved M4 contract locally. The remaining release gate is the remote Python 3.10/3.12 CI matrix on the implementation pull request.

## Final PR review hardening

- [x] Every source and narrative assertion reference is registered, and assumption assertions match the top-level narrative assertion set in both directions.
- [x] Addressable-market growth and capacity-utilization series are independently recomputed.
- [x] Every stored calculation-trail step is compared with the engine-generated trail.
- [x] Terminal-growth / terminal-cost sensitivity points and supported market-comparison break-even values are independently recomputed.
- [x] Adversarial mutations for each control are rejected.

Final release evidence: PR #10 Python 3.10/3.12 validation and the full repository test suite must pass on the hardened head before merge.
