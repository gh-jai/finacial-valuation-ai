# M4 Growth-company Scaling and Fade - Milestone Contract

Status: Approved for implementation
Contract version: 1.0.0
Primary source: `SRC-DAMODARAN-DARK-SIDE-2018`
Proposed workflow: `WFL-GRW-001`
Proposed schema: `schemas/growth-company-valuation.schema.json`

## Decision

M4 is a bounded intrinsic FCFF vertical slice for a company that has moved beyond the M3 young-company stage but still derives a material part of value from growth assets. It operationalizes the joint fade of revenue growth, operating margin, reinvestment economics, and risk into one internally consistent mature state.

This contract was approved by the FVI maintainers on 2026-08-02 and is the locked baseline for M4 implementation. Implementation must remain within this contract or document any proposed contract amendment separately.

## Source boundary

The governing boundary is Chapter 10, "Shooting Stars: Valuing Growth Companies," printed pages 323-357 and PDF pages 371-405. Chapter 11 starts on printed page 358 and PDF page 406.

| Treatment | Sections | Printed pages |
|---|---|---:|
| Executable M4 method | Life-cycle boundary, intrinsic valuation issues, DCF dark side, DCF light side | 323-346 |
| Composition boundary | Equity bridge and uncertainty | 346-351 |
| Excluded implementation | Relative valuation | 333-335, 352-356 |
| Summary support | Chapter conclusion | 356 |
| Location verification only | Notes | 356-357 |

The extraction manifest is `extraction/manifests/M4-growth-company-scaling-and-fade.yaml`. The 30 reviewed atomic claims are in `extraction/reviewed/M4-growth-company-scaling-and-fade-claims.yaml`.

## Model scope

### Included

- Growth-company classification and explicit separation from M3 young-company subjects.
- Current-period normalization for fast-changing revenue, operating income, capital invested, cash, debt, and NOL values.
- Revenue growth scaling and fade using absolute revenue changes, market size/share, competition, company history, and mature peers.
- Operating-margin convergence from current to reviewed target margin.
- Three reviewed reinvestment methods: revenue-change/sales-to-capital, fundamental return-on-capital linkage, and a bounded capacity-based investment holiday.
- Invested-capital roll-forward and implied return-on-capital checks.
- Period-specific costs of equity, debt, and capital converging with the operating narrative.
- Stable-state growth, return, reinvestment, risk, and leverage controls.
- FCFF generation and delegation of DCF arithmetic to `WFL-VAL-001`.
- Deterministic scenarios, two-driver sensitivity, and market-price break-even review without changing the approved base case.
- A bounded handoff to M3 survival-adjustment semantics if discrete failure risk remains material.

### Excluded

- Relative valuation, PEG, forward-multiple, and sector-specific-multiple engines.
- Monte Carlo simulation, decision trees, and real-options valuation.
- Live company or market-data ingestion.
- Statistical failure-probability estimation.
- Convertible-security decomposition, preferred-stock waterfalls, control premiums, voting-right allocation, and illiquidity discounts.
- Autonomous investment recommendations.
- Reimplementation of M1 DCF, M2 narrative, or M3 young-company mechanics.

## Life-cycle routing contract

The top-level forecast workflow must be selected before valuation.

| Condition | Route | Control |
|---|---|---|
| Idea, pre-revenue, early commercial, or otherwise meets the M3 young-company profile | `WFL-YNG-001` | Do not run an independent M4 forecast for the same narrative. |
| Demonstrated commercial product, meaningful operating evidence, and material growth-asset value | `WFL-GRW-001` | Record why the subject cleared the M3 boundary. |
| Growth company with material discrete failure risk | `WFL-GRW-001`, then M3 survival-adjustment semantics | Do not embed the same failure exposure in FCFF or discount rates. |
| Mature or declining company | Stop and route to a later milestone | Do not force M4 fade mechanics onto a later life-cycle stage. |

Classification is evidence-backed and reviewed; a single threshold such as revenue growth, sector, company age, or trading multiple is insufficient.

## Financial responsibility contract

| Concern | M4 responsibility | Delegated responsibility |
|---|---|---|
| Evidence and business narrative | Require approved assertions and driver mappings | `WFL-NAR-001` |
| Revenue path | Scale test, explicit fade, market/competition constraints | None |
| Margin path | Current-to-target convergence with stated driver | None |
| Taxes and NOL | Period tax calculation and NOL roll-forward | Reuse proven M3 semantics without changing its public contract |
| Reinvestment | Select one method, apply lag/capacity rule, reconcile implied ROC | None |
| FCFF | Emit revenues, margins, tax rates, and reinvestments | `WFL-VAL-001` computes FCFF and DCF |
| Discount rates | Produce a reviewed period-specific cost-of-capital path | `WFL-VAL-001` applies cumulative discounting |
| Terminal state | Rebuild terminal FCFF from stable growth, stable ROC, and reinvestment | `WFL-VAL-001` applies Gordon growth |
| Failure risk | Flag and provide a going-concern operating value | M3 survival-adjustment semantics apply expected value once |
| Equity bridge | Provide current bridge inputs and provenance | M1 standard bridge or bounded M3 claim controls, selected explicitly |
| Sensitivity | Separate deterministic alternatives and break-even cases | M1 sensitivity arithmetic may be reused |

## Required formulas and invariants

### Revenue and scale

For each forecast year `t`:

```text
revenue[t] = revenue[t-1] * (1 + revenue_growth[t])
absolute_revenue_change[t] = revenue[t] - revenue[t-1]
market_share[t] = revenue[t] / addressable_market[t]  # when market data is supplied
```

The contract does not require monotonically declining growth in every case, but any increase or plateau must have a reviewed narrative assertion. The forecast must expose absolute scale and any market-share constraint.

### Margin and operating income

```text
operating_income[t] = revenue[t] * operating_margin[t]
after_tax_operating_income[t] = operating_income[t] - cash_tax[t]
```

The target margin, convergence start, convergence end, and path must be explicit. A margin path may rise or fall but cannot silently jump to the target.

### Reinvestment

Exactly one primary method is selected for each forecast segment:

```text
revenue_change_method:
  reinvestment[t] = applicable_revenue_change / sales_to_capital_ratio

fundamental_method:
  operating_income_growth[t]
  = return_on_capital[t] * reinvestment_rate[t] + efficiency_growth[t]

capacity_holiday_method:
  reinvestment[t] may be minimal only while documented spare capacity supports forecast output
```

In all cases:

```text
invested_capital[t] = invested_capital[t-1] + reinvestment[t]
implied_return_on_capital[t]
= after_tax_operating_income[t] / invested_capital[t-1]
fcff[t] = after_tax_operating_income[t] - reinvestment[t]
```

Every discontinuity, lag, or investment holiday requires a stated capacity or operating rationale.

### Risk fade and discounting

The period cost of capital must reconcile to documented operating risk, financing mix, and available tax benefits. A default linear interpolation is permitted only when the start and mature endpoints are independently supported and the interpolation is declared.

```text
cumulative_discount_denominator[t]
= product(1 + cost_of_capital[i]) for i = 1..t
present_value[t] = fcff[t] / cumulative_discount_denominator[t]
```

Discrete failure risk is not a cost-of-capital premium and is not a forecast cash-flow loss.

### Stable state and terminal value

The mature year must be explicit. Forecasts longer than ten years require exceptional evidence and a reviewer finding.

```text
stable_reinvestment_rate = stable_growth_rate / stable_return_on_capital
terminal_after_tax_operating_income
= terminal_revenue * terminal_operating_margin * (1 - terminal_tax_rate)
terminal_reinvestment
= terminal_after_tax_operating_income * stable_reinvestment_rate
terminal_fcff
= terminal_after_tax_operating_income - terminal_reinvestment
terminal_value
= terminal_fcff / (terminal_cost_of_capital - stable_growth_rate)
```

The terminal FCFF must be rebuilt from terminal-state drivers. It must not be obtained by simply growing the final high-growth FCFF when the return, reinvestment, margin, or risk state changes.

Required terminal controls:

- `stable_growth_rate < terminal_cost_of_capital`.
- Stable growth respects the existing M1 long-run ceiling.
- Stable return on capital and excess return are supportable for the stated competitive position.
- Stable reinvestment rate is finite and reconciles to growth and return.
- Terminal margin, tax rate, risk, leverage, and reinvestment all represent the same mature company.

## Schema contract

The M4 implementation will add `schemas/growth-company-valuation.schema.json` with `additionalProperties: false` at every governed object.

| Object | Required fields |
|---|---|
| Root | `schema_version`, `id`, `narrative_id`, `as_of_date`, `subject`, `currency`, `growth_company_profile`, `base_period`, `forecast`, `stable_state`, `going_concern`, `traceability`, `limitations`, `review` |
| `growth_company_profile` | `classification`, `m3_boundary_cleared`, `classification_reasoning`, `commercial_evidence_refs`, `growth_asset_reasoning`, `financial_dynamism`, `evidence_refs` |
| `base_period` | `period_end`, `as_of_date`, `staleness_days`, `revenues`, `operating_income`, `cash`, `debt`, `net_operating_loss`, `invested_capital`, `normalization_adjustments`, `evidence_refs` |
| `forecast` | `years`, `revenue_growth_rates`, `revenues`, `absolute_revenue_changes`, `operating_margins`, `operating_incomes`, `tax_rates`, `cash_taxes`, `nol_balances`, `after_tax_operating_incomes`, `reinvestment_method`, `reinvestments`, `invested_capital`, `implied_returns_on_capital`, `discount_rates`, `assumption_trace` |
| `stable_state` | `mature_year`, `growth_rate`, `operating_margin`, `tax_rate`, `return_on_capital`, `reinvestment_rate`, `cost_of_capital`, `excess_return`, `supporting_refs` |
| `going_concern` | `engine`, `fcff`, `cumulative_discount_factors`, `forecast_present_value`, `terminal_fcff`, `terminal_value`, `terminal_present_value`, `operating_asset_value`, `terminal_value_share`, `calculation_trail` |
| `traceability` | `source_refs`, `claim_refs`, `narrative_assertion_refs` |
| `review` | `status`, `reviewer`, `reviewed_at`, `classification_approved`, `scale_approved`, `reinvestment_approved`, `risk_fade_approved`, `stable_state_approved`, `failure_risk_reviewed` |

Optional governed objects:

- `market_context`: addressable market, market growth, market share, mature-peer evidence, and competition notes.
- `capacity_holiday`: capacity, utilization, maximum supported output, start/end years, and reinvestment resumption.
- `failure_handoff`: whether failure risk is material, the M3-compatible adjustment input reference, and double-counting attestations.
- `equity_bridge_handoff`: selected M1 or M3 bridge path and current-input references.
- `sensitivity`: separate scenario IDs, driver grid, break-even values, and market-price observation used only as a comparison.

The validator must recompute every numeric series and reject length mismatches, non-finite values, stale-base omissions, unsupported fade discontinuities, reinvestment-method conflicts, inconsistent terminal state, and risk double counting.

## Workflow contract

`WFL-GRW-001` executes in this order:

1. Receive one approved `WFL-NAR-001` narrative and driver map.
2. Confirm the subject clears the M3 young-company boundary.
3. Normalize the base period to the valuation date.
4. Build the revenue scale and fade path.
5. Build the target-margin convergence path.
6. Select and apply the reinvestment method by forecast segment.
7. Roll forward NOL and taxes, invested capital, implied ROC, and FCFF.
8. Build period-specific discount rates consistent with the same maturation narrative.
9. Rebuild the stable state and terminal FCFF.
10. Delegate DCF arithmetic to `WFL-VAL-001`.
11. If material failure risk exists, apply M3 survival-adjustment semantics once to the M4 going-concern operating value.
12. Select the explicit M1 or M3 equity-bridge path.
13. Run deterministic sensitivity and break-even review without changing the base assumptions.
14. Return value-driver findings to the M2 feedback revision loop.

Each materially different narrative, fade path, or failure assumption remains a separate valuation object. The engine must not average alternatives.

## Risk-placement contract

| Risk | Placement | Prohibited duplicate |
|---|---|---|
| Market saturation and scale | Revenue growth and absolute scale | Arbitrary post-valuation discount |
| Competition and moat erosion | Revenue fade, margin path, stable excess return | Unsupported discount-rate premium for the same effect |
| Operating leverage and execution | Margin path and deterministic scenarios | Hidden haircut after valuation |
| Reinvestment effectiveness | Sales-to-capital, reinvestment rate, implied ROC | Growth without capital support |
| Continuous business and financing risk | Period-specific cost of capital | Constant rate unrelated to maturation |
| Discrete failure | M3 expected-value survival adjustment | Failure premium in rates or failure loss in FCFF |
| Future equity financing | Negative FCFF present value | Adding forecast future shares to today's denominator |
| Market-price uncertainty | Sensitivity and break-even comparison | Calibrating the base case to observed price |

## Synthetic benchmark design

### Benchmark A - Asset-light platform fade

Purpose: test scale, margin, reinvestment, risk, and stable-state convergence for a profitable asset-light growth company.

- Ten-year explicit forecast.
- Revenue growth is high for the first three years, then fades to a stable rate.
- Absolute revenues and market share remain below explicit synthetic ceilings.
- Margin converges upward to a mature peer target.
- Revenue-change/sales-to-capital reinvestment method.
- Implied ROC rises during scaling and fades to a positive but bounded stable excess return.
- Cost of capital declines to a mature endpoint.
- No failure adjustment; M1 equity bridge.

Required assertions include exact recomputation, terminal-state rebuild, cumulative discount factors, and a terminal-value-share disclosure.

### Benchmark B - Capacity-led expansion

Purpose: test a profitable but capital-intensive growth company with prebuilt capacity and later reinvestment resumption.

- Ten-year explicit forecast.
- A documented two-year capacity holiday supports growth without major reinvestment.
- Capacity utilization reaches its reviewed ceiling before reinvestment resumes.
- Margin converges modestly rather than expanding dramatically.
- Later reinvestment uses a lower sales-to-capital ratio than Benchmark A.
- Implied ROC remains above zero and converges toward cost of capital in stable growth.
- Cost of capital declines more slowly than Benchmark A.
- A separate low-probability failure case exercises the M3 handoff without changing the going-concern rates.

Required assertions include rejection if the holiday exceeds capacity, probability reconciliation, no failure double count, and no future-share dilution double count.

### Adversarial cases

- Historical high growth extended without scale evidence.
- High growth with zero reinvestment and no documented capacity.
- Low terminal growth with a frozen high reinvestment rate.
- Constant high-growth discount rate after mature-state transition.
- Regression beta accepted despite a short and shifting history without review.
- Terminal FCFF calculated by growing the last high-growth FCFF.
- Stable growth at or above terminal cost of capital.
- Market price used to overwrite approved assumptions.
- M3 and M4 forecast workflows applied to the same base narrative.
- Failure risk in both discount rates and survival adjustment.

## Acceptance criteria

M4 implementation is complete only when all of the following pass:

- All 30 `CLM-GRW-*` claims are maintainer-reviewed and mapped to M4 Knowledge artifacts.
- The extraction manifest and source-map relationships validate without private-source content.
- The new schema loads under JSON Schema 2020-12 and rejects undeclared properties.
- The calculation validator independently recomputes revenue, margin, taxes, NOL, reinvestment, invested capital, implied ROC, FCFF, cumulative discount factors, terminal FCFF, terminal value, and operating-asset value.
- Both deterministic benchmarks match committed expected outputs within documented tolerances.
- Every adversarial case fails for the intended reason.
- M1, M2, and M3 artifact, benchmark, and regression tests remain unchanged in behavior and pass.
- The complete suite passes on Python 3.10 and Python 3.12.
- Repository policy reports no PDFs, raw extracts, copied tables/figures, sequential source text, or long quotations.
- A human reviewer completes `templates/m4-growth-company-review-checklist.md`.

## Stop conditions

Stop implementation or valuation for an uncleared M3 boundary, stale or unexplained base period, unbounded scale, unsupported growth plateau, missing margin target, growth without reinvestment, overlapping reinvestment methods, unexplained investment holiday, implausible implied ROC, constant risk unsupported by the narrative, terminal-state inconsistency, failure-risk double counting, future-share dilution double counting, market-price anchoring, merged alternatives, or private source content.

## Approved implementation baseline

The FVI maintainers approved the following items on 2026-08-02:

1. Chapter 10 printed pages 323-357 / PDF pages 371-405 as the exact source boundary.
2. The executable, boundary-only, and excluded section split.
3. All 30 atomic claims and their source locations.
4. The M3-to-M4 life-cycle routing rule.
5. The schema field contract and formula invariants.
6. Reuse of M3 survival-adjustment semantics without invoking a duplicate young-company forecast.
7. The two deterministic benchmark designs and adversarial cases.
8. The acceptance criteria and no-regression requirement.

Codex may implement the repository-wide M4 artifact graph, engine, validator, schema, fixtures, expected outputs, tests, and documentation on a separate feature branch.
