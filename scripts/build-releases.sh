#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"

rm -rf "$DIST"
mkdir -p "$DIST"

(
  cd "$ROOT/datapacks/vanilla-utilities"
  zip -qr "$DIST/vanilla-utilities-v3.2.zip" . -x ".git/*"
)

(
  cd "$ROOT/datapacks/warehouse"
  zip -qr "$DIST/warehouse-v4.0.zip" . -x ".git/*"
)

echo "Built:"
ls -lh "$DIST"
