---
id: VAL-003
title: Growth, Reinvestment, and Return on Capital
type: knowledge
status: draft
version: 0.1.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-002
owner: fvi-maintainers
last_updated: "2026-08-01"
summary: Sustainable operating growth requires both reinvestment and returns on the capital reinvested.
claim_refs:
  - CLM-VAL-DCF-005
  - CLM-VAL-DCF-006
---

# Growth, Reinvestment, and Return on Capital

## Core principle

Growth is not a free input. For operating income with stable margins, expected growth is linked to the reinvestment rate and return on invested capital:

```text
Expected operating-income growth = Reinvestment rate × Return on capital
```

When margins are changing, forecast revenue and margins explicitly and tie reinvestment to incremental revenue through a sales-to-capital ratio.

## FCFF construction

A basic operating forecast links:

```text
Revenue
× Operating margin
= EBIT
× (1 − Tax rate)
= After-tax operating income
− Reinvestment
= FCFF
```

Reinvestment may include net capital expenditures and changes in noncash working capital. In a driver-based model, it can also be inferred from revenue growth and capital efficiency.

## Decision rules

1. Do not forecast long-term growth without specifying the reinvestment required to support it.
2. Use reinvestment rate × return on capital only when the operating-margin assumption is sufficiently stable.
3. When margins change materially, forecast revenue, margins, and reinvestment separately.
4. Use sales-to-capital as a capital-efficiency driver only when its definition and industry comparability are documented.
5. Flag growth created only by margin recovery separately from growth created by new investment.

## Failure modes

- Treating growth as independent of capital needs
- Forecasting high growth with negligible reinvestment
- Using historical growth mechanically despite structural change
- Confusing revenue growth, operating-income growth, and FCFF growth
- Assuming permanent excess returns without competitive evidence

## Evidence

Derived from `CLM-VAL-DCF-005` and `CLM-VAL-DCF-006`, sourced to Chapter 3, PDF pages 69–73 of `SRC-DAMODARAN-LBV-2024`.
