## Building Images Locally

`build_images.sh` will build all docker images locally.

## CI and Automated Builds

Images are built:

- On Pull Requests
- On merge to `master`
- Weekly

In addition, the successful builds on `master` will be uploaded to [Harbor](https://harbor.stfc.ac.uk) too.
