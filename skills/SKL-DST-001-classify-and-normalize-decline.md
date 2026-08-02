---
id: SKL-DST-001
title: Classify and Normalize Declining Company
type: skill
status: draft
version: 0.1.0
domain: lifecycle
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [WFL-NAR-001, WFL-YNG-001, WFL-GRW-001, DST-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Approved narrative, Multi-period decline evidence, Sector evidence, Current financials]
outputs: [M5 boundary decision, Normalized base, Evidence trace]
---

# Classify and Normalize Declining Company

Clear young, growth, mature, and cycle-driven boundaries. Normalize continuing revenue, operating income, cash, book and market debt, face debt, capital, and fixed obligations to the valuation date. Stop for a one-period label, stale unexplained inputs, or overlapping top-level workflow.
