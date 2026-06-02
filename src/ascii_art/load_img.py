# Copyright 2026 Louis Masarei-Boulton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

from PIL import Image
import numpy as np

def load_img(fp: Path) -> np.ndarray:
    """Load image from file path and convert to a NumPy array of
    shape (width, height, 4) to represent a 2-dimensional array
    of RGBA values."""

    # Open the image and ensure it's in RGBA mode
    with Image.open(fp) as img:
        rgba_img = img.convert("RGBA")
        # Convert to a standard NumPy array (creates shape: height, width, 4)
        arr = np.array(rgba_img)
        # Transpose axes 0 and 1 to change shape from (height, width, 4) to (width, height, 4)
        return np.transpose(arr, (1, 0, 2))
