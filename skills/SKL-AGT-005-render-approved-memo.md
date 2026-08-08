---
id: SKL-AGT-005
title: Render Approved Memo
type: skill
status: draft
version: 0.1.0
domain: cross-domain
source_refs: []
dependencies: [SKL-AGT-002, SKL-AGT-004]
owner: fvi-maintainers
last_updated: "2026-08-08"
inputs: [Active exact-hash output approval, Validated output, Independent findings, Limitations]
outputs: [Immutable valuation memo artifact]
---

# Render Approved Memo

Render only approved fields and findings. Refuse to change numbers, omit blocking limitations, add unsupported certainty, or produce a buy, sell, timing, leverage, hedging, or sizing recommendation.
