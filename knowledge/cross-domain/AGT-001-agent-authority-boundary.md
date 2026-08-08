---
id: AGT-001
title: Agent Authority Boundary
type: knowledge
status: draft
version: 0.1.0
domain: cross-domain
source_refs: []
dependencies: [WFL-NAR-001, WFL-VAL-001, WFL-YNG-001, WFL-GRW-001, WFL-DST-001, WFL-CYC-001]
owner: fvi-maintainers
last_updated: "2026-08-08"
summary: Keep orchestration, evidence assembly, deterministic execution, independent review, human approval, and memo rendering as separate authorities.
claim_refs: []
---

# Agent Authority Boundary

M7 agents are roles inside a governed protocol, not autonomous principals. Each receives the minimum actions and tools needed for one responsibility. All approvals remain human-only, deterministic calculations remain in M1-M6 engines, and review cannot modify the artifact under review.

The registry is deny-by-default. Unknown actions, tools, workflows, agents, prompts, or artifact kinds stop the run. No prompt can expand the registry or override repository governance.
