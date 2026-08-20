"""Parsing and formatting for compound duration strings like "1h30m" or "2.5s"."""

from __future__ import annotations

import re

# Ordered largest to smallest so parsing and formatting can both walk
# the list in one direction instead of needing separate tables.
_UNIT_SECONDS = [
    ("d", 86400),
    ("h", 3600),
    ("m", 60),
    ("s", 1),
    ("ms", 0.001),
    ("us", 0.000001),
    ("ns", 0.000000001),
]
_UNIT_SECONDS_MAP = dict(_UNIT_SECONDS)

# A single "<number><unit>" chunk, e.g. "1.5h" or "500ms". Longer unit
# names ("ms", "us", "ns") must come before "s" or the alternation
# would stop at "s" and leave a dangling "m"/"u"/"n".
_CHUNK_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)(d|h|m|ms|us|ns|s)")


class DurationParseError(ValueError):
    """Raised when a duration string does not match the expected grammar."""


def parse_duration(text: str) -> float:
    """Parse a compound duration string into a number of seconds.

    Accepts one or more "<number><unit>" chunks concatenated together,
    e.g. "1h30m", "2.5s", "500ms". Units: d, h, m, s, ms, us, ns.
    """
    if not isinstance(text, str):
        raise DurationParseError(f"expected a string, got {type(text).__name__}")

    stripped = text.strip()
    if not stripped:
        raise DurationParseError("empty duration string")

    total = 0.0
    pos = 0
    matched_any = False

    while pos < len(stripped):
        match = _CHUNK_RE.match(stripped, pos)
        if match is None:
            raise DurationParseError(
                f"could not parse {stripped[pos:]!r} in duration {text!r}"
            )
        number, unit = match.groups()
        total += float(number) * _UNIT_SECONDS_MAP[unit]
        pos = match.end()
        matched_any = True

    if not matched_any:
        raise DurationParseError(f"not a valid duration: {text!r}")

    return total


def format_duration(total_seconds: float, precision: int = 0) -> str:
    """Format a number of seconds as a compound duration string.

    Drops units that would contribute zero, so 90 seconds formats as
    "1m30s" rather than "0d0h1m30s". Sub-second totals fall back to
    the largest sub-second unit so short durations stay readable.
    """
    if total_seconds < 0:
        raise ValueError("duration cannot be negative")

    if total_seconds == 0:
        return "0s"

    if total_seconds < 1:
        for unit, size in _UNIT_SECONDS[4:]:
            value = total_seconds / size
            if value >= 1:
                return f"{value:.{precision}f}{unit}"
        return f"{total_seconds}s"

    remaining = total_seconds
    parts = []
    for unit, size in _UNIT_SECONDS[:4]:
        count, remaining = divmod(remaining, size)
        if count:
            parts.append(f"{int(count)}{unit}")

    return "".join(parts) if parts else "0s"
