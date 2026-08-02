---
id: SKL-GRW-003
title: Build Margin Tax and NOL Path
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-GRW-002, GRW-003, YNG-003]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Revenue path, Current margin, Target margin, NOL, Marginal tax rate]
outputs: [Operating income, Cash taxes, NOL balances, After-tax operating income]
---

# Build Margin Tax and NOL Path

## Procedure

Create the declared current-to-target margin path, calculate operating income, then reuse M3 NOL carryforward semantics to derive cash taxes and after-tax operating income.

## Controls

Reject a silent margin jump, a missing target, an unsupported target, premature cash taxes, or series-length mismatch.

## Source evidence

Implements `CLM-GRW-003`, `CLM-GRW-004`, and `CLM-GRW-019`.
