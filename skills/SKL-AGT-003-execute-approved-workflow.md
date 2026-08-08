---
id: SKL-AGT-003
title: Execute Approved Workflow
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: []
dependencies: [SKL-AGT-001, SKL-AGT-002, WFL-CYC-001]
owner: fvi-maintainers
last_updated: "2026-08-08"
inputs: [Active exact-hash case approval, Registered adapter, Remaining action budget]
outputs: [Deterministic valuation-output artifact, Audited tool call]
---

# Execute Approved Workflow

Authorize the executor against the registry, verify the active case-lock approval, invoke only the registered M6 synthetic adapter, and record input and output hashes. Never select or modify the approved route.
