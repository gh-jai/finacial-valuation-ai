---
id: SKL-DST-003
title: Reconcile Divestitures
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-DST-002, DST-003]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Asset sale schedule, Capital removed, Operating contributions, Sale costs and taxes]
outputs: [Net proceeds, Remaining operations, Double-count reconciliation]
---

# Reconcile Divestitures

For each asset and year, subtract costs and taxes from gross proceeds, remove capital and later operating contribution, and attest whether proceeds are already represented in reinvestment. Stop for retained disposed earnings or a repeated cash-flow line.
