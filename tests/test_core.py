"""Test core FFI functionality."""

import json
import tempfile
from pathlib import Path

import pytest

from wired_ffi.core import FFIBridge, FFISerializer, SerializationError


class TestFFISerializer:
    """Test FFI serializer functionality."""

    def test_json_serialization(self) -> None:
        """Test JSON serialization and deserialization."""
        serializer = FFISerializer("json")
        test_data = {"key": "value", "number": 42, "bool": True}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Test serialization
            serializer.serialize(test_data, temp_path)
            assert temp_path.exists()

            # Test deserialization
            result = serializer.deserialize(temp_path)
            assert result == test_data
        finally:
            temp_path.unlink(missing_ok=True)

    def test_pickle_serialization(self) -> None:
        """Test Pickle serialization and deserialization."""
        serializer = FFISerializer("pickle")
        test_data = {"key": "value", "complex": [1, 2, {"nested": True}]}

        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Test serialization
            serializer.serialize(test_data, temp_path)
            assert temp_path.exists()

            # Test deserialization
            result = serializer.deserialize(temp_path)
            assert result == test_data
        finally:
            temp_path.unlink(missing_ok=True)

    def test_invalid_format(self) -> None:
        """Test invalid serialization format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            FFISerializer("invalid_format")

    def test_serialization_error(self) -> None:
        """Test serialization error handling."""
        serializer = FFISerializer("json")

        # Try to serialize non-JSON-serializable object
        class NonSerializable:
            pass

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            with pytest.raises(SerializationError):
                serializer.serialize(NonSerializable(), temp_path)
        finally:
            temp_path.unlink(missing_ok=True)


class TestFFIBridge:
    """Test FFI bridge functionality."""

    def test_function_call(self) -> None:
        """Test basic function call functionality."""
        serializer = FFISerializer("json")
        bridge = FFIBridge(serializer)

        function_data = {
            "function_name": "test_function",
            "args": [1, 2, 3],
            "kwargs": {"key": "value"},
        }

        result = bridge.call_function(function_data)

        assert result["status"] == "success"
        assert result["function_name"] == "test_function"
        assert result["args"] == [1, 2, 3]
        assert result["kwargs"] == {"key": "value"}
        assert "result" in result
        assert "timestamp" in result

    def test_process_request(self) -> None:
        """Test request processing."""
        serializer = FFISerializer("json")
        bridge = FFIBridge(serializer)

        request_data = {
            "function_name": "process_test",
            "args": ["arg1", "arg2"],
            "kwargs": {"param": "value"},
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as request_file:
            json.dump(request_data, request_file)
            request_path = Path(request_file.name)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as response_file:
            response_path = Path(response_file.name)

        try:
            bridge.process_request(request_path, response_path)

            assert response_path.exists()

            with open(response_path) as f:
                response_data = json.load(f)

            assert response_data["status"] == "success"
            assert response_data["function_name"] == "process_test"

        finally:
            request_path.unlink(missing_ok=True)
            response_path.unlink(missing_ok=True)

    def test_error_handling(self) -> None:
        """Test error handling in request processing."""
        serializer = FFISerializer("json")
        bridge = FFIBridge(serializer)

        # Create invalid request file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as request_file:
            request_file.write("invalid json content")
            request_path = Path(request_file.name)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as response_file:
            response_path = Path(response_file.name)

        try:
            bridge.process_request(request_path, response_path)

            assert response_path.exists()

            with open(response_path) as f:
                response_data = json.load(f)

            assert response_data["status"] == "error"
            assert "error" in response_data
            assert "error_type" in response_data

        finally:
            request_path.unlink(missing_ok=True)
            response_path.unlink(missing_ok=True)


@pytest.mark.integration
class TestIntegration:
    """Integration tests."""

    def test_end_to_end_workflow(self) -> None:
        """Test complete end-to-end workflow."""
        # Test data
        original_data = {
            "user": "test_user",
            "data": [1, 2, 3, 4, 5],
            "metadata": {"version": "1.0", "type": "test"},
        }

        # Step 1: Serialize to JSON
        json_serializer = FFISerializer("json")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            json_path = Path(f.name)

        json_serializer.serialize(original_data, json_path)

        # Step 2: Deserialize and re-serialize to Pickle
        deserialized_data = json_serializer.deserialize(json_path)
        assert deserialized_data == original_data

        pickle_serializer = FFISerializer("pickle")
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle_path = Path(f.name)

        pickle_serializer.serialize(deserialized_data, pickle_path)

        # Step 3: Deserialize from Pickle
        final_data = pickle_serializer.deserialize(pickle_path)
        assert final_data == original_data

        # Cleanup
        json_path.unlink(missing_ok=True)
        pickle_path.unlink(missing_ok=True)
