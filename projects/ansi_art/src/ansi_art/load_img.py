# load_img.py - module for loading images for the ANSI art generator
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

from pathlib import Path

from PIL import Image
import numpy as np

def load_img(fp: Path) -> np.ndarray:
    """Load image from file path and convert to a NumPy array of
    shape (height, width, 4) to represent a 2-dimensional array
    of RGBA values."""

    with Image.open(fp) as img:
        rgba_img = img.convert("RGBA")

    arr = np.array(rgba_img)
    return arr
