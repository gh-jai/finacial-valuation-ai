---
id: DST-005
title: Separate Contingent Survival
type: knowledge
status: draft
version: 0.1.0
domain: risk
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [DST-001, YNG-005, VAL-002]
owner: fvi-maintainers
last_updated: "2026-08-02"
summary: Apply one deterministic cessation or forced-sale probability after the conditional going-concern value.
claim_refs: [CLM-DST-014, CLM-DST-023, CLM-DST-024, CLM-DST-025, CLM-DST-027]
---

# Separate Contingent Survival

A higher conditional cost of capital does not remove the later cash flows lost when operations cease. M5 therefore keeps the going-concern forecast conditional on survival, defines one event and matching horizon, estimates a separate distress-sale value, and probability-weights the two values once.

Bond default, bankruptcy, cessation, and liquidation are not synonyms. Evidence for a different event needs a reviewed mapping. Direct transaction costs and indirect customer, employee, supplier, and lender effects belong in recovery, not in a second haircut.

## Evidence

Implements `CLM-DST-014`, `CLM-DST-023` through `CLM-DST-025`, and `CLM-DST-027`, printed pages 405-418.
