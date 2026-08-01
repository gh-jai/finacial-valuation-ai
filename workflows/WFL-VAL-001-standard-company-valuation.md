---
id: WFL-VAL-001
title: Standard Company Valuation
type: workflow
status: draft
version: 0.1.0
domain: valuation
source_refs: []
dependencies:
  - VAL-001
  - SKL-VAL-001
owner: fvi-maintainers
last_updated: "2026-08-01"
---

# Standard Company Valuation

## Objective

Create a traceable, reviewable company valuation that connects evidence and narrative to financial assumptions and an explicit value range.

## Entry criteria

The user has lawful access to required company data, the valuation purpose and date are known, and no private input will be committed.

## Steps

1. Define scope, value basis, date, currency, audience, and decision context.
2. Register authorized evidence and distinguish source statements from inferences.
3. Normalize historical financials and document adjustments.
4. Form the business narrative and translate it into forecast drivers.
5. Select applicable methods and run `SKL-VAL-001` where a DCF is appropriate.
6. Perform sensitivities, scenarios, and independent cross-checks.
7. Reconcile methods and prepare the valuation memo and assumption register.
8. Complete model, evidence, copyright, and decision-risk review.

## Human review gates

- Evidence and accounting normalization before forecasting
- Forecast narrative and key assumptions before valuation
- Mechanics, sensitivities, and enterprise-to-equity bridge before reporting
- Final limitations, conflicts, and communication before approval

## Outputs and exit criteria

Produce a valuation memo, assumption register, evidence table, model review, and schema-valid structured valuation output. Exit only when material findings are resolved or visibly accepted by an authorized reviewer.

## Escalation

Stop and escalate missing authority, material non-public information, unresolved data conflicts, method inapplicability, or results that fail basic reconciliation checks.
