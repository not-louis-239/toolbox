#!/usr/bin/env python3

# v1.0.0
# show_tags.py - a quick Git tag displayer

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

from dataclasses import dataclass
import subprocess
import os
import sys

# Constants for terminal colours
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BLUE = "\033[34m"
RESET = "\033[0m"
RED = "\033[31m"

@dataclass
class GitTag:
    commit_hash: str
    date: str
    name: str
    desc: str

def run_git(cmd, cwd):
    """Helper to run git commands and return stripped output."""
    return subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()

def show_help():
    help_text = f"""
{BLUE}Usage:{RESET} show_tags.py [path]

{BLUE}Arguments:{RESET}
  path             Path to the Git repository (default: current directory)

{BLUE}Notes:{RESET}
  - Tags are sorted by creator date (oldest → newest).
"""
    print(help_text)
    sys.exit(0)

def get_repo_tags(repo_path: str) -> list[GitTag]:
    """Fetches all tags and returns a list of GitTag objects."""
    try:
        tags_raw = run_git(["git", "tag", "--sort=creatordate"], cwd=repo_path)
        if not tags_raw:
            return []
        tag_names = tags_raw.splitlines()
    except subprocess.CalledProcessError:
        print(f"{RED}Error: Unable to access Git tags.{RESET}")
        sys.exit(1)

    tag_list: list[GitTag] = []

    for name in tag_names:
        # Fetch Date
        try:
            date = run_git(["git", "log", "-1", "--format=%as", name], cwd=repo_path)
        except subprocess.CalledProcessError:
            date = "????-??-??"

        # Fetch Commit Hash (Short)
        try:
            commit_hash = run_git(["git", "rev-parse", "--short=7", name], cwd=repo_path)
        except subprocess.CalledProcessError:
            commit_hash = "???????"

        # Fetch Annotation/Description
        try:
            desc = run_git(
                ["git", "for-each-ref", f"refs/tags/{name}", "--format=%(contents)"],
                cwd=repo_path
            ).splitlines()[0] if name else "" # Get first line of message only
        except (subprocess.CalledProcessError, IndexError):
            desc = ""

        tag_list.append(GitTag(commit_hash=commit_hash, date=date, name=name, desc=desc))

    return tag_list

def run():
    args = sys.argv[1:]

    if any(arg in args for arg in ["--help", "-h"]):
        show_help()

    positional_args = [a for a in args if not a.startswith("-")]
    repo_input = positional_args[0] if positional_args else "."
    repo_path = os.path.abspath(repo_input.strip().strip("'\""))  # strip quotes

    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print(f"{RED}Error: path '{repo_path}' is not a Git repository.{RESET}")
        sys.exit(1)

    # Print status message
    print("Fetching Git tags...", end="\r", flush=True)

    git_tags = get_repo_tags(repo_path)

    # Clear the "Fetching" line
    print(" " * 30, end="\r")

    if not git_tags:
        print("No tags found.")
        return

    # Build the final output string
    output = [
        f"{BLUE}Repository:{RESET} {repo_path}",
        f"{BLUE}Showing {len(git_tags)} tags (oldest → newest):{RESET}"
    ]

    for tag in git_tags:
        line = f"{YELLOW}{tag.date:<10}{RESET} {CYAN}{tag.commit_hash}{RESET} {GREEN}{tag.name}{RESET}"
        if tag.desc:
            line += f" {tag.desc}"
        output.append(line)

    # Print everything at once
    print("\n".join(output))

def main():
    try:
        run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
