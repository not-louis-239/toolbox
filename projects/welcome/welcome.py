#!/usr/bin/env python3
# welcome.py - entry point for terminal welcome sequence


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

import os
import sys
import json
from typing import Any, NoReturn
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

try:
    root = next(p for p in Path(__file__).parents if (p / ".git").exists())
except StopIteration:
    raise RuntimeError("Could not find repository root directory") from None

sys.path.insert(0, str(root / "lib"))

from toolbox_lib.dialog_boxes import make_dialog_box
from toolbox_lib.welcome_utils import get_day_phase_literal, get_uptime
from toolbox_lib.colours import COL_FAINT, COL_END, COL_BOLD, COL_ERR
from toolbox_lib.ansi_convert import ColourSpace
from toolbox_lib.count_files import count_files_in_dir
from toolbox_lib.ansi_parse import load_ansi_from_img, serialise, blit, unserialise

def die(msg: str, exitcode: int = 1) -> NoReturn:
    print(f"{COL_ERR}{COL_BOLD}fatal{COL_END}: {COL_ERR}{msg}{COL_END}", file=sys.stderr)
    sys.exit(exitcode)

def unescape_str(s: str) -> str:
    return s.replace("\\033", "\x1b")

@dataclass(frozen=True, kw_only=True)
class Args:
    config_path: Path

def parse_args() -> Args:
    import argparse as ap

    ap = ap.ArgumentParser(description="Toolbox Welcome Script")
    ap.add_argument("--config", "-c", dest="config_path", type=Path, default=Path(__file__).resolve().parent / "config.json", help="explicit parameter to point to config file")

    args_raw = ap.parse_args()

    return Args(
        config_path=args_raw.config_path
    )


@dataclass(frozen=True, kw_only=True)
class ClutterWarningThresholds:
    note: int = 15
    warn: int = 30
    crit: int = 50

@dataclass(frozen=True, kw_only=True)
class WelcomeConfig:
    username: str

    date_fmt: str
    time_fmt: str
    uptime_fmt: str

    accent_main: str
    accent_sec: str

    col_info: str
    col_warn: str
    col_err: str

    clutter_warnings: dict[Path, ClutterWarningThresholds] | None

    # optional image path to display ANSI art
    img_path: Path | None
    img_colour_space: ColourSpace
    dialog_box_pos: tuple[int, int] | None

def parse_warning_thresholds(json_data: dict[str, dict[str, int]]) -> dict[Path, ClutterWarningThresholds]:
    """Parse a dictionary of {paths, thresholds} into a
    deserialised ClutterWarningThresholds object for each path."""

    thresholds = {}
    for path_str, threshold_dict in json_data.items():
        path = Path(path_str)
        thresholds_dict = ClutterWarningThresholds(
            note=threshold_dict.get("note", 15),
            warn=threshold_dict.get("warn", 30),
            crit=threshold_dict.get("crit", 50)
        )
        thresholds[path] = thresholds_dict
    return thresholds

def generate_clutter_warnings(config: WelcomeConfig) -> str:
    """Return a formatted string of clutter warnings based on the given configs."""
    if not config.clutter_warnings:
        return ""

    warning_config: dict[Path, ClutterWarningThresholds] = config.clutter_warnings
    out: list[str] = []

    for path_to_scan, thresholds in warning_config.items():
        if not path_to_scan.expanduser().exists():
            print(f"warning: skipping path: no such directory: '{path_to_scan}'", file=sys.stderr)
            continue
        num_files = count_files_in_dir(path_to_scan)

        if num_files >= thresholds.crit:
            severity, colour = "Critical", config.col_err
        elif num_files >= thresholds.warn:
            severity, colour = "Warning", config.col_warn
        elif num_files >= thresholds.note:
            severity, colour = "Note", config.col_info
        else:
            continue

        out.append(f"{colour}{COL_BOLD}{severity}{COL_END}: '{path_to_scan}' {COL_FAINT}({num_files}){COL_END}")

    return "\n".join(out)

def parse_welcome_file(path: Path) -> WelcomeConfig:
    try:
        with open(path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        config_data = {}
    except PermissionError:
        die(f"Invalid JSON: read permission denied: '{path}'")
    except json.JSONDecodeError:
        die(f"Invalid JSON: '{path}'")
    except Exception as e:
        err_str = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
        die(f"Unexpected error: '{path}' ({err_str})")

    username = config_data.get("username", Path.home().name)

    date_fmt = config_data.get("date_fmt", "%A %d %B %Y")
    time_fmt = config_data.get("time_fmt", "%H:%M")
    uptime_fmt = config_data.get("uptime_fmt", "{hours}h {minutes}m")

    accent_main = unescape_str(config_data.get("accent_main", "\033[95m"))
    accent_sec = unescape_str(config_data.get("accent_sec", "\033[92m"))

    col_info = unescape_str(config_data.get("col_info", "\033[94m"))
    col_warn = unescape_str(config_data.get("col_warn", "\033[93m"))
    col_err = unescape_str(config_data.get("col_err", "\033[91m"))

    img_path = config_data.get("img_path", None)
    if img_path is not None:
        img_path = Path(img_path).resolve()
        if not img_path.exists():
            die(f"no such image file: '{img_path}'")
        if not os.access(img_path, os.R_OK):
            die(f"invalid image file: read permission denied: '{img_path}'")
        if not img_path.is_file():
            die(f"not an image file: '{img_path}'")

        dialog_box_pos_raw: list[int] | None = config_data.get("dialog_box_pos", None)
        if dialog_box_pos_raw:
            # Parse coordinates
            if not isinstance(dialog_box_pos_raw, list):
                die("dialog_box_pos must be an array of two integers")

            if len(dialog_box_pos_raw) != 2:
                die("dialog_box_pos must be an array of two integers")

            parsed: list[int] = []
            for coord in dialog_box_pos_raw:
                try:
                    parsed_int = int(coord)
                    if parsed_int < 0:
                        die(f"expected non-negative integer for dialog_box_pos, got {coord!r}")
                    parsed.append(parsed_int)
                except ValueError:
                    die(f"expected non-negative integer for dialog_box_pos, got {coord!r}")
            dialog_box_pos = (parsed[0], parsed[1])
        else:
            dialog_box_pos = None
    else:
        dialog_box_pos = None

    # parse clutter warnings
    clutter_warnings_raw: dict[str, Any] | None = config_data.get("clutter_warnings", None)
    if not clutter_warnings_raw:
        clutter_warnings: dict[Path, ClutterWarningThresholds] | None = None
    else:
        clutter_warnings: dict[Path, ClutterWarningThresholds] | None = parse_warning_thresholds(clutter_warnings_raw)

    return WelcomeConfig(
        username=username,

        date_fmt=date_fmt,
        time_fmt=time_fmt,
        uptime_fmt=uptime_fmt,

        accent_main=accent_main,
        accent_sec=accent_sec,

        col_info=col_info,
        col_warn=col_warn,
        col_err=col_err,

        clutter_warnings=clutter_warnings,

        img_path=img_path,
        dialog_box_pos=dialog_box_pos,
        img_colour_space=config_data.get("img_colour_space", "true")
    )

def main():
    args = parse_args()
    day_phase_literal: str = get_day_phase_literal()
    config = parse_welcome_file(args.config_path)

    now = datetime.now()
    date_str = now.strftime(config.date_fmt)
    time_str = now.strftime(config.time_fmt)

    try:
        uptime_seconds = get_uptime()
        _uptime_str = config.uptime_fmt.format(
            hours=int(uptime_seconds // 3600),
            minutes=int((uptime_seconds % 3600) // 60)
        )
        uptime_display_str = f"{config.accent_sec}↑{COL_END} {_uptime_str}"
    except RuntimeError as e:
        err_str = str(e)
        if len(err_str) > 40:
            err_str = err_str[:39] + "…"

        uptime_seconds = None
        uptime_display_str = f"{config.col_err}ø{COL_END} Uptime N/A - reason: {err_str}{COL_END}"  # truncate error message to prevent overflow

    print(f"{date_str} {COL_FAINT}·{COL_END} {config.accent_main}{time_str}{COL_END}")

    dialog_lines: list[str] = []

    dialog_lines.append(f"{day_phase_literal}, {config.accent_sec}{config.username}{COL_END}, welcome back!")
    dialog_lines.append(uptime_display_str)
    dialog_lines.append(generate_clutter_warnings(config=config))

    dialog_out = make_dialog_box("\n".join(dialog_lines), COL_FAINT)

    if not config.img_path:
        print(dialog_out)
    else:
        try:
            ansi_pixels = load_ansi_from_img(config.img_path)
        except Exception as e:
            die(f"failed to load image: {e}")

        if config.dialog_box_pos is None:
            print(serialise(ansi_pixels, mode=config.img_colour_space))
            print(dialog_out)
            return

        blit(ansi_pixels, unserialise(dialog_out), pos=config.dialog_box_pos)
        print(serialise(ansi_pixels, mode=config.img_colour_space))

if __name__ == "__main__":
    main()
