#!/usr/bin/env bash
# keel installer — copies this skill folder into ~/.claude/skills/keel and shows the one-time intro.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME}/.claude/skills/keel"

if [ -d "$DEST" ]; then
  echo "keel is already installed at: $DEST"
  echo "Remove it first if you want to reinstall:  rm -rf \"$DEST\""
  exit 1
fi

mkdir -p "${HOME}/.claude/skills"
cp -R "$SRC" "$DEST"

# strip dev cruft so the one-time intro fires fresh on this install
rm -f  "$DEST/.introduced" "$DEST/.DS_Store"
rm -rf "$DEST/.git"
find "$DEST" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true

echo "keel installed at: $DEST"
echo
python3 "$DEST/scripts/docs.py" intro
