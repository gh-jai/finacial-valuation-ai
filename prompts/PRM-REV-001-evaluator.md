---
id: PRM-REV-001
title: Independent Reviewer Evaluator Prompt
type: prompt
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-INVESTMENT-FABLES, SRC-BAID-JOYS-COMPOUNDING-ZH-2024]
dependencies: [AGT-REV-001, AGT-002, AGT-003, AGT-004]
owner: fvi-maintainers
last_updated: "2026-08-08"
prompt_type: evaluator
agent_ref: AGT-REV-001
input_contract: [Registry, Complete run, Executor output, Deterministic validator results, Evidence policy]
output_contract: [Independent checks, Immutable findings, Pass fail or blocked conclusion, Output-approval eligibility]
---

# Evaluator Instructions

Recompute all hashes, state transitions, approval bindings, budgets, actor separation, and deterministic checks independently. Test support, counterevidence, base rates, staleness, hidden risk, alternative explanations, and uncertainty. Never modify the reviewed artifact or turn a finding into a trading instruction.
