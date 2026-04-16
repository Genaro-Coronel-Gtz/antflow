#!/usr/bin/env bash

set -e

DIST_INTERNAL="dist/antflow/_internal"
DIST_BIN="dist/antflow/antflow"
DEST_DIR="/usr/local/bin"

echo "==> Removing previous binary..."
sudo rm -rf "${DEST_DIR}/_internal"

echo "==> Removing previous executable..."
sudo rm -f "${DEST_DIR}/antflow"

echo "==> Copying _internal..."
sudo cp -r "${DIST_INTERNAL}" "${DEST_DIR}"

echo "==> Copying antflow executable..."
sudo cp "${DIST_BIN}" "${DEST_DIR}"

echo ""
echo "✓ Installation completed successfully."