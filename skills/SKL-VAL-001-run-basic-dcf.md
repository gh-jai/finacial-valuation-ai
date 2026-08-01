---
id: SKL-VAL-001
title: Run a Basic Discounted Cash Flow Valuation
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: []
dependencies:
  - VAL-001
owner: fvi-maintainers
last_updated: "2026-08-01"
---

# Run a Basic Discounted Cash Flow Valuation

## Purpose

Produce a transparent enterprise-value DCF from synthetic or authorized inputs while preserving assumptions and review evidence.

## Preconditions

The valuation date, currency, cash-flow definition, forecast periods, discount-rate basis, and terminal-value convention are explicit and internally consistent.

## Inputs

- Forecast free cash flow by period
- Period timing or discount exponents
- Discount rate
- Terminal growth rate or exit assumption
- Non-operating assets, debt-like claims, and share count when an equity bridge is required

## Procedure

1. Validate units, dates, signs, and cash-flow/discount-rate consistency.
2. Discount forecast cash flows to the valuation date.
3. Calculate terminal value only when its assumptions are economically coherent.
4. Sum present values to enterprise value.
5. Reconcile to equity or per-share value if requested.
6. Run material sensitivities and record limitations.

## Outputs

Return a document conforming to `schemas/valuation-output.schema.json`, plus a calculation trail suitable for independent review.

## Controls and failure modes

Stop for terminal growth at or above the discount rate under a perpetuity-growth method, mixed nominal and real inputs, inconsistent currencies, missing valuation timing, or an unexplained enterprise-to-equity bridge. Flag sensitivity concentration and unsupported precision.

## Tests

Use only synthetic fixtures in the public suite. Verify arithmetic identities, boundary rejection, unit consistency, and complete assumption/evidence fields.
