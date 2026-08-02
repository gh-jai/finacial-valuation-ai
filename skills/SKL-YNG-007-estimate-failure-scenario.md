---
id: SKL-YNG-007
title: Estimate Failure Probability and Failure Value
type: skill
status: draft
version: 0.1.0
domain: risk
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [SKL-YNG-006, YNG-005]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Failure probability, Survival probability, Failure value and basis, Recovery evidence]
outputs: [Reconciled failure scenario, Control findings]
---

# Estimate Failure Probability and Failure Value
## Purpose
Represent truncation risk as an explicit expected-value scenario.
## Preconditions
Going-concern operating risk excludes failure premiums and losses.
## Input schema
Bounded probabilities, finite failure value, claim-level basis, rationale, beneficiary, evidence.
## Procedure
Reconcile probabilities; reconcile failure value to operating assets; document recovery and claim beneficiary.
## Decision rules
Probabilities sum to one; basis mismatch stops; zero recovery still needs rationale.
## Output schema
Schema-ready `failure_scenario` and findings.
## Controls
Human recovery and probability review.
## Failure modes
Unsupported zero, arbitrary recovery percentage, claim mismatch, or double counting.
## Source evidence
Implements `CLM-YNG-022` through `CLM-YNG-025`, pages 304–308.
## Tests or test expectations
Test probability sum, nonzero recovery, finite value, and basis mismatch.
