# Governance

FVI uses maintainer-led, review-based governance during its pre-1.0 phase.

## Roles

- **Maintainers** approve releases, governance changes, schema changes, and security responses.
- **Domain reviewers** assess financial correctness and evidence quality.
- **Contributors** propose original artifacts, tests, and documentation.

## Decisions

Routine changes require one maintainer approval. Breaking schema, licensing, citation-policy, or governance changes require two maintainer approvals and a documented rationale. Security fixes may be merged privately and disclosed after remediation.

Artifact status advances from `draft` to `reviewed` to `approved`; deprecated artifacts remain addressable. Maintainers resolve disputes by evidence quality, reproducibility, safety, and project scope. Material conflicts of interest must be disclosed.

## Releases

Releases require passing validation, a changelog entry, documented schema compatibility, benchmark results, and copyright/security review. No release may depend on private source files to run its public tests.
