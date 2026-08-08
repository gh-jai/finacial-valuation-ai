# Architecture

FVI is a provenance-preserving artifact pipeline:

```text
Source -> Claim -> Knowledge -> Skill -> Workflow -> Agent -> Prompt -> Test -> Release
```

- **Source** is a redistributable metadata record that identifies a work and may include a relative private locator without containing the work itself.
- **Claim** captures one compact proposition, its exact location, and whether it is a `source_statement`, `derived_rule`, or `model_inference`.
- **Knowledge** consolidates reviewed claims into an original, reusable explanation with assumptions and limitations.
- **Skill** defines a bounded capability with inputs, procedure, outputs, controls, and failure modes.
- **Workflow** composes skills into ordered steps, decision points, and human review gates.
- **Agent** assigns an operational role, permitted tools, context limits, escalation rules, and handoff contracts.
- **Prompt** supplies versioned instructions for system behavior, tasks, and evaluation.
- **Test** validates structure and behavior using synthetic or redistributable fixtures.
- **Release** freezes compatible schemas, artifacts, benchmark results, and governance evidence.

## Design rules

Each artifact has a stable ID, semantic version, lifecycle status, owner, date, dependencies, and source references. References point backward; generated outputs record the exact artifact versions used. Schemas are contracts, Markdown is the principal knowledge carrier, and YAML is reserved for catalogs and compact configuration.

Promotion between stages requires validation and review. Rejected material remains available for audit without being treated as approved knowledge. Agents may automate transformations, but material valuation judgments remain reviewable and must identify uncertainty, assumptions, and conflicts.

## Trust boundaries

Private sources and local financial data sit outside version control. Extraction is untrusted until reviewed. Prompts and agents cannot upgrade an inference into a sourced fact. Release artifacts must be reproducible from redistributable fixtures without access to private works.

The pipeline operates on the source metadata record, not directly on a committed source file. Private inputs are local trust-boundary inputs and must never become release dependencies.

## Valuation workflow composition

Life-cycle routing selects one top-level operating forecast before valuation:

```text
WFL-NAR-001
├─ WFL-YNG-001 for young and early-commercial companies
├─ WFL-GRW-001 for established growth companies
├─ WFL-DST-001 for structurally or potentially reversibly declining companies
├─ WFL-CYC-001 for mature companies with supported cycle exposure
└─ WFL-VAL-001 for standard mature operating cases without a specialized route
```

`WFL-GRW-001` owns revenue scale and fade, margin convergence, reinvestment, invested-capital and implied-return checks, and risk convergence. It delegates cumulative FCFF discounting and Gordon-growth arithmetic to `WFL-VAL-001`. Material discrete failure is applied once through the expected-value semantics of `WFL-YNG-001` without running a second young-company forecast.

`WFL-DST-001` independently classifies reversibility and distress, owns negative-growth and capital-release paths, financing and tax-benefit recomputation, divestiture integrity, closure, orderly-liquidation, and forced-sale controls, and delegates cumulative FCFF discounting to `WFL-VAL-001`. Reversible operating alternatives remain separate final values. Material cessation or forced-sale risk is applied once through M3-compatible contingent-survival arithmetic before one dated claim bridge.

`WFL-CYC-001` selects one complete-input normalization, current-to-normal transition, current-expectations path, or stop decision. It delegates intrinsic-value arithmetic to `WFL-VAL-001`, reuses bounded M4 series controls, and routes discrete issuer distress once to `WFL-DST-001`. Its dated five-dimension judgment overlay is produced only after intrinsic value and cannot modify value, predict timing, or authorize a trade.
