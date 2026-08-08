# M8 Retail Product and Safety Contract Review

Contract: `docs/milestones/M8-retail-product-safety-contract.md`
Review record: `docs/milestones/M8-cross-functional-review.md`
Review status: Complete — recommend approval of M9 implementation planning with conditions
Review date: 2026-08-08
Reviewed baseline: `9099a287caf7c8e363d99586db1173f76d63956a`

## Product owner

- [x] Supported user and issuer scope is narrow enough for v1.0 planning.
- [x] Unsupported cases stop with understandable reasons and no silent alternate method.
- [x] The required user journey is specified for completion without Python or Git knowledge.
- [x] No completion language implies M9-M14 functionality already exists.
- [x] Requested country is context only; distribution approval is server-side and default deny.

## Financial reviewer

- [x] FCFF is applied only to suitable non-financial operating-company cases.
- [x] Data provenance, normalization, route, assumptions, scenarios, claim bridges, and overrides are reviewable.
- [x] Bear/base/bull outputs are conditional ranges without hidden probabilities.
- [x] Pilot and holdout reconciliation gates are sufficient and independent.
- [x] Active case locks require a supported issuer, approved matching route, approved assumptions, current evidence, and an exact canonical case hash.

## Security reviewer

- [x] Data gateway, upload, normalization, valuation, validator, renderer, browser, and operations trust zones are separated.
- [x] Injection, SSRF, redirects, traversal, uploads, access control, CSRF/replay, secrets, exports, availability, and supply-chain threats are covered.
- [x] M7 exact-hash, approval invalidation, budgets, and executor/reviewer separation remain mandatory.
- [x] ASVS 5.0.0 and LLMSVS v2.0 were rechecked and must be rechecked before implementation review and release.
- [x] Request fields and evidence are explicitly unable to approve a territory, license, route, artifact, or action.

## Internal legal/compliance and data-licensing perimeter

- [x] Advice, personal recommendation, territory, marketing, and disclaimer risks are recorded as product controls rather than disclaimer-only controls.
- [x] Buy/sell/hold/sizing/timing/suitability fields are prohibited by contract and schema.
- [x] SEC access behavior and per-provider storage/display/export/redistribution rights have mandatory review fields and default-deny behavior.
- [x] Privacy, retention, deletion, upload, AI-provider handling, copyright, and report wording have named pre-launch gates.
- [x] This internal review does not claim qualified legal advice or provider permission.

## Repository and source boundary

- [x] Five draft schemas and contract tests pass.
- [x] No live-data, LLM, API, CLI, Web UI, or report-rendering implementation is present.
- [x] No PDF, ebook, page image, private extract, real issuer snapshot, or credential is committed.
- [x] Existing M1-M7 validators, tests, CI, and repository policy remain green.

## Mandatory conditions carried into M9-M14

- [ ] A qualified legal/compliance reviewer approves each intended distribution territory and final product wording before external beta or release.
- [ ] Each non-SEC provider owner approves storage, display, export, redistribution, attribution, retention, and territorial use before its adapter or fields are enabled.
- [ ] Privacy notices, retention/deletion schedules, processor terms, and user-upload handling receive territory-specific approval before collecting user files.
- [ ] M13 independently reconciles eight pilots and two holdouts, closes critical/high security findings, and completes usability/accessibility testing.
- [ ] M14 rechecks SEC, FCA, WCAG, ASVS, LLMSVS, provider terms, and release territories before `v1.0.0`.

Recommendation: `[x] approve M9 implementation planning with conditions  [ ] request changes  [ ] reject`

Project-owner decision: `[x] authorize M9 implementation planning  [ ] request further M8 changes`

Authorization recorded: 2026-08-08. This authorizes planning only; accepting or publishing the planning baseline, M9 implementation, live retrieval, provider activation, and later release actions remain separate checkpoints.

Reviewer record and evidence:

- Product owner: project-owner instruction to complete the M8 cross-functional review, 2026-08-08.
- Financial review: FVI maintainer review against M1-M6 approved workflows and the M8 support/pilot contracts.
- Security review: FVI maintainer review against the M7 authority boundary, M8 threat model, OWASP ASVS 5.0.0, and OWASP LLMSVS v2.0.
- Internal legal/data perimeter: FVI maintainer review against current SEC fair-access/API guidance and FCA PERG 8; this is not external counsel or provider sign-off.
- Detailed findings and exact external links: `docs/milestones/M8-cross-functional-review.md`.
