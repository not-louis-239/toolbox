#!/usr/bin/env python3

# svmr - module for generating Stardew Valley mod receipts
# Copyright (C) 2026 Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>
# https://github.com/not-louis-239
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import argparse as ap
import sys
import json
from datetime import datetime
from collections import deque  # use for recursively traversing the mods folder
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn


COL_ERROR = "\033[91m"
COL_WARN = "\033[93m"
COL_INFO = "\033[94m"
COL_SYNTAX_HIGHLIGHT = "\033[95m"  # for mods that start with e.g. [CP], [FTM], etc.
COL_RESET = "\033[0m"

DEFAULT_SV_MODS_FOLDER = Path.home() / "Library" / "Application Support" / "Steam" / "steamapps" / "common" / "Stardew Valley" / "Contents" / "MacOS" / "Mods"
POSSIBLE_VERSION_KEYS = ["Version", "version", "version_number", "versionNumber", "version_number", "versionNumber"]


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    suffix: str | None = None  # e.g. "beta", "alpha", "rc1", etc.

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"v{base}{self.suffix if self.suffix else ''}"


SENTINEL_VERSION = Version(-1, -1, -1)  # used when we can't find a version in the manifest


@dataclass
class Args:
    mods_folder: Path


@dataclass
class StardewValleyMod:
    name: str
    version: Version


def make_mod_str(mod: StardewValleyMod) -> str:
    # If the mod name starts with an opening bracket, attempt to find the closing
    # bracket, then colour everything inside it.
    # If no closing bracket can be found, skip highlighting.

    if mod.name.startswith("[") and (closing_index := mod.name.find("]")) != -1:
        highlighted_part = f"{COL_SYNTAX_HIGHLIGHT}{mod.name[:closing_index + 1]}{COL_RESET}"
        mod_name = highlighted_part + mod.name[closing_index + 1:]
    else:
        mod_name = mod.name

    version_str = f"({mod.version})" if mod.version is not SENTINEL_VERSION else f"{COL_WARN}(unknown version){COL_RESET}"
    return f"{COL_INFO}- {COL_RESET}{mod_name} {version_str}"


def parse_version_string(version_str: str) -> Version:
    """Parse a version string like '1.2.3' into a Version object.
    If the version string is invalid, return the SENTINEL_VERSION."""
    version_str = version_str.strip().lstrip("vV")  # remove leading 'v' or 'V' if present
    try:
        # Get the suffix and if there is one, strip it and save it for later
        suffix = None
        for i, ch in enumerate(version_str):
            if not (ch.isdigit() or ch == "."):
                suffix = version_str[i:].strip()
                version_str = version_str[:i].strip()
                break

        parts = version_str.split(".")
        if len(parts) >= 3:
            return Version(int(parts[0]), int(parts[1]), int(parts[2]), suffix)
        elif len(parts) == 2:
            return Version(int(parts[0]), int(parts[1]), 0, suffix)
        elif len(parts) == 1:
            return Version(int(parts[0]), 0, 0, suffix)
        elif not parts:
            return SENTINEL_VERSION
    except ValueError:
        return SENTINEL_VERSION

    return SENTINEL_VERSION


def _remove_json_comments(text: str) -> str:
    """Remove JavaScript-style comments from JSON text."""
    buf: list[str] = []
    in_string = False
    escape = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_string:
            buf.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            buf.append(ch)
            i += 1
            continue

        if ch == "/" and i + 1 < len(text):
            next_ch = text[i + 1]
            if next_ch == "/":
                i += 2
                while i < len(text) and text[i] not in "\r\n":
                    i += 1
                continue
            if next_ch == "*":
                i += 2
                while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                    i += 1
                i += 2
                continue

        buf.append(ch)
        i += 1

    return "".join(buf)

def _remove_json_trailing_commas(text: str) -> str:
    """Remove trailing commas from JSON objects and arrays."""
    buf: list[str] = []
    in_string = False
    escape = False
    for ch in text:
        if in_string:
            buf.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            buf.append(ch)
            continue

        if ch in "}]":
            j = len(buf) - 1
            while j >= 0 and buf[j] in " \t\r\n":
                j -= 1
            if j >= 0 and buf[j] == ',':
                del buf[j]
            buf.append(ch)
            continue

        buf.append(ch)

    return "".join(buf)

def normalise_json(text: str) -> str:
    """Normalise JSON text by removing comments and trailing commas."""
    norm = _remove_json_comments(text)
    norm = _remove_json_trailing_commas(norm)
    return norm


def make_stardew_valley_mod_receipt(mods: list[StardewValleyMod]) -> str:
    buf: list[str] = []
    buf.append(f"{COL_INFO}Stardew Valley Mod Receipt{COL_RESET}")
    buf.append(f"Created: {COL_INFO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{COL_RESET}")

    mods_count_str = f"{len(mods)} mod{'' if len(mods) == 1 else 's'}"
    num_unversioned = sum(1 for mod in mods if mod.version is SENTINEL_VERSION)
    if num_unversioned:
        buf.append(f"Includes {COL_INFO}{mods_count_str} {COL_WARN}({num_unversioned} unversioned){COL_RESET}:")
    else:
        buf.append(f"Includes {COL_INFO}{mods_count_str}{COL_RESET}:")

    if not mods:
        buf.append(f"{COL_WARN}<no mods - to install mods, put them in the 'Mods' folder and check the path>{COL_RESET}")

    for mod in mods:
        buf.append(make_mod_str(mod))
    return "\n".join(buf)


def get_stardew_valley_mods(folder_path: Path) -> list[StardewValleyMod]:
    """Traverse this mods folder and get all the names of all
    Stardew Valley mods in it. Return a list of mod names.
    Works recursively."""
    def read_sv_mod(folder: Path) -> StardewValleyMod | None:
        """Returns a StardewValleyMod if this folder is a valid mod, otherwise None."""

        # check if this folder contains a manifest.json file
        # this is similar to how SMAPI identifies mods,
        # so it's a good way to check if this is a mod folder
        if (manifest_path := folder / "manifest.json").exists():
            # Attempt to read the manifest.json to find a version attribute
            version = SENTINEL_VERSION

            try:
                # Some manifest files may begin with a UTF-8 BOM, include JS-style
                # comments, or use trailing commas. Normalize before parsing.
                with open(manifest_path, "r", encoding="utf-8-sig") as f:
                    manifest_text = f.read()
                cleaned = normalise_json(manifest_text)
                manifest = json.loads(cleaned)
                for key in POSSIBLE_VERSION_KEYS:
                    if key in manifest:
                        value = manifest[key]
                        if isinstance(value, (str, int, float)):
                            version = parse_version_string(str(value))
                        break
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

            return StardewValleyMod(name=folder.name, version=version)
        return None

    mods: list[StardewValleyMod] = []
    to_check: deque[Path] = deque([Path(folder_path)])

    while to_check:
        current = to_check.popleft()
        if current.is_dir():
            if (mod := read_sv_mod(current)):
                mods.append(mod)
            else:
                to_check.extend(current.iterdir())

    if not mods:
        print(f"{COL_WARN}Warning: No mods found in '{folder_path}'{COL_RESET}", file=sys.stderr)

    return sorted(mods, key=lambda m: m.name.lower())


def die(message: str, exitcode: int = 1) -> NoReturn:
    print(f"{COL_ERROR}Fatal: {message}{COL_RESET}", file=sys.stderr)
    sys.exit(exitcode)


def parse_args():
    parser = ap.ArgumentParser(description="Generate a mod receipt for Stardew Valley mods.")
    parser.add_argument("mods_folder", type=Path, help=f"Path to the folder containing your Stardew Valley mods. If not given, assumes '{DEFAULT_SV_MODS_FOLDER}'.", nargs="?", default=DEFAULT_SV_MODS_FOLDER)

    args_raw = parser.parse_args()
    if not args_raw.mods_folder.exists():
        die(f"No such directory: '{args_raw.mods_folder}'")
    if not args_raw.mods_folder.is_dir():
        die(f"Not a directory: '{args_raw.mods_folder}'")

    try:
        args_raw.mods_folder.stat()
    except PermissionError:
        die(f"Permission denied: '{args_raw.mods_folder}'")

    return args_raw

def main():
    args = parse_args()
    mods = get_stardew_valley_mods(args.mods_folder)
    receipt = make_stardew_valley_mod_receipt(mods)
    print(receipt)


if __name__ == "__main__":
    main()
