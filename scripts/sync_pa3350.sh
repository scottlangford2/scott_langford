#!/usr/bin/env bash
# Sync PA 3350 public-facing course materials from the Dropbox course folder
# into the website repo's files/ directory. ALLOWLIST ONLY — never copies
# answer keys, third-party comparator/prior syllabi, or reading PDFs.
# Re-run any time a source document changes; then review, commit, and push.
set -euo pipefail

SRC="/Users/scottlangford/Dropbox/Texas State/Teaching/PA 3350 - Public Policy Process/2026 - Fall"
DST="$(cd "$(dirname "$0")/.." && pwd)/files"

# Explicit allowlist: source file  ->  published filename
declare -a MAP=(
  "Syllabus.pdf|PA_3350_Syllabus_Fall2026.pdf"
  "Course_Map.pdf|PA_3350_Course_Map_Fall2026.pdf"
  "Module_Readings.pdf|PA_3350_Readings_Fall2026.pdf"
)

echo "Syncing PA 3350 materials -> $DST"
for entry in "${MAP[@]}"; do
  src="${entry%%|*}"; out="${entry##*|}"
  if [[ -f "$SRC/$src" && -s "$SRC/$src" ]]; then
    cp "$SRC/$src" "$DST/$out"
    echo "  ok   $out  ($(wc -c < "$DST/$out") bytes)"
  else
    echo "  MISS $src not found or empty (Dropbox eviction?) — skipped"
  fi
done
echo "Done. Publishes ONLY: syllabus, course map, readings list (links-only)."
echo "Excluded by design: answer keys, comparator/prior syllabi, reading PDFs."
echo "Next: review, then  git -C \"$(dirname "$DST")\" add files/PA_3350_*.pdf _teaching/public-policy-process.md && git commit && git push"
