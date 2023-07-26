#!/usr/bin/env bash
set -euxo pipefail
# Builds all docker images in all subirectories
find -name Dockerfile -execdir docker build . \;
echo "All images built successfully"
