---
id: SKL-VAL-008
title: Run Basic DCF Sensitivity Review
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-004
  - VAL-005
  - SKL-VAL-004
  - SKL-VAL-005
  - SKL-VAL-006
  - SKL-VAL-007
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs:
  - Validated base DCF
  - Terminal discount-rate scenarios
  - Terminal growth-rate scenarios
  - Material assumption ranges
outputs:
  - Deterministic sensitivity grid
  - Sensitivity concentration findings
  - Human review recommendation
---

# Run Basic DCF Sensitivity Review

## Purpose

Expose value concentration and boundary risk by rerunning the accepted DCF over controlled terminal-rate and growth scenarios.

## Preconditions

Skills `SKL-VAL-004` through `SKL-VAL-007` have produced a complete base valuation and all scenario inputs use the same FCFF, timing, currency, and units.

## Input schema

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `cash_flows` | array[number] | yes | Validated explicit FCFF |
| `discount_rate` | number or array[number] | yes | Validated forecast rate contract |
| `terminal_discount_rates` | array[number] | yes | At least one finite stable-state rate |
| `terminal_growth_rates` | array[number] | yes | At least one finite rate; each below its paired terminal rate |

## Procedure

1. Define a small, documented scenario grid around material assumptions.
2. Recalculate operating asset value for each valid terminal-rate/growth pair.
3. Record point estimates deterministically without overwriting the base case.
4. Report terminal value as a share of operating asset value and identify concentrated outcomes.
5. Escalate boundary proximity, unstable rankings, or unsupported precision for human approval.

## Decision rules

- Reject every scenario with terminal growth at or above its terminal discount rate.
- Do not interpret the grid as a probability distribution.
- Expand review beyond terminal assumptions when forecast drivers or the equity bridge are more material.
- Never select a base case merely because it is the midpoint of the grid.

## Output schema

| Field | Type | Meaning |
|---|---|---|
| `sensitivity` | array[object] | Scenario label, terminal rate, growth rate, and point estimate |
| `concentration_findings` | array[string] | Material value drivers and boundary risks |
| `review_status` | string | Unreviewed, reviewed, approved, or rejected |

## Controls

Require final human approval of scenario plausibility, terminal-value concentration, unresolved limitations, and communication of uncertainty.

## Failure modes

Invalid rate pairs, inconsistent scenario bases, treating sensitivity as probability, hiding concentrated terminal value, or approving without human review.

## Source evidence

Applies `CLM-VAL-DCF-007`, `CLM-VAL-DCF-008`, `CLM-VAL-DCF-009`, and `CLM-VAL-DCF-012` from `SRC-DAMODARAN-LBV-2024`, Chapter 3, PDF pages 74–79.

## Tests or test expectations

Test grid cardinality, deterministic ordering, point estimates, invalid terminal boundaries, and structured-output compatibility. `tools.dcf.run_dcf_sensitivity` is the executable reference.
