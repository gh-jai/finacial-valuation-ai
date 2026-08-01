---
id: VAL-004
title: Terminal Value and Stable-Growth Discipline
type: knowledge
status: draft
version: 0.1.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-002
  - VAL-003
owner: fvi-maintainers
last_updated: "2026-08-01"
summary: Terminal value requires economically coherent stable-growth, risk, and reinvestment assumptions.
claim_refs:
  - CLM-VAL-DCF-007
  - CLM-VAL-DCF-008
  - CLM-VAL-DCF-012
---

# Terminal Value and Stable-Growth Discipline

## Core principle

Terminal value closes the explicit forecast by valuing either liquidation proceeds or a continuing business. A going-concern FCFF model uses the next period's stable cash flow and terminal cost of capital:

```text
Terminal value = FCFF(n+1) / (Terminal cost of capital − Stable growth)
```

The formula is only the final arithmetic step. The economic assumptions behind stable growth, risk, reinvestment, and excess returns determine whether the result is credible.

## Stable-growth constraints

1. Stable growth should not exceed the long-run growth capacity of the relevant economy; the source gives the risk-free rate as a practical ceiling.
2. Terminal risk and capital structure should move toward mature-company characteristics.
3. The company must reinvest enough to support stable growth.
4. For FCFF, the stable reinvestment rate is linked to stable growth and return on capital.
5. The terminal growth rate must be lower than the terminal cost of capital.

## Excess-return interpretation

Higher terminal growth does not automatically create value because supporting that growth consumes cash through reinvestment. Value increases from additional stable growth only when the assumed return on capital exceeds the cost of capital. If the two are equal, higher growth is offset by higher reinvestment.

## Review controls

- Report terminal value as a share of total operating value.
- Test lower and higher growth, discount-rate, and return-on-capital assumptions.
- Explain the transition from explicit forecast assumptions to stable state.
- Reject non-positive Gordon-growth denominators.
- Do not use an exit multiple as a hidden replacement for stable-state economics in this M1 workflow.

## Evidence

Derived from `CLM-VAL-DCF-007`, `CLM-VAL-DCF-008`, and `CLM-VAL-DCF-012`, sourced to Chapter 3, PDF pages 74–76 of `SRC-DAMODARAN-LBV-2024`.
