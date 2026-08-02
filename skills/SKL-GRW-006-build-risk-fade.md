---
id: SKL-GRW-006
title: Build Growth-company Risk Fade
type: skill
status: draft
version: 0.1.0
domain: risk
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-GRW-005, GRW-005]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Operating-risk evidence, Financing path, Initial rate, Mature rate]
outputs: [Period-specific cost-of-capital path, Risk-separation record]
---

# Build Growth-company Risk Fade

## Procedure

Support initial and mature endpoints independently, declare any interpolation, and reconcile the path to the operating and financing narrative. Leave discrete failure outside the rate.

## Controls

Reject an unexplained constant high-growth rate, regression beta accepted despite shifting fundamentals, or failure premiums duplicated in the rate.

## Source evidence

Implements `CLM-GRW-006`, `CLM-GRW-013`, `CLM-GRW-014`, and `CLM-GRW-024`.
