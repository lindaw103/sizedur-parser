import pytest

from sizedur import SizeParseError, format_size, parse_size


class TestParseSize:
    def test_bare_number_is_bytes(self):
        assert parse_size("512") == 512

    def test_decimal_units(self):
        assert parse_size("1.5GB") == 1_500_000_000
        assert parse_size("10MB") == 10_000_000
        assert parse_size("1KB") == 1_000

    def test_binary_units(self):
        assert parse_size("1.5GiB") == 1_610_612_736
        assert parse_size("1KiB") == 1024

    def test_unit_is_case_insensitive(self):
        assert parse_size("1.5gb") == 1_500_000_000
        assert parse_size("1.5Gb") == 1_500_000_000
        assert parse_size("1gib") == 1_073_741_824

    def test_bytes_unit_variants(self):
        assert parse_size("5B") == 5
        assert parse_size("5b") == 5

    def test_allows_space_before_unit(self):
        assert parse_size("1.5 GB") == 1_500_000_000

    def test_rejects_non_string(self):
        with pytest.raises(SizeParseError):
            parse_size(512)

    def test_rejects_empty_string(self):
        with pytest.raises(SizeParseError):
            parse_size("")

    def test_rejects_negative(self):
        with pytest.raises(SizeParseError):
            parse_size("-5B")

    def test_rejects_unknown_unit(self):
        with pytest.raises(SizeParseError, match="furlongs"):
            parse_size("12 furlongs")


class TestFormatSize:
    def test_zero(self):
        assert format_size(0) == "0B"

    def test_decimal(self):
        assert format_size(1_500_000_000) == "1.50GB"
        assert format_size(999) == "999B"

    def test_binary(self):
        assert format_size(1_610_612_736, binary=True) == "1.50GiB"
        assert format_size(1023, binary=True) == "1023B"

    def test_precision(self):
        assert format_size(1_500_000_000, precision=0) == "2GB"
        assert format_size(1_500_000_000, precision=4) == "1.5000GB"

    def test_top_unit_does_not_overflow(self):
        huge = 2 * 1000**6
        assert format_size(huge) == "2.00EB"

    def test_rejects_negative(self):
        with pytest.raises(ValueError):
            format_size(-1)

    def test_rejects_infinity(self):
        with pytest.raises(ValueError):
            format_size(float("inf"))

    def test_rejects_nan(self):
        with pytest.raises(ValueError):
            format_size(float("nan"))

    def test_round_trips_through_parse(self):
        for text in ["1.50KB", "2.00MB", "1.50GiB"]:
            assert format_size(parse_size(text), binary="i" in text) == text
