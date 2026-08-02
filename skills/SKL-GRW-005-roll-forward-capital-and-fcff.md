---
id: SKL-GRW-005
title: Roll Forward Capital and FCFF
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018, SRC-DAMODARAN-LBV-2024]
dependencies: [SKL-GRW-004, GRW-004, WFL-VAL-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [After-tax operating income, Reinvestment, Opening invested capital]
outputs: [Invested capital, Implied return on capital, FCFF]
---

# Roll Forward Capital and FCFF

## Procedure

Add reinvestment to opening capital, calculate each period's implied return from after-tax operating income and opening capital, and emit FCFF as after-tax operating income less reinvestment.

## Controls

Recompute every series independently; stop for growth without support, nonfinite outputs, or implausible implied returns requiring narrative revision.

## Source evidence

Implements `CLM-GRW-010`, `CLM-GRW-021`, and `CLM-GRW-023` while delegating FCFF arithmetic to M1 semantics.
