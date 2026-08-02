---
id: YNG-007
title: Young-company Equity Claims Options and Value Bridges
type: knowledge
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [YNG-005, YNG-006]
owner: fvi-maintainers
last_updated: "2026-08-02"
summary: Bridge survival-adjusted operating value to common equity while preserving claim differences.
claim_refs: [CLM-YNG-007, CLM-YNG-008, CLM-YNG-028, CLM-YNG-029, CLM-YNG-030]
---

# Equity Claims, Employee Options, and Value Bridges

Add existing cash and authorized retained financing proceeds; subtract debt, senior claims, explicitly valued options, and other equity claims; divide by the current applicable share count. Materially different claim structures remain separate objects. Real-option premiums require meaningful exclusivity and are outside this implementation.

## Evidence

Implements `CLM-YNG-007`, `CLM-YNG-008`, and `CLM-YNG-028` through `CLM-YNG-030`, printed pages 262–321.
