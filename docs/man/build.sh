#!/bin/bash
# Build man page from markdown
# Requires: pandoc

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$DOCS_DIR/man"

mkdir -p "$OUTPUT_DIR"

# Build vorto.1 man page
if command -v pandoc &> /dev/null; then
    pandoc -s -t man "$SCRIPT_DIR/vorto.1.md" -o "$OUTPUT_DIR/vorto.1"
    echo "Built: $OUTPUT_DIR/vorto.1"
else
    echo "pandoc not installed. Install with: pip install pandoc"
    echo "Or copy vorto.1.md to vorto.1 for manual formatting"
fi