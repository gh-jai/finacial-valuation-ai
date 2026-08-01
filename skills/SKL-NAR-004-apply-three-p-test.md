---
id: SKL-NAR-004
title: Apply the 3P Test
type: skill
status: draft
version: 0.1.0
domain: narrative
source_refs: [SRC-DAMODARAN-NARRATIVE-NUMBERS-2017]
dependencies: [SKL-NAR-003, NAR-002]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Narrative assertions, Evidence register]
outputs: [Possible plausible probable assessments, Overall judgment]
---

# Apply the 3P Test

## Purpose
Test coherence, demonstrated viability, and scalability with progressively stronger evidence.

## Preconditions
Atomic assertions and supporting/contradicting evidence exist.

## Input schema
Assertions, evidence references, and reviewer identity.

## Procedure
Assess possible, then plausible, then probable; record pass/fail/uncertain, evidence, and reasoning at every level; set the most defensible overall label.

## Decision rules
Do not assess a higher level as passed when a prerequisite level fails; uncertainty is not a pass.

## Output schema
Schema-ready `three_p` object.

## Controls
Independent human judgment and contradiction review.

## Failure modes
Unsupported labels, evidence-free reasoning, or possible treated as probable.

## Source evidence
Implements `CLM-NAR-007` through `CLM-NAR-011`, Chapter 7, printed pages 92–109.

## Tests or test expectations
Reject unsupported labels, missing evidence, and empty reasoning.
