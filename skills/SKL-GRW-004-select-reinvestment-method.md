---
id: SKL-GRW-004
title: Select Reinvestment Method by Segment
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-GRW-003, GRW-004]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Revenue changes, Operating income, Capital history, Capacity evidence]
outputs: [One reinvestment method per period, Method inputs, Review findings]
---

# Select Reinvestment Method by Segment

## Procedure

Choose revenue-change/sales-to-capital, fundamental return/reinvestment, or a bounded capacity holiday. Record one applicable input per period and the rationale for every transition.

## Controls

Reject overlapping methods, nonpositive sales-to-capital, unsupported fundamental returns, or a holiday without capacity, utilization, maximum output, and resumption year.

## Source evidence

Implements `CLM-GRW-010`, `CLM-GRW-011`, and `CLM-GRW-020` through `CLM-GRW-022`.
