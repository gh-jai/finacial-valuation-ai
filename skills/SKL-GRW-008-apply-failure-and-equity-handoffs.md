---
id: SKL-GRW-008
title: Apply Failure and Equity Handoffs
type: skill
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-GRW-007, GRW-007, WFL-YNG-001, WFL-VAL-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Going-concern value, Failure scenario, Current cash and debt, Bridge path]
outputs: [Applicable operating value, Equity-bridge handoff, Double-counting findings]
---

# Apply Failure and Equity Handoffs

## Procedure

If discrete failure is material, apply M3 expected-value semantics once to M4 operating value. Select either the standard M1 bridge or M3 claim controls and pass current cash, debt, and provenance.

## Controls

Reject failure in rates or FCFF as well as the handoff, hypothetical future debt, future financing shares in today's denominator, or an implicit claim structure.

## Source evidence

Implements `CLM-GRW-016`, `CLM-GRW-027`, `CLM-GRW-028`, `CLM-GRW-029`, and `CLM-GRW-030`.
