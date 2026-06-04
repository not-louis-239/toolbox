#!/usr/bin/env python3

# v1.0.0
# venv_touch.py
# Create a venv in ~/venvs and symlink to ./.venv in the current directory
# Usage: ./venv_touch.py <venv_name> [python_bin]
# Uses the python3 binary that is highest in the PATH if [python_bin] is not provided

# repo at: https://github.com/not-louis-239/toolbox
# Copyright (C) 2026 Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import string
import shutil
import subprocess
import argparse as ap
from dataclasses import dataclass
from pathlib import Path

VENVS_DIR = Path.home() / "venvs"
VALID_NAME_CHARS = string.ascii_letters + string.digits + "_- "

def run_cmd(argv: list[str], cwd: Path | str = ".") -> None:
    subprocess.run(args=argv, check=True, cwd=cwd)

def fatal_err(msg: str) -> None:
    print(f"{Path(__file__).name}: fatal: {msg}", file=sys.stderr)
    sys.exit(1)

@dataclass
class Args:
    venv_name: str
    python_bin: str

def parse_args() -> Args:
    parser = ap.ArgumentParser(description="Create a virtual environment in ~/venvs symlinked to ./.venv")
    parser.add_argument("venv_name", type=str, help="Name of venv in ~/venvs")
    parser.add_argument("python_bin", type=str, nargs="?", default="python3", help="Path to python binary (e.g. /usr/bin/python3)")
    parsed = parser.parse_args()
    return Args(venv_name=parsed.venv_name, python_bin=parsed.python_bin)

def main():
    args = parse_args()

    if any(c not in VALID_NAME_CHARS for c in args.venv_name):
        fatal_err("venv name can only contain letters, numbers, underscores, spaces, and hyphens (A-Z, a-z, 0-9, _, -, ' ')")

    VENVS_DIR.mkdir(parents=True, exist_ok=True)

    venv_path = VENVS_DIR / args.venv_name / ".venv"
    venv_link = Path("./.venv")

    # Abort if Python binary not found
    if shutil.which(args.python_bin) is None:
        fatal_err(f"python binary '{args.python_bin}' not found in PATH")

    # Abort if venv path already exists
    if venv_path.exists():
        fatal_err(f"venv '{args.venv_name}' already exists in {VENVS_DIR.absolute()}")

    # Abort if link already exists
    if venv_link.exists() or venv_link.is_symlink():
        fatal_err(f"link '{venv_link}' already exists in current directory")

    try:
        run_cmd([args.python_bin, "-m", "venv", str(venv_path)])
    except Exception as e:
        fatal_err(
            f"venv creation failed ({e})."
        )

    try:
        venv_link.symlink_to(venv_path, target_is_directory=True)
    except Exception as e:
        fatal_err(
            f"Symlink creation failed ({e}). \nPlease remove the orphaned"
            f" venv ('{venv_path}') and try again."
        )

if __name__ == "__main__":
    main()
