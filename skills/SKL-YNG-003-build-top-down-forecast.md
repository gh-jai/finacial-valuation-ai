---
id: SKL-YNG-003
title: Build a Top-down Forecast
type: skill
status: draft
version: 0.1.0
domain: lifecycle
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-YNG-002, YNG-002]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Total market path, Market-share path, Narrative traces]
outputs: [Derived revenue path, Forecast trace]
---

# Build a Top-down Forecast
## Purpose
Derive revenue from explicit market and share paths.
## Preconditions
Top-down method approved with matching periods and units.
## Input schema
Nonnegative total markets, bounded shares, assertion IDs, evidence, and rationale.
## Procedure
Multiply each period's market by share; reconcile implied scale and capacity; retain traces.
## Decision rules
Reject negative markets, shares outside zero-to-one, or mismatched periods.
## Output schema
Market, share, revenue series, and traceability.
## Controls
Human market-definition and share-plausibility review.
## Failure modes
Circular market sizing or share disconnected from competition.
## Source evidence
Implements `CLM-YNG-014`, pages 279–286.
## Tests or test expectations
Test deterministic revenues and invalid market/share inputs.
