#!/usr/bin/env bash
set -euo pipefail

# Build a release image, tagged with latest version.
#
# If the git tag already exists then does nothing. 
#
# Usage: build_release_image.sh <image_path>
#
# Env:
#   REGISTRY, IMAGE_NAMESPACE   required
#   PUSH=true                   push; otherwise images are loaded locally
#   BUILD_CACHE=1               use the registry build cache
#
# Outputs:
#   skip        "true" or "false" - if git-tag exists matching version, returns true
#   tag         git tag to set (for CI), <image-name>-<version>
#   image       image reference
#   latest      :latest image reference
#   dockerfile  path to the image_path's Dockerfile
#
# Local run:
#   REGISTRY=harbor.stfc.ac.uk PUSH=false IMAGE_NAMESPACE=stfc-cloud \
#     .github/scripts/build-release-image.sh service-a

# shellcheck source=.github/scripts/utils
source "$(dirname -- "${BASH_SOURCE[0]}")/utils.sh"

# shellcheck source=.github/scripts/build_image.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/build_image.sh"

image_path=${1:?usage: build-release-image.sh <image_path>}
require REGISTRY IMAGE_NAMESPACE

version=$(read_version "$image_path")
name=$(image_name "$image_path")
tag="$name-$version"

# if the git-tag already exists - do nothing as image likely already exists in registry
if git rev-parse -q --verify "refs/tags/$tag" > /dev/null; then
  info "tag $tag already exists — nothing to release - did you remember to bump the version in version.txt?"
  output skip true
  exit 0
fi

dockerfile=$(find_dockerfile "$image_path")
image="$REGISTRY/$IMAGE_NAMESPACE/$name:$version"
latest="$REGISTRY/$IMAGE_NAMESPACE/$name:latest"

output skip false
output tag "$tag"
output dockerfile "$dockerfile"
output image "$image"
output latest "$latest"

build_image "$image_path" "$dockerfile" "$image" "$latest"

info "built $image"
summary "release image: \`$image\`"