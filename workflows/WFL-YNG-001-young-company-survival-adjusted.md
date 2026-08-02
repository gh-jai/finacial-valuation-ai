---
id: WFL-YNG-001
title: Young-company Survival-adjusted Valuation
type: workflow
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018, SRC-DAMODARAN-NARRATIVE-NUMBERS-2017, SRC-DAMODARAN-LBV-2024]
dependencies: [WFL-NAR-001, WFL-VAL-001, YNG-001, YNG-002, YNG-003, YNG-004, YNG-005, YNG-006, YNG-007]
owner: fvi-maintainers
last_updated: "2026-08-02"
skill_refs: [SKL-YNG-001, SKL-YNG-002, SKL-YNG-003, SKL-YNG-004, SKL-YNG-005, SKL-YNG-006, SKL-YNG-007, SKL-YNG-008, SKL-YNG-009]
review_gates:
  - M2 narrative approval
  - Young-company classification
  - Forecast-method selection
  - Margin tax and reinvestment consistency
  - Operating and failure risk separation
  - Failure probability value and basis
  - Equity claims financing and dilution
  - Alternative and key-person scenario separation
  - Final approval
---

# Young-company Survival-adjusted Valuation

## Objective

Convert an approved M2 narrative into a young-company operating forecast, delegate going-concern FCFF valuation to M1, apply discrete survival adjustment once, and bridge to current common-equity value.

## Execution order

1. Run `WFL-NAR-001` and retain assertion/evidence traces.
2. `SKL-YNG-001`: classify the young company.
3. `SKL-YNG-002`: select top-down, bottom-up, or reviewed hybrid forecasting.
4. `SKL-YNG-003` or `SKL-YNG-004`: build the revenue forecast.
5. `SKL-YNG-005`: forecast margins, NOL-based taxes, reinvestment, and FCFF drivers.
6. `SKL-YNG-006`: build period-specific discount rates converging to maturity.
7. Pass FCFF and rates to `WFL-VAL-001` for going-concern value.
8. `SKL-YNG-007`: estimate a reconciled failure scenario.
9. `SKL-YNG-008`: calculate survival-adjusted operating value and any separate key-person scenario.
10. `SKL-YNG-009`: bridge pre-money/post-money common equity and per-share value.
11. Return evidence and value changes to `WFL-NAR-001` feedback revision.

## Risk separation

- Operating risk belongs in revenue, margins, reinvestment, and period rates.
- Discrete failure risk belongs only in failure/survival probabilities and failure value.
- Key-person risk uses a separately valued operating scenario.

## Stop conditions

Stop for probability mismatch, terminal growth at/above the terminal rate, basis mismatch, failure risk embedded twice, unsupported growth, future-share dilution double counting, unauthorized proceeds, unvalued option deductions, merged alternatives or claim structures, or private source content.

## Outputs

One schema-valid young-company valuation per narrative and materially different claim structure, including going-concern calculation trail, survival components, failure delta, pre/post-money bridge, per-share value, limitations, and human review record.

## Source evidence

Operationalizes all 30 `CLM-YNG-*` claims from Chapter 9, printed pages 259–321. Chapter 10 begins on printed page 323 and is outside M3. M1 and M2 mechanics are composed, not duplicated.
