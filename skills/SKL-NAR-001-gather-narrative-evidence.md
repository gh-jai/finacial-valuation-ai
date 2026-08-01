---
id: SKL-NAR-001
title: Gather Narrative Evidence
type: skill
status: draft
version: 0.1.0
domain: narrative
source_refs: [SRC-DAMODARAN-NARRATIVE-NUMBERS-2017]
dependencies: [NAR-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Valuation scope, Authorized evidence records]
outputs: [Evidence register, Sufficiency findings]
---

# Gather Narrative Evidence

## Purpose
Create an auditable evidence set for company, market, competition, history, and management.

## Preconditions
Authority, subject, date, geography, and copyright controls are explicit.

## Input schema
Evidence IDs, dates, provenance, observations, and access classification.

## Procedure
Collect relevant supporting and contradicting observations; deduplicate; label gaps and private inputs; retain identifiers instead of source text.

## Decision rules
Require evidence for every material narrative area and prefer contradictory evidence over confirmation-only collection.

## Output schema
An evidence register plus missing, stale, conflicting, and private-data findings.

## Controls
No raw PDF, sequential extract, or long quotation enters a public artifact.

## Failure modes
Missing authority, unverifiable references, stale evidence, or evidence gaps hidden as assumptions.

## Source evidence
Implements `CLM-NAR-001` through `CLM-NAR-005` and `CLM-NAR-022`, printed pages 70–80 and 151–166.

## Tests or test expectations
Reject missing evidence and unknown `SRC-` or `CLM-` references; repository policy must pass.
