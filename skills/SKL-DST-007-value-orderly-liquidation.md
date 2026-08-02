---
id: SKL-DST-007
title: Value Orderly Liquidation Alternative
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-DST-003, SKL-DST-005, DST-003]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Governed asset perimeter, Multi-year sale schedule, Status-quo value]
outputs: [Orderly-liquidation value, Selected no-distress alternative]
---

# Value Orderly Liquidation Alternative

Discount net non-urgent sale proceeds without a terminal value, then select the higher reviewed alternative for irreversible low distress. Keep the full sale program outside the status-quo closure object.
