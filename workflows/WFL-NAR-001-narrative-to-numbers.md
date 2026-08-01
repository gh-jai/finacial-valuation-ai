---
id: WFL-NAR-001
title: Narrative to Numbers
type: workflow
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-NARRATIVE-NUMBERS-2017, SRC-DAMODARAN-LBV-2024]
dependencies: [NAR-001, NAR-002, NAR-003, NAR-004, NAR-005, NAR-006, WFL-VAL-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
skill_refs: [SKL-NAR-001, SKL-NAR-002, SKL-NAR-003, SKL-NAR-004, SKL-NAR-005, SKL-NAR-006, SKL-NAR-007, SKL-NAR-008]
review_gates:
  - Business and market definition
  - Evidence sufficiency
  - 3P judgment
  - Story and input consistency
  - Alternative-story separation
  - Valuation mapping
  - Revision classification
  - Final approval
---

# Narrative to Numbers

## Objective

Convert an evidence-backed business narrative into separate, traceable FCFF input sets and conditional valuations, then preserve feedback-driven revisions without duplicating the M1 valuation workflow.

## Entry criteria

The subject, date, purpose, evidence authority, source boundary, reviewer, and M1 FCFF applicability are explicit. Private sources remain outside version control.

## Execution order

1. `SKL-NAR-001`: gather supporting and contradicting evidence.
2. `SKL-NAR-002`: define the business, market, and competition.
3. `SKL-NAR-003`: construct atomic, parsimonious assertions.
4. `SKL-NAR-004`: apply possible, plausible, and probable review.
5. `SKL-NAR-005`: map assertions to value drivers and emit an FCFF input set.
6. `SKL-NAR-006`: generate each credible alternative as a separate narrative and input set.
7. `SKL-NAR-007`: pass every isolated set into `WFL-VAL-001`; receive separate structured valuation outputs.
8. `SKL-NAR-008`: classify feedback, append revision history, rerun affected inputs, and record value delta.

## Human review gates

| Gate | Required evidence | Stop condition |
|---|---|---|
| Business and market definition | Products, customers, geography, life cycle, market, competition | Material boundary is ambiguous |
| Evidence sufficiency | Supporting and contradicting evidence register | Material assertion lacks evidence |
| 3P judgment | Three assessments with reasoning | Unsupported label or failed possibility |
| Story and input consistency | Two-way assertion/input trace | Orphan input or assertion |
| Alternative-story separation | Distinct IDs, objects, assessments, and mappings | Alternatives are merged or averaged |
| Valuation mapping | Complete M1 FCFF contracts | Material driver is missing |
| Revision classification | Trigger, prior version, classification, deltas | History is erased or chain is broken |
| Final approval | Narrative artifacts, separate values, limitations | Human reviewer rejects or findings remain |

## Outputs

- Schema-valid current and alternative narrative JSON documents.
- Separate traceable FCFF input contracts.
- Separate `WFL-VAL-001` results and calculation trails.
- Feedback revision history, changed assumptions, and value delta.
- Structured valuation memo sections identifying each value as conditional on its narrative.

## Failure and escalation

Stop on missing authority, inadequate evidence, failed possibility, unmapped material assertions, unknown references, merged alternatives, incomplete M1 inputs, broken revision history, or copyrighted source content.

## Source evidence

Operationalizes the 24 reviewed M2 claims from Chapters 6–10, printed pages 70–166. The break/change/shift terminology continues on pages 167–183 and remains explicitly scoped. DCF mechanics are delegated to `WFL-VAL-001`.
