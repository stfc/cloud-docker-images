
FROM jupyter/tensorflow-notebook:ubuntu-22.04

# Switch to root to install packages
USER root

RUN apt-get update --yes \
    && apt-get install -y --no-install-recommends \
    nvidia-headless-515 \
    nvidia-utils-515 \
    libnvidia-gl-515-server \
    libopengl0 \
    && apt-get install --yes \
    curl \
    wget \
    patch  \
    nvidia-cuda-toolkit \
    && rm -rf /var/lib/apt/lists/*

# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}
RUN pip install jupyter-server-proxy tensorflow tensorboard --no-cache-dir

# Note, the trailing slash is important!
ENV TENSORBOARD_PROXY_URL=/user-redirect/proxy/6006/
