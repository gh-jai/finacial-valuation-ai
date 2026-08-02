---
id: SKL-YNG-001
title: Classify a Young Company
type: skill
status: draft
version: 0.1.0
domain: lifecycle
source_refs: [SRC-DAMODARAN-DARK-SIDE-2018]
dependencies: [YNG-001, WFL-NAR-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Company history, Commercial status, Revenue and loss status, Financing and claim profile]
outputs: [Young-company profile, Classification findings]
---

# Classify a Young Company
## Purpose
Determine whether M3 applies and record the valuation consequences.
## Preconditions
An M2 narrative and lawful evidence set exist.
## Input schema
History years, revenue, operating-loss flag, private-capital dependence, commercial status, claim complexity, and evidence IDs.
## Procedure
Evaluate observable indicators; select idea, pre-revenue, early-commercial, or second-stage; document reasoning and exclusions.
## Decision rules
Require at least two young-company indicators and reject established high-growth companies outside Chapter 9 scope.
## Output schema
Schema-ready `young_company_profile` and findings.
## Controls
Human classification and life-cycle boundary review.
## Failure modes
Unsupported stage, missing evidence, or confusing young with established growth.
## Source evidence
Implements `CLM-YNG-001` through `CLM-YNG-010`, pages 259–266.
## Tests or test expectations
Test limited history, pre-revenue, loss, and insufficient-indicator cases against `classify_young_company`.
