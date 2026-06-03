#!/usr/bin/env python3

# check_licences.py - check a target folder for files missing a licence header
# optionally, input a path to a text file with a list of files or directories
# to ignore recursively

# Copyright (C) 2026 Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>
# https://github.com/not-louis-239

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
import os
import re
import argparse as ap
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


COL_INFO = "\033[94m"
COL_WARN = "\033[93m"
COL_ERR = "\033[91m"
COL_RESET = "\033[0m"
COL_BOLD = "\033[1m"


@dataclass
class Args:
    licence_header_fp: Path
    ignore_fp: Path
    target_dir: Path

def die(msg: str, exitcode: int = 1) -> None:
    print(f"{COL_ERR}{COL_BOLD}fatal{COL_RESET}: {COL_ERR}{msg}{COL_RESET}", file=sys.stderr)
    sys.exit(exitcode)

def parse_args() -> Args:
    parser = ap.ArgumentParser(
        description=(
            "Scan a target directory for missing licence headers.\n"
            "Optionally accepts an ignore text file with a list of files\n"
            " or directories to ignore recursively.\n"
        ),
        formatter_class=ap.RawDescriptionHelpFormatter  # Stop eating all my newlines, argparse!!
    )
    parser.add_argument("target_dir", type=Path, help="path to the directory to scan")
    parser.add_argument("-l", "--licence", dest="licence_header_fp", type=Path, required=True, help="path to the licence header file")
    parser.add_argument("-i", "--ignore", dest="ignore_fp", type=Path, required=False, help="path to the ignore file (optional)")

    args_raw = parser.parse_args()

    return Args(
        licence_header_fp=args_raw.licence_header_fp,
        ignore_fp=args_raw.ignore_fp,
        target_dir=args_raw.target_dir
    )

def validate_args(args: Args) -> None:
    if not args.licence_header_fp.exists():
        die(f"invalid licence: no such file: {args.licence_header_fp}")
    if not os.access(args.licence_header_fp, os.R_OK):
        die(f"invalid licence: read permission denied: {args.licence_header_fp}")
    if not args.licence_header_fp.is_file():
        die(f"invalid licence: not a file: {args.licence_header_fp}")

    if args.ignore_fp is not None:
        if not os.access(args.ignore_fp, os.R_OK):
            die(f"invalid ignore: read permission denied: {args.ignore_fp}")
        if not args.ignore_fp.exists():
            die(f"invalid ignore: no such file: {args.ignore_fp}")
        if not args.ignore_fp.is_file():
            die(f"invalid ignore: not a file: {args.ignore_fp}")

def _normalise_text(text: str) -> str:
    # Strip common line comment markers from each line and trim whitespace.
    # Handles '#', '//' and C-style block comment markers like '/*' and leading '*'.
    lines = text.splitlines()
    out_lines = []
    for line in lines:
        # Remove leading comment markers and surrounding whitespace
        ln = re.sub(r"^\s*(?:#|//|/\*|\*)\s?", "", line)
        # Remove trailing end-of-block marker if present
        ln = re.sub(r"\s*\*/\s*$", "", ln)
        out_lines.append(ln.rstrip())

    # Rejoin and strip any leading/trailing blank lines
    return "\n".join(out_lines).strip()

def _path_matches_pattern(p: Path, pat: str) -> bool:
    """Check whether a path matches an ignore pattern.
    Expects a relative path."""

    pp = PurePosixPath(p)

    # Directory pattern (ends with a slash) - match any path that contains
    # the directory name in its parts.
    if pat.endswith("/"):
        pat = pat.rstrip("/")
        return any(part == pat for part in pp.parts)

    # If the pattern contains glob characters or a path separator, use
    # pathlib's match which understands globs (e.g. "*.pyc", "dir/*.txt").
    if any(ch in pat for ch in "*/?[]") or "/" in pat:
        return pp.match(pat)

    # Plain name (e.g. ".git") - match if any path part equals the name.
    return any(part == pat for part in pp.parts)

def retrieve_paths(directory: Path, ignore: str) -> list[Path]:
    """Retrieve all files in the given directory, in accordance
    with the contents of an ignore file. The `ignore` param is
    expected to be the contents of the read ignore file."""

    resolved_dir = directory.resolve()
    ignore_lines = ignore.splitlines()

    # Get the patterns
    patterns: list[str] = []
    for line in ignore_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)

    valid: list[Path] = []
    paths = list(p for p in directory.rglob("*") if p.is_file())

    # Go through each path and check against patterns
    for path in paths:
        # Hardcoded ignores required as some files
        # will crash the scanner if not ignored
        if path.name == ".DS_Store":
            continue

        resolved = path.resolve()

        # Path not relative -> skip
        if not resolved.is_relative_to(resolved_dir):
            continue

        # Use the path relative to the scanned directory for matching
        rel = path.relative_to(directory)

        if not any(_path_matches_pattern(rel, pattern) for pattern in patterns):
            valid.append(path)

    return valid

def scan_file_for_licence(file_text: str, licence_text: str) -> bool:
    """Scan the given text for the presence of a specified licence text.
    Returns True if the licence text was found, else False."""

    if not file_text:
        return False

    file_lines_norm = _normalise_text(file_text).splitlines()
    licence_lines_norm = _normalise_text(licence_text).splitlines()

    num_file_lines = len(file_lines_norm)
    num_licence_lines = len(licence_lines_norm)

    file_lineno = 0
    licence_lineno = 0

    while file_lineno < num_file_lines:
        file_line, licence_line = file_lines_norm[file_lineno], licence_lines_norm[licence_lineno]

        # Start scanning until either the entire licence is matched,
        # we reach the end of the file, or we find a line that doesn't match
        if file_line == licence_line:
            file_lineno += 1
            licence_lineno += 1

            while file_line == licence_line:
                file_lineno += 1
                licence_lineno += 1
                if licence_lineno >= num_licence_lines:
                    return True
                file_line, licence_line = file_lines_norm[file_lineno], licence_lines_norm[licence_lineno]

        licence_lineno = 0
        file_lineno += 1

    return False

def main() -> int:
    args = parse_args()
    validate_args(args)

    num_missing = 0

    if args.ignore_fp is None:
        ignore_text = ""
    else:
        try:
            ignore_text = args.ignore_fp.read_text()
        except UnicodeDecodeError:
            die(f"invalid ignore: invalid source encoding: {args.ignore_fp}")

    paths_to_scan = retrieve_paths(args.target_dir, ignore_text)
    print(f"Found {COL_INFO}{len(paths_to_scan):,}{COL_RESET} files to scan.")

    # Read licence once
    licence_text = args.licence_header_fp.read_text()
    if not licence_text.strip():
        die(f"invalid licence: licence file is empty: {args.licence_header_fp}")

    for path in paths_to_scan:
        if not os.access(path, os.R_OK):
            print(f"skipping file: {COL_WARN}'{path}'{COL_RESET} - read permission denied", file=sys.stderr)
            continue

        try:
            file_text = path.read_text()
        except UnicodeDecodeError:
            print(f"skipping file: {COL_WARN}'{path}'{COL_RESET} - unknown encoding", file=sys.stderr)
            continue

        if not scan_file_for_licence(file_text, licence_text):
            print(f"missing licence: {COL_ERR}'{path}'{COL_RESET}")
            num_missing += 1

    print()

    if num_missing:
        print(f"Scan complete. {COL_ERR}{num_missing:,}{COL_RESET} files are missing licences.")
        return 1

    print("Scan complete. No files missing licences were found.")
    return 0

if __name__ == "__main__":
    exitcode = main()
    sys.exit(exitcode)
