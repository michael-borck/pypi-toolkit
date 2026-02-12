"""Package management commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pypi_toolkit.core.pypi_client import PyPIClient, PyPIAPIError

console = Console()


def list_packages(
    username: str = typer.Argument(help="PyPI username to list packages for"),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output to JSON file"
    ),
    test_pypi: bool = typer.Option(
        False, "--test-pypi", "-T", help="Use TestPyPI instead of PyPI"
    ),
) -> None:
    """List all packages for a PyPI user.

    Shows packages where the user is listed as author or maintainer.
    """
    client = PyPIClient(test_pypi=test_pypi)
    index_name = "TestPyPI" if test_pypi else "PyPI"

    try:
        console.print(f"[blue]Fetching packages for user: {username}[/blue]")
        packages = client.get_user_packages(username)

        if not packages:
            console.print(f"[yellow]No packages found for user '{username}'[/yellow]")
            raise typer.Exit(0)

        console.print(f"[green]Found {len(packages)} packages[/green]\n")

        table = Table(title=f"Packages by {username}")
        table.add_column("Package", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Description")
        table.add_column("License")

        results = []
        for pkg_name in packages:
            try:
                pkg_info = client.get_package(pkg_name)
                table.add_row(
                    pkg_info.name,
                    pkg_info.version,
                    (pkg_info.summary or "")[:50] + "..." if pkg_info.summary and len(pkg_info.summary) > 50 else pkg_info.summary or "-",
                    pkg_info.license or "-",
                )
                results.append({
                    "name": pkg_info.name,
                    "version": pkg_info.version,
                    "summary": pkg_info.summary,
                    "license": pkg_info.license,
                })
            except PyPIAPIError:
                table.add_row(pkg_name, "?", "Error fetching info", "-")

        console.print(table)

        if output:
            Path(output).write_text(json.dumps(results, indent=2))
            console.print(f"\n[green]Results saved to {output}[/green]")

    except PyPIAPIError as e:
        console.print(f"[red]Error: {e.message}[/red]")
        raise typer.Exit(1) from e


def info(
    package: str = typer.Argument(help="Package name on PyPI"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
    test_pypi: bool = typer.Option(
        False, "--test-pypi", "-T", help="Use TestPyPI instead of PyPI"
    ),
) -> None:
    """Show detailed information about a PyPI package."""
    client = PyPIClient(test_pypi=test_pypi)

    try:
        pkg = client.get_package(package)

        if json_output:
            data = {
                "name": pkg.name,
                "version": pkg.version,
                "summary": pkg.summary,
                "author": pkg.author,
                "license": pkg.license,
                "home_page": pkg.home_page,
                "docs_url": pkg.docs_url,
                "package_url": pkg.package_url,
                "requires_python": pkg.requires_python,
                "project_urls": pkg.project_urls,
                "version_count": pkg.version_count,
            }
            console.print_json(json.dumps(data))
            return

        # Build info panel
        info_lines = [
            f"[bold]Name:[/bold] {pkg.name}",
            f"[bold]Version:[/bold] {pkg.version}",
            f"[bold]Summary:[/bold] {pkg.summary or '[dim]None[/dim]'}",
            f"[bold]Author:[/bold] {pkg.author or '[dim]None[/dim]'}",
            f"[bold]License:[/bold] {pkg.license or '[dim]None[/dim]'}",
            f"[bold]Python:[/bold] {pkg.requires_python or '[dim]Any[/dim]'}",
            f"[bold]Versions:[/bold] {pkg.version_count}",
            "",
            "[bold]URLs:[/bold]",
            f"  PyPI: {pkg.package_url}",
        ]

        if pkg.home_page:
            info_lines.append(f"  Homepage: {pkg.home_page}")
        if pkg.docs_url:
            info_lines.append(f"  Docs: {pkg.docs_url}")

        for name, url in pkg.project_urls.items():
            info_lines.append(f"  {name}: {url}")

        # Health indicators
        info_lines.extend([
            "",
            "[bold]Health:[/bold]",
            f"  {'[green]✓[/green]' if pkg.has_description else '[red]✗[/red]'} Has description",
            f"  {'[green]✓[/green]' if pkg.has_license else '[red]✗[/red]'} Has license",
            f"  {'[green]✓[/green]' if pkg.has_github_url else '[yellow]○[/yellow]'} GitHub link",
            f"  {'[green]✓[/green]' if pkg.has_docs_url else '[yellow]○[/yellow]'} Documentation link",
        ])

        panel = Panel(
            "\n".join(info_lines),
            title=f"[bold]{pkg.name}[/bold]",
            border_style="blue",
        )
        console.print(panel)

    except PyPIAPIError as e:
        console.print(f"[red]Error: {e.message}[/red]")
        raise typer.Exit(1) from e


def audit(
    username: str | None = typer.Option(
        None, "--user", "-u", help="Audit all packages by this PyPI user"
    ),
    packages: list[str] | None = typer.Option(
        None, "--package", "-p", help="Package name(s) to audit"
    ),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output audit report to JSON file"
    ),
    test_pypi: bool = typer.Option(
        False, "--test-pypi", "-T", help="Use TestPyPI instead of PyPI"
    ),
) -> None:
    """Audit PyPI packages for missing metadata.

    Checks for:
    - Missing description/summary
    - Missing license
    - Missing GitHub/source URL
    - Missing documentation URL
    - Missing Python version requirement
    """
    if not username and not packages:
        console.print("[red]Error: Provide either --user or --package[/red]")
        raise typer.Exit(1)

    client = PyPIClient(test_pypi=test_pypi)
    index_name = "TestPyPI" if test_pypi else "PyPI"
    pkg_names: list[str] = []

    if username:
        try:
            console.print(f"[blue]Fetching packages for user: {username}[/blue]")
            pkg_names = client.get_user_packages(username)
            console.print(f"[green]Found {len(pkg_names)} packages[/green]\n")
        except PyPIAPIError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            raise typer.Exit(1) from e

    if packages:
        pkg_names.extend(packages)

    if not pkg_names:
        console.print("[yellow]No packages to audit[/yellow]")
        raise typer.Exit(0)

    # Audit each package
    issues: dict[str, list[str]] = {}
    results = []

    console.print("[blue]Auditing packages...[/blue]")

    for pkg_name in pkg_names:
        try:
            pkg = client.get_package(pkg_name)
            pkg_issues = []

            if not pkg.has_description:
                pkg_issues.append("missing_description")
            if not pkg.has_license:
                pkg_issues.append("missing_license")
            if not pkg.has_github_url:
                pkg_issues.append("no_github_url")
            if not pkg.has_docs_url:
                pkg_issues.append("no_docs_url")
            if not pkg.requires_python:
                pkg_issues.append("no_python_requires")

            if pkg_issues:
                issues[pkg_name] = pkg_issues

            results.append({
                "name": pkg_name,
                "version": pkg.version,
                "issues": pkg_issues,
            })

        except PyPIAPIError as e:
            console.print(f"[yellow]  Skipping {pkg_name}: {e.message}[/yellow]")

    # Print summary
    console.print("\n[bold]Audit Results[/bold]")
    console.print("=" * 50)
    console.print(f"Total packages: {len(pkg_names)}")
    console.print(f"Packages with issues: {len(issues)}")

    if issues:
        # Count issue types
        issue_counts: dict[str, int] = {}
        for pkg_issues in issues.values():
            for issue in pkg_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        console.print("\n[bold]Issue Summary:[/bold]")
        for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
            label = issue.replace("_", " ").title()
            console.print(f"  ! {label}: {count}")

        console.print("\n[bold]Packages with issues:[/bold]")
        for pkg_name, pkg_issues in issues.items():
            issue_str = ", ".join(i.replace("_", " ") for i in pkg_issues)
            console.print(f"  [yellow]{pkg_name}[/yellow]: {issue_str}")

    else:
        console.print("\n[green]All packages pass audit![/green]")

    if output:
        Path(output).write_text(json.dumps(results, indent=2))
        console.print(f"\n[green]Report saved to {output}[/green]")
