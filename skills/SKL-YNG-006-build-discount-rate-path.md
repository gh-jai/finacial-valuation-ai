---
id: SKL-YNG-006
title: Build a Time-varying Discount-rate Path
type: skill
status: draft
version: 0.1.0
domain: risk
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-YNG-005, YNG-004]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Initial cost of capital, Mature cost of capital, Forecast periods, Operating-risk rationale]
outputs: [Period-specific rates, Cumulative discount factors]
---

# Build a Time-varying Discount-rate Path
## Purpose
Converge operating risk toward maturity without embedding discrete failure risk.
## Preconditions
Operating and failure risks are separately identified.
## Input schema
Finite initial/mature rates, period count, evidence, and explicit no-survival-premium flag.
## Procedure
Interpolate period rates and derive cumulative factors through M1 discounting.
## Decision rules
Failure probability never creates an unsupported rate premium.
## Output schema
Rate path, cumulative factors, terminal rate, and risk-treatment record.
## Controls
Risk-separation review.
## Failure modes
Flat unexplained risk, noncumulative discounting, or duplicated survival risk.
## Source evidence
Implements `CLM-YNG-020`, `CLM-YNG-021`, and `CLM-YNG-023`, pages 298–308.
## Tests or test expectations
Test convergence, cumulative factors, and double-counting rejection.
