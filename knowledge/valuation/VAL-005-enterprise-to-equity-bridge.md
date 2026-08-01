---
id: VAL-005
title: Enterprise-to-Equity and Per-Share Bridge
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
summary: Convert operating-asset value to equity and per-share value through an explicit, non-duplicative bridge.
claim_refs:
  - CLM-VAL-DCF-009
  - CLM-VAL-DCF-010
  - CLM-VAL-DCF-011
---

# Enterprise-to-Equity and Per-Share Bridge

## Core principle

Discounted FCFF produces the value of operating assets. It does not directly produce common-equity value. A transparent bridge adjusts for claims and assets that are outside the operating FCFF forecast.

```text
Value of operating assets
+ Cash and eligible non-operating assets
+ Value of relevant non-operating holdings
− Debt
− Debt-like obligations and other non-equity claims
= Equity value

Equity value
− Value attributable to outstanding equity options or senior equity claims, when applicable
÷ Appropriate share count
= Value per common share
```

## Decision rules

1. Discount explicit FCFF and terminal value to obtain operating-asset value before applying bridge items.
2. Add cash only when its income and cash flows are not already included in FCFF.
3. Subtract debt and other claims at economically appropriate values and the same valuation date.
4. Avoid double counting cross-holdings, minority interests, leases, pensions, or options.
5. Divide by share count only after completing the equity bridge.
6. State whether the share count is basic, diluted, or otherwise adjusted and why.

## Failure modes

- Calling operating-asset value equity value
- Subtracting debt twice
- Adding cash whose interest income was already capitalized
- Ignoring debt-like claims
- Using an unexplained diluted share count instead of valuing material options
- Mixing balance-sheet dates with the valuation date

## Evidence

Derived from `CLM-VAL-DCF-009` through `CLM-VAL-DCF-011`, sourced to Chapter 3, PDF pages 77–81 of `SRC-DAMODARAN-LBV-2024`.
