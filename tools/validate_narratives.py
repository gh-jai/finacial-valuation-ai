"""Validate narrative JSON and its cross-document audit invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
NARRATIVE_ROOT = ROOT / "benchmarks" / "fixtures" / "narratives"


def _validate_three_p(document: Mapping[str, Any]) -> list[str]:
    """Enforce the ordered possible -> plausible -> probable evidence ladder."""
    errors: list[str] = []
    three_p = document.get("three_p", {})
    results: dict[str, Any] = {}
    for level in ("possible", "plausible", "probable"):
        assessment = three_p.get(level, {})
        results[level] = assessment.get("result")
        if not assessment.get("reasoning") or not assessment.get("supporting_evidence"):
            errors.append(f"3P {level} assessment requires reasoning and evidence")

    if results.get("possible") != "pass" and results.get("plausible") == "pass":
        errors.append("3P plausible cannot pass unless possible passes")
    if results.get("possible") != "pass" and results.get("probable") == "pass":
        errors.append("3P probable cannot pass unless possible passes")
    if results.get("plausible") != "pass" and results.get("probable") == "pass":
        errors.append("3P probable cannot pass unless plausible passes")

    if results.get("possible") != "pass":
        expected_overall = "fails-possible"
    elif results.get("plausible") != "pass":
        expected_overall = "possible"
    elif results.get("probable") != "pass":
        expected_overall = "plausible"
    else:
        expected_overall = "probable"
    overall = three_p.get("overall")
    if overall in {"fails-possible", "possible", "plausible", "probable"}:
        if overall != expected_overall:
            errors.append(
                f"3P overall must equal highest consecutive passed level: {expected_overall}"
            )
    return errors


def validate_narrative_document(
    document: Mapping[str, Any],
    schema: Mapping[str, Any],
    source_ids: set[str],
    claim_ids: set[str],
) -> list[str]:
    errors = [
        f"schema {'.'.join(map(str, error.path)) or '<root>'}: {error.message}"
        for error in sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
            key=lambda item: list(item.path),
        )
    ]
    assertions = document.get("assertions", [])
    assertion_ids = [item.get("id") for item in assertions if isinstance(item, Mapping)]
    if len(assertion_ids) != len(set(assertion_ids)):
        errors.append("assertion IDs must be unique")
    mapped_ids = {
        item.get("assertion_id")
        for item in document.get("value_driver_mappings", [])
        if isinstance(item, Mapping)
    }
    for assertion in assertions:
        if not isinstance(assertion, Mapping):
            continue
        assertion_id = assertion.get("id")
        status = assertion.get("quantification_status")
        if status == "mapped" and assertion_id not in mapped_ids:
            errors.append(f"mapped assertion {assertion_id} has no value-driver mapping")
        if assertion_id in mapped_ids and status != "mapped":
            errors.append(f"mapping references assertion {assertion_id} not marked mapped")
        if (
            status == "unquantified-limitation"
            and "limitation" not in assertion.get("statement", "").lower()
        ):
            errors.append(
                f"unquantified assertion {assertion_id} must explicitly state its limitation"
            )
    unknown = mapped_ids - set(assertion_ids)
    if unknown:
        errors.append(f"mappings reference unknown assertions: {', '.join(sorted(unknown))}")

    errors.extend(_validate_three_p(document))

    current_id = document.get("id")
    alternative_ids = [item.get("narrative_id") for item in document.get("alternatives", [])]
    if current_id in alternative_ids:
        errors.append("alternative narrative ID must differ from current narrative ID")
    if len(alternative_ids) != len(set(alternative_ids)):
        errors.append("alternative narratives must remain separate; duplicate IDs found")

    history = document.get("revision_history", [])
    versions = [item.get("version") for item in history if isinstance(item, Mapping)]
    if len(versions) != len(set(versions)):
        errors.append("revision history versions must be unique")
    seen: set[str] = set()
    for index, revision in enumerate(history):
        version = revision.get("version")
        previous = revision.get("previous_version_ref")
        if index == 0 and (revision.get("classification") != "initial" or previous is not None):
            errors.append("revision history must begin with an initial version")
        if index > 0 and previous not in seen:
            errors.append(f"revision {version} does not preserve a prior version reference")
        seen.add(version)

    refs: list[str] = list(document.get("source_refs", []))
    for assertion in assertions:
        refs.extend(assertion.get("supporting_evidence", []))
        refs.extend(assertion.get("contradicting_evidence", []))
    for mapping in document.get("value_driver_mappings", []):
        refs.extend(mapping.get("evidence_refs", []))
    for ref in refs:
        if ref.startswith("SRC-") and ref not in source_ids:
            errors.append(f"unknown source reference {ref}")
        if ref.startswith("CLM-") and ref not in claim_ids:
            errors.append(f"unknown claim reference {ref}")
    return errors


def validate_repository(root: Path = ROOT) -> tuple[list[str], int]:
    schema = json.loads(
        (root / "schemas" / "narrative.schema.json").read_text(encoding="utf-8")
    )
    catalog = yaml.safe_load((root / "sources" / "catalog.yaml").read_text(encoding="utf-8"))
    source_ids = {item["id"] for item in catalog["sources"]}
    claim_ids: set[str] = set()
    for path in (root / "extraction" / "reviewed").glob("*.yaml"):
        claim_ids.update(
            item["id"] for item in yaml.safe_load(path.read_text(encoding="utf-8"))["claims"]
        )
    errors: list[str] = []
    paths = sorted((root / "benchmarks" / "fixtures" / "narratives").glob("*.json"))
    documents: list[Mapping[str, Any]] = []
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        documents.append(document)
        errors.extend(
            f"{path.relative_to(root)}: {error}"
            for error in validate_narrative_document(document, schema, source_ids, claim_ids)
        )
    document_ids = {item.get("id") for item in documents}
    for document in documents:
        for alternative in document.get("alternatives", []):
            if (
                alternative["status"] == "active"
                and alternative["narrative_id"] not in document_ids
            ):
                errors.append(
                    f"{document['id']}: active alternative "
                    f"{alternative['narrative_id']} has no separate document"
                )
    return errors, len(paths)


def main() -> int:
    try:
        errors, count = validate_repository()
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Narrative validation failed: {exc}")
        return 1
    if errors:
        print("Narrative validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validated {count} narrative document(s) and cross-document invariants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
