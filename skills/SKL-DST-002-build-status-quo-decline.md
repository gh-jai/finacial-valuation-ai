---
id: SKL-DST-002
title: Build Status-quo Decline Forecast
type: skill
status: draft
version: 0.1.0
domain: valuation
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-DST-001, DST-002, WFL-VAL-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Normalized revenue and capital, Growth path, Margins, Tax rates, Reinvestment]
outputs: [Revenue, Operating income, Tax, Capital, Implied return, FCFF]
---

# Build Status-quo Decline Forecast

Roll revenue, operating income, loss-limited cash tax, invested capital, implied return, and FCFF. Negative reinvestment requires an equal documented release. Reject optimistic recovery hidden inside status quo.
