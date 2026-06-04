# ansiparse.py - module for parsing strings using ANSI escape codes
# into runtime objects to make them easier to manipulate

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

# TODO: figure out what to do with the damn dependencies inside the lib/ folder

from pathlib import Path
from typing import cast
from PIL import Image

from toolbox_lib.ansi_convert import (
    ANSIPixel,
    AColour,
    ColourSpace,
    convert_img_to_ansi_pixels
)


def load_img_pixels(img_path: Path) -> list[list[AColour]]:
    """Load pixel data from an image file.
    Returns a grid of tuples of (r, g, b, a)"""
    raw = Image.open(img_path).convert("RGBA")

    pixels: list[list[AColour]] = []
    for y in range(raw.height):
        row: list[AColour] = []

        for x in range(raw.width):
            r, g, b, a = cast(AColour, raw.getpixel((x, y)))
            row.append((r, g, b, a))

        pixels.append(row)

    return pixels


def load_from_img(img_path: Path) -> list[list[ANSIPixel]]:
    """Load pixel data from an image file and convert it to
    ANSIPixel objects."""
    raw = load_img_pixels(img_path)
    pixels = convert_img_to_ansi_pixels(raw)
    return pixels


def blit(dest: list[list[ANSIPixel]], src: list[list[ANSIPixel]], pos: tuple[int, int]) -> None:
    """Copy pixels from src to dest, starting from the top left at `pos`."""
    px, py = pos

    for y, row in enumerate(src):
        start_x, start_y = px, py + y
        end_x = start_x + len(row)
        dest[start_y][start_x:end_x] = row


def serialise(img: list[list[ANSIPixel]], mode: ColourSpace) -> str:
    """Serialise an image into a string that can be printed to the terminal."""
    lines = []
    for row in img:
        line = "".join(p.render(mode=mode) for p in row)
        lines.append(line)

    return "\n".join(lines)
