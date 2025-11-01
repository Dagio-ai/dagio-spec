#!/usr/bin/env bash
set -euo pipefail

OUTPUT=${1:-architecture.pdf}
TMP_DIR=$(mktemp -d)
# Collect markdown files relative to this script
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Ensure dependencies exist
command -v md-to-pdf >/dev/null 2>&1 || {
  echo "md-to-pdf is required. Install it with 'npm install -g md-to-pdf @mermaid-js/mermaid-cli'." >&2
  exit 1
}

shopt -s globstar
md_files=("$SCRIPT_DIR"/**/*.md)
shopt -u globstar

if [ ${#md_files[@]} -eq 0 ]; then
  echo "No Markdown files found under $SCRIPT_DIR" >&2
  exit 1
fi

pdf_list=()
for md in "${md_files[@]}"; do
  rel_path=${md#$SCRIPT_DIR/}
  out_pdf="$TMP_DIR/${rel_path%.md}.pdf"
  mkdir -p "$(dirname "$out_pdf")"
  md-to-pdf "$md" --basedir "$(dirname "$md")" --output "$out_pdf"
  pdf_list+=("$out_pdf")
  echo "Rendered $rel_path"
done

echo "Merging into $OUTPUT"
pdftk "${pdf_list[@]}" cat output "$OUTPUT" 2>/dev/null || {
  echo "pdftk not found; attempting qpdf"
  qpdf --empty --pages "${pdf_list[@]}" -- "$OUTPUT"
}

echo "Export complete: $OUTPUT"
