FROM jupyter/tensorflow-notebook
# Get the latest image tag at:
# https://hub.docker.com/r/jupyter/minimal-notebook/tags/
# Inspect the Dockerfile at:
# https://github.com/jupyter/docker-stacks/tree/HEAD/minimal-notebook/Dockerfile

# Switch to root to install packages
USER root

# install additional package...
RUN echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /" >> /etc/apt/sources.list
RUN apt-get update --yes && apt-get install --yes --allow-unauthenticated curl wget patch cuda-toolkit nvidia-driver-470
# install tensorflow for GPUs
RUN pip install tensorflow-gpu

# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}
