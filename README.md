# sizedur

Config files and CLI flags are full of strings like `500ms`, `2h30m`,
`1.5GiB`, and `10MB`. Every project that reads them either pulls in a
dependency for it or writes a slightly-wrong regex by hand. This is the
small, dependency-free version: a parser that validates and normalizes
those strings, and a formatter that turns numbers back into readable
ones.

Byte sizes and durations are the two units where "how big" and "how
long" get written down in dozens of interchangeable ways, so it made
sense to handle both with the same shape of code rather than pulling
in two separate one-off helpers.

## Usage

```python
from sizedur import parse_size, format_size, parse_duration, format_duration

parse_size("1.5GB")        # 1500000000  (decimal, base 1000)
parse_size("1.5GiB")       # 1610612736  (binary, base 1024)
parse_size("512")          # 512         (bare number = bytes)

format_size(1610612736, binary=True)   # "1.50GiB"
format_size(1500000000)                # "1.50GB"

parse_duration("1h30m")    # 5400.0 (seconds)
parse_duration("500ms")    # 0.5
parse_duration("2.5s")     # 2.5

format_duration(5400)      # "1h30m"
format_duration(0.5)       # "500ms"
```

Invalid input raises `SizeParseError` or `DurationParseError` (both
subclass `ValueError`) instead of silently returning something wrong:

```python
>>> parse_size("12 furlongs")
sizedur.sizes.SizeParseError: unknown unit 'furlongs' in '12 furlongs'
```

## Supported units

- Sizes: `B`, `KB`/`MB`/`GB`/`TB`/`PB`/`EB` (decimal, x1000), `KiB`/`MiB`/`GiB`/`TiB`/`PiB`/`EiB` (binary, x1024). Case-insensitive.
- Durations: `d`, `h`, `m`, `s`, `ms`, `us`, `ns`, combinable in one string (`1d2h3m4s`).

## Status

Early. The parsing grammar is deliberately simple (no negative sizes
or durations) and will get stricter edge-case handling over time.
Covered by a pytest suite
(`pip install -e .[test]` then `pytest`).

## License

MIT, see LICENSE.
