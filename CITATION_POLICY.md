# Citation Policy

FVI citations make knowledge traceable without reproducing source works.

## Source IDs and locations

Every external source receives an exact, stable ID in `sources/catalog.yaml`, such as `SRC-PRIVATE-001`. Claims reference that ID and a precise location appropriate to the medium: page and section, chapter and heading, table number, timestamp, paragraph, or stable URL fragment. A citation must be specific enough for a lawful holder of the source to verify it.

Do not use filenames as source identity, and do not put private absolute paths in tracked files. Optional `private_locator` values must be relative to `sources/private/` and contain no secrets.

## Claim types

- `source_statement`: a faithful, compact paraphrase or a necessary short quotation of what the source states.
- `derived_rule`: an original operational rule transparently derived from one or more source statements.
- `model_inference`: a conclusion generated from supplied evidence or calculations that the source does not itself assert.

These types must remain distinct. Never present a derived rule or model inference as a sourced statement.

## Copyright boundary

Prefer original paraphrase. Quote only the minimum needed for criticism, verification, or terminology, and never store long passages, chapter substitutes, sequential extracts, figures, or tables copied from copyrighted works. Location references do not authorize redistribution. Raw PDFs, ebooks, scans, and extraction dumps are prohibited in version control.

## Citation quality

Record the source ID, exact location, claim type, and reviewer status. When sources conflict, preserve each position and document the reconciliation rather than silently merging them. Derived artifacts must carry forward the source references that materially support them.
