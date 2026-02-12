"""Configuration management for pypi-toolkit."""

from __future__ import annotations

import configparser
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "pypi-toolkit"
CONFIG_FILE = CONFIG_DIR / "config.ini"
PYPIRC_FILE = Path.home() / ".pypirc"


def get_config_username() -> str | None:
    """Get username from config file.

    Returns:
        Username if configured, None otherwise
    """
    if not CONFIG_FILE.exists():
        return None

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    if "pypi-toolkit" in config and "username" in config["pypi-toolkit"]:
        return config["pypi-toolkit"]["username"]

    return None


def set_config_username(username: str) -> None:
    """Save username to config file.

    Args:
        username: PyPI username to save
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)

    if "pypi-toolkit" not in config:
        config["pypi-toolkit"] = {}

    config["pypi-toolkit"]["username"] = username

    with open(CONFIG_FILE, "w") as f:
        config.write(f)


def get_pypirc_username() -> str | None:
    """Try to get username from ~/.pypirc.

    Note: Most modern configs use __token__ which isn't useful.

    Returns:
        Username if found and not a token, None otherwise
    """
    if not PYPIRC_FILE.exists():
        return None

    config = configparser.ConfigParser()
    config.read(PYPIRC_FILE)

    # Check [pypi] section first
    for section in ["pypi", "testpypi", "server-login"]:
        if section in config and "username" in config[section]:
            username = config[section]["username"]
            # Skip if it's a token
            if username and not username.startswith("__"):
                return username

    return None


def get_default_username() -> str | None:
    """Get default username from config or pypirc.

    Priority:
    1. pypi-toolkit config file
    2. ~/.pypirc (if not using token auth)

    Returns:
        Username if found, None otherwise
    """
    # First check our config
    username = get_config_username()
    if username:
        return username

    # Fall back to pypirc
    return get_pypirc_username()
