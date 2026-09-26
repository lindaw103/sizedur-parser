import pytest

import sizedur
from sizedur.cli import main


class TestVersionFlag:
    def test_prints_version_and_exits_zero(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            main(["--version"])
        assert excinfo.value.code == 0
        assert capsys.readouterr().out.strip() == f"sizedur {sizedur.__version__}"


class TestSizeCommand:
    def test_parse_string(self, capsys):
        assert main(["size", "1.5GiB"]) == 0
        assert capsys.readouterr().out == "1610612736\n"

    def test_format_number_decimal_by_default(self, capsys):
        assert main(["size", "1500000000"]) == 0
        assert capsys.readouterr().out == "1.50GB\n"

    def test_format_number_binary_flag(self, capsys):
        assert main(["size", "1610612736", "--binary"]) == 0
        assert capsys.readouterr().out == "1.50GiB\n"

    def test_format_respects_precision(self, capsys):
        assert main(["size", "1500000000", "--precision", "0"]) == 0
        assert capsys.readouterr().out == "2GB\n"

    def test_invalid_input_reports_error_and_exit_code(self, capsys):
        assert main(["size", "12 furlongs"]) == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "furlongs" in captured.err

    def test_negative_number_reports_error(self, capsys):
        assert main(["size", "-5"]) == 1
        assert "negative" in capsys.readouterr().err

    def test_infinity_reports_parse_error_instead_of_crashing(self, capsys):
        assert main(["size", "inf"]) == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err.startswith("sizedur:")

    def test_nan_reports_parse_error_instead_of_crashing(self, capsys):
        assert main(["size", "nan"]) == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err.startswith("sizedur:")


class TestDurationCommand:
    def test_parse_string(self, capsys):
        assert main(["duration", "1h30m"]) == 0
        assert capsys.readouterr().out == "5400.0\n"

    def test_format_number(self, capsys):
        assert main(["duration", "5400"]) == 0
        assert capsys.readouterr().out == "1h30m\n"

    def test_format_respects_precision(self, capsys):
        assert main(["duration", "0.5", "--precision", "2"]) == 0
        assert capsys.readouterr().out == "500.00ms\n"

    def test_invalid_input_reports_error_and_exit_code(self, capsys):
        assert main(["duration", "1x"]) == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err.startswith("sizedur:")

    def test_infinity_reports_parse_error_instead_of_crashing(self, capsys):
        assert main(["duration", "inf"]) == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err.startswith("sizedur:")
