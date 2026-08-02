---
id: YNG-006
title: Negative FCFF Future Financing and Dilution
type: knowledge
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [YNG-003, YNG-005]
owner: fvi-maintainers
last_updated: "2026-08-02"
summary: Prevent future funding needs from being counted in both enterprise value and today's share denominator.
claim_refs: [CLM-YNG-027, CLM-YNG-028]
---

# Negative FCFF, Future Financing, and Dilution

Negative forecast FCFF already reduces operating value and captures future funding economics. Do not add expected future shares to today's denominator. Add financing proceeds only when authorized and retained, with explicit pre-money and post-money values.

## Evidence

Implements `CLM-YNG-027` and `CLM-YNG-028`, printed pages 311–318.
