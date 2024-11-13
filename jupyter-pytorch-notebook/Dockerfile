
# Use a GPU-enabled base image based on the recommendation from
# https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#gpu-accelerated-notebooks
# As this combines the tensorflow-notebook and the cuda-notebook, so we only
# need to install the additional packages for each course.
FROM cschranz/gpu-jupyter:v1.5_cuda-11.6_ubuntu-20.04_python-only

USER root
# The base image only gets updated when a new version of CUDA is released.
# We need to update the base image to get the latest security updates.
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# Required for Tensorboard on a remote container
RUN mamba install --yes \
    'jupyter-server-proxy' && \
    # SciML requirements
    mamba install --yes \
    'pytorch' 'transformers' 'accelerate' 'bitsandbytes' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

