FROM jupyter/scipy-notebook
# Get the latest image tag at:
# https://hub.docker.com/r/jupyter/minimal-notebook/tags/
# Inspect the Dockerfile at:
# https://github.com/jupyter/docker-stacks/tree/HEAD/minimal-notebook/Dockerfile

# Switch to root to install packages
USER root

# install additional package...
RUN apt-get update --yes && apt-get install --yes curl wget patch

# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}
