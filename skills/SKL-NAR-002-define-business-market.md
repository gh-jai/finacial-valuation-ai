---
id: SKL-NAR-002
title: Define the Business and Market
type: skill
status: draft
version: 0.1.0
domain: narrative
source_refs: [SRC-DAMODARAN-NARRATIVE-NUMBERS-2017]
dependencies: [SKL-NAR-001, NAR-001]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Evidence register, Company scope]
outputs: [Business definition, Market and competition definition]
---

# Define the Business and Market

## Purpose
Set boundaries that determine customers, market opportunity, competitors, and life-cycle context.

## Preconditions
`SKL-NAR-001` completed with traceable evidence.

## Input schema
Company products, customers, geographies, market metrics, competitors, barriers, advantages, history, and management evidence.

## Procedure
Define the business; describe market size, growth, structure; identify current and potential competitors; connect history and management to current position.

## Decision rules
Use one coherent base definition and disclose credible boundary alternatives.

## Output schema
Schema-ready `business_definition`, `market`, and `competition` objects.

## Controls
Human gate approves business and market boundaries.

## Failure modes
Category ambiguity, circular market sizing, omitted entrants, or historical extrapolation without reasoning.

## Source evidence
Implements `CLM-NAR-001` through `CLM-NAR-005`, Chapter 6, printed pages 70–80.

## Tests or test expectations
Require all schema fields, market evidence, and competition evidence.
