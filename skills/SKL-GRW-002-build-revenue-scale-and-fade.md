---
id: SKL-GRW-002
title: Build Revenue Scale and Fade
type: skill
status: draft
version: 0.1.0
domain: lifecycle
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-GRW-001, GRW-002]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Normalized revenue, Growth rates, Market path, Competition evidence]
outputs: [Revenue path, Absolute revenue changes, Market-share checks]
---

# Build Revenue Scale and Fade

## Procedure

Compound the normalized base by each reviewed rate, expose absolute changes, and divide revenue by addressable market when supplied. Compare the path with company history, competitors, and mature peers.

## Decision rules

Any growth plateau or increase needs a reviewed assertion. Reject unbounded scale, share above one, or historical growth extended without competitive evidence.

## Source evidence

Implements `CLM-GRW-005`, `CLM-GRW-008`, `CLM-GRW-009`, `CLM-GRW-017`, and `CLM-GRW-018`.
