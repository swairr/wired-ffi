"""Main entry point for wired-ffi CLI application."""

import click

from .core import FFIBridge, FFISerializer, SerializationError


@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """wired-ffi: FFI(Foreign Function Interface) library based on serialization.

    A tool for simplifying cross-language function calls and data exchange
    through serialization mechanisms.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    if verbose:
        click.echo("Verbose mode enabled")


@main.command()
@click.option(
    "--format",
    "-f",
    default="json",
    type=click.Choice(["json", "pickle", "msgpack"]),
    help="Serialization format to use",
)
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.pass_context
def serialize(
    ctx: click.Context, format: str, input_file: str, output_file: str
) -> None:
    """Serialize data from input file to output file."""
    verbose = ctx.obj.get("verbose", False)

    try:
        # Read input data (assuming it's a JSON file for now)
        import json

        with open(input_file, encoding="utf-8") as f:
            data = json.load(f)

        # Create serializer and serialize
        serializer = FFISerializer(format)
        serializer.serialize(data, output_file)

        if verbose:
            click.echo(
                f"Successfully serialized {input_file} to {output_file} using {format} format"
            )
        else:
            click.echo(f"Serialized to {output_file}")

    except SerializationError as e:
        click.echo(f"Serialization error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.option(
    "--format",
    "-f",
    default="json",
    type=click.Choice(["json", "pickle", "msgpack"]),
    help="Serialization format to use",
)
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.pass_context
def deserialize(
    ctx: click.Context, format: str, input_file: str, output_file: str
) -> None:
    """Deserialize data from input file to output file."""
    verbose = ctx.obj.get("verbose", False)

    try:
        # Create serializer and deserialize
        serializer = FFISerializer(format)
        data = serializer.deserialize(input_file)

        # Write output as JSON for readability
        import json

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if verbose:
            click.echo(
                f"Successfully deserialized {input_file} to {output_file} using {format} format"
            )
        else:
            click.echo(f"Deserialized to {output_file}")

    except SerializationError as e:
        click.echo(f"Deserialization error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.option(
    "--format",
    "-f",
    default="json",
    type=click.Choice(["json", "pickle", "msgpack"]),
    help="Serialization format to use",
)
@click.argument("request_file", type=click.Path(exists=True))
@click.argument("response_file", type=click.Path())
@click.pass_context
def call(
    ctx: click.Context, format: str, request_file: str, response_file: str
) -> None:
    """Call a function through FFI using request/response files."""
    verbose = ctx.obj.get("verbose", False)

    try:
        # Create FFI bridge
        serializer = FFISerializer(format)
        bridge = FFIBridge(serializer)

        # Process request
        bridge.process_request(request_file, response_file)

        if verbose:
            click.echo(
                f"Successfully processed FFI call from {request_file} to {response_file}"
            )
        else:
            click.echo(f"FFI call completed: {response_file}")

    except SerializationError as e:
        click.echo(f"FFI call error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@main.command()
def info() -> None:
    """Show information about wired-ffi."""
    click.echo("wired-ffi v0.1.0")
    click.echo("FFI(Foreign Function Interface) library based on serialization")
    click.echo("\nSupported formats:")
    click.echo("  - json: JSON serialization")
    click.echo("  - pickle: Python pickle serialization")
    click.echo("  - msgpack: MessagePack serialization")


if __name__ == "__main__":
    main()
