#!/usr/bin/env python3

# blackimg/main.py - main script to generate black images of customisable sizes
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

import os
import secrets
from PIL import Image

def create_black_image():
    # Prompt user for dimensions
    user_input = input("Enter width and height separated by a comma (e.g., 800, 600): ")

    try:
        # Parse the input
        width, height = map(int, user_input.split(','))

        # Create a randomized hex suffix (e.g., a1b2c3d)
        suffix = secrets.token_hex(4)[:7]
        filename = f"black_image_{suffix}.png"

        # Create a new black image (RGB mode, (0, 0, 0) is black)
        img = Image.new("RGB", (width, height), (0, 0, 0))

        # Get the current script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(script_dir, filename)

        # Save the image
        img.save(save_path)
        print(f"Successfully created {filename} ({width}x{height}) in '{script_dir}'")

    except ValueError:
        print("Error: Please ensure you enter two numbers separated by a comma.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    create_black_image()
