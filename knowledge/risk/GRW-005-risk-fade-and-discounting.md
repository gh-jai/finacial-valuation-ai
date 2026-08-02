---
id: GRW-005
title: Growth-company Risk Fade and Discounting
type: knowledge
status: draft
version: 0.1.0
domain: risk
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [GRW-002, GRW-004, YNG-004]
owner: fvi-maintainers
last_updated: "2026-08-02"
summary: Converge operating and financing risk with the same maturation narrative and discount every period cumulatively.
claim_refs: [CLM-GRW-006, CLM-GRW-013, CLM-GRW-014, CLM-GRW-024, CLM-GRW-026]
---

# Growth-company Risk Fade and Discounting

Period-specific costs of capital reconcile to operating risk, earnings stability, financing mix, and tax benefits. Supported endpoints may be joined by a declared interpolation; a short regression history does not substitute for forward operating evidence.

Every FCFF and the terminal value use the cumulative product of all applicable period rates. Discrete failure risk is excluded from rates and cash flows when an M3-compatible survival handoff is used.

## Controls

Reject an unexplained constant high-growth rate, noncumulative discounting, or the same risk in both forecast drivers and an arbitrary premium.

## Evidence

Implements `CLM-GRW-006`, `CLM-GRW-013`, `CLM-GRW-014`, `CLM-GRW-024`, and `CLM-GRW-026`, printed pages 326–346.
