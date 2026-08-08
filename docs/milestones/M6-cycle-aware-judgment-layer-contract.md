# M6 Cycle-Aware Judgment Layer - Milestone Contract

Status: Approved for implementation
Contract version: 1.0.0
Primary methodology source: `SRC-DAMODARAN-DARK-SIDE-2018`
Primary judgment source: `SRC-MARKS-MASTERING-MARKET-CYCLE-2018`
Proposed workflow: `WFL-CYC-001`
Proposed schema: `schemas/cycle-aware-judgment.schema.json`

## Decision

M6 is a bounded cycle-aware layer for intrinsic valuation work. It prevents a peak or trough observation from being mistaken for a permanent operating state, selects one governed treatment for cyclical or commodity-sensitive inputs, and records a separate market-cycle judgment overlay based on dated evidence.

M6 does not predict exact turning points. It does not replace company valuation with a market-cycle score. It does not issue a buy, sell, leverage, or position-size instruction. Its two outputs remain distinct:

1. a `valuation_input_handoff` that supplies cycle-consistent operating and risk inputs to an existing intrinsic-value workflow; and
2. a `judgment_overlay` that describes the observed market climate, confidence, counterevidence, and a bounded human-review posture without modifying intrinsic value.

This contract was approved by the FVI maintainers on 2026-08-02 and is the locked baseline for M6 implementation. Implementation must remain within this contract or document any proposed contract amendment separately.

## Source boundary

### Methodology source

The valuation-method boundary is Chapter 13, "Ups and Downs: Cyclical and Commodity Companies," printed pages 438-458 and PDF pages 486-506 in the reviewed private edition.

| Treatment | Sections | Printed pages |
|---|---|---:|
| Executable M6 method | Classification, valuation issues, normalization, current expectations, deterministic scenarios | 438-450 |
| Composition boundary | Scenario ranges and driver-to-financial mapping | 450 |
| Excluded implementation | Monte Carlo example, relative valuation, natural-resource real options | 450-458 |
| Summary support | Chapter conclusion | 458 |

### Judgment source

The judgment boundary uses selected chapters of *Mastering the Market Cycle* in the reviewed private edition.

| Treatment | Chapters | PDF pages |
|---|---|---:|
| Cycle nature and limits | I-III | 13-44 |
| Profit, psychology, risk-attitude, and credit evidence | VI-IX | 69-149 |
| Market-cycle synthesis and present-condition assessment | XII-XIII | 170-227 |
| Posture continuum and limits | XIV-XV | 228-250 |
| Summary cross-check only | XVIII | 272-291 |

Chapters IV-V do not authorize a macroeconomic or policy-forecasting engine. Chapters X-XI do not replace M5 distress mechanics or create a real-estate valuation method. Chapters XVI-XVII do not add an executable M6 control. Chapter XIV supports a review-posture continuum only; portfolio allocation remains excluded.

The extraction manifest is `extraction/manifests/M6-cycle-aware-judgment-layer.yaml`. The 36 reviewed atomic claims are in `extraction/reviewed/M6-cycle-aware-judgment-layer-claims.yaml`.

## Model scope

### Included

- Company-level classification as economic-cycle exposed, commodity-price exposed, mixed, or unsupported.
- Separation of firm-specific weakness, structural decline, ordinary growth/maturity, and cycle-driven volatility.
- Classification of the governing cycle as established and recurring, unstable, structurally broken, or insufficiently evidenced.
- A dated evidence ledger spanning economic conditions, company profit behavior, psychology and valuation, risk attitude, and credit conditions.
- Explicit supporting and contradicting evidence, staleness controls, confidence rules, and an `indeterminate` result.
- One selected valuation treatment: full-input normalization, current-to-normal transition, current-expectations driver path, or stop.
- Scale-aware historical normalization, sector normalization with company adjustments, and commodity-driver normalization.
- Consistent treatment of revenue, margins, reinvestment, capital, returns, leverage, financing cost, and closure assumptions.
- A deterministic scenario range for material driver uncertainty; probability weighting only when probabilities are separately reviewed and reconciled.
- Price-to-intrinsic-value comparison as one market-cycle observation, not as a replacement for valuation.
- A bounded `defensive_review`, `balanced_review`, `opportunity_review`, or `insufficient_evidence` posture for human review.
- Composition with M2 evidence and narrative, M1 DCF arithmetic, M4 forecast-series controls, M5 distress and forced-sale treatment, and M2 feedback revision.

### Excluded

- Exact peak, trough, recession, recovery, or commodity-price timing forecasts.
- A macroeconomic forecasting engine, econometric regime model, hidden composite score, or machine-learned cycle classifier.
- Live economic, market, credit, futures, company, or alternative-data ingestion.
- Autonomous investment recommendations, trade instructions, portfolio weights, leverage targets, hedging orders, or execution.
- Monte Carlo simulation, statistical scenario-probability estimation, derivatives valuation, or current-price hedging implementation.
- Relative valuation, precedent transactions, natural-resource real options, and generalized option valuation.
- A new distress probability, recovery, liquidation, or claim-waterfall method; these remain governed by M5.
- Using psychology, sentiment, credit, or market-price labels as an unexplained DCF haircut or discount-rate premium.
- Treating a sector label, single weak period, single valuation multiple, single spread, or one narrative adjective as sufficient cycle evidence.
- Private-source text, copied tables or figures, and historical examples in public fixtures.

## Boundary and routing contract

### Subject classification

`subject_classification.exposure_type` must be exactly one of:

- `economic_cycle`
- `commodity_price`
- `mixed_cycle`
- `not_supported`

The classification must identify the external driver, the company financial series linked to it, the observation window, and both supporting and contradicting evidence. An industry label alone cannot select an exposure type. A commodity consumer with input-cost sensitivity is not silently treated as a commodity producer; its driver-to-margin mapping must be explicit.

Before M6 proceeds, the subject must clear the existing life-cycle boundaries:

| Observed condition | Required route | Prohibited shortcut |
|---|---|---|
| Young company with sparse operating history | M3 first | Fabricated full-cycle average |
| Still-scaling growth company | M4 with bounded M6 driver handoff | Replacing scale economics with a cycle label |
| Structural or potentially reversible decline | M5 first | Calling irreversible decline a trough |
| Mature company with material cycle exposure | M6 | Using the latest fiscal year unchanged |
| Cycle exposure plus material distress | M6 operating basis, then M5 distress handoff | Cycle haircut plus separate distress probability |
| No supported cycle exposure | M1 or the applicable life-cycle workflow | Forced M6 normalization |

### Regime assessment

`cycle_assessment.regime` must be one of:

- `established_recurring`: a sufficiently representative history supports a recurring driver and a defensible midpoint or normalized state;
- `unstable`: the driver remains relevant but cycle length, amplitude, or current anchor is too unstable for a historical normal;
- `structural_break`: technology, demand, supply, regulation, cost structure, or another durable change invalidates the prior normalization regime;
- `insufficient_evidence`: the evidence cannot support a governed treatment.

`established_recurring` requires a documented full-cycle window or a defensible sector window that contains both strong and weak conditions. `structural_break` requires a named break hypothesis, date or interval, mechanism, affected inputs, and counterevidence. A large price move by itself is not a structural break.

`company_cycle_position` may be `trough`, `below_midpoint`, `midpoint`, `above_midpoint`, `peak`, or `indeterminate`. This is an as-of classification, not a forecast of the next turning date.

### Treatment routing

Exactly one `valuation_treatment.mode` is selected:

| Regime and evidence | Permitted mode | Required behavior |
|---|---|---|
| Established recurring, representative full-cycle data | `normalized_inputs` | Replace all cycle-sensitive inputs with one consistent normalized state. |
| Established recurring, current state materially away from normal | `transition_to_normal` | Start from the current base and converge once to a documented normalized anchor. |
| Unstable or structural break | `current_expectations` | Use a dated reviewed driver path and disclose uncertainty through deterministic scenarios. |
| Insufficient evidence | `stop` | Return missing evidence and no valuation-input handoff. |

`normalized_inputs` and `transition_to_normal` cannot be applied to the same operating series. `current_expectations` cannot include a hidden historical-normal terminal anchor unless the break assessment separately supports it.

## Evidence contract

### Evidence ledger

Each evidence item requires:

- `evidence_id`
- `dimension`
- `indicator_name`
- `observation`
- `unit`
- `as_of_date`
- `window_start` and `window_end` where a history is used
- `source_ref`
- `direction`
- `strength`
- `supports`
- `limitations`

`dimension` must be one of `economic`, `company_profit`, `psychology_valuation`, `risk_attitude`, or `credit`. Each dimension must appear in the document with either one or more evidence items or an explicit `not_available` record. Missing data is never silently treated as neutral.

Every evidence date must be on or before `valuation_date`. A declared `evidence_staleness_policy.max_age_days` applies to point observations. Stale evidence remains visible but cannot support a current extreme or high-confidence classification.

Every cycle or posture conclusion requires at least one `supporting_evidence_ref` and one `counterevidence_ref` or an explicit statement that no material counterevidence was found after a named search. The latter is a human review statement, not proof that counterevidence does not exist.

### Ordinal signals

Each available dimension receives an ordinal `signal` of `deep_negative`, `negative`, `neutral`, `positive`, or `excess_positive`. The meaning is dimension-specific and must be declared in `signal_definition`; M6 does not add the five signals into a universal numeric score.

Each `dimension_assessment` must also declare `availability`, `signal`, `signal_definition`, `band_implication`, `evidence_refs`, `stale_evidence_refs`, `counterevidence_refs`, and `limitations`. `band_implication` uses the market-overlay order `extreme_low`, `below_midpoint`, `midpoint`, `above_midpoint`, `extreme_high`, or `indeterminate`. It is a reviewed categorical translation from that dimension's declared signal definition, not a numeric conversion. An unavailable dimension must use `signal: neutral` only as a serialization placeholder and `band_implication: indeterminate`; it cannot count as aligned evidence.

For confidence testing, two available dimensions are aligned when their `band_implication` values are the selected market band or an immediately adjacent band in the stated order. `indeterminate` is never adjacent to a directional band. A dimension with an opposing extreme, unresolved strong counterevidence, or only stale supporting evidence cannot count as aligned. The validator must recompute the alignment count from the governed dimension assessments rather than accept a reported count.

The market overlay may use `extreme_low`, `below_midpoint`, `midpoint`, `above_midpoint`, `extreme_high`, or `indeterminate`:

- An extreme requires non-stale price-to-value evidence, non-stale credit evidence, and at least one aligned psychology or risk-attitude item.
- A high-confidence position requires all five dimensions to be available, at least four to align within the selected band or an adjacent band, and no unresolved strong contradiction.
- A medium-confidence position requires at least three non-stale dimensions and at least three aligned observations.
- All other supported conclusions are low confidence; unresolved opposing extremes require `indeterminate`.

These are governance thresholds, not statistical probabilities.

## Valuation-input contract

### Current base

The governed current base must state valuation date, reporting period, currency, continuing operations, current driver value, revenue, operating margin, operating income, reinvestment, invested capital, return on capital, cash, debt, and material fixed obligations. Completed disposals, acquisitions, restructurings, and accounting discontinuities must be reconciled before any cycle treatment.

### Full-input normalization

`normalized_inputs` requires:

- a `normalization_window` covering the selected full cycle or sector cycle;
- a selected method for each input;
- the raw governed observations used by the method;
- scale and business-mix adjustments;
- the normalized value and calculation trail; and
- limitations and counterevidence.

Permitted methods include `absolute_historical_average`, `relative_historical_average`, `sector_average_with_adjustment`, and `normalized_external_driver`. Each use must satisfy its own boundary:

- An absolute average is prohibited when material scale or business-mix change makes levels incomparable.
- A relative average must name its denominator and apply the normalized ratio to a current reconciled scale.
- A sector average must document comparability and preserve a separate company-specific efficiency adjustment.
- A normalized external driver must map the driver to company revenue, costs, margins, reinvestment, and financing effects.

For a margin-based method:

```text
normalized_operating_income
= reconciled_reference_revenue * normalized_operating_margin
```

If stable growth uses a return-based reinvestment method:

```text
normalized_reinvestment_rate
= normalized_growth_rate / normalized_return_on_capital
```

The implementation must recompute the full vector. It must not normalize operating income while retaining peak or trough reinvestment, leverage, funding cost, or return assumptions.

### Current-to-normal transition

`transition_to_normal` begins with the reconciled current base and ends at exactly one approved normalized anchor. The series must declare transition length, endpoint, and driver-to-financial mapping for revenue, margin, reinvestment, capital, returns, leverage, and financing cost.

The path represents convergence from the observed state to normal. It cannot encode multiple predicted booms and recessions. A trough recovery or peak contraction can appear either in the transition series or in the starting-level normalization, never both.

### Current expectations

`current_expectations` requires a dated `driver_curve` whose points identify date or period, value, unit, source type, as-of date, and source reference. Source type must be one of `spot`, `forward_or_futures`, `survey_or_consensus`, or `reviewed_assumption`.

For a storable commodity, a forward or futures curve must disclose that cost-of-carry, including storage and financing, can drive the curve. It cannot be labeled an independent fundamental forecast without separate evidence.

Each driver point must map to operating inputs through a transparent relationship or reviewed lookup. A change to the driver must recompute every linked revenue, cost, margin, reinvestment, return, and financing item in each affected period.

### Deterministic scenarios

Scenarios may expose uncertainty in a normalized anchor, transition length, driver curve, margin sensitivity, or funding response. Each scenario is a complete isolated input set with one intrinsic valuation result.

Scenario probabilities are optional. If supplied, they require an as-of date, event definition, horizon, provenance, and sum to one within tolerance. Without approved probabilities, M6 reports a range and does not manufacture an expected value. Monte Carlo draws and statistically estimated distributions remain excluded.

## Judgment-overlay contract

The overlay must declare:

- `market_cycle_position`
- `confidence`
- `dimension_assessments`
- `supporting_evidence_refs`
- `counterevidence_refs`
- `price_value_observation`
- `review_posture`
- `invalidation_conditions`
- `limitations`

`review_posture` is deterministically bounded:

| Position | Required posture |
|---|---|
| `extreme_high` | `defensive_review` |
| `extreme_low` | `opportunity_review` |
| Middle bands | `balanced_review` |
| `indeterminate` or insufficient evidence | `insufficient_evidence` |

These labels are prompts for a human review. They do not authorize buying, selling, leverage, hedging, timing, or portfolio sizing. The overlay never changes the intrinsic-value result. A later decision process may consume the overlay only through a separately approved workflow.

## Risk-placement and double-counting contract

| Exposure | Correct placement | Prohibited duplicate |
|---|---|---|
| Current peak or trough | One selected normalization or transition treatment | Normalized start plus recovery or contraction counted again |
| Commodity driver | Driver curve and complete operating mapping | Driver view plus unsupported valuation haircut |
| Continuous operating sensitivity | Revenue, margin, reinvestment, and return paths | Psychology label added to FCFF |
| Financing conditions | Governed leverage and cost-of-funding path | Credit posture plus a second arbitrary rate premium |
| Discrete distress or forced sale | WFL-DST-001 only | M6 distress score plus M5 probability |
| Market psychology and risk attitude | Judgment overlay evidence | Direct DCF input with no financial bridge |
| Price relative to value | Post-valuation observation | Market price used to manufacture intrinsic value |
| Scenario uncertainty | Separate complete scenario values | Scenario probability and the same uncertainty in discount rates |

M6 can map observed credit conditions to a period-specific financing input only when the document supplies the financial relationship, basis, and evidence and the downstream workflow independently recomputes it. A qualitative label alone has no numeric effect.

## Composition contract

```text
WFL-NAR-001 evidence and narrative
-> M6 subject and regime classification
-> M6 dated five-dimension evidence ledger
-> exactly one valuation treatment
-> WFL-VAL-001 and bounded WFL-GRW-001 series controls
-> optional WFL-DST-001 distress handoff
-> intrinsic value
-> M6 judgment overlay and review posture
-> WFL-NAR-001 feedback revision
```

- M2 owns narrative assertions, evidence traceability, alternatives, and revisions.
- M1 owns FCFF discounting, terminal arithmetic, enterprise-to-equity bridge, and per-share value.
- M4 owns reusable forecast-series, reinvestment, capital, return, risk-fade, and stable-state consistency controls; M6 does not apply growth-company classification to mature cyclicals.
- M5 exclusively owns discrete distress, forced-sale value, contingent survival, and current-claim bridge controls.
- M6 owns the choice and audit trail for cycle treatment and the separate non-numeric market judgment overlay.

## Schema contract

The M6 schema must reject undeclared properties and require these top-level objects:

- `schema_version`
- `judgment_id`
- `valuation_id`
- `valuation_date`
- `company`
- `narrative_id`
- `subject_classification`
- `current_base`
- `evidence_staleness_policy`
- `cycle_evidence`
- `cycle_assessment`
- `valuation_treatment`
- `valuation_input_handoff`
- `intrinsic_value_reference`
- `judgment_overlay`
- `risk_controls`
- `calculation_trail`
- `limitations`
- `review`

The schema and independent validator must enforce at least these cross-field invariants:

1. All evidence and driver-curve dates are on or before `valuation_date` unless explicitly labeled as a future period sourced from a dated curve.
2. Future curve points retain an `as_of_date` on or before `valuation_date`.
3. All five evidence dimensions appear as available or explicitly unavailable.
4. Stale or unavailable evidence cannot support high confidence or an extreme.
5. Every conclusion reference resolves bidirectionally to one evidence item.
6. `not_supported` exposure and `insufficient_evidence` regime require `valuation_treatment.mode: stop`.
7. `normalized_inputs` requires `established_recurring` and a representative normalization window.
8. `transition_to_normal` begins at the current base and ends at one normalized anchor.
9. `current_expectations` is required for `unstable` or `structural_break` unless the document stops.
10. Exactly one valuation-treatment payload is present.
11. Normalized and current values preserve units, currency, and valuation basis.
12. Every normalized input recomputes from its governed method and observations.
13. Every driver-curve point recomputes all linked financial inputs.
14. Recovery growth is not applied to an already normalized starting level.
15. Scenario documents isolate their complete input sets and do not share mutable calculation trails.
16. Scenario probabilities, when present, reconcile to one and use one defined event and horizon.
17. An extreme market position satisfies the multi-dimension evidence threshold.
18. `review_posture` is the deterministic mapping from `market_cycle_position`.
19. `intrinsic_value_reference` is unchanged by the judgment overlay.
20. Any material distress handoff resolves to WFL-DST-001 and no M6 field applies a second distress adjustment.

## Workflow design

`WFL-CYC-001` should compose ten bounded Skills in this order:

1. `SKL-CYC-001` - classify cycle exposure and clear life-cycle boundaries.
2. `SKL-CYC-002` - reconcile the dated current operating and financing base.
3. `SKL-CYC-003` - build the five-dimension evidence ledger and staleness record.
4. `SKL-CYC-004` - assess recurrence, structural break, position, and confidence.
5. `SKL-CYC-005` - select exactly one valuation treatment.
6. `SKL-CYC-006` - normalize the full input vector or construct the transition path.
7. `SKL-CYC-007` - build a current-expectations driver path and deterministic scenarios.
8. `SKL-CYC-008` - hand off to intrinsic valuation and optional M5 distress treatment.
9. `SKL-CYC-009` - create the separate judgment overlay and bounded review posture.
10. `SKL-CYC-010` - run independent review, return findings, and trigger narrative revision.

No implementation Skill may combine treatment selection, intrinsic valuation, and posture assignment into an opaque single score.

## Synthetic benchmark design

### Benchmark A - Established-cycle industrial at a trough

Purpose: prove that a cyclical trough is normalized without being misclassified as structural decline or double-counted as recovery.

- Synthetic mature industrial company with ten years covering strong and weak economic conditions.
- Company revenue and operating margin show material but non-identical correlation with the external cycle.
- Current year is a trough with low margin, reduced reinvestment, conservative credit conditions, and low distress.
- Regime is `established_recurring`; treatment is `transition_to_normal`.
- The transition begins at current continuing operations and converges once to a scale-adjusted historical margin and complete normalized reinvestment and financing state.
- No separate recovery premium is added to normalized earnings.
- M1 performs the DCF; M5 is not invoked.
- Synthetic market evidence is pessimistic but mixed, producing `below_midpoint` and `balanced_review`, not an automatic opportunity label.

Required assertions include life-cycle routing, representative-window coverage, scale-adjusted normalization, complete input recomputation, one convergence path, no growth double count, dated evidence, and unchanged intrinsic value after the overlay.

### Benchmark B - Commodity producer after a structural break

Purpose: prove that a broken historical normal is rejected and current expectations remain separate from market posture and distress.

- Synthetic mature commodity producer with an old high-price regime and a documented demand-and-cost break.
- Regime is `structural_break`; historical normalized price treatment must be rejected.
- Treatment is `current_expectations` using a dated synthetic spot and forward curve with the storable-commodity carry limitation disclosed.
- Low, base, and high deterministic driver scenarios map independently to volume, revenue, margin, reinvestment, return, and financing inputs.
- No scenario probability is supplied, so the output is a value range without expected-value aggregation.
- Broad market credit is abundant and aligned with the market overlay, while issuer-specific leverage, liquidity, and refinancing weakness create a separately documented WFL-DST-001 handoff; M6 applies no distress haircut.
- Elevated optimism, broad credit availability, and price above intrinsic value align across the required dimensions, producing an `extreme_high` / `defensive_review` overlay.

Required assertions include structural-break evidence, prohibition of the historical normal, curve dating, full driver mapping, scenario isolation, no probability invention, one M5 handoff, extreme-evidence thresholds, and no overlay effect on intrinsic value.

### Adversarial cases

- One weak quarter or an industry label selects M6. **Expected rejection:** unsupported company-specific exposure and observation window.
- A young company without a full history is normalized from a fabricated cycle. **Expected rejection:** uncleared M3 boundary and nonrepresentative normalization history.
- Structural decline is relabeled as a temporary trough. **Expected rejection:** unresolved M5 routing conflict.
- A structural break is declared from price movement alone. **Expected rejection:** missing mechanism, date, affected-input mapping, and counterevidence.
- An absolute earnings average ignores a material scale change. **Expected rejection:** incomparable historical levels without scale adjustment.
- A sector margin is used without company comparability or efficiency adjustment. **Expected rejection:** unsupported sector-normalization bridge.
- Operating income is normalized while reinvestment, leverage, and funding cost remain at a peak or trough. **Expected rejection:** mixed cycle states in the normalized input vector.
- Normalized trough earnings also receive a recovery growth path. **Expected rejection:** duplicated recovery effect.
- `normalized_inputs` and `transition_to_normal` coexist. **Expected rejection:** multiple treatment payloads.
- A current-expectations case silently returns to the invalid old normal. **Expected rejection:** unsupported terminal anchor after instability or structural break.
- A storable commodity futures curve is labeled a pure forecast with no carry disclosure. **Expected rejection:** missing curve-composition limitation.
- A future curve point has an as-of date later than the valuation date. **Expected rejection:** forward-looking information leakage.
- A driver change fails to update one linked financial input. **Expected rejection:** incomplete driver-to-financial recomputation.
- Scenarios share one mutated calculation trail. **Expected rejection:** non-isolated scenario state.
- An expected value is reported without approved probabilities. **Expected rejection:** invented probability weighting.
- Probabilities use different events or horizons or do not sum to one. **Expected rejection:** unreconciled probability basis.
- One sentiment word, valuation multiple, or credit spread determines an extreme. **Expected rejection:** insufficient multi-dimension evidence.
- Stale evidence supports a high-confidence extreme. **Expected rejection:** staleness-policy breach.
- Contradictory dimensions produce a confident directional posture. **Expected rejection:** unresolved opposing evidence and recomputed alignment failure.
- A hidden numeric score replaces the evidence matrix. **Expected rejection:** prohibited opaque aggregation.
- Market psychology directly changes FCFF or WACC. **Expected rejection:** missing governed financial bridge and overlay contamination.
- Market price is embedded in intrinsic-value inputs. **Expected rejection:** price-to-value ordering violation.
- `judgment_overlay` changes `intrinsic_value_reference`. **Expected rejection:** intrinsic-value immutability violation.
- `opportunity_review` is rendered as a buy instruction or position size. **Expected rejection:** prohibited autonomous decision output.
- Cycle stress is included in both M6 rates and M5 distress probability. **Expected rejection:** duplicated distress risk.
- Relative valuation, simulation, derivatives, or real-option value is stacked onto M6. **Expected rejection:** excluded method imported into the governed result.
- A private source extract, table, figure, or historical source example is committed. **Expected rejection:** repository copyright-policy violation.

## Acceptance criteria

The approved M6 contract baseline satisfies all of the following:

- Both source boundaries and authority roles are confirmed by a human reviewer.
- All 36 `CLM-CYC-*` claims are reviewed as original paraphrases with precise locations.
- The company-valuation treatment and market-judgment overlay remain separate.
- Routing, staleness, evidence thresholds, treatment selection, risk placement, and no-timing rules are approved.
- The schema fields and 20 cross-field invariants are accepted as independently recomputable.
- Both synthetic benchmark designs cover distinct regimes and composition paths.
- Every adversarial case has a named expected rejection reason.
- M1-M5 public contracts remain unchanged.
- Source, claim, schema, repository-policy, test, and pre-commit gates pass.
- `templates/m6-cycle-aware-judgment-review-checklist.md` records an explicit maintainer decision.

M6 implementation is complete only after a later approved implementation adds the Knowledge, Skills, Workflow, strict schema, deterministic engine, independent validator, synthetic fixtures, expected outputs, tests, CI integration, and a separate implementation human review.

## Stop conditions

Stop contract approval, implementation, or valuation for an uncleared life-cycle boundary, unsupported exposure, stale or one-dimensional evidence, missing counterevidence, unsupported structural break, nonrepresentative normalization window, mixed cycle states, recovery double count, invalid futures interpretation, incomplete driver mapping, overlapping treatment payloads, invented scenario probabilities, inconsistent events or horizons, hidden composite score, unsupported extreme, direct psychology-to-DCF mapping, market-price contamination of intrinsic value, duplicated distress, trade instruction, imported excluded method, or private source content.

## Approved implementation baseline

The FVI maintainers approved the following items on 2026-08-02:

1. The dual-source boundary and each source's authority role.
2. All 36 reviewed claims and exact locations.
3. The separation between valuation-input treatment and market judgment.
4. The exposure, regime, position, confidence, and treatment enums.
5. The complete-input normalization and transition-to-normal rules.
6. The current-expectations, futures, and deterministic-scenario controls.
7. The five-dimension evidence, staleness, counterevidence, and extreme thresholds.
8. The no-timing, no-trade, no-hidden-score, and no-overlay-to-DCF rules.
9. The M1, M2, M4, and M5 composition boundaries.
10. The schema invariants, benchmark designs, adversarial cases, and acceptance criteria.

The financial review also distinguishes broad market credit evidence from issuer-specific liquidity and refinancing risk in Benchmark B, allowing the M6 market overlay and the M5 distress handoff to coexist without contradictory credit classifications or duplicated risk.

Codex may implement the repository-wide M6 artifact graph, engine, validator, schema, fixtures, expected outputs, tests, and documentation in a later separately authorized checkpoint. Live data ingestion, statistical cycle estimation, allocation, trade instructions, and excluded valuation methods remain outside the approved scope.
