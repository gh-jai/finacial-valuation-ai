---
id: SKL-VAL-007
title: Calculate Per-Share Value
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-005
  - SKL-VAL-006
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs:
  - Common equity value
  - Reviewed share count
outputs:
  - Value per common share
  - Share-count basis disclosure
---

# Calculate Per-Share Value

## Purpose

Convert reviewed common-equity value to per-share value using an explicit and appropriate share-count basis.

## Preconditions

`SKL-VAL-006` has completed the equity bridge, and the share count is measured on a documented basic, diluted, or otherwise adjusted basis.

## Input schema

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `equity_value` | number | yes | Finite common-equity value |
| `share_count` | number | yes | Finite and strictly positive |
| `share_count_basis` | string | yes | Basic, diluted, or documented adjusted basis |

## Procedure

1. Confirm the numerator represents common equity after all senior claims.
2. Review the share-count date, dilution basis, and unit scale.
3. Divide equity value by share count.
4. Record the share-count basis and unresolved option or dilution limitations.

## Decision rules

- Divide only after completing the equity bridge.
- Reject zero or negative share counts.
- Do not use an unexplained diluted count as a substitute for valuing material options or senior equity claims.

## Output schema

| Field | Type | Meaning |
|---|---|---|
| `per_share_value` | number | Common-equity value divided by share count |
| `share_count_basis` | string | Disclosed denominator convention |

## Controls

Independently reconcile share count to authorized evidence and confirm that value and shares use compatible unit scales.

## Failure modes

Non-finite equity, non-positive shares, stale or unexplained share count, mixed units, or division before senior claims are removed.

## Source evidence

Implements `CLM-VAL-DCF-011` from `SRC-DAMODARAN-LBV-2024`, Chapter 3, PDF pages 80–81.

## Tests or test expectations

Test positive per-share arithmetic, zero and negative share rejection, non-finite inputs, and unit-scale reconciliation. `tools.dcf.calculate_per_share_value` is the executable reference.
