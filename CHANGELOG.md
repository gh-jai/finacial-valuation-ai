# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) conventions. The project intends to use semantic versioning after its first tagged release.

## [Unreleased]

### Added

- M0 repository foundation, governance, schemas, ontology seeds, agent-ready templates, validation tools, automated source-policy enforcement, CI, and synthetic sample artifacts.
- M1 basic FCFF vertical slice with 12 reviewed claims, four sourced Knowledge artifacts, eight bounded skills, an explicit workflow, claim-reference validation, deterministic DCF calculations, structured valuation output, and two synthetic benchmarks.
- M2 Narrative-to-Numbers vertical slice with 24 reviewed claims, six Knowledge artifacts, eight bounded skills, a compositional narrative workflow, cross-document validation, isolated alternatives, feedback history, and two synthetic benchmark cases.
- M3 young-company survival-adjusted valuation vertical slice with 30 reviewed claims, seven Knowledge artifacts, nine bounded Skills, top-down and bottom-up forecasting, NOL and reinvestment handling, time-varying rates, survival adjustment, equity-bridge controls, and two synthetic benchmarks.
- M4 growth-company scaling-and-fade vertical slice with 30 reviewed claims, seven Knowledge artifacts, nine bounded Skills, current-base normalization, explicit scale and margin paths, three reinvestment methods, implied-return checks, risk convergence, stable-state terminal rebuild, bounded M3 failure handoff, strict recomputation validation, and two deterministic synthetic benchmarks.
- M5 decline, distress, and contingent-survival vertical slice with 32 reviewed claims, eight Knowledge artifacts, ten bounded Skills, four-quadrant routing, negative reinvestment and divestiture controls, financing and loss-limited tax-benefit paths, three closure modes, turnaround and orderly-liquidation alternatives, three forced-sale recovery methods, one contingent-survival adjustment, one current-claim bridge, and two deterministic synthetic benchmarks.
- M6 cycle-aware judgment vertical slice with 36 reviewed claims, eight Knowledge artifacts, ten bounded Skills, company-specific exposure and regime routing, complete-input normalization and transition controls, dated current-expectations scenarios, five-dimension evidence and staleness controls, immutable intrinsic-value references, one M5 distress handoff, and two deterministic synthetic benchmarks.
- M7 governed-agentization vertical slice with 20 reviewed claims, four Knowledge artifacts, five Skills, five agents, five prompts, a deny-by-default registry, exact-hash handoffs and human approvals, append-only events, independent state and integrity validation, offline adapters, and three synthetic governance benchmarks.
- M8 contract-only retail-product boundary with five draft interface schemas, issuer support rules, error/data/output policy, threat model, pilot/holdout design, and cross-functional review checklist.

### Changed

- Valuation output contract advanced to `1.1.0` with required sensitivity, review status, and deterministic calculation trail fields.
- Claim validation now covers every reviewed claim collection and narrative validation is enforced locally and in CI.
- Young-company schema and cross-field controls are enforced through pytest, pre-commit, and the Python 3.10/3.12 CI matrix.
- Growth-company schema, cross-field recomputation, adversarial controls, and M1–M3 regressions are enforced through pytest, pre-commit, and the Python 3.10/3.12 CI matrix.
- M4 validation now enforces bidirectional registered traceability and independently recomputes market scale, capacity utilization, the full calculation trail, terminal-driver sensitivity points, and supported break-even values.
- M5 validation independently recomputes operating and financing series, divestiture and negative-reinvestment support, closure, alternative selection, recovery, probability components, claim bridges, and every stored calculation trail; it is enforced through pytest, pre-commit, and the Python 3.10/3.12 CI matrix.
- M6 validation independently recomputes evidence dates and staleness, normalization methods, transition paths, complete driver mappings, scenario isolation and ranges, dimension alignment, confidence, posture, price-value ordering, and distress separation; local pytest and pre-commit enforce the same controls before the Python 3.10/3.12 CI matrix.
- Agent and prompt frontmatter now validate as governed artifacts; M7 validation independently recomputes hashes, state transitions, approval freshness, budgets, actor separation, tool authorization, and prohibited-output controls in pytest, pre-commit, and the Python 3.10/3.12 CI matrix.
- The roadmap now defers v1.0 until M9-M14 deliver real-data ingestion, assumptions/routing, governed real-case interfaces, retail UX, pilots, security/licensing review, and operational release gates.
