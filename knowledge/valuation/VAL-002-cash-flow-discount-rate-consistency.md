---
id: VAL-002
title: Cash-Flow and Discount-Rate Consistency
type: knowledge
status: draft
version: 0.1.0
domain: valuation
source_refs:
  - SRC-DAMODARAN-LBV-2024
dependencies:
  - VAL-001
owner: fvi-maintainers
last_updated: "2026-08-01"
summary: Match the claimholder definition of cash flow to the discount rate used to value it.
claim_refs:
  - CLM-VAL-DCF-001
  - CLM-VAL-DCF-002
  - CLM-VAL-DCF-003
  - CLM-VAL-DCF-004
---

# Cash-Flow and Discount-Rate Consistency

## Core principle

A DCF must value the same claim in both numerator and denominator. Free cash flow to the firm is an unlevered operating cash flow available to debt and equity capital providers, so it is discounted at the cost of capital. Equity cash flows are discounted at the cost of equity.

## FCFF perspective

The FCFF route first values operating assets. Its cash flow starts from after-tax operating income and subtracts reinvestment required for future operations. Financing cash flows, interest expense, debt issuance, and debt repayment do not belong in FCFF.

The cost of capital combines the cost of equity and after-tax cost of debt using capital-structure weights. All components must use a consistent currency, inflation convention, risk-free rate basis, and valuation date.

## Decision rules

1. Use FCFF with cost of capital when valuing the operating business before debt claims.
2. Use FCFE or dividends with cost of equity when valuing equity directly.
3. Reject a model that discounts FCFF at the cost of equity or equity cash flow at the cost of capital.
4. Separate operating value from the later enterprise-to-equity bridge.
5. State whether rates and cash flows are nominal or real and keep them consistent.

## Failure modes

- Mixing levered and unlevered cash flows
- Deducting interest expense inside FCFF
- Using book capital weights without justification
- Combining cash flows and discount rates from different currencies
- Treating the discount rate as an arbitrary conservatism adjustment

## Evidence

Derived from `CLM-VAL-DCF-001` through `CLM-VAL-DCF-004`, sourced to Chapter 3, PDF pages 50–68 of `SRC-DAMODARAN-LBV-2024`.
