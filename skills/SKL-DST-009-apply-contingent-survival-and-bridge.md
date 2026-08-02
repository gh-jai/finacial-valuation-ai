---
id: SKL-DST-009
title: Apply Contingent Survival and Claim Bridge
type: skill
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-DST-006, SKL-DST-007, SKL-DST-008, DST-005, DST-007, WFL-YNG-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [No-distress value, Distress-sale value, Event probability, Current claim inventory]
outputs: [Contingent value, Common equity, Per-share value, Calculation trail]
---

# Apply Contingent Survival and Claim Bridge

Require one event, horizon, date, source, and any default-to-cessation mapping. Weight same-basis values once, then apply current cash and market-valued claims once. Reject probability mismatches, risk double counting, stale claims, or mixed bases.
