---
id: SKL-YNG-005
title: Forecast Margin Taxes and Reinvestment
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-YNG-003, SKL-YNG-004, YNG-003]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Revenue path, Current and target margins, NOL, Tax rate, Sales-to-capital ratio, Reinvestment lag]
outputs: [Margin tax NOL and reinvestment paths, FCFF drivers]
---

# Forecast Margin, Taxes, and Reinvestment
## Purpose
Build internally consistent operating drivers from losses to maturity.
## Preconditions
One approved revenue path exists.
## Input schema
Current/target margins, mature year, NOL, marginal tax rate, sales-to-capital, lag, and initial revenue.
## Procedure
Create margin convergence; apply NOL shelter; calculate growth investment with lag; check implied return on capital.
## Decision rules
No immediate unexplained margin jump; taxes start only after NOL use; growth requires reinvestment.
## Output schema
Equal-length margins, tax rates, NOL balances, reinvestments, and traces.
## Controls
Human target-margin and reinvestment review.
## Failure modes
Premature taxes, unsupported growth, or omitted capacity investment.
## Source evidence
Implements `CLM-YNG-016` through `CLM-YNG-019`, pages 283–298.
## Tests or test expectations
Test convergence, NOL exhaustion, reinvestment lag, and growth support.
