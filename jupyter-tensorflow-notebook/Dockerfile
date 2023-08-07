
FROM jupyter/tensorflow-notebook:ubuntu-22.04
# Switch to root to install packages

USER root

RUN apt-get update --yes \
    && apt-get install -y --no-install-recommends \
    && apt-get install --yes nvidia-cuda-toolkit

# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}

# pip install required packages
RUN pip install jupyter-server-proxy tensorflow tensorboard --no-cache-dir
RUN pip install gym==0.25.2 pygame --no-cache-dir

# Note, the trailing slash is important!
ENV TENSORBOARD_PROXY_URL=/user-redirect/proxy/6006/
