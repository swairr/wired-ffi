"""Core FFI functionality for wired-ffi."""

import json
import pickle
import sys
from pathlib import Path
from typing import Any


class SerializationError(Exception):
    """Raised when serialization/deserialization fails."""

    pass


class FFISerializer:
    """Handles serialization and deserialization for FFI operations."""

    def __init__(self, format: str = "json"):
        """Initialize serializer with specified format.

        Args:
            format: Serialization format ("json", "pickle", "msgpack")
        """
        self.format = format.lower()
        self._validate_format()

    def _validate_format(self) -> None:
        """Validate the serialization format."""
        supported_formats = ["json", "pickle", "msgpack"]
        if self.format not in supported_formats:
            raise ValueError(
                f"Unsupported format: {self.format}. "
                f"Supported formats: {supported_formats}"
            )

    def serialize(self, data: Any, output_path: str | Path) -> None:
        """Serialize data to file.

        Args:
            data: Data to serialize
            output_path: Output file path
        """
        try:
            output_path = Path(output_path)

            if self.format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            elif self.format == "pickle":
                with open(output_path, "wb") as f:
                    pickle.dump(data, f)

            elif self.format == "msgpack":
                try:
                    import msgpack  # pyright: ignore
                except ImportError as e:
                    raise SerializationError(
                        "msgpack library not installed. "
                        "Install with: pip install msgpack"
                    ) from e

                with open(output_path, "wb") as f:
                    msgpack.pack(data, f)  # pyright: ignore

        except Exception as e:
            raise SerializationError(f"Failed to serialize data: {e}") from e

    def deserialize(self, input_path: str | Path) -> Any:
        """Deserialize data from file.

        Args:
            input_path: Input file path

        Returns:
            Deserialized data
        """
        try:
            input_path = Path(input_path)

            if self.format == "json":
                with open(input_path, encoding="utf-8") as f:
                    return json.load(f)

            elif self.format == "pickle":
                with open(input_path, "rb") as f:
                    return pickle.load(f)

            elif self.format == "msgpack":
                try:
                    import msgpack  # pyright: ignore
                except ImportError as e:
                    raise SerializationError(
                        "msgpack library not installed. "
                        "Install with: pip install msgpack"
                    ) from e

                with open(input_path, "rb") as f:
                    return msgpack.unpack(f)  # pyright: ignore

        except Exception as e:
            raise SerializationError(f"Failed to deserialize data: {e}") from e


class FFIBridge:
    """Bridge for cross-language function calls through serialization."""

    def __init__(self, serializer: FFISerializer):
        """Initialize FFI bridge with serializer.

        Args:
            serializer: Serializer instance to use
        """
        self.serializer = serializer

    def call_function(self, function_data: dict[str, Any]) -> dict[str, Any]:
        """Call a function through FFI.

        Args:
            function_data: Function call data including name, args, kwargs

        Returns:
            Function result data
        """
        # TODO: Implement actual FFI function calling
        # This is a placeholder implementation

        function_name = function_data.get("function_name", "unknown")
        args = function_data.get("args", [])
        kwargs = function_data.get("kwargs", {})

        # Simulate function call
        result = {
            "status": "success",
            "function_name": function_name,
            "args": args,
            "kwargs": kwargs,
            "result": f"Called {function_name} with args {args} and kwargs {kwargs}",
            "timestamp": str(sys.version_info),
        }

        return result

    def process_request(
        self, request_path: str | Path, response_path: str | Path
    ) -> None:
        """Process FFI request from file and write response.

        Args:
            request_path: Path to request file
            response_path: Path to response file
        """
        try:
            # Deserialize request
            request_data = self.serializer.deserialize(request_path)

            # Process function call
            response_data = self.call_function(request_data)

            # Serialize response
            self.serializer.serialize(response_data, response_path)

        except Exception as e:
            error_response = {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
            }
            self.serializer.serialize(error_response, response_path)
