---
id: DST-006
title: Financing Tax-benefit and Risk Path
type: knowledge
status: draft
version: 0.1.0
domain: risk
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [DST-001, DST-005, GRW-005]
owner: fvi-maintainers
last_updated: "2026-08-02"
summary: Recompute face debt, market-value capital weights, loss-limited interest tax benefits, and conditional costs of capital.
claim_refs: [CLM-DST-009, CLM-DST-010, CLM-DST-016, CLM-DST-026]
---

# Financing Tax-benefit and Risk Path

Face debt rolls forward from issuances and repayments. Capital weights use nonnegative market values rather than book balances. Interest tax benefits are limited by nonnegative available operating income, so a loss creates no negative shield and no full marginal-rate benefit.

After-tax debt cost and WACC are recomputed every period. The path may recover with survival-consistent deleveraging, but it cannot add a discrete cessation premium already handled by contingent survival.

## Evidence

Implements `CLM-DST-009`, `CLM-DST-010`, `CLM-DST-016`, and `CLM-DST-026`, printed pages 399-405 and 415-424.
