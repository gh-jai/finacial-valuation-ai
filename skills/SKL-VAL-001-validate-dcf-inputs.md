---
id: SKL-VAL-001
title: Validate Basic FCFF DCF Inputs
type: skill
status: draft
version: 0.2.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-002
  - VAL-004
  - VAL-005
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs:
  - DCF scope and valuation metadata
  - Explicit FCFF sequence
  - Forecast and terminal discount rates
  - Terminal growth rate
  - Optional bridge and share-count inputs
outputs:
  - Normalized validated DCF inputs
  - Validation findings and stop conditions
---

# Validate Basic FCFF DCF Inputs

## Purpose

Establish a finite, internally consistent, and reviewable input contract before any DCF arithmetic is performed.

## Preconditions

The valuation date, subject, currency, FCFF definition, period timing, and units are explicit. Inputs are synthetic or lawfully authorized and contain no private source text.

## Input schema

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `cash_flows` | array[number] | yes | At least one finite end-of-period FCFF |
| `discount_rate` | number or array[number] | yes | Finite; each rate greater than -100%; array length equals FCFF count |
| `terminal_growth_rate` | number | yes | Finite and below terminal discount rate |
| `terminal_discount_rate` | number | no | Defaults to the last forecast rate; finite and greater than -100% |
| `cash_and_non_operating_assets` | number | no | Finite; default zero |
| `debt_and_debt_like_claims` | number | no | Finite; default zero |
| `share_count` | number | no | Finite and positive when supplied |

## Procedure

1. Confirm the model is an FCFF enterprise-valuation model.
2. Normalize numeric values and expand a constant forecast discount rate by period.
3. Verify period counts, finite numbers, rate boundaries, and terminal-growth ordering.
4. Confirm FCFF and cost-of-capital consistency, currency, timing, and units.
5. Record validation findings and stop on any hard failure.

## Decision rules

- Accept constant or period-specific forecast discount rates.
- Use the final forecast rate as the terminal discount rate only when no separate stable-state rate is supplied.
- Reject terminal growth at or above the terminal discount rate.
- Treat bridge inputs as outside operating FCFF; do not embed financing cash flows in FCFF.

## Output schema

| Field | Type | Meaning |
|---|---|---|
| `cash_flows` | tuple[number] | Normalized explicit FCFF |
| `discount_rates` | tuple[number] | One forecast rate per period |
| `terminal_discount_rate` | number | Stable-state discount rate |
| `terminal_growth_rate` | number | Validated stable-growth rate |
| `findings` | array[string] | Review findings; empty on acceptance |

## Controls

Require a human consistency check for FCFF versus cost of capital, nominal versus real inputs, valuation date, currency, and period timing.

## Failure modes

Empty cash flows, non-finite numbers, mismatched rate counts, rates at or below -100%, incoherent terminal growth, non-positive share count, or mixed cash-flow and discount-rate definitions.

## Source evidence

Implements `CLM-VAL-DCF-002`, `CLM-VAL-DCF-003`, `CLM-VAL-DCF-009`, and `CLM-VAL-DCF-012` from `SRC-DAMODARAN-LBV-2024`, Chapter 3, PDF pages 60–79.

## Tests or test expectations

Test constant and varying rates, empty FCFF, non-finite inputs, rate-count mismatch, terminal-growth equality and excess, and invalid share counts. `tools.dcf.validate_dcf_inputs` is the executable reference.
