---
id: SKL-VAL-004
title: Calculate Gordon-Growth Terminal Value
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-004
  - SKL-VAL-003
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs:
  - Final explicit-period FCFF
  - Stable terminal growth rate
  - Stable terminal discount rate
outputs:
  - Next-period terminal FCFF
  - Gordon-growth terminal value
---

# Calculate Gordon-Growth Terminal Value

## Purpose

Calculate a going-concern terminal value only after stable growth, risk, and reinvestment assumptions have been reviewed.

## Preconditions

`SKL-VAL-003` has established a coherent stable-growth assumption and the model has an explicit final-period FCFF.

## Input schema

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `final_fcff` | number | yes | Finite final explicit-period FCFF |
| `terminal_growth_rate` | number | yes | Finite and below terminal discount rate |
| `terminal_discount_rate` | number | yes | Finite and greater than -100% |

## Procedure

1. Calculate next-period FCFF as final FCFF multiplied by one plus stable growth.
2. Verify the Gordon-growth denominator is strictly positive.
3. Divide next-period FCFF by terminal discount rate minus terminal growth.
4. Record stable-state assumptions and the undiscounted terminal value.

## Decision rules

- Use next-period rather than final-period FCFF in the numerator.
- Reject terminal growth equal to or greater than the terminal discount rate.
- Do not replace stable-state economics with an exit multiple in this M1 workflow.
- Escalate a negative terminal value for economic review even when arithmetic is finite.

## Output schema

| Field | Type | Meaning |
|---|---|---|
| `terminal_cash_flow` | number | FCFF for the first stable-growth period |
| `terminal_value` | number | Value at the end of the explicit forecast |

## Controls

Review the transition to mature-company risk, capital structure, reinvestment, return on capital, and the share of total operating value attributable to the terminal period.

## Failure modes

Non-finite inputs, a non-positive denominator, inconsistent terminal risk, unsupported growth, or accidental use of final-period rather than next-period FCFF.

## Source evidence

Implements `CLM-VAL-DCF-007`, `CLM-VAL-DCF-008`, and derived rule `CLM-VAL-DCF-012` from `SRC-DAMODARAN-LBV-2024`, Chapter 3, PDF pages 74–76.

## Tests or test expectations

Test terminal arithmetic, separate terminal discount rates, equality and excess growth boundaries, and non-finite inputs. `tools.dcf.calculate_terminal_value` is the executable reference.
