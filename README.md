# Cloud Docker Images

This repo stores various Docker images and build scripts that are used by the STFC Cloud

# Adding a new docker image

Create a new unique directory and create a `Dockerfile` and `version.txt`. 

The `version.txt` will track the latest version of your image for build tagging and version bumps.

If adding source-code - please a new CI github action for performing tests and linting checks 


# Image build scripts and CI

Docker images are built and pushed to https://harbor.stfc.ac.uk by CI jobs


`.github/workflows/create_dev_image.yml` runs when a PR is created and will build and push a dev image following the format: `<image-name>-dev.<version>-<github commit sha>` - e.g. `cloud-monitoring-dev.1.0.0-ase34e1`

`.github/workflows/create_release_image.yml` runs when the PR is merged. A new version - specified in `version.txt` is required to be bumped before merging. Once merged - a new image with that version will be built and pushed to harbor

To manually build and push images, you can run:

```sh
VERSION=$(cat cloud-monitoring/version.txt) 

# docker build <repo>/<image-namespace>/<image>:$VERSION
docker build harbor.stfc.ac.uk/stfc-cloud/cloud-monitoring:$VERSION --push

# for a dev image
docker build harbor.stfc.ac.uk/stfc-cloud-staging/cloud-monitoring:$VERSION-dev.1 --push
```

## Linting and Testing

Currently linting and testing CI actions are prefixed with `test_and_lint*`. Since each image is built slightly differently, we have separate CI actions for each. These CI jobs do not build images and are run when a PR is opened

