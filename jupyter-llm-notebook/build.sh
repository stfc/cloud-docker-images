#!/bin/bash

set -eux -o pipefail

git submodule update --init

# Use our custom Dockerfile
mkdir -p gpu-jupyter-base/.build
cp install-sciml-deps.sh gpu-jupyter-base/.build
cp Dockerfile gpu-jupyter-base/custom/usefulpackages.Dockerfile

# Prep the docker file
gpu-jupyter-base/generate-Dockerfile.sh --python-only

echo "Dockerfile in gpu-jupyter-base/.build ready to build..."
echo "Run manually with:    docker build gpu-jupyter-base/.build -t your-tag"
