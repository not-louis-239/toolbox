#!/usr/bin/env python3

# Enter the path to your Stardew Valley save file that you
# would like to back up, and the output path where it will save
# a backup file AND a mod receipt (a text file listing all the mods you have installed, and their versions if they can be found).

# The mod receipt is reflective of the mods inside your mods folder
# when you run the script, so make sure to run it before you add/remove any mods if you want it to be accurate.
# Mod receipts help you go back to old saves without bricking them
# due to mod incompatibilities between versions.

import shutil
import random
import sys
import argparse as ap

from pathlib import Path
from dataclasses import dataclass
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).parent))  # allow importing from the same directory

from svmr import (
    DEFAULT_SV_MODS_FOLDER,
    die,
    make_stardew_valley_mod_receipt,
    get_stardew_valley_mods
)

HEX_CHARS = "0123456789abcdef"

SEASON_IDX: dict[str, int] = {  # used for parsing the XML save file
    "spring": 0,
    "summer": 1,
    "fall": 2,
    "winter": 3
}

@dataclass
class Args:
    save_folder: Path
    output_folder: Path
    mods_folder: Path

def strip_ansi_escape_codes(s: str) -> str:
    # https://stackoverflow.com/a/14693789
    import re
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', s)

def retrieve_year_season_day(save_folder: Path) -> tuple[int, int, int]:
    # get the most recently modified .xml file in the save folder, and parse the year, season, and day from it
    # this is used to name the output folder in the format "yXX_Season_DD" (e.g. "y01_Spring_01")

    # It seems that the XML has the same name as the folder
    # but no XML suffix? Weird.
    xml_path = save_folder / f"{save_folder.name}"

    # parse the XML file to get the year, season, and day

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Safely extract required text values from the XML, with clear errors
    def get_required_text(elem_name: str) -> str:
        # Try exact match first
        elem = root.find(elem_name)
        # If not found, search the entire tree (case-insensitive, namespace-aware)
        if elem is None:
            lower_name = elem_name.lower()
            for node in root.iter():
                tag = node.tag
                if not isinstance(tag, str):
                    continue
                if '}' in tag:
                    tag = tag.split('}', 1)[1]
                if tag.lower() == lower_name:
                    elem = node
                    break

        if elem is None:
            die(f"Save file missing <{elem_name}> element: '{xml_path}'")
        if elem.text is None:
            die(f"Save file <{elem_name}> element has no text: '{xml_path}'")
        return elem.text.strip()

    year_text = get_required_text("year")
    try:
        year = int(year_text)
    except ValueError:
        die(f"Invalid year value '{year_text}' in '{xml_path}'")

    season_text = get_required_text("season")
    season_key = season_text.lower()
    if season_key not in SEASON_IDX:
        die(f"Unknown season '{season_text}' in '{xml_path}'")
    season = SEASON_IDX[season_key]

    day_text = get_required_text("dayOfMonth")
    try:
        day = int(day_text)
        if not 1 <= day <= 28:
            die(f"dayOfMonth value out of range (1-28) '{day_text}' in '{xml_path}' (must be 1-28 inclusive)")
    except ValueError:
        die(f"Invalid dayOfMonth value '{day_text}' in '{xml_path}'")

    return year, season, day

def make_folder_name(year: int, season: int, day: int) -> str:
    return f"y{year:04d}_{season:02d}{day:02d}"

def parse_args() -> Args:
    parser = ap.ArgumentParser(
        description=(
            "Back up a Stardew Valley save file and installed mods.\n"
            "\n"
            "Creates a timestamped sub-directory (e.g., 'y0001_0101') inside a pre-existing\n"
            "output folder. This backup directory will contain:\n"
            "  - A copy of your Stardew Valley save folder.\n"
            "  - A manifest text file listing all currently active mods and their versions."
        ),
        formatter_class=ap.RawDescriptionHelpFormatter  # Stop eating all my newlines, argparse!!
    )

    parser.add_argument("save_folder", type=Path, help="The path to the Stardew Valley save folder you want to back up.")
    parser.add_argument("output_folder", type=Path, help="The path to the folder where the backup and mod receipt will be saved.")
    parser.add_argument("--mods-folder", type=Path, default=DEFAULT_SV_MODS_FOLDER, help=f"The path to your Stardew Valley mods folder (default: '{DEFAULT_SV_MODS_FOLDER}').")
    args = parser.parse_args()

    if not args.save_folder.exists():
        die(f"Invalid save folder: No such directory: '{args.save_folder}'")
    if not args.save_folder.is_dir():
        die(f"Invalid save folder: Not a directory: '{args.save_folder}'")
    if not args.output_folder.exists():
        die(f"Invalid output folder: No such directory: '{args.output_folder}'")
    if not args.output_folder.is_dir():
        die(f"Invalid output folder: Not a directory: '{args.output_folder}'")
    if not args.mods_folder.exists():
        die(f"Invalid mod folder: No such directory: '{args.mods_folder}'")
    if not args.mods_folder.is_dir():
        die(f"Invalid mod folder: Not a directory: '{args.mods_folder}'")

    return Args(save_folder=args.save_folder, output_folder=args.output_folder, mods_folder=args.mods_folder)

def main():
    args = parse_args()
    ysd = retrieve_year_season_day(args.save_folder)
    folder_name = make_folder_name(*ysd)

    # Salt the backup path with a random hex suffix to avoid name collisions
    salt = ''.join(random.choices(HEX_CHARS, k=8))
    backup_path = args.output_folder / (folder_name + "__" + salt)

    # copy save folder to output folder
    shutil.copytree(args.save_folder, backup_path / args.save_folder.name)

    mods = get_stardew_valley_mods(args.mods_folder)
    receipt = strip_ansi_escape_codes(make_stardew_valley_mod_receipt(mods))
    with open(backup_path / "mod_receipt.md", "w", encoding="utf-8") as f:
        f.write(receipt)

if __name__ == "__main__":
    main()
