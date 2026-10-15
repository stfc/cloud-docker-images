#!/usr/bin/env bash
set -euo pipefail

# Bump the patch version of a given version.txt
# Usage: bump_patch_version.sh <version.txt filepath>
 
version_file="${1:-}"

if [[ -z "$version_file" ]]; then
    echo "Usage: $0 <path/to/version.txt>" >&2
    exit 1
fi

if [[ ! -f "$version_file" ]]; then
    echo "Error: file does not exist: $version_file" >&2
    exit 1
fi

version=$(<"$version_file")


if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: $version_file must contain exactly one version in MAJOR.MINOR.PATCH format" >&2
    exit 1
fi

IFS='.' read -r major minor patch <<< "$version"

printf '%s.%s.%s\n' "$major" "$minor" "$((patch + 1))" > "$version_file"
