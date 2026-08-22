"""Command-line entry point for quick size/duration conversions.

The direction is inferred from the input: a plain number is formatted
into a human-readable string, anything else is parsed as one. That
way `sizedur size 1.5GiB` and `sizedur size 1610612736` are both
useful without a separate --parse/--format flag to remember.
"""

from __future__ import annotations

import argparse
import sys

from .durations import DurationParseError, format_duration, parse_duration
from .sizes import SizeParseError, format_size, parse_size


def _is_plain_number(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


def _run_size(value: str, binary: bool, precision: int) -> str:
    if _is_plain_number(value):
        return format_size(round(float(value)), binary=binary, precision=precision)
    return str(parse_size(value))


def _run_duration(value: str, precision: int) -> str:
    if _is_plain_number(value):
        return format_duration(float(value), precision=precision)
    return str(parse_duration(value))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sizedur",
        description="Convert between human-readable size/duration strings and raw numbers.",
    )
    subparsers = parser.add_subparsers(dest="kind", required=True)

    size_parser = subparsers.add_parser("size", help="convert a byte size")
    size_parser.add_argument(
        "value", help="a size string (e.g. 1.5GiB) or a plain byte count"
    )
    size_parser.add_argument(
        "--binary",
        action="store_true",
        help="use binary units (KiB, MiB, ...) when formatting",
    )
    size_parser.add_argument(
        "--precision",
        type=int,
        default=2,
        help="decimal places when formatting (default: 2)",
    )

    duration_parser = subparsers.add_parser("duration", help="convert a duration")
    duration_parser.add_argument(
        "value", help="a duration string (e.g. 1h30m) or a plain second count"
    )
    duration_parser.add_argument(
        "--precision",
        type=int,
        default=0,
        help="decimal places when formatting (default: 0)",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.kind == "size":
            print(_run_size(args.value, args.binary, args.precision))
        else:
            print(_run_duration(args.value, args.precision))
    except (SizeParseError, DurationParseError, ValueError) as exc:
        print(f"sizedur: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
