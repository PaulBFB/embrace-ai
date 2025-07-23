"""Command-line interface for TimeToAct parser."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from loguru import logger

from src.embrace_ai_katas.timetoact.parser import ParseError, parse

app = typer.Typer(
    name="timetoact",
    help="Parse TimeToAct DocumentAI format files",
    add_completion=False,
)


@app.command()
def parse_file(
    input_file: Path = typer.Argument(
        ..., help="Path to the TimeToAct format file to parse"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path (default: stdout)"
    ),
    pretty: bool = typer.Option(
        True, "--pretty/--compact", help="Pretty-print JSON output"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """Parse a TimeToAct document and output JSON."""
    if verbose:
        logger.enable("embrace_ai_katas.timetoact")
    else:
        logger.disable("embrace_ai_katas.timetoact")

    try:
        # Read input file
        if not input_file.exists():
            typer.secho(
                f"Error: File '{input_file}' not found", fg=typer.colors.RED, err=True
            )
            raise typer.Exit(1)

        text = input_file.read_text(encoding="utf-8")
        logger.info(f"Read {len(text)} characters from {input_file}")

        # Parse the document
        try:
            result = parse(text)
            logger.info("Parsing completed successfully")
        except ParseError as e:
            typer.secho(f"Parse error: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(2)

        # Convert to JSON
        json_data = result.model_dump()
        json_output = json.dumps(
            json_data, indent=2 if pretty else None, ensure_ascii=False
        )

        # Write output
        if output:
            output.write_text(json_output, encoding="utf-8")
            typer.secho(f"✅ Output written to {output}", fg=typer.colors.GREEN)
        else:
            typer.echo(json_output)

    except Exception as e:
        typer.secho(f"Unexpected error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(3)


@app.command()
def validate(
    input_file: Path = typer.Argument(
        ..., help="Path to the TimeToAct format file to validate"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """Validate a TimeToAct document without outputting JSON."""
    if verbose:
        logger.enable("embrace_ai_katas.timetoact")
    else:
        logger.disable("embrace_ai_katas.timetoact")

    try:
        # Read input file
        if not input_file.exists():
            typer.secho(
                f"Error: File '{input_file}' not found", fg=typer.colors.RED, err=True
            )
            raise typer.Exit(1)

        text = input_file.read_text(encoding="utf-8")

        # Parse the document
        try:
            result = parse(text)

            # Count elements
            def count_elements(node):
                count = 1
                if hasattr(node, "body"):
                    for item in node.body:
                        if hasattr(item, "kind"):
                            count += count_elements(item)
                if hasattr(node, "items"):
                    for item in node.items:
                        count += count_elements(item)
                return count

            total_elements = count_elements(result)
            typer.secho(f"✅ Valid TimeToAct document", fg=typer.colors.GREEN)
            typer.echo(f"   Total elements: {total_elements}")
            if result.head:
                typer.echo(f"   Document title: {result.head}")

        except ParseError as e:
            typer.secho(f"❌ Invalid document: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(2)

    except Exception as e:
        typer.secho(f"Unexpected error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(3)


@app.command()
def test(
    spec_dir: Path = typer.Argument(
        Path("data/timetoact_tests"), help="Directory containing test files"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Run tests on specification examples."""
    if not spec_dir.exists():
        typer.secho(
            f"Error: Directory '{spec_dir}' not found", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(1)

    test_files = list(spec_dir.glob("*.txt"))
    if not test_files:
        typer.secho(f"No test files found in {spec_dir}", fg=typer.colors.YELLOW)
        return

    passed = 0
    failed = 0

    for test_file in test_files:
        try:
            text = test_file.read_text(encoding="utf-8")
            result = parse(text)
            passed += 1
            if verbose:
                typer.secho(f"✅ {test_file.name}", fg=typer.colors.GREEN)
        except ParseError as e:
            failed += 1
            typer.secho(f"❌ {test_file.name}: {e}", fg=typer.colors.RED)
        except Exception as e:
            failed += 1
            typer.secho(
                f"❌ {test_file.name}: Unexpected error: {e}", fg=typer.colors.RED
            )

    typer.echo(f"\nResults: {passed} passed, {failed} failed")
    if failed > 0:
        raise typer.Exit(1)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
