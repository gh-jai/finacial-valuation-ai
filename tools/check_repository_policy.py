"""Reject repository candidates that violate FVI's private-source boundary."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
PROHIBITED_SUFFIXES = {".pdf", ".epub", ".mobi"}
PROHIBITED_DIRECTORIES = {"raw-copyrighted-extracts", "copyrighted-extracts"}


def violation_for(path_text: str) -> str | None:
    """Return the policy violation for a repository-relative path, if any."""
    path = PurePosixPath(path_text.replace("\\", "/"))
    lowered_parts = tuple(part.lower() for part in path.parts)
    lowered_name = path.name.lower()

    if len(lowered_parts) >= 2 and lowered_parts[:2] == ("sources", "private"):
        return "private source paths may not be tracked"
    if any(part in PROHIBITED_DIRECTORIES for part in lowered_parts):
        return "copyrighted extract directories may not be tracked"
    if len(lowered_parts) >= 2 and lowered_parts[:2] == ("extraction", "raw-notes"):
        if lowered_name != ".gitkeep":
            return "raw extraction notes may not be tracked"
    if path.suffix.lower() in PROHIBITED_SUFFIXES:
        return f"{path.suffix.lower()} source files may not be tracked"
    if lowered_name.endswith(".extract.txt"):
        return "raw extract files may not be tracked"
    return None


def repository_candidates() -> list[str]:
    """Return tracked and non-ignored untracked paths, including pre-initial-commit files."""
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT.as_posix()}",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.decode(errors="replace").strip()
        raise RuntimeError(f"unable to inspect repository candidates: {message}")
    return [item.decode(errors="surrogateescape") for item in result.stdout.split(b"\0") if item]


def main() -> int:
    try:
        candidates = repository_candidates()
    except (OSError, RuntimeError) as exc:
        print(f"Repository policy check failed: {exc}")
        return 1

    violations = [
        (path, reason) for path in candidates if (reason := violation_for(path)) is not None
    ]
    if violations:
        print("Repository content policy violations:")
        for path, reason in violations:
            print(f"- {path}: {reason}")
        return 1
    print(f"Checked {len(candidates)} repository candidate file(s); no prohibited sources found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
