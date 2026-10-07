#!/usr/bin/env bash
set -euo pipefail

# Shared helpers. Sourced by the other scripts, not run directly.

# allows these scripts to be used by github runners
# if run locally will go back to stdout and summaries discarded
: "${GITHUB_OUTPUT:=/dev/stdout}"
: "${GITHUB_STEP_SUMMARY:=/dev/null}"
 
# Emit a step output (key=value).
output() { printf '%s=%s\n' "$1" "$2" >> "$GITHUB_OUTPUT"; }
 
# Append a line to the job summary.
summary() { printf '%s\n' "$*" >> "$GITHUB_STEP_SUMMARY"; }
 
# Logging. All to stderr.
info() { printf '%s\n' "$*" >&2; }
warn() { printf '::warning::%s\n' "$*" >&2; }
fail() { printf '::error::%s\n' "$*" >&2; exit 1; }
 
# The image name for a image_path is just its directory name.
get_image_name() { basename "$1"; }

# Assert that the named variables are set and non-empty.
require() {
  local var
  for var in "$@"; do
    [ -n "${!var:-}" ] || fail "$var is not set"
  done
}
 
# Read and validate a image_path's version.txt. Prints the version.
read_version() {
  local image_path=$1 file version
  file="$image_path/version.txt"
  [ -f "$file" ] || fail "$file not found"
  version=$(tr -d '[:space:]' < "$file")
  [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] \
    || fail "$file is '$version', expected MAJOR.MINOR.PATCH"
  printf '%s' "$version"
}
 
# Locate a image_path's Dockerfile, at any depth. Prints the path.
find_dockerfile() {
  local image_path=$1 dockerfile
  dockerfile=$(find "$image_path" -name Dockerfile | head -n1)
  [ -n "$dockerfile" ] || fail "no Dockerfile found under $image_path"
  printf '%s' "$dockerfile"
}