#!/usr/bin/env python3

# v1.0.0
# clear_pip_packages.py - simple utility to clear pip packages


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


import subprocess
import sys

SKIP_PACKAGES: set[str] = {"pip", "setuptools", "wheel"}


def clear_pip_packages() -> int:
    print("Fetching installed packages...")

    try:
        # Get the list of installed packages from pip freeze
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Filter out empty lines, editable installs (-e), and the protected packages
        packages_to_remove: list[str] = []

        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("-e"):
                continue

            # Extract package name (handles ==, >=, @, etc.)
            # e.g., "requests==2.31.0" -> "requests"
            package_name = (
                line
                .split("==")[0]
                .split(">=")[0]
                .split("@")[0]
                .strip()
            )

            if package_name.lower() not in SKIP_PACKAGES:
                packages_to_remove.append(package_name)

        if not packages_to_remove:
            print("No external packages found to uninstall.")
            return 0

        print(f"Found {len(packages_to_remove)} packages to uninstall:")

        for package in packages_to_remove:
            print(f"  - {package}")

        confirm = (
            input(
                f"\nAre you sure you want to continue?\n"
                f"This will clear all of the previously listed pip packages (except: {', '.join(SKIP_PACKAGES)})\n"
                "This cannot be undone. [y/N]: "
            ).strip().lower()
        )

        if confirm != "y":
            print("Operation cancelled.")
            return 1

        print()

        # Run pip uninstall on the filtered list
        # Using sys.executable ensures it targets the current environment's pip
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y"]
            + packages_to_remove,
            check=True,
        )

        print("\nSuccessfully cleared packages.")
        return 0

    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred while running pip: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exitcode = clear_pip_packages()
    sys.exit(exitcode)
