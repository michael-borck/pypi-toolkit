"""PyPI API client for fetching package information."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from rich.console import Console

console = Console()


class PyPIAPIError(Exception):
    """Exception raised for PyPI API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


@dataclass
class PackageInfo:
    """Information about a PyPI package."""

    name: str
    version: str
    summary: str | None
    author: str | None
    author_email: str | None
    license: str | None
    home_page: str | None
    project_url: str | None
    docs_url: str | None
    package_url: str
    requires_python: str | None
    classifiers: list[str]
    project_urls: dict[str, str]
    releases: dict[str, list[dict[str, Any]]]

    @property
    def has_license(self) -> bool:
        """Check if package has a license specified."""
        return bool(self.license and self.license.strip())

    @property
    def has_description(self) -> bool:
        """Check if package has a summary/description."""
        return bool(self.summary and self.summary.strip())

    @property
    def has_github_url(self) -> bool:
        """Check if package links to GitHub."""
        urls = list(self.project_urls.values()) + [self.home_page or ""]
        return any("github.com" in url.lower() for url in urls if url)

    @property
    def has_docs_url(self) -> bool:
        """Check if package has documentation URL."""
        if self.docs_url:
            return True
        urls = self.project_urls
        return any(key.lower() in ("documentation", "docs") for key in urls)

    @property
    def version_count(self) -> int:
        """Get number of released versions."""
        return len(self.releases)


class PyPIClient:
    """Client for interacting with the PyPI API."""

    BASE_URL = "https://pypi.org/pypi"

    def __init__(self) -> None:
        """Initialize the PyPI client."""
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "pypi-toolkit/0.1.0",
        })

    def get_package(self, package_name: str) -> PackageInfo:
        """Get information about a specific package.

        Args:
            package_name: Name of the package on PyPI

        Returns:
            PackageInfo object with package details

        Raises:
            PyPIAPIError: If the API request fails
        """
        url = f"{self.BASE_URL}/{package_name}/json"

        try:
            response = self.session.get(url, timeout=30)

            if response.status_code == 404:
                raise PyPIAPIError(f"Package '{package_name}' not found", 404)

            if not response.ok:
                raise PyPIAPIError(
                    f"API error: {response.status_code}", response.status_code
                )

            data = response.json()
            info = data["info"]

            return PackageInfo(
                name=info["name"],
                version=info["version"],
                summary=info.get("summary"),
                author=info.get("author"),
                author_email=info.get("author_email"),
                license=info.get("license"),
                home_page=info.get("home_page"),
                project_url=info.get("project_url"),
                docs_url=info.get("docs_url"),
                package_url=info["package_url"],
                requires_python=info.get("requires_python"),
                classifiers=info.get("classifiers", []),
                project_urls=info.get("project_urls") or {},
                releases=data.get("releases", {}),
            )

        except requests.exceptions.RequestException as e:
            raise PyPIAPIError(f"Request failed: {str(e)}") from e

    def get_user_packages(self, username: str) -> list[str]:
        """Get list of packages maintained by a user.

        Note: PyPI doesn't have a direct API for this.
        This uses the XML-RPC API which is limited.

        Args:
            username: PyPI username

        Returns:
            List of package names
        """
        # PyPI XML-RPC API for user packages
        import xmlrpc.client

        client = xmlrpc.client.ServerProxy("https://pypi.org/pypi")
        try:
            # Get packages where user is listed as maintainer or author
            packages = client.user_packages(username)
            return [pkg[1] for pkg in packages]  # Returns list of (role, package_name)
        except Exception as e:
            raise PyPIAPIError(f"Failed to get user packages: {str(e)}") from e

    def search_packages(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Search for packages on PyPI.

        Note: PyPI search API is deprecated. This uses the Simple API
        or falls back to web scraping if needed.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of package info dicts
        """
        # PyPI deprecated their search API, so we use pypi.org/search
        # This is a simplified implementation
        console.print("[yellow]Note: PyPI search API is limited[/yellow]")

        url = f"https://pypi.org/search/?q={query}"
        response = self.session.get(url, timeout=30)

        if not response.ok:
            raise PyPIAPIError(f"Search failed: {response.status_code}")

        # Would need to parse HTML here - simplified for now
        return []
