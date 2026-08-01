---
id: SKL-NAR-006
title: Generate Alternative Narratives
type: skill
status: draft
version: 0.1.0
domain: narrative
source_refs: [SRC-DAMODARAN-NARRATIVE-NUMBERS-2017]
dependencies: [SKL-NAR-005, NAR-005]
owner: fvi-maintainers
last_updated: "2026-08-02"
inputs: [Current narrative, Material disagreements]
outputs: [Separate versioned alternative narratives]
---

# Generate Alternative Narratives

## Purpose
Represent credible disagreements as separately reviewable stories rather than blended assumptions.

## Preconditions
The current narrative and mapped inputs are complete.

## Input schema
Current narrative ID, disagreements, alternative evidence, and status.

## Procedure
Create a distinct ID and full narrative object for each active alternative; repeat 3P and mapping; record difference summary and credibility.

## Decision rules
No alternative may reuse the current ID or be averaged, merged, or silently omitted.

## Output schema
Current narrative pointers plus separate schema-valid narrative documents.

## Controls
Alternative-story separation gate.

## Failure modes
Duplicate IDs, partial alternatives, merged assumptions, or unreviewed credibility.

## Source evidence
Implements `CLM-NAR-019` through `CLM-NAR-021`, Chapter 9, printed pages 128–150.

## Tests or test expectations
Reject current/alternative ID collisions and silently merged alternatives; verify isolated contracts.
