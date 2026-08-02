---
id: DST-002
title: Declining FCFF and Capital Release
type: knowledge
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [DST-001, VAL-002, GRW-004]
owner: fvi-maintainers
last_updated: "2026-08-02"
summary: Build negative-growth operating paths without forcing optimistic growth or treating supported capital release as an error.
claim_refs: [CLM-DST-005, CLM-DST-007, CLM-DST-008, CLM-DST-013]
---

# Declining FCFF and Capital Release

Revenue growth and reinvestment may be negative. A negative reinvestment amount must reconcile to a dated capital reduction, excess depreciation, working-capital release, or governed divestiture; it cannot be a plug. Existing assets may remain below book value when their returns stay below the cost of capital.

FCFF remains after-tax operating income less reinvestment. Positive growth, restored margins, healthy rates, and large terminal values are never inserted automatically into the status-quo case.

## Evidence

Implements `CLM-DST-005`, `CLM-DST-007`, `CLM-DST-008`, and `CLM-DST-013`, printed pages 398-403.
