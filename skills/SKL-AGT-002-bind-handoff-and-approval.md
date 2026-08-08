---
id: SKL-AGT-002
title: Bind Handoff and Human Approval
type: skill
status: draft
version: 0.1.0
domain: cross-domain
source_refs: []
dependencies: [AGT-001, AGT-002]
owner: fvi-maintainers
last_updated: "2026-08-08"
inputs: [Canonical artifact, Sender and recipient, Human gate decision]
outputs: [Content-addressed handoff, Exact-hash approval or invalidation event]
---

# Bind Handoff and Human Approval

Hash canonical JSON, bind one handoff to one artifact revision, and accept approvals only from a human actor. Invalidate approval after any payload change and return to the relevant gate.
