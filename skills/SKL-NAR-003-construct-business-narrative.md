---
id: SKL-NAR-003
title: Construct a Business Narrative
type: skill
status: draft
version: 0.1.0
domain: narrative
source_refs: [SRC-DAMODARAN-NARRATIVE-NUMBERS-2017]
dependencies: [SKL-NAR-002, NAR-004]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Business and market definition, Evidence register]
outputs: [Atomic narrative assertions, Quantification classifications]
---

# Construct a Business Narrative

## Purpose
Express a focused story as atomic, testable assertions.

## Preconditions
Business, market, and competition boundaries passed review.

## Input schema
Approved definitions and evidence references.

## Procedure
Write one assertion per material idea; attach supporting and contradicting evidence; classify each as mapped, observable-only, or unquantified limitation; remove non-material complexity.

## Decision rules
Every assertion has a unique ID and every unquantified item explicitly states its limitation.

## Output schema
Narrative `assertions` array with stable IDs and evidence.

## Controls
Parsimony and evidence-sufficiency review.

## Failure modes
Compound assertions, duplicate IDs, advocacy language, missing counterevidence, or hidden limitations.

## Source evidence
Implements `CLM-NAR-006`, `CLM-NAR-012`, `CLM-NAR-017`, and `CLM-NAR-018`, printed pages 81–127.

## Tests or test expectations
Reject duplicate IDs, unmapped mapped assertions, and unmarked limitations.
