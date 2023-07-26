## Building Images Locally

`build_images.sh` will build all docker images locally.

## CI and Automated Builds

[![CI](https://img.shields.io/github/actions/workflow/status/stfc/cloud-docker-images/build_images.yaml?logo=docker)](https://github.com/stfc/cloud-docker-images/actions/workflows/build_images.yaml?query=branch%3Amaster)

Images are built:

- On Pull Requests
- On merge to `master`
- Weekly

In addition, the successful builds on `master` will be uploaded to [Harbor](https://harbor.stfc.ac.uk) too.
