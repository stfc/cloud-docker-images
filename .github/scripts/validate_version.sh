#!/usr/bin/env bash
set -euo pipefail

image_path="$1"
base="$2"

version_file="$image_path/version.txt"

new=$(tr -d '[:space:]' < "$version_file")

if [[ ! "$new" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "ERROR: $version_file contains '$new', expected MAJOR.MINOR.PATCH"
    exit 1
fi

tag="$(basename "$image_path")-$new"

if git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
    echo "ERROR: tag $tag already exists"
    exit 1
fi

if ! git cat-file -e "$base:$version_file" 2>/dev/null; then
    echo "$image_path is new at $new"
    exit 0
fi

old=$(git show "$base:$version_file" | tr -d '[:space:]')

if [[ "$old" == "$new" ]]; then
    echo "ERROR: $version_file was not bumped (still $old)"
    exit 1
fi

if [[ "$(printf '%s\n%s\n' "$old" "$new" | sort -V | head -1)" != "$old" ]]; then
    echo "ERROR: version went backwards: $old -> $new"
    exit 1
fi

echo "$image_path correctly updated: $old -> $new"