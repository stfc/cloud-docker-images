
FROM jupyter/tensorflow-notebook:ubuntu-22.04

# Switch to root to install packages
USER root

RUN apt-get update --yes \
    && apt-get install -y --no-install-recommends \
    nvidia-headless-515 \
    nvidia-utils-515 \
    libnvidia-gl-515-server \
    libopengl0 && \
    apt-get install --no-install-recommends --yes \
    # The Nvidia cuda toolkit has to be installed after the driver to allow
    # apt to select the correct one
    nvidia-cuda-toolkit \
    libglvnd0 \
    libgl1 \
    libglx0 \
    libegl1 \
    libgles2 \
    xvfb && \
    rm -rf /var/lib/apt/lists/*

# COPY requirements.yml .
# RUN mamba env update --file requirements.yml && rm requirements.yml

ENV NVIDIA_DRIVER_CAPABILITIES compute,graphics,utility,video

USER ${NB_UID}
