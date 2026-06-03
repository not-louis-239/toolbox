# ASCII Art Generator

This project uses Python to accept an image path and convert it to a script that prints terminal art, using `▀`, `▄` and escape codes to handle transparency to ensure proper display inside the terminal.

This is mostly a utility for making pixel art that can be printed in the terminal. Depending on:
- the font that you are using in your terminal;
- your terminal's colour system (ANSI, 256, true colour);
- and terminal size,
the output may or may not print correctly. Hence, it is also not recommended to be used on large images.

## How to Use

1. Clone the repository: `git clone https://github.com/not-louis-239/ascii_art_generator.git`
2. Run the executable: `bin/ascii_art /path/to/image.png -o /path/to/output.py`. The script will then run the freshly produced script.

## Requirements

- Python 3.x (tested on 3.14, older versions may or may not work)
- For futher dependencies, run: `pip install -r requirements.txt`
