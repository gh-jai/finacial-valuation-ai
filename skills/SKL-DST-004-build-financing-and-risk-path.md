---
id: SKL-DST-004
title: Build Financing Tax-benefit and Risk Path
type: skill
status: draft
version: 0.1.0
domain: risk
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-DST-002, DST-006]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Face-debt schedule, Cash interest, Operating income, Market debt and equity, Costs of debt and equity]
outputs: [Debt roll-forward, Tax benefits, Capital weights, After-tax debt cost, WACC]
---

# Build Financing Tax-benefit and Risk Path

Roll face debt, floor available taxable operating income at zero, cap the interest tax benefit, compute market-value weights, and calculate each period's conditional WACC. Stop for book-weight proxies, negative market equity, or a duplicated cessation premium.
