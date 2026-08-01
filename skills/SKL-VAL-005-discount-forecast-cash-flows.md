---
id: SKL-VAL-005
title: Discount Forecast FCFF and Terminal Value
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-002
  - VAL-005
  - SKL-VAL-001
  - SKL-VAL-004
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs:
  - Explicit FCFF sequence
  - Forecast discount rate by period
  - Terminal value
outputs:
  - Cumulative discount factors
  - Discounted FCFF sequence
  - Operating asset value
---

# Discount Forecast FCFF and Terminal Value

## Purpose

Convert explicit FCFF and terminal value to the valuation date using cumulative cost-of-capital discount factors.

## Preconditions

`SKL-VAL-001` has validated the FCFF/rate match and `SKL-VAL-004` has produced an accepted terminal value.

## Input schema

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `cash_flows` | array[number] | yes | At least one finite FCFF |
| `discount_rates` | number or array[number] | yes | Constant or one finite rate per period; each greater than -100% |
| `terminal_value` | number | yes | Finite value at the end of the explicit forecast |

## Procedure

1. Build a cumulative present-value factor for each forecast period.
2. Multiply each FCFF by its corresponding cumulative factor.
3. Discount terminal value with the final cumulative forecast factor.
4. Sum forecast present value and terminal present value to operating asset value.
5. Preserve every period in a deterministic calculation trail.

## Decision rules

- Apply varying rates cumulatively; never discount each period using only that period's standalone rate.
- Use end-of-period timing throughout this M1 workflow.
- Keep operating asset value separate from the later equity bridge.

## Output schema

| Field | Type | Meaning |
|---|---|---|
| `cumulative_discount_factors` | tuple[number] | Present-value multiplier by period |
| `discounted_cash_flows` | tuple[number] | Present value of each explicit FCFF |
| `forecast_present_value` | number | Sum of discounted explicit FCFF |
| `terminal_present_value` | number | Discounted terminal value |
| `operating_asset_value` | number | Forecast PV plus terminal PV |

## Controls

Recompute at least one period independently, reconcile the sum, and review terminal value as a percentage of operating asset value.

## Failure modes

Rate-count mismatch, non-finite factors or results, rates at or below -100%, inconsistent timing, or terminal value discounted to the wrong date.

## Source evidence

Implements `CLM-VAL-DCF-003` and `CLM-VAL-DCF-009` from `SRC-DAMODARAN-LBV-2024`, Chapter 3, PDF pages 63–79.

## Tests or test expectations

Test constant and varying rates, cumulative factors, explicit FCFF present value, terminal present value, empty cash flows, and overflow/non-finite rejection. `tools.dcf.discount_fcff` and `run_fcff_dcf` are executable references.
