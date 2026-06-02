#!/bin/bash

# svbackup - stardew valley mod backup
# use this to back up your Stardew Valley save folder along with a receipt of what mods you have when making a backup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/src/svbackup.py" "$@"
