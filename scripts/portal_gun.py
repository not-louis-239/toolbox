#!/usr/bin/env python3

# 'portal' (symlink) manager for fast travel around your filesystem in your terminal
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


import sys
import shlex
from pathlib import Path

# If the symlink hub is missing, make it
PORTALS_DIR = Path.home() / "portals"
PORTALS_DIR.mkdir(exist_ok=True)

# List of portals to ignore in ls / fsck commands
IGNORE = [".DS_Store"]

def col(code: int) -> str:
    return f"\033[38;5;{code}m"

RESET = "\033[0m"
BOLD = "\033[1m"

COL_OK = col(2)
COL_ERR = col(3)
COL_INFO = col(4)

def portal_path(name: str) -> Path:
    return PORTALS_DIR / name

def print_err(msg: str):
    print(f"{COL_ERR}{msg}{RESET}")

def print_ok(msg: str):
    print(f"{COL_OK}{msg}{RESET}")

# Commands
def add_portal(name, target):
    p = portal_path(name)
    target = Path(target).expanduser().resolve()

    if p.exists():
        print_err(f"Portal, file or directory '{name}' already exists")
        return
    if not target.exists():
        print_err(f"Target does not exist: {target}")
        return

    p.symlink_to(target)
    print_ok(f"Added portal '{name}' → {target}")

def rm_portal(name):
    p = portal_path(name)

    if not p.exists():
        print_err(f"No such portal: {name}")
        return
    if not p.is_symlink():
        print_err(f"Not a portal: {name}")
        return

    p.unlink()
    print_ok(f"Removed portal '{name}'")

def list_portals():
    for p in sorted(PORTALS_DIR.iterdir()):
        if p.name in IGNORE:
            continue

        if not p.is_symlink():
            print(f"{COL_ERR}{p.name}{RESET} (not a portal)")
            continue
        try:
            target = p.resolve()
            print(f"{COL_INFO}{p.name}{RESET} → {target}")
        except FileNotFoundError:
            print(f"{COL_ERR}{p.name}{RESET} → (dangling)")

def rename_portal(name, new):
    old_path = portal_path(name)

    if not old_path.is_symlink():
        print_err(f"Not a portal: {name}")
        return

    new_path = portal_path(new)

    if not old_path.exists():
        print_err(f"No such portal: {name}")
        return
    if new_path.exists():
        print_err(f"Target name already exists: {new}")
        return

    old_path.rename(new_path)
    print_ok(f"Renamed '{name}' → '{new}'")

def relink_portal(name, target):
    p = portal_path(name)
    target = Path(target).expanduser().resolve()

    if not p.exists():
        print_err(f"No such portal: {name}")
        return
    if not target.exists():
        print_err(f"Target does not exist: {target}")
        return

    p.unlink()
    p.symlink_to(target)
    print_ok(f"Relinked '{name}' → {target}")

def fsck_portals(fix: bool = False):
    """Check portal integrity. When called with the fix flag, will remove malfunctioning portals."""

    seen = {}
    num_errors: int = 0
    num_files_removed: int = 0

    for p in PORTALS_DIR.iterdir():
        if p.name in IGNORE:
            continue

        # Report (but never remove) non-portals, even with fix=True
        if not p.is_symlink():
            print_err(f"not a portal: {p.name}")

        target = p.resolve()
        if not target.exists():
            if fix:
                p.unlink()
                num_files_removed += 1

            # Dangling symlink
            print_err(f"dangling: {p.name}")
            num_errors += 1
            continue

        seen[p] = target
        if p == target:
            print_err(f"self-loop: {p.name}")
            num_errors += 1

            if fix:
                p.unlink()
                num_files_removed += 1

    for a, b in seen.items():
        if b in seen and seen[b] == a:
            print_err(f"cycle: {a.name} ↔ {b.name}")
            num_errors += 1

            if fix:
                p.unlink()
                num_files_removed += 1

    if num_errors == 0:
        print_ok("No portal issues found")
    else:
        if fix:
            print_err(f"Found {num_errors} errors. Removed {num_files_removed} broken portals.")
        else:
            print_err(f"Found {num_errors} errors. Run fsck --fix to remove broken portals.")


def show_help():
    commands = {
        "add [name] [path]": "Add a symlink to ~/portals.",
        "rm [name]": "Remove a symlink from ~/portals.",
        "ls": "List all symlinks in ~/portals and their destinations",
        "rename [name] [new]": "Rename a portal, if it exists.",
        "relink [name] [path]": "Keep a portal's name unchanged, but change the target path.",
        "help": "Show this help message.",
        "fsck": "Check for broken or circular portals.",
        "clear, cls": "Clear the terminal screen.",
        "exit, quit": "Exit the REPL."
    }

    print("Available commands:")

    max_len = max(len(key) for key in commands.keys())
    for command, description in commands.items():
        print(f"{COL_INFO}{command:<{max_len}}  {RESET}{description}")

def exit_repl(newline: bool = False):
    print(f"{'\n' if newline else ''}Exited.")
    sys.exit(0)

def clear_screen():
    print("\033[H\033[J", end='')

def run_repl():
    print(f"{COL_OK}{BOLD}Portal Gun Shell{RESET}")
    print(f"Type 'help' to see available commands.")
    print(f"Use Ctrl-C, Ctrl-D, quit or exit to exit the REPL")

    # Interactive REPL
    while True:
        try:
            cmd_input = input(f"{COL_OK}→{RESET} ")
            args = shlex.split(cmd_input)
        except ValueError as e:
            print(f"{COL_ERR}Syntax error:{RESET} {e}")
            continue
        except KeyboardInterrupt:
            exit_repl(newline=True)
        except EOFError:
            exit_repl(newline=True)

        if not args:
            continue
        cmd = args.pop(0)

        if cmd == "add" and len(args) == 2:
            add_portal(*args)
        elif cmd == "rm" and len(args) == 1:
            rm_portal(args[0])
        elif cmd == "ls" and not args:
            list_portals()
        elif cmd == "rename" and len(args) == 2:
            rename_portal(*args)
        elif cmd == "relink" and len(args) == 2:
            relink_portal(*args)
        elif cmd == "fsck" and 0 <= len(args) <= 1:
            if len(args) == 1 and args[0] == "--fix":
                fsck_portals(fix=True)
            else:
                fsck_portals()
        elif cmd == "help":
            show_help()
        elif cmd in ("exit", "quit"):
            exit_repl()
        elif cmd in ("clear", "cls"):
            clear_screen()
        else:
            print_err("Invalid command or arguments")

def main():
    try:
        run_repl()
    except EOFError:
        exit_repl(newline=True)

if __name__ == "__main__":
    main()