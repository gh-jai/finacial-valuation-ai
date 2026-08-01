from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "templates"


def test_template_frontmatter_is_parseable() -> None:
    parsed = 0
    for path in sorted(TEMPLATE_DIR.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != "---":
            continue
        end = lines.index("---", 1)
        metadata = yaml.safe_load("\n".join(lines[1:end]))
        assert isinstance(metadata, dict), f"{path.name} frontmatter must be a mapping"
        parsed += 1
    assert parsed == 6, "Expected frontmatter in six operational and artifact templates"
