---
id: SKL-NAR-005
title: Map Narrative Assertions to Value Drivers
type: skill
status: draft
version: 0.1.0
domain: narrative
source_refs: [SRC-DAMODARAN-NARRATIVE-NUMBERS-2017]
dependencies: [SKL-NAR-004, NAR-003, NAR-004]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [3P-reviewed narrative, Forecast horizon and units]
outputs: [Traceable value-driver mappings, Explicit FCFF input contract]
---

# Map Narrative Assertions to Value Drivers

## Purpose
Translate the reviewed story into revenue, margin, reinvestment, risk, and terminal assumptions.

## Preconditions
The narrative passes possibility and has a recorded 3P judgment.

## Input schema
Assertions plus revenues, margins, taxes, reinvestments, discount rate, failure probability, terminal growth, and optional bridge inputs.

## Procedure
Map each material assertion; attach assertion and evidence IDs; generate FCFF through `tools.dcf.forecast_fcff`; emit the M1 DCF contract.

## Decision rules
Require all material mappings; retain failure risk even though M1 does not probability-adjust it; never duplicate DCF formulas.

## Output schema
One isolated FCFF contract with `cash_flows`, rates, terminal growth, bridge inputs, failure probability, and traceability.

## Controls
Two-way story/input review and unit/timing checks.

## Failure modes
Orphan assumptions, duplicate input names, missing material driver, or input without narrative rationale.

## Source evidence
Implements `CLM-NAR-012` through `CLM-NAR-018`, Chapter 8, printed pages 110–127.

## Tests or test expectations
Test deterministic mapping, missing mappings, assertion references, and composition with `tools.dcf`.
