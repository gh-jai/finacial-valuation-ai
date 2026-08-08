# M8 Retail Product and Safety — Cross-Functional Review

Status: Complete — recommend approval of M9 implementation planning with conditions
Review date: 2026-08-08
Reviewed baseline: P0+M8 merge `9099a287caf7c8e363d99586db1173f76d63956a`
Decision authority: project owner; M9 planning authorization pending

## Decision

The M8 product and safety boundary is sufficiently narrow, testable, and fail-closed for the reviewers to recommend **M9 implementation planning with conditions** after the corrections recorded below. This review does not itself authorize M9 planning, M9 implementation, live retrieval, provider use, user uploads, model calls, an API, a UI, external beta, public distribution, or release.

The review is conditional because qualified territory-specific legal/compliance approval, provider permission, privacy approval, penetration testing, accessibility/usability evidence, and real-company pilot reconciliation cannot honestly be completed against a contract-only system. Those are mandatory M9-M14 gates, not waived M8 findings.

## Review outcome by function

| Function | Outcome | Evidence and boundary |
|---|---|---|
| Product | Pass for planning | v1 scope is US-listed, USD-reporting non-financial operating companies; unsupported issuers and ambiguous identity stop. The ten-step no-code journey is specified but not implemented. |
| Financial method | Pass for planning | Mature, young, growth, decline/distress, and cyclical cases route to approved M1-M6 workflows. FCFF is not extended to banks, insurers, REITs, funds, SPACs, or reserve real-option cases. Three scenarios remain isolated and unweighted. |
| Data governance | Pass with implementation conditions | Immutable snapshots, provenance, freshness, reconciliation, record-level license references, exact hashes, manual-input labels, and no-silent-fill rules are specified. Provider adapters remain disabled until the provider register is approved. |
| Security | Pass for planning | Network/data/runtime zones, untrusted-input rules, SSRF/redirect controls, uploads, LLM injection, object authorization, browser approval forgery, secrets, supply chain, availability, exact-hash approvals, and independent validation are covered as build requirements. No control is claimed implemented. |
| Legal/compliance | Internal perimeter pass only | Advice/action outputs are prohibited structurally; territory distribution is default deny and server-authorized. Qualified counsel must approve each intended territory and final wording before external beta or release. |
| Data licensing | Internal perimeter pass only | SEC fair-access behavior and provider-rights fields are mandatory. No market-data storage, display, export, or redistribution permission is claimed. |
| Accessibility/UX | Contract pass only | Traditional Chinese-first output, English source identifiers, explainability, limitations, and WCAG 2.2 AA are launch requirements. M12/M13 must produce user-test and accessibility evidence. |
| Engineering/operations | Pass for planning | Schemas remain unstable `0.1.0`; validators and offline fixtures are required; runtime, incident, backup, deletion, rollback, and release evidence remain later gates. |

## Findings closed during review

### M8-R01 — Request data could appear to grant distribution authority

Severity: High contract defect

`company-request` previously accepted a client-supplied `distribution_approved` boolean. That contradicted the rule that browser fields and other untrusted data cannot grant authority.

Resolution: the field was removed. The request contains only a country code; a server-side, default-deny territory registry must approve distribution. A formal retail report now requires a human-reviewed distribution decision and legal-review reference.

### M8-R02 — Draft schemas allowed impossible “complete” states

Severity: High contract defect

The initial schemas could represent a complete source snapshot with stale or unlicensed data, complete normalized financials with blocking findings, and an active case lock over a rejected route or assumptions.

Resolution: conditional schema invariants now bind:

- complete snapshots to verified identity, current data, approved storage rights, at least one record, and no blocking warnings;
- complete normalized financials to no missing/review/blocking codes and only passed reconciliations;
- active case locks to reviewed support, a matching approved route, approved assumptions, and no missing or stale evidence;
- complete normalized facts to approved review status, and unsupported normalized sets to at least one blocking code;
- route identifiers to their matching lifecycle classes.

### M8-R03 — Approval hash targets were ambiguous

Severity: High integrity defect

The initial contract did not say whether output approval bound the valuation output or the final report, creating a possible cyclic or wrong-artifact hash design.

Resolution: the contract now defines canonical hash subjects. `case_lock` binds the canonical valuation-case payload; `output_approval` binds the independently validated valuation output; `report_hash` protects the final approved export. Cross-field hash equality, actor separation, finite numbers, scenario/range ordering, sensitivity uniqueness, arithmetic, and canonicalization remain mandatory independent-validator checks because Draft 2020-12 cannot express them all safely.

### M8-R04 — Expired reports could retain an active approval

Severity: Medium integrity defect

Resolution: approved reports require active output approval; expired reports require invalidated output approval with an invalidation timestamp. Reuse of the old approval remains prohibited.

### M8-R05 — Browser and data-gateway attack paths needed explicit controls

Severity: Medium security completeness defect

Resolution: the threat model now explicitly covers SSRF, redirect escape, DNS/private-address defenses, CSRF, session theft, replay, step-up/recent authentication, server-side registries, and idempotent approval handling.

## Mandatory open conditions

These are not M8 contract defects and do not block M9 planning. They block the stated later action:

| ID | Condition | Owner | Blocks |
|---|---|---|---|
| `M8-C01` | Qualified counsel approves the product perimeter, marketing, disclaimers, report wording, and each intended distribution country. | Legal/compliance owner | External beta and release |
| `M8-C02` | Each market-data provider's dated terms and written/contractual rights are approved for storage, display, export, redistribution, attribution, retention, and territories. | Data-license owner | Enabling that provider/field |
| `M8-C03` | Privacy notices, retention/deletion schedules, processor terms, incident handling, and user-upload processing are approved per territory. | Privacy owner | Collecting user files or personal data |
| `M8-C04` | ASVS/LLMSVS control matrix, authenticated penetration test, dependency/license scan, SBOM, and closure of critical/high findings are complete. | Security owner | M13 exit and release |
| `M8-C05` | WCAG 2.2 AA audit and retail-user comprehension/usability tests meet the approved M13 thresholds. | Product/accessibility owner | Retail-ready claim |
| `M8-C06` | Eight pilots and two holdouts pass independent raw-to-normalized and identical-assumption valuation reconciliation. | Financial reviewer independent of executor | M13 exit and release |
| `M8-C07` | SEC, FCA, WCAG, OWASP standards, provider terms, and territory decisions are rechecked against then-current official sources. | Release owner | Implementation review and M14 release |

## External evidence rechecked

- SEC EDGAR data interfaces: <https://www.sec.gov/search-filings/edgar-application-programming-interfaces>
- SEC fair access, currently no more than 10 requests per second in aggregate: <https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data>
- FCA PERG 8 advice/information boundary: <https://handbook.fca.org.uk/handbook/perg8>
- FCA PERG 8.30B personal recommendations: <https://handbook.fca.org.uk/handbook/perg8/perg8s41>
- WCAG 2.2 Recommendation: <https://www.w3.org/TR/WCAG22/>
- OWASP ASVS 5.0.0 project: <https://owasp.org/www-project-application-security-verification-standard/>
- OWASP LLMSVS v2.0: <https://owasp.org/www-project-llm-verification-standard/LLMSVS-v2.0-en.html>

These references are design baselines, not certifications or legal opinions. Their versions and applicability must be checked again at the gates above.

## Source and repository boundary

No private PDF, ebook, extract, page image, real issuer record, provider response, or credential was required or read for this review. M8 reviews the product bridge over already approved M1-M7 methods; it adds no new book-derived valuation claim. Private sources remain outside the repository and are not runtime dependencies.

## Final authorization boundary

Recommendation: `[x] approve M9 implementation planning with conditions  [ ] request changes  [ ] reject`

Separate project-owner authorization remains required for staging, committing, pushing, creating a PR, M9 implementation planning, M9 implementation, live network/provider access, and every later release action.
