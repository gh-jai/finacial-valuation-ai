---
id: SKL-DST-005
title: Build Closure and Going-concern Value
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-DST-002, SKL-DST-004, DST-008, WFL-VAL-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Status-quo FCFF, Conditional WACC, One closure mode]
outputs: [Closure value, Cumulative discount factors, Going-concern operating value]
---

# Build Closure and Going-concern Value

Select finite life, stabilized smaller company, or negative perpetuity. Rebuild any terminal FCFF and delegate cumulative discounting to M1. Reject overlapping terminal and full-liquidation values.
