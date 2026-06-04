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

from dataclasses import dataclass

def col(colour: tuple[int, int, int] | int | None, bg: bool = False) -> str:
    """Generate a colour code for the given colour."""

    if colour is None:
        return "49" if bg else "39"

    if isinstance(colour, int):
        return f"{48 if bg else 38};5;{colour}"

    r, g, b = colour
    return f"{48 if bg else 38};2;{r};{g};{b}"


@dataclass
class ANSIPixel:
    # tuple[int, int, int] = TrueColor (r, g, b)
    # int                  = 8-bit colours (0-255)
    # None                 = default colour
    bg_colour: tuple[int, int, int] | int | None = None
    fg_colour: tuple[int, int, int] | int | None = None
    fg_char: str = " "
    fg_faint: bool = False

    def render(self) -> str:
        """Serialise the ANSIPixel into a string that can be
        printed to the terminal."""

        codes: list[str] = []
        codes.append(col(self.fg_colour, False))
        codes.append(col(self.bg_colour, True))

        if self.fg_faint:
            codes.append("2")
        else:
            codes.append("22")  # cancel faint

        return f"\033[{';'.join(c for c in codes if c)}m{self.fg_char}"


def serialise(img: list[list[ANSIPixel]]) -> str:
    """Serialise an image into a string that can be printed to the terminal."""
    lines = []
    for row in img:
        lines.append("".join(p.render() for p in row))

    return "\n".join(lines)


def unserialise(src: list[str]) -> list[list[ANSIPixel]]:
    """Parse an image from a list of string rows
    into a list of ANSIPixels. Expects that the source
    does not have trailing newlines."""

    ... # TODO: implement this function
