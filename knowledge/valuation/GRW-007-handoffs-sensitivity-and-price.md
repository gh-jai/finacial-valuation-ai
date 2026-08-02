---
id: GRW-007
title: Valuation Handoffs Sensitivity and Price Independence
type: knowledge
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [GRW-001, GRW-006, WFL-VAL-001, WFL-YNG-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
summary: Compose FCFF, failure, equity bridge, sensitivity, and feedback without double counting or market-price anchoring.
claim_refs: [CLM-GRW-015, CLM-GRW-016, CLM-GRW-027, CLM-GRW-028, CLM-GRW-029, CLM-GRW-030]
---

# Valuation Handoffs Sensitivity and Price Independence

M4 emits FCFF and period rates to M1. Material discrete failure is applied once to the going-concern operating value using M3 semantics, without running a duplicate young-company forecast. The equity bridge uses current cash, debt, and an explicit M1 or M3 claim path.

Negative forecast FCFF already captures future funding needs; adding forecast future shares to today's denominator would double count them. Deterministic scenarios, two-driver sensitivity, and price break-even review remain separate from the approved base narrative. Observed price never overwrites intrinsic assumptions.

## Evidence

Implements `CLM-GRW-015`, `CLM-GRW-016`, and `CLM-GRW-027` through `CLM-GRW-030`, printed pages 333–349.
