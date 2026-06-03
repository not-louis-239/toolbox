# welcome utils

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

import subprocess
import re
import time
from datetime import datetime

def get_day_phase() -> float:
    """Returns a value between 0 and 86,400 representing
    the total seconds elapsed since the last midnight."""
    now = datetime.now()
    start_of_day = datetime(now.year, now.month, now.day)
    return (now - start_of_day).total_seconds()

def get_day_phase_literal() -> str:
    p = get_day_phase()
    if p < 12 * 3600:
        return "Morning"
    if p < 18 * 3600:
        return "Afternoon"
    return "Evening"

def get_uptime() -> float:
    """Get an uptime value in terms of total seconds since
    last reboot. Throws errors if it cannot be determined."""
    try:
        cmd = ["sysctl", "-n", "kern.boottime"]
        out = subprocess.check_output(cmd, text=True)
        match = re.search(r"\d+", out)
        if match is None:
            raise RuntimeError("Failed to parse uptime output.")
        last_boot_time = int(match.group())
        uptime = time.time() - last_boot_time

    except Exception:
        raise

    return uptime

def _test():
    print(f"Current Day Phase: {get_day_phase():,.0f} seconds since last midnight.")
    print(f"Uptime: {get_uptime():,.0f}s")

if __name__ == "__main__":
    _test()
