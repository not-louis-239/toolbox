#!/usr/bin/env python3

# main.py - main script for resizing images using Nearest-Neighbor interpolation


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

import argparse
import os
import sys
from pathlib import Path
from PIL import Image

def die(msg: str, exitcode: int = 1) -> None:
    """Print an error message to stderr and terminate execution."""
    print(f"nn_resize: fatal: {msg}", file=sys.stderr)
    sys.exit(exitcode)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resize an image using Nearest Neighbor interpolation."
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
        help="Path to save the resized output image."
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        nargs=2,
        required=True,
        metavar=("WIDTH", "HEIGHT"),
        help="Target dimensions as two integers: width height"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force overwrite if the output file already exists."
    )
    return parser.parse_args()

def validate_paths(input_path: Path, output_path: Path, force: bool) -> None:
    # Check input file existence
    if not input_path.exists():
        die(f"Input file does not exist: {input_path}")

    if not input_path.is_file():
        die(f"Input path is not a file: {input_path}")

    # Check input read permissions
    if not os.access(input_path, os.R_OK):
        die(f"No read permission for input file: {input_path}")

    # Check output parent directory existence
    parent_dir = output_path.parent
    if not parent_dir.exists():
        die(f"Output directory does not exist: {parent_dir}")

    if not parent_dir.is_dir():
        die(f"Output parent path is not a directory: {parent_dir}")

    # Check if output parent directory is writable
    if not os.access(parent_dir, os.W_OK):
        die(f"No write permission for output directory: {parent_dir}")

    # Handle output conflict / overwrite scenarios
    if output_path.exists():
        # Even if --force is used, we cannot write if the file itself is system write-protected
        if not os.access(output_path, os.W_OK):
            die(f"Output file exists but is write-protected: {output_path}")

        if force:
            print(f"Warning: Overwriting existing file: {output_path}", file=sys.stderr)
        else:
            die(f"Output file already exists: {output_path}. Use -f or --force to overwrite.")

def main() -> None:
    args = parse_args()

    # Run all path and safety validations (passing the force flag)
    validate_paths(args.input, args.output, args.force)

    width, height = args.size

    if width <= 0:
        die("Invalid target width: width must be 1 or greater.")
    if height <= 0:
        die("Invalid target height: height must be 1 or greater.")

    try:
        # Open, process, and save
        with Image.open(args.input) as img:
            converted_img = img.convert("RGBA")

        # Perform nearest neighbor resize
        resized_img = converted_img.resize((width, height), Image.Resampling.NEAREST)

        # Save to destination
        resized_img.save(args.output)

    except Exception as e:
        err_str = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
        die(f"An unexpected error occurred during image processing: {err_str}")

if __name__ == "__main__":
    main()
