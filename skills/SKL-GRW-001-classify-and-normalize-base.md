---
id: SKL-GRW-001
title: Classify Growth Company and Normalize Base
type: skill
status: draft
version: 0.1.0
domain: lifecycle
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [WFL-NAR-001, WFL-YNG-001, GRW-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Approved narrative, Commercial evidence, Current financials, Valuation date]
outputs: [M4 routing decision, Normalized base period, Evidence trace]
---

# Classify Growth Company and Normalize Base

## Purpose

Confirm the subject has cleared M3 and reconcile revenue, operating income, cash, debt, NOL, and invested capital to one valuation date.

## Procedure and controls

Review commercial evidence, operating history, and growth-asset dependence; reject single-threshold classification. Calculate staleness and document every normalization. Stop for an uncleared boundary, unexplained stale base, or simultaneous M3 and M4 forecast.

## Source evidence

Implements `CLM-GRW-001` through `CLM-GRW-004` and `CLM-GRW-029`.
