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

import re
from pathlib import Path
from typing import cast
from PIL import Image

from toolbox_lib.ansi_convert import (
    ANSIPixel,
    AColour,
    ColourSpace,
    convert_img_to_ansi_pixels,
    _col256_to_rgb
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


def load_ansi_from_img(img_path: Path) -> list[list[ANSIPixel]]:
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
        if start_y >= len(dest):
            continue
        dest[start_y][start_x:end_x] = row


def serialise(img: list[list[ANSIPixel]], mode: ColourSpace) -> str:
    """Serialise an image into a string that can be printed to the terminal."""
    lines = []
    for row in img:
        line = "".join(p.render(mode=mode) for p in row)
        lines.append(line)

    return "\n".join(lines)




ESC_RE = re.compile(r"\x1b\[([0-9;]*)m")


def unserialise(img_str: str) -> list[list[ANSIPixel]]:
    """Unserialise an image from a string to a 2-dimensional
    array of ANSIPixels."""

    # TODO: Add support for vanilla ANSI escapes like '\x1b[3Xm' or '\x1b[9Xm'

    rows: list[list[ANSIPixel]] = []

    fg_colour: AColour | None = None
    bg_colour: AColour | None = None
    faint = False

    for line in img_str.splitlines():
        row: list[ANSIPixel] = []

        pos = 0

        while pos < len(line):
            match = ESC_RE.match(line, pos)

            if match:
                params = match.group(1)

                codes = (
                    [0]
                    if params == ""
                    else [int(x) for x in params.split(";")]
                )

                i = 0
                while i < len(codes):
                    code = codes[i]

                    if code == 0:
                        fg_colour = None
                        bg_colour = None
                        faint = False

                    elif code == 2:
                        faint = True

                    elif code == 22:
                        faint = False

                    elif code == 38:
                        if (
                            i + 2 < len(codes)
                            and codes[i + 1] == 5
                        ):
                            col256 = codes[i + 2]
                            r, g, b = _col256_to_rgb(col256)

                            fg_colour = (
                                r,
                                g,
                                b,
                                127 if faint else 255,
                            )

                            i += 2

                    elif code == 48:
                        if (
                            i + 2 < len(codes)
                            and codes[i + 1] == 5
                        ):
                            col256 = codes[i + 2]
                            r, g, b = _col256_to_rgb(col256)

                            bg_colour = (
                                r,
                                g,
                                b,
                                127 if faint else 255,
                            )

                            i += 2

                    i += 1

                pos = match.end()
                continue

            row.append(
                ANSIPixel(
                    fg_colour=fg_colour,
                    bg_colour=bg_colour,
                    fg_char=line[pos],
                )
            )

            pos += 1

        rows.append(row)

    return rows
