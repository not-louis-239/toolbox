#!/usr/bin/env python3


# wrap_lines.py - wrap lines in a file to a specified width

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
import textwrap
import os
from typing import NoReturn

IGNORED_PREFIXES: list[str] = ['*', '#', '>', '//']

def die(msg: str, exitcode: int = 1) -> NoReturn:
    print(f"fatal: {msg}", file=sys.stderr)
    sys.exit(exitcode)

def wrap_file(file_path: str, width: int) -> None:
    if not os.path.exists(file_path):
        die(f"no such file: '{file_path}'")
    if not os.path.isfile(file_path):
        die(f"not a file: '{file_path}'")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        die(f"failed to read file '{file_path}': invalid encoding")

    paragraphs = []
    current_para = []

    for line in lines:
        stripped = line.lstrip()
        # Treat ignored lines as their own paragraph
        if any(stripped.startswith(prefix) for prefix in IGNORED_PREFIXES):
            if current_para:
                paragraphs.append(current_para)
                current_para = []
            paragraphs.append([line.rstrip("\n")])  # Keep line exactly as-is
        elif stripped.strip() == "":  # Blank line
            if current_para:
                paragraphs.append(current_para)
                current_para = []
            paragraphs.append([])  # Preserve blank line
        else:
            current_para.append(line.rstrip("\n"))

    if current_para:
        paragraphs.append(current_para)

    wrapped_paragraphs = []
    for para in paragraphs:
        if not para:  # Blank line
            wrapped_paragraphs.append("")
        elif len(para) == 1 and any(para[0].lstrip().startswith(prefix) for prefix in IGNORED_PREFIXES):
            wrapped_paragraphs.append(para[0])  # Preserve exactly
        else:
            # Merge lines, strip inner spaces, and wrap
            single_line_para = " ".join(line.strip() for line in para)
            wrapped_paragraphs.append(textwrap.fill(single_line_para, width=width))

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(wrapped_paragraphs) + "\n")  # Ensure final newline
    except PermissionError:
        die(f"write permission denied: '{file_path}'")

def main():
    if len(sys.argv) < 3:
        die("Usage: line_wrapper.py [file_path] [width]")

    file_path = sys.argv[1]

    try:
        width = int(sys.argv[2])
        if width <= 0:
            die(f"invalid width: must be a positive integer")
    except ValueError:
        die(f"invalid width: not an integer: '{sys.argv[2]}'")

    wrap_file(file_path, width)
    print(f"Success: '{file_path}' has been wrapped to {width} characters.")

if __name__ == "__main__":
    main()
