# tool for formatting dialog boxes in the terminal

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


from toolbox_lib.utils import raw_len
from toolbox_lib.colours import COL_END, COL_FAINT

def make_dialog_box(text: str, border_colour: str = "") -> str:
    """Creates a dialog box from a list of lines."""
    lines = text.splitlines()

    max_line_len = max((raw_len(line) for line in lines), default=0)

    body: list[str] = []
    for line in lines:
        body.append(f"{border_colour}│{COL_END} {line}{' ' * (max_line_len - raw_len(line))} {border_colour}│{COL_END}\n")

    dialog_box = (
        f"{border_colour}┌{'─' * (max_line_len + 2)}┐\n{COL_END}"
        + "".join(body)
        + f"{border_colour}└{'─' * (max_line_len + 2)}┘{COL_END}"
    )

    return dialog_box

def _test():
    test_cases = [
        "Hello, World!",
        "Multiline text\nThis is the second line",
        "Short line",
        "Line with colour codes: \033[31mRed\033[0m and \033[32mGreen\033[0m.",
        "Multiline message with formatting codes and Unicode characters:\n\033[1m\033[92m↑ 0:00:23\033[0m\n\033[2mThis is some faint text.\033[0m",
        ""  # Empty string test case
    ]

    for test_case in test_cases:
        print(make_dialog_box(test_case, COL_FAINT))

if __name__ == "__main__":
    _test()
