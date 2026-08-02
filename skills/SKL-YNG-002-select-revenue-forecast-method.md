---
id: SKL-YNG-002
title: Select a Revenue Forecast Method
type: skill
status: draft
version: 0.1.0
domain: lifecycle
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-YNG-001, YNG-002]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Young-company profile, Market evidence, Capacity and unit evidence]
outputs: [Forecast method decision, Required input checklist]
---

# Select a Revenue Forecast Method
## Purpose
Choose top-down, bottom-up, or reviewed hybrid forecasting before valuation.
## Preconditions
Classification and M2 narrative gates pass.
## Input schema
Market definition and share evidence; capacity, utilization, pricing, cost, and fixed-cost evidence.
## Procedure
Score evidence completeness; choose the method with the more observable causal chain; use hybrid only with an explicit reconciliation.
## Decision rules
Top-down requires market/share paths; bottom-up requires capacity and unit economics.
## Output schema
Method, rationale, required inputs, gaps, reviewer.
## Controls
Prevent method selection based on desired value.
## Failure modes
Undefined market, unconstrained capacity, or silent method blending.
## Source evidence
Implements `CLM-YNG-011` through `CLM-YNG-015`, pages 275–292.
## Tests or test expectations
Test method selection and missing-input stop conditions.
