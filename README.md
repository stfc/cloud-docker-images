Building Images Locally
-----------------------

A helper script is provided called `build_images.sh`. This will iterate through
and build all docker images locally.

CI and Automated Builds
----------------------

Images are built
- In Pull Requests
- On merge to `master`
- Weekly

In addition, the successful builds on `master` will be uploaded to Harbor too.
