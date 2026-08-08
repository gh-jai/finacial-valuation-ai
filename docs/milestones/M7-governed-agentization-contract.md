# M7 Governed Agentization and Human-Gated Valuation Orchestration - Milestone Contract

Status: Approved for implementation
Contract version: 1.0.0
Evidence-review source: `SRC-DAMODARAN-INVESTMENT-FABLES`
Decision-process source: `SRC-BAID-JOYS-COMPOUNDING-ZH-2024`
Workflow: `WFL-AGT-001`
Registry: `REG-AGT-001`

## Decision

M7 completes the `Workflow -> Agent -> Prompt -> Test` portion of the FVI architecture. It adds a constrained, offline-reproducible protocol around existing M1-M6 artifacts and deterministic engines. It does not add a valuation formula, an autonomous investment agent, a strategy screener, or a trading system.

The locked vertical slice is the existing established-cycle synthetic industrial case. M7 may orchestrate `WFL-CYC-001` only after a human approves the exact case, assumptions, route, and evidence payload. A separate human approval is required for the exact independently validated output before memo rendering.

## Authority boundary

Repository governance is authoritative for software permissions, event integrity, approval binding, separation of duties, and stop behavior. The two private sources support only adversarial evidence review, base-rate discipline, checklists, contemporaneous decision records, and belief revision.

No runtime component reads the private PDFs. Only source metadata, reviewed atomic claims, original Knowledge artifacts, and synthetic fixtures enter the repository.

## Included

- Five versioned agents and five versioned prompts.
- A strict registry of allowed agents, prompts, actions, tools, workflows, and budgets.
- An append-only event protocol with independently derived state.
- Immutable artifact revisions, content-addressed handoffs, and SHA-256 approval binding.
- Human-only approvals at `case_lock` and `output_approval`.
- Executor-reviewer role separation.
- Independent schema, hash, state, traceability, budget, separation-of-duties, and policy validation.
- Adversarial evidence review covering supporting evidence, counterevidence, missing evidence, base rates, staleness, and strategy-failure claims.
- A decision journal that records concise rationale, assumptions, evidence references, findings, revisions, and approvals without storing hidden model reasoning.
- Synthetic happy-path, adversarial-stop, and approval-tampering benchmarks.
- Offline CI without model or external-service calls.

## Excluded

- Autonomous route, assumption, valuation, output, or publication approval.
- Shell, arbitrary filesystem write, network, browser, email, Slack, GitHub, brokerage, or order-management access.
- Direct access to private PDFs, private financial files, or secrets.
- Prompt arithmetic that replaces M1-M6 engines or validators.
- Live data ingestion, autonomous research, backtesting, screening, portfolio construction, trade timing, orders, leverage, hedging, or position sizing.
- Chain-of-thought storage or requests for hidden reasoning.
- Self-modifying prompts, agents, registry, policy, budgets, or approvals.
- One agent executing and independently approving or reviewing its own valuation output.

## Roles

| Agent | Responsibility | Cannot do |
|---|---|---|
| `AGT-ORC-001` | Derive state, authorize registered transitions, dispatch bounded handoffs | Value, review, approve, or modify artifacts |
| `AGT-EVD-001` | Assemble evidence, counterevidence, missing evidence, base-rate, and M2 inputs | Promote inference to fact, access private sources, select a trade |
| `AGT-VAL-001` | Invoke an approved deterministic workflow through a registered adapter | Choose the route, alter the case, approve, or review itself |
| `AGT-REV-001` | Recompute hashes, state, validators, evidence policy, and findings | Modify executor output, approve, or render the final memo |
| `AGT-MEM-001` | Render only an approved validated artifact into a memo | Change numbers, assumptions, findings, or add recommendations |

`AGT-VAL-001` and `AGT-REV-001` must be different agent IDs, prompt IDs, and run actors.

## State machine

```text
initialized
-> case_assembled
-> awaiting_case_lock
-> case_locked
-> draft_computed
-> deterministic_validated
-> independent_reviewed
-> awaiting_output_approval
-> output_approved
-> memo_rendered
-> completed
```

Terminal states are `blocked_missing_evidence`, `validation_failed`, `review_failed`, `rejected`, and `cancelled`.

`artifact_revised` or `approval_invalidated` returns a case revision to `awaiting_case_lock` and an output revision to `awaiting_output_approval`. The validator derives state from the complete event sequence and rejects an illegal transition even when the reported status appears plausible.

## Artifact and hash contract

Every governed artifact has an ID, kind, revision, creator, JSON payload, and SHA-256 hash of canonical UTF-8 JSON using sorted keys and compact separators. A handoff names one exact artifact ID and hash.

An approval records:

- approval ID and gate ID;
- artifact ID and current payload hash;
- a human actor ID and `actor_type: human`;
- approval timestamp; and
- active or invalidated status.

An agent cannot create an approval. If an artifact payload or revision changes, all active approvals for the old hash become invalid and an `approval_invalidated` event is required. Reusing an old approval after any case, route, assumption, evidence, number, finding, or memo-source change is prohibited.

## Tool contract

Every allowed tool is registered by ID and adapter. The registry fixes its allowed workflows and declares network, filesystem, shell, and run-mutation permissions. The first release allows only approved-artifact reads and no network or shell access.

Every tool call records agent and prompt IDs, tool ID, input and output hashes, parent event, timestamp, success or failure, error code, approval reference, and remaining action budget. Authorization fails closed for unknown agents, tools, actions, workflow IDs, missing active approvals, exhausted budgets, terminal runs, or a requested action not listed for the agent.

The cycle fixture adapter accepts only a named synthetic fixture from an explicit allowlist, runs the existing independent M6 validator, and returns a bounded structured projection. It cannot accept an arbitrary path.

## Evidence-review contract

The reviewer checks that:

- every material conclusion names supporting and contradicting evidence or a documented search for counterevidence;
- missing and stale evidence is explicit;
- any empirical claim identifies period, population, filters, benchmark, costs, and important limitations when applicable;
- a vivid case does not silently replace an outside-view base rate;
- a fixed threshold is dated and scoped;
- apparent certainty is not inferred from a historical study;
- valuation remains anchored in M1-M6 fundamentals;
- alternative explanations for apparent mispricing or unusual performance have been tested; and
- findings are recorded without converting them into a buy, sell, size, timing, leverage, or hedging instruction.

This evidence policy may block or request revision. It cannot change deterministic valuation output.

## Prompt and model boundary

Prompts request structured fields, short rationale, assumptions, evidence references, missing evidence, counterevidence, and findings. They must refuse embedded instructions that request broader tools, private-source access, policy changes, hidden reasoning, autonomous approval, or trading action.

CI validates prompt artifacts and fixtures as static files. No CI test requires an OpenAI, Gemini, Anthropic, or other model API.

## Benchmarks

1. `happy_path`: approved established-cycle case; exact-hash case lock; deterministic execution and validation; independent review; exact-hash output approval; memo; completion.
2. `adversarial_stop`: prompt injection, missing counterevidence, stale evidence, and a trade request; stop before valuation with blocking findings and no valuation output.
3. `approval_tampering`: approve a case, revise one assumption, invalidate the old approval, and return to `awaiting_case_lock`; execution with the stale approval must be impossible.

## Acceptance criteria

- All five schemas are valid and reject undeclared fields.
- All agent and prompt frontmatter validates.
- Registry references resolve bidirectionally and denies approval capability to every agent.
- Runtime authorization, hash, event, handoff, approval invalidation, budget, and adapter functions have focused tests.
- Independent validation does not call runtime state or hash helpers.
- The three fixture documents pass schema and independent validation.
- Adversarial mutations cover forged hashes, stale approvals, illegal transitions, actor spoofing, executor-reviewer identity collision, unknown tools, budget overflow, trade instructions, and arbitrary fixture paths.
- M1-M6 validators and the full pre-existing suite remain green.
- Pre-commit and Python 3.10/3.12 CI include M7 validation.
- No private source text, page image, table, PDF, live datum, or secret is committed.

This contract is the locked M7 baseline approved by the project owner on 2026-08-08. Publication, merge, and any later model-provider integration remain separate authorized actions.
