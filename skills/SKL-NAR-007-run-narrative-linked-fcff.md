---
id: SKL-NAR-007
title: Run Narrative-linked FCFF Valuation
type: skill
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-NARRATIVE-NUMBERS-2017, SRC-DAMODARAN-LBV-2024]
dependencies: [SKL-NAR-006, WFL-VAL-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Separate narrative FCFF contracts]
outputs: [Separate M1 valuation results, Conditional value comparison]
---

# Run Narrative-linked FCFF Valuation

## Purpose
Compose narrative input sets with `WFL-VAL-001` and preserve conditional values separately.

## Preconditions
Each narrative has passed mapping and separation controls.

## Input schema
One M1 FCFF input contract per narrative ID.

## Procedure
Call `tools.dcf.run_fcff_dcf` for each isolated contract; retain calculation trails and traceability; compare values only after valuation.

## Decision rules
Do not apply failure probability unless an approved method exists. Preserve it as a mapped but unapplied input and emit an explicit model limitation stating that it does not alter M1 value.

## Output schema
Narrative ID keyed valuation results, input traces, and model limitations.

## Controls
M1 human gates remain authoritative for DCF mechanics.

## Failure modes
Duplicated formulas, cross-contaminated inputs, unsupported probability adjustment, undisclosed unapplied risk, or lost narrative IDs.

## Source evidence
Implements `CLM-NAR-019` through `CLM-NAR-021` and composes with the M1 FCFF claims.

## Tests or test expectations
Verify separate valuations, deterministic results, explicit `WFL-VAL-001` composition, and mapped-but-unapplied failure-risk disclosure.
