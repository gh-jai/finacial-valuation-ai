---
id: YNG-004
title: Time-varying Discount Rates and Mature-state Convergence
type: knowledge
status: draft
version: 0.1.0
domain: risk
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [VAL-002, YNG-003]
owner: fvi-maintainers
last_updated: "2026-08-02"
summary: Model operating risk through a period-specific cost-of-capital path and cumulative discounting.
claim_refs: [CLM-YNG-020, CLM-YNG-021, CLM-YNG-023]
---

# Time-varying Discount Rates

Young-company risk and financing evolve, so the cost of capital may converge toward a mature rate. Each period uses cumulative discount factors. Operating risk belongs in cash flows and rates; discrete failure risk does not belong in an unsupported rate premium.

## Evidence

Implements `CLM-YNG-020`, `CLM-YNG-021`, and `CLM-YNG-023`, printed pages 298–308.
