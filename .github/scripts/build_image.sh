#!/usr/bin/env bash

set -euo pipefail

# Helper function to build an image.
#
#   build_image.sh <context> <dockerfile> <tag> [tag...]
#
# Env:
#
#   PUSH=true      push to remote registry; 
#
#   BUILD_CACHE=1  read (and, when pushing, write) a :buildcache tag alongside
#                  the image. Needs a docker-container buildx driver.
#                  docker/setup-buildx-action CI job builds this.
#

build_image() {
  local context=$1 dockerfile=$2
  
  # tags are positional args - provide at least one
  shift 2
  [ $# -gt 0 ] || fail "build_image: at least one tag is required"
  
  local args=(buildx build "$context" --file "$dockerfile")
  
  local tag
  for tag in "$@"; do
    args+=(--tag "$tag")
  done
 
  if [ "${BUILD_CACHE:-0}" = "1" ]; then
    local cache_ref="${1%:*}:buildcache"
    args+=(--cache-from "type=registry,ref=$cache_ref")
    if [ "${PUSH:-false}" = "true" ]; then
      args+=(--cache-to "type=registry,ref=$cache_ref,mode=max")
    fi
  fi
 
  if [ "${PUSH:-false}" = "true" ]; then
    args+=(--push)
  else
    args+=(--load)
    info "PUSH is not 'true' — building locally, not pushing"
  fi
 
  info "+ docker ${args[*]}"
  docker "${args[@]}"
}
