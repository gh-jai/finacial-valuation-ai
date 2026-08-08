---
id: CYC-004
title: Current Expectations and Deterministic Scenarios
type: knowledge
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [CYC-001, CYC-002, WFL-VAL-001]
owner: fvi-maintainers
last_updated: "2026-08-08"
summary: Use dated current or market-implied driver paths after instability or structural breaks and expose uncertainty through complete isolated scenarios.
claim_refs: [CLM-CYC-016, CLM-CYC-017, CLM-CYC-018]
---

# Current Expectations and Deterministic Scenarios

Each driver point retains its source type, as-of date, and financial mapping. A storable-commodity futures curve discloses storage and financing carry and is not described as an independent fundamental forecast.

Every scenario contains its own complete input set and calculation trail. Report a range when no approved probabilities exist. Probability weighting requires one reviewed event, horizon, as-of date, provenance, and weights that sum to one.

## Evidence

Implements `CLM-CYC-016` through `CLM-CYC-018`, Chapter 13, printed pages 448-451.
