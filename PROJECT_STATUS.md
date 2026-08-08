# Financial Valuation Intelligence — Project Status

Last updated: 2026-08-08

Repository: `gh-jai/financial-valuation-ai`

## Current state

The repository has merged seven implementation milestones through delivery PR #14:

- M0 — Repository foundation
- M1 — Basic FCFF DCF vertical slice
- M2 — Narrative-to-Numbers vertical slice
- M3 — Young-company survival-adjusted valuation vertical slice
- M4 — Growth-company scaling-and-fade vertical slice
- M5 — Decline, distress, and contingent-survival vertical slice
- M6 — Cycle-aware judgment layer

The M4 contract and repository-wide implementation were delivered through PR #10. The implementation includes the locked source boundary and 30 claims, seven Knowledge artifacts, nine Skills, `WFL-GRW-001`, a strict schema, deterministic engine, independent recomputation validator, two synthetic benchmarks, adversarial controls, and CI/pre-commit integration. Final review hardened registered bidirectional traceability and independent recomputation of market scale, capacity utilization, calculation trails, sensitivity points, and supported break-even values.

The M5 contract was approved and merged through PR #12, and the repository-wide implementation was delivered through PR #13. Its locked boundary is Chapter 12, printed pages 397-436 / PDF pages 445-484, with 32 reviewed atomic claims. Final review hardened partial-liquidation routing, bidirectional divestiture support, turnaround probability dating, and the one-bridge rule. The full suite reports 179 passing tests, and the Python 3.10/3.12 matrix passes.

M6 contract-first planning, source-fidelity/financial review, repository-wide implementation, and publication are complete. The implementation preserves the dual-source boundary and 36 reviewed claims, adds eight Knowledge artifacts, ten Skills, `WFL-CYC-001`, a strict schema, deterministic engine, independent validator, two synthetic benchmarks, 54 focused tests, and CI/pre-commit integration. PR #14 passed the Python 3.10/3.12 matrix and merged as `f4175ee`; the post-merge Actions run also passed. The complete merged suite reports 242 passing tests.

Current mainline architecture:

```text
Evidence
→ Narrative
→ 3P Review
→ Value Drivers
→ Life-cycle Routing / Scaling / Decline / Reinvestment / Risk Fade
→ FCFF Inputs
→ Going-concern DCF
→ Optional Survival / Distress-sale Adjustment
→ Equity and Claim Bridge
→ Per-share Value
→ Optional Dated Cycle Judgment Overlay
→ Feedback Revision
```

The project remains pre-v1.0 and is not investment advice.

## Milestone summary

### M0 — Repository foundation

Status: Complete and merged

Merge commit: `327fd2b84d83d4838084123c0ed42ba070204fee`

Delivered:

- Repository governance and contribution conventions
- Provenance-aware schemas and templates
- Source catalog and source-map structure
- Knowledge, Skill, Workflow, benchmark, and test conventions
- Repository content and copyright policy
- Validation tooling
- Pre-commit integration
- GitHub Actions CI
- Synthetic sample artifacts

### M1 — Basic FCFF DCF

Status: Complete and merged

Merge commit: `3d795efd3a35f8576496ec539bc21713ab03dfd8`

Primary source:

- `SRC-DAMODARAN-LBV-2024`

Delivered:

- Reviewed FCFF valuation claims
- Sourced Knowledge artifacts
- Bounded valuation Skills
- `WFL-VAL-001` standard-company valuation workflow
- Deterministic FCFF forecasting and DCF engine
- Period-specific and cumulative discounting
- Terminal-value controls
- Enterprise-to-equity bridge
- Sensitivity and calculation-trail requirements
- Synthetic benchmarks and regression tests

### M2 — Narrative-to-Numbers

Status: Complete and merged

Merge commit: `c2c5f5e34f1b9b04e484f03b8bb88d5b2e185197`

Primary source:

- `SRC-DAMODARAN-NARRATIVE-NUMBERS-2017`

Source boundary:

- Chapters 6–10
- Printed pages approximately 70–166
- Break, change, and shift taxonomy extends into printed pages 167–183

Delivered:

- 24 reviewed atomic claims
- Six Knowledge artifacts
- Eight bounded Skills
- `WFL-NAR-001` narrative-to-numbers workflow
- Evidence-backed narrative assertions
- Possibility, plausibility, and probability review
- Value-driver mapping
- Separate alternative narratives and valuations
- Feedback revision history
- Two deterministic synthetic benchmarks
- Narrative validators and regression coverage

M2 composition:

```text
Evidence
→ Narrative
→ 3P Review
→ Value Drivers
→ FCFF Inputs
→ WFL-VAL-001
→ Alternative Values
→ Feedback Revision
```

### M3 — Young-company survival-adjusted valuation

Status: Complete and merged

Merge commit: `d9f85c917b4729caf81a4171c249f52e3c194411`

Primary source:

- `SRC-DAMODARAN-DARK-SIDE-2018`

Source boundary:

- Chapter 9, “Baby Steps: Young and Start-Up Companies”
- Printed pages 259–321
- Chapter 10 begins on printed page 323 and is outside M3

Delivered:

- 30 reviewed atomic claims
- Seven Knowledge artifacts
- Nine bounded Skills
- `WFL-YNG-001` young-company workflow
- Young-company classification
- Top-down and bottom-up revenue forecasting
- Margin convergence
- Net operating loss carryforward
- Reinvestment and reinvestment-lag handling
- Time-varying discount-rate paths
- M1-composed going-concern FCFF valuation
- Deterministic survival/failure adjustment
- Key-person separate-scenario control
- Controlled pre-money and post-money equity bridge
- Employee-option and other-claim deductions
- Financing authorization, retention, and share-count controls
- Negative-FCFF dilution double-counting prevention
- Two deterministic synthetic benchmarks
- Full cross-field recomputation validator
- M1 and M2 regression tests

M3 composition:

```text
WFL-NAR-001
→ Young-company Classification
→ Forecast-method Selection
→ Revenue Forecast
→ Margin / NOL / Reinvestment
→ Time-varying Discount Rates
→ WFL-VAL-001 Going-concern DCF
→ Failure Scenario
→ Survival Adjustment
→ Equity and Claim Bridge
→ Per-share Value
→ M2 Feedback Revision
```

Core survival formula:

```text
Adjusted operating value
= Survival probability × Going-concern operating value
+ Failure probability × Failure value
```

Core risk separation:

- Operating and going-concern risk belongs in forecast cash flows and period-specific discount rates.
- Discrete failure risk belongs in failure probability, survival probability, and failure value.
- Key-person risk requires a separately valued operating scenario.
- The same failure exposure must not be embedded in both discount rates or FCFF and the survival adjustment.

Human review strengthened M3 so that the validator recomputes:

- FCFF
- Cumulative discount factors
- Terminal value
- Going-concern operating value
- Survival and failure components
- Failure-adjustment delta
- Pre-money common equity
- Post-money common equity
- Per-share value

The equity contract also requires that financing proceeds be authorized and retained, and that any post-money per-share denominator include shares issued in the financing round.

### M4 — Growth-company scaling and fade

Status: Complete and merged

Merge commit: `d8fec65ce1b1edbde733d74fc42b6bdb3837a64d`

Primary source:

- `SRC-DAMODARAN-DARK-SIDE-2018`

Approved source boundary:

- Chapter 10, “Shooting Stars: Valuing Growth Companies”
- Printed pages 323–357
- PDF pages 371–405 in the reviewed private edition

Approved contract artifacts:

- `docs/milestones/M4-growth-company-scaling-and-fade-contract.md`
- `extraction/manifests/M4-growth-company-scaling-and-fade.yaml`
- `extraction/reviewed/M4-growth-company-scaling-and-fade-claims.yaml`
- `templates/m4-growth-company-review-checklist.md`

Completed implementation review:

- `docs/milestones/M4-implementation-human-review.md`

Delivered through PR #10:

- Seven `GRW-*` Knowledge artifacts covering all 30 reviewed claims
- Nine `SKL-GRW-*` Skills
- `WFL-GRW-001` growth-company scaling-and-fade workflow
- `schemas/growth-company-valuation.schema.json` with strict governed objects
- `tools/growth_company.py` for scale, margin, taxes, reinvestment, invested capital, implied ROC, FCFF, stable-state rebuild, M1 discounting, and optional M3 failure handoff
- `tools/validate_growth_company_valuations.py` for independent numeric and cross-field recomputation
- Asset-light platform and capacity-led expansion deterministic benchmarks
- Adversarial coverage for boundary, stale base, scale, reinvestment, capacity, margin, risk, terminal state, failure, dilution, and market-price controls
- M1–M3 composition regressions and local/CI validation integration

Acceptance evidence:

- Maintainer-approved implementation and human-review checklist
- Full local repository validators and regression suite
- Remote Python 3.10 and Python 3.12 CI on PR #10
- Final adversarial review fixes for traceability, market/capacity series, calculation trail, sensitivity, and break-even recomputation

### M5 — Decline, distress, and contingent survival

Status: Complete; final review approved for merge

Primary source:

- `SRC-DAMODARAN-DARK-SIDE-2018`

Approved source boundary:

- Chapter 12, “Winding Down: Declining Companies”
- Printed pages 397-436
- PDF pages 445-484 in the reviewed private edition
- Chapter 11 mature-company methods are outside the M5 boundary
- Chapter 13 begins on printed page 438 / PDF page 486

Approved contract artifacts:

- `docs/milestones/M5-decline-distress-contingent-survival-contract.md`
- `extraction/manifests/M5-decline-distress-contingent-survival.yaml`
- `extraction/reviewed/M5-decline-distress-contingent-survival-claims.yaml`
- `templates/m5-decline-distress-review-checklist.md`

Approved contract decisions:

- Classify decline reversibility independently from financial distress
- Route one of four reversible/irreversible and low/high-distress combinations
- Keep status-quo, turnaround, orderly-liquidation, and forced-sale alternatives separate
- Permit evidence-backed negative growth and negative reinvestment
- Reconcile divestiture proceeds with capital and operating contribution removed
- Apply deterministic distress probability once on a common declared valuation basis
- Require probability event, horizon, as-of date, and default-to-cessation mapping
- Reuse M1 DCF, M4 forecast consistency, and M3 survival arithmetic without changing their public contracts
- Exclude live data, statistical probability estimation, relative valuation, simulation, APV, and equity-as-option methods

Implementation delivered:

- Eight `DST-*` Knowledge artifacts covering all 32 reviewed claims
- Ten `SKL-DST-*` Skills and `WFL-DST-001`
- Strict `decline-distress-valuation.schema.json`
- Deterministic decline/distress engine and independent recomputation validator
- Negative-growth, negative-reinvestment, divestiture, financing, loss-limited tax-benefit, WACC, and closure controls
- Separate turnaround, orderly-liquidation, distress-sale, contingent-survival, and current-claim bridge calculations
- Irreversible/low-distress and reversible/high-distress deterministic benchmarks
- Adversarial mutation coverage and M1-M4 composition regressions
- Pre-commit and Python 3.10/3.12 CI integration

Acceptance evidence:

- 10 schemas, 10 sources, and 128 claims validate
- Two M5 valuation documents independently recompute
- Repository copyright policy passes with no private source content
- Full local suite: 179 passed
- Maintainer final review approved on 2026-08-02
- PR #13 final-head Actions run #42 passed on Python 3.10 and Python 3.12

### M6 — Cycle-aware judgment layer

Status: Merged through PR #14; local and remote validation complete

Primary sources:

- `SRC-DAMODARAN-DARK-SIDE-2018` for cycle-aware valuation-input methods
- `SRC-MARKS-MASTERING-MARKET-CYCLE-2018` for the non-numeric judgment overlay

Approved source boundary:

- Damodaran Chapter 13, printed pages 438-458 / PDF pages 486-506
- Marks Chapters I-III, VI-IX, and XII-XV, with Chapter XVIII used only as a summary cross-check
- Damodaran simulation, relative valuation, and natural-resource real-options sections are excluded
- Marks macro/policy forecasting, distressed-debt, real-estate, allocation, and trade instructions are excluded

Approved contract artifacts:

- `docs/milestones/M6-cycle-aware-judgment-layer-contract.md`
- `extraction/manifests/M6-cycle-aware-judgment-layer.yaml`
- `extraction/reviewed/M6-cycle-aware-judgment-layer-claims.yaml`
- `templates/m6-cycle-aware-judgment-review-checklist.md`

Implemented artifacts:

- Eight `CYC-*` Knowledge artifacts split across lifecycle, valuation, risk, and market-pricing domains
- Ten bounded `SKL-CYC-*` Skills
- `WFL-CYC-001-cycle-aware-judgment-layer.md`
- `schemas/cycle-aware-judgment.schema.json`
- `tools/cycle_aware.py`
- `tools/validate_cycle_aware_judgments.py`
- Established-cycle industrial and structural-break commodity synthetic fixtures
- Two expected benchmark outputs
- Engine, validator, benchmark, artifact-graph, adversarial, mutation, and composition tests
- CI and pre-commit validator integration
- `docs/milestones/M6-implementation-human-review.md`

Approved decisions:

- Keep the `valuation_input_handoff` separate from the `judgment_overlay`
- Route exactly one of normalized inputs, transition to normal, current expectations, or stop
- Require dated five-dimension evidence, counterevidence, staleness controls, and an indeterminate result
- Normalize the complete cycle-sensitive input vector rather than one earnings line
- Use deterministic scenario ranges without invented probabilities or Monte Carlo simulation
- Treat price relative to intrinsic value as an observation, never as an intrinsic-value input
- Keep discrete distress and forced-sale treatment exclusively in `WFL-DST-001`
- Produce only bounded human-review posture labels, never timing, trading, leverage, or sizing instructions

Implementation remains within the approved source boundary, all 36 reviewed claims, financial and evidence controls, schema invariants, benchmark designs, and review checklist. PR #14 validated the exact implementation tree on Python 3.10 and Python 3.12 before merge.

Acceptance and publication evidence:

- 11 schemas and 101 governed documents validate
- 10 source records, 10 source mappings, 164 atomic claims, and 172 Knowledge references validate
- Two M6 documents independently recompute
- Full local suite: 242 passed
- Maintainer checklist approved on 2026-08-02 after separating market-wide credit evidence from issuer-specific refinancing risk in Benchmark B
- Repository copyright policy and all-candidate pre-commit pass with no private source content
- PR #14 exact-head Actions run #44 passed on Python 3.10 and Python 3.12
- PR #14 merged to `main` as `f4175ee64212288862e37eba74c43b570f6d598a`
- Post-merge Actions run `31252836713` passed

## Current governed artifact graph

```text
Sources
→ Extraction Manifests
→ Reviewed Atomic Claims
→ Knowledge
→ Skills
→ Workflows
→ Schemas
→ Engines and Validators
→ Synthetic Fixtures
→ Expected Benchmark Outputs
→ Unit and Integration Tests
→ CI
```

Important workflow dependencies:

```text
WFL-NAR-001 → WFL-VAL-001
WFL-NAR-001 + WFL-VAL-001 → WFL-YNG-001
WFL-NAR-001 + WFL-VAL-001 + bounded WFL-YNG-001 handoff → WFL-GRW-001
WFL-NAR-001 + WFL-VAL-001 + bounded WFL-GRW-001/WFL-YNG-001 reuse → WFL-DST-001
WFL-NAR-001 + WFL-VAL-001 + bounded WFL-GRW-001/WFL-DST-001 reuse → WFL-CYC-001 treatment handoff → intrinsic valuation → separate judgment overlay
```

## Validation and CI

Latest merged implementation PR CI:

- GitHub Actions run 44
- Python 3.10: Passed
- Python 3.12: Passed

The M6 implementation passed local validation and PR #14 remote matrix validation on Python 3.10 and Python 3.12. The post-merge `main` run also passed after merge commit `f4175ee`.

Validated controls include:

- Schema validity
- Source metadata integrity
- Atomic-claim and Knowledge references
- Narrative cross-references
- Probability reconciliation
- Failure-value basis consistency
- Survival-risk double-counting prevention
- FCFF and DCF recomputation
- Terminal growth and discount-rate constraints
- Reinvestment support for growth
- Revenue scale and market-share reconciliation
- Margin convergence and current-base normalization
- Invested-capital and implied-return recomputation
- Stable-state reinvestment and terminal-FCFF rebuild
- Capacity-holiday limits and resumption
- Negative-FCFF dilution controls
- Financing authorization and retention
- Post-money share-count consistency
- Explicit option and claim valuation
- Alternative narrative and claim-structure isolation
- Decline boundary and four-quadrant routing
- Negative reinvestment and divestiture reconciliation
- Face-debt, market-weight, interest-tax-benefit, after-tax debt-cost, and WACC recomputation
- Finite-life, stabilized-smaller-company, and negative-perpetuity closure controls
- Turnaround and orderly-liquidation alternative separation
- Distress event, horizon, recovery, common-basis, and one-bridge controls
- Cycle exposure, life-cycle, recurrence, structural-break, and treatment routing
- Evidence dating, staleness, availability, bidirectional references, and counterevidence
- Complete normalization, single-transition, driver-curve, carry, and scenario-isolation controls
- Scenario range and reviewed-probability controls
- Five-dimension alignment, confidence, extreme, and posture recomputation
- Intrinsic-value immutability, price-value ordering, and M5 distress separation
- Hidden-score, market-timing, trade-instruction, and excluded-method rejection
- Repository copyright policy
- Unit, integration, benchmark, and regression tests

At M3 completion, the full suite reported 88 passing tests. M4 and its final review fixes brought the suite to 125. M5 brought the merged suite to 179 passing tests. M6 brings the complete merged suite to 242 passing tests, including 54 focused M6 engine, validator, benchmark, artifact-graph, adversarial, mutation, and composition tests.

## Source and copyright policy

Private PDFs must remain under:

```text
sources/private/
```

They must never be committed.

The repository must not contain:

- Source PDFs
- Raw source extracts
- Sequential source text
- Copied tables or figures
- Long quotations
- Private source material

Public artifacts must use original paraphrases, precise source locations, and explicit claim references.

## Current limitations

The repository does not yet provide:

- Live company or market-data ingestion
- Autonomous investment recommendations
- Preferred-stock liquidation waterfalls
- Venture-capital ownership negotiation
- Monte Carlo simulation
- Decision-tree valuation
- Generalized real-options valuation
- Full relative-valuation implementation
- Statistical failure-probability estimation
- Automated extraction from private source PDFs

M3 failure probabilities and recovery values are deterministic reviewed assumptions rather than statistical forecasts.

## Recommended next milestone

The next milestone should remain a bounded vertical slice rather than a broad platform expansion.

M4, M5, and M6 are merged. The next checkpoint is to select and lock the next bounded milestone's source boundary, claims, financial controls, schema contract, composition rules, benchmarks, and acceptance criteria before implementation begins.

Recommended sequencing:

```text
M6: Merged implementation and remote Python 3.10/3.12 validation complete
→ Next milestone: Contract-first scope and source review
```

Before implementation, each milestone should first lock:

- Exact source boundary
- Atomic claims
- Model scope and exclusions
- Schema contract
- Risk placement
- Composition with existing workflows
- Synthetic benchmark design
- Acceptance criteria

## Working model

Recommended division of work:

```text
ChatGPT and maintainer review
→ Approved source boundary, claims, financial rules, schema contract, and review gates

Codex local implementation
→ Knowledge, Skills, Workflow, schema, engine, validator, benchmarks, tests, and CI integration

Publication review
→ Commit and PR authorization, exact-head remote CI, review-thread resolution, Ready, and merge
```

Codex should be used after the method, source, and financial-control contracts are locked.

## New-conversation handoff

Use this file as the canonical project handoff for a new ChatGPT or Codex session.

Minimum startup instruction:

```text
Read PROJECT_STATUS.md, README.md, sources/source-coverage-plan.md,
sources/catalog.yaml, sources/source-map.yaml, and the existing M1–M6
workflows before proposing or implementing the next milestone.

Do not alter completed milestone contracts without identifying a concrete defect.
Do not commit private source material.
Preserve composition with WFL-NAR-001, WFL-VAL-001, WFL-YNG-001,
WFL-GRW-001, and WFL-DST-001.
```
