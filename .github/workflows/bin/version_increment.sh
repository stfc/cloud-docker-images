#!/usr/bin/bash

set -euo pipefail

#reads the version.txt file and sets the version to the current version
version=`cat ~0/OpenStack-Rabbit-Consumer/version.txt`

# cuts the $version variable into major, minor and patch numbers, removing the fullstop
major=$(echo $version | cut -f1 -d.)
minor=$(echo $version | cut -f2 -d.)
patch=$(echo $version | cut -f3 -d.)

#increments the patch by 1
patch=$((patch + 1))

#concatenate the version
newversion="$major.$minor.$patch"

#overwrites the version.txt file with new new version
printf "$newversion" > ~0/OpenStack-Rabbit-Consumer/version.txt
