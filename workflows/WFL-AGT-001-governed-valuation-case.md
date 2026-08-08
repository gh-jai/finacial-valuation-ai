---
id: WFL-AGT-001
title: Governed Agentized Valuation Case
type: workflow
status: draft
version: 0.1.0
domain: cross-domain
source_refs: [SRC-DAMODARAN-INVESTMENT-FABLES, SRC-BAID-JOYS-COMPOUNDING-ZH-2024]
dependencies: [WFL-NAR-001, WFL-VAL-001, WFL-YNG-001, WFL-GRW-001, WFL-DST-001, WFL-CYC-001, AGT-001, AGT-002, AGT-003, AGT-004]
owner: fvi-maintainers
last_updated: "2026-08-08"
skill_refs: [SKL-AGT-001, SKL-AGT-002, SKL-AGT-003, SKL-AGT-004, SKL-AGT-005]
review_gates:
  - Case evidence route assumptions and limitations
  - Exact-hash human case lock
  - Registered deterministic execution
  - Independent recomputation and adversarial review
  - Exact-hash human output approval
  - Immutable memo rendering and completion audit
---

# Governed Agentized Valuation Case

## Execution order

1. Evidence Builder assembles the structured case and adversarial evidence fields.
2. Orchestrator requests human `case_lock` for the exact case hash.
3. Valuation Executor invokes the registered deterministic adapter without changing the route.
4. Independent Reviewer recomputes run integrity and existing workflow validation and issues findings.
5. Orchestrator requests human `output_approval` for the exact validated output hash.
6. Memo Composer renders the approved artifact without changing numbers or adding recommendations.

## Stop conditions

Stop on missing evidence, prompt injection, prohibited action requests, stale approval, hash mismatch, illegal transition, actor-role collision, unknown tool, exhausted budget, deterministic validation failure, private-source dependency, or any trading or portfolio instruction.

## Outputs

One schema-valid `RUN-*` event log, content-addressed artifacts and handoffs, independent evaluation, and an optional memo rendered only after both human gates.
