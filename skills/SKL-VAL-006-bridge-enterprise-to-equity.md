---
id: SKL-VAL-006
title: Bridge Operating Asset Value to Equity
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-005
  - SKL-VAL-005
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs:
  - Operating asset value
  - Cash and non-operating assets
  - Debt and debt-like claims
outputs:
  - Common equity value
  - Enterprise-to-equity reconciliation
---

# Bridge Operating Asset Value to Equity

## Purpose

Convert FCFF-derived operating asset value to common-equity value without double counting operating or financing items.

## Preconditions

`SKL-VAL-005` has produced reviewed operating asset value, and all bridge items share the valuation date, currency, and unit.

## Input schema

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `operating_asset_value` | number | yes | Finite FCFF-derived operating value |
| `cash_and_non_operating_assets` | number | yes | Finite; excluded from operating FCFF |
| `debt_and_debt_like_claims` | number | yes | Finite; economically measured at the valuation date |

## Procedure

1. Start with operating asset value.
2. Add eligible cash and non-operating assets excluded from FCFF.
3. Subtract debt and debt-like or other non-equity claims.
4. Reconcile each bridge line to evidence and record potential double counting.

## Decision rules

- Add cash only if its income was not capitalized in operating FCFF.
- Include debt-like claims consistently; do not subtract debt twice.
- Keep cross-holdings, minority interests, leases, pensions, and options explicit when material; unsupported items must be escalated rather than guessed.

## Output schema

| Field | Type | Meaning |
|---|---|---|
| `equity_value` | number | Operating value plus non-operating assets less non-equity claims |
| `bridge_reconciliation` | array[object] | Named additions, deductions, evidence, and review status |

## Controls

Require a line-by-line human review of bridge classification, measurement date, units, and double-counting risk.

## Failure modes

Non-finite values, mixed dates or currencies, debt deducted twice, omitted debt-like claims, or cash added after its income was already valued.

## Source evidence

Implements `CLM-VAL-DCF-001` and `CLM-VAL-DCF-010` from `SRC-DAMODARAN-LBV-2024`, Chapter 3, PDF pages 50–52 and 79–81.

## Tests or test expectations

Test cash additions, debt deductions, simultaneous bridge items, negative equity outcomes, and non-finite inputs. `tools.dcf.bridge_enterprise_to_equity` is the executable reference.
