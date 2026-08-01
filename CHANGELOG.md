# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) conventions. The project intends to use semantic versioning after its first tagged release.

## [Unreleased]

### Added

- M0 repository foundation, governance, schemas, ontology seeds, agent-ready templates, validation tools, automated source-policy enforcement, CI, and synthetic sample artifacts.
- M1 basic FCFF vertical slice with 12 reviewed claims, four sourced Knowledge artifacts, eight bounded skills, an explicit workflow, claim-reference validation, deterministic DCF calculations, structured valuation output, and two synthetic benchmarks.
- M2 Narrative-to-Numbers vertical slice with 24 reviewed claims, six Knowledge artifacts, eight bounded skills, a compositional narrative workflow, cross-document validation, isolated alternatives, feedback history, and two synthetic benchmark cases.

### Changed

- Valuation output contract advanced to `1.1.0` with required sensitivity, review status, and deterministic calculation trail fields.
- Claim validation now covers every reviewed claim collection and narrative validation is enforced locally and in CI.
