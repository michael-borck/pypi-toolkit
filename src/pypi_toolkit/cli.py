"""Main CLI entry point for pypi-toolkit."""

import typer
from rich.console import Console
from rich.table import Table

from pypi_toolkit import __version__
from pypi_toolkit.commands.package import audit, info, list_packages

app = typer.Typer(
    name="pypi-toolkit",
    help="PyPI package portfolio management and auditing toolkit",
    no_args_is_help=True,
)
console = Console()

# Create subcommands
package_app = typer.Typer(help="Package management commands")

# Register subcommands
app.add_typer(package_app, name="package")


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"pypi-toolkit version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None, "--version", "-v", help="Show version and exit", callback=version_callback
    ),
) -> None:
    """PyPI Toolkit - Package portfolio management and auditing."""
    pass


# Package commands
package_app.command("list")(list_packages)
package_app.command("info")(info)
package_app.command("audit")(audit)


if __name__ == "__main__":
    app()
