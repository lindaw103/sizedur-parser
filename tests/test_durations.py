import pytest

from sizedur import DurationParseError, format_duration, parse_duration


class TestParseDuration:
    def test_single_chunk(self):
        assert parse_duration("2.5s") == 2.5
        assert parse_duration("500ms") == 0.5

    def test_compound_chunks(self):
        assert parse_duration("1h30m") == 5400.0
        assert parse_duration("1d2h3m4s") == 86400 + 2 * 3600 + 3 * 60 + 4

    def test_all_units(self):
        assert parse_duration("1d") == 86400.0
        assert parse_duration("1h") == 3600.0
        assert parse_duration("1m") == 60.0
        assert parse_duration("1s") == 1.0
        assert parse_duration("1ms") == 0.001
        assert parse_duration("1us") == 0.000001
        assert parse_duration("1ns") == 0.000000001

    def test_strips_outer_whitespace(self):
        assert parse_duration("  1h  ") == 3600.0

    def test_rejects_non_string(self):
        with pytest.raises(DurationParseError):
            parse_duration(3600)

    def test_rejects_empty_string(self):
        with pytest.raises(DurationParseError):
            parse_duration("")

    def test_rejects_whitespace_only(self):
        with pytest.raises(DurationParseError):
            parse_duration("   ")

    def test_rejects_unknown_unit(self):
        with pytest.raises(DurationParseError):
            parse_duration("1x")

    def test_rejects_trailing_garbage(self):
        with pytest.raises(DurationParseError):
            parse_duration("1h!")

    def test_allows_whitespace_between_chunks(self):
        assert parse_duration("1h 30m") == 5400.0
        assert parse_duration("1d  2h   3m") == 86400 + 2 * 3600 + 3 * 60

    def test_rejects_whitespace_inside_a_chunk(self):
        with pytest.raises(DurationParseError):
            parse_duration("1 h30m")

    def test_rejects_negative(self):
        with pytest.raises(DurationParseError):
            parse_duration("-5s")


class TestFormatDuration:
    def test_zero(self):
        assert format_duration(0) == "0s"

    def test_sub_second(self):
        assert format_duration(0.5) == "500ms"

    def test_seconds_only(self):
        assert format_duration(30) == "30s"

    def test_compound(self):
        assert format_duration(5400) == "1h30m"
        assert format_duration(90) == "1m30s"

    def test_drops_zero_units(self):
        assert format_duration(86400 + 5) == "1d5s"

    def test_precision_on_sub_second(self):
        assert format_duration(0.5, precision=2) == "500.00ms"

    def test_sub_second_remainder_on_longer_duration(self):
        assert format_duration(1.5) == "1s500ms"
        assert format_duration(90.5) == "1m30s500ms"

    def test_precision_on_sub_second_remainder(self):
        assert format_duration(1.25, precision=2) == "1s250.00ms"

    def test_ignores_negligible_float_noise(self):
        # 0.1h in seconds picks up float error far below 1ns; that
        # noise should be dropped rather than printed as a bogus unit.
        assert format_duration(0.1 * 3600) == "6m"

    def test_rejects_negative(self):
        with pytest.raises(ValueError):
            format_duration(-1)

    def test_rejects_infinity(self):
        with pytest.raises(ValueError):
            format_duration(float("inf"))

    def test_rejects_nan(self):
        with pytest.raises(ValueError):
            format_duration(float("nan"))

    def test_round_trips_through_parse(self):
        for text in ["1d5s", "1h30m", "1m30s", "30s"]:
            assert format_duration(parse_duration(text)) == text
