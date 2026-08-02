---
id: GRW-004
title: Reinvestment and Implied Returns
type: knowledge
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [GRW-003, VAL-003]
owner: fvi-maintainers
last_updated: "2026-08-02"
summary: Support growth with one reviewed reinvestment method per segment and expose invested capital and implied return on capital.
claim_refs: [CLM-GRW-010, CLM-GRW-011, CLM-GRW-020, CLM-GRW-021, CLM-GRW-022, CLM-GRW-023]
---

# Reinvestment and Implied Returns

Each period uses exactly one primary method: revenue change divided by sales-to-capital, a fundamental return/reinvestment linkage, or a bounded capacity holiday. A holiday states capacity, utilization, maximum output, and the year investment resumes.

Invested capital rolls forward with reinvestment. After-tax operating income divided by opening invested capital exposes the implied return on capital and makes unsupported growth visible. Stable reinvestment equals stable growth divided by stable return on capital.

## Controls

Reject growth without capital support, overlapping methods, an unexplained lag or holiday, implausible implied returns, or a high-growth reinvestment rate frozen into maturity.

## Evidence

Implements `CLM-GRW-010`, `CLM-GRW-011`, and `CLM-GRW-020` through `CLM-GRW-023`, printed pages 329–338.
