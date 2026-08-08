---
id: AGT-002
title: Immutable Handoffs and Approval Binding
type: knowledge
status: draft
version: 0.1.0
domain: cross-domain
source_refs: []
dependencies: [AGT-001]
owner: fvi-maintainers
last_updated: "2026-08-08"
summary: Bind every handoff and human approval to the canonical hash of one exact artifact revision and invalidate approval after mutation.
claim_refs: []
---

# Immutable Handoffs and Approval Binding

Canonical JSON hashes make the approved object explicit. Handoffs carry an artifact ID and payload hash; human approvals carry the same pair plus a gate. An artifact revision creates a new hash and invalidates every active approval for the prior hash.

State is derived from the append-only event sequence. A reported status is not authoritative when events, hashes, approvals, or actors disagree.
