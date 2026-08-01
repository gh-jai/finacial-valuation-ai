# Contributing

## Before contributing

Read `CITATION_POLICY.md`, `SECURITY.md`, and the relevant JSON Schema. Do not submit raw source files, copied chapters, long quotations, confidential company data, or material you cannot redistribute.

## Artifact workflow

1. Register source metadata in `sources/catalog.yaml` using an opaque source ID.
2. Record source-to-artifact links in `sources/source-map.yaml`.
3. Write original claims or notes in the appropriate extraction stage.
4. Promote reviewed material into knowledge, skills, and workflows.
5. Add synthetic tests or benchmarks for important behavior.
6. Run all validation commands from the README.

Artifact IDs are immutable and use a domain prefix, for example `VAL-001`, `SKL-VAL-001`, and `WFL-VAL-001`. Use semantic versions, ISO `YYYY-MM-DD` dates, relative repository paths, and stable source IDs. Prefer one concept or capability per file.

## Pull requests

Keep changes focused. Explain provenance, assumptions, schema impacts, test evidence, and copyright review. Breaking schema changes require a migration note and a changelog entry. At least one maintainer must review changes to schemas, governance, or release benchmarks.

By contributing, you agree that your contribution is original or appropriately licensed and may be distributed under this repository's license.
