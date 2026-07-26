#!/usr/bin/env bash
# Static site link & structure verification
# Usage: bash verify-links.sh /path/to/site
set -euo pipefail

DIR="${1:?Usage: verify-links.sh /path/to/site}"
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); }
fail() { FAIL=$((FAIL+1)); echo "FAIL: $1"; }

echo "=== Static site verification: $DIR ==="

# Collect all HTML files
HTML_FILES=("$DIR"/*.html)
NUM_HTML=${#HTML_FILES[@]}

# 1. Required files exist — detect by scanning HTML for href/src
for page in "${HTML_FILES[@]}"; do
  # Extract internal href targets (.html, .css, .js, images)
  grep -ohP 'href="(?!http|#|mailto:)[^"]*\.(html|css|js|png|jpg|svg|ico)"' "$page" 2>/dev/null \
    | sed 's/href="//;s/"//' | sort -u | while read -r ref; do
    [ -f "$DIR/$ref" ] || fail "broken link in $(basename "$page"): $ref"
  done
  # Extract internal src targets
  grep -ohP 'src="(?!http)[^"]*\.(js|css|png|jpg|svg)"' "$page" 2>/dev/null \
    | sed 's/src="//;s/"//' | sort -u | while read -r ref; do
    [ -f "$DIR/$ref" ] || fail "broken src in $(basename "$page"): $ref"
  done
done
ok

# 2. Check for stale path prefixes (css/ and js/ when site uses flat structure)
stale_css=$(grep -rnP 'href="css/' "${HTML_FILES[@]}" 2>/dev/null || true)
stale_js=$(grep -rnP 'src="js/' "${HTML_FILES[@]}" 2>/dev/null || true)
if [ -z "$stale_css" ] && [ -z "$stale_js" ]; then
  ok
else
  [ -n "$stale_css" ] && fail "stale css/ path prefix found: $stale_css"
  [ -n "$stale_js" ] && fail "stale js/ path prefix found: $stale_js"
fi

# 3. No circular or self-referencing variant/direction paths
stale_refs=$(grep -rnP 'variant-|direction-' "${HTML_FILES[@]}" 2>/dev/null || true)
if [ -z "$stale_refs" ]; then ok; else fail "stale variant/direction ref: $stale_refs"; fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && echo "ALL CHECKS PASSED" || exit 1
