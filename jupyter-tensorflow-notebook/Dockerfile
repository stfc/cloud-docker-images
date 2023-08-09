
FROM jupyter/tensorflow-notebook:ubuntu-22.04

# pip install required packages
# source: https://github.com/jupyter/docker-stacks
RUN pip install jupyter-server-proxy tensorboard --no-cache-dir \
    && fix-permissions "${CONDA_DIR}" \
    && fix-permissions "/home/${NB_USER}"
RUN pip install gym==0.25.2 pygame --no-cache-dir

# Note, the trailing slash is important!
ENV TENSORBOARD_PROXY_URL=/user-redirect/proxy/6006/
