"""Main application entry point."""

import sys
import click

from weather_app.interfaces.cli import cli as cli_interface
from weather_app.interfaces.web import main as web_main
from weather_app.interfaces.mcp_server import main as mcp_main


@click.group()
def main():
    """Weather Multi-Interface Application.

    A comprehensive weather application with CLI, Web, and MCP interfaces.
    """
    pass


@main.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--zipcode", "-z", help="US zipcode (e.g., 90210)")
@click.option("--city", "-c", help="City name")
@click.option("--state", "-s", help="State or province")
@click.option("--country", "-C", help="Country name or code")
def cli(verbose, zipcode, city, state, country):
    """Run the CLI interface."""
    # Import and run CLI with parameters
    import asyncio
    from weather_app.interfaces.cli import get_weather_async

    if verbose:
        import logging

        logging.basicConfig(level=logging.DEBUG)

    asyncio.run(get_weather_async(zipcode, city, state, country))


@main.command()
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind to")
@click.option("--port", "-p", default=8000, help="Port to bind to")
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode")
def web(host, port, debug):
    """Run the Flask web interface."""
    from weather_app.interfaces.web import create_app

    app = create_app()
    app.run(host=host, port=port, debug=debug)


@main.command()
def mcp():
    """Run the MCP server for VS Code integration."""
    mcp_main()


if __name__ == "__main__":
    main()
