#!/usr/bin/env python3

# v1.0.0
# colsample.py - script to test terminal colours
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


def col(code: int, bg: bool = False) -> str:
    return f"\033[{48 if bg else 38};5;{code}m"

def rgb(rgb_val: tuple[int, int, int], bg: bool = False) -> str:
    r, g, b = rgb_val
    return f"\033[{48 if bg else 38};2;{r};{g};{b}m"

END = "\033[0m"
BOLD = "\033[1m"

def main():
    print("Colour Palette Test")

    print("\nANSI Colours:")
    for i in range(16):
        print(f"{col(i)}{i:03} ", end=('\n' if i%8==7 else ''))
        print(END, end='')

    print("\n8-Bit Colours")
    for i in range(16):
        for j in range(16):
            code = i * 16 + j
            print(f"{col(code)}{code:03}", end=' ')
        print(END)

if __name__ == "__main__":
    main()
