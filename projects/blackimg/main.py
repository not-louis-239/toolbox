#!/usr/bin/env python3

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
