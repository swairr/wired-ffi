"""Test CLI functionality."""

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from wired_ffi.main import main


class TestCLI:
    """Test CLI commands."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_help_command(self) -> None:
        """Test help command."""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "wired-ffi" in result.output
        assert "FFI(Foreign Function Interface)" in result.output

    def test_info_command(self) -> None:
        """Test info command."""
        result = self.runner.invoke(main, ["info"])
        assert result.exit_code == 0
        assert "wired-ffi v0.1.0" in result.output
        assert "Supported formats:" in result.output

    def test_version_command(self) -> None:
        """Test version command."""
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0

    def test_serialize_command(self) -> None:
        """Test serialize command."""
        test_data = {"test": "data", "number": 42}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as input_file:
            json.dump(test_data, input_file)
            input_path = input_file.name

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as output_file:
            output_path = output_file.name

        try:
            result = self.runner.invoke(
                main, ["serialize", "--format", "json", input_path, output_path]
            )

            assert result.exit_code == 0
            assert "Serialized to" in result.output

            # Verify output file exists and contains correct data
            assert Path(output_path).exists()
            with open(output_path) as f:
                output_data = json.load(f)
            assert output_data == test_data

        finally:
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def test_deserialize_command(self) -> None:
        """Test deserialize command."""
        test_data = {"test": "data", "items": [1, 2, 3]}

        # Create pickle file
        from wired_ffi.core import FFISerializer

        serializer = FFISerializer("pickle")

        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as input_file:
            input_path = input_file.name

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as output_file:
            output_path = output_file.name

        try:
            serializer.serialize(test_data, input_path)

            result = self.runner.invoke(
                main, ["deserialize", "--format", "pickle", input_path, output_path]
            )

            assert result.exit_code == 0
            assert "Deserialized to" in result.output

            # Verify output file exists and contains correct data
            assert Path(output_path).exists()
            with open(output_path) as f:
                output_data = json.load(f)
            assert output_data == test_data

        finally:
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def test_call_command(self) -> None:
        """Test FFI call command."""
        request_data = {
            "function_name": "test_function",
            "args": [1, 2, 3],
            "kwargs": {"param": "value"},
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as request_file:
            json.dump(request_data, request_file)
            request_path = request_file.name

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as response_file:
            response_path = response_file.name

        try:
            result = self.runner.invoke(main, ["call", request_path, response_path])

            assert result.exit_code == 0
            assert "FFI call completed" in result.output

            # Verify response file exists and contains expected data
            assert Path(response_path).exists()
            with open(response_path) as f:
                response_data = json.load(f)

            assert response_data["status"] == "success"
            assert response_data["function_name"] == "test_function"
            assert response_data["args"] == [1, 2, 3]
            assert response_data["kwargs"] == {"param": "value"}

        finally:
            Path(request_path).unlink(missing_ok=True)
            Path(response_path).unlink(missing_ok=True)

    def test_verbose_mode(self) -> None:
        """Test verbose mode."""
        result = self.runner.invoke(main, ["--verbose", "info"])
        assert result.exit_code == 0
        assert "Verbose mode enabled" in result.output

    def test_invalid_format(self) -> None:
        """Test invalid format handling."""
        test_data = {"test": "data"}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as input_file:
            json.dump(test_data, input_file)
            input_path = input_file.name

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as output_file:
            output_path = output_file.name

        try:
            result = self.runner.invoke(
                main, ["serialize", "--format", "invalid", input_path, output_path]
            )

            assert result.exit_code == 2  # Click validation error

        finally:
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def test_nonexistent_input_file(self) -> None:
        """Test handling of nonexistent input file."""
        result = self.runner.invoke(
            main, ["serialize", "--format", "json", "nonexistent.json", "output.json"]
        )

        assert result.exit_code == 2  # Click file validation error
