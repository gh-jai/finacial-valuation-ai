---
id: SKL-CYC-005
title: Select One Cycle Valuation Treatment
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-CYC-004, CYC-002, CYC-003, CYC-004]
owner: fvi-maintainers
last_updated: "2026-08-08"
inputs: [Approved regime, Current base, Representative-window decision]
outputs: [One treatment mode, Treatment stop findings]
---

# Select One Cycle Valuation Treatment

Choose exactly one of normalized inputs, transition to normal, current expectations, or stop. Reject overlapping payloads, unsupported historical anchors, selective normalization, and recovery double counting.
