---
id: WFL-VAL-001
title: M1 Basic FCFF Company Valuation
type: workflow
status: draft
version: 0.2.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-002
  - VAL-003
  - VAL-004
  - VAL-005
  - SKL-VAL-001
  - SKL-VAL-002
  - SKL-VAL-003
  - SKL-VAL-004
  - SKL-VAL-005
  - SKL-VAL-006
  - SKL-VAL-007
  - SKL-VAL-008
owner: fvi-maintainers
last_updated: "2026-08-02"
skill_refs:
  - SKL-VAL-001
  - SKL-VAL-002
  - SKL-VAL-003
  - SKL-VAL-004
  - SKL-VAL-005
  - SKL-VAL-006
  - SKL-VAL-007
  - SKL-VAL-008
review_gates:
  - Cash-flow and discount-rate consistency
  - Forecast driver and reinvestment coherence
  - Terminal-value assumptions
  - Enterprise-to-equity bridge
  - Per-share calculation
  - Sensitivity concentration
  - Final human approval
---

# M1 Basic FCFF Company Valuation

## Objective

Produce a traceable basic FCFF DCF, enterprise-to-equity bridge, per-share estimate, sensitivity review, and schema-valid structured valuation memo from synthetic or authorized inputs.

## Scope

This workflow covers only basic intrinsic enterprise valuation using explicit FCFF and a Gordon-growth terminal value. It excludes FCFE, dividend discount, relative valuation, banks, commodity companies, distressed companies, live data ingestion, and autonomous investment recommendations.

## Entry criteria

- Valuation subject, date, currency, unit, and purpose are explicit.
- Input data is synthetic or lawfully authorized and remains outside version control when private.
- The analysis uses only the 12 reviewed M1 claims; no additional source claim is invented.
- A human reviewer is identified for the final approval gate.

## Execution order

1. **`SKL-VAL-001` — Validate Basic FCFF DCF Inputs.** Normalize the input contract and stop on finite-number, timing, unit, or terminal-boundary failures.
2. **`SKL-VAL-002` — Forecast FCFF.** Translate revenue, operating margin, tax, and reinvestment drivers into explicit FCFF.
3. **`SKL-VAL-003` — Estimate Sustainable Growth.** Reconcile stable growth to reinvestment, return on capital, and a reviewed long-run ceiling.
4. **`SKL-VAL-004` — Calculate Terminal Value.** Apply the Gordon-growth formula using next-period FCFF and a separate stable-state discount rate.
5. **`SKL-VAL-005` — Discount Forecast Cash Flows.** Apply cumulative constant or period-specific discount factors and calculate operating asset value.
6. **`SKL-VAL-006` — Bridge Enterprise Value to Equity.** Add eligible cash and non-operating assets and subtract debt and debt-like claims.
7. **`SKL-VAL-007` — Calculate Per-Share Value.** Divide reviewed common-equity value by an explicit positive share count when per-share output is requested.
8. **`SKL-VAL-008` — Run DCF Sensitivity Review.** Run deterministic terminal-rate/growth scenarios and identify value concentration and boundary risk.

## Human review gates

| Gate | Required evidence | Stop condition |
|---|---|---|
| Cash-flow and discount-rate consistency | FCFF definition, cost-of-capital basis, currency, nominal/real convention | FCFF is not matched to cost of capital |
| Forecast driver and reinvestment coherence | Revenue, margins, taxes, reinvestment, return on capital | Growth lacks operating or reinvestment support |
| Terminal-value assumptions | Stable growth, return, reinvestment, terminal discount rate, transition | Growth is at/above discount rate or stable state is unsupported |
| Enterprise-to-equity bridge | Cash, non-operating assets, debt, debt-like claims, valuation date | Material bridge item is missing, stale, or double counted |
| Per-share calculation | Equity numerator, share-count basis and units | Share count is non-positive or unexplained |
| Sensitivity concentration | Scenario grid and terminal-value share | Result is dominated by unsupported terminal assumptions |
| Final human approval | Structured memo, evidence, assumptions, limitations, review record | Reviewer rejects or material findings remain unresolved |

## Structured outputs

1. A calculation result with explicit FCFF, discount rates, cumulative discount factors, terminal value, operating asset value, bridge values, and deterministic calculation trail.
2. A valuation object conforming to `schemas/valuation-output.schema.json` containing value basis, assumptions, evidence references, limitations, sensitivity, and review status.
3. A structured valuation memo based on `templates/valuation-memo.md`, with the schema-valid valuation object as its numerical contract.
4. A completed human review checklist based on `templates/model-review.md`.

## Exit criteria

- All eight skills complete in order without an unresolved stop condition.
- The valuation output validates against JSON Schema.
- Benchmark and boundary tests pass.
- Evidence uses registered source and claim IDs with no copyrighted extract.
- Final review status is recorded; only an authorized human can mark the result approved.

## Failure and escalation paths

Stop and escalate non-finite inputs, missing authority, inconsistent FCFF/rates, unsupported reinvestment or stable growth, terminal growth at or above the terminal rate, incomplete bridge items, invalid share count, concentrated sensitivity, or any attempt to commit private source material.

## Source evidence

The workflow operationalizes `CLM-VAL-DCF-001` through `CLM-VAL-DCF-012` from `SRC-DAMODARAN-LBV-2024`, Chapter 3, PDF pages 50–81, through knowledge artifacts `VAL-002` through `VAL-005`.
