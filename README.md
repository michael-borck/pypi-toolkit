# pypi-toolkit

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

### List your packages

```bash
# List all packages for a PyPI user
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
# Audit all packages by a user
pypi-toolkit package audit --user your-username

# Audit specific packages
pypi-toolkit package audit --package requests --package flask

# Save audit report
pypi-toolkit package audit --user your-username --output audit.json
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
