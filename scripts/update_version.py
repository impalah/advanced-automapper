#!/usr/bin/env python3
"""Synchronize version from pyproject.toml to __init__.py and docs_source/conf.py."""

import re
import sys
import tomllib
from pathlib import Path


def get_version() -> str:
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print("Error: pyproject.toml not found", file=sys.stderr)
        sys.exit(1)
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    version = data.get("project", {}).get("version")
    if not version:
        print("Error: version not found in pyproject.toml", file=sys.stderr)
        sys.exit(1)
    return version


def update_init(version: str) -> None:
    init_path = Path("src/automapper/__init__.py")
    if not init_path.exists():
        return
    content = init_path.read_text()
    new_content = re.sub(
        r'^__version__\s*=\s*["\'].*?["\']',
        f'__version__ = "{version}"',
        content,
        flags=re.MULTILINE,
    )
    if new_content != content:
        init_path.write_text(new_content)
        print(f"Updated {init_path} to {version}")


def update_conf(version: str) -> None:
    conf_path = Path("docs_source/conf.py")
    if not conf_path.exists():
        return
    content = conf_path.read_text()
    new_content = re.sub(
        r'^release\s*=\s*["\'].*?["\']',
        f'release = "{version}"',
        content,
        flags=re.MULTILINE,
    )
    new_content = re.sub(
        r'^version\s*=\s*["\'].*?["\']',
        f'version = "{version}"',
        new_content,
        flags=re.MULTILINE,
    )
    if new_content != content:
        conf_path.write_text(new_content)
        print(f"Updated {conf_path} to {version}")


if __name__ == "__main__":
    v = get_version()
    print(f"Version: {v}")
    update_init(v)
    update_conf(v)
