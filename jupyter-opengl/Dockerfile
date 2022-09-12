FROM harbor.stfc.ac.uk/stfc-cloud/jupyter-tensorflow-notebook

USER root

RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
    libglvnd0 \
    libgl1 \
    libglx0 \
    libegl1 \
    libgles2 \
    xvfb && \
    rm -rf /var/lib/apt/lists/*

USER ${NB_UID}