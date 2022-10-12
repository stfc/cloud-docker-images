
FROM jupyter/tensorflow-notebook:ubuntu-20.04

# Switch to root to install packages
USER root

RUN apt-get update --yes \
    && apt-get install -y --no-install-recommends \
    nvidia-headless-515 \
    nvidia-cuda-toolkit \
    nvidia-utils-515 \
    libnvidia-gl-515-server \
    libopengl0 \
    && apt-get install --yes curl wget patch \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
    libglvnd0 \
    libgl1 \
    libglx0 \
    libegl1 \
    libgles2 \
    xvfb && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.yml .
# Downgrade ipywidgets to less than 8 to avoid https://github.com/matplotlib/ipympl/issues/460
RUN pip install --no-cache-dir --ignore-installed "ipywidgets>=7.0,<8"
RUN conda env update --file requirements.yml && rm requirements.yml

ENV NVIDIA_DRIVER_CAPABILITIES compute,graphics,utility,video

USER ${NB_UID}
