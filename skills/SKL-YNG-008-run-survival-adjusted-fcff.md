---
id: SKL-YNG-008
title: Run Survival-adjusted FCFF Valuation
type: skill
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018, SRC-DAMODARAN-LBV-2024]
dependencies: [SKL-YNG-007, WFL-VAL-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Forecast drivers, Discount-rate path, Failure scenario]
outputs: [Going-concern result, Survival adjustment, Calculation trail]
---

# Run Survival-adjusted FCFF Valuation
## Purpose
Delegate going-concern mechanics to M1 and apply the discrete failure expected value once.
## Preconditions
Forecast, terminal, rate, probability, and basis gates pass.
## Input schema
M1 FCFF drivers plus reconciled operating-assets failure scenario.
## Procedure
Call `forecast_fcff` and `run_fcff_dcf`; calculate survival and failure components; record delta and trail.
## Decision rules
Never duplicate M1 formulas or apply failure losses twice; key-person risk uses another M1 scenario.
## Output schema
`going_concern` and `survival_adjustment` objects.
## Controls
Arithmetic, basis, terminal, and risk-separation checks.
## Failure modes
Probability mismatch, basis mismatch, duplicated risk, or arbitrary key-person haircut.
## Source evidence
Implements `CLM-YNG-021` through `CLM-YNG-026`, pages 302–311.
## Tests or test expectations
Test negative FCFF, cumulative factors, survival arithmetic, recovery, and key-person isolation.
