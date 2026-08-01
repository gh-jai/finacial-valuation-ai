---
id: SKL-VAL-003
title: Estimate Sustainable Operating Growth
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-003
  - VAL-004
  - SKL-VAL-002
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs:
  - Stable-state reinvestment rate
  - Stable-state return on capital
  - Long-run growth ceiling evidence
outputs:
  - Sustainable operating growth estimate
  - Stable-state coherence findings
---

# Estimate Sustainable Operating Growth

## Purpose

Link stable operating growth to the reinvestment needed to produce it and the return expected on that investment.

## Preconditions

The explicit forecast from `SKL-VAL-002` identifies a plausible transition to stable margins, risk, and capital efficiency.

## Input schema

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `reinvestment_rate` | number | yes | Finite; definition and denominator documented |
| `return_on_capital` | number | yes | Finite; stable-state basis documented |
| `growth_ceiling` | number | yes | Externally reviewed long-run ceiling, not embedded source text |

## Procedure

1. Confirm stable-state definitions for after-tax operating income and invested capital.
2. Calculate sustainable growth as reinvestment rate multiplied by return on capital.
3. Compare the result with the reviewed long-run growth ceiling.
4. Reconcile growth, reinvestment, risk, and excess-return duration.

## Decision rules

- Do not treat growth as an independent terminal input.
- Reject growth above the approved long-run ceiling.
- Flag stable returns on capital materially above cost of capital unless competitive evidence supports them.
- Keep the estimate distinct from the Gordon-growth denominator check performed by `SKL-VAL-004`.

## Output schema

| Field | Type | Meaning |
|---|---|---|
| `sustainable_growth_rate` | number | Reinvestment rate multiplied by return on capital |
| `coherence_findings` | array[string] | Growth, reinvestment, and return review findings |

## Controls

Human review must approve the stable-state reinvestment definition, return on capital, growth ceiling, and transition from the explicit forecast.

## Failure modes

Non-finite inputs, unsupported permanent excess returns, growth above the approved ceiling, or growth assumed without corresponding reinvestment.

## Source evidence

Implements `CLM-VAL-DCF-005`, `CLM-VAL-DCF-007`, and `CLM-VAL-DCF-008` from `SRC-DAMODARAN-LBV-2024`, Chapter 3, PDF pages 69–76.

## Tests or test expectations

Test the growth identity, zero and negative returns, non-finite inputs, and human-review flags for ceiling breaches. `tools.dcf.estimate_sustainable_growth` is the executable arithmetic reference.
