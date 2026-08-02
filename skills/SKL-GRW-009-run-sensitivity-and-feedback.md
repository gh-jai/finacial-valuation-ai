---
id: SKL-GRW-009
title: Run Growth Sensitivity and Narrative Feedback
type: skill
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018, SRC-DAMODARAN-NARRATIVE-NUMBERS-2017]
dependencies: [SKL-GRW-008, GRW-007, WFL-NAR-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Approved base case, Separate scenarios, Two-driver grid, Optional market price]
outputs: [Sensitivity results, Break-even findings, Narrative revision inputs]
---

# Run Growth Sensitivity and Narrative Feedback

## Procedure

Keep materially different fade paths as separate valuation objects, run deterministic two-driver points and break-even comparisons, and return value-driver findings to the M2 feedback loop.

## Controls

Never average alternatives, calibrate the approved base to market price, or turn a price comparison into an investment recommendation.

## Source evidence

Implements `CLM-GRW-015` and `CLM-GRW-017`; preserves M2 feedback semantics.
