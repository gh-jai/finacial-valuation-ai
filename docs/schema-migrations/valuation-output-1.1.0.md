# Valuation output schema migration: 1.0.0 to 1.1.0

Version 1.1.0 makes the review and audit contract explicit for M1 FCFF outputs.

## Required changes

- Set `schema_version` to `1.1.0`.
- Include `sensitivity`, using an empty array when no approved sensitivity set exists.
- Include `review` with `status`, nullable `reviewer`, and nullable `reviewed_at`.
- Include `calculation_trail` with at least four ordered calculation steps.

Existing value, assumption, evidence, and limitation fields remain compatible. No public v1.0 valuation output was released, so this pre-release migration does not require data backfill.
