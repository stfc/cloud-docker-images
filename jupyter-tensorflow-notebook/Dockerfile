
FROM jupyter/tensorflow-notebook:ubuntu-20.04

# Switch to root to install packages
USER root

RUN apt-get update --yes \
    # Pinned to 460.32.03 to match prod version (capped by CoreOS)
    && apt-get install -y --no-install-recommends \
    nvidia-headless-460 \
    nvidia-cuda-toolkit \
    nvidia-utils-460 \
    libnvidia-gl-470-server \
    libopengl0 \
    && apt-get install --yes curl wget patch \
    && rm -rf /var/lib/apt/lists/*

# install tensorflow for GPUs
RUN pip uninstall tensorflow tensorboard --yes \
    && pip install --no-cache-dir tensorflow-gpu tensorboard \
    && pip install --no-cache-dir jupyter-server-proxy \
    && pip install --no-cache-dir jupyterlab --upgrade \
    && pip install --no-cache-dir graphviz --upgrade

# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}
ENV TENSORBOARD_PROXY_URL=/user-redirect/proxy/6006
