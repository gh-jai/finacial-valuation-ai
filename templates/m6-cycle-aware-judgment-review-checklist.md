# M6 cycle-aware judgment layer human review checklist

Reviewer: FVI maintainers
Review date: 2026-08-02
Contract version: `1.0.0`

## Source fidelity and authority

- [x] All 36 `CLM-CYC-*` claims are original paraphrases with precise locations.
- [x] Damodaran Chapter 13, printed pages 438-458 / PDF pages 486-506, is approved as the methodology boundary.
- [x] Marks Chapters I-III, VI-IX, and XII-XV are approved as the judgment boundary; Chapter XVIII is summary support only.
- [x] Damodaran governs valuation-input treatment, while Marks governs dated evidence and review posture only.
- [x] Simulation, relative valuation, natural-resource real options, macro forecasting, distressed-debt methods, real-estate methods, and allocation instructions remain excluded.
- [x] No PDF, raw extract, copied table, figure, long quotation, sequential source text, or source example is committed.

## Classification and routing

- [x] Exposure is supported as `economic_cycle`, `commodity_price`, `mixed_cycle`, or `not_supported` from company-specific evidence rather than an industry label.
- [x] Young, scaling-growth, structural-decline, mature, and distress boundaries route consistently to M3, M4, M5, M1, or M6.
- [x] `established_recurring`, `unstable`, `structural_break`, and `insufficient_evidence` have distinct evidence requirements.
- [x] A structural break names its mechanism, date or interval, affected inputs, and counterevidence.
- [x] Exactly one of `normalized_inputs`, `transition_to_normal`, `current_expectations`, or `stop` is selected.
- [x] The cycle-position label is an as-of assessment and never predicts a turning date.

## Evidence and confidence

- [x] Economic, company-profit, psychology/valuation, risk-attitude, and credit dimensions are each populated or explicitly unavailable.
- [x] Every evidence and curve as-of date is on or before the valuation date.
- [x] Stale evidence remains visible but cannot support high confidence or an extreme.
- [x] Supporting and contradicting evidence resolve to governed ledger items.
- [x] No hidden composite score replaces the evidence matrix.
- [x] Each available dimension translates its declared signal into a governed `band_implication`; unavailable or stale items cannot count as aligned.
- [x] High-confidence and extreme labels satisfy the proposed multi-dimension thresholds.
- [x] Unresolved opposing extremes or insufficient evidence produce `indeterminate`.

## Valuation-input integrity

- [x] The current base reconciles continuing operations, transactions, accounting discontinuities, capital, cash, debt, and fixed obligations.
- [x] A normalization window covers a representative full cycle or a documented comparable sector cycle.
- [x] Absolute, relative, sector-adjusted, and external-driver methods satisfy their individual scale and comparability boundaries.
- [x] Revenue, margin, reinvestment, capital, return, leverage, financing cost, and closure assumptions use one consistent cycle state.
- [x] A transition starts from the current base and converges exactly once to one approved normal anchor.
- [x] Normalized starting inputs do not also receive a duplicated recovery or contraction path.
- [x] A structural break or unstable regime cannot silently return to an invalid historical normal.
- [x] Every current-expectations driver point has a reviewed source, as-of date, unit, and complete driver-to-financial mapping.
- [x] Any storable-commodity forward or futures curve discloses cost-of-carry, storage, and financing limitations.

## Scenarios, overlay, and risk placement

- [x] Each deterministic scenario is a complete isolated input set with its own intrinsic-value result and calculation trail.
- [x] Probabilities, if used, share one event and horizon, have dated provenance, and sum to one; otherwise only a range is reported.
- [x] `judgment_overlay` cannot change `intrinsic_value_reference` or any DCF input.
- [x] Price relative to value is observed only after intrinsic valuation.
- [x] Review posture maps deterministically from market-cycle position and remains a human-review prompt.
- [x] No output becomes a buy/sell instruction, target allocation, position size, leverage decision, hedge, or timing claim.
- [x] Financing effects require an explicit financial mapping; psychology and credit labels alone have no numeric effect.
- [x] Distress probability, recovery, forced sale, and claim-waterfall effects appear only through `WFL-DST-001`.

## Composition, benchmarks, and approval

- [x] M2 evidence and narrative, M1 DCF, bounded M4 series controls, M5 distress treatment, and M2 feedback retain their approved responsibilities.
- [x] Benchmark A proves one trough-to-normal path without recovery or distress double counting.
- [x] Benchmark B rejects an old normal after a structural break, keeps scenarios isolated, and delegates distress once.
- [x] Every adversarial case has a named expected rejection reason before implementation begins.
- [x] The proposed top-level fields and 20 independent cross-field invariants are implementable and recomputable.
- [x] M1-M5 public contracts remain unchanged.
- [x] No M6 schema, engine, validator, fixture, workflow, Skill, or benchmark output was implemented as part of this contract review.

Decision: `[x] approve  [ ] request changes  [ ] reject`

Findings: Approved after separating broad market credit evidence from issuer-specific refinancing risk in Benchmark B and refining CLM-CYC-009, CLM-CYC-018, CLM-CYC-027, and CLM-CYC-031 so source paraphrases do not silently carry repository-governance language. The 36 claims, source roles, financial controls, exclusions, schema invariants, benchmark designs, and implementation boundary are approved.
