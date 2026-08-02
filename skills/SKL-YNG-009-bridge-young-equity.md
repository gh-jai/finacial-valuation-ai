---
id: SKL-YNG-009
title: Bridge to Young-company Equity and Per-share Value
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-YNG-008, YNG-006, YNG-007]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Adjusted operating value, Cash, Authorized financing, Senior claims, Explicit option value, Current shares]
outputs: [Pre-money value, Post-money value, Common equity and per-share value]
---

# Bridge to Young-company Equity and Per-share Value
## Purpose
Allocate survival-adjusted operating value to current common equity without dilution or claim double counting.
## Preconditions
Claim structure and financing authority are reviewed.
## Input schema
Operating value, cash, retained authorized financing, debt/senior claims, explicit option/other-claim values, current shares, dilution flags.
## Procedure
Calculate pre-money common equity; add authorized financing for post-money value; divide by current applicable shares.
## Decision rules
Reject unauthorized proceeds, unvalued option deductions, and future shares added for already-valued negative FCFF.
## Output schema
Schema-ready equity bridge and calculation trail.
## Controls
Separate materially different claim structures and preserve current versus future share distinction.
## Failure modes
Circular dilution, option haircut, proceeds not retained, or merged claim structures.
## Source evidence
Implements `CLM-YNG-027` through `CLM-YNG-030`, pages 311–321.
## Tests or test expectations
Test negative-FCFF dilution, financing authorization, option valuation, pre/post money, and per-share arithmetic.
