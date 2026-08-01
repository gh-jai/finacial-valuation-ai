from tools.check_repository_policy import violation_for


def test_prohibited_source_extensions_are_case_insensitive() -> None:
    assert violation_for("documents/private-book.PDF")
    assert violation_for("documents/private-book.EpUb")
    assert violation_for("documents/private-book.MOBI")


def test_private_and_raw_extract_paths_are_rejected() -> None:
    assert violation_for("sources/private/book.txt")
    assert violation_for("extraction/raw-notes/chapter-01.md")
    assert violation_for("notes/raw-copyrighted-extracts/chapter.txt")
    assert violation_for("notes/chapter.extract.txt")


def test_framework_files_and_raw_notes_placeholder_are_allowed() -> None:
    assert violation_for("schemas/source.schema.json") is None
    assert violation_for("extraction/raw-notes/.gitkeep") is None
