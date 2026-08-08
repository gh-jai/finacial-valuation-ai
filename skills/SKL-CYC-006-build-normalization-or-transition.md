---
id: SKL-CYC-006
title: Build Full Normalization or One Transition
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-CYC-005, CYC-002, CYC-003, WFL-GRW-001]
owner: fvi-maintainers
last_updated: "2026-08-08"
inputs: [Representative observations, Reconciled current vector, Normalized anchor]
outputs: [Complete normalized vector, Current-to-normal path, Calculation trail]
---

# Build Full Normalization or One Transition

Apply method-specific scale and comparability controls and recompute every linked input. A transition starts at the current base, ends once at the approved anchor, and cannot encode forecast cycles or a second recovery.
