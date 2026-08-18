#!/usr/bin/env bash

# Build a dev image.
#
# Tag format: <version>dev-<short sha>, e.g. 1.0.0-dev-ase241f
#
# Usage: build_dev_image.sh <image_name> [sha]
#   sha defaults to HEAD.
#
# Env:
#   REGISTRY, IMAGE_NAMESPACE   required
#   PUSH=true                   push; otherwise the image is loaded locally
#   BUILD_CACHE=1               use the registry build cache
#
# Outputs:
#   image_path       full image reference
#   dockerfile  path to the image_name's Dockerfile
#
# Local run:
#   REGISTRY=harbor.stfc.ac.uk PUSH=false IMAGE_NAMESPACE=stfc-cloud-staging \
#     .github/scripts/build-release-image.sh service-a

set -euo pipefail

# shellcheck source=.github/scripts/_common.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/utils.sh"

# shellcheck source=.github/scripts/build_image.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/build_image.sh"


image_path=${1:?usage: build_dev_image.sh <image_path> [sha]}
sha=${2:-$(git rev-parse HEAD)}
require REGISTRY IMAGE_NAMESPACE

version=$(read_version "$image_path")
name=$(get_image_name "$image_path")
dockerfile=$(find_dockerfile "$image_path")
short=${sha:0:7}

image="$REGISTRY/$IMAGE_NAMESPACE/$name:${version}-dev-${short}"

output image "$image"
output dockerfile "$dockerfile"
 
build_image "$image_path" "$dockerfile" "$image"
 
info "built $image"
summary "dev image: \`$image\`"
