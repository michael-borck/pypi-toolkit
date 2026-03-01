# pypi-toolkit

<!-- BADGES:START -->
[![audit](https://img.shields.io/badge/-audit-blue?style=flat-square)](https://github.com/topics/audit) [![cli](https://img.shields.io/badge/-cli-blue?style=flat-square)](https://github.com/topics/cli) [![metadata](https://img.shields.io/badge/-metadata-blue?style=flat-square)](https://github.com/topics/metadata) [![package-management](https://img.shields.io/badge/-package--management-blue?style=flat-square)](https://github.com/topics/package-management) [![pypi](https://img.shields.io/badge/-pypi-blue?style=flat-square)](https://github.com/topics/pypi) [![python](https://img.shields.io/badge/-python-3776ab?style=flat-square)](https://github.com/topics/python) [![toolkit](https://img.shields.io/badge/-toolkit-blue?style=flat-square)](https://github.com/topics/toolkit)
<!-- BADGES:END -->

PyPI package portfolio management and auditing toolkit.

## Features

- **List packages** - View all packages you've published to PyPI
- **Package info** - Get detailed information about any package
- **Audit** - Check packages for missing metadata (description, license, URLs)

## Installation

```bash
pip install pypi-toolkit
```

Or with uv:

```bash
uv pip install pypi-toolkit
```

## Usage

### Configure default username

```bash
# Set your default PyPI username
pypi-toolkit package config --username your-username

# Show current configuration
pypi-toolkit package config --show
```

### List your packages

```bash
# List all packages (uses default username)
pypi-toolkit package list

# Or specify a username
pypi-toolkit package list your-username

# Save to JSON
pypi-toolkit package list your-username --output packages.json
```

### Get package info

```bash
# Show detailed package information
pypi-toolkit package info requests

# Output as JSON
pypi-toolkit package info requests --json
```

### Audit packages

```bash
# Audit your packages (uses default username)
pypi-toolkit package audit

# Audit a specific user's packages
pypi-toolkit package audit --user your-username

# Audit specific packages
pypi-toolkit package audit --package requests --package flask

# Save audit report
pypi-toolkit package audit --output audit.json
```

### Check name availability

```bash
# Check if a package name is available on PyPI
pypi-toolkit package check my-cool-package

# Check on TestPyPI instead
pypi-toolkit package check my-cool-package --test-pypi
```

## TestPyPI Support

All commands support the `--test-pypi` / `-T` flag to use TestPyPI instead of PyPI:

```bash
pypi-toolkit package info my-package --test-pypi
pypi-toolkit package list my-username --test-pypi
pypi-toolkit package audit --user my-username --test-pypi
```

## Audit Checks

The audit command checks for:

- **Missing description** - Package has no summary
- **Missing license** - No license specified in metadata
- **No GitHub URL** - No link to source repository
- **No docs URL** - No documentation link
- **No Python requires** - No Python version requirement specified

## Requirements

- Python 3.12+

## License

MIT
