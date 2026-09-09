"""Parsing and formatting for byte size strings like "1.5 GiB" or "512B"."""

from __future__ import annotations

import math
import re

# Decimal units are powers of 1000, binary units are powers of 1024.
# Both show up in the wild -- disk vendors and network speeds use decimal,
# most OS tools report binary -- so we support both instead of guessing.
_DECIMAL_UNITS = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
_BINARY_UNITS = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"]

_UNIT_TO_MULTIPLIER = {}
for _i, _u in enumerate(_DECIMAL_UNITS):
    _UNIT_TO_MULTIPLIER[_u] = 1000**_i
for _i, _u in enumerate(_BINARY_UNITS):
    _UNIT_TO_MULTIPLIER[_u] = 1024**_i

_SIZE_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]+)\s*$")


class SizeParseError(ValueError):
    """Raised when a byte size string does not match the expected grammar."""


def parse_size(text: str) -> int:
    """Parse a byte size string into a whole number of bytes.

    Accepts a decimal number followed by a unit, e.g. "512B", "1.5 GB"
    (decimal, base 1000) or "1.5 GiB" (binary, base 1024). A bare
    number with no unit is treated as a raw byte count.
    """
    if not isinstance(text, str):
        raise SizeParseError(f"expected a string, got {type(text).__name__}")

    match = _SIZE_RE.match(text)
    if match is None:
        stripped = text.strip()
        if stripped.isdigit():
            return int(stripped)
        raise SizeParseError(f"not a valid size: {text!r}")

    number_part, unit_part = match.groups()
    unit = _normalize_unit(unit_part)
    if unit not in _UNIT_TO_MULTIPLIER:
        raise SizeParseError(f"unknown unit {unit_part!r} in {text!r}")

    value = float(number_part)
    return round(value * _UNIT_TO_MULTIPLIER[unit])


def _normalize_unit(unit: str) -> str:
    unit = unit.strip()
    if unit.lower() == "b":
        return "B"
    # case-insensitive match, since "gb", "Gb" and "GB" all mean the
    # same thing to whoever typed the string in.
    for known in _UNIT_TO_MULTIPLIER:
        if unit.lower() == known.lower():
            return known
    return unit


def format_size(num_bytes: int, binary: bool = False, precision: int = 2) -> str:
    """Format a byte count as a human-readable string.

    With binary=False (the default) uses decimal units (KB = 1000 bytes).
    With binary=True uses binary units (KiB = 1024 bytes), matching what
    tools like `du -h` typically show.
    """
    # inf/nan pass the "< 0" check below (comparisons against nan are
    # always false) and would otherwise fall through to int(inf) or a
    # silently bogus "nanEB", instead of the clean error callers expect.
    if not math.isfinite(num_bytes):
        raise ValueError(f"byte count must be finite, got {num_bytes!r}")
    if num_bytes < 0:
        raise ValueError("byte count cannot be negative")

    units = _BINARY_UNITS if binary else _DECIMAL_UNITS
    base = 1024 if binary else 1000

    value = float(num_bytes)
    unit = units[0]
    for candidate in units:
        unit = candidate
        if value < base or candidate is units[-1]:
            break
        value /= base

    if unit == "B":
        return f"{int(value)}{unit}"
    return f"{value:.{precision}f}{unit}"
