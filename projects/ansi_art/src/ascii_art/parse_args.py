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


import argparse as ap
import sys
import os
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

from ascii_art.utils import ColourSpace

@dataclass
class Args:
    input: Path
    output: Path
    small: bool
    force: bool
    mode: ColourSpace  # force the compiler to use a specific colour mode

def die(msg: str, exitcode: int = 1) -> NoReturn:
    print(f"ascii_art: fatal: {msg}", file=sys.stderr)
    sys.exit(exitcode)

def parse_args() -> Args:
    parser = ap.ArgumentParser(
        description="Convert images to ANSI/ASCII art."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Path to the input image file."
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        required=True,
        help="Path to the output file."
    )

    parser.add_argument(
        "-s", "--small",
        action="store_true",
        help="Generate a smaller version of the output."
    )

    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite the output file if it exists."
    )

    parser.add_argument(
        "-m", "--mode",
        choices=["col256", "true"],
        default="true",  # Default to Truecolor if they don't specify
        help="Force the colour space compiler mode (default: true)"
    )

    args_raw = parser.parse_args()

    args = Args(
        input=args_raw.input,
        output=args_raw.output,
        small=args_raw.small,
        force=args_raw.force,
        mode=args_raw.mode
    )

    return args

def validate_args(args: Args) -> None:
    """Validates arguments and throws errors or prints warnings accordingly"""

    if not os.access(args.input, os.R_OK):
        die(f"Cannot read from input - permission denied: '{args.input}'")
    if not args.input.exists():
        die(f"No such input file: '{args.input}'")
    if not args.input.is_file():
        die(f"Invalid input file: '{args.input}'")

    output = args.output
    if not output.parent.exists():
        die(f"Invalid output path - parent directory does not exist: '{output.parent}'")
    if not os.access(output.parent, os.W_OK):
        die(f"Invalid output path - no write permission for directory: {output.parent}")
    if args.output.exists():
        if args.force:
            print(f"Warning: overwriting existing file '{args.output}'", file=sys.stderr)
        else:
            die(f"Output file '{args.output}' already exists")
