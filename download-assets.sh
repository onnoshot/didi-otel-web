#!/usr/bin/env bash
# Idempotent asset scraper for DİDİ Otel Sapanca redesign.
# Re-run anytime: existing non-empty files are skipped.
set -u
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
REF="https://sapancadidiotel.com/"
ROOT="$(cd "$(dirname "$0")" && pwd)"
ok=0; skip=0; fail=0

dl() { # dl <url> <out>
  local url="$1" out="$2"
  if [ -s "$out" ]; then skip=$((skip+1)); return; fi
  mkdir -p "$(dirname "$out")"
  if curl -sL --fail -A "$UA" -e "$REF" "$url" -o "$out" && [ -s "$out" ]; then
    ok=$((ok+1)); echo "  ok   $out"
  else
    fail=$((fail+1)); rm -f "$out"; echo "  FAIL $url"
  fi
}

# ---- ROOMS (slug:source-list pairs; bash 3.2 safe) ----
ROOMS="king-suit:/tmp/room_4.txt junior-suit:/tmp/room_5.txt superior:/tmp/room_6.txt family:/tmp/room_7.txt triple:/tmp/room_8.txt"
for pair in $ROOMS; do
  slug="${pair%%:*}"; src="${pair##*:}"; [ -f "$src" ] || { echo "missing list $src"; continue; }
  i=0
  while IFS= read -r url; do
    [ -z "$url" ] && continue
    ext="${url##*.}"
    dl "$url" "$ROOT/assets/rooms/$slug/$(printf '%02d' $i).$ext"
    i=$((i+1))
  done < "$src"
done

# ---- GALLERY / SLIDER / SETTINGS ----
if [ -f /tmp/gallery.txt ]; then
  i=0
  while IFS= read -r url; do
    [ -z "$url" ] && continue
    ext="${url##*.}"
    dl "$url" "$ROOT/assets/gallery/$(printf '%02d' $i).$ext"
    i=$((i+1))
  done < /tmp/gallery.txt
fi

echo "---- done: ok=$ok skip=$skip fail=$fail ----"
