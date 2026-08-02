# Financial Valuation Intelligence

Financial Valuation Intelligence (FVI) is an open, software-style framework for turning privately held financial valuation source materials into traceable claims, reusable knowledge, executable skills, repeatable workflows, prompts, and benchmarks. The repository contains original metadata, abstractions, and tooling—not source books or copied chapters.

## Repository philosophy

- Treat financial knowledge as versioned, testable artifacts.
- Preserve provenance from each claim to a precise private-source location.
- Separate sourced statements, derived rules, and model inferences.
- Prefer small Markdown and YAML artifacts governed by JSON Schema.
- Require human review for judgment-heavy valuation conclusions.
- Keep examples synthetic, minimal, and safe to redistribute.

## Legal and copyright boundary

Raw PDFs, ebooks, scans, and copyrighted extracts must never be committed. Private source files may be placed locally under `sources/private/`, which Git ignores. Only source metadata, compact factual citations, original paraphrases, and independently authored framework artifacts belong in the repository. See [CITATION_POLICY.md](CITATION_POLICY.md) and [NOTICE.md](NOTICE.md).

## Knowledge pipeline

```text
Source -> Claim -> Knowledge -> Skill -> Workflow -> Agent -> Prompt -> Test -> Release
```

Here, **Source** means the redistributable metadata record. A private local input may inform that record but remains outside version control. Every transformation should retain `source_refs`, declare dependencies, pass schema validation, and expose human-review checkpoints.

## Folder structure

| Path | Purpose |
|---|---|
| `sources/` | Redistributable source metadata; private inputs remain ignored |
| `schemas/` | JSON Schemas for governed artifacts |
| `ontology/` | Concepts, relationships, and aliases |
| `extraction/` | Manifests, maps, and staged original notes |
| `knowledge/` | Reviewed domain knowledge units |
| `skills/` | Bounded, reusable valuation capabilities |
| `workflows/` | Ordered combinations of skills and review gates |
| `agents/` | Future agent role and policy definitions |
| `prompts/` | System, task, and evaluator prompts |
| `templates/` | Authoring templates for consistent contributions |
| `benchmarks/` | Synthetic fixtures, expected results, and scoring rules |
| `tests/` | Schema, unit, integration, regression, and adversarial tests |
| `tools/` | Lightweight validation utilities |
| `docs/` | Extended project documentation |

## First milestone

M0 establishes repository governance, provenance rules, schemas, templates, validation tooling, and one synthetic vertical slice: intrinsic-value knowledge, a basic DCF skill, and a standard valuation workflow. M1 will exercise the complete pipeline against one privately held source without publishing that source or substantial extracts.

## Validate

Python 3.10 or newer is required.

```bash
python -m pip install -e ".[dev]"
python tools/validate_schemas.py
python tools/validate_sources.py
python tools/validate_claims.py
python tools/validate_narratives.py
python tools/validate_young_company_valuations.py
python tools/validate_growth_company_valuations.py
python tools/validate_decline_distress_valuations.py
python tools/check_repository_policy.py
pytest
```

Run `pre-commit install` once to enable local checks. See [CONTRIBUTING.md](CONTRIBUTING.md) before adding artifacts.

## Implemented vertical slices

- M1: traceable basic FCFF DCF, enterprise-to-equity bridge, sensitivity review, structured output, and synthetic benchmarks.
- M2: evidence-backed narrative construction, 3P review, assertion-to-value-driver mapping, separate alternative valuations, and feedback revision composed with the M1 workflow.
- M3: young-company top-down and bottom-up forecasts, NOL and reinvestment handling, time-varying rates, discrete survival adjustment, and controlled pre/post-money equity bridges composed with M1 and M2.
- M4: growth-company revenue scaling and fade, margin convergence, segment-specific reinvestment, implied returns, risk convergence, stable-state terminal rebuild, and bounded M3 failure handoff composed with M1–M3.
- M5: declining-company routing, negative reinvestment and divestitures, financing and tax-benefit paths, closure alternatives, deterministic distress-sale adjustment, and one current-claim bridge composed with M1–M4.

FVI remains pre-v1.0 and is not investment advice. Interfaces and schemas may change before release.
