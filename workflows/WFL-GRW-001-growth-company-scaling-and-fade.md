---
id: WFL-GRW-001
title: Growth-company Scaling and Fade Valuation
type: workflow
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018, SRC-DAMODARAN-NARRATIVE-NUMBERS-2017, SRC-DAMODARAN-LBV-2024]
dependencies: [WFL-NAR-001, WFL-VAL-001, WFL-YNG-001, GRW-001, GRW-002, GRW-003, GRW-004, GRW-005, GRW-006, GRW-007]
owner: fvi-maintainers
last_updated: "2026-08-02"
skill_refs: [SKL-GRW-001, SKL-GRW-002, SKL-GRW-003, SKL-GRW-004, SKL-GRW-005, SKL-GRW-006, SKL-GRW-007, SKL-GRW-008, SKL-GRW-009]
review_gates:
  - M2 narrative approval
  - M3 boundary clearance
  - Current-base normalization
  - Revenue scale and market constraint
  - Margin target and convergence
  - Reinvestment method and implied return
  - Operating-risk fade
  - Stable-state consistency
  - Failure and equity handoff separation
  - Sensitivity price independence and final approval
---

# Growth-company Scaling and Fade Valuation

## Objective

Convert one approved narrative for an established growth company into an internally consistent FCFF fade, delegate discounting to M1, optionally apply M3 failure semantics once, and preserve an explicit equity bridge and feedback loop.

## Execution order

1. Receive one approved `WFL-NAR-001` narrative and driver map.
2. `SKL-GRW-001`: clear the M3 boundary and normalize the base period.
3. `SKL-GRW-002`: build revenue, absolute scale, and market-share checks.
4. `SKL-GRW-003`: converge margins and roll forward taxes and NOL.
5. `SKL-GRW-004`: select one reinvestment method for each segment.
6. `SKL-GRW-005`: roll invested capital, implied ROC, and FCFF.
7. `SKL-GRW-006`: build period-specific costs of capital.
8. `SKL-GRW-007`: rebuild stable FCFF and delegate cumulative DCF arithmetic to `WFL-VAL-001`.
9. `SKL-GRW-008`: apply material failure risk once and select an explicit equity bridge.
10. `SKL-GRW-009`: run separate deterministic sensitivity and price break-even review.
11. Return value-driver findings to the M2 feedback revision loop.

## Stop conditions

Stop for an uncleared life-cycle boundary, stale unexplained base, unbounded scale, unsupported growth plateau, margin jump, growth without reinvestment, overlapping methods, capacity breach, implausible implied return, constant unsupported risk, terminal inconsistency, failure or dilution double counting, market-price anchoring, merged alternatives, or private source content.

## Outputs

One schema-valid `GCV-*` object per narrative, including all recomputed operating series, stable-state rebuild, M1 calculation trail, optional M3 failure handoff, bridge inputs, sensitivity separation, limitations, provenance, and human review.

## Source evidence

Operationalizes all 30 `CLM-GRW-*` claims from Chapter 10, printed pages 323–357. Relative valuation and the other contract exclusions remain outside this workflow.
