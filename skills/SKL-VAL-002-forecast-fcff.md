---
id: SKL-VAL-002
title: Forecast Free Cash Flow to the Firm
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-002
  - VAL-003
  - SKL-VAL-001
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs:
  - Revenue forecast by period
  - Operating margin by period
  - Operating tax rate by period
  - Reinvestment by period
outputs:
  - Explicit FCFF sequence
  - Forecast-driver review findings
---

# Forecast Free Cash Flow to the Firm

## Purpose

Translate explicit operating drivers into an unlevered FCFF sequence without introducing financing cash flows.

## Preconditions

`SKL-VAL-001` has accepted the valuation scope, units, currency, timing, and FCFF definition. Forecast drivers share the same period convention.

## Input schema

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `revenues` | array[number] | yes | Finite, non-negative, one value per period |
| `operating_margins` | array[number] | yes | Finite, one value per period |
| `tax_rates` | array[number] | yes | Finite values from 0 through 1 |
| `reinvestments` | array[number] | yes | Finite, one value per period |

## Procedure

1. Calculate EBIT as revenue multiplied by operating margin.
2. Calculate after-tax operating income using the operating tax rate.
3. Subtract reinvestment for each period to obtain FCFF.
4. Reconcile growth, margins, taxes, and reinvestment to the stated business narrative.
5. Return the FCFF sequence and surface unsupported driver transitions for review.

## Decision rules

- Exclude interest, debt issuance, and debt repayment from FCFF.
- Keep revenue, margins, taxes, and reinvestment period-aligned.
- Separate margin recovery from investment-supported operating growth.
- Allow negative FCFF when explicit reinvestment economics support it; do not silently floor values at zero.

## Output schema

| Field | Type | Meaning |
|---|---|---|
| `cash_flows` | tuple[number] | FCFF by forecast period |
| `driver_reconciliation` | array[string] | Material driver assumptions and review findings |

## Controls

Review revenue growth, margin transitions, operating tax rates, reinvestment, capital efficiency, and the absence of financing flows.

## Failure modes

Unequal driver lengths, non-finite values, negative revenue, invalid tax rates, mixed units, or growth unsupported by reinvestment.

## Source evidence

Implements `CLM-VAL-DCF-002`, `CLM-VAL-DCF-005`, and `CLM-VAL-DCF-006` from `SRC-DAMODARAN-LBV-2024`, Chapter 3, PDF pages 60–73.

## Tests or test expectations

Test driver arithmetic, mismatched periods, invalid tax rates, non-finite inputs, and negative FCFF. `tools.dcf.forecast_fcff` is the executable reference.
