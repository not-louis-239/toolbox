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

from dataclasses import dataclass
from typing import TypeAlias
from enum import StrEnum

from toolbox_lib.colours import COL_END


AColour: TypeAlias = tuple[int, int, int, int]


class ColourSpace(StrEnum):
    TRUE = "true"
    COL256 = "col256"


def _rgb_to_col256(r: int, g: int, b: int) -> int:
    """Convert RGB values to a 256-colour code"""
    return 16 + 36 * (r // 51) + 6 * (g // 51) + b // 51

def col(colour: AColour | None, *, bg: bool = False, mode: ColourSpace) -> str:
    """Generate a colour code for the given colour."""

    if colour is None:
        return f"\033[{49 if bg else 39}m"

    r, g, b, a = colour

    # round alpha to either faint or not - alpha is not applicable for background
    alpha_val = "" if bg else "22" if a > 127 else "2"

    bg_section = "48" if bg else "38"

    if mode == ColourSpace.TRUE:
        colour_section = f"2;{r};{g};{b}"
    else:
        code = _rgb_to_col256(r, g, b)
        colour_section = f"5;{code}"

    return f"\x1b[{alpha_val};{bg_section};{colour_section}m"


@dataclass
class ANSIPixel:
    # for each bg_colour and fg_colour, AColour = RGBA, None = default colour
    bg_colour: AColour | None = None
    fg_colour: AColour | None = None
    fg_char: str = " "

    def render(self, mode: ColourSpace) -> str:
        """Serialise the ANSIPixel into a string that can be
        printed to the terminal."""

        fg_code = col(self.fg_colour, bg=False, mode=mode)
        bg_code = col(self.bg_colour, bg=True, mode=mode)

        return f"{bg_code}{fg_code}{self.fg_char}{COL_END}"


def _pix(top: AColour, bot: AColour) -> ANSIPixel:
    """Convert a single pair of (top, bot) in small mode"""

    # We start by assuming that top = foreground, bot = background.
    top_r, top_g, top_b, top_a = top
    bot_r, bot_g, bot_b, bot_a = bot

    # Currently, using the trick with half-block characters does not accept alpha very well.
    # So we normalise alpha values to either completely opaque or completely transparent
    # We round them to either full (1) or none (0)
    top_opaque = top_a > 127
    bot_opaque = bot_a > 127

    # Now run through each possible case:

    # Both fully transparent
    if not top_opaque and not bot_opaque:
        return ANSIPixel()

    # Top transparent, bottom opaque
    if not top_opaque and bot_opaque:
        return ANSIPixel(
            bg_colour=None,
            fg_colour=(bot_r, bot_g, bot_b, bot_a),
            fg_char="▄"
        )

    # Top opaque, bottom transparent
    if top_opaque and not bot_opaque:
        return ANSIPixel(
            bg_colour=None,
            fg_colour=(top_r, top_g, top_b, top_a),
            fg_char="▀"
        )

    # Both fully opaque
    return ANSIPixel(
        bg_colour=(bot_r, bot_g, bot_b, bot_a),
        fg_colour=(top_r, top_g, top_b, top_a),
        fg_char="▀"
    )


def convert_img_to_ansi_pixels(img: list[list[AColour]]) -> list[list[ANSIPixel]]:
    height, width = len(img), len(img[0])
    lines: list[list[ANSIPixel]] = []

    for y in range(0, height, 2):
        row_pixels: list[ANSIPixel] = []

        for x in range(width):
            top_pix, bot_pix = img[y][x], (img[y + 1][x] if y + 1 < height else (0, 0, 0, 0))  # if we don't check for bounds, well then hello, IndexError!
            pix = _pix(top=top_pix, bot=bot_pix)
            row_pixels.append(pix)

        lines.append(row_pixels)
    return lines
