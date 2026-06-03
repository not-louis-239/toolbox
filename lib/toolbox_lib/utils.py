# module for general utils used commonly across programs

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


import re

ANSI_ESCAPE_CODE = re.compile(r'\x1b\[[0-9;]*m')

def raw_len(s: str) -> int:
    """Return the length of a string without ANSI escape codes."""
    raw = ANSI_ESCAPE_CODE.sub('', s)
    return len(raw)

def _test():
    test_text = "\x1b[38;5;249mHello, \x1b[31mWorld!\x1b[0m"
    print(test_text)
    assert raw_len(test_text) == 13

if __name__ == "__main__":
    _test()
