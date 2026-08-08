---
id: SKL-AGT-004
title: Review Agent Output Independently
type: skill
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-INVESTMENT-FABLES, SRC-BAID-JOYS-COMPOUNDING-ZH-2024]
dependencies: [SKL-AGT-003, AGT-003, AGT-004]
owner: fvi-maintainers
last_updated: "2026-08-08"
inputs: [Agent run, Executor output, Registry, M1-M6 validators]
outputs: [Independent evaluation result, Blocking and nonblocking findings, Output-approval request or failed state]
---

# Review Agent Output Independently

Recompute hashes and state without runtime helpers, execute existing deterministic validators, verify evidence policy and separation of duties, and issue findings. Do not modify the artifact under review.
