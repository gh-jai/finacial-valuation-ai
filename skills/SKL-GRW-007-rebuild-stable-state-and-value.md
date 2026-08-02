---
id: SKL-GRW-007
title: Rebuild Stable State and Value Operating Assets
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018, SRC-DAMODARAN-LBV-2024]
dependencies: [SKL-GRW-005, SKL-GRW-006, GRW-006, WFL-VAL-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Explicit FCFF, Period rates, Stable growth return margin tax and risk]
outputs: [Rebuilt terminal FCFF, Terminal value, Operating asset value, Calculation trail]
---

# Rebuild Stable State and Value Operating Assets

## Procedure

Calculate stable reinvestment as growth divided by return; rebuild next-period terminal revenue, after-tax operating income, reinvestment, and FCFF; then use M1 cumulative discounting and Gordon arithmetic.

## Controls

Reject growth at or above cost of capital, inconsistent stable drivers, a horizon over ten years without a contract amendment, or terminal FCFF grown mechanically from the last high-growth FCFF.

## Source evidence

Implements `CLM-GRW-007`, `CLM-GRW-012`, `CLM-GRW-023`, `CLM-GRW-025`, and `CLM-GRW-026`.
