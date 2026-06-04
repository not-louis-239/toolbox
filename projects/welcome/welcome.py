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

import sys
import json
from typing import Any
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
from toolbox_lib.colours import COL_FAINT, COL_END, COL_BOLD
from toolbox_lib.count_files import count_files_in_dir

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

def parse_warning_thresholds(json_data: dict[str, Any]) -> dict[Path, ClutterWarningThresholds]:
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
        raise PermissionError(f"Read permission denied: {path}") from None
    except json.JSONDecodeError:
        raise RuntimeError("Invalid JSON file") from None
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from None

    username = config_data.get("username", Path.home().name)

    date_fmt = config_data.get("date_fmt", "%A %d %B %Y")
    time_fmt = config_data.get("time_fmt", "%H:%M")
    uptime_fmt = config_data.get("uptime_fmt", "{hours}h {minutes}m")

    accent_main = config_data.get("accent_main", "\033[95m")
    accent_sec = config_data.get("accent_sec", "\033[92m")

    col_info = config_data.get("col_info", "\033[94m")
    col_warn = config_data.get("col_warn", "\033[93m")
    col_err = config_data.get("col_err", "\033[91m")
    clutter_warnings = config_data.get("clutter_warnings", None)

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

        clutter_warnings=clutter_warnings
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
    print(dialog_out)

if __name__ == "__main__":
    main()

