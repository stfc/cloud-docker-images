#!/usr/bin/env bash
set -euo pipefail

base="$1"
head="$2"

changed=$(git diff --name-only "$base...$head")

find . -name Dockerfile -not -path './.git/*' -printf '%h\n' |
while read -r dir; do
    dir=${dir#./}

    # Only consider directories containing both Dockerfile and version.txt 
    # as these directories will be the name of the image that has changed
    [[ -f "$dir/Dockerfile" && -f "$dir/version.txt" ]] || continue

    # Check whether anything in the image directory changed
    if grep -q "^$dir/" <<< "$changed"; then
        # version.txt must also have changed
        if ! grep -q "^$dir/version.txt$" <<< "$changed"; then
            echo "ERROR: $dir has changed, but version.txt was not changed - bump the version!" >&2
            exit 1
        fi
        echo "$dir"
    fi
done |
sort -u
