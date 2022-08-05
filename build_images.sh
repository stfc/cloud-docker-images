#!/bin/bash

set -e

# Iterates through all folders within the repo to build their docker images
# this is used for various CI jobs

# This assumes the script is in the root of the repository
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
declare -a DOCKER_FILES
mapfile -d '' DOCKER_FILES < <(find "$SCRIPT_DIR" -name Dockerfile -type f -print0)

for i in "${DOCKER_FILES[@]}"; 
    do echo "Building ${i}..." && docker build $(dirname "${i}"); 
done
echo "All images built successfully"