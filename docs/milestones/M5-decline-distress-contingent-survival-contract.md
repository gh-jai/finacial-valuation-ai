# M5 Decline, Distress, and Contingent Survival - Milestone Contract

Status: Approved for implementation
Contract version: 1.0.0
Primary source: `SRC-DAMODARAN-DARK-SIDE-2018`
Proposed workflow: `WFL-DST-001`
Proposed schema: `schemas/decline-distress-valuation.schema.json`

## Decision

M5 is a bounded intrinsic FCFF vertical slice for operating companies in structural or potentially reversible decline. It classifies decline separately from financial distress, values the relevant no-distress operating alternatives, and applies one explicit contingent-survival or liquidation decision on a declared valuation basis.

This contract was approved by the FVI maintainers on 2026-08-02 and is the locked baseline for M5 implementation. Implementation must remain within this contract or document any proposed contract amendment separately.

## Source boundary

The governing boundary is Chapter 12, "Winding Down: Declining Companies," printed pages 397-436 and PDF pages 445-484. Chapter 11 covers mature companies and ends before this boundary. Chapter 13 starts on printed page 438 and PDF page 486; PDF page 485 is the Part IV divider.

| Treatment | Sections | Printed pages |
|---|---|---:|
| Executable M5 method | Life-cycle boundary, intrinsic valuation issues, dark-side controls, decline/distress framework, separate distress adjustment | 397-424 |
| Composition boundary | Reversible decline/control input, modified DCF alternative, debt and hybrid-claim inventory | 400, 407, 410-415, 419 |
| Excluded implementation | Relative valuation, simulation, statistical probability models, APV, equity-as-option | 400-401, 406, 413-418, 424-435 |
| Summary support | Chapter conclusion | 435 |
| Location verification only | Notes | 435-436 |

The extraction manifest is `extraction/manifests/M5-decline-distress-contingent-survival.yaml`. The 32 reviewed atomic claims are in `extraction/reviewed/M5-decline-distress-contingent-survival-claims.yaml`.

## Model scope

### Included

- Declining-company classification and explicit separation from mature, cyclical, commodity, young, and still-growing subjects.
- Independent classification of decline reversibility and financial-distress severity.
- Four-quadrant routing for reversible/irreversible decline and low/high distress.
- Current-base normalization after discontinued operations, asset sales, cash depletion, payouts, debt changes, and restructuring events.
- Status-quo declining FCFF paths with negative revenue growth, margin deterioration or recovery, negative reinvestment, invested-capital reduction, and sub-cost returns.
- Divestiture schedules that remove both capital and the disposed assets' future operating contribution while recognizing sale proceeds once.
- Orderly-liquidation comparison for irreversible low-distress cases.
- Separate status-quo and turnaround cases for reversible decline, using a reviewed probability of change supplied through an approved narrative or control input.
- Conditional going-concern valuation and deterministic distress-sale or forced-liquidation value for high-distress cases.
- Explicit probability event, horizon, as-of date, source, and mapping from default evidence to cessation or forced-sale risk.
- Basis-consistent contingent-survival aggregation and one controlled bridge to equity or a named claim.
- Period-specific financing, tax-benefit, leverage, and discount-rate paths that remain conditional on going-concern survival.
- Finite-life, stabilized smaller-company, or reviewed negative-perpetuity closure modes.
- Composition with M1 DCF arithmetic, M2 narrative traceability, M4 forecast consistency, and M3 discrete survival semantics.

### Excluded

- Chapter 11 mature-company acquisition, restructuring, control-probability, voting-right, and LBO engines.
- Cyclical and commodity normalization, which begins in Chapter 13 and belongs to M6 or a later type-specific slice.
- Live financial statements, credit ratings, bond prices, market prices, recovery databases, or market-data ingestion.
- Statistical failure-probability estimation, ratings transition models, Z-scores, probit/logit models, and bond-implied default solvers.
- Monte Carlo simulation, decision trees, modified expected-cash-flow DCF, APV, and equity-as-option valuation.
- Relative valuation and forward-multiple engines.
- Bankruptcy-law prediction, legal advice, debt restructuring optimization, creditor negotiation, and generalized claim waterfalls.
- Preferred-stock liquidation waterfalls, convertible decomposition engines, and management-option valuation.
- Autonomous investment recommendations.
- Modification of M1-M4 public contracts without a separate documented defect and migration.

## Life-cycle and quadrant routing contract

The top-level route is selected before any M5 valuation.

| Condition | Route | Control |
|---|---|---|
| Meets M3 young-company profile | `WFL-YNG-001` | Do not classify short history or losses alone as late-stage decline. |
| Material growth-asset value and clears M3 | `WFL-GRW-001` | Do not force negative-growth mechanics onto a growth company. |
| Stable mature operations without documented decline | `WFL-VAL-001` or later mature-company method | Chapter 11 is not silently imported into M5. |
| Structural or potentially reversible operating decline | `WFL-DST-001` | Record multi-period operating and sector evidence. |
| Primarily cyclical or commodity-driven weakness | Stop and route to M6/later method | Do not label a cycle trough as irreversible decline. |

For a subject admitted to M5, select exactly one quadrant:

| Reversibility | Distress | Required valuation route |
|---|---|---|
| Irreversible | Low | Status-quo going concern versus orderly liquidation; select the higher reviewed alternative, allowing an explicit partial liquidation. |
| Reversible | Low | Status-quo value and separate turnaround value; probability-weight the two using a reviewed change probability. |
| Irreversible | High | Build the irreversible no-distress value, then apply one forced-sale contingent-survival adjustment. |
| Reversible | High | Build a no-distress expected value from status quo and turnaround, then apply one forced-sale contingent-survival adjustment. |

Reversibility evidence includes company recovery history, peer health, management-specific performance, sector structure, and macro cyclicality. Distress evidence includes fixed obligations, debt maturity, refinancing access, liquidity runway, interest coverage, credit quality, and current claim terms. Neither classification may be inferred from one ratio, market price, or label.

## Financial responsibility contract

| Concern | M5 responsibility | Delegated responsibility |
|---|---|---|
| Evidence and business narrative | Require approved assertions for decline, reversibility, obligations, and recovery | `WFL-NAR-001` |
| Base period | Normalize continuing operations, cash, debt, capital, payouts, and completed divestitures | None |
| Status-quo forecast | Produce declining revenue, margins, taxes, reinvestment, capital, ROC, and risk paths | Reuse M4 series controls where compatible |
| FCFF and present value | Emit internally consistent FCFF and period rates | `WFL-VAL-001` |
| Turnaround case | Keep a separately approved operating scenario and change probability | Narrative/control input; no Chapter 11 engine |
| Divestitures | Schedule capital removed, earnings removed, proceeds, timing, and sale conditions | None |
| Orderly liquidation | Value sale program without a forced-sale urgency assumption | None |
| Distress probability | Validate deterministic input, event, horizon, date, and mapping | No estimation engine in M5 |
| Distress-sale value | Apply one reviewed recovery method and expose costs/haircuts | None |
| Contingent survival | Reconcile mutually exclusive probabilities and same-basis values | Reuse M3 expected-value semantics |
| Claims and equity | Inventory current claims and apply one declared bridge | Bounded M1/M3 bridge; no generalized waterfall |

## Required formulas and invariants

### Status-quo declining path

For each explicit year `t`:

```text
revenue[t] = revenue[t-1] * (1 + revenue_growth[t])
operating_income[t] = revenue[t] * operating_margin[t]
after_tax_operating_income[t] = operating_income[t] - cash_tax[t]
invested_capital[t] = invested_capital[t-1] + reinvestment[t]
implied_return_on_capital[t]
= after_tax_operating_income[t] / invested_capital[t-1]
fcff[t] = after_tax_operating_income[t] - reinvestment[t]
```

Negative revenue growth and negative reinvestment are permitted. Negative reinvestment must arise from an identified reduction in capital, depreciation in excess of capital expenditure, working-capital release, or divestiture. It cannot be inserted merely to increase FCFF.

### Divestiture integrity

For every governed divestiture `d`:

```text
net_divestiture_proceeds[d]
= gross_sale_proceeds[d]
- transaction_costs[d]
- taxes_on_sale[d]

remaining_revenue[t]
= pre_sale_revenue[t] - disposed_revenue_contribution[d, t]

remaining_operating_income[t]
= pre_sale_operating_income[t] - disposed_operating_income_contribution[d, t]
```

The same proceeds cannot appear in both negative reinvestment and a separate cash-flow line unless the reconciliation removes the duplicate. The disposed asset's capital and operating contribution must disappear at the correct time. Orderly and forced sales remain distinct.

### No-distress alternative aggregation

For reversible decline:

```text
no_distress_value
= (1 - probability_of_change) * status_quo_value
+ probability_of_change * turnaround_value
```

For irreversible low-distress decline:

```text
selected_no_distress_value
= max(status_quo_going_concern_value, orderly_liquidation_value)
```

An explicit partial-liquidation case may replace the maximum only when it is separately modeled and its retained operations reconcile to the divestiture schedule. Operating inputs from alternatives are never averaged into a hybrid forecast.

### Separate contingent-survival adjustment

High-distress cases use one common basis:

```text
survival_probability + distress_probability = 1

contingent_value
= survival_probability * no_distress_value
+ distress_probability * distress_sale_value
```

Required controls:

- `probability_event` identifies cessation, forced sale, liquidation, or another precisely defined event.
- `probability_horizon` matches the valuation horizon.
- `probability_as_of_date` is not later than the valuation date.
- A default probability cannot be treated as cessation probability without a reviewed mapping.
- `no_distress_value`, `distress_sale_value`, and `contingent_value` share one declared basis: operating assets, firm, equity, or a named claim.
- Cash, debt, senior claims, sale costs, and options are included or deducted exactly once.
- Discrete distress is not added to FCFF losses or discount rates when this separate method is selected.

### Distress-sale methods

Exactly one primary method is selected:

```text
going_concern_haircut:
  distress_sale_value = reference_going_concern_asset_value * (1 - haircut)

existing_asset_value:
  distress_sale_value = present_value(existing_asset_cash_flows_without_growth)

adjusted_book_assets:
  distress_sale_value
  = eligible_book_assets * (1 - economic_impairment) * (1 - forced_sale_discount)
```

Every method exposes the asset perimeter, valuation date, direct sale costs, indirect operating consequences, excluded growth assets, and recovery beneficiary. Book value without an impairment and sale-condition analysis is invalid.

### Risk fade, tax benefits, and discounting

The conditional going-concern rate path may reflect high current financing and operating risk and a reviewed transition if survival includes deleveraging or recovery. It must not include an additional discrete cessation premium.

```text
taxable_operating_income_available[t]
= max(0, operating_income[t])

cash_interest_tax_benefit[t]
= min(cash_interest[t], taxable_operating_income_available[t]) * tax_rate[t]

opening_face_debt[1] = base_period.face_debt
closing_face_debt[t]
= opening_face_debt[t] + debt_issuances[t] - debt_repayments[t]
opening_face_debt[t + 1] = closing_face_debt[t]

capital_value[t] = market_value_debt[t] + market_value_equity[t]
debt_to_capital_ratio[t] = market_value_debt[t] / capital_value[t]
equity_to_capital_ratio[t] = market_value_equity[t] / capital_value[t]

effective_interest_tax_rate[t]
= 0 if cash_interest[t] = 0
  else cash_interest_tax_benefit[t] / cash_interest[t]

after_tax_cost_of_debt[t]
= pretax_cost_of_debt[t] * (1 - effective_interest_tax_rate[t])

cost_of_capital[t]
= equity_to_capital_ratio[t] * cost_of_equity[t]
+ debt_to_capital_ratio[t] * after_tax_cost_of_debt[t]

cumulative_discount_denominator[t]
= product(1 + cost_of_capital[i]) for i = 1..t

present_value[t] = fcff[t] / cumulative_discount_denominator[t]
```

`cash_interest[t]` is a nonnegative, dated contractual cash-obligation input and must map to the debt schedule and evidence. `taxable_operating_income_available[t]` is a derived nonnegative series; a loss therefore produces no negative tax benefit. `capital_value[t]` must be positive, both market-value capital components must be nonnegative, and the two capital weights must sum to one within tolerance. Every `financing_path` series must align one-for-one with `status_quo_forecast.years`, and `status_quo_forecast.discount_rates[t]` must equal `financing_path.costs_of_capital[t]` exactly.

Book interest rates, book capital weights, unsupported negative market equity, and a healthy target debt ratio applied from year one are prohibited without a documented reconciliation. The validator must roll face debt forward, recompute capital weights, tax benefits, effective tax rates, after-tax debt costs, and costs of capital from the governed inputs. This financing path is part of the conditional going-concern case; it does not add a separate cessation premium.

### Terminal or closure state

Exactly one mode is selected:

- `finite_life`: all remaining operating cash flows and closure proceeds are explicitly valued; no perpetuity is added.
- `stabilized_smaller_company`: revenue decline ends at a reviewed point and the M4 stable-state rebuild applies.
- `negative_perpetuity`: a reviewed negative nominal growth rate remains above `-1`, is below the terminal cost of capital, and describes a viable indefinitely shrinking business.

`closure` belongs only to the status-quo going-concern valuation. A full `orderly_liquidation` is a separate conditional alternative, never a `closure.mode`. When the irreversible/low-distress route compares the two, the status-quo case still uses exactly one of the three modes above; the orderly-liquidation object separately reconciles all sale proceeds and retained operations. If orderly liquidation is selected, its value replaces the status-quo alternative only after both have been computed, and no terminal value may remain inside the full-liquidation alternative. A partial liquidation is modeled as governed divestitures within a retained going concern, not as a fourth closure mode.

Any terminal FCFF is rebuilt from the terminal operating state, return on capital, and reinvestment. Crisis-level discount rates, current leverage, and expiring tax losses cannot be frozen into perpetuity without evidence.

## Schema contract

The M5 implementation will add `schemas/decline-distress-valuation.schema.json` with `additionalProperties: false` at every governed object.

| Object | Required fields |
|---|---|
| Root | `schema_version`, `id`, `narrative_id`, `as_of_date`, `subject`, `currency`, `decline_profile`, `routing`, `base_period`, `status_quo_forecast`, `financing_path`, `closure`, `going_concern`, `traceability`, `limitations`, `review` |
| `decline_profile` | `classification`, `m4_boundary_cleared`, `decline_evidence`, `sector_condition`, `reversibility`, `reversibility_reasoning`, `evidence_refs` |
| `routing` | `distress_level`, `quadrant`, `distress_reasoning`, `fixed_obligation_evidence_refs`, `route_approved` |
| `base_period` | `period_end`, `staleness_days`, `continuing_revenues`, `continuing_operating_income`, `cash`, `book_debt`, `market_debt`, `face_debt`, `invested_capital`, `fixed_obligations`, `normalization_adjustments`, `evidence_refs` |
| `status_quo_forecast` | `years`, `revenue_growth_rates`, `revenues`, `operating_margins`, `operating_incomes`, `tax_rates`, `cash_taxes`, `after_tax_operating_incomes`, `reinvestments`, `invested_capital`, `implied_returns_on_capital`, `discount_rates`, `assumption_trace` |
| `financing_path` | `opening_face_debt`, `debt_issuances`, `debt_repayments`, `closing_face_debt`, `cash_interest`, `taxable_operating_income_available`, `cash_interest_tax_benefits`, `market_value_debt`, `market_value_equity`, `debt_to_capital_ratios`, `equity_to_capital_ratios`, `pretax_costs_of_debt`, `effective_interest_tax_rates`, `after_tax_costs_of_debt`, `costs_of_equity`, `costs_of_capital`, `assumption_trace` |
| `closure` | `mode`, `closure_year`, `terminal_growth_rate`, `terminal_return_on_capital`, `terminal_reinvestment_rate`, `terminal_cost_of_capital`, `supporting_refs` |
| `going_concern` | `engine`, `fcff`, `cumulative_discount_factors`, `forecast_present_value`, `terminal_or_closure_value`, `terminal_or_closure_present_value`, `operating_asset_value`, `calculation_trail` |
| `traceability` | `source_refs`, `claim_refs`, `narrative_assertion_refs` |
| `review` | `status`, `reviewer`, `reviewed_at`, `classification_approved`, `quadrant_approved`, `divestiture_approved`, `probability_approved`, `basis_approved`, `risk_separation_approved`, `closure_approved` |

Conditional governed objects:

- `divestitures`: required when reinvestment or capital removal includes sale proceeds; asset IDs, timing, capital removed, operating contributions removed, gross/net proceeds, costs, taxes, sale condition, method, and double-count reconciliation.
- `turnaround_case`: required for reversible decline; separate valuation ID, operating changes, value, change probability, probability basis, and no-input-averaging attestation.
- `orderly_liquidation`: required for every irreversible low-distress comparison; asset perimeter, schedule, proceeds, retained operations, urgency assessment, value, and selection result. It is forbidden in every other quadrant and cannot also appear as `closure.mode`.
- `distress_case`: required for high distress; event, horizon, probability date/source/mapping, probabilities, recovery method, distress-sale value, aggregation basis, components, calculation trail, and double-count attestations.
- `claim_bridge`: required when the aggregation basis is not already common equity; cash, debt, senior claims, hybrid claims, option claims, basis date, and per-claim or per-share result.

The validator must recompute every derived numeric series from governed inputs, including the financing roll-forward, leverage weights, interest-tax-benefit path, divestiture reconciliation, alternative-value weight, probability component, distress-sale method, claim bridge, terminal or closure amount, and calculation-trail step. It must validate each non-derived numeric input against its declared bounds, dated evidence, and bidirectional traceability. It must reject unknown or one-way traceability, inconsistent bases, stale claims, probability/event mismatches, retained disposed earnings, duplicated proceeds, hidden book-value proxies, risk double counting, merged alternatives, and undeclared properties.

## Workflow contract

`WFL-DST-001` executes in this order:

1. Receive one approved `WFL-NAR-001` narrative and driver map.
2. Confirm documented decline and clear the M3, M4, mature, and cycle-driven boundaries.
3. Normalize continuing operations, cash, capital, debt, and completed restructuring events to the valuation date.
4. Classify reversibility and distress independently; select one quadrant.
5. Build the status-quo decline forecast and closure mode.
6. Reconcile negative reinvestment, divestitures, retained operations, and FCFF.
7. Build conditional going-concern discount rates, tax benefits, and leverage path.
8. Delegate FCFF and cumulative DCF arithmetic to `WFL-VAL-001`.
9. If reversible, value a separate turnaround case and compute the no-distress expected value.
10. If irreversible and low distress, value orderly liquidation and select the higher reviewed alternative or an explicit partial-liquidation case.
11. If high distress, validate the event/horizon probability and distress-sale value, then apply M3-compatible contingent-survival arithmetic once.
12. Reconcile values on a common basis and apply the selected claim bridge exactly once.
13. Return classification, probability, recovery, and value-driver findings to the M2 feedback revision loop.

Each materially different reversibility view, turnaround path, probability event, recovery method, or claim structure remains a separate valuation object. The engine must not average alternatives.

## Risk-placement contract

| Risk or effect | Placement | Prohibited duplicate |
|---|---|---|
| Structural market decline | Revenue and closure path | Arbitrary post-valuation haircut |
| Margin erosion and operating failure | Margin and FCFF scenarios | Hidden distress discount |
| Value-destroying reinvestment | Reinvestment and implied ROC | Unsupported positive-growth recovery |
| Divestiture | Capital/earnings removal and net proceeds | Sale proceeds with retained earnings |
| Continuous operating and financing risk | Period-specific conditional going-concern rates | Healthy rate from year one |
| Lost tax benefits | Period cash taxes and after-tax debt cost | Full marginal shield during losses |
| Management or policy change | Separate turnaround value and change probability | Averaged operating inputs |
| Discrete cessation or forced sale | One contingent-survival adjustment | Failure loss in FCFF or rate premium |
| Recovery impairment and sale urgency | Distress-sale method | Second post-valuation recovery haircut |
| Claim priority and dilution | One dated claim bridge | Book debt proxy or repeated deduction |

## Synthetic benchmark design

### Benchmark A - Orderly wind-down of a legacy distributor

Purpose: test irreversible decline with low distress and a multi-year orderly divestiture program.

- Five-year explicit forecast with negative revenue growth and modest margin improvement as weak locations close.
- Negative reinvestment tied to identified asset sales and working-capital release.
- Capital removed, revenue lost, operating income lost, and net sale proceeds reconcile by asset and year.
- Status-quo operations earn below the cost of capital.
- No material fixed-obligation or refinancing threat.
- Compare the status-quo going-concern value with an orderly-liquidation value and select the higher result.
- Closure uses a smaller stabilized company or finite-life mode, not an overlapping liquidation value and perpetuity.
- M1 equity bridge with current cash and debt.

Required assertions include exact divestiture recomputation, no proceeds/earnings double count, value-basis consistency, and a documented selection between continuing and liquidation.

### Benchmark B - Reversible but highly levered service operator

Purpose: test reversible decline with high distress and two sequential contingent gates.

- A status-quo declining valuation and a separately valued turnaround scenario based on synthetic healthy peers.
- A reviewed probability of management or policy change creates the no-distress expected value.
- Current debt, fixed obligations, depleted cash, interest tax benefits, and a survival-consistent deleveraging path are explicit.
- A deterministic forced-sale probability states cessation event, horizon, date, and synthetic evidence basis.
- Distress-sale value uses existing-asset earnings power with explicit direct costs and no growth assets.
- The no-distress and forced-sale values are converted to the same firm basis before probability weighting.
- The common-equity bridge is applied once after contingent firm value and floors limited-liability equity at zero only where the selected claim basis requires it.

Required assertions include probability reconciliation, default-versus-cessation mapping, no operating-input averaging, no distress-rate double count, and current claim-inventory consistency.

### Adversarial cases

- One weak year misclassified as structural decline.
- A cyclical trough classified as irreversible decline.
- Positive growth and healthy margins inserted without a separate turnaround scenario.
- Negative reinvestment with no capital reduction or divestiture evidence.
- Sale proceeds retained while disposed earnings remain in the forecast.
- Book asset value used directly as liquidation value.
- Book debt or a stale claim inventory used for the equity bridge.
- Full interest tax shield during periods without taxable operating income.
- A debt balance, capital weight, tax benefit, or cost-of-capital series altered without changing its governed inputs.
- Current crisis discount rate frozen into the terminal state.
- Perpetual terminal value retained after complete liquidation.
- Full orderly liquidation encoded as `closure.mode` instead of a separate alternative.
- Default probability used as cessation probability without a mapping.
- Probability horizon shorter than the valuation horizon.
- Going-concern operating value mixed with distress equity value.
- Debt or cash deducted in both scenario values and the final bridge.
- Distress embedded in forecast cash flows, discount rates, and contingent-survival probability.
- Status-quo and turnaround inputs averaged into one forecast.
- M3/M4/M5 top-level workflows applied to the same operating narrative.
- Relative, APV, simulation, or option outputs stacked onto M5 intrinsic value.

## Acceptance criteria

M5 implementation is complete only when all of the following pass:

- All 32 `CLM-DST-*` claims are maintainer-reviewed and mapped to M5 Knowledge artifacts.
- The extraction manifest and source-map relationships validate without private-source content.
- The new schema loads under JSON Schema 2020-12 and rejects undeclared properties.
- The validator independently recomputes base normalization, forecast series, financing roll-forward, leverage weights, interest tax benefits, after-tax debt costs, costs of capital, divestitures, negative reinvestment, invested capital, implied ROC, FCFF, cumulative discount factors, terminal or closure value, alternative aggregation, distress-sale value, contingent-survival components, claim bridge, and audit trail.
- Both deterministic benchmarks match committed expected outputs within documented tolerances.
- Every adversarial case fails for the intended reason.
- M1-M4 artifact, benchmark, and regression tests remain unchanged in behavior and pass.
- The complete suite passes on Python 3.10 and Python 3.12.
- Repository policy reports no PDFs, raw extracts, copied tables/figures, sequential source text, or long quotations.
- A human reviewer completes `templates/m5-decline-distress-review-checklist.md`.

## Stop conditions

Stop implementation or valuation for an uncleared life-cycle boundary, unsupported decline or reversibility classification, missing fixed-obligation evidence, stale base or claim inventory, unselected quadrant, merged status-quo and turnaround inputs, unexplained negative reinvestment, divestiture double counting, unsupported liquidation/book-value proxy, probability event or horizon mismatch, default-to-cessation substitution, inconsistent valuation bases, repeated claim deduction, loss tax shield, distress-risk double counting, overlapping closure and terminal value, imported excluded method, or private source content.

## Approved implementation baseline

The FVI maintainers approved the following items on 2026-08-02:

1. Chapter 12 printed pages 397-436 / PDF pages 445-484 as the exact M5 boundary.
2. The executable, composition-only, and excluded section split.
3. All 32 atomic claims and source locations.
4. The life-cycle boundary and four-quadrant routing rule.
5. The separate contingent-survival method as M5's only distress placement.
6. The common-basis, one-bridge, and probability event/horizon invariants.
7. The schema field contract, workflow order, and risk-placement rules.
8. The two deterministic benchmark designs and adversarial cases.
9. The acceptance criteria and M1-M4 no-regression requirement.

Codex may implement the repository-wide M5 artifact graph, engine, validator, schema, fixtures, expected outputs, tests, and documentation on a separate feature branch. Live data ingestion, statistical distress estimation, and excluded valuation engines remain outside the approved scope.
