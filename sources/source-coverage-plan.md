# Private Source Coverage Plan

This document controls how private books may support FVI knowledge artifacts. Registration does not imply approval for every domain, and no private source file is committed.

## Authority tiers

- **Primary methodology source**: may directly support reviewed claims and operational rules within its documented scope.
- **Primary judgment source**: may support investment-process, risk, behavior, and decision rules, but not substitute for valuation mechanics.
- **Secondary source**: summary, translation, commentary, or partial extract. Claims must preserve that limitation and must not be silently attributed to an original author or complete work.
- **Operations source**: supports process, controls, and lifecycle operations rather than intrinsic valuation theory.

## Source matrix

| Source ID | Authority tier | Planned domains | Milestone | Restrictions |
|---|---|---|---|---|
| `SRC-DAMODARAN-LBV-2024` | Primary methodology | intrinsic valuation, FCFF/FCFE, growth, reinvestment, discount rates, terminal value, relative valuation, life cycle | M1 onward | M1 is limited to Chapter 3, PDF pages 50–81 |
| `SRC-DAMODARAN-NARRATIVE-NUMBERS-2017` | Primary methodology | narrative, story-to-input mapping, feedback loops, corporate life cycle | M2 | Do not replace numerical valuation controls with narrative claims |
| `SRC-DAMODARAN-DARK-SIDE-2018` | Primary methodology | probabilistic valuation, macro inputs, young/growth/mature/declining companies, special situations | M3 | Adaptations must declare company type and model limitations |
| `SRC-DAMODARAN-INVESTMENT-FABLES` | Primary evidence framework | strategy testing, empirical evidence, base rates, screening failure modes | M4 | Historical tests require time-period and sample-context disclosure |
| `SRC-MARKS-MOST-IMPORTANT-THING-ZH-2019` | Primary judgment, translated edition | second-level thinking, risk, price versus value, defensive process, psychology | M3–M4 | Preserve translation-edition status; do not use for DCF mechanics |
| `SRC-MARKS-MASTERING-MARKET-CYCLE-2018` | Primary judgment | economic, profit, psychology, risk-attitude, credit, distressed, real-estate and market cycles | M3 | Cycle position is probabilistic, not a precise timing signal |
| `SRC-BAID-JOYS-COMPOUNDING-ZH-2024` | Primary judgment, translated edition | mental models, temperament, checklists, decision journals, margin of safety, portfolio sizing, compounding | M4 | Distinguish cited ideas from the many thinkers discussed in the book |
| `SRC-GRAHAM-DODD-SECURITY-ANALYSIS-2008-EXTRACT` | Secondary/partial extract | discrepancies between price and value, warrants, dilution, relative-analysis limitations | M4 | Uploaded file appears limited to Part VII; never imply full-book coverage |
| `SRC-PYSH-BRODERSEN-INTELLIGENT-INVESTOR-SUMMARY-2014` | Secondary summary | navigation, thematic cross-checking | M4 | Do not directly attribute summary wording to Benjamin Graham without a primary text |
| `SRC-BAKER-TRADE-LIFECYCLE-2015` | Operations source | products, execution, booking, confirmation, settlement, lifecycle events, controls, operational risk | Post-v1 operations track | Must remain separate from intrinsic-value methodology |

## Conflict and synthesis rules

1. Keep each atomic claim tied to one exact source location.
2. Store disagreements as separate claims before creating a synthesis.
3. Label synthesis as `derived_rule`; label application-specific conclusions as `model_inference`.
4. Prefer primary methodology sources for formulas and model-selection rules.
5. Use judgment sources as review overlays, not hidden numerical inputs.
6. Do not promote a translated edition, summary, or partial extract beyond its registered authority tier.
7. Every milestone must define a narrow source boundary before extraction begins.
