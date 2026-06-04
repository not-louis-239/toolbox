# count_files.py - utils for counting files and formatting file paths
# in user-friendly ways

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

from pathlib import Path

ICLOUD: Path = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs"

IGNORE: list[str] = [".DS_Store", ".localized", ".Trash"]
IGNORE_SUFFIXES: list[str] = [".icloud"]
IGNORE_PREFIXES: list[str] = ["."]

def abbreviate_home(s: str | Path) -> str:
    """Takes a string path and abbreviates the home directory to `~` if it
    is in the path"""
    s = str(s)
    home = str(Path.home())
    if s.startswith(home):
        return "~" + s[len(home):]
    return s

def count_files_in_dir(directory: Path) -> int:
    """Count the number of files and subdirectories
    in a directory (non-recursive).
    Returns 0 if the path is invalid or inaccessible."""
    try:
        return sum(
            1 for p in directory.iterdir()
            if p.name not in IGNORE
            and not any(p.name.startswith(prefix) for prefix in IGNORE_PREFIXES)
            and not any(p.name.endswith(suffix) for suffix in IGNORE_SUFFIXES)
        )
    except FileNotFoundError:
        return 0
    except NotADirectoryError:
        return 0
    except PermissionError:
        return 0
    except Exception:
        return 0
