---
id: SKL-YNG-004
title: Build a Bottom-up Forecast
type: skill
status: draft
version: 0.1.0
domain: lifecycle
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-YNG-002, YNG-002]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Capacity, Utilization, Unit price and cost, Fixed cost, Capacity investment]
outputs: [Revenue and operating-income paths, Required capacity investment]
---

# Build a Bottom-up Forecast
## Purpose
Derive revenue, operating income, and capacity investment from operating units.
## Preconditions
Bottom-up method approved and units are consistent.
## Input schema
Equal-length capacity, utilization, price, unit cost, fixed cost, and investment-rate inputs.
## Procedure
Calculate units, revenue, contribution, fixed-cost deduction, and incremental capacity investment.
## Decision rules
Utilization is bounded; capacity and costs are nonnegative.
## Output schema
Revenue, operating income, and capacity-investment series.
## Controls
Reconcile demand to available capacity.
## Failure modes
Over-100% utilization, unit mismatch, or free capacity growth.
## Source evidence
Implements `CLM-YNG-015`, pages 286–292.
## Tests or test expectations
Test capacity constraints, unit economics, and investment calculations.
