import re
from pathlib import Path

import sizedur

_PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def test_version_matches_pyproject():
    # tomllib is 3.11+ and this package supports 3.9, so a small regex
    # is what stands in for a real TOML parser here.
    text = _PYPROJECT.read_text()
    match = re.search(r'(?m)^version = "([^"]+)"', text)
    assert match is not None, "no version field found in pyproject.toml"
    assert sizedur.__version__ == match.group(1)
