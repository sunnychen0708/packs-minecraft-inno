#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <pack-name> <version>"
  exit 2
fi

PACK="$1"
VERSION="$2"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"

if [[ -d "$ROOT/datapacks/$PACK" ]]; then
  SRC="$ROOT/datapacks/$PACK"
elif [[ -d "$ROOT/resourcepacks/$PACK" ]]; then
  SRC="$ROOT/resourcepacks/$PACK"
else
  echo "Pack not found: $PACK"
  exit 1
fi

mkdir -p "$DIST"
OUT="$DIST/$PACK-$VERSION.zip"
rm -f "$OUT"

(
  cd "$SRC"
  zip -qr "$OUT" .
)

echo "$OUT"
