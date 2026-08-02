---
id: WFL-DST-001
title: Decline Distress and Contingent-survival Valuation
type: workflow
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018, SRC-DAMODARAN-NARRATIVE-NUMBERS-2017, SRC-DAMODARAN-LBV-2024]
dependencies: [WFL-NAR-001, WFL-VAL-001, WFL-YNG-001, WFL-GRW-001, DST-001, DST-002, DST-003, DST-004, DST-005, DST-006, DST-007, DST-008]
owner: fvi-maintainers
last_updated: "2026-08-02"
skill_refs: [SKL-DST-001, SKL-DST-002, SKL-DST-003, SKL-DST-004, SKL-DST-005, SKL-DST-006, SKL-DST-007, SKL-DST-008, SKL-DST-009, SKL-DST-010]
review_gates:
  - Approved narrative and life-cycle boundary
  - Normalized current base and claim inventory
  - Independent reversibility and distress classification
  - Status-quo decline and negative reinvestment support
  - Divestiture and retained-operations reconciliation
  - Financing tax-benefit and conditional WACC path
  - Closure and going-concern value
  - Turnaround or orderly-liquidation alternative
  - Distress event recovery basis and one contingent adjustment
  - Claim bridge traceability limitations and final approval
---

# Decline Distress and Contingent-survival Valuation

## Objective

Convert one approved declining-company narrative into a status-quo FCFF value, select only the quadrant-required operating alternative, apply material forced-sale risk once, and bridge one declared value basis through current claims.

## Execution order

1. Receive one approved `WFL-NAR-001` narrative and driver map.
2. `SKL-DST-001`: clear M3, M4, ordinary mature, and cycle-driven boundaries; normalize the base.
3. Classify reversibility and distress independently and select one quadrant.
4. `SKL-DST-002`: build the status-quo decline forecast.
5. `SKL-DST-003`: reconcile capital release, divestitures, and retained operations.
6. `SKL-DST-004`: rebuild face debt, tax benefits, market weights, and conditional WACC.
7. `SKL-DST-005`: select one closure and delegate cumulative FCFF discounting to `WFL-VAL-001`.
8. `SKL-DST-006` only for reversible decline: value and weight a separate turnaround alternative.
9. `SKL-DST-007` only for irreversible low distress: value orderly liquidation and select the higher alternative.
10. `SKL-DST-008` only for high distress: value one governed forced-sale recovery.
11. `SKL-DST-009`: apply M3-compatible contingent survival once and one dated claim bridge.
12. `SKL-DST-010`: complete human review and return findings to the M2 feedback loop.

## Stop conditions

Stop for an uncleared boundary, stale base or claims, merged alternatives, unsupported negative reinvestment, retained disposed earnings, duplicated proceeds, book-value recovery proxy, loss tax shield, altered financing series, overlapping liquidation and terminal value, event or horizon mismatch, mixed bases, repeated claim deduction, distress-risk double counting, excluded methods, or private source content.

## Outputs

One schema-valid `DDV-*` object per narrative with full operating, financing, closure, alternative, contingent-survival, claim, provenance, limitation, and review trails.

## Source evidence

Operationalizes all 32 reviewed `CLM-DST-*` claims from Chapter 12, printed pages 397-436. Chapter 11 and Chapter 13 methods remain outside this workflow.
