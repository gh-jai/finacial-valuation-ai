---
id: WFL-CYC-001
title: Cycle-aware Judgment Layer
type: workflow
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018, SRC-MARKS-MASTERING-MARKET-CYCLE-2018]
dependencies: [WFL-NAR-001, WFL-VAL-001, WFL-YNG-001, WFL-GRW-001, WFL-DST-001, CYC-001, CYC-002, CYC-003, CYC-004, CYC-005, CYC-006, CYC-007, CYC-008]
owner: fvi-maintainers
last_updated: "2026-08-08"
skill_refs: [SKL-CYC-001, SKL-CYC-002, SKL-CYC-003, SKL-CYC-004, SKL-CYC-005, SKL-CYC-006, SKL-CYC-007, SKL-CYC-008, SKL-CYC-009, SKL-CYC-010]
review_gates:
  - Company-specific exposure and life-cycle boundaries
  - Dated reconciled operating and financing base
  - Five-dimension evidence completeness and staleness
  - Recurrence structural-break and present-position evidence
  - Exactly one valuation treatment
  - Complete normalization or one transition path
  - Dated driver mapping scenario isolation and probability basis
  - Intrinsic-value and optional M5 handoff separation
  - Recomputed overlay confidence and bounded posture
  - Independent validation limitations and narrative feedback
---

# Cycle-aware Judgment Layer

## Objective

Prevent peak or trough observations from becoming permanent inputs, select one governed cycle treatment, and record a separate dated market judgment for human review.

## Execution order

1. `SKL-CYC-001` classifies company-specific exposure and clears M3-M5 boundaries.
2. `SKL-CYC-002` reconciles the dated continuing-operation base.
3. `SKL-CYC-003` builds the five-dimension evidence and staleness ledger.
4. `SKL-CYC-004` assesses recurrence, breaks, company position, and counterevidence.
5. `SKL-CYC-005` selects exactly one treatment.
6. `SKL-CYC-006` performs complete normalization or one current-to-normal transition.
7. `SKL-CYC-007` handles dated current expectations and isolated deterministic scenarios.
8. `SKL-CYC-008` hands inputs to M1, uses bounded M4 controls, and routes issuer distress once to M5.
9. `SKL-CYC-009` observes price after value and creates the separate bounded overlay.
10. `SKL-CYC-010` independently validates the document and returns findings to M2.

## Stop conditions

Stop for an uncleared boundary, unsupported exposure, nonrepresentative history, selective normalization, overlapping payloads, recovery double counting, an invalid old normal, future-dated evidence, incomplete mapping, shared scenario state, invented probabilities, stale or one-dimensional extremes, a hidden composite score, psychology-to-DCF contamination, market-price contamination, duplicated distress, excluded methods, timing claims, trade instructions, or private-source content.

## Outputs

One schema-valid `CYJ-*` object with a distinct valuation-input handoff and judgment overlay. No hidden composite score may combine treatment selection, intrinsic valuation, and posture assignment.

## Source evidence

Valuation treatment implements Chapter 13 of the approved Damodaran source. The non-numeric evidence and review posture implement the approved selected chapters of the Marks source. Neither source authorizes live ingestion, statistical cycle prediction, or portfolio instructions.
