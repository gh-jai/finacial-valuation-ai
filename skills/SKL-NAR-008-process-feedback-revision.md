---
id: SKL-NAR-008
title: Process Feedback and Revise Narrative
type: skill
status: draft
version: 0.1.0
domain: narrative
source_refs: [SRC-DAMODARAN-NARRATIVE-NUMBERS-2017]
dependencies: [SKL-NAR-007, NAR-006]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Prior narrative and value, New evidence or disagreement]
outputs: [Versioned revised narrative, Input and value delta]
---

# Process Feedback and Revise Narrative

## Purpose
Update story and value without erasing prior versions.

## Preconditions
A prior version, valuation, and triggering evidence exist.

## Input schema
Prior version reference, evidence, reviewer reasoning, and proposed classification.

## Procedure
Classify tweak/shift/change/break; append revision history; update affected assertions and mappings; rerun the isolated valuation; calculate value delta.

## Decision rules
Every non-initial revision points to an existing prior version; a break requires rebuilding the core narrative.

## Output schema
Schema-valid revised narrative, preserved history, changed inputs, prior/new values, and delta.

## Controls
Revision-classification and final-approval human gates; retain the pages 167–183 scope note.

## Failure modes
History rewrite, missing trigger, misclassification, or value update without changed assumptions.

## Source evidence
Implements `CLM-NAR-022` through `CLM-NAR-024`, pages 151–166 with terminology continuing on 167–183.

## Tests or test expectations
Test all classifications, history chaining, deterministic rerun, and value delta.
